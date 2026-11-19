# Pré-projeto ICMC (MECAI), bilíngue

Um único código gera quatro PDFs: português e inglês, colorido e preto e branco.

## Projeto curto da inscrição (`admissao.tex`)

Versão de no máximo 5 páginas para anexar à inscrição no processo seletivo, com o roteiro do item 3.4.2 do edital (título e resumo; introdução com motivação, justificativa e objetivos; principais pontos e metodologia; cronograma; bibliografia). É um documento à parte, que apresenta só a ideia: não cita o estudo preliminar, os resultados com os dados da operação nem a dissertação. Compilar com `python compilar.py admissao` (PDFs `output/Projeto_MECAI_Felipe_Terrazas[_EN][_PB].pdf`). Depois de qualquer mudança, conferir que as quatro versões continuam com 5 páginas.

## Compilar

Na raiz do repositório: `python compilar.py preprojeto` (as quatro versões) ou, por exemplo, `python compilar.py preprojeto --lingua en --modo pb`. À mão, dentro desta pasta:

```
TEXINPUTS=".;../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas main.tex        # português, cor
TEXINPUTS=".;../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN main.tex     # inglês, cor
TEXINPUTS=".;../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas_PB main.tex     # português, P&B
TEXINPUTS=".;../;" latexmk -pdf -outdir=output -jobname=PreProjeto_MECAI_Felipe_Terrazas_EN_PB main.tex  # inglês, P&B
```

A língua troca também a hifenização, os rótulos ("Tabela"/"Table"), o título das referências e o estilo das citações (ABNT em português, autor-ano em inglês). O modo P&B troca as cores do texto e das caixas e as figuras.

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

Figuras: `\includegraphics[width=\textwidth]{\arqfig{fig_nome}}`. A macro escolhe `fig_nome.pdf`, `fig_nome_en.pdf`, `fig_nome_pb.pdf` ou `fig_nome_en_pb.pdf` conforme a versão; os scripts de figura sempre geram as quatro. Se a legenda cita uma cor, use `\corpb{versão colorida}{versão P\&B}`, por exemplo `\corpb{faixa azul-clara}{faixa cinza}`.

Fórmulas, tabelas e referências cruzadas ficam fora dos comandos de língua quando são iguais nas duas versões (exemplo: a equação do modelo em `partes/05-metodologia.tex`).

Fluxo sugerido: edite só o português e peça "sincroniza o inglês"; os blocos `\en{}` são atualizados a partir dos `\pt{}` alterados.

## Convenções

- Pendências visíveis: `\preencher{...}` (vermelho). Nenhuma pode sobrar na versão enviada.
- Referências: `../referencias.bib`. Toda entrada nova leva `note = {CONFERIR}` até ser checada na fonte; aparece em vermelho no texto e na lista.
- O texto não nomeia a empresa, clientes nem unidades, e só usa ordens de grandeza dos dados (sem números internos exatos) até a autorização formal.
- Sem travessão nem `---`.

## Pendências do texto

- Edital: limite de páginas, formato e norma de referências. Duração (36 meses, sem qualificação) e roteiro do projeto já conferidos na FAQ do programa (ver `../programa/README.md`).
- Nome oficial do programa na capa: conferir.
- Comitê de ética: confirmar se é exigido.
- Busca bibliográfica sistemática sobre acidentes em operações de pátio (a introdução diz que o tema é pouco explorado; precisa ser confirmado).
