import time
import math
import tkinter as tk
from tkinter import messagebox, ttk

from main import gerar_fachada_aleatoria, forca_bruta, vizinho_mais_proximo, otimizacao_2opt

class AppLimpezaFachada:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Limpeza de Fachadas - Green Computing")
        self.root.geometry("950x750")

        self.fachada = []
        self.rota_fb = None
        self.rota_vmp = None
        self.rota_2opt = None
        self.linhas = 0
        self.colunas = 0

        self.setup_ui()

    def setup_ui(self):
        controle_frame = tk.Frame(self.root, padx=10, pady=10, width=320)
        controle_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(controle_frame, text="Configurações da Grade", font=("Arial", 12, "bold")).pack(pady=5)

        tk.Label(controle_frame, text="Linhas:").pack()
        self.ent_linhas = tk.Entry(controle_frame)
        self.ent_linhas.insert(0, "4")
        self.ent_linhas.pack(pady=2)

        tk.Label(controle_frame, text="Colunas:").pack()
        self.ent_colunas = tk.Entry(controle_frame)
        self.ent_colunas.insert(0, "4")
        self.ent_colunas.pack(pady=2)

        tk.Label(controle_frame, text="Base X:").pack()
        self.ent_base_x = tk.Entry(controle_frame)
        self.ent_base_x.insert(0, "0")
        self.ent_base_x.pack(pady=2)

        tk.Label(controle_frame, text="Base Y:").pack()
        self.ent_base_y = tk.Entry(controle_frame)
        self.ent_base_y.insert(0, "0")
        self.ent_base_y.pack(pady=2)

        tk.Button(controle_frame, text="Gerar e Calcular Rotas", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.executar_algoritmos).pack(pady=15, fill=tk.X)

        self.frame_progresso = tk.Frame(controle_frame)
        self.frame_progresso.pack(fill=tk.X, pady=5)
        
        self.lbl_progresso = tk.Label(self.frame_progresso, text="Aguardando execução...", font=("Arial", 9))
        self.lbl_progresso.pack()
        
        self.barra_progresso = ttk.Progressbar(self.frame_progresso, orient="horizontal", mode="determinate", length=200)
        self.barra_progresso.pack(fill=tk.X, pady=2)

        tk.Label(controle_frame, text="Visualização das Rotas", font=("Arial", 12, "bold")).pack(pady=10)

        self.btn_ver_vmp = tk.Button(controle_frame, text="1. Vizinho Mais Próximo", state=tk.DISABLED, command=lambda: self.desenhar_rota(self.rota_vmp, "blue"))
        self.btn_ver_vmp.pack(pady=5, fill=tk.X)

        self.btn_ver_2opt = tk.Button(controle_frame, text="2. Otimização 2-Opt", bg="#d4edda", state=tk.DISABLED, command=lambda: self.desenhar_rota(self.rota_2opt, "green"))
        self.btn_ver_2opt.pack(pady=5, fill=tk.X)

        self.btn_ver_fb = tk.Button(controle_frame, text="Força Bruta (Apenas < 10 janelas)", state=tk.DISABLED, command=lambda: self.desenhar_rota(self.rota_fb, "red"))
        self.btn_ver_fb.pack(pady=5, fill=tk.X)

        self.lbl_resultados = tk.Label(controle_frame, text="", justify=tk.LEFT, fg="#333", font=("Arial", 9))
        self.lbl_resultados.pack(pady=15, fill=tk.X)

        canvas_frame = tk.Frame(self.root, padx=10, pady=10)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def atualizar_progresso(self, prefixo, atual, total):
        """Atualiza a barra de progresso e força o Tkinter a redesenhar a tela."""
        percentual = (atual / total) * 100
        self.barra_progresso["value"] = percentual
        self.lbl_progresso.config(text=f"{prefixo}: {percentual:.1f}%")
        self.root.update()

    def executar_algoritmos(self):
        try:
            self.linhas = int(self.ent_linhas.get())
            self.colunas = int(self.ent_colunas.get())
            base_x = int(self.ent_base_x.get())
            base_y = int(self.ent_base_y.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores inteiros válidos.")
            return

        if not (0 <= base_x < self.colunas and 0 <= base_y < self.linhas):
            messagebox.showerror("Erro", "Coordenadas da base fora dos limites da grade.")
            return

        self.fachada = gerar_fachada_aleatoria(self.linhas, self.colunas, base_x, base_y)
        num_janelas = len(self.fachada)
        resultados_texto = f"Total de Janelas para Limpar: {num_janelas}\n"
        resultados_texto += "-"*40 + "\n"
        
        self.btn_ver_vmp.config(state=tk.DISABLED)
        self.btn_ver_2opt.config(state=tk.DISABLED)
        self.btn_ver_fb.config(state=tk.DISABLED)
        self.desenhar_grade()
        inicio = time.time()
        self.rota_vmp, custo_vmp, op_vmp = vizinho_mais_proximo(self.fachada,callback=lambda a, t: self.atualizar_progresso("Vizinho", a, t))
        tempo_vmp = time.time() - inicio
        resultados_texto += f"[Vizinho Mais Próximo]\nCusto: {custo_vmp:.2f}  |  Ops: {op_vmp}  |  {tempo_vmp:.4f}s\n\n"
        self.btn_ver_vmp.config(state=tk.NORMAL)

        inicio = time.time()
        self.rota_2opt, custo_2opt, op_2opt = otimizacao_2opt(self.rota_vmp,callback=lambda a, t: self.atualizar_progresso("2-Opt", a, t))
        tempo_2opt = time.time() - inicio
        resultados_texto += f"[Otimização 2-Opt]\nCusto: {custo_2opt:.2f}  |  Ops Extras: {op_2opt}  |  {tempo_2opt:.4f}s\n\n"
        self.btn_ver_2opt.config(state=tk.NORMAL)

        executar_fb = True
        if num_janelas > 10:
            qtd_rotas = math.factorial(num_janelas - 1)
            resposta = messagebox.askyesno("Aviso de Desempenho", 
                                           f"Atenção!\nVocê tem {num_janelas} janelas sujas.\n\n"
                                           f"A Força Bruta precisará testar {qtd_rotas:,} rotas diferentes.\n"
                                           f"Isso pode demorar bastante tempo consumindo muita CPU.\n\n"
                                           f"Deseja executar a Força Bruta mesmo assim?")
            if not resposta:
                executar_fb = False

        if executar_fb:
            self.root.config(cursor="watch") 
            inicio = time.time()
            self.rota_fb, custo_fb, op_fb = forca_bruta(self.fachada, callback=lambda a, t: self.atualizar_progresso("Força Bruta", a, t))
            tempo_fb = time.time() - inicio

            resultados_texto += f"[Força Bruta O(N!)]\nCusto: {custo_fb:.2f}  |  Ops: {op_fb}  |  {tempo_fb:.4f}s\n"
            self.btn_ver_fb.config(state=tk.NORMAL)
            self.root.config(cursor="")
        else:
            self.rota_fb = None
            resultados_texto += "[Força Bruta]\nIgnorado pelo usuário.\n"

        self.lbl_progresso.config(text="Cálculos concluídos!")
        self.barra_progresso["value"] = 100
        self.lbl_resultados.config(text=resultados_texto)

    def desenhar_grade(self):
        self.canvas.delete("all")
        if self.linhas == 0 or self.colunas == 0:
            return

        largura_canvas = self.canvas.winfo_width()
        altura_canvas = self.canvas.winfo_height()

        if largura_canvas <= 1:
            largura_canvas = 550
        if altura_canvas <= 1:
            altura_canvas = 600

        self.cell_w = min(largura_canvas / self.colunas, altura_canvas / self.linhas)
        self.cell_h = self.cell_w

        self.offset_x = (largura_canvas - (self.colunas * self.cell_w)) / 2
        self.offset_y = (altura_canvas - (self.linhas * self.cell_h)) / 2

        for y in range(self.linhas):
            for x in range(self.colunas):
                x0 = self.offset_x + x * self.cell_w
                y0 = self.offset_y + y * self.cell_h
                x1 = x0 + self.cell_w
                y1 = y0 + self.cell_h

                cor_fundo = "#e0e0e0"
                if (x, y) == self.fachada[0]:
                    cor_fundo = "#ffd700"
                elif (x, y) in self.fachada:
                    cor_fundo = "#8b4513"

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=cor_fundo, outline="white")

                self.canvas.create_text(x0 + self.cell_w/2, y0 + self.cell_h/2, text=f"({x},{y})", fill="#555")

        self.canvas.create_text(10, 10, anchor=tk.NW, text="Amarelo: Base | Marrom: Suja | Cinza: Limpa", font=("Arial", 9, "bold"))

    def desenhar_rota(self, rota, cor):
        self.desenhar_grade()
        if not rota:
            return

        for i in range(len(rota) - 1):
            x1, y1 = rota[i]
            x2, y2 = rota[i+1]

            px1 = self.offset_x + x1 * self.cell_w + self.cell_w / 2
            py1 = self.offset_y + y1 * self.cell_h + self.cell_h / 2
            px2 = self.offset_x + x2 * self.cell_w + self.cell_w / 2
            py2 = self.offset_y + y2 * self.cell_h + self.cell_h / 2

            if i % 2 == 0:
                self.canvas.create_line(px1, py1, px2, py2, fill=cor, width=3, arrow=tk.LAST, dash=(5, 2))
            else:
                self.canvas.create_line(px1, py1, px2, py2, fill=cor, width=3, arrow=tk.LAST)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLimpezaFachada(root)
    root.mainloop()