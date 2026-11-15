# 10. Escala de motoristas: artigo ou expansão da dissertação

Criada em 2026-11-12. **Nota interna**: cita sistemas e tabelas da empresa. O cliente e a unidade do piloto aparecem mascarados ("unidade piloto"); não escrever o nome em nenhum arquivo do repositório.

Fonte: código e README do app Streamlit "Staffing" (`ANALYTICS_DB.PROD.ZCMOL0KVVFHUVZLQ`), lidos pelo usuário de serviço a partir da cópia em `@ANALYTICS_DB.DASHBOARDS.APP_SOURCE` (cópia de 2026-11-12; refazer o `COPY FILES` se o app mudar). Nenhuma tabela de dados foi consultada.

## 1. O que o app faz

1. **Movimentos:** eventos `MOVE - DROPOFF COMPLETE` do sistema de gestão de pátio (`DOMOVIEW.IQDOX.ASSETEVENTS`), agregados por unidade, dia operacional (começa às 06:00) e turno (1: 06 a 14 h; 2: 14 a 22 h; 3: 22 a 06 h).
2. **Motoristas:** `USERID` distintos que concluíram ao menos um movimento (proxy; `DRIVERID` e `YARDTRACTORID` vêm vazios).
3. **Produtividade:** movimentos por motorista-hora (MPDH) = movimentos / motorista-horas, em que motorista-horas soma, hora a hora, os usuários que concluíram algum movimento naquela hora. Mediana (P50) e P80 dos últimos 60 dias por unidade e turno.
4. **Previsão:** Snowflake ML `FORECAST` por unidade e turno, 21 dias à frente, com intervalo de 80%. Retreinada todo dia por uma task.
5. **Regra de escala:** motoristas necessários = teto(movimentos planejados × (1 + folga) / (MPDH × horas do turno × % produtivo)), com mínimo por turno e teto pelo número de tratores. Lacuna = necessários − "equipe atual" (mediana de usuários distintos por turno em 60 dias).
6. **Cenários:** baixo, esperado e alto = limite inferior, previsão e limite superior do intervalo de 80%; ajuste manual de volume.

Por enquanto cobre só uma unidade piloto. O roadmap prevê levar para o dbt, cobrir todas as unidades, trocar o proxy pela escala da folha e criar um modelo de alocação por nível de serviço.

## 2. Pontos de método (valem como motivação de artigo)

### 2.1 Unidades diferentes na comparação da lacuna

Os "necessários" estão em **motoristas equivalentes de turno inteiro**, e a "equipe atual" está em **usuários distintos**. Num dia típico, MPDH ≈ movimentos / motorista-horas, então:

necessários ≈ motorista-horas × (1 + folga) / (horas × % produtivo) = motorista-horas / 6,2 (com os padrões 8 h, 85% e 10%).

Com os valores médios do README da unidade piloto (arredondados):

| Turno | Motorista-horas ativas | Usuários distintos | Horas ativas por usuário | Necessários pela regra |
| --- | --- | --- | --- | --- |
| 1 | cerca de 34 | cerca de 6 | cerca de 6 | cerca de 6 |
| 2 | cerca de 34 | cerca de 10 | cerca de 3,5 | cerca de 6 |
| 3 | cerca de 31 | cerca de 5 | cerca de 6 | cerca de 5 |

O "excedente" do turno 2 vem quase todo do fato de cada usuário aparecer, em média, só cerca de 3,5 horas ativas no turno (sobreposição na troca de turno, gente de outra função usando o sistema, motorista que cobre parte do turno). Não é necessariamente excesso de gente. O próprio README já desconfia disso ("validar contra a folha"). **Correção simples:** comparar em motorista-horas (necessárias contra observadas) ou converter a equipe atual em equivalentes de turno inteiro, até a escala da folha estar ligada.

### 2.2 O % produtivo e a folga são arbitrários e se sobrepõem

- O MPDH já é medido por hora **ativa** (só horas com movimento concluído). Aplicar depois um % produtivo de 85% supõe que o motorista fica ativo 6,8 de 8 horas, o que não foi medido. Esse % pode ser estimado: motorista-horas ativas / horas pagas da folha, por unidade e turno.
- A folga de 10% e o cenário "alto" respondem à mesma pergunta (quanto proteger contra pico). A forma de princípio é escolher o **quantil** da previsão pelo custo relativo de faltar e de sobrar motorista (problema do jornaleiro): q* = c_falta / (c_falta + c_sobra). Isso troca dois parâmetros arbitrários por um custo que a operação sabe estimar (atraso, hora extra, multa contratual contra hora ociosa).

### 2.3 A avaliação da previsão não avalia a decisão

O README compara modelos por MAPE e cobertura do intervalo. Para escala, o que importa é a decisão: quantos turnos ficariam curtos ou com sobra com cada regra, e a que custo. Dá para fazer um backtest de decisão: escalar com a previsão feita no passado e comparar com os movimentos e as motorista-horas que de fato aconteceram. A previsão em si deve ser avaliada por perda quantílica ou CRPS (como no cap. 5 da dissertação), não só por MAPE.

## 3. Ponte com a dissertação

1. **Objetivo (f) já é isso.** O pré-projeto reposicionou a extensão para "previsão da exposição para planejamento de escala e supervisão". O app é a versão real: movimentos por unidade e turno no lugar de horas da folha por unidade e semana. A extensão deixa de ser um exercício genérico.
2. **Carga de trabalho como fator de risco (expansão mais forte).** Com movimentos e motorista-horas por unidade, dia e turno, dá para testar se turnos de alta intensidade (MPDH acima do usual da unidade) ou com escala curta têm mais acidentes por motorista-hora. Liga-se à literatura de horas extras e risco (`dembe2005`) e fecha o ciclo: prever a demanda, dimensionar a escala e mostrar o efeito disso no risco.
   - **Desenho:** painel unidade × dia × turno, Poisson ou binomial negativa com motorista-horas ativas como offset, efeito de unidade, dia da semana e turno; intensidade como desvio em relação à mediana da própria unidade e turno (compara a unidade com ela mesma).
   - **Cuidados:** causalidade reversa (um acidente para o pátio e derruba os movimentos daquele turno; usar a intensidade das horas anteriores ao acidente ou a previsão, não o realizado); poder (acidentes por turno são raríssimos; refazer o estudo de poder do cap. 5 nessa escala).
   - **Dados a conferir:** se o relato de acidente tem hora (para atribuir o turno) **[não verificado]**; quantas unidades usam o sistema de gestão de pátio e desde quando (o modelo antigo cobre 37 unidades; o novo, só a piloto); se o `USERID` dos movimentos pode ser ligado ao caminhão (até agora não pode, `notas/03`, item 13).
3. **Não mexer no núcleo.** H1 a H3 continuam sendo o centro. A carga de trabalho entraria como hipótese secundária (H4) ou como análise da extensão (f), decisão a tomar antes de mudar o pré-projeto.

## 4. Opções de artigo

| Opção | Pergunta | Tipo | Depende de |
| --- | --- | --- | --- |
| A | Da previsão probabilística de movimentos à escala por turno: quantil por custo contra folga fixa, avaliado por backtest de decisão | Aplicado, pesquisa operacional e previsão | Escala da folha por unidade e turno; várias unidades no sistema de pátio |
| B | Intensidade de trabalho e escala curta aumentam o risco de acidentes no pátio? | Segurança, entra na dissertação como H4 ou na extensão (f) | Hora do acidente; poder suficiente |

Recomendação: **B como expansão da dissertação** (é da linha de Modelagem de Risco e usa o mesmo arcabouço) e **A como possível terceiro artigo**, no lugar ou ao lado do artigo de simulação do `09`. Revistas e congressos ainda a escolher **[não verificado]**.

## 5. Próximos passos

1. Decidir se H4 entra no pré-projeto ou fica só na dissertação.
2. Conferir a hora do acidente nos relatos e a cobertura do sistema de pátio por unidade (consultas só de metadados ou agregados).
3. Corrigir a comparação de unidades do app (seção 2.1) antes de usar a lacuna para qualquer decisão de escala.
