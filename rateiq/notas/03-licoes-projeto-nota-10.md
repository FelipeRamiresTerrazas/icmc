# 03. Lições de um projeto nota 10 (turma de 2026)

O Felipe conseguiu o projeto de pesquisa de um aluno aprovado na turma de 2026, que teve nota 10 no projeto. O PDF fica **só localmente** em `programa/exemplos-locais/` (excluído do git por `.git/info/exclude`). Esta nota não nomeia o aluno nem a empresa dele. Não sabemos a rubrica da banca: os motivos abaixo são inferência a partir do texto.

## 1. O projeto em uma frase

Previsão antecipada da queda de um índice de qualidade de vendas de pontos de venda (canais indiretos de telecomunicações), usado para ajustar a comissão dos parceiros, comparando modelos tabulares com modelos de redes complexas e GraphSAGE. Tem 20 páginas, 9 seções e 28 referências.

**Primeira lição: o tamanho.** O relato do aluno do MECAI (`notas/12`) falava em "no máximo cerca de 5 páginas", mas um projeto de 20 páginas tirou 10. O edital não limita páginas. O limite de 5 páginas do nosso projeto curto foi decisão nossa, não regra.

## 2. Por que provavelmente tirou 10

1. **O problema de negócio é explicado com precisão.** Fórmulas da comissão e do índice, uma figura com a linha do tempo (venda em M0, índice em M4, pagamento em M6), um exemplo numérico de cálculo e a tabela de parâmetros. Quem lê entende o mecanismo sem conhecer a empresa.
2. **Há teoria por trás do negócio, não só método.** Teoria da agência (principal e agente, risco moral, informação assimétrica) explica *por que* o índice existe. O método (redes) entra depois, como resposta a uma premissa falha (independência entre pontos de venda).
3. **Uma pergunta de pesquisa única, comparativa e testável:** "a estrutura de rede melhora a previsão em relação ao modelo tabular?". Qualquer resposta é útil.
4. **Escada de modelos com regra de parcimônia.** Cinco níveis (regra vigente, logística, boosting, boosting com métricas de rede, GraphSAGE); se o mais simples empatar, fica o mais simples.
5. **Cuidado explícito com as armadilhas do problema.** Matriz de disponibilidade temporal das variáveis (o que pode ser preditor e o que só serve de rótulo), corte das safras ainda não maturadas, validação fora do tempo, calibração, limiar escolhido por custo e benefício.
6. **Métricas de negócio, não só estatísticas.** Lift por decil, precision@k e simulação retrospectiva do impacto financeiro.
7. **Cara de mestrado profissional.** Entrega um artefato (painel de apoio à decisão), com governança: sinaliza risco, não penaliza automaticamente; seção de ética e LGPD, inclusive viés.
8. **Gestão de riscos.** Seção própria e cronograma em tabela com atividade, entregável e risco com mitigação por período.
9. **Método moderno, mas justificado.** GraphSAGE escolhido por ser indutivo (gera previsão para ponto de venda novo, sem histórico).

## 3. O que ele tem de fraco (onde podemos ser melhores)

- Hipóteses vagas, sem hipótese nula, teste, tamanho de efeito ou critério de decisão.
- Fala em **qualificação**, que o MECAI não tem, e não tem plano alternativo se os dados faltarem.
- Nenhuma simulação nem estudo preliminar.
- Expõe parâmetros internos da empresa e um exemplo com números de telefone. **Não copiar isso:** nossa regra é não nomear a empresa e dar volumes só em ordem de grandeza.

## 4. O que levar para o projeto do RateIQ

| # | Ação | Equivalente no projeto nota 10 | Situação no `admissao.tex` |
|---|---|---|---|
| 1 | Decidir o tamanho: versão completa (cerca de 12 a 15 páginas) além ou no lugar do projeto curto | 20 páginas | Feito: versão completa, 18 páginas em português (decisão de 2026-11-26) |
| 2 | Seção "Problema e pergunta de pesquisa" com **uma** pergunta comparativa | 1.1 | Feito: seção 1.2, com a pergunta destacada e H1 a H3 derivadas dela |
| 3 | Fundamento teórico do negócio: diferenciais compensatórios e mercados de trabalho locais (economia do trabalho) e teoria de propostas, além de pequenas áreas | Teoria da agência | Feito: seção 2 (2.1 diferenciais compensatórios, mercados locais e monopsônio; 2.2 propostas; 2.3 pequenas áreas como resposta) |
| 4 | Figura da cadeia de cálculo (fontes públicas, correspondência geográfica, salário, taxa $b = p(1+c)h/(1-m)$) com **exemplo numérico fictício** | Figuras 1 e 2 | Feito: Figura 1 (`analise/fig_cadeia.py`), exemplo fictício de 20 US$/h de salário e 40 US$/h de taxa |
| 5 | Tabela das fontes: geografia, defasagem de publicação, erro padrão, uso no modelo | Matriz de disponibilidade | Feito: Quadro 1 (OEWS, QCEW, RPP, ACS, HUD-USPS, salário mínimo, internos) |
| 6 | Vazamento temporal: prever cada proposta só com a edição da OEWS e do BEA disponível na data | Matriz temporal | Feito: seção 3.3, regra das edições publicadas e validação transversal e temporal |
| 7 | Escada de modelos com parcimônia: pesos fixos, estimativa direta, Fay-Herriot, hierárquico com camada interna, conformal | 5 níveis | Feito: seção 3.5 e Quadro 2 (M0 a M4), com regra de parcimônia |
| 8 | Métrica de negócio: simulação retrospectiva do efeito do erro de preço (proposta perdida por preço alto, margem perdida por preço baixo) | Seção 5.10 | Feito: seção 3.8, Equação 5 (proposta perdida e margem perdida) |
| 9 | Artefato e governança: calculadora com faixa de incerteza; recomenda, não decide; revisão humana | Painel, seção 5.12 | Feito: seção 3.9 (recomenda, não decide; revisão humana; aviso de pouca informação) |
| 10 | Ética ampliada: salário como dado sensível, risco de perpetuar desigualdade salarial, cuidado com troca de informação salarial entre empresas | LGPD e viés | Feito: seção 3.10 (LGPD, desigualdade salarial, diretrizes antitruste sobre troca de informação salarial) |
| 11 | Seção de riscos (dados internos escassos, mudança de suporte, viés de seleção nas propostas) com mitigação | Seção 8 | Feito: seção 4 e Quadro 3, com plano alternativo |
| 12 | Cronograma com entregáveis por semestre | Tabela com entregáveis e riscos | Feito: Quadro 4 (S1 a S4, atividades, entregáveis, risco e mitigação) |

Situação em 2026-11-26: as 12 ações estão no português; o inglês ainda não foi sincronizado (parágrafos `\en{}` marcados como pendentes).

**Manter o que já temos e ele não tem:** hipóteses H1 a H3 com teste e critério, validação deixando áreas e unidades de fora, simulação com parâmetros conhecidos, plano alternativo só com dados públicos, 36 meses sem qualificação.

Referências novas levantadas em 2026-11-26 (dados bibliográficos conferidos em catálogos, sem leitura do texto integral; todas com `note = {CONFERIR}`): rosen1986, moretti2011, manning2021, burks2019, agrawal2007, cullen2024, kaufman2012, doj2025workers, bls2025qcew, census2025acs, hud2025crosswalk e dol2025minwage.
