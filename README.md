# icmc

Mestrado Profissional MECAI (ICMC-USP, ênfase em Ciência de Dados). Duas ideias de tese, cada uma na sua pasta, com estilo, bibliografia e documentos do programa compartilhados na raiz.

| Pasta | Ideia | Situação |
| :-- | :-- | :-- |
| `risco-patio/` | 1. Risco de acidentes em operações de pátio: modelos hierárquicos de contagem com exposição e telemetria (linha Modelagem de Risco) | Pré-projeto, projeto curto da inscrição, viabilidade e rascunho da dissertação |
| `rateiq/` | 2. RateIQ: recomendação de salário e taxa de motoristas por região, com dados públicos e internos | Ideia candidata (desde 2026-11-23): notas e projeto curto da inscrição |

```
icmc/
├── risco-patio/       projeto 1 (ver risco-patio/README.md)
│   ├── preprojeto/    pré-projeto e projeto curto da inscrição, em LaTeX bilíngue
│   ├── dissertacao/   RASCUNHO da dissertação
│   ├── analise/       Python
│   ├── r/             R (renv)
│   ├── notas/         notas desta ideia (03, 05 a 11)
│   ├── dados/         fora do git
│   └── resultados/    fora do git
├── rateiq/            projeto 2 (ver rateiq/README.md)
│   ├── preprojeto/    projeto curto da inscrição (admissao.tex), em LaTeX bilíngue
│   └── notas/         origem e escopo (epics do Jira), ângulo de pesquisa
├── notas/             notas gerais, que valem para as duas ideias
│   ├── 01-inventario-dados.md     fontes de dados da empresa (interno)
│   ├── 02-ideias-de-projeto.md    ideias avaliadas e ranking (interno)
│   ├── 04-disciplinas.md          disciplinas do MECAI
│   └── 12-conversa-aluno-mecai.md conversa com aluno do MECAI (interno)
├── estilo/            estilo LaTeX compartilhado e ABNT.md (normas)
├── referencias.bib    bibliografia única (entradas com CONFERIR ainda não checadas)
├── referencias/       PDFs da bibliografia, nome = chave do .bib
├── programa/          documentos do MECAI (regras, disciplinas, linhas, horários, edital)
├── compilar.py        compila os documentos LaTeX dos projetos
└── requirements.txt   dependências Python (um .venv na raiz serve aos dois projetos)
```

## Branches

`main` reúne tudo. Uma branch por área (`preprojeto`, `dissertacao`, `analise`, `artigos`, `notas`, `referencias`, `infra`, `rateiq`); cada commit mexe só nos arquivos da sua área e o merge na `main` é feito com `--no-ff`. Tabela de arquivos por branch no `CLAUDE.md`, seção Git.

## Compilar os documentos

Cada documento sai em quatro versões, escolhidas pelo sufixo do PDF: português ou inglês (`_EN`) e colorido ou preto e branco (`_PB`). As figuras acompanham sozinhas (`\arqfig{nome}` pega `nome[_en][_pb].pdf`). Na raiz:

```
python compilar.py                          # tudo: os três documentos do projeto 1 e o projeto curto do RateIQ
python compilar.py preprojeto               # só o pré-projeto, 4 versões
python compilar.py admissao                 # só o projeto curto da inscrição (projeto 1)
python compilar.py rateiq                   # projeto curto da inscrição do RateIQ (projeto 2)
python compilar.py dissertacao --modo pb    # dissertação em P&B, PT e EN
python compilar.py preprojeto --lingua pt --modo cor
```

No VS Code, as receitas do LaTeX Workshop têm os mesmos nomes ("Pré-projeto: PT + EN, cor", "Dissertação: todas as versões" etc.); rode a receita com o `main.tex` do documento certo aberto. À mão, dentro da pasta do documento: `TEXINPUTS=".;../../;" latexmk -pdf -outdir=output -jobname=<NomeDoPDF> main.tex`.

Comandos de análise e dos estudos de viabilidade do projeto 1: `risco-patio/README.md`.
