# 01. Origem e escopo do RateIQ

Criada em 2026-11-23 a partir das três epics do Jira (DA-489, DA-490 e DA-491) e das nove issues filhas (DA-492 a DA-500), todas em Backlog. Sem nome da empresa, de pessoas, clientes ou unidades; volumes internos só em ordem de grandeza.

## O que é

Ferramenta de recomendação de taxa de motoristas, proposta internamente em 2026-11-13. Entrada: ZIP de 3 dígitos (ZIP3), função e turno. Saída: dois números, com os componentes (fonte, peso, data, faixa de confiança):

- o **salário esperado** do motorista (custo);
- a **taxa por hora a cobrar** do cliente (bill rate).

Motivo: hoje cada proposta pesquisa a taxa à mão, em parte com uma ferramenta comercial em piloto. A meta é uma consulta rápida, repetível e explicável.

## Cadeia de cálculo planejada (versão 1, transparente)

```
taxa = salário de mercado (média ponderada de fontes)
       × ajuste de custo de vida (paridade regional de preços)
       × encargos sobre a folha (impostos do empregador, benefícios, seguro)
       × fator horas pagas / horas faturáveis
       ÷ (1 − margem alvo)
```

Calibrada contra as taxas faturadas históricas e os preços de propostas ganhas e perdidas. O plano diz explicitamente que aprendizado de máquina só entra se superar essa média ponderada num backtest, porque os dados internos são poucos.

## Fases

| Epic | Quando | Conteúdo |
| :-- | :-- | :-- |
| DA-489 Discovery and Data Foundation | 2027, T1 | Três spikes de descoberta (pagamento interno e encargos; fontes públicas de salário e custo de vida; taxas faturadas, sites e histórico de propostas). Ingestão dos dados públicos no data warehouse, com dimensão ZIP3. Linha de base: o método manual aplicado a 3 a 5 sites e comparado com o realizado. |
| DA-490 Rate Model and Pricing Engine | 2027, T2 | Motor v1 (média ponderada, parâmetros de encargos e margem definidos pelo financeiro, faixa de confiança, backtest deixando um site de fora, erro absoluto médio em US$/h). Spike de ML com dados internos (regressão hierárquica ou regularizada). Depois, ainda sem issue: probabilidade de ganho em função da razão preço/mercado. |
| DA-491 Rate API and App Handoff | 2027, T2 | API de consulta (ZIP, função, turno → recomendação e componentes), só com agregados e usuário de serviço de menor privilégio. Protótipo do app levado para repositório próprio com CI e hospedagem. |

## Dados

**Públicos (EUA, livres):**

- BLS OEWS: salário por ocupação e área (ocupações-alvo SOC 53-3032, motoristas de caminhão pesado, e 53-7051, operadores de equipamento de movimentação);
- BLS QCEW, LAUS e ECI/CPI: emprego e salário por condado, desemprego, índices de custo do trabalho e de preços;
- BEA Regional Price Parities: custo de vida por estado e área metropolitana;
- Census ACS; tabela de correspondência ZIP ↔ condado do HUD-USPS; tabelas de salário mínimo.

**Licenciados ou limitados:** uma API comercial de salários (em piloto), agregadores de vagas.

**Internos (situação em 2026-11-23):**

- taxas faturadas por hora desde 2023, na ordem de dezenas de clientes;
- pagamento dos motoristas: os campos de remuneração chegam vazios ao data warehouse, e o caminho de acesso ainda vai ser decidido;
- propostas no CRM: o datamart parou no início de 2025, na ordem de centenas de propostas e dezenas de ganhas;
- localização dos sites: ainda não está modelada.

## Estado

Nada começou. Reunião de abertura interna em 2026-12-02. A área de dados cuida dos dados, do modelo e da API; outra equipe cuida da especificação e da interface.

## Perguntas em aberto na empresa que afetam a pesquisa

- Quem define encargos e margem, e se a margem varia por cliente ou segmento.
- Se o pagamento interno vai ficar acessível, e com que granularidade.
- Como separar função e turno.
- Se o CRM volta a ter um feed vivo (sem ele, não há propostas novas para a probabilidade de ganho).
