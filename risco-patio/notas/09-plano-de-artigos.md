# 09. Plano de artigos

Criada em 2026-11-11. Três trabalhos saem do projeto: dois artigos em periódico e um trabalho opcional de método. Estão no cronograma do pré-projeto (seção 8).

As revistas listadas são candidatas e não foram conferidas. Antes de escolher, verificar escopo, tipo de artigo aceito, política de dados e prazos de revisão **[não verificado]**.

## Artigo 1: medir e comparar o risco de acidentes no pátio (H1)

- **Pergunta:** como comparar o risco de acidentes entre unidades e caminhões numa operação de pátio, em que exposição e tipo de operação variam muito?
- **Mensagem central:** a escolha da exposição e o ajuste pelo tipo de operação mudam a conclusão. Contagens brutas medem tamanho, não risco, e taxas com encolhimento são a forma defensável de comparar unidades.
- **Contribuições:**
  1. **Exposição:** por milha o spotter tem taxa mais de 20 vezes a do caminhão local; por hora, cerca de 3 vezes. A escolha da medida inverte comparações.
  2. **Tipo de uso como confundidor central** (spot, shuttle, local).
  3. **H1:** variação real entre unidades (homogeneidade rejeitada, funil); a taxa por Bayes empírico prevê melhor o semestre seguinte; ela não se confunde com o tamanho (equivalência), ao contrário da contagem bruta; o ranking é instável, então a comunicação deve ser por intervalos e grupos.
  4. **Duas fontes de exposição** (telemetria e folha) e quando elas concordam.
- **Dados e métodos:** painel veículo × mês. NB2 hierárquica (efeitos de veículo, unidade e calendário), Bayes empírico, gráfico de funil, validação temporal e bootstrap.
- **Revistas candidatas:** Journal of Safety Research, Safety Science, Accident Analysis & Prevention.
- **Lacuna que justifica:** quase não há literatura revisada por pares sobre segurança em pátio de centro de distribuição (ver `06-mapa-da-literatura.md`). Confirmar numa busca no Scopus antes de escrever.
- **Quando:** análise no S3, submissão ao fim do S4. Precisa de mais 6 a 12 meses de dados além do ano atual.
- **Situação:** resultados preliminares em `08-viabilidade-dados-reais.md` (seções 3 e 8) e na Figura 2 do pré-projeto.

## Artigo 2: telemetria de estrada aplicada ao pátio (H2 e H3)

- **Pergunta:** a telemetria comercial, desenhada para a estrada, serve para medir risco e detectar acidentes no pátio?
- **Mensagem central:** dentro do mesmo tipo de operação, os eventos de condução pouco ou nada informam sobre o risco de acidente, e a detecção automática de colisão quase não capta acidentes de pátio. Ferramentas de estrada não substituem dados próprios do pátio.
- **Contribuições:**
  1. **H2 com equivalência:**
     - sem ajuste, eventos parecem associados a acidentes;
     - com tipo de uso e efeito de veículo, nenhum rejeita H0 e a maioria tem efeito desprezível;
     - a telemetria não melhora o escore fora da amostra.
  2. **Cobertura da detecção automática:**
     - menos de 10% dos acidentes relatados têm detecção, igual entre tipos de uso;
     - mais de 80% das detecções são descartadas na revisão.
  3. **Subnotificação com a manutenção como segunda fonte:**
     - captura e recaptura com dependência entre as fontes;
     - variação entre unidades (H3).
- **Cuidados:**
  - **Fixar as margens antes.** Fixar as margens de equivalência e o plano de análise antes dos dados finais, de preferência com pré-registro (por exemplo no OSF). Isso protege contra a crítica de "resultado nulo escolhido a posteriori".
  - **Verificar a manutenção como fonte.** Confirmar se as ordens de manutenção são independentes do relato. O motivo "ACC-REPORTED" pode significar que o acidente já foi relatado (ver `08`, seção 8).
- **Revistas candidatas:** Accident Analysis & Prevention, Traffic Injury Prevention, Transportation Research Record (porta de entrada pelo congresso anual do TRB).
- **Quando:** análise no S4 e no S5, submissão no S6. Depende de reativar a sincronização da Samsara e de validar a fonte de manutenção.

## Trabalho 3 (opcional): estudo de simulação calibrado em dados públicos

- **Pergunta:** quantos acidentes e que estrutura de modelo são necessários para detectar efeitos de telemetria e comparar unidades em frotas de algumas centenas de veículos?
- **Contribuições:**
  - poder em função do número de acidentes;
  - falsos positivos sem o efeito aleatório de veículo (até 3 vezes o nominal);
  - desempenho de rankings brutos contra encolhimento;
  - estimação da subnotificação com encolhimento.
- **Vantagem:** é totalmente reproduzível (dados públicos e código aberto) e não depende de autorização da empresa. Pode sair primeiro.
- **Formato:** artigo de congresso. Candidatos: SBPO, congresso da ANPET, workshop de ciência de dados. Também pode virar nota metodológica em periódico.
- **Quando:** S2 e S3. O material já existe em `dissertacao/capitulos/05-viabilidade.tex` e `analise/viabilidade/`.

## Condições comuns

1. **Autorização para publicar.** É diferente da autorização para a dissertação. Pedir no acordo de confidencialidade uma cláusula de publicação com anonimização: sem nome da empresa, dos clientes nem das unidades, só valores relativos e ordens de grandeza.
2. **Disponibilidade dos dados.** Os dados reais não podem ser abertos. Publicar o código, o estudo de simulação e a aplicação ao dataset público, com declaração de disponibilidade explicando a restrição.
3. **Autoria.** Orientador(a) como coautor(a), conforme a prática do programa. Coautores da empresa, se houver contribuição, decididos com a empresa.
4. **Programa.**
   - O PPG-CCMC exige comprovante de artigo no depósito. Para o MECAI, essa exigência **não foi verificada**: conferir no edital ou no regulamento do MECAI.
   - Publicação costuma render créditos especiais.

## Pendências

- [ ] Busca no Scopus para confirmar a lacuna sobre segurança em pátio (artigos 1 e 2).
- [ ] Ler o escopo das revistas candidatas e escolher a primeira opção de cada artigo.
- [ ] Verificar a independência e a ligação das ordens de manutenção (artigo 2).
- [ ] Redigir o pré-registro do artigo 2 antes da análise final.
- [ ] Incluir a cláusula de publicação no pedido de autorização à empresa.
