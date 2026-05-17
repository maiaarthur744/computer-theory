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
    - Descidas (y2 > y1): 0.75x (menos custoso - aproveita gravidade)
    - Subidas (y2 < y1): 1.5x (mais custoso - gasto energético)
    - Horizontal: 1.0x (custo normal)
    """
    x1, y1 = janela1
    x2, y2 = janela2

    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    if y2 > y1:
        esforco_vertical = 0.75
    elif y2 < y1:
        esforco_vertical = 1.5
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
    callback: função(progresso, total) chamada a cada iteração para mostrar progresso
    """
    base = janelas[0]
    janelas_limpar = janelas[1:]

    melhor_rota = None
    menor_custo = float('inf')
    operacoes = 0

    permutacoes = list(itertools.permutations(janelas_limpar))
    total = len(permutacoes)

    for idx, permutacao in enumerate(permutacoes):
        operacoes += 1
        rota_atual = [base] + list(permutacao) + [base]
        custo_atual = calcular_custo_rota(rota_atual)

        if custo_atual < menor_custo:
            menor_custo = custo_atual
            melhor_rota = rota_atual

        if callback and idx % max(1, total // 100) == 0:
            callback(idx + 1, total)

    return melhor_rota, menor_custo, operacoes


def vizinho_mais_proximo(janelas: list[tuple[int, int]], callback=None):
    """
    Vizinho Mais Próximo O(N^2): Escolhe a mais próxima e no fim retorna à base.
    callback: função(progresso, total) chamada a cada passo
    """
    base = janelas[0]
    nao_visitadas = set(janelas[1:])
    rota_atual = [base]
    operacoes = 0
    total = len(janelas)

    while nao_visitadas:
        janela_atual = rota_atual[-1]

        proxima_janela = min(nao_visitadas, key=lambda j: calcular_custo(janela_atual, j))
        operacoes += len(nao_visitadas)

        rota_atual.append(proxima_janela)
        nao_visitadas.remove(proxima_janela)

        if callback:
            callback(len(rota_atual) - 1, total)

    rota_atual.append(base)
    custo_total = calcular_custo_rota(rota_atual)

    return rota_atual, custo_total, operacoes