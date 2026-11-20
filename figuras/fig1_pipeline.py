"""Figura 1 da V3: visão geral do pipeline (mesmo estilo da V2, com 106 avaliações e o conjunto-ouro)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY, ORANGE, GOLD, GREY = "#0f1b2d", "#f5a21f", "#2e6f8e", "#9aa3ad"
plt.rcParams["font.family"] = "serif"
fig, ax = plt.subplots(figsize=(13.2, 6.6), dpi=200)
ax.set_xlim(0, 100); ax.set_ylim(0, 56); ax.axis("off")


def box(x, y, w, h, title, sub, fc=NAVY, tc="white", ec=None, lw=1.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6", fc=fc, ec=ec or fc, lw=lw)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", color=tc, fontsize=13, fontweight="bold")
    ax.text(x + w / 2, y + h * 0.27, sub, ha="center", va="center", color=tc, fontsize=10.5)


def arrow(x1, y1, x2, y2, color=NAVY, style="-|>", ls="-", lw=2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=18, color=color, lw=lw, linestyle=ls))


ax.text(50, 53.5, "Pipeline reprodutível de categorização semântica", ha="center", fontsize=17, fontweight="bold", color=NAVY)
ax.text(50, 50.2, "a etapa de otimização configura vetorizador e classificador; o conjunto-ouro é a referência externa ao léxico",
        ha="center", fontsize=11, style="italic", color="#555")

# linha de cima
W, H, Y = 20, 9.5, 36
xs = [3, 27, 51, 75]
for x, (t, s) in zip(xs, [("Corpus", "4 Mensagens (PDF)"), ("Extração", "pdfplumber, parágrafos"),
                          ("Limpeza", "estrutural, hifenização"), ("Rotulagem", "léxico V3, 9 classes")]):
    box(x, Y, W, H, t, s)
for x in xs[:-1]:
    arrow(x + W + 0.4, Y + H / 2, x + 4 - 0.4, Y + H / 2)

# otimização
box(43, 21, 40, 8.5, "Otimização por Algoritmo Genético", "HPO auditável: 106 avaliações únicas", fc=ORANGE, tc=NAVY, ec="#b86e00")

# linha de baixo
Y2 = 6
box(75, Y2, W, H, "TF-IDF", "vetorização")
box(45, Y2, W, H, "Classificadores", "LogReg · SVM · RF")
box(13, Y2, W, H, "Avaliação", "CV 3-fold · F1-macro\nWilcoxon 30×")
arrow(85, Y - 0.4, 85, Y2 + H + 0.4)            # rotulagem -> tf-idf
arrow(75 - 0.4, Y2 + H / 2, 45 + W + 0.4, Y2 + H / 2)  # tf-idf -> clf
arrow(45 - 0.4, Y2 + H / 2, 13 + W + 0.4, Y2 + H / 2)  # clf -> aval
arrow(75, 21 - 0.4, 80, Y2 + H + 0.4, color="#b86e00", ls="--")  # AG -> tf-idf
arrow(55, 21 - 0.4, 55, Y2 + H + 0.4, color="#b86e00", ls="--")  # AG -> clf
# fitness
ax.add_patch(FancyArrowPatch((31.5, Y2 + H + 0.4), (46, 21 - 0.4), connectionstyle="arc3,rad=-0.25", arrowstyle="-", color=GREY, lw=1.6, linestyle="--"))
ax.text(37.5, 20.6, "F1-macro\n(fitness)", ha="center", fontsize=10, style="italic", color="#666")

# conjunto-ouro
box(3, 22, 26, 8.5, "Conjunto-ouro", "540 parágrafos · 2 anotadores", fc="white", tc=GOLD, ec=GOLD, lw=1.8)
arrow(14, 22 - 0.4, 16, Y2 + H + 0.4, color=GOLD)
ax.text(19.5, 17.6, "referência externa:\nF1 contra o ouro", ha="left", fontsize=10, style="italic", color=GOLD)

fig.savefig("/home/claude/v3_tex/figuras/Fig1_Pipeline.pdf", bbox_inches="tight")
fig.savefig("/home/claude/v3_tex/figuras/Fig1_Pipeline.png", bbox_inches="tight")
print("ok")
