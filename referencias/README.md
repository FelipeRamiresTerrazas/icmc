# Referências bibliográficas

PDFs de artigos, livros e relatórios citados (ou candidatos a citação) no pré-projeto e na dissertação.

- **Nome do arquivo = chave do `../referencias.bib`**, por exemplo `lord2010.pdf`, `cameron2013.pdf`. Assim fica fácil achar o PDF de cada citação.
- Ao conferir uma referência na fonte, remova o `note = {CONFERIR}` da entrada no `.bib`.
- Material sem entrada no `.bib` ainda (leitura exploratória): pode ficar em `referencias/a-ler/` até decidir se entra.

Documentos do programa (edital, linhas de pesquisa, horários) **não** ficam aqui: vão em `../programa/`. Datasets ficam em `../dados/publicos/` (fora do git), descritos em `../notas/05-datasets-publicos.md`.

## Lista de leitura em PDF

`Lista_de_Leitura.pdf` traz todas as referências do `.bib` por tema, com o motivo de ler, link (DOI ou busca no Google Scholar) e caixa de "lido". Para atualizar depois de mexer no `.bib` (dentro desta pasta):

```
../.venv/Scripts/python gerar_lista.py
TEXINPUTS=".;../;" latexmk -pdf -jobname=Lista_de_Leitura lista_leitura.tex
```

Referência nova entra no tema certo acrescentando a chave em `TEMAS` no `gerar_lista.py` (senão aparece em "Sem tema").
