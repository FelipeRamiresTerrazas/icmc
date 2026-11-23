"""Estilo comum das figuras (Python). O equivalente em R fica em r/estilo_fig.R.

Cada figura sai em quatro arquivos, como o texto sai em quatro PDFs:
    nome.pdf        portugues, colorida
    nome_en.pdf     ingles, colorida
    nome_pb.pdf     portugues, preto e branco
    nome_en_pb.pdf  ingles, preto e branco
No LaTeX, \\arqfig{nome} escolhe o arquivo pela lingua e pelo modo do documento
(sufixos _EN e _PB no -jobname; ver estilo/icmc.sty).

As cores sao papeis, nao valores: os scripts pedem P["principal"], P["faixa"] etc.
A versao colorida usa o azul dos titulos do documento e a paleta Okabe-Ito
(segura para daltonismo); a preto e branco usa tons de cinza. Marcadores,
tracejados e hachuras sao os mesmos nos dois modos, para que a figura continue
legivel impressa em preto e branco.
"""

import matplotlib

LARGURA = 6.3  # polegadas, largura util da pagina
LINGUAS = (0, 1)  # 0 = portugues, 1 = ingles
MODOS = ("cor", "pb")

PALETAS = {
    "cor": dict(
        principal="#1F3A5F",   # azul dos titulos (estilo/icmc.sty)
        secundaria="#D55E00",  # vermelhao
        terciaria="#009E73",   # verde azulado
        quaternaria="#E69F00",  # laranja
        barra="#4A6F96",
        clara="#A9BDD4",
        caixa="#D3DEEA",
        pontos="#1F3A5F",
        faixa="#CCD9E8",
        fundo1="#F2F5F9",
        fundo2="#DCE5EF",
        destaque="#C0392B",
        neutro="#9AA5B1",
        linha="black",
        referencia="0.5",
    ),
    "pb": dict(
        principal="0.15",
        secundaria="0.5",
        terciaria="0.75",
        quaternaria="0.9",
        barra="0.55",
        clara="0.8",
        caixa="0.87",
        pontos="0.35",
        faixa="0.85",
        fundo1="0.94",
        fundo2="0.86",
        destaque="black",
        neutro="0.62",
        linha="black",
        referencia="0.5",
    ),
}


def paleta(modo):
    return PALETAS[modo]


def sufixo(lang, modo):
    return ("_en" if lang else "") + ("_pb" if modo == "pb" else "")


def aplicar(tamanho=8):
    matplotlib.rcParams.update({"font.family": "serif", "font.size": tamanho, "axes.titlesize": tamanho + 0.5,
                                "hatch.linewidth": 0.4, "pdf.fonttype": 42})


def variantes():
    """Todas as combinacoes (lingua, modo), na ordem em que os arquivos sao gerados."""
    return [(lang, modo) for modo in MODOS for lang in LINGUAS]
