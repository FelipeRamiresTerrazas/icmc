# icmc

Pré-projeto para o Mestrado Profissional MECAI (ICMC-USP, ênfase em Ciência de Dados). Repositório privado.

Tema: risco de acidentes em operações de pátio, com modelos hierárquicos de contagem, exposição e telemetria veicular (linha Modelagem de Risco).

```
icmc/
├── preprojeto/        pré-projeto em LaTeX, bilíngue (PT e EN do mesmo código)
│   ├── partes/        uma seção por arquivo
│   └── output/        PDFs compilados (PT, EN, cor, P&B)
├── dissertacao/       RASCUNHO da dissertação (não entra no pré-projeto)
│   ├── capitulos/     um capítulo por arquivo; cap. 5 = estudos de viabilidade
│   ├── tabelas/       geradas por script (não editar à mão)
│   ├── figuras/       geradas por script (não editar à mão)
│   └── output/        PDFs compilados (PT, EN, cor, P&B)
├── estilo/            estilo LaTeX compartilhado (pré-projeto e futura dissertação) e ABNT.md (normas)
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
│   ├── 09-plano-de-artigos.md     três artigos planejados (periódicos e congresso)
│   ├── 10-escala-de-motoristas.md app de escala por turno: método, ponte com a tese (interno)
│   ├── 11-contexto-claude-desktop.md  contexto para colar no projeto do Claude Desktop (sem nome da empresa)
│   └── 12-conversa-aluno-mecai.md  conversa com aluno do MECAI: seleção, disciplinas, docentes (interno)
├── analise/           código: modelos, painel sintético, datasets públicos, testes
│   ├── viabilidade/   poder.py (poder semi-sintético) e previsao.py (previsão da exposição)
│   └── real/          dados reais, só agregados: extrair, explorar, testes, figuras, descritiva
├── r/                 R (renv): h2_misto.R (modelo misto de H2) e descritiva.R (figuras de contagem e eventos)
├── dados/             fora do git (datasets públicos baixados)
└── resultados/        fora do git (saídas das análises, inclusive agregados reais)
```

## Branches

`main` reúne tudo. Uma branch por área (`preprojeto`, `dissertacao`, `analise`, `artigos`, `notas`, `referencias`, `infra`); cada commit mexe só nos arquivos da sua área e o merge na `main` é feito com `--no-ff`. Detalhes e a tabela de arquivos por branch no `CLAUDE.md`, seção Git.

## Compilar os documentos

Cada documento sai em quatro versões, escolhidas pelo sufixo do PDF: português ou inglês (`_EN`) e colorido ou preto e branco (`_PB`). As figuras acompanham sozinhas (`\arqfig{nome}` pega `nome[_en][_pb].pdf`). Na raiz:

```
python compilar.py                          # tudo: pré-projeto e dissertação, PT/EN, cor/P&B (8 PDFs)
python compilar.py preprojeto               # só o pré-projeto, 4 versões
python compilar.py dissertacao --modo pb    # dissertação em P&B, PT e EN
python compilar.py preprojeto --lingua pt --modo cor
```

No VS Code, as receitas do LaTeX Workshop têm os mesmos nomes ("Pré-projeto: PT + EN, cor", "Dissertação: todas as versões" etc.); rode a receita com o `main.tex` do documento certo aberto. À mão, dentro da pasta do documento: `TEXINPUTS=".;../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN_PB main.tex`.

## Rascunho da dissertação e estudos de viabilidade

```
.venv/Scripts/python analise/dados_publicos.py baixar                  # se ainda não baixou
.venv/Scripts/python analise/viabilidade/poder.py --repeticoes 200     # cerca de 10 min
.venv/Scripts/python analise/viabilidade/previsao.py                   # cerca de 1 min
.venv/Scripts/python analise/real/extrair.py    # dados reais, so agregados (interno; precisa da chave do usuario de servico)
.venv/Scripts/python analise/real/explorar.py   # conclusoes em notas/08
.venv/Scripts/python analise/real/testes.py     # testes de H1, H2 (preditivo) e H3; prepara o painel do R
(cd r && Rscript h2_misto.R)                    # H2 com modelo misto (glmmTMB), Holm e equivalencia
.venv/Scripts/python analise/real/figuras.py    # fig_real*.pdf (so valores relativos)
.venv/Scripts/python analise/real/descritiva.py # capitulo 4: fig_desc_*.pdf, tab_descritiva.tex, num_descritiva.tex
(cd r && Rscript descritiva.R)                  # capitulo 4: fig_desc_contagem, fig_desc_eventos, num_descritiva_r.tex
python compilar.py dissertacao
```

Todo script de figura gera as quatro variantes (`nome.pdf`, `nome_en.pdf`, `nome_pb.pdf`, `nome_en_pb.pdf`) com a paleta comum de `analise/estilo_fig.py` (Python) e `r/estilo_fig.R` (R). As cores são papéis (`principal`, `secundaria`, `faixa`...), não valores: para mudar o visual de todas as figuras, basta mudar a paleta.

## Rodar a análise

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/rodar_exemplo.py          # painel sintético
.venv/Scripts/python analise/dados_publicos.py baixar                          # dataset do Kaggle (15 MB)
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/dados_publicos.py exemplo  # modelos no dataset público
.venv/Scripts/python -m pytest analise/tests -q
```
