import os
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import seaborn as sns

# Configuração visual do Matplotlib / Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.sans-serif": "DejaVu Sans",
        "axes.edgecolor": "#CCCCCC",
        "axes.linewidth": 1.1,
    }
)

# 1. Carregar planilha de respostas
file_path = "Pesquisa sobre o consumo de conteúdos audiovisuais pelos estudantes do IFS – Campus Lagarto  (respostas).xlsx"
df = pd.read_excel(file_path)
df.columns = [c.strip().replace("\n", "") for c in df.columns]

col_qual = "Qual tipo de conteúdo audiovisual você mais assiste?"
col_quant1 = "O total de plataformas de conteúdo audiovisual você utiliza com frequência? Exemplo: Netflix, amazon prime, YouTube, etc."
col_horas_str = "Aproximadamente, quantas horas por semana você passa consumindo conteúdos audiovisuais?"

# Converter faixas de horas para valores médios numéricos
hours_mapping = {
    "Entre 0 e 1 hora": 0.5,
    "Entre 1 e 2 horas": 1.5,
    "Entre 2 e 3 horas": 2.5,
    "Entre 3 e 4 horas": 3.5,
    "Entre 4 e 5 horas": 4.5,
    "Mais de 6 horas": 7.0,
}
df["Horas_Semana_Num"] = df[col_horas_str].map(hours_mapping)

# ==========================================
# 2. GERAR GRÁFICO QUALITATIVO
# ==========================================
plt.figure(figsize=(9, 5))
freq_qual = df[col_qual].value_counts()
colors = sns.color_palette("Blues_r", len(freq_qual))
bars = plt.bar(
    freq_qual.index,
    freq_qual.values,
    color=colors,
    edgecolor="#333333",
    width=0.55,
)

plt.title(
    "Tipo de Conteúdo Audiovisual Mais Assistido pelos Estudantes",
    fontsize=12,
    fontweight="bold",
    pad=15,
)
plt.ylabel("Frequência Absoluta (fi)", fontsize=10)
plt.xlabel("Tipo de Conteúdo", fontsize=10)
plt.xticks(rotation=20, ha="right")
plt.ylim(0, max(freq_qual.values) * 1.25)

for bar in bars:
    yval = bar.get_height()
    pct = (yval / len(df)) * 100
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        yval + 0.3,
        f"{int(yval)} ({pct:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
    )

plt.tight_layout()
plt.savefig("grafico_qualitativa.png", dpi=300)
plt.close()


# ==========================================
# 3. GERAR GRÁFICOS QUANTITATIVOS (Histograma + Boxplot)
# ==========================================
def processar_quantitativa(s, title, filename, xlabel):
    n = len(s)
    media = s.mean()
    mediana = s.median()
    moda = s.mode()[0] if not s.mode().empty else np.nan
    amp = s.max() - s.min()
    var = s.var(ddof=1)
    dp = s.std(ddof=1)

    q1 = s.quantile(0.25)
    q2 = s.quantile(0.50)
    q3 = s.quantile(0.75)
    aiq = q3 - q1
    li = q1 - 1.5 * aiq
    ls = q3 + 1.5 * aiq
    outliers = s[(s < li) | (s > ls)].tolist()

    skew = s.skew()
    kurt = s.kurtosis()

    print(f"\n==========================================")
    print(f" STATS: {title.upper()}")
    print(f"==========================================")
    print(f"• n = {n}")
    print(f"• Média = {media:.2f}")
    print(f"• Mediana = {mediana:.2f}")
    print(f"• Moda = {moda:.2f}")
    print(
        f"• Amplitude Total = {amp:.2f} (Mín: {s.min():.2f}, Máx: {s.max():.2f})"
    )
    print(f"• Variância Amostral = {var:.2f}")
    print(f"• Desvio Padrão = {dp:.2f}")
    print(f"• Quartis: Q1 = {q1:.2f} | Q2 = {q2:.2f} | Q3 = {q3:.2f}")
    print(f"• AIQ = {aiq:.2f}")
    print(f"• Limites de Outliers: LI = {li:.2f} | LS = {ls:.2f}")
    print(f"• Outliers: {outliers if outliers else 'Nenhum'}")
    print(f"• Assimetria = {skew:.2f}")
    print(f"• Curtose = {kurt:.2f}")

    fig, (ax_hist, ax_box) = plt.subplots(
        2, 1, figsize=(8, 6), gridspec_kw={"height_ratios": [3, 1.2]}
    )

    sns.histplot(
        s, kde=True, ax=ax_hist, color="#2B579A", bins="sturges", edgecolor="white"
    )
    ax_hist.axvline(
        media,
        color="#D9534F",
        linestyle="--",
        linewidth=2,
        label=f"Média ({media:.2f})",
    )
    ax_hist.axvline(
        mediana,
        color="#5CB85C",
        linestyle="-.",
        linewidth=2,
        label=f"Mediana ({mediana:.2f})",
    )
    ax_hist.set_title(
        f"Histograma e Curva de Densidade - {title}",
        fontsize=12,
        fontweight="bold",
    )
    ax_hist.set_ylabel("Frequência", fontsize=10)
    ax_hist.legend(fontsize=9)

    sns.boxplot(
        x=s,
        ax=ax_box,
        color="#A6C8E0",
        fliersize=6,
        flierprops={"markerfacecolor": "red"},
    )
    ax_box.set_title(
        "Boxplot e Identificação de Outliers", fontsize=10, fontweight="bold"
    )
    ax_box.set_xlabel(xlabel, fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{filename}.png", dpi=300)
    plt.close()


processar_quantitativa(
    df[col_quant1],
    "Total de Plataformas Utilizadas",
    "grafico_quant1",
    "Quantidade de Plataformas",
)
processar_quantitativa(
    df["Horas_Semana_Num"],
    "Horas de Consumo Audiovisual por Semana",
    "grafico_quant2",
    "Horas Semanal Estimadas",
)