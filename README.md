# icmc

Pré-projeto para o Mestrado Profissional MECAI (ICMC-USP, ênfase em Ciência de Dados). Repositório privado.

Tema: risco de acidentes em operações de pátio, com modelos hierárquicos de contagem, exposição e telemetria veicular (linha Modelagem de Risco).

```
icmc/
├── preprojeto/        pré-projeto em LaTeX, bilíngue (PT e EN do mesmo código) + PDFs
│   └── partes/        uma seção por arquivo
├── dissertacao/       RASCUNHO da dissertação (não entra no pré-projeto)
│   ├── capitulos/     um capítulo por arquivo; cap. 5 = estudos de viabilidade
│   ├── tabelas/       geradas por script (não editar à mão)
│   └── figuras/       geradas por script (não editar à mão)
├── estilo/            estilo LaTeX compartilhado (pré-projeto e futura dissertação)
├── referencias.bib    bibliografia única (entradas com CONFERIR ainda não checadas)
├── referencias/       PDFs da bibliografia, nome = chave do .bib
├── programa/          documentos do MECAI (regras, disciplinas, linhas, horários, edital)
├── notas/             notas de trabalho internas
│   ├── 01-inventario-dados.md     fontes de dados da empresa (interno)
│   ├── 02-ideias-de-projeto.md    ideias avaliadas e ranking (interno)
│   ├── 03-perguntas-em-aberto.md  decisões pendentes
│   ├── 05-datasets-publicos.md    datasets públicos (Kaggle, OSHA, FMCSA)
│   ├── 06-mapa-da-literatura.md   referências por tema, lacunas, ordem de leitura
│   ├── 07-prompt-cortex-dashboard.md  prompt do app Streamlit no Snowflake (interno)
│   ├── 08-viabilidade-dados-reais.md  conclusões e testes com os dados reais (interno)
│   └── 09-plano-de-artigos.md     três artigos planejados (periódicos e congresso)
├── analise/           código: modelos, painel sintético, datasets públicos, testes
│   ├── viabilidade/   poder.py (poder semi-sintético) e previsao.py (previsão da exposição)
│   └── real/          dados reais, só agregados: extrair, explorar, testes, figuras
├── r/                 R (renv): h2_misto.R, modelo misto de H2 com glmmTMB
├── dados/             fora do git (datasets públicos baixados)
└── resultados/        fora do git (saídas das análises, inclusive agregados reais)
```

## Compilar o pré-projeto

Dentro de `preprojeto/` (ou pela receita "Pré-projeto PT + EN" do LaTeX Workshop):

```
TEXINPUTS=".;../;" latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas main.tex       # português
TEXINPUTS=".;../;" latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN main.tex    # inglês
```

## Rascunho da dissertação e estudos de viabilidade

```
.venv/Scripts/python analise/dados_publicos.py baixar                  # se ainda não baixou
.venv/Scripts/python analise/viabilidade/poder.py --repeticoes 200     # cerca de 10 min
.venv/Scripts/python analise/viabilidade/previsao.py                   # cerca de 1 min
.venv/Scripts/python analise/real/extrair.py    # dados reais, so agregados (interno; precisa da chave do usuario de servico)
.venv/Scripts/python analise/real/explorar.py   # conclusoes em notas/08
.venv/Scripts/python analise/real/testes.py     # testes de H1, H2 (preditivo) e H3; prepara o painel do R
(cd r && Rscript h2_misto.R)                    # H2 com modelo misto (glmmTMB), Holm e equivalencia
.venv/Scripts/python analise/real/figuras.py    # fig_real.pdf e fig_real_en.pdf (so valores relativos)
cd dissertacao && TEXINPUTS=".;../;" latexmk -pdf -jobname=Dissertacao_MECAI_Felipe_Terrazas main.tex
```

## Rodar a análise

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/rodar_exemplo.py          # painel sintético
.venv/Scripts/python analise/dados_publicos.py baixar                          # dataset do Kaggle (15 MB)
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/dados_publicos.py exemplo  # modelos no dataset público
.venv/Scripts/python -m pytest analise/tests -q
```
