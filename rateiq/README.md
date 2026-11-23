# Projeto 2: RateIQ (recomendação de taxa de motoristas)

Segunda ideia de tese, surgida em conversas no trabalho em novembro de 2026. Ainda é **candidata**: a primeira ideia (`../risco-patio/`) continua sendo a do pré-projeto até o Felipe decidir trocar.

**O que é.** Um sistema que, para uma região (ZIP de 3 dígitos, nos EUA), uma função e um turno, recomenda o salário esperado do motorista e a taxa por hora a cobrar do cliente, com cada componente e uma faixa de incerteza à vista. Hoje cada proposta comercial pesquisa essa taxa à mão. Na empresa, o projeto está planejado em três epics para o 1º e o 2º trimestre de 2027.

**Onde pode estar a pesquisa.** O produto (API, app) é engenharia. A pesquisa é o núcleo estatístico: estimar salário e taxa em áreas pequenas combinando dados públicos agregados com poucos dados internos, com incerteza calibrada, e escolher o preço sabendo que ele muda a chance de ganhar a proposta. Detalhes em `notas/02-angulo-de-pesquisa.md`.

```
rateiq/
├── README.md
├── preprojeto/
│   ├── admissao.tex          projeto curto da inscrição (até 5 páginas), bilíngue, mesmo formato do da ideia 1
│   └── output/               PDFs (PT, EN, cor, P&B): python compilar.py rateiq
└── notas/
    ├── 01-origem-e-escopo.md     o que as epics do Jira planejam (sem nomes, volumes em ordem de grandeza)
    └── 02-angulo-de-pesquisa.md  perguntas, hipóteses candidatas, dados, riscos e comparação com a ideia 1
```

Quando a ideia avançar, esta pasta ganha `analise/`, `dados/` e `resultados/` (os dois últimos fora do git), como a primeira.

## Cuidados

- O repositório é público. Nada aqui nomeia a empresa, pessoas, clientes ou unidades, e volumes internos aparecem só em ordem de grandeza.
- Salários pagos e taxas cobradas são **informação comercial sensível**: nunca entram no git, nem agregados por cliente. Conferir se a autorização de uso dos dados (dada em 2026-11-15 para a pesquisa de risco) cobre este tema.
- Jira e Confluence da empresa: só leitura.
