# 01. Inventário de dados (Fase 1)

Levantamento feito em 2026-11-08, só com leitura. Nenhum arquivo, branch ou commit foi criado nos repositórios da YMX. Números são agregados; sites aparecem anonimizados (Site 01, 02...) e não há nome de motorista, funcionário ou cliente.

Legenda: **[verificado]** = conferido no código, no banco ou no ticket citado; **[inferido]** = conclusão razoável a partir de evidência indireta; **[não verificado]** = precisa de confirmação (ver `../risco-patio/notas/03-perguntas-em-aberto.md`).

## 0. Repositório `mestrado`: estrutura, compilação e reaproveitamento

**Estado git.** O repositório estava na branch `revisao-pre-e-diss` (não na `main`), com um arquivo não rastreado (`lattes/01-dados-gerais.pdf`, deixado como estava). A `main` e a `revisao-pre-e-diss` divergiram (10 commits só na segunda, 3 só na primeira). A branch `icmc-preprojeto` foi criada a partir da `revisao-pre-e-diss`, que é a versão mais completa (pré-projeto, dissertação, `r/` com renv, bibliografia com 76 entradas). Nada do projeto do Prof. Otto foi alterado.

**Organização.** Cada documento LaTeX tem sua pasta (`preprojeto/`, `dissertacao/`, `proposta-orientador/`, `conversa-otto/`), todos usando `estilo/mestrado.sty` e `referencias.bib` na raiz.

**Como compila.**

- MiKTeX com `latexmk`, `pdflatex` e `biber` (Perl disponível). Dentro da pasta do documento: `TEXINPUTS=".;../;" latexmk -pdf -jobname=<NomeDoPDF> main.tex`.
- O nome do PDF controla o modo de impressão: se o `-jobname` terminar em `_PB`, o estilo liga a versão preto e branco (títulos pretos, pendências em cinza, figuras lidas de `figuras/pb/`).
- O VS Code tem duas receitas no LaTeX Workshop (latexmk ou pdflatex, biber e pdflatex duas vezes), com `TEXINPUTS=../;../../;`.
- Não há Makefile. Python: `.venv/` na raiz (3.12, numpy, pandas, scipy, scikit-learn, statsmodels, matplotlib, pytest; **sem `requirements.txt`**). R 4.6.1 fora do PATH, com projeto `renv` isolado em `r/` (`renv.lock`, `.Rprofile`).

**O que dá para reaproveitar no pré-projeto do ICMC.**

| Peça | Reaproveitamento | Ajuste necessário |
| :-- | :-- | :-- |
| `estilo/mestrado.sty` | Integral (Times 12, margens 3/2 cm ABNT, biblatex-abnt, `\preencher{}`, caixa `nota`, modo `_PB`) | Ajustar ao formato do edital 002/2026 (limite de páginas e fonte não verificados) |
| `preprojeto/main.tex` | Modelo de capa e de ordem das seções | Trocar instituição (ICMC), programa (MECAI), retirar orientador; o edital diz que a coordenação define |
| `referencias.bib` | Padrão de entradas e marcação `CONFERIR`; entradas de estatística espacial e de random forest (`breiman2001`, `pedregosa2011`, `cressie1993`, `diggle2007`) | Quase toda a bibliografia é de solos e geoestatística; a do novo tema terá de ser montada |
| Convenções do `CLAUDE.md` do mestrado | Tabelas e figuras geradas por script, sem número fixo no texto, sem referência inventada | Nenhum |
| `experimento/` (Python) e `r/` (renv) | Padrão de projeto: `config.toml` com semente, `simular.py` e `analisar.py`, testes com pytest, conferência cruzada em R | Criar `icmc/analise/` com o mesmo padrão e um `requirements.txt` |
| `.gitignore` | Já protegia `dados/`; foram acrescentadas regras para `icmc/` (dados, resultados, csv, xlsx, parquet, json, .env) | Nenhum |

**Edital 002/2026.** Não há pasta `mestrado/referencias/` e nenhum arquivo do edital no repositório. Limite de páginas, formato e itens obrigatórios: **[não verificado]**.

## 1. `analytics-dbt-project` (dbt + Snowflake)

Fonte: código na branch `fix/timecard-ca-week-start` (limpa) e `target/manifest.json` gerado em 2026-11-06 (dbt 1.12.5). Não há `catalog.json`, então **não há contagem de linhas local**.

**Tamanho do projeto [verificado]:** 106 modelos, 35 sources declaradas, 258 testes, 4 seeds, 2 snapshots. Camadas `staging` e `marts` (dimensions, finance, inventory, ml, operations, safety, workforce). Vários modelos leem tabelas por caminho fixo em vez de `source()` (o ticket DA-355 trata disso).

### 1.1 Fontes por sistema

| Sistema | Onde está no Snowflake | Grão | Período coberto | Volume | Qualidade aparente |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **Yard Commander (YMS da YMX)** | `DOMOVIEW.IQDOX.ASSETEVENTS` (eventos), `DOMOVIEW.IQDOX.AML`, inventário por API em `RAW.INVENTORY_SNAPSHOTS.*` e `RAW.API.*` | Um evento por transação de pátio (move, dropoff, gate), com usuário, trator, trailer, campus e horário local e UTC | Os modelos filtram os últimos 365 dias (`domo_lookback_days`); histórico bruto **[não verificado]** | 2,5 milhões de eventos nos últimos 90 dias, último em 2026-11-08 [verificado] | Linhas duplicadas idênticas (DA-385, corrigido com `QUALIFY`); cargas paradas (DA-378, DA-397, DA-456) |
| **ADP** (folha e ponto) | `RAW.ADP.*` (API e cargas manuais) e `RAW_FIVETRAN.ADP_WORKFORCE_NOW.*` (Fivetran) | Batida de ponto por funcionário (entrada, saída, horas, código de pagamento, departamento, tarefa); cadastro com departamento e supervisor | Semanas desde 2024 (`week_starts_since_2024`) **[inferido]** | **[não verificado]** | Departamento, nome e fuso errados em batidas (DA-435, corrigido); duplicatas e violação de chave (DA-281); nulos (DA-321, DA-444, DA-445) |
| **TMW** (faturamento) | `DOMOVIEW.TMWVIEWS.TMW_INVOICEDETAILS`, `TMW_INVOICEHEADER`, `TMW_ORDERHEADER` | Linha de fatura | **[não verificado]** | **[não verificado]** | Divergências recorrentes com outras fontes (DA-43, DA-242, DA-256) |
| **Manutenção (asset management)** | `EDW_PROD_100460.*` (ordens de oficina, unidades, contas) | Ordem e transação de oficina | **[não verificado]** | **[não verificado]** | Sem bug registrado |
| **Formulário de acidentes (MS Forms)** | `RAW.ACCIDENTS_INJURIES.SAFETY_INCIDENT_REPORTING_LOAD` | Um relato por linha | Última atualização em 2026-03-18, segundo a página de soft launch no Confluence **[não verificado no banco]** | **[não verificado]** | Site em texto livre (ver 2.3) |
| **YardSafe** (app de safety) | `RAW.ACCIDENTS_INJURIES.INCIDENTS` (cópia via MERGE pela edge function `submit-incident`) | Um relato por linha | Set/2025 em diante | 635 linhas em 2026-10-21 (Confluence) | **Ainda não é lida pelo dbt** (DA-450 vai trocar a fonte) |
| **Mapa login → funcionário** | `ANALYTICS_DB.YMX_AUDIT.YMX_USER_MAP` (mantido por um agente, com aprovação humana) | Um login de pátio por linha | Desde 2026-10-22 | 1.506 linhas em 2026-11-02 (DA-405) | 194/194 acertos na validação contra logins com ID (DA-415) |
| **Previsão de movimentos** | `ANALYTICS_DB.MARTS.predicted_daily_moves` (gerada fora do dbt, por notebook) | Campus × dia | Desde mai/2026 **[inferido pelos commits]** | **[não verificado]** | Falha de task (DA-252) |
| **Samsara** (telemetria) | `RAW_FIVETRAN.SAMSARA` (Fivetran, esquema criado em 2026-09-24, 71 tabelas). **Não aparece no dbt** | Evento de safety, viagem e leitura de sensor por veículo | Eventos de set/2025 a out/2026; viagens de mar/2025 a out/2026 | 87 mil eventos de safety, 1,17 milhão de viagens, 297 veículos (ver seção 3) | **Sincronização parada desde 2026-10-13** [verificado] |
| **Orbcomm** (telemetria de trailers) | ETL próprio da plataforma Yard Commander para um cliente (Confluence, espaço YM); não está no dbt | **[não verificado]** | **[não verificado]** | **[não verificado]** | Discovery DA-332 concluído |

Sobre o nome **IQDOX**: as páginas "Moves Validation Evidence" e "Response Time Validation Evidence" validam os números do Snowflake contra exports do Yard Commander, e a página "Inventory" diz que o inventário vem do Yard Commander. Portanto `IQDOX` é a camada de dados (via Domo) dos eventos do Yard Commander **[inferido; confirmar]**. O ticket DA-383 trata de uma segunda ingestão do Yard Commander por Fivetran para um site.

### 1.2 Linhagem relevante para os temas candidatos

- **Movimentos:** `ASSETEVENTS` → `stg_moves_dropoff_complete` (filtro `MOVE - DROPOFF COMPLETE`, deduplicação, preenchimento de login pelo último valor) → `fact_moves_dropoff_complete` → `fact_moves_billedhours`, `fact_hourly_moves_by_driver`, `fact_daily_yard_move_features` (contagem diária por campus com defasagens de 1 e 7 dias).
- **Previsão:** `predicted_daily_moves` (notebook) → `fact_predicted_moves_history` (incremental) → `fact_moves_predicted_vs_actual`.
- **Horas trabalhadas:** tabelas Fivetran do ADP + seeds de fuso e de departamento → `stg_adp__timecard_supervisor_pay_code` → `fact_timecard_supervisor_pay_code` (batida com `TIME_IN`, `TIME_OUT`, `HOURS`, departamento de trabalho, tarefa, semana iniciando no domingo).
- **Sites:** `RAW.ADP.WORKERS` → `stg_adp__departments_parsed` (regex no nome longo do departamento: cliente, cidade, UF, tipo de serviço; teste de colisão de chave) → `dim_site`, `dim_department`. `stg_supervisor_site` alimenta a lista de sites do YardSafe.
- **Safety:** `SAFETY_INCIDENT_REPORTING_LOAD` → `stg_accidents_injuries_forms_raw` (um `CASE` com 22 regras `ILIKE` para padronizar o site) → `fact_accidents_injuries` → `stg_operations_kpi_labor_efficiency`, que liga acidentes ao supervisor pelo **sobrenome de quem reportou** (ligação frágil).

### 1.3 Chaves de ligação entre fontes

| Ligação | Chave | Situação |
| :-- | :-- | :-- |
| Login do pátio ↔ funcionário ADP | `USERID_NORM` via `YMX_USER_MAP` | Existe e é auditada [verificado no código e no DA-405] |
| Campus do pátio ↔ departamento ADP | Nenhuma chave comum; `CAMPUSNAME` é texto | Não há tabela de correspondência no dbt; o DA-450 cita uma `DIM_SITES_TREATED` **[não verificado]** |
| Relato YardSafe ↔ site ADP | `site_location_code` = código do departamento ADP | Gravado desde a migração de 2026-08-25; preenchido em 221 de 644 relatos (ver 2.2) |
| Relato YardSafe ↔ funcionário ADP | `employee_worker_id` | Preenchido em 8 de 644 relatos |
| Relato ↔ veículo Samsara | `truck_number` ↔ `SAMSARA.VEHICLE.NAME` (igualdade exata) | **Casa em 402 de 570 relatos com caminhão (71%)**; 165 de 259 códigos distintos [verificado] |
| Relato ↔ trator do pátio | `truck_number` ↔ `YARDTRACTORID` | **Impossível hoje:** `YARDTRACTORID` e `DRIVERID` vazios em 100% dos 2,5 milhões de eventos dos últimos 90 dias [verificado] |
| Motorista Samsara ↔ funcionário ADP | `SAMSARA.DRIVER.EXTERNAL_ID` | Vazio nos 1.056 motoristas; só por nome (sensível) [verificado] |
| Horário | Pátio tem hora local e UTC; ADP tem fuso por departamento (seed); relatos têm data e hora local em texto | Exige padronização; fuso e semana já geraram bugs (DA-195, DA-435, DA-447) |

## 2. `yardsafe-log` (app de safety)

**Confirmado [verificado]:** é o YardSafe, app de relato de acidentes, incidentes e lesões da YMX (React + Vite + TypeScript no Vercel; Supabase com Postgres, autenticação e storage; edge functions em Deno; cópia para o Snowflake). Go-live previsto para 15 e 16 de novembro de 2026 (DA-390, DA-449). Substitui o MS Forms.

### 2.1 Esquema (tabela `incidents` e auxiliares)

- **Identificação e site:** `id`, `site_location` (texto), `site_location_code` (código ADP), `new_site`, `go_live_date`.
- **Tempo:** `actual_incident_date`, `actual_incident_time`, `supervisor_notification_date`, `supervisor_notification_time`, `submitted_at`, `updated_at`.
- **Pessoa:** `employee_full_name`, `employee_worker_id`; na lesão também data de nascimento, data de admissão, raça e sexo (campos OSHA, dados sensíveis).
- **Tipo:** `incident_type` (accident_incident, work_injury, other) e `other_category` (Near Miss, Roadside/Scale Inspection, Citation, Altercation, Other/Misc).
- **Acidente:** `truck_type` (D1 Spotter, D2 Shuttle, D3 OTR), `truck_number`, `trailer_number`, `direction`, `accident_root_cause` (12 categorias fixas), `police_contacted`, `roadway_address`, `insurance_claim`.
- **Lesão:** `work_injury_root_cause` (5 categorias), 14 perguntas de investigação, `missed_time`, `days_away_from_work`, `days_restricted_work`, `days_modified_work`, `osha_classification`, `osha_recordable`, `dart_case`.
- **Textos livres:** `accident_description`, `work_injury_description`, `other_description`, `why_1` a `why_5` (5 porquês), `concerns_about_claim`. No MS Forms havia também o depoimento escrito do motorista.
- **Gravidade:** não há escala de gravidade. Os proxies são `insurance_claim`, `osha_recordable`, `dart_case`, dias de afastamento e, no acidente, a causa raiz.
- **Exposição:** **não existe nenhum campo de exposição** (horas, viagens ou movimentos). Ela terá de vir do ADP (horas) e do Yard Commander (movimentos).
- **Tabelas auxiliares:** `incident_corrective_actions` (achado, ação, dono, prazo, % concluído), `assets` (276 caminhões e 642 trailers segundo o Confluence; tipo, marca, modelo, ano, domicílio), `profiles`.

### 2.2 Contagens agregadas (Supabase, consulta de agregação em 2026-11-08)

Total de **644 relatos**, com data do incidente entre 2025-09-15 e 2026-11-04.

| Trimestre do incidente | Acidente/incidente | Lesão | Outros (quase-acidente e diversos) | Total |
| :-- | --: | --: | --: | --: |
| 2025-T3 (desde 15/set) | 19 | 1 | 0 | 20 |
| 2025-T4 | 132 | 17 | 0 | 149 |
| 2026-T1 | 108 | 21 | 0 | 129 |
| 2026-T2 | 126 | 13 | 2 | 141 |
| 2026-T3 | 144 | 16 | 9 | 169 |
| 2026-T4 (até 04/nov) | 29 | 4 | 3 | 36 |
| **Total** | **558** | **72** | **14** | **644** |

- Quase-acidentes: **13** no total. É pouco para modelar.
- OSHA Recordable: 0; DART: 1. Os campos OSHA foram criados há pouco e quase não estão preenchidos, então **não servem como rótulo de gravidade** por ora.
- 5 porquês preenchidos: 7 relatos. Descrição de acidente preenchida: 558.
- **Relatos migrados (antes de out/2026), 594:** código de site em 172, ID do funcionário em 0, hora em 577.
- **Relatos novos pelo app (desde out/2026), 50:** código de site em 49, ID do funcionário em 8, número do caminhão em 44.
- **Possíveis testes:** a página de soft launch estima cerca de 130 relatos "pending" de mai a out/2026 que parecem teste e ainda não foram limpos (item 7 do plano, DA-449). **As contagens acima incluem esses relatos.** O volume real pode ser perto de 500 **[não verificado]**.

### 2.3 Por site e período (export histórico do MS Forms, 617 respostas)

O arquivo `Accident, Incident, and Injury reporting(1-617).xlsx` fica na raiz do `yardsafe-log`, fora do git pelo `.gitignore`, e tem dados pessoais. Foi lido localmente por script, imprimindo só agregados. Datas de 2025-09-15 a 2026-10-13.

- O campo de site é texto livre com **131 grafias distintas**.
- O `CASE` do dbt mapeia **370 dos 617 (60%)** para 16 sites canônicos. Os outros **247 (40%)** caem no `ELSE` com 69 grafias.
- Com uma normalização simples (só letras), sobram **83 "sites"**. Desses, 17 têm 10 ou mais eventos, 10 têm 20 ou mais e 46 têm 1 ou 2. Parte dessa cauda é a mesma unidade escrita de outro jeito.

| Site (anonimizado) | 2025-S2 | 2026-S1 | 2026-S2 (até out) | Total | % acidente/incidente |
| :-- | --: | --: | --: | --: | --: |
| Site 01 | 23 | 28 | 15 | 66 | 97% |
| Site 02 | 25 | 25 | 8 | 58 | 97% |
| Site 03 | 11 | 24 | 5 | 40 | 70% |
| Site 04 | 9 | 20 | 11 | 40 | 72% |
| Site 05 | 11 | 16 | 7 | 34 | 88% |
| Site 06 | 12 | 10 | 9 | 31 | 77% |
| Site 07 | 10 | 10 | 7 | 27 | 96% |
| Site 08 | 8 | 9 | 8 | 25 | 92% |
| Site 09 | 0 | 14 | 11 | 25 | 84% |
| Site 10 | 6 | 6 | 10 | 22 | 95% |
| Site 11 | 7 | 10 | 0 | 17 | 94% |
| Site 12 | 0 | 0 | 16 | 16 | 75% |
| Site 13 | 5 | 9 | 0 | 14 | 93% |
| Site 14 | 1 | 7 | 5 | 13 | 77% |
| Site 15 | 0 | 0 | 13 | 13 | 100% |
| Demais 68 | 41 | 79 | 56 | 176 | |

Outros agregados do export:

- **Tipo:** 534 acidente/incidente, 57 lesão, 14 quase-acidente, 10 "Workman's Comp", 2 vazios. Há variantes com espaço no fim, e essa diferença de grafia também aparece no `CASE` do dbt.
- **Caminhão:** 431 Spotter, 60 Shuttle, 45 OTR, 81 vazios.
- **Causa raiz:** 12 categorias principais, com duplicatas por grafia ("trailer connection/coupling issues" aparece em duas formas). As mais comuns são falhas de fixação de porta ou equipamento (79), erro operacional (77), ré mal feita ou folga mal calculada (67), colisão com objeto fixo (54) e queda de trailer ou do pé de apoio (53).
- **Texto:** descrição preenchida em 87% (mediana de 158 caracteres); depoimento do motorista em 75% (mediana de 203).

## 3. Snowflake (Samsara) e Domo

**Acesso usado (2026-11-08):** o usuário de serviço só de leitura `CLAUDE_CODE_SVC` (papel `CLAUDE_READONLY`, login por chave, warehouse `ANALYTICS_WH`), pelo script `~/.snowflake/claude_sf.py`. Só metadados e consultas agregadas. As duas tabelas gigantes não foram varridas: `READING_HISTORY_FEED` (2,6 bilhões de linhas, 56 GB) e `GPS` (195 milhões de linhas). Nenhum nome de motorista foi lido.

### 3.1 Samsara (`RAW_FIVETRAN.SAMSARA`)

**Tabelas úteis para o projeto [verificado]:**

| Tabela | Linhas | O que tem |
| :-- | --: | :-- |
| `SAFETY_EVENT` | 87.137 | Evento detectado pela câmera ou telemetria: veículo, motorista, início e fim, local (lat/long, cidade, UF), g-force máxima, velocidade e limite, estado da revisão |
| `SAFETY_EVENT_BEHAVIOR_LABEL` | 87.215 | Tipo do evento (rótulo do sistema ou do revisor) |
| `VEHICLE_TRIP` | 1.172.432 | Viagem por veículo e motorista: início, fim, distância, combustível, endereços (exposição) |
| `VEHICLE` | 297 | Cadastro: nome (código do caminhão), VIN, marca, modelo, ano |
| `DRIVER` / `DRIVER_VEHICLE_ASSIGNMENT` | 1.056 / 868.556 | Motoristas (525 ativos) e atribuição motorista–veículo no tempo |
| `TAGS` / `TAG_VEHICLE` | 91 / 777 | Grupos de veículos: 8 raízes e 83 filhas, mediana de 3 veículos por tag filha. Se as tags filhas são sites ou clientes: **[não verificado]** |
| `VEHICLE_IDLING_REPORT`, `HOS_LOG`, `DVIR`, `FAULT_CODE` | 1,5 mi / 477 mil / 23,6 mil / 466 mil | Marcha lenta, jornada (HOS), inspeção pré-viagem e falhas mecânicas |

**Eventos de safety por mês (todos os tipos):**

| Mês | Eventos | Veículos |
| :-- | --: | --: |
| 2025-09 (desde 28/set) | 268 | 49 |
| 2025-10 | 2.877 | 113 |
| 2025-11 | 2.799 | 120 |
| 2025-12 | 11.908 | 123 |
| 2026-01 | 9.536 | 139 |
| 2026-02 | 7.507 | 156 |
| 2026-03 | 8.530 | 152 |
| 2026-04 | 7.582 | 157 |
| 2026-05 | 5.950 | 160 |
| 2026-06 | 6.234 | 172 |
| 2026-07 | 6.397 | 176 |
| 2026-08 | 6.859 | 188 |
| 2026-09 | 7.811 | 235 |
| 2026-10 (até 13/out) | 2.879 | 222 |

O pico de dez/2025 pode refletir uma mudança de configuração (por exemplo, ativação do alerta de cinto) **[não verificado]**.

- **Tipos de evento (rótulos do sistema):** sem cinto 41.283; velocidade máxima 12.173; curva brusca 11.075; frenagem 9.608; distância de seguimento 4.926; parada sem parar 2.258; distração 1.821; celular 1.784; sonolência 619; excesso grave de velocidade 516; **colisão 356**; câmera obstruída 332; aceleração 307.
- **Revisão humana:** 54.965 revisados, 25.914 descartados (falso positivo ou irrelevante), 3.708 aguardando coaching, 1.834 aguardando revisão, 631 com coaching feito.
- **Colisões detectadas:** 360 no total, das quais cerca de 80% foram descartadas na revisão (por trimestre: 2/0, 48/41, 65/43, 69/60, 149/127, 27/22). Sobram cerca de 67 colisões não descartadas.
- **Motorista ausente:** 24% dos eventos não têm motorista.

**Viagens (exposição) por mês.** De mar a jul/2025 só 26 a 33 veículos e quase nenhuma viagem com motorista (96% a 100% sem). De ago/2025 em diante a frota cresce (85 veículos em set/2025, 253 em out/2026) e 16% a 24% das viagens ficam sem motorista. Em 2026 são 340 a 410 mil milhas e 15 a 27 mil horas de viagem por mês. 3.480 viagens (0,3%) têm fim inválido ou aberto e precisam de filtro: sem esse filtro, as horas de set e out/2026 explodem.

**Nome do veículo:** 179 dos 297 seguem o padrão "duas letras + cinco dígitos", o mesmo do `truck_number` do YardSafe.

### 3.2 Ligações verificadas

- **YardSafe ↔ Samsara por caminhão:** 402 de 570 relatos com número de caminhão casam exatamente com um veículo Samsara (71%). A normalização deve elevar esse número.
- **Yard Commander ↔ Samsara:** impossível pelo trator (`YARDTRACTORID` vazio). Só pelo site ou pela pessoa (login → ADP pelo `YMX_USER_MAP`).
- **Samsara ↔ ADP por motorista:** não há ID externo. Só por nome, o que é sensível e não é necessário no nível de veículo ou site.

### 3.3 Qualidade e riscos

- O conector Fivetran da Samsara não sincroniza desde 2026-10-13. Ninguém abriu ticket, e a Samsara não está no dbt.
- Cerca de 30% dos eventos são descartados na revisão, e os rótulos do sistema têm falsos positivos.
- A base inclui localização GPS contínua e câmera (`SAFETY_EVENT_MEDIA`). Para pesquisa, só agregados por veículo, site e período.

### 3.4 Segunda rodada de descobertas (2026-11-08)

**Fivetran da Samsara.** Foi pausado de propósito por custo (confirmado por você). O dado congelado vai de set/2025 a 13/10/2026 nos eventos e de mar/2025 a 13/10/2026 nas viagens. Isso já cobre 13 meses em sobreposição com os relatos do YardSafe.

Quase todo o volume está em duas tabelas que o projeto não usa: `READING_HISTORY_FEED` (2,6 bilhões de linhas) e `GPS` (195 milhões). As tabelas necessárias somam cerca de 2,2 milhões de linhas (0,07% do total): `SAFETY_EVENT`, `SAFETY_EVENT_BEHAVIOR_LABEL`, `VEHICLE_TRIP`, `VEHICLE`, `TAGS`, `TAG_VEHICLE` e `DRIVER_VEHICLE_ASSIGNMENT`. Se o custo do Fivetran vem de linhas ativas por mês, reativar só essas tabelas deve custar uma fração do anterior **[provável; confirmar com o painel de uso do Fivetran]**.

**Tags da Samsara são sites [verificado].**

- As tags filhas das quatro regiões (Midwest, North East, South East, West) têm no nome o código de departamento ADP (formato `SP1234` ou `SH1234`). Só um código não aparece no `DIM_DEPARTMENT`.
- Dos 277 caminhões com viagem em 2026, 262 (95%) têm tag de site.
- **Validação:** cruzando os relatos do YardSafe que têm código de site com a tag do mesmo caminhão, o código coincide em quase todos os sites (pureza 1,00 na maioria). As exceções são a oficina central, com caminhões que circulam entre sites, e poucos casos de código vizinho.
- As outras raízes de tag trazem atributos úteis do caminhão: uso (spot, local, shuttle), combustível (diesel, EV) e propriedade (alugado).
- A cadeia **relato → caminhão → site → ADP** existe sem depender de texto livre.

**Yard Commander [verificado].**

- `ASSETEVENTS` tem 11,6 milhões de linhas (0,83 GB), de 2023-04 a 2026-11-08, em 39 campi (38 desde set/2025).
- O `YARDTRACTORID` foi preenchido em só 1.696 eventos, em 2025, e o `DRIVERID` nunca. A ligação com o pátio só existe por campus ou por login.
- Nenhum nome de campus contém código de departamento: a ponte campus ↔ departamento (38 itens) ainda precisa ser montada.
- `AML` tem 1,6 milhão de linhas. `FACT_MOVES_DROPOFF_COMPLETE` tem 1,78 milhão (janela de 365 dias).

**Horas ADP por mês (exposição).** `FACT_TIMECARD_SUPERVISOR_PAY_CODE` tem 227.752 linhas e começa em jun/2025 (mês parcial).

| Mês | Departamentos | Horas |
| :-- | --: | --: |
| 2025-07 | 45 | 38.309 |
| 2025-10 | 52 | 48.039 |
| 2026-01 | 61 | 54.732 |
| 2026-04 | 63 | 66.626 |
| 2026-07 | 70 | 86.795 |
| 2026-10 | 83 | 107.240 |

Há 12 departamentos com horas sem data válida. A empresa cresceu muito no período (horas quase triplicaram), o que reforça a necessidade de ajustar por exposição.

**Tabelas de site e de safety [verificado].**

- `RAW.ACCIDENTS_INJURIES.DIM_SITES_TREATED`: 53 linhas, atualizada em 2026-07-30. Colunas: departamento, código, descrição, supervisor, site ajustado.
- `INJURY_BY_SITE`: 51 linhas (site, supervisor, última lesão, dias sem incidente). É a tabela estática que o DA-450 quer substituir.
- `DIM_SITE`: 81 linhas. `DIM_DEPARTMENT`: 93. `STG_SUPERVISOR_SITE`: 79.
- `FACT_ACCIDENTS_INJURIES` tem 275 linhas, iguais à carga do MS Forms parada em 2026-03-18. O mart de safety está defasado oito meses.
- A cópia do app (`INCIDENTS`) tem 647 linhas.

**Política de uso da Samsara.** Não há página no Confluence nem ticket no Jira sobre política, dono ou regras de uso da telemetria e da câmera. O único registro é o discovery do DA-443, pedido pela liderança de produto.

### 3.5 Domo e outras fontes

O Domo não foi consultado. O que se sabe pelo Confluence e pelo Jira, sem conferência direta:

- **Domo:** existe um Domo App de Safety com "Incident-Free Days by Site", hoje calculado a partir de uma tabela estática (DA-450). O consumo de créditos caiu de 1.804 (jul/2026) para 1.276 (out/2026).
- **Snowflake:** a cópia do YardSafe tinha 635 linhas em 2026-10-21.

As consultas de volume do Yard Commander e do ADP listadas em `../risco-patio/notas/03-perguntas-em-aberto.md` ainda não foram rodadas. Agora posso rodá-las pelo mesmo acesso.

### 3.6 Terceira rodada: relatos, auditorias e manutenção (2026-11-15)

Só metadados e agregados, pelo usuário de serviço; nenhum valor de texto livre ou campo pessoal foi lido. Scripts no scratchpad da sessão (`safety_meta.py`, `fontes_extra.py`, `manutencao.py`), fora do repositório.

**Relatos: `RAW.ACCIDENTS_INJURIES.INCIDENTS` é a fonte única.** É a cópia do YardSafe e já inclui o histórico do MS Forms: as contagens mensais de set/2025 a fev/2026 são praticamente iguais às da `SAFETY_INCIDENT_REPORTING_LOAD` (carga parada em 2026-03-16, 275 linhas). A carga antiga não acrescenta relatos; serve só para auditar a migração.

- 648 relatos, de 2025-09-15 a 2026-11-14 (cerca de 14 meses), na ordem de 40 a 60 por mês (todos os tipos).
- **Hora do acidente:** preenchida e convertível em 97% dos relatos (`ACTUAL_INCIDENT_TIME`). Dá para atribuir turno, o que viabiliza a ideia da carga de trabalho por turno (`notas/10`). Os acidentes se espalham pelas 24 horas, sem turno vazio. Na carga antiga, só cerca de dois terços das horas convertem no formato `HH12:MI AM`.
- Os campos de RH sensíveis (data de nascimento, admissão, raça, sexo) estão vazios na cópia do Snowflake. Não usar de qualquer forma.
- O mart do dbt `MARTS.FACT_ACCIDENTS_INJURIES` continua com as 275 linhas do MS Forms (defasado).

**Fonte nova: auditorias de segurança por site.** `DOMOVIEW."cust_mmmm_0034_2137".ACCIDENTS_INJURIES_POWER_APPS_RAW` (258 linhas) **não é de acidentes**, apesar do nome: são avaliações de segurança feitas por auditores em cada site (data, tipo de avaliação, pontuação obtida e possível, percentual, status do relatório), vindas do Power Apps via Domo. Cobre de mar/2026 a nov/2026, com volume regular a partir de jun/2026 (30 a 60 por mês) e cerca de 66 sites. **Uso possível:** a pontuação da auditoria como medida de clima ou prática de segurança por site e mês, covariável para o risco (H1) e, principalmente, para a probabilidade de relato (H3b), na linha de `probst2008` e `probst2010`. Limites: começa tarde, a pontuação falta em parte das linhas e há dois tipos de avaliação.

**Manutenção: `EDW_PROD_100460` (banco compartilhado).** Não aparece em `ACCOUNT_USAGE.TABLES`, por isso a busca por nome não acha.

- `FCT_AMORDERSEC` (seções de ordem): 46,6 mil linhas, de mar/2023 a nov/2026, com `REPREASON`. **Atenção:** os motivos vêm com e sem espaços no fim (`DAMAGE` e `DAMAGE      `); sempre usar `TRIM`.
- **Mudança de regime em nov/2025:** até out/2025, as ordens de dano usam a grafia com espaços, somam 10 a 35 por mês e têm `ACC-REPORTED` frequente. A partir de nov/2025, a grafia sem espaços, quase só `DAMAGE`, 20 a 90 por mês, e `ACC-REPORTED` praticamente some. Parece troca de sistema ou de regra de preenchimento. Consequência: no período comum com o YardSafe (nov/2025 em diante), a dúvida sobre `ACC-REPORTED` quase não pesa, mas é preciso entender o que passou a entrar como `DAMAGE` e por que o volume subiu **[não verificado]**.
- **Veículo da ordem:** não está em `FCT_AMORDERSEC`. O caminho é `FCT_AMORDERSEC.ORDERID` → `FCT_AMORDERS` (`UNITID`, `COMPANYUNIT`) → `DIM_AMUNITS` (`UNITNUMBER`, `PHYLOCATION` e campos livres da unidade). Falta medir quanto o `UNITNUMBER` casa com o nome do veículo na Samsara e com o `TRUCK_NUMBER` do YardSafe, e se `PHYLOCATION` dá a unidade do veículo **[próxima consulta]**.
- O banco também tem tabelas de outro sistema de transporte (`AGG_TS*`, inclusive relatórios de segurança com 0 ou 1 linha); não servem.

## 4. Jira e Confluence

Projeto **DA** com 384 tickets (37 bugs). Espaços do Confluence: DA (Data Analytics) e YM (Yard Management).

### 4.1 O que você já construiu (com evidência)

- **YardSafe** (DA-390, DA-71, DA-217, DA-436 a DA-451): app completo com 178 testes automatizados, histórico importado, sync com Snowflake e plano de soft launch.
- **YMX Resource Agent** (DA-405, DA-411 a DA-425): primeiro agente de IA rodando no Snowflake. Liga logins do pátio a funcionários do ADP com normalização de nomes, Jaro-Winkler, pontuação por site e data, faixas de confiança, revisão por IA dos casos incertos, fila de aprovação humana em Streamlit e trilha de auditoria. Validado em 194/194.
- **Previsão diária de movimentos por campus** com intervalo, comparação previsto × realizado e painéis embutidos para clientes (DA-252, DA-259, commits de mai/2026).
- **Produtividade:** movimentos por hora e por hora faturada, análise por dia da semana, tempo de resposta do pátio (DA-107, DA-379, DA-406, DA-407, DA-433).
- **Inventário e dwell:** inventário de trailers por API do Yard Commander com snapshots e painéis de dwell de porta para clientes (DA-333, DA-345, DA-391, DA-434).
- **ADP:** ingestão por API e Fivetran, escalas planejadas × realizadas, KPIs de operação e de horas (DA-72, DA-331, DA-382, DA-392, DA-395).
- **Plataforma:** orquestração dbt nativa no Snowflake, dynamic tables e programa de custo de Domo e Snowflake (DA-348, DA-350).
- **Discovery:** Samsara (DA-443), Orbcomm (DA-332), EV Analytics (DA-312).

### 4.2 Problemas recorrentes

Classificação dos títulos dos 37 bugs e das histórias de investigação:

1. **Números que não batem entre sistemas** (cerca de 9 bugs: DA-43, DA-184, DA-223, DA-242, DA-247, DA-256, DA-406...): TMW × ADP × Yard Commander × lançamento manual.
2. **Cargas paradas ou tasks falhando** (cerca de 8: DA-127, DA-221, DA-252, DA-290, DA-378, DA-397, DA-446, DA-456).
3. **Identidade de pessoa e de site** (DA-309, DA-346, DA-408, DA-405, a regex de departamento e o `CASE` de sites): login sem mapeamento distorce a produtividade (2,8 contra 3,2 a 3,5 movimentos por motorista-hora num site, DA-408), e site em texto livre distorce o safety.
4. **Duplicatas e chaves** (DA-281, DA-385, commits de setembro).
5. **Tempo:** semana, fuso e virada de turno (DA-195, DA-435, DA-447; DA-360 e DA-372 para criar uma macro única de início de semana).
6. **Dívida de engenharia** listada em DA-349 a DA-377: sources não declaradas, falta de testes e de freshness.

### 4.3 Observações de governança relevantes para o projeto

- As edge functions do YardSafe entram no Snowflake com senha e papel `ACCOUNTADMIN`. A troca por usuário de serviço já é o item DA-449.
- O código do YardSafe está numa conta pessoal do GitHub. A página de soft launch recomenda limpar o export do MS Forms do histórico antes de qualquer migração de repositório. Hoje o arquivo está ignorado (`.gitignore`, `*.xlsx`), mas foi commitado em `7704055` e só deixou de ser rastreado em `9c23e05`. **Continua no histórico** [verificado com `git log --all`].
