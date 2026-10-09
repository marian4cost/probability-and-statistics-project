import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import seaborn as sns

# Configuração visual profissional para o Matplotlib / Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.sans-serif": "DejaVu Sans",
        "axes.edgecolor": "#CCCCCC",
        "axes.linewidth": 1.1,
    }
)


class Application(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Análise Estatística Descritiva - Consumo Audiovisual (BSI / IFS)")
        self.geometry("1180x800")
        self.configure(bg="#F4F6F9")

        self.df = None
        self.create_widgets()

    def create_widgets(self):
        # Cabeçalho
        header_frame = tk.Frame(self, bg="#1F4E78", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header_frame,
            text="Relatório Estatístico: Consumo de Conteúdos Audiovisuais",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg="#1F4E78",
        )
        title_lbl.pack(side=tk.LEFT, padx=20, pady=12)

        # Painel de Leitura de Ficheiro
        control_frame = tk.LabelFrame(
            self,
            text=" 1. Painel de Controlo ",
            font=("Segoe UI", 11, "bold"),
            bg="#F4F6F9",
            fg="#1F4E78",
            padx=15,
            pady=10,
        )
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        btn_load = tk.Button(
            control_frame,
            text="📂 Carregar Respostas do Forms (.xlsx / .csv)",
            command=self.load_and_process_data,
            font=("Segoe UI", 10, "bold"),
            bg="#2B579A",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
        )
        btn_load.pack(side=tk.LEFT, padx=5)

        self.lbl_file = tk.Label(
            control_frame,
            text="Aguardando carregamento da base de dados...",
            font=("Segoe UI", 10, "italic"),
            bg="#F4F6F9",
            fg="#666666",
        )
        self.lbl_file.pack(side=tk.LEFT, padx=15)

        # Abas de Exibição
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tab_qual = ttk.Frame(self.notebook)
        self.tab_quant1 = ttk.Frame(self.notebook)
        self.tab_quant2 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_qual, text="Qualitativa: Tipo de Conteúdo")
        self.notebook.add(self.tab_quant1, text="Quantitativa 1: Total Plataformas")
        self.notebook.add(self.tab_quant2, text="Quantitativa 2: Horas/Semana")

    def load_and_process_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos Excel/CSV", "*.xlsx *.xls *.csv")]
        )
        if not file_path:
            return

        try:
            # 1. Carregamento dos dados brutos
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)

            # Normalização de nomes de colunas
            self.df.columns = [c.strip().replace("\n", "") for c in self.df.columns]

            # 2. TRATAMENTO ESTATÍSTICO EXPLÍCITO DAS VARIÁVEIS DO TRABALHO
            
            # Variável Qualitativa Nominal
            self.col_qual = self.df.columns[1]  # "Qual tipo de conteúdo audiovisual você mais assiste?"

            # Variável Quantitativa Discreta
            self.col_quant1 = self.df.columns[3]  # "O total de plataformas..."

            # Variável Quantitativa Contínua (Mapeamento explícito do ponto médio das faixas)
            hours_mapping = {
                "Entre 0 e 1 hora": 0.5,
                "Entre 1 e 2 horas": 1.5,
                "Entre 2 e 3 horas": 2.5,
                "Entre 3 e 4 horas": 3.5,
                "Entre 4 e 5 horas": 4.5,
                "Mais de 6 horas": 7.0,
            }
            col_horas_texto = self.df.columns[2]  # "Aproximadamente, quantas horas..."
            self.df["Horas_Semana_Num"] = self.df[col_horas_texto].map(hours_mapping)

            # Atualiza etiqueta visual
            filename = os.path.basename(file_path)
            self.lbl_file.config(
                text=f"Ficheiro Carregado: {filename} (Amostra n = {len(self.df)})",
                fg="#107C41",
            )

            # 3. Renderização Visual dos Resultados
            self.render_qualitative_tab()
            self.render_quantitative_tab(
                self.tab_quant1,
                self.col_quant1,
                "Total de Plataformas Utilizadas",
                is_integer=True,
            )
            self.render_quantitative_tab(
                self.tab_quant2,
                "Horas_Semana_Num",
                "Horas Semanal de Consumo Audiovisual",
                is_integer=False,
            )

        except Exception as e:
            messagebox.showerror(
                "Erro no Processamento",
                f"Ocorreu um erro ao ler a estrutura do ficheiro:\n{e}",
            )

    def render_qualitative_tab(self):
        """Renderiza a Tabela de Frequência e o Gráfico de Barras para a Variável Qualitativa"""
        for w in self.tab_qual.winfo_children():
            w.destroy()

        s = self.df[self.col_qual].dropna()
        freq_abs = s.value_counts()
        freq_rel = s.value_counts(normalize=True) * 100
        df_freq = pd.DataFrame(
            {"fi (Absoluta)": freq_abs, "fi % (Relativa)": freq_rel}
        )

        moda = s.mode()[0] if not s.mode().empty else "N/A"

        # Lado Esquerdo: Painel de Texto / Tabela
        frame_left = tk.Frame(self.tab_qual, bg="white", bd=1, relief=tk.SOLID)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        lbl_title = tk.Label(
            frame_left,
            text="Tabela de Distribuição\nde Frequências",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1F4E78",
        )
        lbl_title.pack(pady=10, padx=10)

        txt = tk.Text(frame_left, width=38, height=18, font=("Consolas", 8.5))
        txt.pack(padx=10, pady=5)
        txt.insert(tk.END, df_freq.to_string())
        txt.insert(tk.END, f"\n\n• Moda (Mo): {moda}")
        txt.config(state=tk.DISABLED)

        # Lado Direito: Gráfico Matplotlib
        frame_right = tk.Frame(self.tab_qual, bg="white")
        frame_right.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
        colors = sns.color_palette("Blues_r", len(freq_abs))
        bars = ax.bar(
            freq_abs.index.astype(str),
            freq_abs.values,
            color=colors,
            edgecolor="#333333",
            width=0.55,
        )

        ax.set_title(
            "Distribuição: Tipo de Conteúdo Mais Assistido",
            fontsize=11,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel("Frequência Absoluta (fi)", fontsize=10)
        ax.set_xticklabels(
            freq_abs.index.astype(str), rotation=20, ha="right"
        )
        ax.set_ylim(0, max(freq_abs.values) * 1.25)

        for bar in bars:
            yval = bar.get_height()
            pct = (yval / len(s)) * 100
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval + (max(freq_abs.values) * 0.02),
                f"{int(yval)} ({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold",
            )

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render_quantitative_tab(self, parent_tab, col_name, title_display, is_integer=False):
        """Calcula todas as Medidas Descritivas e renderiza o Histograma e Boxplot"""
        for w in parent_tab.winfo_children():
            w.destroy()

        s = pd.to_numeric(self.df[col_name], errors="coerce").dropna()

        # --- CÁLCULOS ESTATÍSTICOS RIGOROSOS ---
        n = len(s)
        media = s.mean()
        mediana = s.median()
        moda_val = s.mode()[0] if not s.mode().empty else np.nan

        amplitude = s.max() - s.min()
        variancia = s.var(ddof=1) if n > 1 else 0.0
        desvio_padrao = s.std(ddof=1) if n > 1 else 0.0

        q1 = s.quantile(0.25)
        q2 = s.quantile(0.50)
        q3 = s.quantile(0.75)
        aiq = q3 - q1
        li = q1 - 1.5 * aiq
        ls = q3 + 1.5 * aiq
        outliers = s[(s < li) | (s > ls)].tolist()

        skew = s.skew() if n > 2 else 0.0
        kurt = s.kurtosis() if n > 3 else 0.0

        # Lado Esquerdo: Relatório Estatístico Textual
        frame_left = tk.Frame(parent_tab, bg="white", bd=1, relief=tk.SOLID)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        lbl_title = tk.Label(
            frame_left,
            text=f"Estatísticas Descritivas\n[{title_display}]",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1F4E78",
        )
        lbl_title.pack(pady=8, padx=10)

        outliers_str = (
            ", ".join([f"{x:.1f}" if not is_integer else f"{int(x)}" for x in outliers])
            if outliers
            else "Nenhum"
        )

        fmt = ".2f" if not is_integer else ".2f"

        report = f"""
--- TENDÊNCIA CENTRAL ---
• Tamanho da Amostra (n): {n}
• Média (x̄): {media:{fmt}}
• Mediana (Md): {mediana:{fmt}}
• Moda (Mo): {moda_val:{fmt}}

--- DISPERSÃO ---
• Amplitude Total (AT): {amplitude:{fmt}}
• Variância Amostral (s²): {variancia:.2f}
• Desvio Padrão (s): {desvio_padrao:.2f}

--- POSIÇÃO & BOXPLOT ---
• Mínimo: {s.min():{fmt}} | Máximo: {s.max():{fmt}}
• 1º Quartil (Q1): {q1:{fmt}}
• 2º Quartil (Q2): {q2:{fmt}}
• 3º Quartil (Q3): {q3:{fmt}}
• AIQ (Q3 - Q1): {aiq:{fmt}}
• Limite Inferior (LI): {li:.2f}
• Limite Superior (LS): {ls:.2f}
• Outliers: {outliers_str}

--- FORMA DA DISTRIBUIÇÃO ---
• Assimetria (Skewness): {skew:.2f}
• Curtose (Kurtosis): {kurt:.2f}
"""
        txt = tk.Text(frame_left, width=36, height=22, font=("Consolas", 8.5))
        txt.pack(padx=10, pady=5)
        txt.insert(tk.END, report)
        txt.config(state=tk.DISABLED)

        # Lado Direito: Visualização Dual (Histograma + Boxplot)
        frame_right = tk.Frame(parent_tab, bg="white")
        frame_right.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        fig, (ax_hist, ax_box) = plt.subplots(
            2, 1, figsize=(6.5, 5), gridspec_kw={"height_ratios": [3, 1.2]}
        )

        # Histograma com Curva KDE
        sns.histplot(
            s,
            kde=True,
            ax=ax_hist,
            color="#2B579A",
            bins="sturges",
            edgecolor="white",
        )
        ax_hist.axvline(
            media,
            color="#D9534F",
            linestyle="--",
            linewidth=1.8,
            label=f"Média ({media:.2f})",
        )
        ax_hist.axvline(
            mediana,
            color="#5CB85C",
            linestyle="-.",
            linewidth=1.8,
            label=f"Mediana ({mediana:.2f})",
        )
        ax_hist.set_title(
            f"Histograma e Densidade - {title_display}",
            fontsize=10,
            fontweight="bold",
        )
        ax_hist.set_ylabel("Frequência", fontsize=9)
        ax_hist.legend(fontsize=8)

        # Boxplot
        sns.boxplot(
            x=s,
            ax=ax_box,
            color="#A6C8E0",
            fliersize=5,
            flierprops={"markerfacecolor": "red"},
        )
        ax_box.set_title("Boxplot e Outliers", fontsize=9)
        ax_box.set_xlabel(title_display, fontsize=9)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = Application()
    app.mainloop()