# Projeto 1: risco de acidentes em operações de pátio

Primeira ideia de tese, escolhida em 2026-11-08: risco de acidentes em operações de pátio, com modelos hierárquicos de contagem, exposição e telemetria veicular (linha Modelagem de Risco). É a ideia do pré-projeto e do projeto curto da inscrição.

```
risco-patio/
├── preprojeto/        pré-projeto completo (main.tex) e projeto curto da inscrição (admissao.tex), bilíngues
│   ├── partes/        uma seção por arquivo
│   └── output/        PDFs compilados (PT, EN, cor, P&B)
├── dissertacao/       RASCUNHO da dissertação (não entra no pré-projeto)
│   ├── capitulos/     um capítulo por arquivo
│   ├── tabelas/       geradas por script (não editar à mão)
│   ├── figuras/       geradas por script (não editar à mão)
│   └── output/        PDFs compilados
├── analise/           Python: modelos, painel sintético, datasets públicos, testes
│   ├── viabilidade/   poder.py (poder semi-sintético) e previsao.py (previsão da exposição)
│   └── real/          dados reais, só agregados: extrair, explorar, testes, figuras, descritiva
├── r/                 R (renv): h2_misto.R (modelo misto de H2) e descritiva.R
├── notas/             notas de trabalho desta ideia
│   ├── 03-perguntas-em-aberto.md     decisões pendentes (interno)
│   ├── 05-datasets-publicos.md       datasets públicos (Kaggle, OSHA, FMCSA)
│   ├── 06-mapa-da-literatura.md      referências por tema, lacunas, ordem de leitura
│   ├── 07-prompt-cortex-dashboard.md prompt do app Streamlit no Snowflake (interno)
│   ├── 08-viabilidade-dados-reais.md conclusões e testes com os dados reais (interno)
│   ├── 09-plano-de-artigos.md        três artigos planejados
│   ├── 10-escala-de-motoristas.md    app de escala por turno e ponte com a tese (interno)
│   └── 11-contexto-claude-desktop.md contexto para colar no Claude Desktop (sem nome da empresa)
├── dados/             fora do git (datasets públicos baixados)
└── resultados/        fora do git (saídas das análises, inclusive agregados reais)
```

As notas mantêm a numeração antiga; as gerais (01 inventário, 02 ideias, 04 disciplinas, 12 conversa) ficam em `../notas/`.

## Compilar

Na raiz do repositório: `python compilar.py` (ou `preprojeto`, `admissao`, `dissertacao`; opções `--lingua` e `--modo`). À mão, dentro da pasta do documento: `TEXINPUTS=".;../../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN_PB main.tex`.

## Rodar a análise

Comandos na raiz do repositório (o `.venv` é compartilhado):

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
PYTHONIOENCODING=utf-8 .venv/Scripts/python risco-patio/analise/rodar_exemplo.py          # painel sintético
.venv/Scripts/python risco-patio/analise/dados_publicos.py baixar                          # dataset do Kaggle (15 MB)
PYTHONIOENCODING=utf-8 .venv/Scripts/python risco-patio/analise/dados_publicos.py exemplo  # modelos no dataset público
.venv/Scripts/python -m pytest risco-patio/analise/tests -q
```

## Rascunho da dissertação e estudos de viabilidade

```
.venv/Scripts/python risco-patio/analise/viabilidade/poder.py --repeticoes 200     # cerca de 10 min
.venv/Scripts/python risco-patio/analise/viabilidade/previsao.py                   # cerca de 1 min
.venv/Scripts/python risco-patio/analise/real/extrair.py    # dados reais, só agregados (precisa da chave do usuário de serviço)
.venv/Scripts/python risco-patio/analise/real/explorar.py   # conclusões em notas/08
.venv/Scripts/python risco-patio/analise/real/testes.py     # testes de H1, H2 (preditivo) e H3; prepara o painel do R
(cd risco-patio/r && Rscript h2_misto.R)                    # H2 com modelo misto (glmmTMB), Holm e equivalência
.venv/Scripts/python risco-patio/analise/real/figuras.py    # fig_real*.pdf (só valores relativos)
.venv/Scripts/python risco-patio/analise/real/descritiva.py # capítulo 4: fig_desc_*.pdf, tab_descritiva.tex, num_descritiva.tex
(cd risco-patio/r && Rscript descritiva.R)                  # capítulo 4: fig_desc_contagem, fig_desc_eventos, num_descritiva_r.tex
python compilar.py dissertacao
```

Os scripts acham `dados/`, `resultados/` e `dissertacao/` relativos a esta pasta. Todo script de figura gera as quatro variantes (`nome.pdf`, `nome_en.pdf`, `nome_pb.pdf`, `nome_en_pb.pdf`) com a paleta comum de `analise/estilo_fig.py` (Python) e `r/estilo_fig.R` (R).
