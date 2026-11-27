# Projeto 2: RateIQ (recomendação de taxa de motoristas)

Segunda ideia de tese, surgida em conversas no trabalho em novembro de 2026. Ainda é **candidata**: a primeira ideia (`../risco-patio/`) continua sendo a do pré-projeto até o Felipe decidir trocar.

**O que é.** Um sistema que, para uma região (ZIP de 3 dígitos, nos EUA), uma função e um turno, recomenda o salário esperado do motorista e a taxa por hora a cobrar do cliente, com cada componente e uma faixa de incerteza à vista. Hoje cada proposta comercial pesquisa essa taxa à mão. Na empresa, o projeto está planejado em três epics para o 1º e o 2º trimestre de 2027.

**Onde pode estar a pesquisa.** O produto (API, app) é engenharia. A pesquisa é o núcleo estatístico: estimar salário e taxa em áreas pequenas combinando dados públicos agregados com poucos dados internos, com incerteza calibrada, e escolher o preço sabendo que ele muda a chance de ganhar a proposta. Detalhes em `notas/02-angulo-de-pesquisa.md`.

```
rateiq/
├── README.md
├── preprojeto/
│   ├── admissao.tex          projeto da inscrição, versão completa (cerca de 18 páginas), bilíngue
│   ├── figuras/              Figura 1 nas quatro variantes, gerada por analise/fig_cadeia.py
│   ├── tabelas/              números do exemplo fictício da Figura 1 (num_exemplo.tex), gerados pelo mesmo script
│   └── output/               PDFs (PT, EN, cor, P&B): python compilar.py rateiq
├── analise/
│   └── fig_cadeia.py         Figura 1: cadeia de cálculo da taxa, com exemplo fictício (.venv/Scripts/python rateiq/analise/fig_cadeia.py)
└── notas/
    ├── 01-origem-e-escopo.md     o que as epics do Jira planejam (sem nomes, volumes em ordem de grandeza)
    ├── 02-angulo-de-pesquisa.md  perguntas, hipóteses candidatas, dados, riscos e comparação com a ideia 1
    └── 03-licoes-projeto-nota-10.md  o que um projeto nota 10 da turma de 2026 faz bem e o que levar para o nosso
```

Quando a ideia avançar, esta pasta ganha `dados/` e `resultados/` (fora do git), como a primeira.

## Cuidados

- O repositório é público. Nada aqui nomeia a empresa, pessoas, clientes ou unidades, e volumes internos aparecem só em ordem de grandeza.
- Salários pagos e taxas cobradas são **informação comercial sensível**: nunca entram no git, nem agregados por cliente. Conferir se a autorização de uso dos dados (dada em 2026-11-15 para a pesquisa de risco) cobre este tema.
- Jira e Confluence da empresa: só leitura.
