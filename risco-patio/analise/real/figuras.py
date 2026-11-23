"""Figura do estudo preliminar com dados operacionais (fig_real.pdf e fig_real_en.pdf).

So valores relativos (razoes, porcentagens, exposicao relativa a mediana), sem
contagens absolutas nem nomes: pode entrar no pre-projeto. Le os resultados de
analise/real/testes.py e r/h2_misto.R em resultados/real/.

Uso (na raiz do repo):  .venv/Scripts/python.exe analise/real/figuras.py
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import estilo_fig as ef  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
R = RAIZ / "resultados" / "real"
FIG = RAIZ / "dissertacao" / "figuras"

ROT = {
    "Braking": ("frenagem brusca", "harsh braking"),
    "HarshTurn": ("curva brusca", "harsh turn"),
    "FollowingDistance": ("seguir de perto", "following distance"),
    "MaxSpeed": ("acima do limite", "over speed limit"),
    "SevereSpeeding": ("excesso grave", "severe speeding"),
    "MobileUsage": ("uso de celular", "phone use"),
    "GenericDistraction": ("distração", "distraction"),
    "RollingStop": ("parada incompleta", "rolling stop"),
    "NoSeatbelt": ("sem cinto", "no seatbelt"),
    "Drowsy": ("sonolência", "drowsiness"),
}
USO = {"Spot Tractor": ("spotter", "spotter"),
       "Shuttle Tractor": ("shuttle", "shuttle"),
       "Local Tractor": ("local", "local")}

TXT = {
    0: dict(a="(a) Taxa relativa ao spotter", a_y="razão de taxas (escala log)", milha="por milha", hora="por hora",
            b="(b) Funil por site (H1)", b_x="exposição / mediana (escala log)",
            b_y="taxa relativa à média", bruta="bruta", eb="Bayes empírico",
            c="(c) Telemetria e acidentes (H2)", c_x="razão de taxas por 1 DP (IC 95%)",
            c_b="sem ajuste", c_a="uso + efeito de veículo", c_eq="equivalência",
            d="(d) Detecção de colisão (H3)", d_x="%", d_rel="relatos detectados",
            d_desc="detecções\ndescartadas", todos="todos"),
    1: dict(a="(a) Rate relative to spotter", a_y="rate ratio (log scale)", milha="per mile", hora="per hour",
            b="(b) Site funnel (H1)", b_x="exposure / median (log scale)",
            b_y="rate relative to mean", bruta="raw", eb="empirical Bayes",
            c="(c) Telematics and accidents (H2)", c_x="rate ratio per 1 SD (95% CI)",
            c_b="unadjusted", c_a="use + vehicle effect", c_eq="equivalence",
            d="(d) Crash detection (H3)", d_x="%", d_rel="reports detected",
            d_desc="detections\ndismissed", todos="all"),
}


def num(lang):
    if lang == 0:
        return matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
    return matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}")


def wilson(k, n, z=1.96):
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def main():
    ef.aplicar()
    p = pd.read_csv(R / "painel_h2.csv")
    sites = pd.read_csv(R / "sites_h1.csv")
    h2 = pd.read_csv(R / "h2_misto.csv")
    h3 = pd.read_csv(R / "h3_uso.csv").set_index("uso")
    col = pd.read_csv(R / "colisoes.csv.gz")
    det = col[col.lado == "deteccao"]
    k_desc, n_det = det[det.grupo == "descartada"].n.sum(), det.n.sum()

    usos = list(USO)
    taxa_m = {u: p[p.uso == u].acid.sum() / p[p.uso == u].milhas.sum() for u in usos}
    taxa_h = {u: p[p.uso == u].acid.sum() / p[p.uso == u].horas.sum() for u in usos}

    m0 = sites.acid.sum() / (sites.horas.sum() / 1e3)
    med = sites.horas.median()
    grade = np.geomspace(sites.horas.min(), sites.horas.max(), 200)
    esp = m0 * grade / 1e3

    for lang, modo in ef.variantes():
        suf, P = ef.sufixo(lang, modo), ef.paleta(modo)
        t = TXT[lang]
        fig, ax = plt.subplots(2, 2, figsize=(6.3, 6.0), gridspec_kw=dict(hspace=0.55, wspace=0.55))

        # (a) exposicao
        a = ax[0, 0]
        x = np.arange(len(usos))
        a.bar(x - 0.18, [taxa_m[u] / taxa_m[usos[0]] for u in usos], 0.36, color=P["clara"], edgecolor="k", lw=0.5, label=t["milha"])
        a.bar(x + 0.18, [taxa_h[u] / taxa_h[usos[0]] for u in usos], 0.36, color=P["principal"], edgecolor="k", lw=0.5, label=t["hora"])
        a.set_yscale("log")
        a.set_ylim(0.02, 2)
        a.axhline(1, color="0.5", lw=0.6)
        a.set_xticks(x, [USO[u][lang] for u in usos])
        a.yaxis.set_major_formatter(num(lang))
        a.set_ylabel(t["a_y"])
        a.set_title(t["a"])
        a.legend(frameon=False, loc="upper right", fontsize=7)

        # (b) funil
        b = ax[0, 1]
        for nivel, est in [(0.95, "--"), (0.998, ":")]:
            lo = stats.poisson.ppf((1 - nivel) / 2, esp) / esp
            hi = stats.poisson.ppf(1 - (1 - nivel) / 2, esp) / esp
            b.plot(grade / med, lo, "k" + est, lw=0.7)
            b.plot(grade / med, hi, "k" + est, lw=0.7, label=f"{nivel:.1%}".replace(".", "," if lang == 0 else "."))
        b.scatter(sites.horas / med, sites.rel, s=12, facecolors="none", edgecolors=P["principal"], lw=0.6, label=t["bruta"])
        b.scatter(sites.horas / med, sites.rel_eb, s=10, color=P["secundaria"], label=t["eb"])
        b.axhline(1, color="0.5", lw=0.6)
        b.set_xscale("log")
        b.set_ylim(-0.1, 4.5)
        b.xaxis.set_major_formatter(num(lang))
        b.yaxis.set_major_formatter(num(lang))
        b.set_xlabel(t["b_x"])
        b.set_ylabel(t["b_y"])
        b.set_title(t["b"])
        b.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.2))

        # (c) floresta H2
        c = ax[1, 0]
        ordem = list(ROT)
        y = np.arange(len(ordem))[::-1]
        c.axvspan(0.8, 1.25, color=P["faixa"], zorder=0, label=t["c_eq"])
        c.axvline(1, color="0.5", lw=0.6)
        for modelo, dy, mk, cor in [("bruto", 0.17, "o", "white"), ("ajustado", -0.17, "s", P["principal"])]:
            d = h2[h2.modelo == modelo].set_index("rotulo").loc[ordem]
            c.errorbar(d.irr, y + dy, xerr=[d.irr - d.ic95_lo, d.ic95_hi - d.irr], fmt=mk, ms=3.5, mfc=cor,
                       mec="k", ecolor="k", elinewidth=0.7, capsize=1.5, label=t["c_b"] if modelo == "bruto" else t["c_a"])
        c.set_yticks(y, [ROT[r][lang] for r in ordem])
        c.set_xscale("log")
        c.set_xticks([0.6, 0.8, 1, 1.25, 1.6])
        c.tick_params(axis="x", labelsize=7)
        c.xaxis.set_major_formatter(num(lang))
        c.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        c.set_xlabel(t["c_x"])
        c.set_title(t["c"])
        c.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=3, bbox_to_anchor=(0.35, -0.2), handletextpad=0.3, columnspacing=0.8)

        # (d) H3
        d = ax[1, 1]
        nomes, val, lo_, hi_ = [], [], [], []
        k_all, n_all = h3.detectados.sum(), h3.relatos.sum()
        for nome, k, n in ([(USO[u][lang], h3.loc[u, "detectados"], h3.loc[u, "relatos"]) for u in usos]
                           + [(t["todos"], k_all, n_all), (t["d_desc"], k_desc, n_det)]):
            lo, hi = wilson(k, n)
            nomes.append(nome)
            val.append(100 * k / n)
            lo_.append(100 * lo)
            hi_.append(100 * hi)
        yy = np.arange(len(nomes))[::-1]
        cores = [P["clara"]] * len(usos) + [P["secundaria"], P["principal"]]
        d.barh(yy, val, color=cores, edgecolor="k", lw=0.5)
        d.errorbar(val, yy, xerr=[np.array(val) - lo_, np.array(hi_) - val], fmt="none", ecolor="k", elinewidth=0.7, capsize=1.5)
        d.set_yticks(yy, nomes)
        d.set_xlim(0, 100)
        d.set_xlabel(t["d_x"])
        d.text(0.98, 0.98, t["d_rel"], transform=d.transAxes, ha="right", va="top", fontsize=7)
        d.axhline(0.5, color="0.6", lw=0.5, ls=":")
        d.set_title(t["d"])

        for e in ax.flat:
            e.spines[["top", "right"]].set_visible(False)
        fig.subplots_adjust(left=0.2, right=0.98, top=0.95, bottom=0.12)
        fig.savefig(FIG / f"fig_real{suf}.pdf")
        plt.close(fig)
        print("ok", FIG / f"fig_real{suf}.pdf")


if __name__ == "__main__":
    main()
