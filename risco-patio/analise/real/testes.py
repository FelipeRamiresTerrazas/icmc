"""Testes formais (H0 de igualdade) do estudo preliminar com dados reais (uso interno).

Le resultados/real/*.csv.gz (extrair.py) e escreve em resultados/real/:
  painel_h2.csv     painel veiculo x mes com taxas de telemetria (entrada do R)
  testes_py.csv     resultados de H1, H2 (preditivo) e H3
  sites_h1.csv      taxas por site mascarado (para a figura)
O modelo misto de H2 (efeito aleatorio de veiculo, TOST) fica em r/h2_misto.R.

Uso (na raiz do repo):  .venv/Scripts/python.exe analise/real/testes.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explorar import ROTULOS, mascara, matriz, nb_irr, taxa_bayes_empirico  # noqa: E402

R = Path(__file__).resolve().parents[2] / "resultados" / "real"
RNG = np.random.default_rng(20261111)
B = 2000
LINHAS = []


def reg(teste, h0, estatistica, valor, ic_lo=np.nan, ic_hi=np.nan, p=np.nan, nota=""):
    LINHAS.append(dict(teste=teste, h0=h0, estatistica=estatistica, valor=valor,
                       ic_lo=ic_lo, ic_hi=ic_hi, p=p, nota=nota))
    print(f"{teste:6s} {estatistica:45s} {valor:8.3f} [{ic_lo:7.3f}, {ic_hi:7.3f}] p={p:.4f} {nota}")


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def painel():
    p = pd.read_csv(R / "painel.csv.gz")
    p["mes"] = pd.to_datetime(p["mes"])
    p = p[p.horas >= 10].copy()
    mapa = mascara(p)
    p["site_m"] = p.site.map(mapa)
    p["uso"] = p.uso.fillna("sem tag")
    ev = pd.read_csv(R / "eventos.csv.gz")
    ev["mes"] = pd.to_datetime(ev["mes"])
    w = ev.pivot_table(index=["vehicle_id", "mes"], columns="label", values="n_mantidos", aggfunc="sum", fill_value=0)
    p = p.merge(w, left_on=["vehicle_id", "mes"], right_index=True, how="left")
    for lab in ROTULOS:
        p[lab] = p[lab].fillna(0)
        x = np.log1p(p[lab] / p.horas * 100)          # eventos por 100 horas de viagem
        p[f"z_{lab}"] = (x - x.mean()) / x.std()
    return p, mapa


def h1(p):
    s = p.dropna(subset=["site_m"]).assign(metade=lambda d: np.where(d.mes < "2026-04-01", 1, 2))
    h = s.groupby(["site_m", "metade"]).agg(acid=("acid", "sum"), horas=("horas", "sum")).unstack()
    h = h[(h["horas"] >= 50).all(axis=1)]
    y1, y2 = h["acid"][1], h["acid"][2]
    e1, e2 = h["horas"][1] / 1e3, h["horas"][2] / 1e3
    eb1 = taxa_bayes_empirico(y1, e1).taxa_eb
    r1, r2 = y1 / e1, y2 / e2
    w = e2 / e2.sum()
    d_obs = np.sum(w * (np.abs(r1 - r2) - np.abs(eb1 - r2)))
    idx = np.arange(len(h))
    boot = []
    for _ in range(B):
        i = RNG.choice(idx, len(idx))
        ww = w.iloc[i] / w.iloc[i].sum()
        boot.append(np.sum(ww * (np.abs(r1.iloc[i] - r2.iloc[i]).values - np.abs(eb1.iloc[i] - r2.iloc[i]).values)))
    boot = np.array(boot)
    reg("H1a", "erro(EB) = erro(bruta)", "ganho de erro absoluto (bruta - EB), por 1000 h", d_obs,
        *np.percentile(boot, [2.5, 97.5]), p=2 * min(np.mean(boot <= 0), np.mean(boot >= 0)),
        nota=f"{len(h)} sites, bootstrap por site")
    # H1b: confundimento com o tamanho (equivalencia: |rho| < 0,3)
    g = s.groupby("site_m").agg(acid=("acid", "sum"), horas=("horas", "sum"))
    g = g[g.horas >= 50]
    eb = taxa_bayes_empirico(g.acid, g.horas / 1e3)
    for nome, x in [("contagem bruta", g.acid), ("taxa EB", eb.taxa_eb)]:
        rho = stats.spearmanr(x, g.horas)[0]
        bs = []
        for _ in range(B):
            i = RNG.choice(len(g), len(g))
            bs.append(stats.spearmanr(x.iloc[i], g.horas.iloc[i])[0])
        lo, hi = np.nanpercentile(bs, [5, 95])          # IC 90% = TOST a 5%
        eq = "equivalente a zero (|rho|<0,3)" if (lo > -0.3 and hi < 0.3) else "nao equivalente"
        reg("H1b", "rho(indicador, exposicao) fora de (-0,3; 0,3)", f"Spearman {nome} x horas (IC 90%)", rho, lo, hi,
            nota=f"{len(g)} sites; {eq}")
    g = g.assign(taxa=eb.taxa_bruta, taxa_eb=eb.taxa_eb, peso=eb.peso)
    m0 = g.acid.sum() / (g.horas.sum() / 1e3)
    g["rel"], g["rel_eb"] = g.taxa / m0, g.taxa_eb / m0
    g["horas_rel"] = g.horas / g.horas.median()
    esperado = m0 * g.horas / 1e3
    g["fora95"] = (g.acid < stats.poisson.ppf(0.025, esperado)) | (g.acid > stats.poisson.ppf(0.975, esperado))
    g["fora998"] = (g.acid < stats.poisson.ppf(0.001, esperado)) | (g.acid > stats.poisson.ppf(0.999, esperado))
    reg("H1c", "taxa igual em todos os sites", "fracao de sites fora do limite de 95%", g.fora95.mean(),
        p=stats.binomtest(int(g.fora95.sum()), len(g), 0.05).pvalue, nota=f"esperado 0,05 sob H0; {len(g)} sites")
    # teste de homogeneidade (qui-quadrado de Poisson)
    chi = np.sum((g.acid - esperado) ** 2 / esperado)
    reg("H1c", "taxa igual em todos os sites", "qui-quadrado de homogeneidade / gl", chi / (len(g) - 1),
        p=stats.chi2.sf(chi, len(g) - 1))
    g.to_csv(R / "sites_h1.csv")


def escore(tr, te, cs):
    mm, aa = nb_irr(tr, "acid", cs)
    mu = np.exp(matriz(te, cs).values @ mm.params.values) * te.horas.values / 100
    n = 1 / aa
    return stats.nbinom.logpmf(te.acid, n, n / (n + mu))


def h2_preditivo(p):
    du = pd.get_dummies(p.uso, prefix="u", dtype=float).drop(columns="u_Spot Tractor")
    p = p.join(du)
    uso = list(du.columns)
    tele = ["z_Braking", "z_HarshTurn", "z_FollowingDistance", "z_MaxSpeed", "z_MobileUsage", "z_SevereSpeeding"]
    corte = np.sort(p.mes.unique())[8]
    tr, te = p[p.mes < corte], p[p.mes >= corte]
    s0, s1 = escore(tr, te, uso), escore(tr, te, uso + tele)
    d = s1 - s0
    veic = te.vehicle_id.values
    uv = np.unique(veic)
    pos = {v: np.where(veic == v)[0] for v in uv}
    boot = []
    for _ in range(B):
        i = np.concatenate([pos[v] for v in RNG.choice(uv, len(uv))])
        boot.append(d[i].mean())
    boot = np.array(boot)
    reg("H2a", "escore(uso+telemetria) = escore(uso)", "diferenca de escore log medio (x1000)", 1000 * d.mean(),
        *(1000 * np.percentile(boot, [2.5, 97.5])), p=2 * min(np.mean(boot <= 0), np.mean(boot >= 0)),
        nota=f"teste nos ultimos 4 meses, {len(te)} veiculo-meses, bootstrap por veiculo")
    p.to_csv(R / "painel_h2.csv", index=False)


def h3():
    c = pd.read_csv(R / "colisoes.csv.gz")
    c["uso"] = c.uso.fillna("sem tag")
    r = c[c.lado == "relato"].copy()
    r["det"] = r.grupo.isin(["com_mantida", "so_descartada"])
    t = r.groupby(["uso", "det"]).n.sum().unstack(fill_value=0)
    t = t.loc[["Spot Tractor", "Shuttle Tractor", "Local Tractor"]]
    k, n = t[True].sum(), t.values.sum()
    reg("H3a", "P(detectado | relatado) = 1", "fracao de relatos com deteccao (+-2 dias)", k / n, *wilson(k, n),
        p=stats.binomtest(int(k), int(n), 0.5).pvalue, nota=f"{n} relatos; frente a 0,5 o p ja e minusculo")
    chi, pv, _, _ = stats.chi2_contingency(t.values)
    for u in t.index:
        kk, nn = t.loc[u, True], t.loc[u].sum()
        reg("H3b", "P(deteccao) igual entre usos", f"fracao detectada: {u}", kk / nn, *wilson(kk, nn), nota=f"n={nn}")
    reg("H3b", "P(deteccao) igual entre usos", "qui-quadrado (3 usos)", chi, p=pv)
    d = c[c.lado == "deteccao"]
    kd, nd = d[d.grupo == "descartada"].n.sum(), d.n.sum()
    reg("H3c", "-", "fracao de deteccoes de colisao descartadas na revisao", kd / nd, *wilson(kd, nd), nota=f"n={nd}")
    pd.DataFrame({"uso": t.index, "detectados": t[True].values, "relatos": t.sum(axis=1).values}).to_csv(
        R / "h3_uso.csv", index=False)


def main():
    p, _ = painel()
    h1(p)
    h2_preditivo(p)
    h3()
    pd.DataFrame(LINHAS).to_csv(R / "testes_py.csv", index=False)


if __name__ == "__main__":
    main()
