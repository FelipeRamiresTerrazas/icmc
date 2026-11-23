"""Modelos de risco do pre-projeto ICMC (etapas 2 a 4 da metodologia).

Funcoes puras sobre um painel veiculo x mes (ver painel_sintetico.py para a
estrutura). Nada aqui le dados da empresa.

Proximo passo previsto: o modelo hierarquico completo (efeitos aleatorios de
veiculo e site, eq. 1 do pre-projeto) sera ajustado no R com glmmTMB ou brms.
Aqui ficam as versoes de referencia em Python: GLM com offset, binomial
negativa e bayes empirico por site.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

COVARIAVEIS_TELEMETRIA = ["z_frenagens", "z_curvas", "z_velocidade"]


# Etapa 2: modelos de contagem com exposicao ---------------------------------

def _matriz(df: pd.DataFrame, covariaveis: list[str], com_site: bool) -> pd.DataFrame:
    X = df[covariaveis].copy() if covariaveis else pd.DataFrame(index=df.index)
    if com_site:
        X = X.join(pd.get_dummies(df["site"], prefix="site", drop_first=True, dtype=float))
    return sm.add_constant(X, has_constant="add")


def ajustar(df: pd.DataFrame, familia: str = "nb", covariaveis: list[str] | None = None,
            com_site: bool = True, exposicao: str = "horas"):
    """Ajusta Poisson ou binomial negativa (NB2) com log(exposicao) como offset."""
    covariaveis = covariaveis or []
    X = _matriz(df, covariaveis, com_site)
    y = df["acidentes"]
    if familia == "poisson":
        modelo = sm.Poisson(y, X, exposure=df[exposicao])
    elif familia == "nb":
        modelo = sm.NegativeBinomial(y, X, exposure=df[exposicao], loglike_method="nb2")
    else:
        raise ValueError(familia)
    res = modelo.fit(method="bfgs", disp=0, maxiter=5000)
    if not res.mle_retvals.get("converged", True):
        raise RuntimeError(f"{familia}: ajuste nao convergiu")
    res.familia, res.covariaveis, res.com_site, res.exposicao = familia, covariaveis, com_site, exposicao
    res.colunas = X.columns
    return res


def prever_mu(res, df: pd.DataFrame) -> np.ndarray:
    X = _matriz(df, res.covariaveis, res.com_site).reindex(columns=res.colunas, fill_value=0.0)
    params = res.params.drop("alpha", errors="ignore")
    return np.exp(X.values @ params.values + np.log(df[res.exposicao].values))


def escore_log(res, df: pd.DataFrame) -> float:
    """Escore logaritmico medio (maior e melhor) em dados nao usados no ajuste."""
    mu, y = prever_mu(res, df), df["acidentes"].values
    if res.familia == "poisson":
        return float(stats.poisson.logpmf(y, mu).mean())
    n = 1 / res.params["alpha"]
    return float(stats.nbinom.logpmf(y, n, n / (n + mu)).mean())


def validacao_temporal(df: pd.DataFrame, meses_teste: int = 4, exposicao: str = "horas",
                       covariaveis: list[str] | None = None) -> pd.DataFrame:
    """Compara modelos (H2): ajusta nos meses iniciais e pontua os ultimos.

    covariaveis: as do modelo mais completo (padrao: taxas de telemetria)."""
    covariaveis = COVARIAVEIS_TELEMETRIA if covariaveis is None else covariaveis
    corte = df["mes"].max() - meses_teste + 1
    treino, teste = df[df["mes"] < corte], df[df["mes"] >= corte]
    teste = teste[teste["site"].isin(treino["site"].unique())]
    candidatos = {
        "poisson | exposicao + site": ("poisson", []),
        "nb | exposicao + site": ("nb", []),
        "nb | exposicao + site + covariaveis": ("nb", covariaveis),
    }
    linhas = []
    for nome, (fam, cov) in candidatos.items():
        res = ajustar(treino, fam, cov, exposicao=exposicao)
        linhas.append(dict(modelo=nome, escore_log_teste=escore_log(res, teste), aic_treino=res.aic))
    return pd.DataFrame(linhas)


# Etapa 3: bayes empirico por site e estabilidade dos rankings ----------------

def taxa_bayes_empirico(y: pd.Series, e: pd.Series) -> pd.DataFrame:
    """Encolhimento gamma-Poisson por momentos (Clayton e Kaldor, 1987).

    y: acidentes por site; e: exposicao (ou acidentes esperados) por site.
    """
    taxa = y / e
    m = y.sum() / e.sum()
    var_entre = max(np.sum(e * (taxa - m) ** 2) / e.sum() - m / e.mean(), 0.0)
    peso = var_entre / (var_entre + m / e) if var_entre > 0 else 0.0 * e
    return pd.DataFrame({"acidentes": y, "exposicao": e, "taxa_bruta": taxa,
                         "peso": peso, "taxa_eb": peso * taxa + (1 - peso) * m})


def estabilidade_rankings(df: pd.DataFrame, exposicao: str = "horas", escala: float = 1000) -> pd.DataFrame:
    """H1: para cada indicador por site calculado na 1a metade do periodo:
    estabilidade (Spearman com a 2a metade), correlacao com o tamanho (exposicao) e
    erro (ponderado por exposicao) ao prever a taxa bruta da 2a metade, por
    `escala` unidades de exposicao."""
    meio = df["mes"].median()
    metades, metades_e = [], []
    for parte in (df[df["mes"] < meio], df[df["mes"] >= meio]):
        g = parte.groupby("site").agg(y=("acidentes", "sum"), e=(exposicao, "sum"))
        eb = taxa_bayes_empirico(g["y"], g["e"])
        metades_e.append(g["e"])
        metades.append(pd.DataFrame({"contagem": g["y"], "taxa_bruta": eb["taxa_bruta"],
                                     "taxa_eb": eb["taxa_eb"]}))
    a, b = metades[0].align(metades[1], join="inner", axis=0)
    e1, e2 = metades_e[0].reindex(a.index), metades_e[1].reindex(a.index)
    taxa_seguinte = b["taxa_bruta"]
    def _spearman(x, y):  # NaN sem aviso quando o indicador e constante (encolhimento total)
        return stats.spearmanr(x, y).statistic if x.nunique() > 1 and y.nunique() > 1 else np.nan

    linhas = []
    for c in a.columns:
        # contagem nao e taxa: vira previsao proporcional a media geral
        prev = a[c] if c != "contagem" else a[c] / a[c].mean() * a["contagem"].sum() / e1.sum()
        linhas.append({
            "indicador": c,
            "spearman_entre_metades": _spearman(a[c], b[c]),
            "corr_com_tamanho": _spearman(a[c], e1),
            "erro_taxa_seguinte_escalada": escala * float(np.sqrt(np.average((prev - taxa_seguinte) ** 2, weights=e2))),
        })
    return pd.DataFrame(linhas)


def limites_funil(exposicao: np.ndarray, taxa_media: float, nivel: float = 0.998) -> tuple[np.ndarray, np.ndarray]:
    """Limites de controle de Poisson para o grafico de funil (Spiegelhalter, 2005)."""
    esperado = taxa_media * exposicao
    lo = stats.poisson.ppf((1 - nivel) / 2, esperado) / exposicao
    hi = stats.poisson.ppf(1 - (1 - nivel) / 2, esperado) / exposicao
    return lo, hi


# Etapa 4: subnotificacao ------------------------------------------------------

def probabilidade_relato(df: pd.DataFrame) -> pd.DataFrame:
    """P(relatado | detectado) por site, com encolhimento beta-binomial por momentos,
    e estimativa de Lincoln-Petersen do total (supoe fontes independentes; e um
    ponto de partida, nao o modelo final)."""
    g = df.groupby("site").agg(d=("colisoes_detectadas", "sum"), b=("detectadas_e_relatadas", "sum"),
                               r=("acidentes", "sum"))
    g = g[g["d"] > 0]
    p_bruta = g["b"] / g["d"]
    p_media = g["b"].sum() / g["d"].sum()
    var_obs = np.average((p_bruta - p_media) ** 2, weights=g["d"])
    var_binom = np.average(p_media * (1 - p_media) / g["d"], weights=g["d"])
    var_entre = max(var_obs - var_binom, 1e-9)
    peso = var_entre / (var_entre + p_media * (1 - p_media) / g["d"])
    g["p_bruta"], g["p_eb"] = p_bruta, peso * p_bruta + (1 - peso) * p_media
    total_lp = g["r"].sum() * g["d"].sum() / max(g["b"].sum(), 1)
    g.attrs["p_media"], g.attrs["total_lincoln_petersen"] = p_media, total_lp
    return g
