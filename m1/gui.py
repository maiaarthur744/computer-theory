import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from typing import Optional
from passeio_cavalo import PasseioDoCavalo

class InterfacePasseio:
    def __init__(self, root):
        self.root = root
        self.root.title("Problema do Passeio do Cavalo")
        self.root.geometry("650x750")
        
        self.frame_controles = tk.Frame(root, pady=10)
        self.frame_controles.pack(fill=tk.X)
        
        frame_tabuleiro = tk.Frame(self.frame_controles)
        frame_tabuleiro.pack(pady=5)
        
        tk.Label(frame_tabuleiro, text="Tamanho (N):").grid(row=0, column=0, padx=5)
        self.entry_n = tk.Entry(frame_tabuleiro, width=5)
        self.entry_n.insert(0, "8")
        self.entry_n.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_tabuleiro, text="Início X:").grid(row=0, column=2, padx=5)
        self.entry_x = tk.Entry(frame_tabuleiro, width=5)
        self.entry_x.insert(0, "0")
        self.entry_x.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_tabuleiro, text="Início Y:").grid(row=0, column=4, padx=5)
        self.entry_y = tk.Entry(frame_tabuleiro, width=5)
        self.entry_y.insert(0, "0")
        self.entry_y.grid(row=0, column=5, padx=5)
        
        frame_algoritmo = tk.Frame(self.frame_controles)
        frame_algoritmo.pack(pady=5)
        
        tk.Label(frame_algoritmo, text="Algoritmo:").pack(side=tk.LEFT, padx=5)
        
        self.combo_algoritmo = ttk.Combobox(frame_algoritmo, state="readonly", width=20)
        self.combo_algoritmo['values'] = ("warnsdorff", "hibrido", "backtracking")
        self.combo_algoritmo.current(0)
        self.combo_algoritmo.pack(side=tk.LEFT, padx=5)
        
        self.btn_iniciar = tk.Button(frame_algoritmo, text="Resolver", command=self.iniciar_simulacao, bg="#4CAF50", fg="white")
        self.btn_iniciar.pack(side=tk.LEFT, padx=10)

        self.btn_cancelar = tk.Button(frame_algoritmo, text="Cancelar", command=self.cancelar_simulacao, state=tk.DISABLED, bg="#f44336", fg="white")
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = tk.Label(root, text="Aguardando configuração...", fg="blue", font=("Arial", 10, "bold"))
        self.lbl_status.pack(pady=5)
        
        self.tamanho_canvas = 500
        self.canvas = tk.Canvas(root, width=self.tamanho_canvas, height=self.tamanho_canvas, bg="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(pady=10)
        
        self.tamanho_celula = 0
        self.passo_atual_animacao = 0
        self.caminho_ordenado = {}
        self.passeio: Optional[PasseioDoCavalo] = None

    def iniciar_simulacao(self):
        try:
            n = int(self.entry_n.get())
            start_x = int(self.entry_x.get())
            start_y = int(self.entry_y.get())
            self.algoritmo_escolhido = self.combo_algoritmo.get()
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira apenas números inteiros.")
            return

        if n <= 4 and n != 1:
            messagebox.showwarning("Aviso", f"Não há solução possível para tabuleiros {n}x{n}.")
            return
        if not (0 <= start_x < n and 0 <= start_y < n):
            messagebox.showerror("Erro", "Posição inicial fora dos limites do tabuleiro.")
            return

        if self.algoritmo_escolhido == "backtracking" and n > 6:
            resposta = messagebox.askyesno("Cuidado", "O Backtracking puro cresce exponencialmente e pode travar por dias. Tem certeza?")
            if not resposta: return

        self.canvas.delete("all")
        self.tamanho_celula = self.tamanho_canvas / n
        self.desenhar_grade(n)
        
        self.lbl_status.config(text=f"Processando com {self.algoritmo_escolhido}...", fg="orange")
        
        self.btn_iniciar.config(state=tk.DISABLED)
        self.combo_algoritmo.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.NORMAL)
        
        self.passeio = PasseioDoCavalo(n, start_x, start_y)
        
        self.thread_processamento = threading.Thread(target=self._executar_algoritmo_em_background)
        self.thread_processamento.start()
        
        self.root.after(100, self._checar_fim_da_thread, n)

    def _executar_algoritmo_em_background(self):
        inicio_tempo = time.perf_counter()
        self.sucesso_calculo = self.passeio.resolver(algoritmo=self.algoritmo_escolhido)
        fim_tempo = time.perf_counter()
        self.tempo_calculo = fim_tempo - inicio_tempo

    def _checar_fim_da_thread(self, n):
        if self.thread_processamento.is_alive():
            self.root.after(100, self._checar_fim_da_thread, n)
        else:
            self.btn_cancelar.config(state=tk.DISABLED)
            
            if getattr(self.passeio, 'cancelado', False):
                self.lbl_status.config(text="Operação abortada pelo usuário.", fg="red")
                self.restaurar_interface()
            elif self.sucesso_calculo:
                texto_status = f"Concluído em {self.tempo_calculo:.4f}s | {self.passeio.avaliacoes} operações"
                self.lbl_status.config(text=texto_status, fg="green")
                self.preparar_animacao(n)
            else:
                self.lbl_status.config(text="Sem solução para esta posição/algoritmo.", fg="red")
                self.restaurar_interface()

    def cancelar_simulacao(self):
        if self.passeio:
            self.passeio.cancelado = True
            self.lbl_status.config(text="Cancelando... aguarde o encerramento da thread.", fg="red")
            self.btn_cancelar.config(state=tk.DISABLED)

    def restaurar_interface(self):
        self.btn_iniciar.config(state=tk.NORMAL)
        self.combo_algoritmo.config(state="readonly")

    def preparar_animacao(self, n):
        self.caminho_ordenado = {}
        for i in range(n):
            for j in range(n):
                if self.passeio.tabuleiro[i][j] != -1:
                    self.caminho_ordenado[self.passeio.tabuleiro[i][j]] = (i, j)
        
        self.passo_atual_animacao = 0
        self.animar_passo(n)

    def desenhar_grade(self, n):
        for i in range(n):
            for j in range(n):
                x1 = j * self.tamanho_celula
                y1 = i * self.tamanho_celula
                x2 = x1 + self.tamanho_celula
                y2 = y1 + self.tamanho_celula
                
                cor = "#DDBB99" if (i + j) % 2 == 0 else "#8B5A2B"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor, outline="black")

    def animar_passo(self, n):
        total_passos = n * n
        if self.passo_atual_animacao < total_passos:
            x, y = self.caminho_ordenado[self.passo_atual_animacao]
            
            x1 = y * self.tamanho_celula
            y1 = x * self.tamanho_celula
            x2 = x1 + self.tamanho_celula
            y2 = y1 + self.tamanho_celula
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#4CAF50", outline="black")
            
            centro_x = x1 + (self.tamanho_celula / 2)
            centro_y = y1 + (self.tamanho_celula / 2)
            fonte = max(8, int(self.tamanho_celula * 0.4)) 
            self.canvas.create_text(centro_x, centro_y, text=str(self.passo_atual_animacao), font=("Arial", fonte, "bold"), fill="white")
            
            self.passo_atual_animacao += 1
            self.root.after(50, lambda: self.animar_passo(n))
        else:
            self.restaurar_interface()
