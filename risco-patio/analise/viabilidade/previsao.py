"""Estudo de viabilidade 2: previsao da exposicao (objetivo opcional f).

Serie: horas de viagem por semana em cada cidade de origem (o "site" do
dataset publico do Kaggle), de 2022 a 2024. Alvo: horas das 4 semanas
seguintes (um "mes"), previstas como distribuicao.

Metodos:
  media8    media das ultimas 8 semanas x 4; quantis dos erros relativos passados
  sazonal   as mesmas 4 semanas do ano anterior; quantis dos erros relativos passados
  ets       ETS aditivo com tendencia amortecida (statsmodels), quantis por simulacao

Avaliacao em origem movel nas ultimas 52 semanas: perda quantilica media
(q = 0,1; 0,5; 0,9) relativa ao valor observado, cobertura do intervalo de 80%.

Pergunta pratica: a incerteza da exposicao pesa na projecao de acidentes? Para
um site com cerca de 1 acidente esperado por mes (ordem de grandeza do
projeto), compara a variancia vinda da exposicao com a variancia de Poisson.

Uso (na raiz do repositorio):
    .venv/Scripts/python analise/viabilidade/previsao.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "analise"))
import dados_publicos  # noqa: E402
import estilo_fig as ef  # noqa: E402

TABELAS = RAIZ / "dissertacao" / "tabelas"
FIGURAS = RAIZ / "dissertacao" / "figuras"
QUANTIS = (0.1, 0.5, 0.9)
H = 4                 # semanas no horizonte
SEMENTE = 20261108


def series_semanais() -> pd.DataFrame:
    p = dados_publicos.PASTA
    trips = pd.read_csv(p / "trips.csv", parse_dates=["dispatch_date"])
    loads = pd.read_csv(p / "loads.csv", usecols=["load_id", "route_id"])
    routes = pd.read_csv(p / "routes.csv", usecols=["route_id", "origin_city"])
    df = trips.merge(loads, on="load_id").merge(routes, on="route_id")
    df["semana"] = df["dispatch_date"].dt.to_period("W").dt.start_time
    s = df.groupby(["origin_city", "semana"])["actual_duration_hours"].sum().unstack(0).fillna(0.0)
    s = s.iloc[1:-1]  # descarta semanas incompletas nas pontas
    return s.loc[:, s.mean() > 0]


def pinball(y, q, tau):
    d = y - q
    return np.maximum(tau * d, (tau - 1) * d)


def quantis_empiricos(hist: np.ndarray, previsor, origens_passadas) -> np.ndarray:
    """Quantis do erro relativo (y / previsao) do proprio metodo no passado."""
    razoes = []
    for t in origens_passadas:
        prev = previsor(hist[:t])
        if prev > 0:
            razoes.append(hist[t:t + H].sum() / prev)
    return np.quantile(razoes, QUANTIS) if len(razoes) >= 8 else np.array([0.8, 1.0, 1.2])


def prev_media8(h):
    return h[-8:].mean() * H


def prev_sazonal(h):
    return h[-52:-52 + H].sum() if len(h) >= 52 else h[-H:].sum()


def prev_ets(h, rng):
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = ETSModel(pd.Series(h), error="add", trend="add", damped_trend=True).fit(disp=False)
        sim = m.simulate(nsimulations=H, repetitions=500, anchor="end", rng=np.random.default_rng(rng.integers(1e9)))
    tot = np.clip(sim.sum(axis=0).to_numpy(), 0, None)
    return np.quantile(tot, QUANTIS)


def main() -> None:
    rng = np.random.default_rng(SEMENTE)
    s = series_semanais()
    n = len(s)
    origens = list(range(n - 52, n - H + 1, H))
    linhas = []
    for site in s.columns:
        h = s[site].to_numpy()
        for t in origens:
            y = h[t:t + H].sum()
            passadas = list(range(26, t - H + 1, 2))
            for nome, prev in (("media8", prev_media8), ("sazonal", prev_sazonal)):
                base = prev(h[:t])
                q = base * quantis_empiricos(h[:t], prev, passadas)
                linhas.append((site, t, nome, y, *q))
            linhas.append((site, t, "ets", y, *prev_ets(h[:t], rng)))
    r = pd.DataFrame(linhas, columns=["site", "origem", "metodo", "y", "q10", "q50", "q90"])
    r = r[r["y"] > 0]
    for tau, c in zip(QUANTIS, ("q10", "q50", "q90")):
        r[f"pb{c[1:]}"] = pinball(r["y"], r[c], tau) / r["y"]
    r["perda"] = r[["pb10", "pb50", "pb90"]].mean(axis=1)
    r["cobre80"] = (r["y"] >= r["q10"]) & (r["y"] <= r["q90"])
    r["erro_mediana"] = (r["q50"] - r["y"]).abs() / r["y"]
    t = r.groupby("metodo").agg(perda=("perda", "mean"), cobre80=("cobre80", "mean"),
                                erro_mediana=("erro_mediana", "median"))

    # Peso da incerteza da exposicao na projecao de acidentes (site com ~1 acidente/mes)
    e = r[r["metodo"] == "ets"].copy()
    sd_h = (e["q90"] - e["q10"]) / (2 * 1.2816)
    lam = 1.0 / e["q50"]                       # taxa que da 1 acidente esperado no mes
    var_exp = (lam * sd_h) ** 2
    frac = var_exp / (var_exp + lam * e["q50"])
    frac_med = float(frac.median())

    print(f"{s.shape[1]} sites (cidades de origem), {n} semanas; {len(origens)} origens de previsao")
    print(t.round(3).to_string())
    print(f"fracao mediana da variancia de acidentes vinda da exposicao (1 acidente/mes): {frac_med:.3f}")

    TABELAS.mkdir(parents=True, exist_ok=True)
    nomes = {"media8": "\\tr{Média de 8 semanas}{8-week mean}", "sazonal": "\\tr{Sazonal ingênuo}{Seasonal naive}",
             "ets": "\\tr{ETS amortecido}{Damped ETS}"}
    v = lambda x: f"{x:.3f}".replace(".", ",")
    corpo = [f"{nomes[m]} & {v(row['perda'])} & {v(row['cobre80'])} & {v(row['erro_mediana'])} \\\\"
             for m, row in t.loc[["media8", "sazonal", "ets"]].iterrows()]
    (TABELAS / "tab_previsao.tex").write_text("\n".join(corpo) + "\n", encoding="utf-8")
    (TABELAS / "num_previsao.tex").write_text(
        f"\\newcommand{{\\nsitesprev}}{{{s.shape[1]}}}\n\\newcommand{{\\nsemanas}}{{{n}}}\n"
        f"\\newcommand{{\\fracexposicao}}{{{frac_med * 100:.0f}}}\n", encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ef.aplicar(9)
    site = s.mean().idxmax()
    ex = r[(r["site"] == site) & (r["metodo"] == "ets")].sort_values("origem")
    textos = (dict(obs="horas em 4 semanas (observado)", faixa="intervalo de 80% (ETS)", med="mediana prevista",
                   y="horas de viagem", titulo="Previsão de exposição, site com maior volume (dados públicos)"),
              dict(obs="4-week hours (observed)", faixa="80% interval (ETS)", med="forecast median",
                   y="trip hours", titulo="Exposure forecast, highest-volume site (public data)"))
    FIGURAS.mkdir(parents=True, exist_ok=True)
    for lang, modo in ef.variantes():
        t, P = textos[lang], ef.paleta(modo)
        fig, ax = plt.subplots(figsize=(ef.LARGURA, 2.6))
        datas = s.index
        ax.plot(datas, s[site].rolling(H).sum().shift(-(H - 1)), color=P["secundaria"], lw=0.8, label=t["obs"])
        x = datas[ex["origem"]]
        ax.fill_between(x, ex["q10"], ex["q90"], color=P["faixa"], label=t["faixa"])
        ax.plot(x, ex["q50"], ".", color=P["principal"], ms=4, label=t["med"])
        ax.set_ylabel(t["y"])
        ax.set_title(t["titulo"], fontsize=9)
        ax.legend(frameon=False, fontsize=7, loc="lower left")
        fig.tight_layout()
        fig.savefig(FIGURAS / f"fig_previsao{ef.sufixo(lang, modo)}.pdf")
        plt.close(fig)


if __name__ == "__main__":
    main()
