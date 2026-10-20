# O problema: preço certo de um contrato

Fonte: `docs/enunciado/Instrucoes_Datathon_UFG.pdf`. As regras do evento estão em `docs/regras/REGRAS.md`.

## Contexto

Para disputar uma licitação, o Grupo HP (parceiro: SIAN) precisa projetar quanto custará prestar o serviço durante toda a vigência do contrato. Consideramos uma licitação de **3 anos**.

Esse preço depende de vários fatores, e os mais importantes são:

- a quantidade de integrantes;
- a rotatividade deles;
- a escala de trabalho.

O desafio tem **três trilhas**. Cada uma estima uma parte do custo que compõe o preço do contrato.

## O que cada trilha pede

### Trilha 1: Rotatividade

- **Objetivo:** encontrar a melhor estratégia para **projetar a rotatividade por empresa** ao longo da vigência do contrato.
- **Medida:** o enunciado define o turnover como

  `Turnover (%) = [ (Admissões + Rescisões) / 2 ] / Headcount × 100`

  - *Admissões:* integrantes que entraram ao final do período.
  - *Rescisões:* integrantes que saíram ao final do período.
  - *Headcount:* integrantes com vínculo durante o período.
- **Pergunta de fundo:** quantas pessoas vão entrar e sair. Isso gera custo de reposição e treinamento.
- **Dados principais:** `dim_integrante` (datas de admissão e demissão, motivo e categoria do desligamento, voluntário ou involuntário).

### Trilha 2: Folguistas e feristas

- **Objetivo:** encontrar a melhor estratégia para **dimensionar a quantidade de integrantes a mais** que cada empresa precisa para cobrir ausências por férias e atestados sem descumprir o contrato.
- **Por que existe:** o serviço precisa ser prestado todos os dias previstos, mesmo com o titular ausente. Faltas, atestados, afastamentos e férias retiram integrantes da operação, e cada ausência precisa ser coberta por outro integrante.
- **Dois tipos de ausência:**
  - *planejadas*, como as férias;
  - *sem aviso*, como faltas e atestados.
- **Pergunta de fundo:** como transformar o histórico em um quadro que mantenha o serviço sem sobrar nem faltar integrantes.
- **Dados principais:** `fBatidas` (minutos de falta, atraso, abono, hora extra e situação no dia) e `fAfastamentos`.

### Trilha 3: Escala 6x1 para 5x2

- **Objetivo:** encontrar a melhor estratégia para **dimensionar a quantidade de integrantes a mais** que cada empresa precisa **se a escala mudar de 6x1 para 5x2**.
- **Mecânica:**
  - na 6x1 o integrante trabalha seis dias e folga um;
  - na 5x2 trabalha cinco e folga dois.
  - Com mais folgas por integrante, manter o mesmo serviço exige um quadro maior.
- **Efeito colateral:** a mudança também pode alterar a rotatividade.
- **Dados principais:** `dim_horario` (escala de cada horário) e o ponto diário.

## As trilhas são interligadas?

**Em boa parte, sim.** O enunciado diz que as trilhas tratam de problemas diferentes, mas se conectam: cada uma estima uma parte do custo do contrato. Na prática, as três compõem um único modelo de dimensionamento de quadro por empresa.

| Relação | Por quê |
|---|---|
| **T3 depende da T2** | A cobertura das folgas extras do 5x2 se soma à cobertura das ausências da T2. |
| **T3 depende da T1** | O enunciado diz que a mudança de escala pode alterar a rotatividade. |
| **T2 e T1 se tocam** | Rotatividade alta gera vagas abertas e pessoas em treinamento. Os desligamentos também aparecem em `fAfastamentos`. |
| **Base comum** | As três usam os mesmos dados (vínculos, ponto, afastamentos) e a mesma unidade de análise: a empresa. |

Visão simplificada do quadro necessário por empresa:

> quadro base (dias a cobrir ÷ dias trabalháveis por pessoa) + folga de ausências (T2) + efeito do 5x2 (T3), ajustado pela reposição de quem sai (T1).

Cada trilha tem nota própria na avaliação, mas pode compartilhar a mesma estrutura de dados e de modelagem.

## Pontos em aberto

O enunciado não define os itens abaixo. Cada um precisa ser escolhido e justificado no relatório:

- se o quadro "a mais" é um número absoluto, um percentual sobre o quadro ou um valor por função;
- se a saída é por empresa, por mês ou por função, e em que formato;
- como evitar contar duas vezes a folga normal da escala como ausência (T2);
- como tratar o horizonte de 3 anos, já que o histórico de ponto cobre só 21 meses (01/01/2025 a 30/09/2026).

## Dados disponíveis

Os arquivos estão em `dados/`. Resumo conforme o enunciado:

| Tabela | O que é | Registros |
|---|---|---|
| `dim_integrante` | Cadastro de vínculos (empresa, filial, seção, função, horário, salário, datas, motivo de saída) | 20.001 vínculos de 18.617 integrantes |
| `fBatidas` | Ponto diário: minutos previstos, de falta, atraso, abono, trabalhados e hora extra | 601.474 linhas |
| `fAfastamentos` | Férias, afastamentos (doença, INSS, acidente, licenças) e desligamentos | 5.052 eventos |
| `dim_funcao`, `dim_horario`, `dim_secao`, `dim_empresa`, `dim_feriados`, `dim_situacao` e outras | Tabelas de apoio | – |

Observações do enunciado:

- O ponto diário e os afastamentos vão de **01/01/2025 a 30/09/2026**.
- O cadastro de vínculos traz o histórico completo: admissões desde 1969 e demissões até 13/10/2026.
- Um integrante que sai e é recontratado tem mais de um vínculo.
- Saída voluntária é quando o integrante pede para sair. Todos os outros casos são involuntários (decisão da empresa, fim de contrato, falecimento).
- Atestados de até 15 dias são pagos pela empresa. Acima disso, pelo INSS.
- O horário de cada integrante define a escala (6x1, 5x2, 12x36 e outras).
