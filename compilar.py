"""Compila o pre-projeto e a dissertacao em todas as versoes.

A lingua e o modo de cor saem do nome do PDF (-jobname), como define estilo/icmc.sty:
    <base>.pdf        portugues, colorido
    <base>_EN.pdf     ingles, colorido
    <base>_PB.pdf     portugues, preto e branco
    <base>_EN_PB.pdf  ingles, preto e branco
As figuras acompanham sozinhas, via \\arqfig{nome} (arquivos nome[_en][_pb].pdf).

Uso (na raiz do repo):
    python compilar.py                          # tudo: 2 documentos x 2 linguas x 2 modos
    python compilar.py preprojeto               # so o pre-projeto, 4 versoes
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
DOCS = {
    "preprojeto": "PreProjeto_MECAI_Felipe_Terrazas",
    "dissertacao": "Dissertacao_MECAI_Felipe_Terrazas",
}


def compilar(doc, en, pb):
    pasta = RAIZ / doc
    job = DOCS[doc] + ("_EN" if en else "") + ("_PB" if pb else "")
    env = dict(os.environ, TEXINPUTS=os.pathsep.join([".", "../", ""]))
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", f"-jobname={job}", "main.tex"],
                       cwd=pasta, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (pasta / f"{job}.log").read_text(encoding="utf-8", errors="replace") if (pasta / f"{job}.log").exists() else ""
    paginas = re.search(r"Output written on .*?\((\d+) pages?", log)
    indef = len(re.findall(r"undefined", log))
    erros = re.findall(r"^! .*", log, flags=re.M)
    status = "ok" if r.returncode == 0 and not erros else "ERRO"
    print(f"{status:4s} {doc}/{job}.pdf  páginas={paginas.group(1) if paginas else '?'}  "
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
