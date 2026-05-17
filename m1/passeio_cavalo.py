class PasseioDoCavalo:
    def __init__(self, n, start_x, start_y):
        self.n = n
        self.tabuleiro = [[-1 for _ in range(n)] for _ in range(n)]
        
        self.movimentos_x = [2, 1, -1, -2, -2, -1, 1, 2]
        self.movimentos_y = [1, 2, 2, 1, -1, -2, -2, -1]
        
        self.pos_atual_x = start_x
        self.pos_atual_y = start_y
        
        self.tabuleiro[self.pos_atual_x][self.pos_atual_y] = 0

        self.avaliacoes = 0

        self.cancelado = False

    def movimento_valido(self, x, y):
        self.avaliacoes += 1
        return (0 <= x < self.n) and (0 <= y < self.n) and (self.tabuleiro[x][y] == -1)

    def contar_movimentos_futuros(self, x, y):
        count = 0
        for i in range(8):
            prox_x = x + self.movimentos_x[i]
            prox_y = y + self.movimentos_y[i]
            if self.movimento_valido(prox_x, prox_y):
                count += 1
        return count

    def resolver_warnsdorff_guloso(self):
        total_casas = self.n * self.n
        for passo in range(1, total_casas):
            if self.cancelado: return False 
            
            min_futuros = 9 
            melhor_x, melhor_y = -1, -1
        
            for i in range(8):
                prox_x = self.pos_atual_x + self.movimentos_x[i]
                prox_y = self.pos_atual_y + self.movimentos_y[i]
                
                if self.movimento_valido(prox_x, prox_y):
                    futuros = self.contar_movimentos_futuros(prox_x, prox_y)

                    if futuros < min_futuros:
                        min_futuros = futuros
                        melhor_x, melhor_y = prox_x, prox_y
                        
            if min_futuros == 9:
                return False
                
            self.pos_atual_x = melhor_x
            self.pos_atual_y = melhor_y
            self.tabuleiro[melhor_x][melhor_y] = passo
            
        return True

    def resolver_backtracking(self, passo, x, y):
        if self.cancelado: return False 
        
        if passo == self.n * self.n:
            return True
            
        for i in range(8):
            prox_x = x + self.movimentos_x[i]
            prox_y = y + self.movimentos_y[i]
            
            if self.movimento_valido(prox_x, prox_y):
                self.tabuleiro[prox_x][prox_y] = passo
                
                if self.resolver_backtracking(passo + 1, prox_x, prox_y):
                    return True
                    
                self.tabuleiro[prox_x][prox_y] = -1
                
        return False

    # ALGORITMO 3: HÍBRIDO (Backtracking + Warnsdorff)
    def resolver_hibrido(self, passo, x, y):
        if self.cancelado: return False 
        
        if passo == self.n * self.n:
            return True
            
        movimentos_possiveis = []
        for i in range(8):
            prox_x = x + self.movimentos_x[i]
            prox_y = y + self.movimentos_y[i]
            
            if self.movimento_valido(prox_x, prox_y):
                futuros = self.contar_movimentos_futuros(prox_x, prox_y)
                movimentos_possiveis.append((futuros, prox_x, prox_y))
                
        movimentos_possiveis.sort(key=lambda item: item[0])
        
        for _, prox_x, prox_y in movimentos_possiveis:
            self.tabuleiro[prox_x][prox_y] = passo
            if self.resolver_hibrido(passo + 1, prox_x, prox_y):
                return True
            self.tabuleiro[prox_x][prox_y] = -1
            
        return False

    def resolver(self, algoritmo="warnsdorff"):
        if algoritmo == "warnsdorff":
            return self.resolver_warnsdorff_guloso()
        elif algoritmo == "backtracking":
            return self.resolver_backtracking(1, self.pos_atual_x, self.pos_atual_y)
        elif algoritmo == "hibrido":
            return self.resolver_hibrido(1, self.pos_atual_x, self.pos_atual_y)
        return False