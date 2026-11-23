# Contexto do projeto: mestrado MECAI (ICMC-USP) do Felipe

Atualizado em 15/11/2026. Responda sempre em português brasileiro.

## 1. Quem sou e o que estou fazendo

Sou Felipe Ramires Terrazas, gestor de inteligência artificial e analytics numa empresa que presta serviços de operação de pátio (movimentação de carretas entre vagas, docas e portarias com caminhões de manobra) em dezenas de unidades. Sou o responsável pela área de dados e já trabalho com as fontes descritas abaixo.

Estou preparando a candidatura ao **Mestrado Profissional MECAI** (Matemática, Estatística e Computação Aplicadas à Indústria) do ICMC-USP, em São Carlos, com **ênfase em Ciência de Dados** e na linha **Modelagem de Risco**. A seleção prevista é a de 2027. Tenho dois documentos em andamento:

1. **Pré-projeto**: documento da inscrição. Está bem avançado.
2. **Rascunho da dissertação**: trabalho adiantado e separado. Nada dele entra no pré-projeto sem que eu peça.

Os dois ficam num repositório git privado, em LaTeX, que edito com o Claude Code. Este projeto do Claude Desktop serve para discutir ideias, estatística, literatura e redação. Você não tem acesso ao repositório nem aos dados: trabalhe com o que eu colar ou anexar.

## 2. Tema

**Título:** Risco de acidentes em operações de pátio: modelos hierárquicos de contagem com exposição e telemetria veicular.
**Em inglês:** Accident risk in yard operations: hierarchical count models with exposure and vehicle telematics.

**Problema.** A empresa compara unidades por contagem bruta de acidentes, um indicador fraco por quatro motivos:
- a exposição varia muito;
- com eventos raros, o acaso pesa muito;
- o tipo de operação muda o risco;
- nem todo acidente é relatado, e a propensão a relatar varia entre unidades.

**Lacuna.** A literatura de modelos de contagem com exposição é rodoviária. No pátio, o aprendizado de máquina aparece em terminais portuários, a pesquisa operacional estuda o agendamento de docas e a segurança em armazéns trata de empilhadeiras. Numa busca preliminar, não achei estudo revisado por pares sobre o risco de acidentes de caminhões de manobra. Isso ainda precisa ser confirmado com uma busca sistemática em Scopus e Web of Science.

## 3. Objetivos

**Geral:** desenvolver e avaliar modelos estatísticos para estimar o risco de acidentes em operações de pátio, ajustado pela exposição e com incerteza quantificada, por veículo e por unidade, combinando relatos de acidentes, telemetria veicular e horas trabalhadas.

**Específicos:**
- (a) Integrar as fontes num painel veículo × mês, com regras de ligação documentadas e qualidade medida em amostra revisada à mão.
- (b) Comparar modelos de contagem: Poisson, binomial negativa, com e sem inflação de zeros, com e sem efeitos aleatórios de veículo e unidade. A comparação considera ajuste e previsão fora da amostra.
- (c) Medir quanto os eventos de condução da telemetria acrescentam à previsão de acidentes, além da exposição, do tipo de uso e da unidade. Se nada acrescentarem, verificar se o efeito pode ser declarado desprezível (teste de equivalência).
- (d) Estimar a subnotificação comparando os relatos formais com as ordens de manutenção abertas por dano, e medir a cobertura da detecção automática de colisão da telemetria.
- (e) Produzir indicadores de risco por unidade, ajustados por exposição, com intervalos e grupos de risco, e compará-los à contagem bruta.
- (f) **Extensão opcional:** previsão probabilística das horas de operação por unidade para planejar escala e supervisão. A projeção de acidentes esperados fica só em nível agregado (região e trimestre).

## 4. Hipóteses

- **H1, comparação entre unidades.**
  - (a) A taxa do modelo hierárquico prevê a taxa do semestre seguinte com erro menor que a taxa bruta.
  - (b) As taxas diferem entre unidades, dada a exposição.
  - (c) Equivalência: a correlação de postos entre a taxa estimada e o tamanho da unidade está dentro de (-0,3; 0,3).
- **H2, telemetria.**
  - (a) Para cada tipo de evento, a razão de taxas por desvio padrão difere de 1, e o escore logarítmico fora da amostra melhora com a telemetria. Correção de Holm.
  - (b) Equivalência: a razão de taxas está dentro de [0,8; 1,25], ou seja, o efeito é desprezível.
- **H3, subnotificação.**
  - (a) A probabilidade de um dano registrado pela manutenção ter relato formal é menor que 1.
  - (b) Essa probabilidade varia entre unidades.

As afirmações de ausência de efeito usam testes de equivalência (TOST: Schuirmann 1987, Lakens 2017). As margens devem ser fixadas antes da análise final, de preferência com pré-registro no OSF.

## 5. Método

**Modelo principal:** binomial negativa hierárquica.

Y_it ~ NB(mu_it, phi), com log mu_it = log E_it + x_it'beta + gamma_t + u_s(i,t) + v_i, em que u_s ~ N(0, sigma_u²) e v_i ~ N(0, sigma_v²).

- Y_it é o número de acidentes do veículo i no mês t.
- E_it é a exposição: **horas de viagem** na análise principal e distância como sensibilidade.
- x_it reúne as taxas de eventos de condução e o **tipo de uso do veículo**, que é obrigatório: manobra no pátio (spotter), transferência entre instalações (shuttle) ou uso local.
- gamma_t é o efeito de calendário, u_s o efeito de unidade e v_i o efeito de veículo, que é obrigatório.

**Etapas:**
1. Integração e painel.
2. Modelos de risco.
3. Validação fora da amostra, temporal e deixando uma unidade de fora, com escore logarítmico, calibração (Gneiting, Czado), gráficos de funil e grupos de risco em vez de ranking.
4. Subnotificação, com modelo logístico hierárquico da probabilidade de relato e captura e recaptura com duas fontes. Como a dependência entre as fontes deve ser positiva, o total é apresentado como limite inferior.

**Covariáveis secundárias por unidade e mês:** horas extras (Dembe 2005) e fração de recém-contratados (Breslin 2006).

**Plano alternativo:** se a telemetria ficar restrita, o modelo passa para unidade × mês, com as horas da folha como exposição. H1 e H3 continuam testáveis, e H2 deixa de existir.

**Ferramentas:**
- SQL dentro do ambiente da empresa, só com agregados.
- Python para extração, preparação, bootstrap, previsão e figuras.
- R para modelos mistos: glmmTMB e diagnóstico com DHARMa (resíduos quantílicos).
- Figuras em matplotlib, exportadas em PDF, com fonte serifada, 6,3 polegadas de largura, rótulos em português e vírgula decimal.
- Toda tabela e figura é gerada por script.

## 6. Dados (só ordens de grandeza)

| Fonte | Conteúdo | Escala |
| --- | --- | --- |
| Relatos de acidentes (app próprio) | data, hora, tipo, unidade, veículo, gravidade, descrição | centenas de relatos em pouco mais de um ano |
| Telemetria veicular | viagens, eventos de condução, colisões detectadas | cerca de 300 veículos, mais de um milhão de viagens |
| Horas trabalhadas (folha) | horas por unidade e mês | dezenas de unidades |
| Manutenção | ordens de reparo por veículo, com motivo | centenas de ordens por dano |

Problemas conhecidos nos dados:
- relatos de teste misturados aos reais na implantação do app;
- unidade e veículo digitados em texto livre;
- viagens com fim inválido;
- veículos que mudam de unidade;
- a sincronização da telemetria está pausada e precisa ser retomada.

**Privacidade:** nenhum dado identifica pessoas. Não uso motorista, nome, câmera nem GPS, e só agregados saem do ambiente da empresa.

## 7. O que os estudos preliminares já mostraram

**Simulação calibrada em dados públicos.** A estrutura vem do Logistics Operations Database do Kaggle (yogape2025), com acidentes simulados. Os incidentes desse dataset são aleatórios e não servem como desfecho. O enquadramento correto é sempre "simulação calibrada em dados públicos", nunca "testamos a ideia com os dados do Kaggle". Resultados:
- Poder para um efeito moderado de telemetria (beta = 0,15): 0,75 com cerca de 300 acidentes, 0,89 com 600 e 0,17 com 70.
- Sem o efeito de veículo, a taxa de falso positivo chegou a 15%, três vezes o nominal.
- Correlação de postos com o risco verdadeiro das unidades: 0,30 para a contagem bruta, 0,51 para a taxa bruta e 0,54 para o Bayes empírico.
- O erro da probabilidade de relato por unidade caiu de 0,23 para 0,11 com encolhimento.
- A incerteza da exposição responde por cerca de 1% da variância dos acidentes mensais por unidade.

**Exploração agregada dos dados reais.** Doze meses, algumas centenas de acidentes, cerca de duas mil combinações veículo-mês e unidades mascaradas. Fora do repositório, só valores relativos:
- **Exposição:** por milha, o spotter tem taxa mais de 20 vezes a do veículo local; por hora, cerca de 3 vezes. Por isso a exposição principal passou a ser o tempo.
- **H1:** as taxas variam entre unidades além do acaso, com cerca de um sexto fora do funil de 95%. O Bayes empírico prevê melhor o semestre seguinte, e a contagem bruta acompanha o tamanho da unidade (correlação de cerca de 0,8). O ranking é instável entre semestres.
- **H2:** associações aparentes no bruto somem com o ajuste pelo tipo de uso e pelo efeito de veículo. Nenhum dos dez eventos passou após Holm, e sete foram declarados desprezíveis. Três ficaram inconclusivos: frenagem brusca, excesso grave de velocidade e parada incompleta.
- **H3:** a detecção automática de colisão quase não capta acidente de pátio. Menos de 10% dos relatos têm detecção, e mais de 80% das detecções são falso alarme. Por isso a segunda fonte passou a ser a manutenção.
- **Modelo:** o efeito de veículo foi significativo, sem superdispersão residual nem excesso de zeros. Isso sustenta a binomial negativa sem inflação de zeros.
- **Extensão (f):** horas semanais previstas com erro de cerca de 6% em oito semanas.

## 8. Decisões já tomadas (não reabrir sem motivo novo)

1. O desfecho principal é o conjunto de todas as colisões relatadas, com ou sem lesão. Lesões e quase-acidentes entram como sensibilidade.
2. O efeito aleatório de veículo é obrigatório.
3. O tipo de uso é ajuste obrigatório, e a exposição principal é o tempo de viagem.
4. A segunda fonte da subnotificação é a manutenção, não a detecção automática.
5. A extensão (f) serve para planejar escala, com projeção de acidentes só agregada.
6. Os resultados por unidade são comunicados com intervalos, funil e grupos, nunca com ranking exato.

## 9. Ideias em avaliação

- **Carga de trabalho por turno (possível H4 ou parte da extensão f).** Com movimentos e motorista-horas por unidade, dia e turno, testar se turnos de alta intensidade têm mais acidentes por motorista-hora.
  - Modelo: Poisson ou binomial negativa com motorista-horas como offset, e intensidade medida como desvio em relação à própria unidade e turno.
  - Cuidados: causalidade reversa (usar intensidade anterior ao acidente ou a prevista) e poder baixo.
  - Os relatos têm hora preenchida na grande maioria.
  - Ainda não decidi se entra no pré-projeto.
- **Pontuação de auditorias de segurança por unidade** como medida de clima de segurança, covariável de H1 e principalmente de H3b (Probst). A série começa tarde (2026).
- **Ordens de manutenção.** Falta confirmar a ligação da ordem com o veículo e com a unidade. Também falta confirmar se o motivo "acidente" é atribuído só depois do relato, o que tornaria as fontes dependentes por construção, e houve uma mudança de regime no preenchimento no fim de 2025.

## 10. Plano de artigos

1. **Medir e comparar o risco entre unidades (H1).** Candidatas: Journal of Safety Research, Safety Science, Accident Analysis & Prevention. Submissão ao fim do 2º ano.
2. **Telemetria de estrada aplicada ao pátio, mais subnotificação (H2, H3).** Candidatas: Accident Analysis & Prevention, Traffic Injury Prevention, TRR/TRB. Submissão no 3º ano, com pré-registro.
3. **Opcional:** estudo de simulação em congresso (SBPO, ANPET). É totalmente reproduzível e pode sair primeiro.

Também existe um possível artigo de escala por turno, ligando a previsão probabilística de movimentos à decisão de escala.

As revistas não foram conferidas. Publicar exige autorização da empresa com cláusula de anonimização.

## 11. Estrutura dos documentos

**Pré-projeto (LaTeX, bilíngue):**
0. Resumo
1. Introdução e justificativa
2. Objetivos e hipóteses
3. Fundamentação
4. Dados
5. Metodologia, que inclui a 5.8, Estudo preliminar de viabilidade: simulação e exploração dos dados reais, com as figuras fig_poder e fig_real
6. Resultados esperados
7. Viabilidade e ética
8. Cronograma de 6 semestres

**Rascunho da dissertação:**
1. Introdução
2. Fundamentação
3. Dados
4. Métodos
5. Viabilidade (pronto)
6. Resultados (esqueleto, depende dos dados completos e da autorização)
7. Conclusão (provisória)

Os capítulos 3, 4, 6 e 7 têm várias pendências marcadas.

## 12. Programa MECAI (resumo; o edital prevalece sobre a FAQ)

- Prazo de depósito de 36 meses, sem exame de qualificação. Gratuito e sem bolsas.
- 96 créditos: 48 em disciplinas e 48 na dissertação. São obrigatórios 18 créditos entre MAI5001, MAI5002 e MAI5003, que têm 10 créditos cada.
- Proficiência em inglês em até 18 meses.
- Aulas preferencialmente às sextas, em São Carlos. É possível cursar disciplinas como aluno especial antes do ingresso e aproveitá-las depois.
- O projeto é de autoria do candidato, sem orientador na inscrição: a coordenação define a orientação depois.
- Disciplinas mais relevantes: MAI5003 (Probabilidade e Estatística), MAI5014 (Metodologia), MAI5036 e MAI5035. Não há disciplina de GLM, modelos mistos ou inferência bayesiana no programa.
- Ainda não li o edital, que define limite de páginas, formato e norma de referências.

## 13. Regras de escrita (valem para qualquer texto que você propuser)

- **Sem travessão (—).**
- **Nunca inventar referência.** Cite só o que eu confirmar. Se você não leu o estudo na fonte, escreva de forma geral e marque [conferir]. Entradas novas no .bib levam `note = {CONFERIR}`.
- **Não nomear a empresa, clientes nem unidades,** e usar só ordens de grandeza dos dados, até a autorização formal, que só será pedida depois da aprovação. Não me peça números internos exatos.
- **O pré-projeto não cita nem se dirige a nenhum docente.**
- **Bilíngue.** No LaTeX, cada parágrafo fica em `\pt{...}` seguido de `\en{...}`, e trechos curtos em `\tr{pt}{en}`. Eu edito o português. Quando eu pedir "sincroniza o inglês", traduza os trechos alterados.
- Pendências visíveis no texto: `\preencher{...}`.
- Estilo: frases diretas, termos estatísticos precisos, sem exagero de promessa. Associação não é causalidade: coeficientes de telemetria são associações.

## 14. Referências centrais (chaves do .bib)

- **Modelos de contagem e acidentes:** lord2010, lord2005, mannering2014, cameron2013, lambert1992.
- **Hierárquico e Bayes empírico:** gelman2007, clayton1987, hauer1997, goldstein1996, spiegelhalter2005 (funil), brooks2017 (glmmTMB), burkner2017 (brms), dunn1996.
- **Telemetria:** cai2021 (a mais próxima do método: binomial negativa com milhas como exposição, caminhões), driessen2024, guo2013.
- **Subnotificação:** leigh2004, rosenman2006, boden2008, iwgdmf1995, hook1995, fellegi1969, probst2010.
- **Segurança ocupacional:** dembe2005, breslin2006, collins1999.
- **Pátio e logística:** filom2022, vanbelle2012, dotoig2018.
- **Avaliação e testes:** gneiting2007, czado2009, diebold1995, hyndman2021, schuirmann1987, lakens2017, holm1979.

Quase todas as entradas ainda estão marcadas CONFERIR, porque nada foi lido na íntegra.

## 15. Pendências abertas

- Ler o edital: páginas, formato, norma, ênfase de 2027 e documentos de comprovação profissional.
- Busca sistemática em Scopus e Web of Science para confirmar a lacuna.
- Confirmar se é preciso comitê de ética para dados secundários agregados.
- Validar a manutenção como segunda fonte (ligação e independência).
- Decidir se H4 (carga por turno) entra no pré-projeto.
- Fixar e registrar as margens de equivalência antes da análise final.
- Perguntas à secretaria: aproveitamento de disciplinas, exigência de artigo no depósito, oferta por semestre.
