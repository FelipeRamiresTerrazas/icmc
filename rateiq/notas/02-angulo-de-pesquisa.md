# 02. Ângulo de pesquisa do RateIQ (rascunho)

Criada em 2026-11-23. Primeiras ideias para transformar o RateIQ em dissertação; nada aqui está decidido. Referências ainda não levantadas: os temas da literatura estão no fim, sem entrada no `referencias.bib`.

## O que é pesquisa e o que é produto

A API, o app e a ingestão são entregas de engenharia da empresa e não sustentam uma dissertação. O que pode sustentar é o problema estatístico do motor de taxa:

> estimar salário e taxa por área pequena, função e turno, combinando dados públicos agregados em outra geografia com poucos dados internos, com incerteza calibrada, e escolher o preço sabendo que ele muda a chance de ganhar a proposta.

## Problemas estatísticos

1. **Estimação em áreas pequenas e mudança de suporte.** O OEWS publica salário por área metropolitana ou estado; o RateIQ precisa de ZIP3 × função. A passagem de condado ou área metropolitana para ZIP3 usa pesos de correspondência e propaga erro.
2. **Fusão de fontes com poucos dados internos.** A média ponderada do plano é um caso particular, com pesos fixos. Um modelo hierárquico com encolhimento aprende quanto confiar em cada fonte e em cada site, e quanto puxar sites com poucos dados para o nível de mercado.
3. **Incerteza calibrada.** A epic pede uma "faixa de confiança". A pergunta é se a faixa tem a cobertura que promete quando se deixa um site de fora. Candidatos: intervalos preditivos do modelo hierárquico e predição conformal.
4. **Preço e probabilidade de ganho (prescritivo).** Com as propostas ganhas e perdidas, modelar P(ganho | razão preço/mercado) e escolher a margem que maximiza a margem esperada. Dificuldades: poucas propostas, e só se observam as propostas que foram feitas (seleção).
5. **Defasagem temporal.** O OEWS sai com cerca de um ano de atraso; atualizar com séries mais rápidas (ECI, QCEW) é um problema de nowcasting. **[a conferir: defasagem exata de cada fonte]**

## Estrutura em três níveis (paralela à ideia 1)

| Nível | Conteúdo |
| :-- | :-- |
| Descritivo | Mapa do salário de mercado por ZIP3 e função; dispersão entre fontes; posição das taxas internas em relação ao mercado. |
| Preditivo | Salário e taxa por ZIP3 com intervalo; comparação da média ponderada, do modelo hierárquico e da linha de base manual, deixando um site de fora. |
| Prescritivo | Margem ou preço recomendado sob incerteza sobre a chance de ganho. |

## Hipóteses candidatas

- **H1.** Um modelo hierárquico com encolhimento tem erro absoluto médio menor, deixando um site de fora, que a média ponderada de pesos fixos e que a linha de base manual.
- **H2.** Os intervalos do modelo hierárquico (ou conformais) têm cobertura próxima da nominal deixando um site de fora; a faixa feita a olho da média ponderada, não.
- **H3.** A chance de ganho cai com a razão preço/mercado, e a margem que maximiza a margem esperada difere da margem alvo fixa. Só é testável se houver propostas fechadas suficientes.

## Pontos a favor

- **Dados públicos fortes.** BLS, BEA, Census e HUD são abertos. O método pode ser desenvolvido, mostrado e publicado inteiro com dados públicos (por exemplo, prevendo o salário de uma área metropolitana deixada de fora), e os dados internos entram só para calibrar e validar. Isso depende menos de autorização do que a ideia 1.
- **Ligação com o trabalho.** As epics já estão no planejamento de 2027 e têm patrocínio interno; o trabalho da dissertação e o do emprego andariam juntos.
- **Ênfase em ciência de dados** e encaixe provável na linha Modelagem de Risco (modelos hierárquicos, incerteza) ou em Pesquisa Operacional (precificação). **[a conferir no PDF de linhas]**

## Riscos

- **Amostra interna minúscula:** na ordem de dezenas de sites e dezenas de propostas ganhas. H3 pode ficar inviável, e H1 tem pouco poder; o estudo pode precisar se apoiar sobretudo na validação com dados públicos.
- **Dados sensíveis:** salário pago e taxa cobrada são informação comercial sensível. A autorização de 2026-11-15 foi dada para a pesquisa de risco: confirmar se cobre este tema ou pedir uma ampliação.
- **Fronteira com o produto:** o texto descreve o método, não o produto da empresa; conferir a questão de propriedade intelectual.
- **Dependência do cronograma da empresa:** o acesso ao pagamento interno está bloqueado, e o feed do CRM, parado.
- **Custo de troca:** a ideia 1 já tem pré-projeto, projeto curto da inscrição, estudo de viabilidade e rascunho de dissertação.

## Comparação rápida com a ideia 1 (risco de acidentes em pátio)

| Critério | Ideia 1: risco em pátio | Ideia 2: RateIQ |
| :-- | :-- | :-- |
| Maturidade | Pré-projeto pronto, viabilidade testada | Só a ideia e o plano da empresa |
| Dados internos | Ricos (relatos, telemetria, exposição) | Poucos (dezenas de sites e de propostas) |
| Dados públicos | Fracos (dataset simulado do Kaggle) | Fortes (BLS, BEA, Census) |
| Dependência de autorização | Alta | Média (o núcleo pode ser público) |
| Ligação com o trabalho | Média | Alta (epics de 2027) |

## Temas de literatura a levantar

Todos **[a conferir]**, sem entrada no `.bib` até a leitura na fonte:

- estimação em pequenas áreas (modelos de nível de área, como o de Fay e Herriot, e os livros-texto da área);
- interpolação entre geografias (mudança de suporte, correspondência ZIP ↔ condado);
- modelos hierárquicos bayesianos e encolhimento com poucos grupos;
- predição conformal e avaliação de cobertura;
- precificação de propostas com probabilidade de ganho (bid pricing);
- mercado de trabalho de motoristas de caminhão nos EUA (salários, escassez).

## Próximos passos

1. Decidir se o RateIQ substitui a ideia 1, vira o tema principal com a ideia 1 de plano B, ou fica só como projeto de trabalho.
2. Confirmar com a empresa o escopo da autorização para salários e taxas.
3. Ver na reunião de abertura (2026-12-02) o que a empresa espera do motor, quem define encargos e margem, e o calendário de acesso ao pagamento.
4. Se seguir: um protótipo só com dados públicos em `rateiq/analise/` (OEWS + RPP + correspondência ZIP3), para testar H1 e H2 deixando áreas metropolitanas de fora.
