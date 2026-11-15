"""Capitulo de analise descritiva: figuras e tabela com os dados da operacao.

So valores relativos (proporcoes, indices em relacao a media, razoes e
exposicao relativa a mediana), sem contagens absolutas, nomes ou codigos de
unidade: as saidas podem entrar no texto. Le os agregados de resultados/real/
(gerados por extrair.py) e reaproveita o painel de testes.py.

Saidas (dissertacao/):
  figuras/fig_desc_{exposicao,concentracao,tempo,tipos,fontes}[_en].pdf
  figuras/fig_desc_pp[_en].pdf          figura composta para o pre-projeto
  tabelas/tab_descritiva.tex            linhas da tabela-resumo
  tabelas/num_descritiva.tex            macros com os numeros citados no texto

Uso (na raiz do repo):  .venv/Scripts/python.exe analise/real/descritiva.py
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import testes  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import estilo_fig as ef  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
R = RAIZ / "resultados" / "real"
FIG = RAIZ / "dissertacao" / "figuras"
TAB = RAIZ / "dissertacao" / "tabelas"
SEMENTE = 20261115
RNG = np.random.default_rng(SEMENTE)
LARG = ef.LARGURA
P = ef.paleta("cor")  # trocada a cada variante em main()
MODO = "cor"

USOS = ["Spot Tractor", "Shuttle Tractor", "Local Tractor"]
NOME_USO = {"Spot Tractor": ("spotter", "spotter"), "Shuttle Tractor": ("shuttle", "shuttle"),
            "Local Tractor": ("local", "local")}
CAUSAS = {
    "Trailer door/Equipment Securing issues": ("porta da carreta / fixação", "trailer door / securing"),
    "Operational Error": ("erro operacional", "operational error"),
    "Improper backing/misjudged clearance": ("ré / folga mal avaliada", "backing / misjudged clearance"),
    "Struck Fixed Object": ("colisão com objeto fixo", "struck fixed object"),
    "Dropped Trailer/Landing gear": ("carreta caída / pé de apoio", "dropped trailer / landing gear"),
    "Other": ("outra", "other"),
    "Trailer connection/coupling issues - Airlines": ("engate / mangueiras de ar", "coupling / air lines"),
    "Yard Maneuvering/Limited Space": ("manobra em espaço restrito", "maneuvering / limited space"),
    "Struck another vehicle": ("bateu em outro veículo", "struck another vehicle"),
    "Equipment/Mechanical Failure": ("falha mecânica", "mechanical failure"),
    "Struck by another vehicle/3rd party": ("atingido por outro veículo", "struck by another vehicle"),
    "3rd Party": ("terceiro", "third party"),
}
TIPOS = {"accident_incident": ("acidente", "accident"), "work_injury": ("lesão", "injury"), "other": ("outro", "other")}
DIAS = (["seg", "ter", "qua", "qui", "sex", "sáb", "dom"], ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
MESES = (["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"],
         ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])


def tr(lang, pt, en):
    return pt if lang == 0 else en


def fmt(lang, casas=1):
    sep = "," if lang == 0 else "."
    return matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:.{casas}f}".rstrip("0").rstrip(".").replace(".", sep)
                                           if casas else f"{x:.0f}")


def gfmt(lang):
    return matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}".replace(".", "," if lang == 0 else "."))


def rot_mes(datas, lang):
    return [(f"{MESES[lang][d.month - 1]}\n{d.year % 100:02d}" if d.month == 1 or i == 0 else MESES[lang][d.month - 1])
            if i % 2 == 0 else "" for i, d in enumerate(datas)]


def limpa(ax):
    ax.spines[["top", "right"]].set_visible(False)


def num_tex(x, casas):
    s = f"{x:.{casas}f}"
    return f"\\tr{{{s.replace('.', ',')}}}{{{s}}}"


# ---------------------------------------------------------------- dados
def carregar():
    p, _ = testes.painel()
    d = dict(p=p)
    d["horario"] = pd.read_csv(R / "horario.csv.gz", parse_dates=["mes"])
    d["causas"] = pd.read_csv(R / "causas.csv.gz", parse_dates=["mes"])
    d["manut"] = pd.read_csv(R / "manutencao.csv.gz", parse_dates=["mes"])
    d["aud"] = pd.read_csv(R / "auditorias.csv.gz", parse_dates=["mes"])
    d["adp"] = pd.read_csv(R / "adp.csv.gz", parse_dates=["week_start"])
    ev = pd.read_csv(R / "eventos.csv.gz", parse_dates=["mes"])
    d["crash"] = ev[ev.label == "Crash"].groupby("mes")[["n_todos", "n_mantidos"]].sum()
    return d


def lorenz(x):
    x = np.sort(np.asarray(x, float))[::-1]
    y = np.concatenate([[0], np.cumsum(x) / x.sum()])
    return np.linspace(0, 1, len(y)), y


def gini_desc(x):
    xx, yy = lorenz(x)
    return 2 * np.trapezoid(yy, xx) - 1


def esperado_poisson(g, p):
    """Acidentes esperados por grupo sob taxa homogenea dentro de cada tipo de uso."""
    taxa = p.groupby("uso").acid.sum() / p.groupby("uso").horas.sum()
    return (p.horas * p.uso.map(taxa)).groupby(p[g]).sum()


# ---------------------------------------------------------------- paineis
def pn_box_uso(ax, p, col, lang, titulo, ylab):
    v = p[p.uso.isin(USOS)].copy()
    v["x"] = col(v)
    med = v.x.median()
    dados = [v.loc[v.uso == u, "x"] / med for u in USOS]
    ax.boxplot(dados, widths=0.55, showfliers=False, medianprops=dict(color="k"),
               boxprops=dict(facecolor=P["caixa"]), patch_artist=True)
    for i, y in enumerate(dados, start=1):
        ax.scatter(i + RNG.uniform(-0.18, 0.18, len(y)), y, s=1.5, color=P["pontos"], alpha=0.35, lw=0)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(base=10, subs=(1, 2, 5)))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.axhline(1, color="0.5", lw=0.6, ls=":")
    ax.set_xticks([1, 2, 3], [NOME_USO[u][lang] for u in USOS])
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_ylabel(ylab)
    ax.set_title(titulo)
    limpa(ax)


def pn_horas_extras(ax, adp, lang, titulo):
    a = adp.assign(mes=adp.week_start.dt.to_period("M"))
    w = a.pivot_table(index=["site", "mes"], columns="pay_code_category", values="horas", aggfunc="sum", fill_value=0)
    w["tot"] = w.sum(axis=1)
    w = w[w.tot >= w.tot.quantile(0.10)]
    share = 100 * w["Over Time"] / w.tot
    ax.hist(share, bins=np.arange(0, 41, 2), color=P["barra"], edgecolor="k", lw=0.4)
    ax.axvline(share.median(), color=P["linha"], lw=0.8, ls="--")
    ax.set_xlabel(tr(lang, "horas extras / horas totais (%)", "overtime / total hours (%)"))
    ax.set_ylabel(tr(lang, "unidade-meses", "site-months"))
    ax.set_yticks([])
    ax.set_title(titulo)
    limpa(ax)
    return share


def pn_lorenz(ax, p, g, lang, titulo):
    t = p.groupby(g).agg(acid=("acid", "sum"), horas=("horas", "sum"))
    e = esperado_poisson(g, p).reindex(t.index)
    sims = np.array([lorenz(RNG.poisson(e))[1] for _ in range(300)])
    x, y_obs = lorenz(t.acid)
    ax.plot([0, 1], [0, 1], color="0.7", lw=0.6)
    ax.plot(*lorenz(t.horas), color=P["secundaria"], lw=1, ls="--", label=tr(lang, "horas", "hours"))
    ax.fill_between(x, np.percentile(sims, 2.5, axis=0), np.percentile(sims, 97.5, axis=0), color=P["faixa"], lw=0,
                    label=tr(lang, "acidentes sob Poisson", "accidents under Poisson"))
    ax.plot(x, y_obs, color=P["principal"], lw=1.2, label=tr(lang, "acidentes observados", "observed accidents"))
    ax.set_xlabel(tr(lang, f"fração acumulada de {'veículos' if g == 'vehicle_id' else 'unidades'}",
                     f"cumulative share of {'vehicles' if g == 'vehicle_id' else 'sites'}"))
    ax.set_ylabel(tr(lang, "fração acumulada", "cumulative share"))
    ax.xaxis.set_major_formatter(gfmt(lang))
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_title(titulo)
    ax.legend(frameon=False, fontsize=6.5, loc="lower right")
    limpa(ax)
    return gini_desc(t.acid), float(np.mean([gini_desc(RNG.poisson(e)) for _ in range(300)])), gini_desc(t.horas)


def pn_caterpillar(ax, p, lang, titulo):
    t = p.dropna(subset=["site_m"]).groupby("site_m").agg(acid=("acid", "sum"))
    e = esperado_poisson("site_m", p.dropna(subset=["site_m"])).reindex(t.index)
    t, e = t[e >= 1], e[e >= 1]
    t["oe"] = t.acid / e
    t["lo"] = np.where(t.acid > 0, stats.chi2.ppf(0.025, 2 * t.acid) / 2, 0) / e
    t["hi"] = stats.chi2.ppf(0.975, 2 * t.acid + 2) / 2 / e
    t = t.sort_values("oe")
    x = np.linspace(0, 1, len(t))
    fora = (t.lo > 1) | (t.hi < 1)
    ax.vlines(x, np.maximum(t.lo, 0.05), t.hi, color=np.where(fora, P["destaque"], P["neutro"]), lw=0.8)
    ax.scatter(x, np.maximum(t.oe, 0.05), s=8, color=np.where(fora, P["destaque"], P["neutro"]), zorder=3)
    ax.axhline(1, color="0.5", lw=0.6, ls=":")
    ax.set_yscale("log")
    ax.set_ylim(0.05, 10)
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_xticks([])
    ax.set_xlabel(tr(lang, "unidades ordenadas", "sites in order"))
    ax.set_ylabel(tr(lang, "observado / esperado (IC 95%)", "observed / expected (95% CI)"))
    ax.set_title(titulo)
    limpa(ax)
    return fora.mean()


def pn_tamanho(ax, p, lang, titulo):
    h = p.dropna(subset=["site_m"]).groupby("site_m").horas.sum()
    r = h / h.median()
    ax.hist(r, bins=np.geomspace(r.min() * 0.9, r.max() * 1.1, 14), color=P["barra"], edgecolor="k", lw=0.4)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(gfmt(lang))
    ax.set_xlabel(tr(lang, "horas de viagem / mediana (escala log)", "trip hours / median (log scale)"))
    ax.set_ylabel(tr(lang, "unidades", "sites"))
    ax.set_yticks([])
    ax.set_title(titulo)
    limpa(ax)
    return np.percentile(h, 90) / np.percentile(h, 10)


def relatos_acid(horario, ate="2026-11-01"):
    h = horario[(horario.incident_type == "accident_incident") & (horario.mes < ate)]
    return h


def pn_mensal(ax, horario, lang, titulo):
    h = relatos_acid(horario)
    m = h.pivot_table(index="mes", columns="suspeito_teste", values="n", aggfunc="sum", fill_value=0)
    media = m.sum(axis=1).mean()
    x = np.arange(len(m))
    ax.bar(x, m.get(0, 0) / media, color=P["principal"], width=0.75, label=tr(lang, "relatos", "reports"))
    ax.bar(x, m.get(1, 0) / media, bottom=m.get(0, 0) / media, color=P["clara"], edgecolor=P["referencia"], lw=0.3, width=0.75,
           hatch="////", label=tr(lang, "suspeitos de teste", "suspected tests"))
    ax.axhline(1, color="0.5", lw=0.6, ls=":")
    ax.set_xticks(x, rot_mes(m.index, lang), fontsize=6)
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_ylabel(tr(lang, "acidentes / média mensal", "accidents / monthly mean"))
    ax.set_title(titulo)
    ax.set_ylim(0, 1.9)
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=2)
    limpa(ax)
    return 100 * m.get(1, 0).sum() / m.values.sum()


def pn_hora(ax, horario, lang, titulo):
    h = relatos_acid(horario)
    h = h[h.suspeito_teste == 0]
    preench = h.dropna(subset=["hora"]).n.sum() / h.n.sum()
    s = h.dropna(subset=["hora"]).groupby("hora").n.sum().reindex(range(24), fill_value=0)
    s = 100 * s / s.sum()
    for a, b, cor in [(6, 14, P["fundo1"]), (14, 22, P["fundo2"]), (22, 24, P["fundo1"]), (0, 6, P["fundo1"])]:
        ax.axvspan(a - 0.5, b - 0.5, color=cor, lw=0, zorder=0)
    ax.bar(s.index, s.values, color=P["principal"], width=0.8)
    ax.axhline(100 / 24, color="k", lw=0.6, ls=":")
    for x0, nome in [(10, "1"), (18, "2"), (2, "3")]:
        ax.text(x0 - 0.5, ax.get_ylim()[1] * 0.98 if False else s.max() * 1.12, tr(lang, f"turno {nome}", f"shift {nome}"),
                ha="center", fontsize=6.5)
    ax.set_ylim(0, s.max() * 1.22)
    ax.set_xticks([0, 6, 12, 18, 23])
    ax.set_xlabel(tr(lang, "hora do acidente", "hour of accident"))
    ax.set_ylabel(tr(lang, "% dos acidentes", "% of accidents"))
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_title(titulo)
    limpa(ax)
    turnos = {1: s.loc[6:13].sum(), 2: s.loc[14:21].sum(), 3: s.loc[22:23].sum() + s.loc[0:5].sum()}
    return preench, turnos


def pn_dia(ax, horario, lang, titulo):
    h = relatos_acid(horario)
    h = h[(h.suspeito_teste == 0)].dropna(subset=["dia_semana"])
    s = h.groupby("dia_semana").n.sum().reindex(range(1, 8), fill_value=0)
    s = 100 * s / s.sum()
    ax.bar(range(7), s.values, color=P["principal"], width=0.7)
    ax.axhline(100 / 7, color="k", lw=0.6, ls=":")
    ax.set_xticks(range(7), DIAS[lang])
    ax.set_ylabel(tr(lang, "% dos acidentes", "% of accidents"))
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_title(titulo)
    limpa(ax)


def pn_semanal(ax, adp, p, lang, titulo):
    w = adp.groupby("week_start").horas.sum()
    w = w[(w.index >= "2025-07-01") & (w.index <= "2026-10-25")]
    ax.plot(w.index, w / w.mean(), color=P["secundaria"], lw=0.9, label=tr(lang, "horas da folha (semana)", "payroll hours (week)"))
    m = p.groupby("mes").horas.sum()
    ax.plot(m.index + pd.Timedelta(days=14), m / m.mean(), "o-", color=P["principal"], ms=3, lw=0.9,
            label=tr(lang, "horas de viagem (mês)", "trip hours (month)"))
    ax.axhline(1, color="0.5", lw=0.6, ls=":")
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: (lambda d: f"{MESES[lang][d.month - 1]}/{d.year % 100:02d}")(matplotlib.dates.num2date(v))))
    ax.tick_params(axis="x", labelsize=6.5)
    ax.set_ylabel(tr(lang, "relativo à média", "relative to mean"))
    ax.set_title(titulo)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left", handlelength=1.8, borderaxespad=0.2)
    limpa(ax)


def pn_tipos(ax, causas, lang, titulo):
    c = causas[(causas.mes < "2026-11-01")]
    s = c.groupby("incident_type").n.sum()
    s = 100 * s / s.sum()
    ordem = ["accident_incident", "work_injury", "other"]
    ax.barh(range(3)[::-1], [s.get(k, 0) for k in ordem], color=[P["principal"], P["secundaria"], P["terciaria"]], edgecolor="k", lw=0.4)
    ax.set_yticks(range(3)[::-1], [TIPOS[k][lang] for k in ordem])
    ax.set_xlim(0, 100)
    ax.set_xlabel(tr(lang, "% dos relatos", "% of reports"))
    ax.set_title(titulo)
    limpa(ax)
    return s.get("accident_incident", 0)


def pn_uso_share(ax, p, lang, titulo):
    v = p[p.uso.isin(USOS)]
    a = 100 * v.groupby("uso").acid.sum().reindex(USOS) / v.acid.sum()
    h = 100 * v.groupby("uso").horas.sum().reindex(USOS) / v.horas.sum()
    mi = 100 * v.groupby("uso").milhas.sum().reindex(USOS) / v.milhas.sum()
    x = np.arange(3)
    ax.bar(x - 0.27, a, 0.27, color=P["principal"], label=tr(lang, "acidentes", "accidents"))
    ax.bar(x, h, 0.27, color=P["secundaria"], label=tr(lang, "horas", "hours"))
    ax.bar(x + 0.27, mi, 0.27, color=P["terciaria"], edgecolor="k", lw=0.4, label=tr(lang, "milhas", "miles"))
    ax.set_xticks(x, [NOME_USO[u][lang] for u in USOS])
    ax.set_ylabel("%")
    ax.set_ylim(0, 100)
    ax.set_title(titulo)
    ax.legend(frameon=False, fontsize=6.5, loc="upper center", ncol=3, handlelength=1)
    limpa(ax)


def pn_causas(ax, causas, lang, titulo):
    c = causas[(causas.incident_type == "accident_incident") & (causas.mes < "2026-11-01")]
    s = c.groupby("accident_root_cause").n.sum()
    s = (100 * s / s.sum()).sort_values()
    ax.barh(range(len(s)), s.values, color=P["barra"], edgecolor="k", lw=0.4)
    ax.set_yticks(range(len(s)), [CAUSAS.get(k, (k, k))[lang] for k in s.index], fontsize=7)
    ax.set_xlabel(tr(lang, "% dos acidentes", "% of accidents"))
    ax.xaxis.set_major_formatter(gfmt(lang))
    ax.set_title(titulo)
    limpa(ax)
    return s


def pn_fontes(ax, d, lang, titulo):
    ini, fim = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-01")
    h = relatos_acid(d["horario"])
    rel = h[h.suspeito_teste == 0].groupby("mes").n.sum()
    man = d["manut"].groupby("mes").ordens.sum()
    cr = d["crash"]
    series = [(rel, tr(lang, "relatos de acidente", "accident reports"), P["principal"], "o-"),
              (man, tr(lang, "ordens de dano", "damage orders"), P["secundaria"], "s--"),
              (cr.n_todos, tr(lang, "colisões detectadas", "detected collisions"), P["terciaria"], "^-")]
    meses = pd.date_range(ini, fim, freq="MS")
    for s, nome, cor, est in series:
        s = s.reindex(meses, fill_value=0)
        ax.plot(range(len(meses)), s / s.mean(), est, color=cor, ms=3, lw=0.9, label=nome)
    ax.axhline(1, color="0.5", lw=0.6, ls=":")
    ax.set_xticks(range(len(meses)), rot_mes(meses, lang), fontsize=6)
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_ylabel(tr(lang, "relativo à média", "relative to mean"))
    ax.set_title(titulo)
    ax.set_ylim(0, 2.9)
    ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=1, handlelength=2.2)
    limpa(ax)


def pn_manut(ax, manut, lang, titulo):
    m = manut[manut.mes < "2026-11-01"].pivot_table(index="mes", columns="com_espacos", values="ordens",
                                                     aggfunc="sum", fill_value=0)
    m = m.reindex(pd.date_range(m.index.min(), m.index.max(), freq="MS"), fill_value=0)
    media = m.sum(axis=1).mean()
    x = np.arange(len(m))
    ax.bar(x, m.get(1, 0) / media, color=P["clara"], edgecolor=P["referencia"], lw=0.3, width=0.8,
           label=tr(lang, "grafia antiga", "old coding"))
    ax.bar(x, m.get(0, 0) / media, bottom=m.get(1, 0) / media, color=P["principal"], width=0.8,
           label=tr(lang, "grafia nova", "new coding"))
    corte = list(m.index).index(pd.Timestamp("2025-11-01"))
    ax.axvline(corte - 0.5, color="k", lw=0.7, ls="--")
    ticks = [i for i, d in enumerate(m.index) if d.month == 1]
    ax.set_xticks(ticks, [str(m.index[i].year) for i in ticks])
    ax.yaxis.set_major_formatter(gfmt(lang))
    ax.set_ylabel(tr(lang, "ordens / média mensal", "orders / monthly mean"))
    ax.set_title(titulo)
    ax.legend(frameon=False, fontsize=6.5, loc="upper left")
    limpa(ax)


def auditorias_validas(aud):
    a = aud[aud.status.str.contains("Submitted", na=False)].dropna(subset=["pontos", "pontos_max"])
    a = a[(a.pontos_max > 0) & (a.pontos <= a.pontos_max)]
    return a.assign(nota=100 * a.pontos / a.pontos_max)


def pn_aud_hist(ax, aud, lang, titulo):
    a = auditorias_validas(aud)
    ax.hist(a.nota, bins=np.arange(30, 101, 5), color=P["barra"], edgecolor="k", lw=0.4)
    ax.axvline(a.nota.median(), color="k", lw=0.8, ls="--")
    ax.set_xlabel(tr(lang, "nota da auditoria (% dos pontos)", "audit score (% of points)"))
    ax.set_ylabel(tr(lang, "auditorias", "audits"))
    ax.set_yticks([])
    ax.set_title(titulo)
    limpa(ax)
    return a


def pn_aud_mes(ax, aud, lang, titulo):
    a = auditorias_validas(aud)
    a = a[a.mes >= "2026-06-01"]
    meses = sorted(a.mes.unique())
    ax.boxplot([a.loc[a.mes == m, "nota"] for m in meses], widths=0.55, showfliers=False,
               medianprops=dict(color="k"), boxprops=dict(facecolor=P["caixa"]), patch_artist=True)
    ax.set_xticks(range(1, len(meses) + 1), [MESES[lang][pd.Timestamp(m).month - 1] for m in meses])
    ax.set_ylabel(tr(lang, "nota (% dos pontos)", "score (% of points)"))
    ax.set_title(titulo)
    limpa(ax)


# ---------------------------------------------------------------- figuras
def figura(nome, lang, desenho, alt=5.6):
    fig, ax = plt.subplots(2, 2, figsize=(LARG, alt), gridspec_kw=dict(hspace=0.62, wspace=0.42))
    out = desenho(ax, lang)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.1)
    fig.savefig(FIG / f"{nome}{ef.sufixo(lang, MODO)}.pdf")
    plt.close(fig)
    return out


def main():
    global P, MODO, RNG
    ef.aplicar()
    d = carregar()
    p = d["p"]
    res = {}
    for lang, modo in ef.variantes():
        P, MODO, RNG = ef.paleta(modo), modo, np.random.default_rng(SEMENTE)
        def exposicao(ax, lang=lang):
            pn_box_uso(ax[0, 0], p, lambda v: v.horas, lang, tr(lang, "(a) Horas de viagem", "(a) Trip hours"),
                       tr(lang, "por veículo-mês / mediana", "per vehicle-month / median"))
            pn_box_uso(ax[0, 1], p, lambda v: v.milhas, lang, tr(lang, "(b) Milhas", "(b) Miles"),
                       tr(lang, "por veículo-mês / mediana", "per vehicle-month / median"))
            pn_box_uso(ax[1, 0], p, lambda v: v.milhas / v.horas, lang,
                       tr(lang, "(c) Velocidade média", "(c) Average speed"),
                       tr(lang, "milhas por hora / mediana", "miles per hour / median"))
            return pn_horas_extras(ax[1, 1], d["adp"], lang, tr(lang, "(d) Horas extras na folha", "(d) Payroll overtime"))

        def concentracao(ax, lang=lang):
            gv = pn_lorenz(ax[0, 0], p, "vehicle_id", lang, tr(lang, "(a) Concentração entre veículos",
                                                                "(a) Concentration across vehicles"))
            gs = pn_lorenz(ax[0, 1], p.dropna(subset=["site_m"]), "site_m", lang,
                           tr(lang, "(b) Concentração entre unidades", "(b) Concentration across sites"))
            fora = pn_caterpillar(ax[1, 0], p, lang, tr(lang, "(c) Risco relativo por unidade",
                                                         "(c) Relative risk by site"))
            p9010 = pn_tamanho(ax[1, 1], p, lang, tr(lang, "(d) Tamanho das unidades", "(d) Site size"))
            return gv, gs, fora, p9010

        def tempo(ax, lang=lang):
            suspeitos = pn_mensal(ax[0, 0], d["horario"], lang, tr(lang, "(a) Acidentes por mês", "(a) Accidents by month"))
            preench, turnos = pn_hora(ax[0, 1], d["horario"], lang, tr(lang, "(b) Hora do dia", "(b) Hour of day"))
            pn_dia(ax[1, 0], d["horario"], lang, tr(lang, "(c) Dia da semana", "(c) Day of week"))
            pn_semanal(ax[1, 1], d["adp"], p, lang, tr(lang, "(d) Exposição ao longo do tempo", "(d) Exposure over time"))
            return suspeitos, preench, turnos

        def tipos(ax, lang=lang):
            fig = ax[0, 0].figure
            for a in ax.flat:
                a.remove()
            gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.35], hspace=0.62, wspace=0.95)
            a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])
            share_acid = pn_tipos(a1, d["causas"], lang, tr(lang, "(a) Tipo de relato", "(a) Report type"))
            pn_uso_share(a2, p, lang, tr(lang, "(b) Participação por tipo de uso", "(b) Share by use type"))
            causas = pn_causas(a3, d["causas"], lang, tr(lang, "(c) Causa do acidente", "(c) Accident cause"))
            return share_acid, causas

        def fontes(ax, lang=lang):
            pn_fontes(ax[0, 0], d, lang, tr(lang, "(a) Três fontes de acidentes", "(a) Three accident sources"))
            pn_manut(ax[0, 1], d["manut"], lang, tr(lang, "(b) Ordens de manutenção por dano", "(b) Damage repair orders"))
            a = pn_aud_hist(ax[1, 0], d["aud"], lang, tr(lang, "(c) Notas das auditorias", "(c) Audit scores"))
            pn_aud_mes(ax[1, 1], d["aud"], lang, tr(lang, "(d) Notas por mês", "(d) Scores by month"))
            return a

        res["horas_extras"] = figura("fig_desc_exposicao", lang, exposicao)
        res["conc"] = figura("fig_desc_concentracao", lang, concentracao)
        res["tempo"] = figura("fig_desc_tempo", lang, tempo)
        res["tipos"] = figura("fig_desc_tipos", lang, tipos, alt=5.0)
        res["aud"] = figura("fig_desc_fontes", lang, fontes)

        def pp(ax, lang=lang):
            pn_box_uso(ax[0, 0], p, lambda v: v.horas, lang, tr(lang, "(a) Exposição por tipo de uso", "(a) Exposure by use type"),
                       tr(lang, "horas por veículo-mês / mediana", "hours per vehicle-month / median"))
            pn_lorenz(ax[0, 1], p, "vehicle_id", lang, tr(lang, "(b) Concentração entre veículos", "(b) Concentration across vehicles"))
            pn_hora(ax[1, 0], d["horario"], lang, tr(lang, "(c) Hora do acidente", "(c) Hour of accident"))
            pn_fontes(ax[1, 1], d, lang, tr(lang, "(d) Três fontes de acidentes", "(d) Three accident sources"))
        figura("fig_desc_pp", lang, pp)
        print("figuras ok", ef.sufixo(lang, modo) or "pt cor")

    # ---------------------------------------------------------- tabela e macros
    zeros = 100 * (p.acid == 0).mean()
    vm = p.acid.var() / p.acid.mean()
    (gv_obs, gv_poi, gv_h), (gs_obs, gs_poi, gs_h), fora, p9010 = res["conc"]
    suspeitos, preench, turnos = res["tempo"]
    share_acid, causas = res["tipos"]
    aud = res["aud"]
    he = res["horas_extras"]
    v = p[p.uso.isin(USOS)]
    cv_h = {u: v.loc[v.uso == u, "horas"].std() / v.loc[v.uso == u, "horas"].mean() for u in USOS}
    mph = {u: (v.loc[v.uso == u, "milhas"].sum() / v.loc[v.uso == u, "horas"].sum()) for u in USOS}
    mph_rel = {u: mph[u] / mph["Local Tractor"] for u in USOS}
    top3 = causas.sort_values(ascending=False).head(3).sum()

    linhas = [
        (r"\tr{Veículo-meses sem acidente (\%)}{Vehicle-months without accidents (\%)}", num_tex(zeros, 0)),
        (r"\tr{Razão variância/média dos acidentes por veículo-mês}{Variance-to-mean ratio of accidents per vehicle-month}", num_tex(vm, 2)),
        (r"\tr{Gini dos acidentes entre veículos: observado}{Gini of accidents across vehicles: observed}", num_tex(gv_obs, 2)),
        (r"\tr{Gini dos acidentes entre veículos: esperado sob Poisson}{Gini of accidents across vehicles: expected under Poisson}", num_tex(gv_poi, 2)),
        (r"\tr{Gini das horas entre veículos}{Gini of hours across vehicles}", num_tex(gv_h, 2)),
        (r"\tr{Unidades fora do IC 95\% do esperado (\%)}{Sites outside the 95\% CI of expected (\%)}", num_tex(100 * fora, 0)),
        (r"\tr{Exposição das unidades: razão P90/P10}{Site exposure: P90/P10 ratio}", num_tex(p9010, 0)),
        (r"\tr{Velocidade média do spotter / do local}{Spotter / local average speed}", num_tex(mph_rel["Spot Tractor"], 2)),
        (r"\tr{CV das horas por veículo-mês (spotter)}{CV of hours per vehicle-month (spotter)}", num_tex(cv_h["Spot Tractor"], 2)),
        (r"\tr{Acidentes nos turnos 1, 2 e 3 (\%)}{Accidents in shifts 1, 2 and 3 (\%)}",
         " / ".join(num_tex(turnos[k], 0) for k in (1, 2, 3))),
        (r"\tr{Três causas mais frequentes (\% dos acidentes)}{Three most frequent causes (\% of accidents)}", num_tex(top3, 0)),
        (r"\tr{Relatos suspeitos de teste (\%)}{Suspected test reports (\%)}", num_tex(suspeitos, 0)),
        (r"\tr{Relatos com hora do acidente (\%)}{Reports with accident time (\%)}", num_tex(100 * preench, 0)),
        (r"\tr{Horas extras / horas totais, mediana por unidade-mês (\%)}{Overtime / total hours, median per site-month (\%)}", num_tex(he.median(), 0)),
        (r"\tr{Nota mediana das auditorias (\% dos pontos)}{Median audit score (\% of points)}", num_tex(aud.nota.median(), 0)),
    ]
    TAB.joinpath("tab_descritiva.tex").write_text("\n".join(f"{a} & {b} \\\\" for a, b in linhas) + "\n", encoding="utf-8")

    macros = {
        "descZeros": num_tex(zeros, 0), "descVarMedia": num_tex(vm, 2),
        "descGiniObs": num_tex(gv_obs, 2), "descGiniPoisson": num_tex(gv_poi, 2), "descGiniHoras": num_tex(gv_h, 2),
        "descGiniSiteObs": num_tex(gs_obs, 2), "descGiniSitePoisson": num_tex(gs_poi, 2),
        "descForaIC": num_tex(100 * fora, 0), "descPnoventaPdez": num_tex(p9010, 0),
        "descVelSpotter": num_tex(mph_rel["Spot Tractor"], 2), "descVelShuttle": num_tex(mph_rel["Shuttle Tractor"], 2),
        "descTurnoUm": num_tex(turnos[1], 0), "descTurnoDois": num_tex(turnos[2], 0), "descTurnoTres": num_tex(turnos[3], 0),
        "descTopCausas": num_tex(top3, 0), "descSuspeitos": num_tex(suspeitos, 0), "descComHora": num_tex(100 * preench, 0),
        "descHorasExtras": num_tex(he.median(), 0), "descNotaAud": num_tex(aud.nota.median(), 0),
        "descAcidentesPct": num_tex(share_acid, 0),
    }
    TAB.joinpath("num_descritiva.tex").write_text(
        "% Gerado por analise/real/descritiva.py: nao editar a mao.\n"
        + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items()) + "\n", encoding="utf-8")
    for k, v in macros.items():
        print(f"{k:22s} {v}")


if __name__ == "__main__":
    main()
