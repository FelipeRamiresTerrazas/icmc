"""Roda o esqueleto inteiro com o painel SINTETICO e grava saidas de teste.

Uso (na raiz do repositorio mestrado):
    .venv/Scripts/python analise/rodar_exemplo.py

Saidas em resultados/ (fora do git). Sao numeros de dados simulados:
servem para conferir o pipeline, nunca para citar no texto.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import modelos  # noqa: E402
import painel_sintetico  # noqa: E402

SAIDA = Path(__file__).resolve().parents[1] / "resultados"


def main() -> None:
    SAIDA.mkdir(exist_ok=True)
    painel, verdade = painel_sintetico.gerar()
    print(f"painel: {len(painel)} linhas, {painel['site'].nunique()} sites, "
          f"{painel['acidentes'].sum()} acidentes relatados (verdadeiros: {verdade['acidentes_verdadeiros']})")

    # Etapa 2: coeficientes de telemetria contra os verdadeiros
    res = modelos.ajustar(painel, "nb", modelos.COVARIAVEIS_TELEMETRIA)
    print("\ncoeficientes de telemetria (estimado | verdadeiro):")
    for c in modelos.COVARIAVEIS_TELEMETRIA:
        lo, hi = res.conf_int().loc[c]
        print(f"  {c:14s} {res.params[c]:+.3f} [{lo:+.3f}, {hi:+.3f}] | {verdade['beta'][c]:+.3f}")
    print(f"  alpha (dispersao) {res.params['alpha']:.3f}")

    # Etapa 3: validacao temporal (H2) e estabilidade dos rankings (H1)
    val = modelos.validacao_temporal(painel)
    est = modelos.estabilidade_rankings(painel)
    print("\nvalidacao temporal:\n", val.round(4).to_string(index=False))
    print("\nestabilidade dos rankings entre metades:\n", est.round(3).to_string(index=False))

    # Etapa 4: subnotificacao
    rel = modelos.probabilidade_relato(painel)
    print(f"\nP(relato | detectado) media: {rel.attrs['p_media']:.2f}; "
          f"total Lincoln-Petersen: {rel.attrs['total_lincoln_petersen']:.0f}")

    # Grafico de funil por site
    g = painel.groupby("site").agg(y=("acidentes", "sum"), e=("horas", "sum"))
    eb = modelos.taxa_bayes_empirico(g["y"], g["e"])
    m = g["y"].sum() / g["e"].sum()
    grade = np.linspace(g["e"].min() * 0.8, g["e"].max() * 1.1, 200)
    fig, ax = plt.subplots(figsize=(6.3, 4))
    for nivel, estilo in ((0.95, ":"), (0.998, "--")):
        lo, hi = modelos.limites_funil(grade, m, nivel)
        ax.plot(grade, hi * 1000, "k" + estilo, lw=0.8)
        ax.plot(grade, lo * 1000, "k" + estilo, lw=0.8)
    ax.axhline(m * 1000, color="k", lw=0.8)
    ax.scatter(g["e"], eb["taxa_bruta"] * 1000, s=14, label="taxa bruta")
    ax.scatter(g["e"], eb["taxa_eb"] * 1000, s=14, marker="x", label="bayes empírico")
    ax.set_xlabel("horas de operação no período")
    ax.set_ylabel("acidentes por 1.000 h")
    ax.set_title("Dados sintéticos", fontsize=9)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(SAIDA / "funil_sintetico.pdf")
    print(f"\nfigura: {SAIDA / 'funil_sintetico.pdf'}")


if __name__ == "__main__":
    main()
