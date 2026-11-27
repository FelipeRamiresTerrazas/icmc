"""Compila o pre-projeto e a dissertacao em todas as versoes.

A lingua e o modo de cor saem do nome do PDF (-jobname), como define estilo/icmc.sty:
    <base>.pdf        portugues, colorido
    <base>_EN.pdf     ingles, colorido
    <base>_PB.pdf     portugues, preto e branco
    <base>_EN_PB.pdf  ingles, preto e branco
Os PDFs (e os auxiliares do LaTeX) saem em <projeto>/<doc>/output/.
Cada projeto (risco-patio/, rateiq/) tem seus documentos; o estilo e o .bib ficam na raiz.
As figuras acompanham sozinhas, via \\arqfig{nome} (arquivos nome[_en][_pb].pdf).

Uso (na raiz do repo):
    python compilar.py                          # tudo: 4 documentos x 2 linguas x 2 modos
    python compilar.py preprojeto               # so o pre-projeto, 4 versoes
    python compilar.py admissao                 # so o projeto curto da inscricao, 4 versoes
    python compilar.py rateiq                   # projeto da inscricao da ideia 2 (rateiq/), 4 versoes
    python compilar.py dissertacao --modo pb    # dissertacao em P&B, PT e EN
    python compilar.py preprojeto --lingua pt --modo cor
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SAIDA = "output"  # pasta dos PDFs dentro de cada documento
# documento: (pasta relativa a raiz, arquivo principal, nome base do PDF)
# Projeto 1, risco de acidentes em patio (risco-patio/)
DOCS = {
    "preprojeto": ("risco-patio/preprojeto", "main.tex", "PreProjeto_MECAI_Felipe_Terrazas"),
    "admissao": ("risco-patio/preprojeto", "admissao.tex", "Projeto_MECAI_Felipe_Terrazas"),  # projeto curto da inscricao (5 paginas)
    "dissertacao": ("risco-patio/dissertacao", "main.tex", "Dissertacao_MECAI_Felipe_Terrazas"),
    # Projeto 2, RateIQ (rateiq/)
    "rateiq": ("rateiq/preprojeto", "admissao.tex", "Projeto_Precificacao_MECAI_Felipe_Terrazas"),  # projeto da inscricao, versao completa (sem limite de paginas)
}


def compilar(doc, en, pb):
    nome_pasta, principal, base = DOCS[doc]
    pasta = RAIZ / nome_pasta
    job = base + ("_EN" if en else "") + ("_PB" if pb else "")
    env = dict(os.environ, TEXINPUTS=os.pathsep.join([".", "../../", ""]))  # ../../ = raiz (estilo/)
    # PDF e auxiliares vao para <projeto>/<doc>/output/ (os auxiliares sao ignorados pelo git)
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", f"-outdir={SAIDA}", f"-jobname={job}", principal],
                       cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    arq_log = pasta / SAIDA / f"{job}.log"
    log = arq_log.read_text(encoding="utf-8", errors="replace") if arq_log.exists() else ""
    paginas = re.search(r"Output written on .*?\((\d+) pages?", log, flags=re.S)  # o caminho longo quebra a linha
    indef = len(re.findall(r"undefined", log))
    erros = re.findall(r"^! .*", log, flags=re.M)
    status = "ok" if r.returncode == 0 and not erros else "ERRO"
    print(f"{status:4s} {nome_pasta}/{SAIDA}/{job}.pdf  páginas={paginas.group(1) if paginas else '?'}  "
          f"referências indefinidas={indef}")
    for e in erros[:5]:
        print("     ", e)
    return status == "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc", nargs="?", default="todos", choices=["todos", *DOCS])
    ap.add_argument("--lingua", default="ambas", choices=["pt", "en", "ambas"])
    ap.add_argument("--modo", default="ambos", choices=["cor", "pb", "ambos"])
    a = ap.parse_args()
    docs = list(DOCS) if a.doc == "todos" else [a.doc]
    linguas = {"pt": [False], "en": [True], "ambas": [False, True]}[a.lingua]
    modos = {"cor": [False], "pb": [True], "ambos": [False, True]}[a.modo]
    ok = all([compilar(d, en, pb) for d in docs for pb in modos for en in linguas])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
