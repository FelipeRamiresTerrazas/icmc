"""Figura 1 do projeto do RateIQ: cadeia de calculo da taxa por hora, com exemplo ficticio.

Fontes publicas -> correspondencia geografica -> salario estimado p (com faixa)
-> taxa b = p (1 + c) h / (1 - m).

Os numeros do exemplo sao FICTICIOS, redondos e so ilustrativos: nao vem de dados
da empresa nem de nenhuma fonte. O script calcula a cadeia (para a figura e o texto
nunca divergirem) e grava as macros em rateiq/preprojeto/tabelas/num_exemplo.tex.

Gera as quatro variantes (PT/EN, cor/P&B) com a paleta de risco-patio/analise/estilo_fig.py.
Uso (na raiz do repo):  .venv/Scripts/python rateiq/analise/fig_cadeia.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "risco-patio" / "analise"))
import estilo_fig as ef  # noqa: E402

DOC = RAIZ / "rateiq" / "preprojeto"
FIG = DOC / "figuras"
TAB = DOC / "tabelas"

# exemplo ficticio (US$/h e fracoes)
P, P_INF, P_SUP = 20.0, 18.0, 22.0   # salario estimado e faixa
C = 0.25                              # encargos sobre a folha
H = 1.20                              # horas pagas / horas faturaveis
M = 0.25                              # margem


def taxa(p):
    return p * (1 + C) * H / (1 - M)


def passos(p):
    """Valores intermediarios da cadeia: p, p(1+c), p(1+c)h, b."""
    a = p * (1 + C)
    return p, a, a * H, a * H / (1 - M)


def fmt(x, lang, casas=2):
    s = f"{x:,.{casas}f}"
    return s if lang else s.replace(",", "X").replace(".", ",").replace("X", ".")


TXT = {
    "fontes": ("Fontes públicas", "Public sources"),
    "oews": ("OEWS: salário por ocupação\ne área metropolitana, com erro", "OEWS: wage by occupation\nand metro area, with error"),
    "rpp": ("BEA: paridades regionais\nde preço (custo de vida)", "BEA: regional price\nparities (cost of living)"),
    "cov": ("QCEW, ACS, salário mínimo:\ncovariáveis por condado", "QCEW, ACS, minimum wage:\ncounty covariates"),
    "hud": ("HUD-USPS: pesos de\ncorrespondência ZIP-condado", "HUD-USPS: ZIP-county\ncorrespondence weights"),
    "int": ("Dados internos: salário pago\ne taxa faturada (calibração)", "Internal data: wage paid\nand billed rate (calibration)"),
    "corr": ("Correspondência geográfica\nárea publicada → ZIP3", "Geographic correspondence\npublished area → ZIP3"),
    "modelo": ("Modelo de pequenas áreas\n(pondera pela precisão)", "Small area model\n(weights by precision)"),
    "p": ("Salário estimado $p$", "Estimated wage $p$"),
    "c": ("× $(1+c)$ encargos, $c$ = {c}", "× $(1+c)$ payroll burden, $c$ = {c}"),
    "h": ("× $h$ horas pagas/faturáveis, $h$ = {h}", "× $h$ paid/billable hours, $h$ = {h}"),
    "m": ("÷ $(1-m)$ margem, $m$ = {m}", "÷ $(1-m)$ margin, $m$ = {m}"),
    "b": ("Taxa recomendada $b$", "Recommended rate $b$"),
    "faixa": ("faixa de {a} a {b}", "range {a} to {b}"),
    "un": ("US\\$/h", "US\\$/h"),
    "nota": ("Exemplo ilustrativo, com valores fictícios.", "Illustrative example with fictitious values."),
    "cadeia": ("Cadeia da taxa (exemplo)", "Rate chain (example)"),
}


def caixa(ax, x, y, w, h, texto, cor, borda, estilo="-", cor_txt="black", peso="normal", tam=7.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=cor, ec=borda, lw=0.8, ls=estilo))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=tam, color=cor_txt,
            weight=peso, linespacing=1.15)


def seta(ax, a, b, cor, estilo="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, lw=0.8, color=cor, ls=estilo,
                                 shrinkA=0, shrinkB=0))


def figura(lang, modo):
    pal = ef.paleta(modo)
    t = {k: v[lang] for k, v in TXT.items()}
    un = t["un"]
    largura, altura = ef.LARGURA, 3.35
    fig = plt.figure(figsize=(largura, altura))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.axis("off")

    # coluna 1: fontes
    x1, w1, h1 = 0.05, 1.95, 0.46
    ax.text(x1 + w1 / 2, 3.18, t["fontes"], ha="center", va="center", fontsize=7.6, weight="bold",
            color=pal["principal"])
    ys = [2.55, 1.98, 1.41, 0.84]
    for y, k in zip(ys, ["oews", "hud", "rpp", "cov"]):
        caixa(ax, x1, y, w1, h1, t[k], pal["caixa"], pal["linha"])
    y_int = 0.12
    caixa(ax, x1, y_int, w1, h1, t["int"], "white", pal["linha"], estilo="--")

    # coluna 2: correspondencia e modelo
    x2, w2, h2 = 2.30, 1.70, 0.62
    y_corr, y_mod = 2.05, 0.95
    caixa(ax, x2, y_corr, w2, h2, t["corr"], pal["fundo2"], pal["linha"])
    caixa(ax, x2, y_mod, w2, h2, t["modelo"], pal["fundo2"], pal["linha"])
    for y in ys:
        alvo = (x2, y_corr + h2 / 2) if y > 1.9 else (x2, y_mod + h2 * 0.7)
        seta(ax, (x1 + w1, y + h1 / 2), alvo, pal["linha"])
    seta(ax, (x1 + w1, y_int + h1 / 2), (x2, y_mod + h2 * 0.25), pal["linha"], estilo="--")
    seta(ax, (x2 + w2 / 2, y_corr), (x2 + w2 / 2, y_mod + h2), pal["linha"])

    # coluna 3: cadeia da taxa
    x3, w3, h3 = 4.20, 2.05, 0.50
    ax.text(x3 + w3 / 2, 3.18, t["cadeia"], ha="center", va="center", fontsize=7.6, weight="bold",
            color=pal["principal"])
    v, vi, vs = passos(P), passos(P_INF), passos(P_SUP)
    linhas = [
        (t["p"] + f"\n{fmt(v[0], lang)} {un}  ({t['faixa'].format(a=fmt(vi[0], lang), b=fmt(vs[0], lang))})",
         pal["fundo1"]),
        (t["c"].format(c=fmt(C, lang)) + f"\n= {fmt(v[1], lang)} {un}", pal["fundo1"]),
        (t["h"].format(h=fmt(H, lang)) + f"\n= {fmt(v[2], lang)} {un}", pal["fundo1"]),
        (t["m"].format(m=fmt(M, lang)) + f"\n= {fmt(v[3], lang)} {un}", pal["fundo1"]),
    ]
    yc = [2.55, 1.85, 1.15, 0.45]
    for (txt, cor), y in zip(linhas, yc):
        caixa(ax, x3, y, w3, h3, txt, cor, pal["linha"], tam=6.9)
    for a, b in zip(yc[:-1], yc[1:]):
        seta(ax, (x3 + w3 / 2, a), (x3 + w3 / 2, b + h3), pal["linha"])
    seta(ax, (x2 + w2, y_mod + h2 / 2), (x3, yc[0] + h3 / 2), pal["linha"])
    # resultado final, destacado
    yb, hb = -0.02, 0.36
    ax.set_ylim(-0.30, altura)
    caixa(ax, x3, yb - 0.18, w3, hb,
          t["b"] + f" = {fmt(v[3], lang)} {un}\n" + t["faixa"].format(a=fmt(vi[3], lang), b=fmt(vs[3], lang)),
          pal["principal"], pal["linha"], cor_txt="white", peso="bold", tam=6.7)
    seta(ax, (x3 + w3 / 2, yc[-1]), (x3 + w3 / 2, yb - 0.18 + hb), pal["linha"])
    ax.text(x2 + w2 / 2, 0.30, t["nota"], ha="center", va="center", fontsize=6.6, style="italic",
            color=pal["referencia"])
    fig.set_size_inches(largura, altura + 0.30)
    return fig


def macros():
    """Numeros do exemplo para o texto (nunca digitados no .tex)."""
    v, vi, vs = passos(P), passos(P_INF), passos(P_SUP)
    linhas = [
        "% Gerado por rateiq/analise/fig_cadeia.py (exemplo FICTICIO). Nao editar a mao.",
        f"\\newcommand{{\\exSalario}}{{{P:.2f}}}",
        f"\\newcommand{{\\exSalarioInf}}{{{P_INF:.2f}}}",
        f"\\newcommand{{\\exSalarioSup}}{{{P_SUP:.2f}}}",
        f"\\newcommand{{\\exEncargos}}{{{C:.2f}}}",
        f"\\newcommand{{\\exHoras}}{{{H:.2f}}}",
        f"\\newcommand{{\\exMargem}}{{{M:.2f}}}",
        f"\\newcommand{{\\exFator}}{{{(1 + C) * H / (1 - M):.2f}}}",
        f"\\newcommand{{\\exTaxa}}{{{v[3]:.2f}}}",
        f"\\newcommand{{\\exTaxaInf}}{{{vi[3]:.2f}}}",
        f"\\newcommand{{\\exTaxaSup}}{{{vs[3]:.2f}}}",
    ]
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / "num_exemplo.tex").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    ef.aplicar()
    matplotlib.rcParams["mathtext.fontset"] = "dejavuserif"  # simbolos serifados, como o texto
    FIG.mkdir(parents=True, exist_ok=True)
    for lang, modo in ef.variantes():
        fig = figura(lang, modo)
        arq = FIG / f"fig_cadeia{ef.sufixo(lang, modo)}.pdf"
        fig.savefig(arq)
        plt.close(fig)
        print(arq.relative_to(RAIZ))
    macros()
    print((TAB / "num_exemplo.tex").relative_to(RAIZ))


if __name__ == "__main__":
    main()
