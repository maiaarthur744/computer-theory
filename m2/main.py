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
    Calcula o custo considerando distância euclidiana e um peso maior (50%)
    para movimentos verticais de subida simulando gasto energético.
    """
    x1, y1 = janela1
    x2, y2 = janela2
    
    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    esforco_vertical = 1.5 if y2 > y1 else 1.0 
    
    return distancia * esforco_vertical


def calcular_custo_rota(rota: list[tuple[int, int]]) -> float:
    """Calcula o custo total de uma sequência, fechando o ciclo."""
    custo = 0.0
    for i in range(len(rota) - 1):
        custo += calcular_custo(rota[i], rota[i+1])
    return custo


def forca_bruta(janelas: list[tuple[int, int]]):
    """
    Força Bruta O(N!): Testa todas as permutações e retorna à base.
    """
    base = janelas[0]
    janelas_limpar = janelas[1:]
    
    melhor_rota = None
    menor_custo = float('inf')
    operacoes = 0
    
    for permutacao in itertools.permutations(janelas_limpar):
        operacoes += 1
        rota_atual = [base] + list(permutacao) + [base]
        custo_atual = calcular_custo_rota(rota_atual)
        
        if custo_atual < menor_custo:
            menor_custo = custo_atual
            melhor_rota = rota_atual
            
    return melhor_rota, menor_custo, operacoes


def vizinho_mais_proximo(janelas: list[tuple[int, int]]):
    """
    Vizinho Mais Próximo O(N^2): Escolhe a mais próxima e no fim retorna à base.
    """
    base = janelas[0]
    nao_visitadas = set(janelas[1:])
    rota_atual = [base]
    operacoes = 0
    
    while nao_visitadas:
        janela_atual = rota_atual[-1]
        
        # Encontra a janela mais barata a partir da atual
        proxima_janela = min(nao_visitadas, key=lambda j: calcular_custo(janela_atual, j))
        operacoes += len(nao_visitadas)
        
        rota_atual.append(proxima_janela)
        nao_visitadas.remove(proxima_janela)
        
    # Retorna para a base fechando o ciclo
    rota_atual.append(base)
    custo_total = calcular_custo_rota(rota_atual)
    
    return rota_atual, custo_total, operacoes