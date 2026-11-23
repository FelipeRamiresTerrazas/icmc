"""Exploracao de viabilidade com os agregados reais (uso interno).

Le resultados/real/*.csv.gz (gerados por extrair.py) e escreve
resultados/real/resumo.txt. Sites aparecem mascarados (Site 01, 02... por
milhas totais, maior primeiro). Nada daqui vai para o pre-projeto sem revisao.

Uso (na raiz do repo):  .venv/Scripts/python.exe analise/real/explorar.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.discrete.discrete_model import NegativeBinomial
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "analise"))
from modelos import limites_funil, taxa_bayes_empirico  # noqa: E402

R = RAIZ / "resultados" / "real"
ROTULOS = ["Braking", "HarshTurn", "FollowingDistance", "MaxSpeed", "SevereSpeeding",
           "MobileUsage", "GenericDistraction", "RollingStop", "NoSeatbelt", "Drowsy"]
SAIDA = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    SAIDA.append(s)


def secao(t):
    out("\n" + "=" * 70 + "\n" + t + "\n" + "=" * 70)


def ler(n):
    return pd.read_csv(R / f"{n}.csv.gz")


def mascara(painel):
    ordem = painel.dropna(subset=["site"]).groupby("site").milhas.sum().sort_values(ascending=False)
    return {s: f"Site {i + 1:02d}" for i, s in enumerate(ordem.index)}


EXPO = "horas"  # exposicao principal: horas de viagem (milhas penaliza spotters, que andam pouco)


def matriz(df, covs):
    X = pd.DataFrame({"const": np.ones(len(df))}, index=df.index)
    return X.join(df[covs].astype(float)) if covs else X


def nb_irr(df, y, covs, expo=None, grupo="vehicle_id"):
    """NB2 com offset log(exposicao); alpha por perfil de verossimilhanca em grade;
    erro padrao robusto por veiculo (substitui o efeito aleatorio nesta exploracao)."""
    expo = expo or EXPO
    X, e = matriz(df, covs), df[expo] / 100
    melhor = None
    for a in np.geomspace(0.01, 10, 31):
        f = sm.GLM(df[y], X, family=sm.families.NegativeBinomial(alpha=a), exposure=e).fit()
        if melhor is None or f.llf > melhor[1]:
            melhor = (a, f.llf)
    alpha = melhor[0]
    m = sm.GLM(df[y], X, family=sm.families.NegativeBinomial(alpha=alpha),
               exposure=e).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df[grupo])[0]})
    return m, alpha


def main():
    painel, eventos, funil, col, adp, rel = (ler(n) for n in
                                             ["painel", "eventos", "funil", "colisoes", "adp", "relatos"])
    painel["mes"] = pd.to_datetime(painel["mes"])
    mapa = mascara(painel)
    painel["site_m"] = painel.site.map(mapa).fillna("Oficina/sem site")

    # ------------------------------------------------------------------
    secao("1. Relatos de acidente (YardSafe) por mes do incidente e status")
    r = rel[rel.incident_type == "accident_incident"].pivot_table(index="mes", columns="status", values="n",
                                                                  aggfunc="sum", fill_value=0)
    out(r.to_string())
    out("Total de acidentes:", int(r.values.sum()))

    secao("2. Funil de ligacao: relato -> caminhao -> veiculo Samsara -> site")
    t = funil.drop(columns="mes").groupby("status").sum()
    t.loc["total"] = t.sum()
    out(t.to_string())
    tt = t.loc["total"]
    out(f"Casa com veiculo Samsara: {tt.casa_samsara / tt.relatos:.0%}; com tag de site: {tt.com_site_tag / tt.relatos:.0%}; "
        f"site do relato = site da tag, entre os que tem os dois: ver abaixo")
    both = funil.assign(ok=1)
    out(f"Relatos com codigo de site no proprio relato: {tt.com_site_relato:.0f}; concordam com a tag: {tt.site_concorda:.0f}")

    # ------------------------------------------------------------------
    secao("3. Painel veiculo x mes (out/2025 a set/2026)")
    p = painel[painel.milhas >= 1].copy()
    out(f"Veiculo-meses: {len(p)}; veiculos: {p.vehicle_id.nunique()}; meses: {p.mes.nunique()}")
    out(f"Milhas: {p.milhas.sum():,.0f}; horas de viagem: {p.horas.sum():,.0f}")
    out(f"Veiculo-meses sem site (oficina central ou sem tag): {(p.site_m == 'Oficina/sem site').mean():.0%}")
    out("Uso:", p.uso.fillna("sem tag").value_counts().to_dict())
    frota = p.groupby("mes").vehicle_id.nunique()
    out("Frota com viagem por mes:", frota.to_dict())
    for y, nome in [("acid", "todos os acidentes relatados"), ("acid_rev", "so revisados"),
                    ("acid_seguro", "com sinistro de seguro")]:
        v = p[y]
        m, a = nb_irr(p, y, [])
        out(f"[{nome}] total no painel {v.sum():.0f}; zeros {np.mean(v == 0):.1%}; media {v.mean():.3f}; "
            f"var {v.var():.3f}; var/media {v.var() / v.mean():.2f}; alpha NB (so offset) {a:.2f}; "
            f"taxa {v.sum() / p.milhas.sum() * 1e4:.2f} por 10 mil milhas")
    out("Distribuicao de acidentes por veiculo-mes:", p.acid.value_counts().sort_index().to_dict())
    pv = p.groupby("vehicle_id").agg(acid=("acid", "sum"), milhas=("milhas", "sum"))
    out(f"Veiculos com >=1 acidente no ano: {(pv.acid > 0).mean():.0%}; "
        f"top 10% dos veiculos concentram {pv.acid.nlargest(int(len(pv) * 0.1)).sum() / pv.acid.sum():.0%} dos acidentes")
    out("Taxa por uso (por 10 mil milhas):",
        (p.groupby(p.uso.fillna("sem tag")).apply(lambda g: g.acid.sum() / g.milhas.sum() * 1e4)).round(2).to_dict())
    out("Taxa por hora de viagem (por 1.000 h), por uso:",
        (p.groupby(p.uso.fillna("sem tag")).apply(lambda g: g.acid.sum() / g.horas.sum() * 1e3)).round(2).to_dict())

    # ------------------------------------------------------------------
    secao("4. H1: taxas por site, funil, Bayes empirico e estabilidade")
    s = p[p.site_m != "Oficina/sem site"]
    g = s.groupby("site_m").agg(acid=("acid", "sum"), milhas=("milhas", "sum"), horas=("horas", "sum"),
                                veic=("vehicle_id", "nunique")).sort_index()
    g["e"] = g.horas / 1e3
    eb = taxa_bayes_empirico(g.acid, g.e)
    m0 = g.acid.sum() / g.e.sum()
    lo95, hi95 = limites_funil(g.e.values, m0, 0.95)
    lo998, hi998 = limites_funil(g.e.values, m0, 0.998)
    g["taxa"] = eb.taxa_bruta.round(2)
    g["taxa_eb"] = eb.taxa_eb.round(2)
    g["peso_eb"] = eb.peso.round(2)
    g["fora95"] = np.where(g.taxa > hi95, "acima", np.where(g.taxa < lo95, "abaixo", ""))
    g["fora998"] = np.where(g.taxa > hi998, "acima", np.where(g.taxa < lo998, "abaixo", ""))
    out(f"Sites com tag: {len(g)}; taxa media {m0:.2f} por 1.000 horas de viagem")
    out(g[["veic", "acid", "horas", "taxa", "taxa_eb", "peso_eb", "fora95", "fora998"]].round(0 if False else 2).to_string())
    out(f"Fora do limite de 95%: {(g.fora95 != '').sum()} (acima {(g.fora95 == 'acima').sum()}); "
        f"fora de 99,8%: {(g.fora998 != '').sum()} (acima {(g.fora998 == 'acima').sum()})")
    var_ratio = eb.peso.mean()
    out(f"Peso medio do proprio site no Bayes empirico: {var_ratio:.2f} (0 = tudo encolhido para a media)")

    # estabilidade: 1a metade (out-mar) vs 2a (abr-set)
    s = s.assign(metade=np.where(s.mes < "2026-04-01", 1, 2))
    h = s.groupby(["site_m", "metade"]).agg(acid=("acid", "sum"), horas=("horas", "sum")).unstack().dropna()
    h = h[(h["horas"] >= 50).all(axis=1)]
    e1, e2 = h["horas"][1] / 1e3, h["horas"][2] / 1e3
    y1, y2 = h["acid"][1], h["acid"][2]
    eb1 = taxa_bayes_empirico(y1, e1).taxa_eb
    r2 = y2 / e2
    out(f"Sites com exposicao nas duas metades: {len(h)}")
    for nome, x in [("contagem", y1), ("taxa bruta", y1 / e1), ("taxa EB", eb1)]:
        rho, pv_ = stats.spearmanr(x, r2)
        out(f"  Spearman ({nome} na 1a metade vs taxa na 2a): {rho:.2f} (p={pv_:.2f})")
    for nome, x in [("taxa bruta", y1 / e1), ("taxa EB", eb1), ("media geral", pd.Series(y1.sum() / e1.sum(), index=y1.index))]:
        err = np.average(np.abs(x - r2), weights=e2)
        out(f"  Erro absoluto medio ponderado ao prever a taxa da 2a metade com {nome}: {err:.2f}")

    # exposicao ADP x Samsara por site-mes
    adp["mes"] = pd.to_datetime(adp.week_start).dt.to_period("M").dt.to_timestamp()
    am = adp.groupby(["site", "mes"]).horas.sum().rename("horas_adp")
    sm_ = s.groupby(["site", "mes"]).horas.sum().rename("horas_samsara")
    j = pd.concat([am, sm_], axis=1, join="inner")
    rho, _ = stats.spearmanr(j.horas_adp, j.horas_samsara)
    out(f"Site-meses com as duas exposicoes: {len(j)}; Spearman horas ADP vs horas de viagem Samsara: {rho:.2f}; "
        f"razao mediana ADP/Samsara {np.median(j.horas_adp / j.horas_samsara):.1f}")
    ja = j.groupby(level=0).sum()
    rho2, _ = stats.spearmanr(ja.horas_adp, ja.horas_samsara)
    out(f"  No total do ano por site: Spearman {rho2:.2f} ({len(ja)} sites)")

    # ------------------------------------------------------------------
    secao("5. H2: telemetria x acidentes (NB2, offset log(horas de viagem), ajuste por tipo de uso, erro robusto por veiculo)")
    ev = eventos.copy()
    ev["mes"] = pd.to_datetime(ev["mes"])
    out("Eventos do sistema no periodo por rotulo (todos / mantidos apos revisao / % descartado):")
    tot = ev.groupby("label")[["n_todos", "n_mantidos"]].sum().sort_values("n_todos", ascending=False)
    tot["desc"] = (1 - tot.n_mantidos / tot.n_todos).map("{:.0%}".format)
    out(tot.head(14).to_string())
    w = ev.pivot_table(index=["vehicle_id", "mes"], columns="label", values="n_mantidos", aggfunc="sum", fill_value=0)
    p2 = p.merge(w, left_on=["vehicle_id", "mes"], right_index=True, how="left").fillna({c: 0 for c in w.columns})
    p2 = p2[p2.horas >= 10].copy()
    du = pd.get_dummies(p2.uso.fillna("sem tag"), prefix="u", dtype=float).drop(columns="u_Spot Tractor")
    p2 = p2.join(du)
    USO = list(du.columns)
    p2 = p2.sort_values(["vehicle_id", "mes"])
    prox = p2.groupby("vehicle_id").shift(-1)
    p2["acid_prox"] = prox.acid
    p2["horas_prox"] = prox.horas
    p2["mes_prox_ok"] = (prox.mes - p2.mes).dt.days.between(27, 32)
    cov = []
    for lab in ROTULOS:
        if lab in p2:
            p2[f"z_{lab}"] = np.log1p(p2[lab] / p2.milhas * 1000)
            p2[f"z_{lab}"] = (p2[f"z_{lab}"] - p2[f"z_{lab}"].mean()) / p2[f"z_{lab}"].std()
            cov.append(f"z_{lab}")
    out(f"Veiculo-meses com >=10 horas de viagem: {len(p2)}; acidentes: {p2.acid.sum():.0f}")
    linhas = []
    for c in cov:
        m, _ = nb_irr(p2, "acid", [c] + USO)
        nx = p2[p2.mes_prox_ok]
        m2, _ = nb_irr(nx, "acid_prox", [c] + USO, expo="horas_prox")
        linhas.append((c[2:], np.exp(m.params[c]), *np.exp(m.conf_int().loc[c]), m.pvalues[c],
                       np.exp(m2.params[c]), m2.pvalues[c]))
    tab = pd.DataFrame(linhas, columns=["rotulo", "IRR_mesmo_mes", "ic_lo", "ic_hi", "p", "IRR_mes_seguinte", "p_seg"])
    out("IRR por 1 DP de log(1 + eventos mantidos por 1.000 milhas), um rotulo por vez, ajustado por uso:")
    out(tab.round(3).to_string(index=False))
    sel = [c for c in ["z_Braking", "z_HarshTurn", "z_FollowingDistance", "z_MaxSpeed", "z_MobileUsage"] if c in p2]
    m, a = nb_irr(p2, "acid", sel + USO)
    out(f"Modelo conjunto ({len(sel)} rotulos), mesmo mes, alpha {a:.2f}:")
    out(pd.DataFrame({"IRR": np.exp(m.params), "lo": np.exp(m.conf_int()[0]), "hi": np.exp(m.conf_int()[1]),
                      "p": m.pvalues}).round(3).to_string())
    # comparacao preditiva: ajusta nos 8 primeiros meses, pontua os 4 ultimos
    corte = np.sort(p2.mes.unique())[8]
    tr, te = p2[p2.mes < corte], p2[p2.mes >= corte]
    for nome, cs in [("so exposicao", []), ("exposicao + uso", USO), ("exposicao + uso + telemetria", sel + USO)]:
        mm, aa = nb_irr(tr, "acid", cs)
        mu = np.exp(matriz(te, cs).values @ mm.params.values) * te[EXPO].values / 100
        n = 1 / aa
        ll = stats.nbinom.logpmf(te.acid, n, n / (n + mu)).mean()
        out(f"  Teste fora da amostra (ultimos 4 meses), {nome}: escore log medio {ll:.4f} (alpha {aa:.2f})")

    # ------------------------------------------------------------------
    secao("6. H3: colisoes detectadas (Samsara) x relatos (YardSafe), +-2 dias, mesmo veiculo")
    d = col[col.lado == "deteccao"]
    rr = col[col.lado == "relato"]
    out("Deteccoes de colisao por estado e se casaram com relato:")
    out(d.groupby(["grupo", "casou"]).n.sum().to_string())
    out("Relatos (de caminhoes com Samsara) por existencia de deteccao:")
    out(rr.groupby("grupo").n.sum().to_string())
    col["site_m"] = col.site.map(mapa).fillna("Oficina/sem site")
    dk = col[(col.lado == "deteccao") & (col.grupo == "mantida")].groupby("site_m").apply(
        lambda x: pd.Series({"n1": x.n.sum(), "m": x.loc[x.casou == 1, "n"].sum()}))
    n2 = col[col.lado == "relato"].groupby("site_m").n.sum().rename("n2")
    lp = dk.join(n2, how="outer").fillna(0)
    lp["N_chapman"] = ((lp.n1 + 1) * (lp.n2 + 1) / (lp.m + 1) - 1).round(0)
    lp["relatado/detectado"] = (lp.m / lp.n1.replace(0, np.nan)).round(2)
    out(lp.astype({"n1": int, "n2": int, "m": int}).sort_values("n2", ascending=False).to_string())
    tot = lp.sum()
    out(f"Total: n1={tot.n1:.0f} deteccoes mantidas, n2={tot.n2:.0f} relatos, m={tot.m:.0f} em comum; "
        f"Chapman N={(tot.n1 + 1) * (tot.n2 + 1) / (tot.m + 1) - 1:.0f}")

    # ------------------------------------------------------------------
    secao("7. Extensao: previsao das horas semanais (ADP, total)")
    wk = adp.groupby("week_start").horas.sum().sort_index()
    wk.index = pd.to_datetime(wk.index)
    wk = wk[(wk.index >= "2025-06-08") & (wk.index <= "2026-10-25")]
    out(f"Semanas: {len(wk)} ({wk.index.min().date()} a {wk.index.max().date()}); "
        f"horas por semana de {wk.min():,.0f} a {wk.max():,.0f}")
    H = 8
    trn, tst = wk.iloc[:-H], wk.iloc[-H:]
    prev = {"media 8 semanas": np.repeat(trn.iloc[-8:].mean(), H),
            "ultima semana": np.repeat(trn.iloc[-1], H)}
    ets = ETSModel(np.log(trn.values), error="add", trend="add", damped_trend=True).fit(disp=False)
    prev["ETS (log, tendencia amortecida)"] = np.exp(ets.forecast(H))
    for k, v in prev.items():
        out(f"  {k}: erro percentual absoluto medio {np.mean(np.abs(v - tst.values) / tst.values):.1%}")
    sim = np.exp(ets.simulate(H, anchor="end", repetitions=2000, rng=np.random.default_rng(1)))
    lo, hi = np.percentile(sim, [10, 90], axis=1)
    out(f"  Cobertura do intervalo de 80% do ETS nas 8 semanas: {np.mean((tst.values >= lo) & (tst.values <= hi)):.0%}")
    cresc = wk.iloc[-8:].mean() / wk.iloc[:8].mean()
    out(f"  Crescimento: media das ultimas 8 semanas / primeiras 8 = {cresc:.2f}")

    (R / "resumo.txt").write_text("\n".join(SAIDA), encoding="utf-8")


if __name__ == "__main__":
    main()
