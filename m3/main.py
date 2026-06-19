import math
import itertools
import random

def gerar_fachada_aleatoria(linhas: int, colunas: int, base_x: int, base_y: int, probabilidade: float = 0.5) -> list[tuple[int, int]]:
    """
    Gera as janelas sujas baseadas em um 'lance de moeda'.
    A posição inicial (base) é dinâmica e definida pelo usuário.
    """
    base: tuple[int, int] = (base_x, base_y)
    janelas_sujas: list[tuple[int, int]] = [base]
    
    for y in range(linhas):
        for x in range(colunas):
            if (x, y) != base:
                if random.random() < probabilidade:
                    janelas_sujas.append((x, y))
                    
    return janelas_sujas


def calcular_custo(janela1: tuple[int, int], janela2: tuple[int, int]) -> float:
    """
    Calcula o custo com:
    - Descidas (y2 > y1): 0.90x (menos custoso - aproveita gravidade)
    - Subidas (y2 < y1): 1.17x (mais custoso - gasto energético)
    - Horizontal: 1.0x (custo normal)
    """
    x1, y1 = janela1
    x2, y2 = janela2

    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    if y2 > y1:
        esforco_vertical = 0.90
    elif y2 < y1:
        esforco_vertical = 1.17
    else:
        esforco_vertical = 1.0

    return distancia * esforco_vertical


def calcular_custo_rota(rota: list[tuple[int, int]]) -> float:
    """Calcula o custo total de uma sequência, fechando o ciclo."""
    custo = 0.0
    for i in range(len(rota) - 1):
        custo += calcular_custo(rota[i], rota[i+1])
    return custo


def forca_bruta(janelas: list[tuple[int, int]], callback=None):
    """
    Força Bruta O(N!): Testa todas as permutações e retorna à base.
    """
    base = janelas[0]
    janelas_limpar = janelas[1:]

    melhor_rota = None
    menor_custo = float('inf')
    operacoes = 0
    total_rotas = math.factorial(len(janelas_limpar))
    passo_callback = max(1, total_rotas // 100)

    for permutacao in itertools.permutations(janelas_limpar):
        operacoes += 1
        rota_atual = [base] + list(permutacao) + [base]
        custo_atual = calcular_custo_rota(rota_atual)

        if custo_atual < menor_custo:
            menor_custo = custo_atual
            melhor_rota = rota_atual
        if callback and operacoes % passo_callback == 0:
            callback(operacoes, total_rotas) 
    if callback:
        callback(total_rotas, total_rotas)

    return melhor_rota, menor_custo, operacoes

def vizinho_mais_proximo(janelas: list[tuple[int, int]], callback=None):
    """
    Vizinho Mais Próximo O(N^2): Escolhe a mais próxima e no fim retorna à base.
    """
    base = janelas[0]
    nao_visitadas = set(janelas[1:])
    rota_atual = [base]
    operacoes = 0
    total_janelas = len(janelas) - 1

    while nao_visitadas:
        janela_atual = rota_atual[-1]

        proxima_janela = min(nao_visitadas, key=lambda j: calcular_custo(janela_atual, j))
        operacoes += len(nao_visitadas)

        rota_atual.append(proxima_janela)
        nao_visitadas.remove(proxima_janela)

        if callback:
            callback(total_janelas - len(nao_visitadas), total_janelas)

    rota_atual.append(base)
    custo_total = calcular_custo_rota(rota_atual)
    if callback:
        callback(total_janelas, total_janelas)

    return rota_atual, custo_total, operacoes

def otimizacao_2opt(rota_inicial: list[tuple[int, int]], callback=None):
    """
    Algoritmo de otimização local 2-Opt O(N^2).
    Desfaz cruzamentos invertendo segmentos da rota gerada pelo Vizinho Mais Próximo.
    """
    melhor_rota = rota_inicial[:]
    menor_custo = calcular_custo_rota(melhor_rota)
    operacoes = 0
    melhoria = True
    
    while melhoria:
        melhoria = False
        for i in range(1, len(melhor_rota) - 2):
            for j in range(i + 1, len(melhor_rota) - 1):
                operacoes += 1

                nova_rota = melhor_rota[:i] + melhor_rota[i:j+1][::-1] + melhor_rota[j+1:]
                custo_nova_rota = calcular_custo_rota(nova_rota)

                if custo_nova_rota < menor_custo - 0.0001:
                    menor_custo = custo_nova_rota
                    melhor_rota = nova_rota
                    melhoria = True
                    break
            if melhoria:
                break
                
    if callback:
        callback(1, 1)

    return melhor_rota, menor_custo, operacoes