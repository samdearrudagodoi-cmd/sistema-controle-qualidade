"""
Sistema de controle de producao e qualidade para linha de montagem.

Trabalho de conclusao de modulo - Desafio de Automacao Digital
Disciplina: Algoritmos e Logica de Programacao
Curso: Inteligencia Artificial e Automacao Digital - UniFECAF
Autor: Samuel de Arruda
Orientadora: Prof.a Patricia Ampese

O sistema recebe os dados de cada peca produzida, avalia automaticamente
sua conformidade contra tres criterios de qualidade, registra o motivo
especifico de cada reprovacao, aloca as pecas aprovadas em caixas de
capacidade limitada e gera relatorio consolidado do lote.

Desenvolvido sem dependencias externas: usa apenas a biblioteca padrao.
"""

# =============================================================================
# A1 - CONSTANTES DE CONFIGURACAO
# =============================================================================
# Os criterios de qualidade ficam centralizados aqui. Alterar uma faixa
# exige mudar um unico valor, sem tocar na logica de validacao.

PESO_MINIMO = 95.0        # gramas
PESO_MAXIMO = 105.0       # gramas
COMPRIMENTO_MINIMO = 10.0  # centimetros
COMPRIMENTO_MAXIMO = 20.0  # centimetros
CORES_ACEITAS = ("azul", "verde")
CAPACIDADE_CAIXA = 10      # pecas por caixa

LARGURA_TELA = 64          # largura padrao para formatacao da saida


# =============================================================================
# ESTADO DA APLICACAO
# =============================================================================
# As pecas sao a unica fonte de verdade. As caixas sao estrutura derivada:
# sao recalculadas a partir das aprovadas sempre que o conjunto muda.
# Isso garante que uma remocao nunca deixe uma caixa com contagem invalida.

pecas_cadastradas = []
caixas = []
proximo_id = 1


# =============================================================================
# A2 - FUNCOES DE VALIDACAO POR CRITERIO
# =============================================================================
# Cada funcao responde por um unico criterio. Alterar a faixa de peso nao
# exige tocar na regra de cor, e vice-versa.

def validar_peso(peso):
    """Verifica se o peso esta dentro da faixa aceita, com limites inclusivos.

    Parametros:
        peso (float): peso da peca em gramas

    Retorna:
        bool: True se o peso for valido
    """
    return PESO_MINIMO <= peso <= PESO_MAXIMO


def validar_cor(cor):
    """Verifica se a cor pertence ao conjunto de cores aceitas.

    A comparacao e normalizada para tolerar variacoes de digitacao
    como maiusculas e espacos extras.

    Parametros:
        cor (str): cor informada da peca

    Retorna:
        bool: True se a cor for aceita
    """
    return normalizar_texto(cor) in CORES_ACEITAS


def validar_comprimento(comprimento):
    """Verifica se o comprimento esta na faixa aceita, com limites inclusivos.

    Parametros:
        comprimento (float): comprimento da peca em centimetros

    Retorna:
        bool: True se o comprimento for valido
    """
    return COMPRIMENTO_MINIMO <= comprimento <= COMPRIMENTO_MAXIMO


def normalizar_texto(texto):
    """Remove espacos nas extremidades e converte para minusculas.

    Parametros:
        texto (str): texto a normalizar

    Retorna:
        str: texto normalizado
    """
    return texto.strip().lower()


# =============================================================================
# A3 - FUNCAO ORQUESTRADORA DE AVALIACAO
# =============================================================================

def avaliar_peca(peso, cor, comprimento):
    """Avalia os tres criterios de qualidade e acumula todos os motivos.

    A validacao nao interrompe no primeiro criterio reprovado. Uma peca
    que falha em peso e cor devolve dois motivos, nao apenas o primeiro.

    Parametros:
        peso (float): peso em gramas
        cor (str): cor informada
        comprimento (float): comprimento em centimetros

    Retorna:
        tuple: (aprovada, motivos) onde aprovada e bool e motivos e list
    """
    motivos = []

    if not validar_peso(peso):
        motivos.append(
            f"peso {peso:.1f}g fora da faixa "
            f"({PESO_MINIMO:.0f}g a {PESO_MAXIMO:.0f}g)"
        )

    if not validar_cor(cor):
        cores = " ou ".join(CORES_ACEITAS)
        motivos.append(f"cor '{cor}' nao permitida (aceitas: {cores})")

    if not validar_comprimento(comprimento):
        motivos.append(
            f"comprimento {comprimento:.1f}cm fora da faixa "
            f"({COMPRIMENTO_MINIMO:.0f}cm a {COMPRIMENTO_MAXIMO:.0f}cm)"
        )

    aprovada = len(motivos) == 0
    return aprovada, motivos


# =============================================================================
# A4 - CONTROLE DE EMPACOTAMENTO
# =============================================================================

def reorganizar_caixas():
    """Reconstroi as caixas a partir das pecas aprovadas, em ordem de cadastro.

    As caixas sao derivadas das pecas, nao armazenadas de forma independente.
    Assim, uma remocao nunca deixa uma caixa com contagem inconsistente.

    A verificacao de lotacao ocorre antes da insercao. Verificar depois
    produziria caixas com uma peca alem da capacidade.
    """
    global caixas
    caixas = []
    caixa_atual = []

    for peca in pecas_cadastradas:
        if not peca["aprovada"]:
            continue

        if len(caixa_atual) >= CAPACIDADE_CAIXA:
            caixas.append(caixa_atual)
            caixa_atual = []

        caixa_atual.append(peca)

    if caixa_atual:
        caixas.append(caixa_atual)


def listar_caixas_fechadas():
    """Retorna apenas as caixas que atingiram a capacidade maxima.

    Retorna:
        list: lista de caixas fechadas
    """
    return [caixa for caixa in caixas if len(caixa) == CAPACIDADE_CAIXA]


def obter_caixa_aberta():
    """Retorna a caixa em preenchimento, se houver.

    Retorna:
        list: caixa aberta, ou lista vazia se nao houver
    """
    if caixas and len(caixas[-1]) < CAPACIDADE_CAIXA:
        return caixas[-1]
    return []


# =============================================================================
# A5 - CONSOLIDACAO DO RELATORIO
# =============================================================================
# A funcao que calcula nao imprime. A funcao que imprime nao calcula.
# Isso permite trocar a saida no futuro sem reescrever a logica.

def consolidar_relatorio():
    """Calcula os dados consolidados do lote processado.

    Retorna:
        dict: estrutura com totais, listas e indicadores do lote
    """
    aprovadas = [p for p in pecas_cadastradas if p["aprovada"]]
    reprovadas = [p for p in pecas_cadastradas if not p["aprovada"]]

    contagem_motivos = {}
    for peca in reprovadas:
        for motivo in peca["motivos"]:
            chave = classificar_motivo(motivo)
            contagem_motivos[chave] = contagem_motivos.get(chave, 0) + 1

    total = len(pecas_cadastradas)
    taxa_aprovacao = (len(aprovadas) / total * 100) if total > 0 else 0.0

    return {
        "total": total,
        "aprovadas": aprovadas,
        "reprovadas": reprovadas,
        "contagem_motivos": contagem_motivos,
        "taxa_aprovacao": taxa_aprovacao,
        "caixas_fechadas": listar_caixas_fechadas(),
        "caixa_aberta": obter_caixa_aberta(),
        "total_caixas": len(caixas),
    }


def classificar_motivo(motivo):
    """Extrai a categoria do criterio a partir do texto do motivo.

    Usado para agrupar as reprovacoes por tipo no relatorio consolidado.

    Parametros:
        motivo (str): texto completo do motivo

    Retorna:
        str: categoria do criterio reprovado
    """
    if motivo.startswith("peso"):
        return "Peso fora da faixa"
    if motivo.startswith("cor"):
        return "Cor nao permitida"
    return "Comprimento fora da faixa"


# =============================================================================
# A6 - EXIBICAO FORMATADA
# =============================================================================

def linha(caractere="-"):
    """Imprime uma linha divisoria na largura padrao da tela."""
    print(caractere * LARGURA_TELA)


def titulo(texto):
    """Imprime um cabecalho de secao formatado."""
    print()
    linha("=")
    print(texto.center(LARGURA_TELA))
    linha("=")


def exibir_peca(peca):
    """Imprime uma peca em linha unica, com status e motivos."""
    status = "APROVADA" if peca["aprovada"] else "REPROVADA"
    print(
        f"  [{peca['id']:>3}] {peca['identificador']:<12} | "
        f"{peca['peso']:>6.1f}g | {peca['cor']:<8} | "
        f"{peca['comprimento']:>5.1f}cm | {status}"
    )
    for motivo in peca["motivos"]:
        print(f"        -> {motivo}")


def exibir_relatorio(dados):
    """Imprime o relatorio consolidado do lote.

    Parametros:
        dados (dict): estrutura devolvida por consolidar_relatorio()
    """
    titulo("RELATORIO FINAL DO LOTE")

    if dados["total"] == 0:
        print("\n  Nenhuma peca cadastrada ate o momento.\n")
        return

    print("\n  RESUMO GERAL")
    linha()
    print(f"  Total de pecas processadas .... {dados['total']}")
    print(f"  Pecas aprovadas ............... {len(dados['aprovadas'])}")
    print(f"  Pecas reprovadas .............. {len(dados['reprovadas'])}")
    print(f"  Taxa de aprovacao ............. {dados['taxa_aprovacao']:.1f}%")

    print("\n  EMPACOTAMENTO")
    linha()
    print(f"  Capacidade por caixa .......... {CAPACIDADE_CAIXA} pecas")
    print(f"  Caixas fechadas ............... {len(dados['caixas_fechadas'])}")
    print(f"  Caixa em preenchimento ........ "
          f"{len(dados['caixa_aberta'])} peca(s)")
    print(f"  Total de caixas utilizadas .... {dados['total_caixas']}")

    if dados["reprovadas"]:
        print("\n  REPROVACOES POR CRITERIO")
        linha()
        for criterio, quantidade in sorted(
            dados["contagem_motivos"].items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            print(f"  {criterio:<30} {quantidade} ocorrencia(s)")

        print("\n  DETALHAMENTO DAS REPROVADAS")
        linha()
        for peca in dados["reprovadas"]:
            exibir_peca(peca)

    print()
    linha("=")
    print()


# =============================================================================
# ENTRADA DE DADOS COM VALIDACAO
# =============================================================================
# input() sempre devolve texto. Converter sem tratamento quebra o programa
# quando o operador digita algo invalido.

def ler_texto(rotulo):
    """Le um texto obrigatorio, repetindo ate receber conteudo valido."""
    while True:
        valor = input(rotulo).strip()
        if valor:
            return valor
        print("  Campo obrigatorio. Digite um valor.")


def ler_numero(rotulo):
    """Le um numero decimal, aceitando virgula ou ponto como separador."""
    while True:
        entrada = input(rotulo).strip().replace(",", ".")
        try:
            valor = float(entrada)
        except ValueError:
            print("  Valor invalido. Digite um numero (ex.: 98.5).")
            continue

        if valor <= 0:
            print("  O valor deve ser maior que zero.")
            continue

        return valor


def ler_inteiro(rotulo):
    """Le um numero inteiro, repetindo ate receber valor valido."""
    while True:
        entrada = input(rotulo).strip()
        try:
            return int(entrada)
        except ValueError:
            print("  Valor invalido. Digite um numero inteiro.")


def confirmar(rotulo):
    """Solicita confirmacao do usuario e devolve True para resposta positiva."""
    resposta = normalizar_texto(input(rotulo))
    return resposta in ("s", "sim", "y", "yes")


# =============================================================================
# OPCAO 1 - CADASTRAR NOVA PECA
# =============================================================================

def cadastrar_peca():
    """Coleta os dados de uma peca, avalia e registra o resultado."""
    global proximo_id

    titulo("CADASTRAR NOVA PECA")
    print()

    identificador = ler_texto("  Identificador da peca (ex.: PC-001): ")
    peso = ler_numero("  Peso em gramas ...................: ")
    cor = ler_texto("  Cor ..............................: ")
    comprimento = ler_numero("  Comprimento em centimetros .......: ")

    aprovada, motivos = avaliar_peca(peso, cor, comprimento)

    peca = {
        "id": proximo_id,
        "identificador": identificador,
        "peso": peso,
        "cor": cor,
        "comprimento": comprimento,
        "aprovada": aprovada,
        "motivos": motivos,
    }

    pecas_cadastradas.append(peca)
    proximo_id += 1
    reorganizar_caixas()

    print()
    linha()
    if aprovada:
        print(f"  Peca {identificador} APROVADA e alocada na caixa "
              f"{len(caixas)}.")
        if len(caixas[-1]) == CAPACIDADE_CAIXA:
            print(f"  Caixa {len(caixas)} atingiu a capacidade e foi fechada.")
    else:
        print(f"  Peca {identificador} REPROVADA pelos seguintes motivos:")
        for motivo in motivos:
            print(f"    - {motivo}")
    linha()


# =============================================================================
# OPCAO 2 - LISTAR PECAS APROVADAS E REPROVADAS
# =============================================================================

def listar_pecas():
    """Exibe as pecas cadastradas separadas por status de aprovacao."""
    titulo("PECAS CADASTRADAS")

    if not pecas_cadastradas:
        print("\n  Nenhuma peca cadastrada ate o momento.\n")
        return

    aprovadas = [p for p in pecas_cadastradas if p["aprovada"]]
    reprovadas = [p for p in pecas_cadastradas if not p["aprovada"]]

    print(f"\n  APROVADAS ({len(aprovadas)})")
    linha()
    if aprovadas:
        for peca in aprovadas:
            exibir_peca(peca)
    else:
        print("  Nenhuma peca aprovada.")

    print(f"\n  REPROVADAS ({len(reprovadas)})")
    linha()
    if reprovadas:
        for peca in reprovadas:
            exibir_peca(peca)
    else:
        print("  Nenhuma peca reprovada.")

    print()


# =============================================================================
# OPCAO 3 - REMOVER PECA CADASTRADA
# =============================================================================

def buscar_peca_por_id(id_peca):
    """Localiza uma peca pelo seu id sequencial.

    Retorna:
        dict ou None: a peca encontrada, ou None se nao existir
    """
    for peca in pecas_cadastradas:
        if peca["id"] == id_peca:
            return peca
    return None


def remover_peca():
    """Remove uma peca cadastrada e reorganiza as caixas."""
    titulo("REMOVER PECA CADASTRADA")

    if not pecas_cadastradas:
        print("\n  Nenhuma peca cadastrada para remover.\n")
        return

    print("\n  Pecas disponiveis:")
    linha()
    for peca in pecas_cadastradas:
        exibir_peca(peca)

    print()
    id_peca = ler_inteiro("  Digite o ID da peca a remover (0 cancela): ")

    if id_peca == 0:
        print("\n  Operacao cancelada.\n")
        return

    peca = buscar_peca_por_id(id_peca)

    if peca is None:
        print(f"\n  Nenhuma peca encontrada com o ID {id_peca}.\n")
        return

    print(f"\n  Peca selecionada: {peca['identificador']} "
          f"({'aprovada' if peca['aprovada'] else 'reprovada'})")

    if not confirmar("  Confirma a remocao? (s/n): "):
        print("\n  Operacao cancelada.\n")
        return

    pecas_cadastradas.remove(peca)
    reorganizar_caixas()

    print()
    linha()
    print(f"  Peca {peca['identificador']} removida.")
    if peca["aprovada"]:
        print(f"  Caixas reorganizadas. Total atual: {len(caixas)} caixa(s).")
    linha()
    print()


# =============================================================================
# OPCAO 4 - LISTAR CAIXAS FECHADAS
# =============================================================================

def exibir_caixas():
    """Exibe as caixas fechadas e a caixa em preenchimento."""
    titulo("CAIXAS")

    fechadas = listar_caixas_fechadas()
    aberta = obter_caixa_aberta()

    if not caixas:
        print("\n  Nenhuma caixa criada. Cadastre pecas aprovadas.\n")
        return

    print(f"\n  CAIXAS FECHADAS ({len(fechadas)})")
    linha()

    if fechadas:
        for indice, caixa in enumerate(fechadas, start=1):
            print(f"\n  Caixa {indice} - {len(caixa)}/{CAPACIDADE_CAIXA} "
                  f"pecas [FECHADA]")
            for peca in caixa:
                print(f"      {peca['identificador']:<12} | "
                      f"{peca['peso']:>6.1f}g | {peca['cor']:<8} | "
                      f"{peca['comprimento']:>5.1f}cm")
    else:
        print("  Nenhuma caixa fechada ate o momento.")

    if aberta:
        print(f"\n  CAIXA EM PREENCHIMENTO")
        linha()
        print(f"\n  Caixa {len(caixas)} - {len(aberta)}/{CAPACIDADE_CAIXA} "
              f"pecas [ABERTA]")
        for peca in aberta:
            print(f"      {peca['identificador']:<12} | "
                  f"{peca['peso']:>6.1f}g | {peca['cor']:<8} | "
                  f"{peca['comprimento']:>5.1f}cm")
        restante = CAPACIDADE_CAIXA - len(aberta)
        print(f"\n  Faltam {restante} peca(s) para fechar esta caixa.")

    print()


# =============================================================================
# OPCAO 5 - GERAR RELATORIO FINAL
# =============================================================================

def gerar_relatorio():
    """Consolida e exibe o relatorio final do lote."""
    dados = consolidar_relatorio()
    exibir_relatorio(dados)


# =============================================================================
# OPCAO 6 - LOTE DE DEMONSTRACAO
# =============================================================================

def carregar_lote_demonstracao():
    """Carrega um conjunto de pecas de teste para demonstracao rapida.

    O lote cobre os casos previstos na bateria de testes: aprovacao,
    reprovacao simples, reprovacao multipla, valores exatamente nos
    limites e volume suficiente para fechar mais de uma caixa.
    """
    global proximo_id

    titulo("CARREGAR LOTE DE DEMONSTRACAO")

    if pecas_cadastradas:
        print("\n  Ja existem pecas cadastradas.")
        if not confirmar("  Deseja adicionar o lote mesmo assim? (s/n): "):
            print("\n  Operacao cancelada.\n")
            return

    lote = [
        ("PC-001", 100.0, "azul", 15.0),
        ("PC-002", 95.0, "verde", 10.0),
        ("PC-003", 105.0, "AZUL", 20.0),
        ("PC-004", 99.5, " Verde ", 12.3),
        ("PC-005", 102.0, "azul", 18.0),
        ("PC-006", 97.0, "verde", 14.5),
        ("PC-007", 101.2, "azul", 16.8),
        ("PC-008", 98.8, "verde", 11.2),
        ("PC-009", 103.5, "azul", 19.4),
        ("PC-010", 96.4, "verde", 13.7),
        ("PC-011", 100.1, "azul", 15.5),
        ("PC-012", 99.9, "verde", 17.2),
        ("PC-013", 88.0, "azul", 15.0),
        ("PC-014", 100.0, "vermelho", 15.0),
        ("PC-015", 100.0, "azul", 25.0),
        ("PC-016", 120.0, "amarelo", 8.0),
    ]

    for identificador, peso, cor, comprimento in lote:
        aprovada, motivos = avaliar_peca(peso, cor, comprimento)
        pecas_cadastradas.append({
            "id": proximo_id,
            "identificador": identificador,
            "peso": peso,
            "cor": cor,
            "comprimento": comprimento,
            "aprovada": aprovada,
            "motivos": motivos,
        })
        proximo_id += 1

    reorganizar_caixas()

    aprovadas = len([p for p in pecas_cadastradas if p["aprovada"]])
    print(f"\n  {len(lote)} pecas carregadas.")
    print(f"  Aprovadas: {aprovadas} | "
          f"Reprovadas: {len(pecas_cadastradas) - aprovadas}")
    print(f"  Caixas criadas: {len(caixas)} "
          f"({len(listar_caixas_fechadas())} fechada(s))")
    print()


# =============================================================================
# MENU INTERATIVO
# =============================================================================

def exibir_menu():
    """Imprime o menu principal e os criterios de qualidade vigentes."""
    titulo("SISTEMA DE CONTROLE DE PRODUCAO E QUALIDADE")
    print()
    print(f"  Criterios: peso {PESO_MINIMO:.0f}-{PESO_MAXIMO:.0f}g | "
          f"cor {'/'.join(CORES_ACEITAS)} | "
          f"comprimento {COMPRIMENTO_MINIMO:.0f}-{COMPRIMENTO_MAXIMO:.0f}cm")
    print(f"  Pecas cadastradas: {len(pecas_cadastradas)} | "
          f"Caixas: {len(caixas)}")
    print()
    linha()
    print("  1 - Cadastrar nova peca")
    print("  2 - Listar pecas aprovadas/reprovadas")
    print("  3 - Remover peca cadastrada")
    print("  4 - Listar caixas fechadas")
    print("  5 - Gerar relatorio final")
    print("  6 - Carregar lote de demonstracao")
    print("  0 - Sair")
    linha()


def main():
    """Laco principal do menu interativo."""
    opcoes = {
        "1": cadastrar_peca,
        "2": listar_pecas,
        "3": remover_peca,
        "4": exibir_caixas,
        "5": gerar_relatorio,
        "6": carregar_lote_demonstracao,
    }

    while True:
        exibir_menu()
        opcao = input("\n  Escolha uma opcao: ").strip()

        if opcao == "0":
            print("\n  Encerrando o sistema. Ate logo.\n")
            break

        acao = opcoes.get(opcao)

        if acao is None:
            print("\n  Opcao invalida. Escolha um numero de 0 a 6.\n")
            continue

        acao()
        input("  Pressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    main()
