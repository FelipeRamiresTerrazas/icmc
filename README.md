# icmc

Pré-projeto para o Mestrado Profissional MECAI (ICMC-USP, ênfase em Ciência de Dados). Repositório privado.

Tema: risco de acidentes em operações de pátio, com modelos hierárquicos de contagem, exposição e telemetria veicular (linha Modelagem de Risco).

| Caminho | Conteúdo |
| --- | --- |
| `preprojeto/` | Pré-projeto em LaTeX, bilíngue: o mesmo código gera o PDF em português e em inglês (ver `preprojeto/README.md`). PDFs versionados. |
| `analise/` | Esqueleto de análise (modelos de contagem, bayes empírico, subnotificação), testado com dados sintéticos. |
| `referencias/` | Documentos do programa (linhas e orientadores, horários; o edital entra aqui). |
| `referencias-icmc.bib` | Bibliografia. Entradas com `CONFERIR` ainda precisam ser checadas na fonte. |
| `01-inventario-dados.md` | Inventário das fontes de dados da empresa (só agregados). **Interno.** |
| `02-ideias-de-projeto.md` | Ideias avaliadas, notas e ranking. **Interno.** |
| `03-perguntas-em-aberto.md` | Decisões e confirmações pendentes. |
| `04-programa-mecai.md` | Regras do programa (FAQ), disciplinas, linhas de pesquisa. |

## Compilar o pré-projeto

Dentro de `preprojeto/`:

```
latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas main.tex       # português
latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN main.tex    # inglês
```

## Rodar a análise (dados sintéticos)

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/rodar_exemplo.py
.venv/Scripts/python -m pytest analise/tests -q
```
