# Pré-projeto MECAI (ICMC-USP), Felipe

**Sempre responda em português brasileiro.** Mapa do repositório no `README.md`.

## Regras de escrita

- **Normas ABNT:** antes de escrever ou revisar texto do pré-projeto, da dissertação ou de artigo, ler `estilo/ABNT.md` (resumo próprio das Diretrizes USP 2024, cujo PDF está em `programa/usp-diretrizes-teses-abnt-2024.pdf`) e passar o checklist da seção 12. Dissertação: ABNT integral. Pré-projeto: o edital prevalece, ABNT no resto. Artigos: normas da revista.
- Sem travessão (—) nem `---` em texto novo.
- Nunca inventar referência. Entrada nova no `referencias.bib` leva `note = {CONFERIR}` até o Felipe checar na fonte. Ao citar resultado de estudo não lido na fonte, escrever de forma geral e marcar `\preencher{conferir ...}`.
- O pré-projeto e qualquer texto externo **não nomeiam a empresa, clientes nem unidades** e dão os volumes da operação (veículos, relatos, viagens, unidades, horas) só em ordem de grandeza, sem números internos exatos. Isso continua valendo depois da autorização da empresa (ver "Dados e segurança").
- O pré-projeto não cita nem se dirige a nenhum docente: a orientação é definida pela coordenação.
- Bilíngue: parágrafos em `\pt{...}` seguido de `\en{...}`; trechos curtos em `\tr{pt}{en}`. Língua escolhida pelo sufixo `_EN` no `-jobname`. O Felipe edita o português e pede "sincroniza o inglês": atualizar os `\en{}` correspondentes aos `\pt{}` alterados.
- Depois de mudar o texto, recompilar (`python compilar.py`, no mínimo PT e EN em cor) e conferir visualmente as páginas alteradas; ao mexer em figura ou legenda com cor, conferir também uma versão P&B.

## Dados e segurança

- Repositório **privado** (tornado privado em 2026-11-08). Os arquivos `notas/01` a `notas/03`, `notas/07`, `notas/08` e `notas/10` são internos: citam a empresa, sistemas e números agregados. Nunca torná-lo público sem antes remover esses arquivos do histórico.
- Dados da empresa nunca entram no git (`dados/`, `resultados/`, csv, xlsx, json, parquet estão no `.gitignore`). Sem segredos, credenciais ou dados pessoais (nomes de motoristas, RH, informação comercial sensível).
- Repositórios e sistemas da empresa (`analytics-dbt-project`, `yardsafe-log`, Snowflake, Jira, Confluence, Domo): **somente leitura**, nunca commitar neles.
- Snowflake: só pelo usuário de serviço somente leitura (`~/.snowflake/claude_sf.py`, chave JWT). Nunca autenticar com senha (a conta pessoal tem MFA e bloqueia). Uma tentativa de conexão; se falhar, parar e reportar. Não usar navegador para isso.
- **A empresa autorizou o uso dos dados na pesquisa** (informado pelo Felipe em 2026-11-15; data e forma da autorização ainda a registrar no pré-projeto). As consultas podem ser no nível do registro, desde que mascaradas:
  - nomes de motoristas e de qualquer pessoa removidos (nunca extrair colunas de nome, e-mail, documento, data de nascimento, raça, sexo, endereço, imagem ou GPS);
  - empresa, clientes e unidades substituídos por códigos (Site 01, 02...); o identificador do veículo trocado por código, com a tabela de correspondência só dentro do ambiente da empresa;
  - texto livre (descrições de acidente, motivos e queixas de manutenção) limpo de nomes, placas e locais antes de qualquer uso, inclusive antes de mandar a qualquer modelo de linguagem.
- Dado pseudonimizado continua sendo dado pessoal pela LGPD: resultados por veículo não são divulgados, só por unidade ou por grupo, com número mínimo de veículos por célula.
- Extrações em `analise/real/` (e futuras) salvam só em `resultados/real/` (fora do git); conclusões internas com números exatos vão para `notas/08`.

## Programa

Regras do MECAI resumidas em `programa/README.md` (36 meses, sem qualificação, 48 créditos em disciplinas). Documentos do programa (edital, linhas, horários) ficam em `programa/`; o edital prevalece sobre a FAQ.

## Organização

- `referencias/`: PDFs de artigos e livros da bibliografia (o Felipe vai colocando). Nome do arquivo = chave do `referencias.bib` (ex.: `lord2010.pdf`).
- `notas/`: notas de trabalho internas (inventário, ideias, perguntas, datasets públicos).
- `dados/`: fora do git. `dados/publicos/` tem datasets públicos baixados por `analise/dados_publicos.py`.
- LaTeX compila dentro da pasta do documento com `TEXINPUTS=".;../;"` e `-outdir=output` (PDFs e auxiliares em `<doc>/output/`; use `python compilar.py`; o `latexmkrc` de cada documento força `output/` mesmo sem a opção, e o `.gitignore` barra PDF solto na pasta do documento) (o estilo fica em `estilo/`, compartilhado com a futura dissertação).

## Dissertação (rascunho)

- `dissertacao/` é rascunho de trabalho, separado do pré-projeto: nada dele vai para o pré-projeto sem o Felipe pedir.
- Tabelas (`dissertacao/tabelas/`) e figuras (`dissertacao/figuras/`) são geradas por `analise/viabilidade/*.py`. Não editar à mão; mudar o script e rodar de novo. Números citados no texto do capítulo 5 têm de bater com as tabelas: conferir depois de rodar.
- Tabelas entram dentro de `tabular` com `\tabinput{arquivo.tex}` (o `\input` normal quebra antes do `\bottomrule`).
- Os estudos de viabilidade usam a ESTRUTURA do dataset público do Kaggle (exposição, caminhões, terminais) com acidentes simulados; os incidentes do dataset são aleatórios e não servem para mostrar efeito.
- O pré-projeto (Seção 5.8, "Estudo preliminar de viabilidade") cita números do capítulo 5 e usa `fig_poder.pdf` / `fig_poder_en.pdf` de `dissertacao/figuras/`. Se os scripts de viabilidade rodarem de novo, conferir e atualizar esses números nos dois documentos. Enquadramento obrigatório: simulação calibrada em dados públicos, nunca "testamos a ideia com os dados do Kaggle".
- A Seção 5.9.2 do pré-projeto ("Exploração dos dados da operação") cita resultados de `analise/real/testes.py` e `r/h2_misto.R` (saídas em `resultados/real/`, fora do git) e usa `fig_real.pdf` / `fig_real_en.pdf`, geradas por `analise/real/figuras.py`. No pré-projeto entram porcentagens arredondadas, razões e volumes só em ordem de grandeza; números exatos ficam em `notas/08`. O texto trata esses resultados como evidência exploratória, nunca como conclusão de hipótese.
- Estrutura da dissertação em três níveis: cap. 4 descritivo, cap. 7 preditivo, cap. 8 prescritivo. O cap. 4 e a subseção "Descrição preliminar" do pré-projeto (Seção 4) usam figuras e números gerados por `analise/real/descritiva.py` e `r/descritiva.R` (`fig_desc_*`, `tabelas/tab_descritiva.tex`, `tabelas/num_descritiva*.tex`). O texto cita os números só pelas macros (`\descZeros` etc.), nunca digitados; o pré-projeto lê as mesmas macros. Se os scripts rodarem de novo, recompilar os dois documentos e reler os parágrafos, porque a interpretação pode mudar. Figuras e números desses scripts não mostram volumes absolutos da operação (só valores relativos, proporções ou ordens de grandeza).
- Python e R: Python para extração, preparação, bootstrap, previsão e figuras; R para modelos mistos (glmmTMB, DHARMa), num projeto renv em `r/` (Rscript em `C:/Users/Usuario/AppData/Local/Programs/R/R-4.6.1/bin/Rscript.exe`, rodar dentro de `r/`).
- Figuras: matplotlib (ou ggplot2 no R), PDF, fonte serifada, largura 6,3 polegadas, rótulos em português com vírgula decimal. Todo script de figura gera quatro variantes, `nome.pdf`, `nome_en.pdf`, `nome_pb.pdf` e `nome_en_pb.pdf`, com a paleta de `analise/estilo_fig.py` / `r/estilo_fig.R` (cores por papel; nunca cor fixa no script). No LaTeX, sempre `\includegraphics{\arqfig{nome}}`; legenda que cita cor usa `\corpb{colorido}{P&B}`. Marcadores, tracejados e hachuras iguais nos dois modos, para a figura funcionar impressa em P&B.
- Compilar com `python compilar.py` (oito PDFs) ou um subconjunto (`python compilar.py preprojeto --modo cor`).

## Git

Commits e push só quando o Felipe pedir. A `main` reúne tudo e deve sempre compilar. Há uma branch por área, e cada commit mexe só nos arquivos da sua área:

| Branch | Arquivos |
|---|---|
| `preprojeto` | `preprojeto/` |
| `dissertacao` | `dissertacao/` (capítulos, tabelas e figuras geradas, PDFs) |
| `analise` | `analise/`, `r/`, `requirements.txt` |
| `artigos` | `notas/09-plano-de-artigos.md` e, no futuro, os textos dos artigos |
| `notas` | `notas/` (menos a 09) e `programa/` |
| `referencias` | `referencias.bib`, `referencias/` |
| `infra` | `README.md`, `CLAUDE.md`, `.gitignore`, `.vscode/`, `estilo/`, `compilar.py` |

- Antes de começar numa branch: `git switch <area>` e `git merge main`, para ter o resto do repositório atualizado.
- Mensagem de commit começa pela área: `preprojeto: ...`, `analise: ...`.
- Mudança que atravessa áreas (ex.: script que gera uma figura citada no pré-projeto) vira um commit por área, na ordem `analise`, `dissertacao`, `preprojeto`, cada um na sua branch.
- Merge na `main` com `git merge --no-ff <area>`, só quando o Felipe decidir.
