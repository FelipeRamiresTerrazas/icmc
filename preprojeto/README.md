# Pré-projeto ICMC (MECAI), bilíngue

Um único código gera o PDF em português e em inglês.

## Compilar

Dentro desta pasta:

```
latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas main.tex       # português
latexmk -pdf -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN main.tex    # inglês
```

Com `_PB` no fim do nome (`..._PB` ou `..._EN_PB`) sai a versão preto e branco. A língua troca também a hifenização, os rótulos ("Tabela"/"Table"), o título das referências e o estilo das citações (ABNT em português, autor-ano em inglês).

## Como escrever

Parágrafos: as duas línguas ficam uma logo abaixo da outra.

```latex
\pt{%
Texto em português.
}
\en{%
Text in English.
}
```

Trechos curtos (títulos, células, itens de lista): `\tr{português}{English}`.

Fórmulas, tabelas e referências cruzadas ficam fora dos comandos de língua quando são iguais nas duas versões (exemplo: a equação do modelo em `partes/05-metodologia.tex`).

Fluxo sugerido: edite só o português e peça "sincroniza o inglês"; os blocos `\en{}` são atualizados a partir dos `\pt{}` alterados.

## Convenções

- Pendências visíveis: `\preencher{...}` (vermelho). Nenhuma pode sobrar na versão enviada.
- Referências: `../referencias-icmc.bib`. Toda entrada nova leva `note = {CONFERIR}` até ser checada na fonte; aparece em vermelho no texto e na lista.
- O texto não nomeia a empresa, clientes nem unidades, e só usa ordens de grandeza dos dados (sem números internos exatos) até a autorização formal.
- Sem travessão nem `---`.

## Pendências do texto

- Edital: limite de páginas, formato e norma de referências. Duração (36 meses, sem qualificação) e roteiro do projeto já conferidos na FAQ do programa (ver `../04-programa-mecai.md`).
- Nome oficial do programa na capa: conferir.
- Comitê de ética: confirmar se é exigido.
- Busca bibliográfica sistemática sobre acidentes em operações de pátio (a introdução diz que o tema é pouco explorado; precisa ser confirmado).
