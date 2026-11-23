# 12. Conversa com um aluno do MECAI (2026-11-17)

Anotações da conversa do Felipe com um aluno do mestrado profissional, traduzidas das notas automáticas da reunião. O Felipe disse que conversou com o **Tulio**, mas as notas chamam o aluno de **Matheus**; o nome está assim abaixo porque veio das notas **[conferir]**.

É **relato informal de um aluno**, não regra do programa. O que conflita com o edital ou com a FAQ está marcado. Nota interna: tem opiniões pessoais sobre docentes e não deve ser compartilhada.

## 1. Visão geral do MECAI

- **Programa:** mestrado profissional em Ciência de Dados no ICMC/USP.
  - O mestrado acadêmico seria conjunto USP e UFSCar; o profissional é só da USP **[não verificado]**.
  - Teria de 16 a 20 vagas por turma e de 6 a 8 candidatos por vaga. **O edital 002/2026 oferece 14 vagas.**
  - Teria de 5 a 10 anos de existência e nota 5 na CAPES, a máxima para mestrado profissional **[não verificado]**.
  - Haveria planos de um doutorado profissional nos próximos anos.
- **Aulas:** às sextas à tarde, pensadas para quem trabalha. O edital diz "de segunda a quinta à noite ou às sextas (manhã, tarde e noite)", eventualmente aos sábados de manhã.
- **Trajetória do aluno:** saiu do mestrado acadêmico por conflito de horário, fez o MBA do ICMC e depois entrou no MECAI.

## 2. Processo seletivo

- **Três componentes:**
  1. Lattes e currículo profissional (trajetória);
  2. histórico da graduação;
  3. projeto de pesquisa.
  - Isso bate com o edital: FA, AC e PP, com pesos 4, 3 e 3.
- **Tamanho do projeto: no máximo cerca de 5 páginas,** com introdução, metodologia, resultados esperados e um cronograma aproximado. **O edital não fixa limite**, mas o pré-projeto atual tem 17 páginas (ver seção 6).
- **O tema pode mudar depois do ingresso;** o projeto serve sobretudo como critério de seleção.
- **Orientador:** é designado pelo programa, não escolhido, em geral uns 2 meses depois do ingresso.
  - **Diverge do edital:** o Anexo II diz que o formulário de matrícula é assinado pelo aluno e pelo orientador. Conferir com a secretaria.
  - Dica: falar antes com docentes para criar um contato informal.
  - Cada docente teria limite de cerca de 10 orientandos; parte vem de outras instituições.
- **Próximo edital:** previsto para abril, o que bate com o calendário de 2026.

## 3. Disciplinas e estilo das aulas

- **Créditos:** 3 disciplinas obrigatórias e cerca de 2 optativas, mais a dissertação. Pela FAQ, o mínimo são 18 créditos entre MAI5001, MAI5002 e MAI5003 (ver `04-disciplinas.md`).
- **Duas disciplinas centrais por projeto:**
  - **Estatística aplicada** (Prof. Louzada; as notas escrevem "Lousada"): sem slides nem material fixo, com projeto em grupo ao longo do semestre que mira um artigo publicado. Provavelmente é a MAI5003 **[conferir]**.
  - **Matemática aplicada:** continua o projeto de estatística e o leva até a submissão do artigo. Provavelmente é a MAI5002 **[conferir]**.
- **Introdução à Ciência da Computação** (Prof. Cláudio, MAI5001): aulas estruturadas, com slides e projeto final; mais flexível com a carga de trabalho dos alunos.
- **Impressões do aluno sobre os docentes:**
  - Louzada: cofundador do MECAI, muito voltado a publicação; aproveitado melhor em aula do que como orientador.
  - Cláudio: voltado ao ensino, acessível; às vezes recruta alunos do MBA.

**Consequência para o plano de artigos:** a disciplina de estatística já gera um artigo em grupo. Vale alinhar o tema desse projeto com o artigo 1 ou com o trabalho de simulação de `09-plano-de-artigos.md`.

## 4. Projeto de pesquisa: cuidados

- **Vínculo e dados:** o programa exigiria vínculo empregatício e acesso aos dados da empresa na matrícula. O edital exige só o comprovante de vínculo (atual ou dos últimos 2 anos); o acesso aos dados não aparece nele.
  - **Risco:** perder o emprego ou o acesso aos dados no meio do curso pode inviabilizar a pesquisa.
  - **A coordenação recomenda** ter um acordo formal de uso de dados com a empresa **ou** usar dados públicos desde o início.
  - Isso reforça o plano alternativo com dados públicos (`../risco-patio/notas/05-datasets-publicos.md`, estudo de simulação) e o pedido de autorização com acordo de confidencialidade.
- **Projeto do aluno:** risco de crédito contra rentabilidade numa empresa do setor bancário. O acesso aos dados está incerto pelo cenário de inadimplência, e ele precisa rever o escopo com o orientador.
- **Projeto do Felipe, como foi apresentado na conversa:** modelo de pontuação de risco de acidente por unidade logística.
  - Variáveis citadas: motoristas por período, horas trabalhadas, **horas extras**, **treinamento** e tamanho da unidade.
  - Desafio citado: **viés de subnotificação, porque o gestor da unidade perde bônus se o acidente for registrado.**

**Consequências para o projeto:**
- O incentivo de bônus é um mecanismo concreto para a H3 (subnotificação desigual entre unidades). Vale citar no pré-projeto em termos gerais, sem nomear a empresa: "incentivos ligados a indicadores de segurança podem reduzir o relato".
- **Horas extras** já existem no ADP (categoria "Over Time"; ver `08`) e podem entrar como covariável, como já apontava a literatura (dembe2005).
- **Treinamento** ainda não está em nenhuma fonte levantada **[verificar se há registro]**.

## 5. Docentes citados

| Docente | O que o aluno disse |
| :-- | :-- |
| Maristela Oliveira dos Santos | Indicada para logística e otimização; formação em matemática computacional e otimização (problemas do tipo caixeiro-viajante); acessível. Ministra a MAI5032 (Tópicos em Pesquisa Operacional) |
| "Sibeli Russo" | Professora de estatística, muito ativa no LinkedIn e no YouTube, muito procurada. Provavelmente **Cibele Russo**, a "Profa. Cibele" já citada em `03-perguntas-em-aberto.md` **[conferir grafia]** |
| Francisco Louzada | Conhecido, difícil de conseguir como orientador pela demanda; segundo o aluno, mostrando certo cansaço com a docência |

Lembrete: o pré-projeto **não cita nem se dirige a nenhum docente** (regra do `CLAUDE.md`). Contato informal antes da seleção é outra coisa e não entra no texto.

**Encaixe com o tema.** O projeto é sobretudo de estatística (modelos de contagem, hierárquicos, subnotificação), com a extensão (f) de previsão e, no futuro, uma parte prescritiva (otimização de escala; ver `10-escala-de-motoristas.md`).
- A Profa. Maristela combina com a parte de otimização e logística.
- A parte central pede alguém de estatística.

## 6. Benefícios ao reingressar na USP

- Número USP e carteirinha reativados.
- Restaurante universitário a R$ 2.
- E-mail USP provavelmente reativável, mas sem as mensagens antigas.

## 7. Próximos passos

- [ ] **Felipe:** escrever para a Profa. Maristela Oliveira dos Santos.
- [ ] **Felipe:** visitar a USP São Carlos numa sexta à tarde.
- [ ] **Aluno:** mandar os e-mails dos docentes.
- [ ] **Decidir o tamanho do pré-projeto.** O relato indica cerca de 5 páginas, e o atual tem 17. O edital não limita, mas, se os avaliadores esperam algo curto, vale fazer uma versão enxuta (cerca de 5 a 8 páginas) e levar o estudo preliminar para um apêndice ou para o texto da dissertação.
- [ ] **Perguntar à secretaria:**
  - se o orientador é definido na matrícula (Anexo II do edital) ou uns 2 meses depois (relato do aluno);
  - se há limite de páginas para o projeto.
