# 03. Perguntas em aberto

Decisões e confirmações que dependem de você. Nenhuma travou a Fase 1 ou a Fase 2; elas afetam a escolha da ideia e a Fase 3. Ordem: primeiro o que bloqueia a escolha.

## A. Edital e programa

1. **Edital do MECAI.** Ainda não está no repositório. Salve o PDF em `programa/` (onde já estão as linhas de pesquisa e o horário). **Já respondido pela FAQ (2026-11-08, ver `programa/README.md`):** roteiro do projeto (introdução, corpo com metodologia, bibliografia), sem vínculo com orientador, 36 meses para depósito, sem exame de qualificação, 48 créditos em disciplinas. **Falta conferir no edital:** limite de páginas, fonte e espaçamento, norma da bibliografia, se pede indicação de linha de pesquisa, a ênfase de 2027 e os documentos de comprovação profissional.
2. **Linha de pesquisa.** Se escolher a Ideia 8, a proposta é Modelagem de Risco. O edital permite indicar uma segunda linha (por exemplo, Inteligência Computacional)?
3. **Comitê de ética.** O projeto usa registros de acidentes de trabalhadores (mesmo que agregados por site). O ICMC ou o edital exigem aprovação em comitê de ética para dados secundários de pessoas? **[não verificado]**

## B. Autorização e governança na YMX

**Adiado (decisão de 2026-11-08):** a autorização só será pedida depois da aprovação no mestrado. Até lá, o pré-projeto descreve os dados em termos gerais (ordens de grandeza, sem nome da empresa, sem números exatos internos).

4. **Autorização escrita.** Quem na YMX pode autorizar o uso de dados internos agregados (safety, horas, movimentos) numa dissertação pública? A dissertação pode nomear a YMX, ou deve dizer "empresa de logística de pátios"? Os clientes nunca seriam nomeados.
5. **Dados do Safety.** A área de Safety precisa aprovar o uso dos relatos de acidentes, mesmo agregados?
6. **Onde a análise roda.** Proposta: toda a análise roda dentro do Snowflake da YMX (ou de uma máquina da YMX), e só tabelas agregadas por site e mês saem para o repositório `mestrado`. Concorda?
7. **Texto livre.** Se a Ideia 2 entrar como capítulo auxiliar: mandar descrições de acidentes a um modelo de linguagem externo está fora de questão sem aprovação. Há algum modelo aprovado dentro do Snowflake (Cortex, que o agente de mapeamento já usa via `AI_COMPLETE`)?

## C. Dados a confirmar (bloqueiam a Ideia 8)

8. **Relatos de teste.** A página de soft launch estima cerca de 130 relatos "pending" de mai a out/2026 que parecem teste (item 7, DA-449). Já há lista de quais são reais? Sem isso, as contagens do inventário estão infladas.
9. **Correspondência de sites [respondida em parte].** A `DIM_SITES_TREATED` existe em `RAW.ACCIDENTS_INJURIES` (53 linhas, atualizada em 2026-07-30), e as tags da Samsara trazem o código ADP. Não encontrei nenhum "Driver Registry" ou "Site Registry". Falta saber quem mantém a `DIM_SITES_TREATED`; pela data, parece carga manual.
10. **Campus do Yard Commander × departamento ADP [verificado que não existe].** Nenhum dos 38 campi traz código no nome. A ponte precisa ser montada (38 itens: uma tabela pequena, revisável à mão, e eu posso propor o primeiro rascunho por similaridade de nome).
11. **Histórico do `ASSETEVENTS` [respondida].** 11,6 milhões de linhas, de 2023-04 a hoje. Os modelos do dbt olham só 365 dias.
12. **IQDOX = Yard Commander?** Confirma que `DOMOVIEW.IQDOX` é a camada de dados (via Domo) dos eventos do Yard Commander?
13. **Número do caminhão [respondida em 2026-11-08].** O `truck_number` do YardSafe casa com o nome do veículo Samsara em 71% dos relatos. Com o Yard Commander não dá: o `YARDTRACTORID` aparece em só 1.696 de 11,6 milhões de eventos, e o `DRIVERID` em nenhum. O trator existe na tela do Yard Commander mas não chega ao `IQDOX`? Se for só uma questão de exportação, valeria um pedido ao time de produto do Yard Commander, porque isso ligaria movimento de pátio a caminhão.
14. **Samsara.** Os dados estão em `RAW_FIVETRAN.SAMSARA` (inventário, seções 3.1 a 3.4).
    - **Fivetran parado [respondida]:** pausado de propósito, por custo. O dado congelado (set/2025 a 13/10/2026) já serve ao pré-projeto. Decisão sua para depois: reativar só as 7 tabelas pequenas que o projeto usa (cerca de 0,07% das linhas; o volume está na tabela de leituras de sensores e no GPS) ou fazer uma carga única antes de março de 2027. Confira no painel do Fivetran se o custo era mesmo dessas tabelas grandes.
    - **Tags [respondida]:** as tags filhas das regiões são sites, com código ADP no nome; 95% dos caminhões ativos têm uma.
    - **Uso para pesquisa [sem resposta nos sistemas]:** não há política, dono nem regra de uso documentados no Confluence ou no Jira. Caminho sugerido:
      1. Pergunte a quem pediu o discovery da Samsara (DA-443) quem é o dono do contrato e se ele restringe uso secundário dos dados.
      2. Pergunte ao RH ou ao jurídico se há termo assinado pelos motoristas sobre câmera e telemetria, e se ele cobre análise interna agregada.
      3. Peça à área de Safety o aval para os relatos.
      4. Junte tudo numa única autorização escrita da YMX para o projeto, citando que só saem agregados por caminhão, site e mês, sem nome, sem imagem e sem trajeto.

      Posso redigir o rascunho dessa autorização em inglês quando quiser.
    - O documento de discovery do DA-443 é um arquivo de workspace e não deu para ler pelo SQL. Se quiser que eu considere as conclusões dele, cole o texto ou salve uma cópia local.
15. **Exposição na série do MS Forms.** Antes do app, qualquer pessoa reportava pelo Forms. Houve mudança de regra de notificação (o que conta como "incident") ao longo de 2025 e 2026?

## D. Consultas leves pendentes no Snowflake

**Todas rodadas em 2026-11-08** pelo usuário de serviço só de leitura (`CLAUDE_CODE_SVC`, via `~/.snowflake/claude_sf.py`). Os resultados estão no inventário, seções 3.1 a 3.4. Ficam abaixo como registro do que foi consultado.

```sql
-- 1. Linhas e tamanho das tabelas candidatas (metadados, sem varrer dados)
select table_catalog, table_schema, table_name, row_count, bytes, last_altered
from DOMOVIEW.INFORMATION_SCHEMA.TABLES
where table_schema = 'IQDOX' and table_name in ('ASSETEVENTS', 'AML');

select table_schema, table_name, row_count, last_altered
from RAW.INFORMATION_SCHEMA.TABLES
where table_schema = 'ACCIDENTS_INJURIES';

select table_schema, table_name, row_count, last_altered
from ANALYTICS_DB.INFORMATION_SCHEMA.TABLES
where table_schema in ('MARTS', 'YMX_AUDIT')
  and table_name in ('FACT_MOVES_DROPOFF_COMPLETE', 'FACT_TIMECARD_SUPERVISOR_PAY_CODE',
                     'DIM_SITE', 'DIM_DEPARTMENT', 'YMX_USER_MAP');

-- 2. Período coberto pelo histórico bruto do pátio (só mínimo e máximo)
select min(sourcetransactiondatetime), max(sourcetransactiondatetime), count(distinct campusname)
from DOMOVIEW.IQDOX.ASSETEVENTS;

-- 3. Horas ADP por mês (exposição agregada, sem pessoa)
select date_trunc('month', time_in) as mes, count(distinct timecard_work_department) as departamentos,
       round(sum(hours)) as horas
from ANALYTICS_DB.MARTS.FACT_TIMECARD_SUPERVISOR_PAY_CODE
group by 1 order by 1;

-- 4. Existe a tabela de sites tratados citada no DA-450?
select table_catalog, table_schema, table_name, row_count
from ANALYTICS_DB.INFORMATION_SCHEMA.TABLES
where table_name ilike '%SITE%';

-- 5. Há dados da Samsara no Snowflake?
select table_catalog, table_schema, table_name, row_count
from SNOWFLAKE.ACCOUNT_USAGE.TABLES
where deleted is null and (table_name ilike '%SAMSARA%' or table_schema ilike '%SAMSARA%');
```

Observações sobre as consultas:

- A consulta 3 usa nomes de colunas tirados do código do `stg_adp__timecard_supervisor_pay_code`. Se algum nome divergir na tabela final, ajuste.
- A consulta 5 precisa de acesso ao `ACCOUNT_USAGE`.

## E. Domo

16. Qual dataset alimenta hoje o Domo App de Safety: a carga antiga do MS Forms (`fact_accidents_injuries`) ou a cópia do app (`INCIDENTS`)? A página de soft launch diz que isso precisa ser confirmado (item 8).

## F. Plano B (Data Solo)

17. Você tem vínculo profissional formal com a Data Solo hoje? Isso define se a Ideia 7 atende ao requisito de "compatível com a atividade profissional".
18. As usinas autorizaram o uso dos laudos numa dissertação? Esse item já está em aberto no `PENDENCIAS.md` do mestrado.

## G. Repositório

19. **Repositório [resolvida em 2026-11-08].** O trabalho começou em `mestrado/icmc/` e foi movido para este repositório (`icmc`), que passou a ser privado. A branch temporária no `mestrado` foi removida.
20. **Merge para a `main`.** O trabalho está na branch `preprojeto`. Fazer merge na `main` quando quiser (não há nada mais na `main` além do README).
21. **Commits.** Só quando você pedir. Dados, resultados e segredos nunca entram (ver `.gitignore`).
22. **Export do MS Forms no histórico do `yardsafe-log` [verificado].** A planilha com dados pessoais foi commitada em `7704055` ("adding historical data into the app") e removida do rastreamento em `9c23e05`. Hoje nenhum `.xlsx` ou `.csv` está rastreado, mas o arquivo **continua no histórico**. Se o repositório está no GitHub (o remoto é uma conta pessoal), quem tem acesso pode baixá-lo. Vale limpar o histórico (por exemplo, com `git filter-repo`) e checar quem tem acesso. Não fiz nada lá, que é somente leitura.
