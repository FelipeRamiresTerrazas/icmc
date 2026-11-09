# 02. Ideias de projeto (Fase 2)

Base: o inventário em `01-inventario-dados.md`. Evidências citadas por arquivo, tabela ou ticket. O que não foi conferido está marcado **[não verificado]**. Referências bibliográficas ficam para a Fase 3: aqui só aparecem nomes de métodos consagrados, e qualquer citação será conferida na fonte antes de entrar no `.bib`.

## Critérios e notas (1 a 5)

| Critério | 5 significa |
| :-- | :-- |
| **Valor YMX** | Resolve um problema que aparece em ticket, painel ou reclamação, e alguém vai usar o resultado |
| **Aderência MECAI** | Cabe numa das linhas e na ênfase em Ciência de Dados, com contribuição metodológica defensável |
| **Dados até mar/2027** | Os dados já estão em mãos ou a extração é trivial e autorizável até março de 2027 |
| **Contribuição** | Há pergunta científica, baseline claro e avaliação que permite concluir algo |
| **Risco técnico** (5 = baixo) | Poucos eventos, falta de exposição ou dependência de terceiros não inviabilizam o trabalho |
| **Privacidade e autorização** (5 = sem problema) | Dados de motoristas, RH, clientes ou texto sensível exigem pouco tratamento |

A nota final soma os seis critérios, com **peso 2 em "Dados até mar/2027"**: a inscrição é em abril ou maio de 2027 e o pré-projeto precisa mostrar que os dados existem.

## Ideia 1. Risco de acidentes ajustado por exposição, por site e período

*Sua ideia "análise de sobrevivência e/ou risco", reformulada.*

**Por que reformular.** A análise de sobrevivência por motorista precisa ligar cada acidente a uma pessoa e a suas horas. Hoje isso não existe: o ID do funcionário está preenchido em 8 de 644 relatos (seção 2.2 do inventário), e a ligação por nome seria frágil e sensível. No nível de **site × semana (ou mês)**, as duas pontas existem: o código de site ADP no relato e as horas ADP por departamento.

- **Pergunta.** Depois de ajustar pela exposição (horas trabalhadas e movimentos de pátio), quais sites têm taxa de acidentes realmente acima do esperado? Quanto do ranking atual ("dias sem incidente", DA-450) é ruído de volume?
- **Hipóteses.**
  - H1: um modelo hierárquico com exposição prevê melhor a contagem futura por site que a taxa bruta e que o histórico de contagens.
  - H2: o ranking por dias sem incidente muda de forma relevante quando se ajusta por exposição e se encolhe a estimativa dos sites pequenos.
  - H3: o tipo de operação (spotter, shuttle, OTR), o volume por hora e a proporção de horas extras explicam parte da variação entre sites.
- **Dados.**
  - Eventos: YardSafe, 644 relatos de set/2025 a nov/2026, menos os testes (cerca de 130, a confirmar).
  - Exposição em horas: `fact_timecard_supervisor_pay_code` (horas por batida e departamento) [verificado no código].
  - Exposição em movimentos: `fact_moves_dropoff_complete` (movimentos por campus e dia) [verificado no código].
  - Covariáveis: tipo de serviço em `dim_department`, horas extras e não faturáveis em `fact_operations_kpi_labor_efficiency`.
  - Falta a correspondência site ↔ campus ↔ departamento para os relatos antigos (40% com site fora do `CASE` do dbt) e para os campi do Yard Commander.
- **Método.** Regressão de Poisson e binomial negativa com offset de exposição. Modelo hierárquico (efeito aleatório de site, bayesiano ou bayes empírico) com componente temporal. Gráficos de funil e probabilidade a posteriori de o site estar acima de um limiar. Extensão possível: dois tipos de evento (acidente e lesão) num modelo multivariado.
- **Baselines a bater.** (a) Taxa bruta por site; (b) contagem do período anterior; (c) Poisson sem efeito de site.
- **Avaliação.** Validação temporal (treino até um mês, teste nos seguintes), log-score preditivo e calibração. Estabilidade do ranking entre janelas. Comparação com o "dias sem incidente".
- **Valor para a YMX.** Alto. Troca um indicador sensível ao volume por um ajustado ao risco, com incerteza, no painel que a área de Safety já usa (Domo, DA-450). Ajuda a priorizar auditoria e treinamento.
- **Linha MECAI.** Modelagem de Risco.
- **Riscos.**
  - Poucos eventos por site: em torno de 500 eventos reais em 80 sites e 14 meses, média abaixo de 1 por site e mês. É justamente o caso em que o modelo hierárquico se justifica, mas limita o número de covariáveis.
  - Mudança de sistema no meio da série (MS Forms → app em nov/2026) pode mudar a taxa de notificação.
  - Correspondência de sites (ver Ideia 3).
  - Privacidade: como o nível é site, só horas agregadas do ADP saem do Snowflake.
- **Viabilidade até mar/2027.** Média para alta. Eventos e horas existem; a correspondência de sites é o gargalo.
- **Atualização em 2026-11-08 (Samsara verificada, inventário seção 3).** O `truck_number` dos relatos casa com o veículo Samsara em 71% dos casos. Isso abre uma segunda unidade de análise, **caminhão × mês**, com:
  - exposição medida (milhas e horas de viagem de `VEHICLE_TRIP`);
  - preditores de comportamento (taxa de frenagem, curva brusca, velocidade e celular por mil milhas, de `SAFETY_EVENT`);
  - um desfecho independente (colisões detectadas pela Samsara) para comparar com os relatos.

  A pergunta passa a ser também se a taxa de eventos de direção de um caminhão prevê acidente reportado, ajustando por exposição. São cerca de 250 veículos e 13 meses, sem precisar de dado pessoal do motorista.
- **Segunda atualização (2026-11-08).** As tags da Samsara carregam o código de departamento ADP, com 95% dos caminhões ativos marcados. A cadeia relato → caminhão → site → horas ADP existe sem texto livre (inventário 3.4). Com isso, o gargalo da correspondência de sites cai para os relatos antigos e para os 38 campi do Yard Commander.
- **Versão recomendada da Ideia 1 (caminhão × mês).**
  - **Desfecho:** acidentes reportados (YardSafe) por caminhão e mês.
  - **Exposição:** milhas e horas da Samsara.
  - **Preditores:** taxas de eventos de direção por mil milhas (frenagem, curva, velocidade, celular, cinto), tipo de uso (spot, shuttle, local), combustível (diesel, EV), idade do veículo.
  - **Estrutura:** efeito aleatório de site, por meio da tag.
  - **Objetivos secundários:** (a) estimar a subnotificação, comparando colisões detectadas pela Samsara com relatos do mesmo caminhão e dia; (b) agregar por site e comparar com o "dias sem incidente".
  - **Escala:** cerca de 260 caminhões × 13 meses, cerca de 3.400 células, com cerca de 400 relatos casados com caminhão.
- **Notas.** Valor 5 · Aderência 5 · Dados 5 · Contribuição 5 · Risco 4 · Privacidade 3. Dados subiu para 5 com a ponte por tags. Contribuição subiu para 5 com a telemetria e a subnotificação. Risco melhora porque a exposição é medida. Privacidade cai para 3: telemetria por caminhão pode identificar o motorista fixo, então a publicação só pode ter agregados.

## Ideia 2. Classificação de causa raiz e triagem a partir dos textos livres

*Sua ideia "classificação de causa e gravidade", ajustada.*

**Ajuste.** Não há rótulo de gravidade: OSHA Recordable é 0 e DART é 1 (inventário 2.2). O que existe como rótulo é a **causa raiz** (12 categorias, 87% preenchida) e o **pedido de seguro** (sim ou não, 47% preenchido no Forms). Gravidade só poderia entrar como rótulo novo, anotado pela área de Safety.

- **Pergunta.** Um classificador lê a descrição e o depoimento do motorista e acerta a causa raiz? As divergências entre o texto e a categoria escolhida revelam erro de preenchimento?
- **Hipóteses.** H1: modelos de texto superam a classe majoritária e um TF-IDF com regressão logística em F1 macro. H2: parte dos erros do modelo é erro de rótulo, verificável por revisão humana numa amostra.
- **Dados.**
  - Cerca de 560 descrições (mediana de 158 caracteres) e cerca de 460 depoimentos (mediana de 203), em inglês.
  - Rótulos de causa raiz.
  - Tudo no Supabase e no export do Forms [verificado].
- **Método.** TF-IDF + regressão logística (baseline). Embeddings de sentença com classificador linear. Modelo de linguagem em zero-shot e few-shot. Detecção de rótulos ruidosos (aprendizado confiante, por exemplo). Calibração das probabilidades para sugerir a categoria no app.
- **Avaliação.** Validação cruzada estratificada (F1 macro e por classe, matriz de confusão). Revisão cega por Safety de uma amostra de discordâncias.
- **Valor para a YMX.** Médio. Sugestão automática no formulário e auditoria da qualidade da causa raiz, que alimenta os planos de ação.
- **Linha MECAI.** Inteligência Computacional.
- **Riscos.**
  - Amostra pequena para 12 classes, algumas com menos de 20 exemplos.
  - Os textos têm nomes, placas e detalhes médicos: precisam de anonimização antes de sair do ambiente da YMX, e não se pode mandar texto a um modelo externo sem aprovação.
  - A contribuição científica é modesta se for só "comparar classificadores".
- **Viabilidade até mar/2027.** Alta.
- **Notas.** Valor 3 · Aderência 4 · Dados 4 · Contribuição 3 · Risco 3 · Privacidade 2.

## Ideia 3. Resolução de entidades de pessoas e sites entre sistemas

*Sua ideia "entity resolution no Driver/Site Registry", melhorada.*

**Nota.** Não encontrei nenhum objeto chamado "Driver Registry" ou "Site Registry" no dbt, no Jira ou no Confluence **[não verificado: pode ter outro nome]**. O que existe é o `YMX_USER_MAP` (pessoas), o `dim_site`/`dim_department` (sites do ADP), o `CASE` de sites do safety e uma `DIM_SITES_TREATED` citada no DA-450.

- **Pergunta.** Um modelo probabilístico de ligação de registros, treinado com as decisões humanas que o agente já registra, liga logins, funcionários e sites com precisão e cobertura maiores que as regras atuais? Como a incerteza da ligação se propaga para os KPIs?
- **Hipóteses.** H1: um modelo de Fellegi e Sunter com parâmetros estimados por EM, ou um classificador supervisionado de pares, supera Jaro-Winkler com limiar fixo em F1, com a precisão fixada. H2: aprendizado ativo (pedir ao revisor os pares mais informativos) reduz o número de revisões para a mesma qualidade. H3: ignorar a incerteza da ligação enviesa produtividade e taxa de acidentes por site de forma mensurável (o caso do DA-408 é um exemplo).
- **Dados.**
  - Pessoas: logins do Yard Commander × ADP, com 1.506 linhas no mapa e 194 pares com ID usados como verdade (DA-405, DA-415). Decisões e auditoria no esquema `YMX_AUDIT` (contagens [não verificado]).
  - Sites: 131 grafias no safety, `CAMPUSNAME` do Yard Commander, departamentos ADP, `site_location_code` do app.
- **Método.**
  - Bloqueio, comparadores por campo e Fellegi-Sunter com EM.
  - Classificador supervisionado de pares (gradient boosting).
  - Aprendizado ativo.
  - Clusterização para garantir transitividade.
  - Propagação da incerteza por amostragem de ligações plausíveis para os KPIs.
- **Baselines a bater.** O motor atual (normalização + Jaro-Winkler + regras) e o `CASE` do dbt.
- **Avaliação.** Precisão, cobertura e F1 em pares rotulados, com divisão temporal (logins novos). Custo de revisão humana. Efeito nos KPIs com e sem incerteza.
- **Valor para a YMX.** Alto. Identidade de pessoa e de site é o problema recorrente número 3 (inventário 4.2) e afeta faturamento, produtividade e safety.
- **Linha MECAI.** Inteligência Computacional, ou Visualização e Mineração Visual de Dados se a ênfase for a revisão humana.
- **Riscos.**
  - Parte do trabalho já está feita (o agente está em produção), então a banca vai perguntar o que é novo.
  - Nomes de funcionários são dados pessoais: o trabalho precisa rodar dentro do Snowflake da YMX e publicar só métricas.
  - Pode ser visto como engenharia de dados se a parte estatística (EM, aprendizado ativo, propagação de incerteza) não ficar no centro.
- **Viabilidade até mar/2027.** Muito alta. Os dados são seus e o rótulo já está sendo produzido toda semana.
- **Notas.** Valor 4 · Aderência 4 · Dados 5 · Contribuição 3 · Risco 4 · Privacidade 3.

## Ideia 4. Tempo de permanência (dwell) de trailers com análise de sobrevivência

*Sua ideia "previsão de permanência ou atraso", com foco em dwell.*

- **Pergunta.** Que fatores (cliente, transportadora, status de carga, área, dia e hora de chegada, ocupação do pátio) explicam o tempo até a saída de um trailer? Dá para prever, na chegada, a probabilidade de passar de um limiar de cobrança (detention)?
- **Hipóteses.** H1: modelos de sobrevivência que tratam a censura (trailers ainda no pátio no snapshot) superam a regressão no tempo observado, que exclui ou trunca os censurados. H2: a ocupação do pátio na chegada tem efeito não linear no dwell.
- **Dados.**
  - Eventos de gate e move em `ASSETEVENTS` (`fact_gate_transactions`) [verificado no código].
  - Snapshots de inventário com "Location Dwell Time", "Age (Days)" e "In Location Since" para alguns clientes [verificado no código].
  - Painéis de dwell de porta já entregues (DA-333, DA-345, DA-391).
  - Volume e histórico: **[não verificado]**. O dbt só olha 365 dias.
- **Método.** Kaplan-Meier e Cox com efeitos de site. Modelos paramétricos de tempo de falha acelerado. Random survival forests. Riscos competitivos (saída carregado × vazio) se fizer sentido. Previsão dinâmica a partir do tempo já decorrido.
- **Baselines a bater.** Mediana histórica por cliente e transportadora; regressão linear no log do tempo sem censura.
- **Avaliação.** Índice C, escore de Brier integrado e calibração em horizontes de cobrança, com validação temporal.
- **Valor para a YMX.** Médio para alto. Atende o cliente (planejamento de porta, cobrança de detention) e alimenta produto vendável (relatórios de Yard Commander, DA-282).
- **Linha MECAI.** Modelagem de Risco (sobrevivência), com interface com Pesquisa Operacional.
- **Riscos.**
  - Dados de clientes são informação comercial: precisa de autorização da YMX e possivelmente do cliente.
  - Os campos de inventário mudam por cliente.
  - A qualidade dos eventos de gate não foi verificada.
- **Viabilidade até mar/2027.** Média. Os dados existem em volume, mas a extração histórica e a autorização não estão confirmadas.
- **Notas.** Valor 4 · Aderência 5 · Dados 3 · Contribuição 4 · Risco 4 · Privacidade 3.

## Ideia 5. Previsão probabilística de movimentos e dimensionamento de escala

*Ideia nova.*

- **Pergunta.** Uma previsão probabilística de movimentos por campus, hora e dia, ligada a um modelo de otimização de escala, reduz horas extras e horas não faturáveis sem piorar o tempo de resposta?
- **Hipóteses.** H1: modelos com sazonalidade semanal e intradiária e com quantis bem calibrados superam a previsão atual (notebook diário) em escore probabilístico. H2: a escala ótima sob incerteza (programação estocástica ou newsvendor por turno) tem custo esperado menor que a escala realizada, em simulação retrospectiva.
- **Dados.**
  - Previsão atual e realizado (`fact_moves_predicted_vs_actual`).
  - Movimentos por hora e campus (`fact_moves_hourly_by_campus`, DA-433).
  - Escala planejada × realizada do ADP (`fact_adp_scheduled_vs_actual_daily`).
  - Horas extras e não faturáveis (`fact_operations_kpi_labor_efficiency`).
  - Tudo no dbt [verificado no código]. Volumes [não verificado].
- **Método.** Baselines sazonais ingênuos, ETS e modelos com regressão de quantis ou gradient boosting de quantis. Avaliação com escore probabilístico próprio (CRPS ou pinball). Otimização de escala por turno com programação inteira e cenários.
- **Avaliação.** Validação temporal da previsão. Simulação retrospectiva da escala proposta contra a realizada, em horas, custo e cobertura.
- **Valor para a YMX.** Alto. Produtividade e horas faturadas são os KPIs centrais (DA-405, DA-407).
- **Linha MECAI.** Pesquisa Operacional, com previsão.
- **Riscos.**
  - A avaliação da escala é contrafactual: precisa de premissas sobre tempo de resposta que a operação aceite.
  - A previsão atual roda num notebook fora do dbt, e como ela é feita não foi verificado.
  - Depende de dados de RH, ainda que agregados por site e turno.
- **Viabilidade até mar/2027.** Alta para a previsão; média para a otimização.
- **Notas.** Valor 5 · Aderência 5 · Dados 4 · Contribuição 4 · Risco 2 · Privacidade 3.

## Ideia 6. Monitoramento estatístico da qualidade do pipeline de dados

*Ideia nova, de menor prioridade.*

- **Pergunta.** Controle estatístico de processo aplicado a métricas das tabelas (linhas por dia, atraso de carga, taxa de nulos, duplicatas) detecta as falhas que hoje viram bug, e com que antecedência?
- **Dados.** Metadados do Snowflake (histórico de consultas e de dynamic tables) e os 37 bugs como eventos rotulados. Metadados [não verificado].
- **Método.** Gráficos de controle (CUSUM, EWMA), detecção de ponto de mudança e modelos sazonais de contagem. Avaliação pelos bugs reais: atraso de detecção e alarmes falsos.
- **Valor para a YMX.** Médio. Cargas paradas são o problema recorrente número 2.
- **Linha MECAI.** Métodos Matemáticos e Numéricos, ou Modelagem de Risco.
- **Riscos.** 37 bugs são poucos para avaliar. Ferramentas comerciais de observabilidade já fazem algo parecido, o que enfraquece a contribuição.
- **Viabilidade até mar/2027.** Alta.
- **Notas.** Valor 3 · Aderência 3 · Dados 4 · Contribuição 2 · Risco 4 · Privacidade 5.

## Ideia 7. Plano B: método e escala de interpolação de solo (Data Solo)

- **Situação.** O trabalho está adiantado em `mestrado/`: pré-projeto completo, rascunho de dissertação, pipeline de simulação com 120 fazendas sintéticas, módulo próprio de geoestatística (REML, modelos aninhados, dose esperada) e análise de laudos reais de 57 fazendas.
- **Pergunta.** A mesma do pré-projeto da ESALQ: efeito do método e da escala de interpolação sobre a dose recomendada, com amostragem esparsa.
- **Adaptação ao ICMC.** Deslocar a ênfase do resultado agronômico para a contribuição de método: avaliação orientada à decisão, propagação de incerteza e dose esperada sob a distribuição preditiva.
- **Valor para a YMX.** Nenhum.
- **Linha MECAI.** Métodos Matemáticos e Numéricos (estatística espacial).
- **Riscos.**
  - O edital pede compatibilidade com a atividade profissional. Se o seu vínculo atual é a YMX, isso fica fraco, a menos que exista vínculo formal com a Data Solo **[não verificado]**.
  - Autorização das usinas para uso dos laudos.
  - Pendências de referências (lista em `PENDENCIAS.md`).
- **Viabilidade até mar/2027.** Muito alta: código, dados e texto existem.
- **Notas.** Valor 1 · Aderência 4 · Dados 5 · Contribuição 4 · Risco 4 · Privacidade 3.

## Ideia 8. Combinação de 1 e 3: risco de acidentes com ligação incerta de fontes

*Combinação proposta: a Ideia 1 como objetivo e a Ideia 3 como etapa metodológica.*

- **Pergunta.** Como estimar a taxa de acidentes por site, ajustada por exposição, quando os eventos, as horas e os movimentos vêm de sistemas sem chave comum? Quanto a incerteza da ligação muda o ranking de risco?
- **Estrutura em três etapas.**
  1. **Ligação de sites** entre os relatos (131 grafias), os departamentos ADP e os campi do Yard Commander, com modelo probabilístico e revisão humana. Rótulos: os 221 relatos que já têm código ADP servem de verdade para treinar e testar. Produz uma tabela de correspondência que a YMX não tem (DA-450 depende disso).
  2. **Modelo hierárquico de contagem com exposição** (Ideia 1), ajustado com a ligação incerta: múltiplas imputações da correspondência propagadas até a posteriori.
  3. **Indicador para o painel de Safety:** taxa ajustada com incerteza, comparada ao "dias sem incidente".
- **Com a Samsara (verificada em 2026-11-08).** A ligação deixa de ser só de sites. Os relatos ligam a caminhões (71% por igualdade exata, e mais com normalização e janela de tempo), e caminhões a exposição e comportamento de direção. O modelo pode ter dois níveis, caminhão dentro de site. Isso também permite estimar a **subnotificação**, comparando colisões detectadas pela Samsara com relatos no YardSafe no mesmo caminhão e dia. Requisitos: religar o Fivetran (parado desde 13/10/2026) e aprovar o uso de telemetria.
- **Por que é mais forte que as partes.**
  - A etapa 1 usa dados já em mãos e entrega valor sozinha, o que reduz o risco de poucos eventos.
  - A pergunta científica fica clara: inferência com registros ligados de forma imperfeita, que é tema estabelecido em estatística.
  - Liga o trabalho diretamente a dois problemas recorrentes da YMX: identidade de site e indicador de safety.
- **Baselines.** O `CASE` atual do dbt mais a taxa bruta; Jaro-Winkler com limiar mais Poisson sem efeito de site; ligação determinística (ignorando a incerteza) mais o modelo hierárquico.
- **Avaliação.** F1 da ligação em relatos com código conhecido; log-score preditivo temporal das contagens; mudança no ranking com e sem incerteza.
- **Linha MECAI.** Modelagem de Risco, com Inteligência Computacional na etapa de ligação.
- **Riscos.**
  - **Escopo:** são duas frentes. Para um mestrado profissional, a etapa 1 deve se limitar a sites (não pessoas), e o modelo da etapa 2 deve se manter simples.
  - A mudança de sistema em nov/2026 afeta a taxa de notificação.
  - Os relatos de teste precisam ser removidos antes.
  - Privacidade: o nível é site, então nenhum dado individual de motorista ou de RH sai do Snowflake.
- **Viabilidade até mar/2027.** Alta para a etapa 1, média para alta para a etapa 2. Por volta de março haverá cerca de 18 meses de relatos e 4 meses do app com código de site limpo.
- **Notas.** Valor 5 · Aderência 5 · Dados 4 · Contribuição 4 · Risco 4 · Privacidade 4.

## Tabela comparativa

| # | Ideia | Linha MECAI | Valor | Aderência | Dados (×2) | Contribuição | Risco | Privacidade | **Total** |
| :-- | :-- | :-- | --: | --: | --: | --: | --: | --: | --: |
| 1 | Risco ajustado por exposição (caminhão × mês, com Samsara) | Modelagem de Risco | 5 | 5 | 5 | 5 | 4 | 3 | **32** |
| 8 | Risco com ligação incerta (1+3) | Modelagem de Risco | 5 | 5 | 5 | 3 | 4 | 4 | **31** |
| 3 | Resolução de entidades | Intelig. Computacional | 4 | 4 | 5 | 3 | 4 | 3 | **28** |
| 5 | Previsão e escala | Pesquisa Operacional | 5 | 5 | 4 | 4 | 2 | 3 | **27** |
| 4 | Dwell com sobrevivência | Modelagem de Risco | 4 | 5 | 3 | 4 | 4 | 3 | **26** |
| 7 | Plano B: solo | Métodos Mat. e Numéricos | 1 | 4 | 5 | 4 | 4 | 3 | **26** |
| 6 | Qualidade do pipeline | Mét. Mat. e Num. / Risco | 3 | 3 | 4 | 2 | 4 | 5 | **25** |
| 2 | Texto: causa raiz | Intelig. Computacional | 3 | 4 | 4 | 3 | 3 | 2 | **23** |

Total = Valor + Aderência + 2 × Dados + Contribuição + Risco + Privacidade (máximo 35).

## Ranking

1. **Ideia 1 na versão caminhão × mês** (32). Subiu duas vezes em 2026-11-08: com a Samsara e com a ponte de sites pelas tags.
2. **Ideia 8**: risco com ligação incerta (31). Dados subiu para 5, mas a contribuição caiu para 3: a ligação de sites ficou em boa parte determinística (tags e código no app), então a "ligação incerta" deixou de ser um eixo forte de pesquisa. O que resta de ligação (relatos antigos, 29% dos caminhões sem casamento exato, 38 campi) vira etapa de preparo da Ideia 1.
3. **Ideia 3**: resolução de entidades (28).
4. **Ideia 5**: previsão de movimentos e escala (27).
5. **Ideia 4**: dwell com sobrevivência (26). Empata com a 7 e fica à frente por ter valor para a YMX.
6. **Ideia 7**: plano B de solo (26).
7. **Ideia 6**: qualidade do pipeline (25).
8. **Ideia 2**: classificação de texto (23). Pode virar um capítulo auxiliar da 8 (causa raiz como covariável), sem ser o tema.

Cautela sobre o ranking: a Ideia 8 é uma combinação montada a partir das duas melhores, e o principal risco dela (escopo) aparece só parcialmente nas notas. A Ideia 3 sozinha é a opção mais segura em dados; a 8 é a de maior valor e mais fácil de defender como pesquisa.

## Recomendação

**Atualizada em 2026-11-08, depois das descobertas no Snowflake:** a **Ideia 1 na versão caminhão × mês**, com a ligação dos relatos antigos e dos campi como etapa de preparo, absorvendo o que sobrou da Ideia 8. A **Ideia 5** segue como segunda opção.

Título provisório: *Risco de acidentes em operações de pátio: modelos hierárquicos de contagem com exposição e telemetria*.

Os motivos abaixo foram escritos para a Ideia 8 e continuam válidos para a versão nova. A diferença é que a unidade principal passa a ser o caminhão, e o site entra como nível superior.

Motivos:

1. Resolve um problema que a YMX já declarou. O DA-450 pede um "dias sem incidente" confiável e depende de mapear sites. O inventário mostra que 40% dos relatos históricos não são mapeados pelo `CASE` atual.
2. Os dados centrais existem e são seus: relatos (YardSafe), horas (ADP no dbt) e movimentos (Yard Commander no dbt). Trabalhar no nível de site evita os dados individuais de motorista e de RH.
3. Tem pergunta estatística clara para a banca (inferência com ligação imperfeita, eventos raros com exposição), baseline explícito e avaliação temporal.
4. Não depende de nenhum docente específico: modelos hierárquicos de contagem e ligação de registros são temas gerais de estatística e ciência de dados.
5. O risco de poucos eventos é amortecido: a etapa de ligação se sustenta sozinha, e o encolhimento hierárquico é a resposta de método para a contagem baixa.

6. A Samsara, verificada em 2026-11-08, dá exposição medida (milhas, horas) e comportamento de direção por caminhão, ligável aos relatos em 71% dos casos. A unidade de análise pode descer de site para caminhão sem usar dado pessoal de motorista.

Condições para confirmar a escolha (detalhes em `03-perguntas-em-aberto.md`):

- Autorização escrita da YMX para usar dados internos agregados numa dissertação pública.
- Confirmação da limpeza dos relatos de teste.
- Acesso às horas ADP agregadas por departamento e dia.
- Contagem real de movimentos por campus no histórico.
- Leitura do edital 002/2026 (formato e limite de páginas).
