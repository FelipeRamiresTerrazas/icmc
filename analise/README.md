# Esqueleto de análise (pré-projeto ICMC)

Código que implementa as etapas 2 a 4 da metodologia. Hoje roda **só com dados sintéticos**: nenhum dado da empresa é lido aqui.

| Arquivo | O que faz |
| --- | --- |
| `painel_sintetico.py` | Gera um painel veículo × mês com a mesma estrutura do real e parâmetros conhecidos (efeito de frenagem e curva, efeito nulo de velocidade, efeitos de site e veículo, superdispersão, detecção pelos sensores e probabilidade de relato por site). |
| `modelos.py` | Poisson e binomial negativa com exposição como offset; escore logarítmico fora da amostra (H2); bayes empírico por site e comparação de indicadores entre semestres (H1); limites do gráfico de funil; probabilidade de relato com encolhimento e Lincoln-Petersen (H3). |
| `rodar_exemplo.py` | Roda tudo e grava `resultados/funil_sintetico.pdf` (pasta fora do git). |
| `tests/test_modelos.py` | Confere se os modelos recuperam os parâmetros verdadeiros. |

Na raiz deste repositório (ambiente criado com `python -m venv .venv` e `.venv/Scripts/python -m pip install -r requirements.txt`):

```
PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/rodar_exemplo.py
.venv/Scripts/python -m pytest analise/tests -q
```

## O que o exemplo sintético já mostrou

Contagens brutas por site são o indicador mais estável entre semestres, mas só porque refletem o tamanho do site (correlação alta com as horas) e erram mais ao prever a taxa seguinte. Por isso a H1 foi escrita em termos de previsão da taxa seguinte e de correlação com o tamanho, não de estabilidade pura.

## Próximos passos (depois da autorização)

1. Consulta SQL que monta o painel veículo × mês **dentro do Snowflake**, só com agregados (sem motorista, sem GPS, sem imagem). Só sai do ambiente da empresa o painel agregado, para `dados/` (fora do git).
2. Modelo hierárquico completo (efeitos aleatórios de veículo e site, eq. 1 do pré-projeto) no R com glmmTMB ou brms, num projeto renv separado do `r/` do projeto ESALQ.
3. Validação por site (deixa um de fora), resíduos quantílicos aleatorizados, definições alternativas de acidente.
