# Normas ABNT: instruções de escrita para este repositório

Instruções para o Claude e para o Felipe seguirem as normas ao escrever o pré-projeto, a dissertação e os artigos.

**Fonte:** *Diretrizes para apresentação de dissertações e teses da USP: parte I (ABNT)*, 5. ed., ABCD/USP, 2024 (versão de julho de 2026). DOI 10.11606/9786598386221. O PDF está em `programa/usp-diretrizes-teses-abnt-2024.pdf`, e os números de seção abaixo são os do documento.

As Diretrizes resumem as normas ABNT vigentes:
- NBR 14724 (trabalhos acadêmicos);
- NBR 6023 (referências);
- NBR 10520:2023 (citações);
- NBR 6024 (numeração das seções);
- NBR 6027 (sumário);
- NBR 6028 (resumo);
- normas tabulares do IBGE.

## 0. O que prevalece em cada documento

| Documento | Regra principal | ABNT entra como |
| :-- | :-- | :-- |
| **Dissertação** | Diretrizes USP (exigidas pelo regimento) e o que o regulamento do MECAI disser | Regra obrigatória, integral |
| **Pré-projeto** | Edital do MECAI (formato, limite de páginas e itens obrigatórios; ainda não está no repositório) | Padrão para tudo o que o edital não definir: citações, referências, figuras, tabelas, siglas, numeração |
| **Artigos** | Normas da revista (*guide for authors*) | Só se a revista pedir ABNT (revistas brasileiras, em geral). Revista internacional: estilo dela (APA, Harvard, Vancouver), não ABNT |
| **Versões em inglês** (`_EN`) | Autor-data padrão do biblatex (`authoryear`) | Mesma estrutura, figuras e tabelas; citação no formato inglês |

Quando a norma e uma regra do Felipe no `CLAUDE.md` parecerem conflitar, avisar e perguntar, sem escolher sozinho. Conflito conhecido: subalíneas (seção 3 abaixo).

## 1. Formato geral (Diretrizes 2.1, 2.2)

Já implementado em `estilo/icmc.sty`: A4, Times 12, entrelinha 1,5, margens 3 cm (superior e esquerda) e 2 cm (inferior e direita), recuo de parágrafo de 1,25 cm, número da página no canto superior direito.

Ao escrever:
- **Espaço simples** em: citações longas, notas de rodapé, referências, legendas e fontes de figuras e tabelas, natureza do trabalho na folha de rosto.
- **Fonte menor (10 ou 11)** em: citações longas, notas de rodapé, paginação, legendas e fontes. Citação com mais de 3 linhas leva recuo de 4 cm, sem aspas.
- **Redação:** objetiva, clara e concisa; sem frases introdutórias, repetições ou descrições supérfluas; tempo verbal coerente; vocabulário técnico padronizado. Evitar estrangeirismos quando houver termo em português; quando não houver, usar o termo em itálico na primeira vez e explicá-lo (ex.: *spotter*, caminhão de manobra).

## 2. Seções e sumário (2.3, 3.1.2.1.11)

- Numeração progressiva em algarismos arábicos, no máximo até a seção quinária (1.1.1.1.1). Abaixo disso, alíneas.
- **Toda seção tem texto próprio.** Nunca abrir um título e passar direto para uma subseção sem um parágrafo entre eles.
- Título da seção depois do número, separado por um espaço, alinhado à esquerda; o texto começa na linha seguinte.
- Seções primárias começam em folha nova (na dissertação; no pré-projeto, conforme o edital).
- **Títulos sem número, centralizados, com o destaque das primárias:** errata, agradecimentos, listas, resumo, abstract, sumário, referências, glossário, apêndice, anexo, índice.
- **Sem título nem número, cada um em folha própria:** dedicatória, epígrafe, folha de aprovação.
- O sumário repete a grafia e o destaque dos títulos do texto.

## 3. Alíneas e listas (2.3.1, 2.3.2)

- **Alíneas:**
  - o texto que as antecede termina em dois pontos;
  - indicadas por letra minúscula e parêntese: a), b), c);
  - texto começa em minúscula e termina em ponto e vírgula, exceto a última, que termina em ponto.
  - Em LaTeX: `\begin{enumerate}[label=\alph*)]`.
- **Subalíneas:** pela norma, começam por travessão. Isso conflita com a regra do Felipe de não usar travessão. **Padrão:** evitar subalíneas (reescrever em alíneas ou em texto corrido); se forem inevitáveis, perguntar ao Felipe antes.
- **Listas com marcadores (`itemize`):** a norma não prevê. No texto formal da dissertação, preferir alíneas. No pré-projeto, as listas atuais (achados, resultados esperados) são aceitáveis enquanto o edital não disser o contrário. Se forem convertidas, seguir as regras de pontuação das alíneas.

## 4. Siglas, equações e números (2.4, 2.5)

- **Siglas:** na primeira menção, forma completa seguida da sigla entre parênteses, como em "binomial negativa (NB)"; depois, só a sigla. Na dissertação, lista de siglas a partir de cerca de 5 itens (opcional, recomendada).
- **Equações:** destacadas e centralizadas, numeradas quando citadas no texto: `\begin{equation}` com `\label`, citada como `\eqref`. Ao quebrar linha, quebrar antes do sinal de igual ou depois de +, −, × ou ÷.
- **Números em português:** vírgula decimal e ponto de milhar, via `siunitx` (já configurado). Números citados no texto vêm das macros geradas pelos scripts, nunca digitados (regra do `CLAUDE.md`).

## 5. Figuras (2.6)

**Isto é o que mais difere do LaTeX padrão:**
- **A identificação vai em cima.** "Figura N" mais o título, breve e claro, entendível sem ler o texto. Em LaTeX, `\caption` **antes** do `\includegraphics`.
- **Abaixo da figura, a fonte é obrigatória, mesmo quando é produção do autor:** `Fonte: elaborado pelo autor.` ou `Fonte: elaborado pelo autor com dados de Autor (ano).` (citação no formato da seção 7). Legendas e notas também vêm abaixo, em fonte menor.
- A figura fica o mais perto possível do trecho que a cita, e todo título de figura que cita obra tem a obra nas referências.
- A palavra designativa depende do tipo: Figura, Gráfico, Quadro, Mapa. Para gráficos estatísticos, "Figura" é aceito. Manter um tipo só em todo o documento.
- Na dissertação, lista de ilustrações a partir de cerca de 5 figuras (opcional, recomendada).

Modelo em LaTeX:

```latex
\begin{figure}[!htbp]
\centering
\caption{\tr{Título breve e explicativo}{Short explanatory title}}
\label{fig:x}
\includegraphics[width=\textwidth]{\arqfig{fig_x}}
\fonte{\tr{Elaborado pelo autor.}{Prepared by the author.}}
\end{figure}
```

O `\fonte{}` ainda não existe no `estilo/icmc.sty`: ver seção 11.

## 6. Tabelas (2.7, normas do IBGE)

- **Título em cima**, precedido de "Tabela N" e um hífen: `Tabela 1 - Título`. Numeração seguida no documento todo ou por capítulo (Tabela 4.1).
- A tabela tem sentido próprio, sem precisar do texto.
- **Sem linhas verticais.** Traços horizontais mais fortes acima e abaixo do cabeçalho; `booktabs` (`\toprule`, `\midrule`, `\bottomrule`) já atende.
- **Fonte e notas abaixo do traço inferior:** `Fonte: elaborado pelo autor.`
- Tabela que continua em outra folha: sem traço inferior na primeira, cabeçalho repetido, e as marcas "continua", "continuação" e "conclusão".
- **Tabela é para dado numérico.** Conteúdo textual em grade é **Quadro** (ex.: "Fontes de dados previstas" e o cronograma são quadros, não tabelas). Quadro tem bordas, e sua identificação também vai em cima.

## 7. Citações no texto (seções 4 e 5)

**Sistema autor-data**, o mesmo em todo o trabalho. Implementado com `biblatex-abnt` mais a correção da NBR 10520:2023 no `estilo/icmc.sty`.

**Formato:**
- Sobrenome em **maiúsculas e minúsculas**: (Pereira, 2013), Pereira (2013).
- Dois e três autores: ponto e vírgula dentro do parêntese, (Ramos; Pestana, 2014); fora do parêntese, "Ramos e Pestana (2014)" e "Oliveira, Ferreira e Mascarenhas (2013)".
- Quatro ou mais autores: primeiro autor e *et al.*, em itálico. Manter o mesmo critério em todo o texto e nas referências.
- Mesmo autor e mesmo ano: 2013a e 2013b. Vários trabalhos juntos: ordem alfabética, separados por ponto e vírgula, (Ando, 1990; Ferreira *et al.*, 1989).
- Entidade como autora: pelo nome que aparece na referência, como (Universidade de São Paulo, 2018).

**Tipos de citação:**
- **Direta:** página obrigatória, (Madigan *et al.*, 2010, p. 89). Até 3 linhas: entre aspas duplas, no parágrafo. Mais de 3 linhas: bloco com recuo de 4 cm, fonte menor, espaço simples, sem aspas.
- **Indireta:** página opcional. É o padrão neste projeto, porque citação direta exige ter lido a fonte.
- **Apud:** só quando a fonte original não foi obtida, e ela não entra nas referências: Vianna (1986 *apud* Segatto, 1995, p. 214).
- **Marcas na citação:** "(grifo nosso)" para destaque, "[...]" para supressão, "(tradução nossa)" para tradução feita pelo autor.

**Regra de integridade, mais forte que a norma:** citar só o que está no `referencias.bib`. Entrada não conferida leva `note = {CONFERIR}`. Resultado de estudo não lido na fonte vai em termos gerais, com `\preencher{conferir ...}`. Citação direta só com o PDF em `referencias/`.

**Notas de rodapé:** permitidas no autor-data; por causa delas, o sistema numérico não é usado. Expressões latinas como *ibid.* e *op. cit.* só em nota de rodapé, e de preferência não usar; *apud* pode ir no texto.

**Fontes informais** (palestra, comunicação pessoal, conversa): indicar no texto ou em nota, sem entrada nas referências.

**Sites:** no texto, autor ou título; o endereço só na referência.

## 8. Referências (3.1.2.3.1, 6, 7)

O `biblatex-abnt` aplica a NBR 6023 automaticamente: SOBRENOME em caixa alta, título em negrito, espaço simples, linha em branco entre referências, ordem alfabética.

O que depende do `.bib`:
- **Todo documento listado é citado no texto, e toda citação está nas referências.** O biblatex garante a primeira parte (só lista o citado); a lista de leitura em `referencias/` é outro documento.
- **Campos completos:** autor, título, periódico, volume, número, páginas, ano e DOI quando houver. Documento *online* sem DOI leva `url` e `urldate`, que geram o "Acesso em:".
- **Edição:** só a partir da 2ª (`edition = {2}`), no idioma da publicação.
- **Quatro ou mais autores:** a norma recomenda indicar todos; o biblatex corta em *et al.* conforme `maxbibnames`. Decidir uma vez e manter (ver seção 11).
- **Dataset, software e legislação:** usar `@misc`, `@software` e `@legislation` com os campos que o `biblatex-abnt` reconhece; conferir a saída no PDF.
- Indicar em nota de rodapé a norma usada nas referências ("Conforme ABNT NBR 6023:2018"). É obrigatório nas Diretrizes (3.1.2.3.1); aplicar na dissertação.

## 9. Resumo e palavras-chave (3.1.2.1.8 e 3.1.2.1.9)

- Parágrafo único, de 150 a 500 palavras, com objetivo, método, resultados e conclusões.
- **Palavras-chave** logo abaixo, depois de "Palavras-chave:", **separadas por ponto e terminadas em ponto**, de preferência do Vocabulário Controlado USP (https://vocabusp.abcd.usp.br/vocab/). O mesmo para *Keywords*.
- Na dissertação, o resumo é precedido da referência do próprio trabalho: SOBRENOME, Nome. **Título**. Ano. Dissertação (Mestrado em ...) – Instituto, Universidade, Cidade, Ano. O *Abstract* tem as mesmas características.
- Título, resumo e palavras-chave em português e inglês (Regimento USP, art. 84). Isto já é garantido pela estrutura bilíngue do repositório.

## 10. Estrutura da dissertação (3.1, Figura 1)

Ordem obrigatória; (op.) indica elemento opcional:

1. Capa: instituição (op.), autor, **título** (minúsculas exceto inicial e nomes próprios), local, ano do depósito.
2. Folha de rosto: autor, título, "Versão original" ou "Versão corrigida", natureza (dissertação apresentada ao ... para obtenção do título de Mestre em ...; área de concentração), orientador, local, ano. A natureza vai em espaço simples, alinhada do meio da página para a direita.
3. Autorização de reprodução e ficha catalográfica, feita pela biblioteca do ICMC, logo após a folha de rosto no formato digital.
4. Errata (op.).
5. Folha de aprovação, com os campos da banca em branco.
6. Dedicatória (op., sem título), agradecimentos (op.) e epígrafe (op., sem título, com a fonte nas referências).
7. Resumo, *Abstract*.
8. Listas (op.): ilustrações, tabelas, siglas, símbolos.
9. Sumário.
10. Texto: introdução, desenvolvimento, conclusão. A conclusão responde aos objetivos e às hipóteses.
11. Referências, glossário (op.), apêndices (op.; "APÊNDICE A - TÍTULO"), anexos (op.; "ANEXO A - TÍTULO") e índice (op.).

**Paginação:** as folhas pré-textuais são contadas, mas não numeradas. O número aparece a partir da Introdução, em arábicos, no canto superior direito, e apêndices e anexos seguem a numeração.

**Agradecimento a financiador:** texto obrigatório da CAPES ou da FAPESP, se houver bolsa. Hoje não se aplica (o MECAI não tem bolsa).

## 11. Adaptações no LaTeX e o que ainda falta

Feito:
- [x] **Citações em maiúsculas e minúsculas** (NBR 10520:2023). O `biblatex-abnt` instalado é a v3.4 (2018) e usava CAIXA ALTA; a correção está em `estilo/icmc.sty` (2026-11-15). Se o pacote for atualizado para uma versão com opção própria, trocar a correção pela opção.

Pendente; aplicar só quando o Felipe pedir:
- [ ] **Legendas de figura em cima** e linha `Fonte:` abaixo de figuras e tabelas. Criar no `icmc.sty` um `\fonte{}` (fonte 10, espaço simples) e mover os `\caption`. Hoje as figuras têm a legenda embaixo e nenhuma tem "Fonte".
- [ ] **Separador "Figura 1 - Título"**, com hífen, no lugar de "Figura 1:". Usar o pacote `caption`, com `labelsep=endash` (meia-risca, não travessão) ou `labelsep=period`, e fonte 10 ou 11.
- [ ] **Quadros:** reclassificar como quadro as tabelas textuais ("Fontes de dados", cronograma), com bordas.
- [ ] **Palavras-chave** separadas por ponto (hoje estão com ponto e vírgula, no pré-projeto).
- [ ] **Títulos sem número centralizados**, como "REFERÊNCIAS" e "RESUMO" (hoje estão alinhados à esquerda e numerados conforme o caso).
- [ ] **Dissertação:** capa, folha de rosto, ficha, folha de aprovação, listas e paginação pré-textual (seção 10). Avaliar usar a classe `abntex2`, que já implementa a NBR 14724, ou adaptar a `report` atual.
- [ ] **Quatro ou mais autores nas referências:** decidir entre todos os nomes (recomendado pela norma) ou *et al.*, e fixar `maxbibnames`.
- [ ] **Nota de rodapé com a norma das referências** (dissertação).

## 12. Checklist antes de entregar um texto

1. Toda seção tem texto antes da primeira subseção?
2. Siglas definidas na primeira menção?
3. Citações em maiúsculas e minúsculas, e citações diretas com página?
4. Toda citação está no `.bib`, e as entradas `CONFERIR` estão sinalizadas ao Felipe?
5. Figura com identificação em cima e `Fonte:` embaixo? Tabela sem linha vertical e com `Fonte:`?
6. Alíneas com dois pontos antes, ponto e vírgula entre elas e ponto na última?
7. Resumo entre 150 e 500 palavras, em parágrafo único, com palavras-chave separadas por ponto?
8. Números com vírgula decimal, vindos das macros dos scripts?
9. Compilou PT e EN sem erro, e as páginas alteradas foram conferidas visualmente?
