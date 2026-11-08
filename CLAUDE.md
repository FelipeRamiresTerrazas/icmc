# Pré-projeto MECAI (ICMC-USP), Felipe

**Sempre responda em português brasileiro.** Mapa do repositório no `README.md`.

## Regras de escrita

- Sem travessão (—) nem `---` em texto novo.
- Nunca inventar referência. Entrada nova no `referencias-icmc.bib` leva `note = {CONFERIR}` até o Felipe checar na fonte. Ao citar resultado de estudo não lido na fonte, escrever de forma geral e marcar `\preencher{conferir ...}`.
- O pré-projeto e qualquer texto externo **não nomeiam a empresa, clientes nem unidades** e usam só ordens de grandeza dos dados (sem números internos exatos) até a autorização formal da empresa, que só será pedida depois da aprovação no mestrado.
- O pré-projeto não cita nem se dirige a nenhum docente: a orientação é definida pela coordenação.
- Bilíngue: parágrafos em `\pt{...}` seguido de `\en{...}`; trechos curtos em `\tr{pt}{en}`. Língua escolhida pelo sufixo `_EN` no `-jobname`. O Felipe edita o português e pede "sincroniza o inglês": atualizar os `\en{}` correspondentes aos `\pt{}` alterados.
- Depois de mudar o texto, recompilar os dois PDFs e conferir visualmente as páginas alteradas.

## Dados e segurança

- Repositório **privado** (tornado privado em 2026-11-08). Os arquivos 01, 02 e 03 são internos: citam a empresa, sistemas e números agregados. Nunca torná-lo público sem antes remover esses arquivos do histórico.
- Dados da empresa nunca entram no git (`dados/`, `resultados/`, csv, xlsx, json, parquet estão no `.gitignore`). Sem segredos, credenciais ou dados pessoais (nomes de motoristas, RH, informação comercial sensível).
- Repositórios e sistemas da empresa (`analytics-dbt-project`, `yardsafe-log`, Snowflake, Jira, Confluence, Domo): **somente leitura**, nunca commitar neles.
- Snowflake: só pelo usuário de serviço somente leitura (`~/.snowflake/claude_sf.py`, chave JWT). Nunca autenticar com senha (a conta pessoal tem MFA e bloqueia). Uma tentativa de conexão; se falhar, parar e reportar. Não usar navegador para isso.
- Consultas só de metadados ou agregados. Nenhum dado real é usado na análise até a autorização.

## Programa

Regras do MECAI resumidas em `04-programa-mecai.md` (36 meses, sem qualificação, 48 créditos em disciplinas). O edital, quando chegar, vai para `referencias/` e prevalece sobre a FAQ.

## Git

Commits e push só quando o Felipe pedir. Trabalho em branch (`preprojeto`), merge na `main` quando ele decidir.
