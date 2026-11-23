# 05. Datasets públicos

Levantamento feito em 2026-11-08 pela API pública do Kaggle (busca por termos como `truck accident`, `fleet telematics`, `harsh braking`, `osha injury`, `fmcsa`, `trucking`, `fleet safety`). Votos, downloads e licenças são os que o Kaggle mostrava nessa data.

**Para que servem:** nenhum substitui os dados da empresa. Eles servem para três coisas:
1. testar o pipeline antes da autorização;
2. mostrar na dissertação que o método roda em dados abertos (reprodutibilidade);
3. dar uma base pública para o plano alternativo por unidade e mês.

Todos ficam fora do git, em `dados/publicos/`.

## 1. Logistics Operations Database (o que você achou)

- **Kaggle:** `yogape/logistics-operations-database`, "3-Year Trucking Operations (2022-2024)".
- **Licença MIT**; cerca de 15 MB zipado e 60 MB extraído; 128 votos, cerca de 12,8 mil downloads, 26 notebooks; atualizado em 2025-11-23.
- **Baixado** em `dados/publicos/logistics-operations-database/` com `analise/dados_publicos.py baixar`.
- **O que é:** transportadora **fictícia**, simulada pelo autor a partir da experiência dele no setor. São 14 tabelas ligadas por chaves:
  - motoristas, caminhões, carretas, clientes, terminais e rotas;
  - cargas e viagens (cerca de 57 mil cada), combustível, manutenção e eventos de entrega;
  - incidentes de segurança (170);
  - duas tabelas mensais agregadas: motorista × mês e **caminhão × mês** (milhas, viagens, manutenção, parada, utilização).
- **Encaixe no projeto:** tem exatamente a forma do nosso painel, caminhão × mês com milhas como exposição e terminal como unidade. O adaptador `analise/dados_publicos.py` monta o painel e roda os modelos de `analise/modelos.py` sem mudança.

**Resultado do primeiro teste (2026-11-08):**

| Item | Valor |
| --- | --- |
| Painel | 3.312 caminhão-mês, 92 caminhões com utilização, 24 terminais |
| Acidentes (Accident + Equipment Damage) | 69; 3.245 meses com 0, 65 com 1, 2 com 2 |
| Média e variância por caminhão-mês | 0,021 e 0,022 (praticamente sem superdispersão) |
| Covariáveis (idade, manutenção, parada) | nenhuma com efeito (todos os IC cruzam zero) |
| Taxa por milhão de milhas por quartil de milhas no mês | 0,74, 0,44, 0,66, 0,52: sem relação clara com a exposição |
| Bayes empírico por terminal | encolhe tudo para a média: a variação entre terminais é compatível com acaso |

**Leitura:** o gerador do dataset parece sortear os incidentes quase independentemente do caminhão, do terminal e das milhas. Isso tem um lado útil e uma limitação:
- **Útil:** é um bom **cenário nulo** para o pipeline. O método não deve "achar" risco onde não há, e não achou.
- **Limitação:** não serve para mostrar efeito de nada. Há também inconsistências típicas de dado simulado, como cidade e estado que não batem ("Seattle, OK").

**Notebooks:** a lista dos 26 notebooks exige login no Kaggle, porque a API pública devolve 401. Para ver, abra a aba Code do dataset logado, ou instale a CLI do Kaggle com seu token (`kaggle kernels list --dataset yogape/logistics-operations-database`). Pela descrição, o foco do autor é SQL, painéis e métricas operacionais (custo por milha, utilização, scorecards de motorista). **Não verificado** se algum notebook modela incidentes com exposição.

## 2. Outros candidatos, por utilidade para o projeto

### Alta: dados reais com contagem e exposição

| Dataset (Kaggle) | O que tem | Licença e tamanho | Uso possível |
| --- | --- | --- | --- |
| `robikscube/osha-injury-data-20162021`, "Work Related Injury Data (2016-2021)" | Cerca de 1 milhão de registros de mais de 100 mil estabelecimentos dos EUA, vindos do formulário OSHA 300A (ITA): **lesões por estabelecimento e ano e horas trabalhadas**, com código de setor (NAICS) | CC0; 321 MB; 6 notebooks | **O melhor análogo público do plano alternativo.** Estabelecimentos de armazenagem e transporte (NAICS 493 e 484) com lesões e horas como offset, modelo hierárquico por empresa e estado, bayes empírico e funil. Dado real. |
| `reedslack/fmcsa-public-safety-data-march-2026-sms-snapshot`, "FMCSA Public Safety Data, March 2026 SMS Snapshot" | Retrato do sistema de segurança das transportadoras dos EUA (SMS): transportadoras, inspeções, violações e acidentes | CC0; 809 MB | Acidentes por transportadora com frota ou milhas como exposição. Conferir na fonte quais campos de exposição vêm (número de caminhões, milhas por ano). **[não verificado]** |
| `jboysen/injured-workers`, "Severely Injured Workers" | Cerca de 22 mil relatos de lesões graves da OSHA (2015 a 2017), com descrição em texto e classificação OIICS | CC0; 3,4 MB; 4 notebooks | Narrativas de acidente com código de causa: base pública para a parte de texto (antiga Ideia 2), se voltar. |
| `trozan24/sif-augmentation-dataset-for-nlp`, "OSHA SIF Incident Narratives with AI-Augmented NLP" | Narrativas de incidentes graves (SIF) da OSHA, aumentadas com IA | MIT; 3,2 MB | Mesmo uso do anterior. Cuidado: parte do texto é gerada por IA. |

### Média: telemetria e comportamento de direção

| Dataset (Kaggle) | O que tem | Licença e tamanho | Uso possível |
| --- | --- | --- | --- |
| `vancharmlab/grabai`, "Grab Safe Driver Telematics" | Telemetria de celular (acelerômetro, giroscópio, velocidade) por viagem, com **rótulo de viagem perigosa**; veio de um desafio da Grab | Licença "Unknown"; 859 MB | Mais próximo de "eventos de condução → risco". O rótulo é condução perigosa, não acidente. Conferir a licença antes de usar. |
| `outofskills/driving-behavior`, "Driving Behavior" | Acelerômetro e giroscópio de celular, 2 amostras por segundo, classes normal, lenta e agressiva | CC BY 4.0; 0,2 MB; 50 notebooks | Pequeno e muito usado. Bom para entender como frenagem e curva bruscas são detectadas; não tem acidentes. |
| `shashwatwork/driving-behavior-dataset` | Similar ao anterior | CC BY 4.0; 7 MB | Idem. |
| `yunlevin/levin-vehicle-telematics` | Telemetria veicular (OBD) de muitas viagens | CC BY-NC-SA 4.0; 616 MB | Exposição e eventos; não comercial, ok para pesquisa. |
| `datasetengineer/driver-behavior-and-route-anomaly-dataset-dbra24` | 120 mil registros de viagem na Califórnia (jan/2023), 26 variáveis (velocidade, aceleração, direção, anomalias) | CC0; 16 MB; 0 notebooks | Provavelmente **sintético** (o autor publica muitos datasets gerados). Só para teste. |
| `shakilofficial0/large-scale-driver-behavior-sensor-dataset` | Sensores de comportamento de direção em grande escala | CC BY-NC-SA 4.0; 432 MB | Idem ao Levin. |

### Baixa: acidentes viários gerais

NYC Motor Vehicle Collisions (vários uploads, CC0, cerca de 80 MB), US DOT Large Truck and Bus Crash (`tobey1/bigtruckfatalities1975to2014`) e caminhões em acidentes fatais do FARS (`marvinbregiosa/us-truck-fatalities-fars-2018-2024`). São acidentes em vias públicas, sem exposição por veículo; servem só como contexto na introdução.

### Para a extensão opcional (previsão de volume)

`datasetengineer/logistics-and-supply-chain-dataset` (CC0, 7 MB) e `umuttuygurr/supply-chain-v2` (CC0, 1 MB, simulação de 365 dias). Ambos parecem sintéticos. A própria base `yogape` tem cargas diárias por três anos, com sazonalidade, e serve para testar a previsão probabilística de volume (objetivo f).

## 3. Fontes oficiais (fora do Kaggle) a considerar

- **OSHA, dados por estabelecimento (ITA):** https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data. É a fonte original do dataset `robikscube`, com anos mais recentes que 2021.
- **FMCSA, SMS e cadastro de transportadoras:** dados abertos do Departamento de Transportes dos EUA. É a fonte original do snapshot acima.

Ambas são dados oficiais e públicos, então são melhores para citar numa dissertação do que cópias no Kaggle. **[não verificado: conferir anos disponíveis e dicionário de dados]**

## 4. Próximos passos sugeridos

1. Baixar o OSHA ITA filtrado para armazenagem e transporte e rodar o plano alternativo (estabelecimento × ano, horas como offset). Seria a primeira **evidência real e pública** do método, utilizável no próprio pré-projeto como teste preliminar.
2. Ver os notebooks do `yogape` (precisa de login) e anotar aqui se algum modela incidentes.
3. Decidir se a telemetria pública (Grab) entra só como exemplo na fundamentação.
