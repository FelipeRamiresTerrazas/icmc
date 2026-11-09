# 06. Mapa da literatura

Pesquisa feita em 2026-11-08: ciência de dados e ML em logística, com foco em pátios de centros de distribuição dos EUA (spotting e shuttling de carretas com caminhões de manobra).

Foram cerca de 35 buscas na web, cobrindo:
- revisões de ML em logística;
- pátios, cross-docks e terminais;
- telemetria e risco em caminhões;
- segurança ocupacional em armazenagem;
- subnotificação.

As referências confirmadas em catálogo (RePEc, EconBiz, PubMed, DSpace do MIT, páginas das editoras) foram para o `referencias.bib`, **todas com `CONFERIR`**: título, ano e volume vieram de catálogos, e nada foi lido na íntegra. O que não deu para confirmar (autor ou veículo) ficou só na seção 7 deste arquivo, fora do `.bib`.

## 1. A principal conclusão: a lacuna existe

**Não encontrei literatura revisada por pares sobre operação ou segurança de pátios de centros de distribuição** (yard jockeys, spotting, shuttling de carretas entre docas e vagas). O que existe se divide em três grupos:

1. **Terminais de contêineres** (portos): muita pesquisa operacional (agendamento de caminhões de pátio, guindastes) e uma literatura crescente de ML, com previsão de tempo de permanência de contêiner e de tempo de giro de caminhão (`filom2022`, `chhetri2026`).
2. **Cross-docks e terminais de carga fracionada**: agendamento de caminhões nas docas e layout (`gue1999`, `boysen2010`, `vanbelle2012`). É o parente acadêmico mais próximo do pátio de um centro de distribuição, mas trata da doca, não da movimentação no pátio.
3. **Material de fornecedores e literatura cinzenta**:
   - guias de mercado de sistemas de gestão de pátio (Gartner, MWPVL), sem método;
   - patentes de caminhões de pátio autônomos;
   - relatórios de investigação de mortes (`wali2022`: motorista atropelado por caminhão de pátio).

Sobre segurança, a literatura de caminhões trata de **rodovia** (telemetria e eventos críticos em viagens longas). A de armazéns trata de **empilhadeiras**. O caminhão de manobra fica no meio, sem estudo próprio.

**Uso no pré-projeto:** isso sustenta a frase da introdução de que aplicações a operações de pátio são pouco exploradas, hoje marcada com `\preencher{}`. Antes de tirar a marca, vale repetir a busca em Scopus ou Web of Science (strings na seção 6), porque busca na web não substitui base bibliográfica.

## 2. Temas e referências no `.bib`

### 2.1 Revisões de ML e analytics em logística

| Chave | O que traz | Uso |
| --- | --- | --- |
| `akbari2021` | Revisão sistemática de ML em logística e cadeia de suprimentos (1994 a 2019, 110 artigos). Foco em previsão e otimização; detecção quase ausente. | Enquadrar o projeto: risco e detecção são pouco estudados. |
| `wang2016` | Big data analytics em logística: descritivo, preditivo e prescritivo; estratégia e operação. | Classificar o projeto (preditivo e operacional). |
| `nguyen2018` | Revisão de big data analytics em cadeia de suprimentos, com quadro de classificação. | Idem. |
| `baryannis2019` | IA aplicada à gestão de risco em cadeias de suprimentos. | Mostra que "risco" na literatura de supply chain é risco de ruptura, não de acidente: outra lacuna. |

### 2.2 Portos, terminais, centros de distribuição e pátios

| Chave | O que traz | Uso |
| --- | --- | --- |
| `filom2022` | Revisão sistemática de ML em operações portuárias (cerca de 70 artigos). Muito dado subutilizado, pouco uso em tempo real. | Referência central do "ML em pátio" que existe hoje (portuário). |
| `vanderspoel2017` | Previsão de horário de chegada de caminhões num **centro de distribuição europeu**, estudo de campo. | Um dos raros trabalhos de ML em CD com dado real. |
| `benjatanont2020` | Trabalho final do mestrado em Supply Chain do MIT: previsão do tempo de permanência de caminhões num operador logístico global (random forest e boosting). A instalação do embarcador é o fator mais forte. | Dwell time em instalações nos EUA, perto da extensão opcional. |
| `chhetri2026` | ML para tempo de permanência de contêiner (porto de Mombaça); modo de transporte é o principal preditor. | Exemplo de ML em dado operacional de pátio. |
| `dotoig2018` | Relatório do órgão de auditoria do Departamento de Transportes dos EUA: 15 minutos a mais de permanência média estão associados a 6,2% a mais de taxa de acidentes; os dados nacionais de detenção são ruins. | **Liga tempo no pátio a risco de acidente.** Bom para a introdução. |
| `gue1999` | Agendamento de carretas nas docas e layout de terminais de carga fracionada. | Base de pesquisa operacional de doca e pátio. |
| `boysen2010`, `vanbelle2012` | Revisões de agendamento de caminhões em cross-docks. | Contexto de pesquisa operacional; mostram o foco na doca. |
| `huynh2016` | Revisão de sistemas de agendamento de caminhões em terminais. | Contexto (portaria e pátio). |

### 2.3 Telemetria e risco em caminhões

| Chave | O que traz | Uso |
| --- | --- | --- |
| `cai2021` | Cerca de 31,8 mil motoristas de uma grande transportadora dos EUA. Eventos críticos (frenagem brusca, distância, mitigação de colisão, estabilidade) por 10 mil milhas associados a acidentes. **Binomial negativa bayesiana com milhas como exposição.** | **A referência mais próxima do método do projeto.** Mostra que telemetria prevê acidentes em rodovia; o projeto testa isso em pátio (H2). |
| `cai2022` | Processos pontuais hierárquicos bayesianos para eventos críticos recorrentes, com efeito aleatório de motorista. | Alternativa de modelagem (eventos no tempo, não contagens mensais). |
| `driessen2024` | 180 motoristas na Holanda, 2 anos: frenagens bruscas por hora preveem multas e **sinistros com dano**. | Evidência de que frenagem por hora prevê dano material, o desfecho mais comum em pátio. |
| `mehdizadeh2020` | Revisão de análise de dados em segurança viária: fontes, modelos de risco, lacuna entre previsão e otimização. | Ponte entre previsão de risco e decisão (objetivo f). |
| `nas2017` | Academias Nacionais dos EUA sobre a medição de segurança de transportadoras (escores do sistema de segurança da agência federal de transporte de carga e risco de acidente). | Debate sobre indicadores que não ajustam por exposição: motivação de H1. |

Já estavam no `.bib`: `lord2010`, `mannering2014` (modelos de frequência de acidentes) e `guo2013` (condução naturalística).

### 2.4 Segurança ocupacional em armazenagem e fatores de risco

| Chave | O que traz | Uso |
| --- | --- | --- |
| `sarkar2020` | Revisão de ML em análise de acidentes de trabalho (232 artigos). Domínios: desfecho, padrões, risco, gravidade. | Enquadra o projeto na literatura de ML em segurança do trabalho. |
| `collins1999` | Estudo caso-controle de lesões com empilhadeiras e outros veículos industriais motorizados (indústria automotiva). | O estudo epidemiológico clássico de veículos industriais motorizados. |
| `wali2022` | Investigação de morte: motorista atropelado por caminhão de pátio num terminal à noite, com pouca iluminação. | Caso concreto do risco estudado; mostra que o atropelamento de pedestre também conta. |
| `dembe2005` | Hora extra e jornadas longas aumentam o risco de lesão (61% a mais com hora extra), com relação dose-resposta. | **Covariável candidata:** horas extras por site e mês, já disponíveis na folha. |
| `breslin2006` | Trabalhadores no primeiro mês de emprego têm risco muito maior de lesão com afastamento. | **Covariável candidata:** fração de recém-contratados por site e mês. |
| `smith2010` | Trabalhadores temporários de agência têm taxa de lesão mais alta (estado de Washington). | Covariável candidata, se houver terceirizados. |

### 2.5 Subnotificação

| Chave | O que traz | Uso |
| --- | --- | --- |
| `leigh2004` | O levantamento oficial de lesões dos EUA deixaria de contar de 33% a 69% das lesões não fatais. | Motivação da etapa 4 (H3). |
| `rosenman2006` | Michigan: o sistema nacional deixou de fora de 61% a 68% dos casos, com captura e recaptura. | **Mesmo método da etapa 4.** |
| `boden2008` | Captura e recaptura em seis estados: subnotificação grande e muito variável entre estados. | Apoia H3: a taxa de relato varia entre unidades. |

Já estava no `.bib`: `iwgdmf1995` (captura e recaptura com múltiplas fontes).

## 3. Como isso muda o pré-projeto (sugestões, ainda não aplicadas)

1. **Introdução:**
   - trocar o `\preencher{conferir com busca bibliográfica sistemática}` por uma frase apoiada em `filom2022`, `akbari2021` e `vanbelle2012`: o ML em pátio é portuário e a pesquisa operacional em CD foca a doca;
   - citar `dotoig2018` para ligar o tempo no pátio ao risco.
2. **Fundamentação, telemetria:** `cai2021` e `driessen2024` são melhores que `guo2013` (motoristas de carro), porque tratam de **caminhões** e usam modelo de contagem com exposição.
3. **Metodologia, covariáveis:** acrescentar hora extra (`dembe2005`) e fração de recém-contratados (`breslin2006`) como covariáveis por site e mês, vindas das horas da folha. São baratas, têm literatura e funcionam também no plano alternativo.
4. **Subnotificação:** citar `rosenman2006` e `boden2008` junto de `iwgdmf1995`.

## 4. Datasets citados na literatura

O Cai e colaboradores usam dados de uma transportadora (não públicos). O dataset público mais próximo é o OSHA por estabelecimento (`notas/05-datasets-publicos.md`).

## 5. O que ler primeiro (ordem sugerida)

1. `cai2021`: método quase igual ao do projeto.
2. `filom2022`: mapa do ML em pátio portuário.
3. `lord2010`: modelos de frequência de acidentes.
4. `rosenman2006`: captura e recaptura aplicada a lesões.
5. `vanderspoel2017` e `benjatanont2020`: ML com dado real de CD e caminhões.

Salve os PDFs em `referencias/` com o nome da chave (`cai2021.pdf`).

## 6. Strings para repetir a busca em base bibliográfica (Scopus, Web of Science, Google Scholar)

- `("yard truck" OR "yard tractor" OR "terminal tractor" OR "yard jockey" OR "yard hostler" OR "shunt truck") AND (distribution OR warehouse)`
- `("trailer yard" OR "yard management") AND ("distribution center" OR warehouse)`
- `("safety-critical event*" OR "harsh braking") AND (truck* OR fleet) AND (crash* OR collision*)`
- `("powered industrial truck*" OR forklift*) AND injur* AND (warehous* OR "distribution center")`
- `(underreport* OR "capture-recapture") AND (occupational injur* OR "workplace injur*")`
- `("negative binomial" OR "hierarchical Bayesian") AND (occupational injur* OR "injury rate") AND (exposure OR "hours worked")`

## 7. Encontrados, mas fora do `.bib` (faltam dados)

- **"An empirical study of truck driver detention time"**, *International Journal of Physical Distribution & Logistics Management*, v. 55, n. 2, p. 154 (2025?). Regressão em 16.227 cargas de um grande produtor de hortifrúti dos EUA: frota própria tem menos detenção. **Faltam os autores.**
- **Babai et al. (2025)**, revisão de ML em gestão da cadeia de suprimentos, *IMA Journal of Management Mathematics*. Faltam título exato, volume e páginas.
- **Hill e Böse (2017)**, rede neural para tempo de espera de caminhões na portaria de um depósito de contêineres vazios na Alemanha. Faltam o veículo e os dados completos.
- **Van der Spoel et al. (2016)**, previsão do tempo de giro de caminhão em terminal com random forest e CART. Citado por outros, mas o veículo não foi encontrado.
- **Foley (2017)**, *American Journal of Industrial Medicine*, temporários versus permanentes. Volume não confirmado.
- **NIOSH (1997)**, incidentes com empilhadeiras e veículos industriais motorizados (916 incidentes); **DOL OIG (2023)**, auditoria de inspeções da OSHA em armazéns, que aponta veículos industriais motorizados como risco-chave. Ambos são literatura cinzenta.
- **Breslin et al. (2019)**, revisão sistemática "Are new workers at elevated risk for work injury?", *Occupational and Environmental Medicine* 76(9). Faltam as páginas.
- **ATRI (American Transportation Research Institute)**, estudos sobre escores de segurança das transportadoras e risco de acidente. Literatura cinzenta do setor.
