"""Estudo de viabilidade 1: poder estatistico, semi-sintetico.

A ESTRUTURA vem do dataset publico do Kaggle (caminhoes, terminais, milhas por
caminhao e mes). Os ACIDENTES sao simulados com efeitos conhecidos, porque os
incidentes do dataset sao praticamente aleatorios (ver notas/05).

Perguntas:
  H2  Com N acidentes no periodo, qual a chance de detectar um efeito de
      telemetria de tamanho beta (por desvio padrao)?
  H1  O bayes empirico ordena os sites pelo risco verdadeiro melhor que a
      taxa bruta e que a contagem bruta?
  H3  Com que erro se estima a probabilidade de relato por site?

Duas bases:
  kaggle  o painel do dataset como esta (92 caminhoes, 24 terminais, 36 meses)
  escala  ordem de grandeza do projeto: 280 caminhoes x 14 meses em 40 sites,
          com milhas reamostradas do Kaggle

Uso (na raiz do repositorio):
    .venv/Scripts/python analise/viabilidade/poder.py --repeticoes 100
Saidas: resultados/viabilidade/poder.csv (fora do git),
        dissertacao/tabelas/tab_poder*.tex e dissertacao/figuras/fig_poder.pdf
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys
import warnings
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "analise"))
import dados_publicos  # noqa: E402
import modelos  # noqa: E402

SAIDA_BRUTA = RAIZ / "resultados" / "viabilidade"
TABELAS = RAIZ / "dissertacao" / "tabelas"
FIGURAS = RAIZ / "dissertacao" / "figuras"

ALVOS = (70, 300, 600)          # acidentes relatados esperados no periodo
BETAS = (0.0, 0.15, 0.30)       # efeito da telemetria por desvio padrao (log da taxa)
BASES = ("kaggle", "escala")
DP_SITE, DP_VEIC, FORMA_NB = 0.40, 0.30, 2.0
P_DETECCAO, RELATO_MEDIO, RELATO_CONC = 0.35, 0.65, 8.0
SEMENTE = 20261108


def base_kaggle() -> pd.DataFrame:
    df = dados_publicos.montar_painel(tipos=None)
    return df[["veiculo", "site", "mes", "milhas"]].reset_index(drop=True)


def base_escala(kaggle: pd.DataFrame, rng, n_veic=280, n_meses=14, n_sites=40) -> pd.DataFrame:
    """280 caminhoes, cada um uma janela de 14 meses de um caminhao do Kaggle."""
    series = {v: g.sort_values("mes")["milhas"].to_numpy() for v, g in kaggle.groupby("veiculo")}
    longas = [v for v, s in series.items() if len(s) >= n_meses]
    peso = rng.lognormal(0, 1.0, n_sites)
    linhas = []
    for i in range(n_veic):
        s = series[longas[rng.integers(len(longas))]]
        ini = rng.integers(0, len(s) - n_meses + 1)
        site = rng.choice(n_sites, p=peso / peso.sum())
        for t in range(n_meses):
            linhas.append((f"V{i:03d}", f"S{site:02d}", t, s[ini + t]))
    return pd.DataFrame(linhas, columns=["veiculo", "site", "mes", "milhas"])


def simular(base: pd.DataFrame, beta: float, alvo: int, rng) -> tuple[pd.DataFrame, dict]:
    df = base.copy()
    veics, sites = df["veiculo"].unique(), df["site"].unique()
    nivel = dict(zip(veics, rng.normal(0, 0.8, len(veics))))
    z = df["veiculo"].map(nivel) + rng.normal(0, 0.6, len(df))
    df["z_tel"] = (z - z.mean()) / z.std()
    u = dict(zip(sites, rng.normal(0, DP_SITE, len(sites))))
    v = dict(zip(veics, rng.normal(0, DP_VEIC, len(veics))))
    eta = np.log(df["milhas"]) + beta * df["z_tel"] + df["site"].map(u) + df["veiculo"].map(v)
    # intercepto calibrado para que os relatos esperados somem `alvo`
    escala = alvo / (RELATO_MEDIO * np.exp(eta).sum())
    mu = escala * np.exp(eta) * rng.gamma(FORMA_NB, 1 / FORMA_NB, len(df))
    verdadeiros = rng.poisson(mu)
    p_rel = dict(zip(sites, rng.beta(RELATO_MEDIO * RELATO_CONC, (1 - RELATO_MEDIO) * RELATO_CONC, len(sites))))
    pr = df["site"].map(p_rel).to_numpy()
    det = rng.binomial(verdadeiros, P_DETECCAO)
    det_rel = rng.binomial(det, pr)
    df["acidentes"] = det_rel + rng.binomial(verdadeiros - det, pr)
    df["colisoes_detectadas"] = det
    df["detectadas_e_relatadas"] = det_rel
    return df, {"u": u, "p_relato": p_rel}


def uma_repeticao(args) -> dict:
    base_nome, alvo, beta, rep = args
    rng = np.random.default_rng([SEMENTE, BASES.index(base_nome), alvo, int(beta * 100), rep])
    base = BASE_KAGGLE if base_nome == "kaggle" else base_escala(BASE_KAGGLE, rng)
    df, verdade = simular(base, beta, alvo, rng)
    out = dict(base=base_nome, alvo=alvo, beta=beta, rep=rep, relatados=int(df["acidentes"].sum()),
               sites=df["site"].nunique())
    # H2: efeito de telemetria
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = modelos.ajustar(df, "nb", ["z_tel"], com_site=True, exposicao="milhas")
        lo, hi = res.conf_int().loc["z_tel"]
        out.update(beta_hat=res.params["z_tel"], p_valor=res.pvalues["z_tel"],
                   cobre=bool(lo <= beta <= hi), convergiu=True)
    except Exception:
        out.update(beta_hat=np.nan, p_valor=np.nan, cobre=np.nan, convergiu=False)
    # H1: quem ordena melhor os sites pelo risco verdadeiro (u_s)?
    g = df.groupby("site").agg(y=("acidentes", "sum"), e=("milhas", "sum"))
    eb = modelos.taxa_bayes_empirico(g["y"], g["e"])
    u_true = g.index.map(verdade["u"])
    for nome, serie in (("contagem", g["y"]), ("taxa_bruta", eb["taxa_bruta"]), ("taxa_eb", eb["taxa_eb"])):
        out[f"rho_{nome}"] = stats.spearmanr(serie, u_true).statistic if serie.nunique() > 1 else 0.0
    # H3: probabilidade de relato por site
    rel = modelos.probabilidade_relato(df)
    p_true = rel.index.map(verdade["p_relato"])
    out.update(detectadas=int(df["colisoes_detectadas"].sum()),
               eam_p_bruta=float(np.mean(np.abs(rel["p_bruta"] - p_true))),
               eam_p_eb=float(np.mean(np.abs(rel["p_eb"] - p_true))))
    return out


def _init():
    global BASE_KAGGLE
    BASE_KAGGLE = base_kaggle()


def virgula(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",")


def tabelas_e_figura(r: pd.DataFrame) -> None:
    TABELAS.mkdir(parents=True, exist_ok=True)
    FIGURAS.mkdir(parents=True, exist_ok=True)
    ok = r[r["convergiu"]]
    # Poder (beta > 0) e taxa de falso positivo (beta = 0)
    p = ok.assign(sig=ok["p_valor"] < 0.05).groupby(["base", "alvo", "beta"])["sig"].mean().unstack("beta")
    linhas = []
    for (base, alvo), row in p.iterrows():
        rot = "\\tr{Kaggle (92 caminhões, 36 meses)}{Kaggle (92 trucks, 36 months)}" if base == "kaggle" \
            else "\\tr{Escala do projeto (280 caminhões, 14 meses)}{Project scale (280 trucks, 14 months)}"
        linhas.append(f"{rot} & {alvo} & " + " & ".join(virgula(row[b]) for b in BETAS) + " \\\\")
    (TABELAS / "tab_poder.tex").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    # H1 e H3
    h = ok.groupby(["base", "alvo"]).agg(contagem=("rho_contagem", "mean"), bruta=("rho_taxa_bruta", "mean"),
                                         eb=("rho_taxa_eb", "mean"), detect=("detectadas", "mean"),
                                         p_bruta=("eam_p_bruta", "mean"), p_eb=("eam_p_eb", "mean"))
    l1, l3 = [], []
    for (base, alvo), row in h.iterrows():
        b = "Kaggle" if base == "kaggle" else "\\tr{Escala}{Scale}"
        l1.append(f"{b} & {alvo} & {virgula(row['contagem'])} & {virgula(row['bruta'])} & {virgula(row['eb'])} \\\\")
        l3.append(f"{b} & {alvo} & {row['detect']:.0f} & {virgula(row['p_bruta'], 3)} & {virgula(row['p_eb'], 3)} \\\\")
    (TABELAS / "tab_poder_h1.tex").write_text("\n".join(l1) + "\n", encoding="utf-8")
    (TABELAS / "tab_poder_h3.tex").write_text("\n".join(l3) + "\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 9})
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.6), sharey=True)
    for ax, base, titulo in zip(axes, BASES, ("Kaggle (92 × 36)", "Escala (280 × 14)")):
        for beta, est in zip(BETAS, (":", "--", "-")):
            ax.plot(ALVOS, [p.loc[(base, a), beta] for a in ALVOS], "k" + est, marker="o", ms=3,
                    label=f"β = {virgula(beta)}")
        ax.axhline(0.8, color="0.6", lw=0.6)
        ax.axhline(0.05, color="0.6", lw=0.6)
        ax.set_title(titulo)
        ax.set_xlabel("acidentes relatados no período")
        ax.set_xticks(ALVOS)
    axes[0].set_ylabel("poder (p < 0,05)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURAS / "fig_poder.pdf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeticoes", type=int, default=100)
    ap.add_argument("--processos", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--so-tabelas", action="store_true")
    a = ap.parse_args()
    SAIDA_BRUTA.mkdir(parents=True, exist_ok=True)
    arq = SAIDA_BRUTA / "poder.csv"
    if not a.so_tabelas:
        tarefas = list(itertools.product(BASES, ALVOS, BETAS, range(a.repeticoes)))
        with Pool(a.processos, initializer=_init) as pool:
            res = pool.map(uma_repeticao, tarefas, chunksize=4)
        pd.DataFrame(res).to_csv(arq, index=False)
    r = pd.read_csv(arq)
    tabelas_e_figura(r)
    print(f"{len(r)} repeticoes; nao convergiram: {(~r['convergiu']).sum()}")
    ok = r[r["convergiu"]]
    print(ok.assign(sig=ok["p_valor"] < 0.05).groupby(["base", "alvo", "beta"])
          .agg(poder=("sig", "mean"), beta_medio=("beta_hat", "mean"), cobertura=("cobre", "mean"),
               relatados=("relatados", "mean")).round(3).to_string())
    print(ok.groupby(["base", "alvo"])[["rho_contagem", "rho_taxa_bruta", "rho_taxa_eb", "detectadas",
                                        "eam_p_bruta", "eam_p_eb"]].mean().round(3).to_string())


if __name__ == "__main__":
    main()
