# Sistema de Controle de Produção e Qualidade

Protótipo em Python para automação da inspeção de peças em linha de montagem, com empacotamento automático e geração de relatórios de lote.

**Trabalho de conclusão de módulo — Desafio de Automação Digital**
Disciplina: Algoritmos e Lógica de Programação
Curso: Inteligência Artificial e Automação Digital — UniFECAF
Autor: Samuel de Arruda
Orientadora: Prof.ª Patrícia Ampese

---

## Sobre o projeto

A inspeção manual de peças em linhas de montagem apresenta três limitações recorrentes: variação de critério entre operadores, ausência de registro estruturado do motivo de reprovação e custo de hora-homem dedicada a tarefa repetitiva.

Este sistema automatiza a camada de decisão do controle de qualidade. Cada peça produzida é avaliada contra três critérios objetivos, e o resultado é registrado com o motivo específico de eventual reprovação. As peças aprovadas são alocadas automaticamente em caixas de capacidade limitada, com fechamento e abertura de nova unidade sem intervenção do operador.

O projeto usa exclusivamente a biblioteca padrão do Python, sem dependências externas.

---

## Critérios de qualidade

Uma peça é aprovada apenas se atender aos **três** critérios simultaneamente. Basta um falhar para que a peça seja reprovada.

| Critério | Faixa aceita | Observação |
|---|---|---|
| Peso | 95g a 105g | Limites inclusivos |
| Cor | azul ou verde | Ignora maiúsculas e espaços extras |
| Comprimento | 10cm a 20cm | Limites inclusivos |

**Capacidade da caixa:** 10 peças aprovadas.

Os critérios são declarados como constantes no topo do arquivo. Alterar uma faixa exige mudar um único valor, sem tocar na lógica de validação.

---

## Como funciona

### Fluxo de processamento

```
Início
  ↓
Ler dados da peça (id, peso, cor, comprimento)
  ↓
Peça aprovada? ──não──→ Registrar reprovação com motivo detalhado
  │ sim
  ↓
Caixa cheia? ──sim──→ Fechar caixa e abrir nova unidade
  │ não                        │
  ↓←───────────────────────────┘
Inserir peça na caixa
  ↓
Há mais peças? ──sim──→ (volta ao início do laço)
  │ não
  ↓
Gerar relatório do lote
  ↓
Fim
```

### Decisões de projeto

**Validação sem interrupção antecipada.** Uma peça que falha em peso e cor devolve dois motivos, não apenas o primeiro encontrado. Isso permite ao operador corrigir todos os problemas de uma vez.

**Verificação de lotação antes da inserção.** Testar a capacidade depois de inserir produziria caixas com onze peças. Esse é um erro que não gera exceção e só aparece na conferência do resultado.

**Caixas como estrutura derivada.** As caixas não são armazenadas de forma independente. Elas são recalculadas a partir da lista de peças aprovadas sempre que o conjunto muda. Assim, remover uma peça já empacotada nunca deixa uma caixa com contagem inconsistente.

**Separação entre cálculo e exibição.** A função que consolida o relatório devolve uma estrutura de dados; a função que exibe recebe essa estrutura e formata. Isso permite trocar a saída no futuro (arquivo, API, interface gráfica) sem reescrever a lógica de negócio.

**Normalização da entrada de cor.** A operação real não entrega dado padronizado. `"Azul"`, `"AZUL"` e `" azul "` são tratados como o mesmo valor.

---

## Como rodar o programa

### Pré-requisitos

- **Python 3.8 ou superior** (o projeto não usa bibliotecas externas)

### Passo 1 — Verificar se o Python está instalado

Abra o terminal e execute:

```bash
python --version
```

Se aparecer algo como `Python 3.12.0`, está pronto. Se o comando não for reconhecido, tente `python3 --version`.

Caso não esteja instalado, baixe em [python.org/downloads](https://www.python.org/downloads/). No Windows, marque a opção **"Add Python to PATH"** durante a instalação.

### Passo 2 — Obter o código

**Opção A — clonar o repositório:**

```bash
git clone https://github.com/SEU-USUARIO/sistema-controle-qualidade.git
cd sistema-controle-qualidade
```

**Opção B — download direto:** baixe o arquivo `sistema_controle_qualidade.py` e salve em uma pasta de sua preferência.

### Passo 3 — Executar

```bash
python sistema_controle_qualidade.py
```

No Linux e macOS, use `python3` no lugar de `python`.

### Passo 4 — Usar o sistema

O menu aparece na tela. Digite o número da opção desejada e pressione ENTER.

Para uma demonstração rápida, escolha a **opção 6**, que carrega 16 peças de teste cobrindo aprovações, reprovações simples, reprovações múltiplas, valores exatamente nos limites e volume suficiente para fechar uma caixa completa.

---

## Menu de opções

```
  1 - Cadastrar nova peça
  2 - Listar peças aprovadas/reprovadas
  3 - Remover peça cadastrada
  4 - Listar caixas fechadas
  5 - Gerar relatório final
  6 - Carregar lote de demonstração
  0 - Sair
```

| Opção | Função |
|---|---|
| 1 | Solicita identificador, peso, cor e comprimento; avalia e informa o resultado com o motivo de eventual reprovação |
| 2 | Exibe todas as peças separadas em aprovadas e reprovadas, com os motivos detalhados |
| 3 | Lista as peças cadastradas, solicita o ID, pede confirmação e reorganiza as caixas após a remoção |
| 4 | Mostra o conteúdo de cada caixa fechada e o estado da caixa em preenchimento |
| 5 | Consolida o lote: totais, taxa de aprovação, contagem de caixas e reprovações agrupadas por critério |
| 6 | Carrega um lote de teste para demonstração rápida do sistema |
| 0 | Encerra a execução |

---

## Exemplos de entrada e saída

### Exemplo 1 — Cadastro de peça aprovada

**Entrada:**

```
  Identificador da peca (ex.: PC-001): PC-001
  Peso em gramas ...................: 100
  Cor ..............................: azul
  Comprimento em centimetros .......: 15
```

**Saída:**

```
----------------------------------------------------------------
  Peca PC-001 APROVADA e alocada na caixa 1.
----------------------------------------------------------------
```

### Exemplo 2 — Peça reprovada em um critério

**Entrada:**

```
  Identificador da peca (ex.: PC-001): PC-013
  Peso em gramas ...................: 88
  Cor ..............................: azul
  Comprimento em centimetros .......: 15
```

**Saída:**

```
----------------------------------------------------------------
  Peca PC-013 REPROVADA pelos seguintes motivos:
    - peso 88.0g fora da faixa (95g a 105g)
----------------------------------------------------------------
```

### Exemplo 3 — Peça reprovada em três critérios

**Entrada:**

```
  Identificador da peca (ex.: PC-001): PC-016
  Peso em gramas ...................: 120
  Cor ..............................: amarelo
  Comprimento em centimetros .......: 8
```

**Saída:**

```
----------------------------------------------------------------
  Peca PC-016 REPROVADA pelos seguintes motivos:
    - peso 120.0g fora da faixa (95g a 105g)
    - cor 'amarelo' nao permitida (aceitas: azul ou verde)
    - comprimento 8.0cm fora da faixa (10cm a 20cm)
----------------------------------------------------------------
```

### Exemplo 4 — Listagem de caixas (opção 4)

```
  CAIXAS FECHADAS (1)
----------------------------------------------------------------

  Caixa 1 - 10/10 pecas [FECHADA]
      PC-001       |  100.0g | azul     |  15.0cm
      PC-002       |   95.0g | verde    |  10.0cm
      PC-003       |  105.0g | AZUL     |  20.0cm
      PC-004       |   99.5g |  Verde   |  12.3cm
      PC-005       |  102.0g | azul     |  18.0cm
      PC-006       |   97.0g | verde    |  14.5cm
      PC-007       |  101.2g | azul     |  16.8cm
      PC-008       |   98.8g | verde    |  11.2cm
      PC-009       |  103.5g | azul     |  19.4cm
      PC-010       |   96.4g | verde    |  13.7cm

  CAIXA EM PREENCHIMENTO
----------------------------------------------------------------

  Caixa 2 - 2/10 pecas [ABERTA]
      PC-011       |  100.1g | azul     |  15.5cm
      PC-012       |   99.9g | verde    |  17.2cm

  Faltam 8 peca(s) para fechar esta caixa.
```

### Exemplo 5 — Relatório final (opção 5)

```
================================================================
                    RELATORIO FINAL DO LOTE
================================================================

  RESUMO GERAL
----------------------------------------------------------------
  Total de pecas processadas .... 16
  Pecas aprovadas ............... 12
  Pecas reprovadas .............. 4
  Taxa de aprovacao ............. 75.0%

  EMPACOTAMENTO
----------------------------------------------------------------
  Capacidade por caixa .......... 10 pecas
  Caixas fechadas ............... 1
  Caixa em preenchimento ........ 2 peca(s)
  Total de caixas utilizadas .... 2

  REPROVACOES POR CRITERIO
----------------------------------------------------------------
  Peso fora da faixa             2 ocorrencia(s)
  Cor nao permitida              2 ocorrencia(s)
  Comprimento fora da faixa      2 ocorrencia(s)

  DETALHAMENTO DAS REPROVADAS
----------------------------------------------------------------
  [ 13] PC-013       |   88.0g | azul     |  15.0cm | REPROVADA
        -> peso 88.0g fora da faixa (95g a 105g)
  [ 14] PC-014       |  100.0g | vermelho |  15.0cm | REPROVADA
        -> cor 'vermelho' nao permitida (aceitas: azul ou verde)
```

### Exemplo 6 — Remoção de peça (opção 3)

**Entrada:**

```
  Digite o ID da peca a remover (0 cancela): 1
  Confirma a remocao? (s/n): s
```

**Saída:**

```
----------------------------------------------------------------
  Peca PC-001 removida.
  Caixas reorganizadas. Total atual: 2 caixa(s).
----------------------------------------------------------------
```

---

## Estrutura do código

| Bloco | Funções | Responsabilidade |
|---|---|---|
| Constantes | — | Parâmetros de qualidade e capacidade |
| Validação | `validar_peso`, `validar_cor`, `validar_comprimento` | Um critério por função |
| Avaliação | `avaliar_peca` | Consolida os três critérios e acumula motivos |
| Empacotamento | `reorganizar_caixas`, `listar_caixas_fechadas`, `obter_caixa_aberta` | Controle de estado das caixas |
| Consolidação | `consolidar_relatorio`, `classificar_motivo` | Cálculo das estatísticas do lote |
| Exibição | `exibir_relatorio`, `exibir_peca`, `exibir_caixas` | Formatação da saída |
| Entrada | `ler_texto`, `ler_numero`, `ler_inteiro`, `confirmar` | Leitura validada do teclado |
| Menu | `exibir_menu`, `main` | Laço principal e roteamento das opções |

---

## Testes realizados

| Cenário | Resultado esperado | Status |
|---|---|---|
| Peça aprovada nos três critérios | Aprovada, sem motivos | OK |
| Peso exatamente 95g | Aprovada (limite inclusivo) | OK |
| Peso exatamente 105g | Aprovada (limite inclusivo) | OK |
| Peso 94.9g | Reprovada, 1 motivo | OK |
| Comprimento exatamente 10cm e 20cm | Aprovada (limites inclusivos) | OK |
| Cor em maiúsculas | Aprovada (normalização) | OK |
| Cor com espaços extras | Aprovada (normalização) | OK |
| Falha nos três critérios | Reprovada, 3 motivos | OK |
| Lote com 12 aprovadas | 1 caixa fechada, 1 aberta com 2 | OK |
| Remoção de peça empacotada | Caixas reorganizadas sem inconsistência | OK |
| Entrada de texto onde se espera número | Mensagem de erro, nova tentativa | OK |
| Lote vazio no relatório | Mensagem informativa, sem erro | OK |

---

## Limitações conhecidas

O protótipo mantém os dados em memória durante a execução. Ao encerrar o programa, o lote é perdido. Persistência em arquivo ou banco de dados está fora do escopo definido no plano de gerenciamento.

Não há integração com sensores físicos, sistemas ERP ou MES. A entrada é manual via terminal.

---

## Possível evolução

- Captura automática dos dados via balança digital, sensor dimensional e sensor colorimétrico
- Persistência em arquivo CSV ou banco de dados para análise histórica
- Integração com sistema MES para cruzar motivo de reprovação com parâmetros de máquina
- Camada preditiva capaz de alertar sobre deriva de processo antes da geração de refugo
