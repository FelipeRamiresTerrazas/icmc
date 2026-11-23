# 08. Conclusões preliminares com os dados reais (exploração de viabilidade)

Nota **interna** (mesmo cuidado de `01` a `03`). Rodada em 2026-11-11, com autorização do Felipe para explorar os dados reais com sites mascarados. Nada daqui vai para o pré-projeto ou outro texto externo sem revisão; lá, só ordens de grandeza.

**Como foi feito.**

- Consultas só de leitura e só agregadas, pelo usuário de serviço, em `analise/real/extrair.py`. O menor grão salvo é veículo × mês, sem nome, ID de pessoa, texto livre nem GPS.
- Análise em `analise/real/explorar.py`. A saída completa fica em `resultados/real/resumo.txt`, fora do git.
- Sites mascarados como Site 01, 02... pela ordem de milhas totais.
- O código do app do Streamlit (THESIS_RISK_EXPLORER) não pôde ser lido, porque exige OWNERSHIP. Os números abaixo vêm de consultas próprias e não foram conferidos contra as telas do app.

**Janela.**

- Out/2025 a set/2026: 12 meses completos em que Samsara e YardSafe se sobrepõem. A Samsara está congelada desde 13/10/2026.
- Exposição: viagens válidas (fim depois do início, no máximo 24 h).
- Desfecho: relatos com `incident_type = accident_incident`, ligados ao veículo pelo número do caminhão normalizado.

## Resumo em uma linha por hipótese

| Tema | Conclusão preliminar | Consequência para o projeto |
| :-- | :-- | :-- |
| Tamanho da amostra | 285 acidentes ligados à exposição em 1.965 veículo-meses; só 37 com sinistro de seguro | O desfecho tem de ser **todos os acidentes relatados**. Estamos perto do limiar de cerca de 300 da simulação; mais meses de dados ajudam |
| Exposição | **Horas** de viagem, e não milhas: por milha o spotter tem taxa 27 vezes maior que o caminhão local; por hora, cerca de 3 vezes | Trocar a exposição principal para horas, com milhas como sensibilidade. O tipo de uso entra como covariável obrigatória |
| H1 (sites) | As taxas variam entre sites além do acaso, mas o ranking entre semestres quase não se mantém. O Bayes empírico é o que melhor prevê a taxa do semestre seguinte | Confirma a simulação: comunicar com funil e encolhimento, nunca com ranking bruto |
| H2 (telemetria) | Associações fortes no bruto **somem quando se ajusta pelo tipo de uso**. Só excesso grave de velocidade fica associado, e fraco. A telemetria não melhora a previsão fora da amostra | H2 continua testável, mas o resultado esperado pode ser nulo. Confundimento pelo tipo de operação é o ponto central |
| H3 (subnotificação) | A detecção de colisão da Samsara **não enxerga acidente de pátio**: só 7% dos relatos têm alguma detecção em até 2 dias, e 83% das detecções são descartadas na revisão | Captura e recaptura com Samsara × YardSafe **não é viável**. É preciso outra segunda fonte ou reformular H3 |
| Extensão (f) | A previsão das horas semanais (ADP) tem erro de cerca de 6% em 8 semanas | (f) é viável e simples |

## 1. Relatos e ligação

- **Relatos de acidente:** 562 no YardSafe, com incidente entre set/2025 e nov/2026. Desses, 146 estão com status `pending`. Em mar a mai/2026, os pendentes são maioria (14 a 30 por mês, contra 15 a 17 revisados).
- **Hipótese de testes não confirmada.** Os pendentes não parecem ser os ~130 relatos de teste da página de soft launch: somando pendentes e revisados, mar a mai/2026 fica no mesmo nível dos outros meses (31 a 46 por mês). A hipótese mais provável é que sejam relatos reais ainda não revisados **[não verificado; confirmar com quem revisa]**.
- **Sensibilidade:** só com os revisados, o painel cai de 285 para 202 acidentes.
- **Funil de ligação** (581 relatos de acidente):
  - 72% casam com um veículo da Samsara pelo número do caminhão;
  - 57% caem num veículo com tag de site.
- **Veículos sem site.** 34% dos veículo-meses não têm site: são, na maioria, caminhões só com a tag da oficina central, que circulam entre sites.
- **Concordância de site.** O site do próprio relato coincide com o site da tag em 94 de 192 relatos que têm código (49%). Isso diverge do inventário, que achou pureza alta. Pode vir dos caminhões da oficina ou de códigos em outro formato (há 16 relatos com código numérico de 2 dígitos) **[a investigar]**.
- **Sites com exposição desprezível.** Alguns têm acidente e quase nenhuma hora; um deles tem 2 acidentes em 40 horas. Sugere tag errada ou caminhão emprestado. É preciso uma regra de atribuição de site por período, e não só pela tag atual.

## 2. Painel veículo × mês

- 277 veículos, 12 meses, 1.965 veículo-meses, 4,2 milhões de milhas e 248 mil horas de viagem.
- **Crescimento da frota:** a frota com viagem passou de 122 (out/2025) para 246 (set/2026). Ajustar por exposição é indispensável.
- **Distribuição dos acidentes:**
  - 88,5% dos veículo-meses têm zero acidente;
  - por veículo-mês, a média é 0,145 e a variância 0,205 (razão de 1,4, sobredispersão moderada);
  - por número de acidentes no mês: 0 em 1.740 veículo-meses, 1 em 181, 2 em 31, 3 em 10 e 4 em 3.
- **Concentração:** 43% dos veículos tiveram pelo menos um acidente no ano, e os 10% piores concentram 53% dos acidentes. Isso é argumento para o efeito aleatório de veículo.
- **Taxa por tipo de uso,** por 1.000 horas de viagem: spot 1,64; shuttle 0,62; local 0,51.
- **Taxa por milha:** spot 3,58, local 0,13 e shuttle 0,33 por 10 mil milhas. O spotter anda pouco e manobra muito, por isso milha não serve como exposição comparável.
- **Desfechos alternativos:**
  - só revisados: 202 acidentes;
  - só com sinistro de seguro: 37. São poucos para modelar; servem só como análise de sensibilidade descritiva.

## 3. H1: sites

Base: 50 sites com tag; taxa média de 1,43 acidente por 1.000 horas de viagem.

- **Gráfico de funil:**
  - 9 sites ficam fora do limite de 95%, onde o acaso explicaria cerca de 2 ou 3;
  - 3 ficam fora do limite de 99,8%: dois acima (Site 17 e Site 24) e um abaixo (Site 01, o maior).
  - Há variação real entre sites.
- **Bayes empírico:** o peso médio do próprio site é 0,49. Metade dos sites tem pouca exposição e quase toda a estimativa vem da média.
- **Estabilidade entre semestres** (out a mar vs abr a set; 32 sites com pelo menos 50 horas em cada metade):
  - correlação de Spearman entre o indicador do 1º semestre e a taxa do 2º: contagem 0,10, taxa bruta 0,20, taxa EB 0,11. Nenhuma é significativa;
  - erro médio ponderado ao prever a taxa do 2º semestre: taxa EB 0,68, média geral 0,81, taxa bruta 0,90.
  - O EB é o melhor preditor, como na simulação, mas a ordenação dos sites é instável. Os pendentes concentrados no 1º semestre de 2026 e o crescimento da frota contribuem para isso.
- **Duas medidas de exposição:** horas do ADP e horas de viagem da Samsara por site.
  - No total do ano por site, concordam bem: Spearman 0,86.
  - Mês a mês, menos: Spearman 0,59. As horas do ADP são cerca de 2,7 vezes as horas de viagem, porque incluem tempo parado, espera e outras funções.

## 4. H2: telemetria

Modelo: NB2 com offset log(horas). Erro padrão robusto por veículo, em vez do efeito aleatório. Covariável: log(1 + eventos mantidos após revisão por 1.000 milhas), padronizada.

- **Revisão humana:** frenagem brusca (73%) e curva brusca (80%) são quase todas descartadas. Sem cinto, velocidade, distância de seguimento e celular quase não são descartados (13% a 19%).
- **Ajuste só pela exposição:** frenagem, curva brusca e sem cinto aparecem fortemente associados (IRR de 1,6 a 1,8 por desvio padrão), e distância de seguimento aparece "protetora" (0,36).
- **Ajustando pelo tipo de uso** (spot, shuttle, local):
  - tudo isso desaparece (IRR entre 0,95 e 1,05, sem significância);
  - sobra excesso grave de velocidade, IRR 1,14 (1,06 a 1,23) no mesmo mês e 1,16 no mês seguinte;
  - parada sem parar fica fraca no mês seguinte (IRR 1,17; p 0,02);
  - com dez rótulos testados, parte disso pode ser acaso.
- **Fora da amostra** (ajuste em 8 meses, teste nos últimos 4; escore logarítmico médio, maior é melhor):
  - só exposição: −0,441;
  - exposição + uso: −0,426;
  - exposição + uso + telemetria: −0,434.
  - O tipo de uso ajuda e a telemetria não acrescenta.
- **Leitura.** O tipo de operação manda: o spotter tem muitos eventos de manobra e muitos acidentes. A pergunta certa é se o comportamento explica diferenças entre caminhões **do mesmo tipo**. Por ora, a resposta preliminar é "pouco ou nada".
- **Ainda não testado:**
  - efeito aleatório de veículo de verdade (glmmTMB ou brms);
  - interação rótulo × tipo de uso;
  - eventos por hora em vez de por milha;
  - G-force máxima.
  - É resultado de pesquisa válido mesmo se der nulo, mas muda o tom de H2 no pré-projeto.

## 5. H3: subnotificação

Detecções de colisão (rótulo `Crash`) de out/2025 a 13/10/2026: 358.

- **Revisão:** 293 descartadas e 65 mantidas.
- **Relatos de acidente** de caminhões com Samsara: 393. Desses, 10 têm uma colisão mantida em até 2 dias no mesmo veículo e 16 só uma descartada. **93% dos relatos não têm nenhuma detecção.**
- **Colisões mantidas:** só 9 das 65 têm relato correspondente.
- **Lincoln-Petersen (Chapman):** daria cerca de 2.600 acidentes "verdadeiros" contra 393 relatados. O número é **inválido**, porque as duas fontes não capturam o mesmo tipo de evento. O sensor de impacto foi feito para colisão em velocidade de estrada, e o acidente de pátio típico é de baixa velocidade: porta, engate, ré, pé de apoio, objeto fixo.
- **Para manter H3, há três caminhos:**
  - (a) trocar a segunda fonte por algo que capture o mesmo universo: ordens de oficina por dano (manutenção), sinistros de seguro ou registros do Yard Commander;
  - (b) restringir H3 a acidentes de estrada (shuttle e OTR), onde a detecção faz sentido, mas aí sobram poucos casos;
  - (c) transformar H3 numa medição da cobertura da telemetria como fonte, o que já é um achado.
  - **Decisão do Felipe.**

## 6. Extensão (f): previsão das horas

- **Série:** horas semanais do ADP (total), de jun/2025 a out/2026, 71 semanas. As horas quase triplicaram no período (razão de 2,8 entre as últimas e as primeiras 8 semanas).
- **Teste nas últimas 8 semanas** (erro percentual absoluto médio):
  - média das 8 anteriores: 15,5%;
  - última semana: 9,7%;
  - ETS no log com tendência amortecida: 5,9%, com cobertura de 75% no intervalo de 80%.
- Viável. A versão por site ainda não foi testada.

## 7. O que muda no pré-projeto (proposta, não aplicada)

1. **Exposição:** horas como medida principal, com o tipo de uso do caminhão como covariável obrigatória.
2. **H2:** dizer que o confundimento pelo tipo de operação é o principal desafio e que se espera efeito pequeno dentro do mesmo tipo de caminhão.
3. **H3:** reescrever conforme a decisão da seção 5. A captura e recaptura com detecção da telemetria não se sustenta.
4. **Dados (seção 4):** em ordem de grandeza, "algumas centenas de acidentes relatados por ano em uma frota de algumas centenas de caminhões, cerca de dois terços ligáveis à telemetria". Sem números exatos e sem nome.
5. **Riscos:** acrescentar a regra de atribuição de site por período e a fila de relatos pendentes de revisão.

## Pendências

- Confirmar o que são os 146 relatos pendentes.
- Investigar a concordância de site de 49%.
- Rodar o modelo com efeito aleatório de veículo (R, glmmTMB).
- Conferir estes números contra as telas do app do Streamlit.

## 8. Testes formais e aplicação no pré-projeto (2026-11-11, mesma data)

Hipóteses reescritas com H0 de igualdade e, para afirmações de ausência de efeito, teste de equivalência (TOST). Scripts:

- `analise/real/testes.py`: H1, H2 preditivo, H3 e o painel para o R.
- `r/h2_misto.R`: glmmTMB NB2 com efeito aleatório de veículo, Holm e TOST; diagnóstico com DHARMa.
- `analise/real/figuras.py`: gera `fig_real.pdf` e `fig_real_en.pdf`, só com valores relativos.

Mudança em relação às seções 4 e 5: os eventos de telemetria agora são **por 100 horas de viagem**, e não por 1.000 milhas, para ficar coerente com a exposição. Por isso as razões de taxas "brutas" diferem das da seção 5.

| Teste | Resultado |
| :-- | :-- |
| H1a: erro EB = erro bruta | Ganho do EB de 0,21 acidente por 1.000 h (IC 95% 0,04 a 0,44); p = 0,016, bootstrap em 31 sites. **Rejeita H0** |
| H1b: taxas iguais entre sites | Qui-quadrado/gl = 2,35, p < 0,001; 16% dos sites fora do limite de 95% (esperado 5%; p = 0,005). **Rejeita H0** |
| H1c: \|rho(taxa, exposição)\| ≥ 0,3 | Contagem bruta: rho = 0,83 (IC 90% 0,73 a 0,90), não equivalente. Taxa EB: rho = 0,03 (IC 90% −0,22 a 0,27). **Equivalente a zero** (43 sites com ≥ 50 h) |
| H2a: IRR = 1 por rótulo (modelo misto, Holm) | Nenhum rótulo rejeita H0 depois do ajuste. Sem ajuste, seguir de perto (0,71) e distração (0,78) rejeitam: confundimento pelo uso |
| H2a: escore com = sem telemetria | Diferença de −6,4 × 10⁻³ (IC −12,7 a −0,9); p = 0,019. **A telemetria piora** o escore fora da amostra |
| H2b: IRR fora de [0,8; 1,25] | 7 de 10 rótulos equivalentes a nulo. Inconclusivos: frenagem (IC 90% 0,98 a 1,22, quase dentro), excesso grave (0,99 a 1,27) e parada incompleta (0,96 a 1,32) |
| Modelo base | Desvio padrão do efeito de veículo 0,51 (TRV p = 0,004). DHARMa: dispersão p = 0,40, zeros p = 0,52, KS p = 0,72. Uso local IRR 0,31 e shuttle 0,39 em relação ao spot |
| H3 (cobertura da telemetria) | 7,3% dos relatos têm detecção em ±2 dias (IC 4,9% a 10,8%). Igual entre usos: spot 7,3%, shuttle 7,1%, local 7,9%; qui-quadrado p = 0,99. 82% das detecções foram descartadas |

**H3 reformulada.** A segunda fonte passa a ser a manutenção (`EDW_PROD_100460`, tabela `FCT_AMORDERSEC`, campo `REPREASON`). Os motivos `DAMAGE` (cerca de 900 ordens) e `ACC-REPORTED` (cerca de 150) são candidatos. Ainda falta verificar:

- como a ordem liga ao veículo (a tabela de ordens tem `ORDERID`; a unidade deve estar no cabeçalho da ordem);
- o período coberto;
- se "ACC-REPORTED" significa que o acidente foi relatado; nesse caso, as fontes não seriam independentes.

Também há uma tabela de acidentes do TMW (`REF_TSACCIDENT`), mas ela tem só 1 linha.

**Aplicado no pré-projeto:**

- seção 2: objetivos (c) e (d) e hipóteses H1 a H3 com H0 e equivalência;
- seção 5:
  - exposição em horas e tipo de uso obrigatório;
  - nova subseção "Testes das hipóteses";
  - Etapa 4 reescrita com a manutenção;
  - estudo preliminar dividido em 5.9.1 (simulação) e 5.9.2 (dados da operação, com a Figura 2);
- resumo, introdução (fonte de manutenção), tabela de dados, resultados esperados e riscos (pendentes de revisão, oficina central, Samsara parada).

Referências novas, todas com `CONFERIR`: schuirmann1987, lakens2017, holm1979 e diebold1995.
