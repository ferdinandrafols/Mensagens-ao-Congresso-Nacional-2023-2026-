"""Figuras 3 e 4 da V3 (Fig5_Convergencia_AG e Fig6_AG_vs_Random_vs_Baseline do notebook) regeradas
a partir dos artefatos da V15.3 com fontes maiores para a largura de coluna da RITA.
Mesmas funções do notebook (célula das figuras), com três mudanças: figsize menor, fontes maiores,
fonte serifada. Estas mudanças devem ser replicadas em fig5_convergencia e fig6_raincloud do notebook.
Uso: python3 figs_3_4_legiveis.py <historico_ag.csv> <resultados_30_execucoes.csv> <fase6c_rs.csv> <saida/>
"""
import sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, wilcoxon

NAVY, GRAY, AMBER = "#0D1B2A", "#94A3B8", "#F59E0B"
F1_BASELINE = 0.8534  # baseline da execução principal (V15.3)
plt.rcParams.update({"font.family": "serif", "font.size": 12})


def fig5_convergencia(historico, saida):
    g = historico["geracao"]; best = historico["melhor_f1"]; med = historico["medio_f1"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(g, best, color=NAVY, lw=2.4, marker="o", ms=6, label="Melhor F1")
    ax.plot(g, med, color=GRAY, lw=1.8, marker="s", ms=5, label="F1 médio da população")
    _bl = float(F1_BASELINE)
    ax.axhline(_bl, color=AMBER, ls="--", lw=1.6, label=f"Baseline ({_bl:.3f})".replace(".", ","))
    ax.set_ylim(min(min(med), _bl) - 0.03, max(best) + 0.02)
    ax.set_xlabel("Geração", fontsize=13); ax.set_ylabel("F1-macro", fontsize=13)
    ax.set_xticks(range(1, 11)); ax.tick_params(labelsize=12)
    ax.legend(frameon=False, fontsize=12, loc="lower right")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRAY, alpha=0.25)
    fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(os.path.join(saida, f"Fig5_Convergencia_AG.{ext}"), dpi=200)


def fig6_raincloud(ag, base, rs, saida):
    rng = np.random.default_rng(42)
    ag, base, rs = map(lambda v: np.asarray(v, float), (ag, base, rs))

    def nuvem(ax, data, pos, cor, label):
        xs = np.linspace(min(data), max(data), 100)
        d = gaussian_kde(data)(xs); d = d / d.max() * 0.32
        ax.fill_betweenx(xs, pos - d, pos, color=cor, alpha=0.30, lw=0)
        bp = ax.boxplot(data, positions=[pos + 0.06], widths=0.10, vert=True, patch_artist=True,
                        showfliers=False, manage_ticks=False)
        for b in bp["boxes"]: b.set(facecolor="white", edgecolor=cor, lw=1.4)
        for w in bp["whiskers"] + bp["caps"]: w.set(color=cor, lw=1.3)
        for m in bp["medians"]: m.set(color=cor, lw=1.8)
        jx = pos + 0.12 + rng.uniform(0, 0.10, len(data))
        ax.scatter(jx, data, s=20, color=cor, alpha=0.65, edgecolor="white", lw=0.3, zorder=3)
        ax.text(pos, min(data) - 0.004, label, ha="center", va="top", fontsize=12, color=cor, fontweight="bold")

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    nuvem(ax, base, 1, GRAY, "Baseline"); nuvem(ax, rs, 2, NAVY, "Random Search"); nuvem(ax, ag, 3, AMBER, "Alg. Genético")
    p_rs = wilcoxon(ag, rs, alternative="greater").pvalue

    def bracket(x1, x2, y, txt):
        ax.plot([x1, x1, x2, x2], [y, y + 0.004, y + 0.004, y], color=NAVY, lw=1.2)
        ax.text((x1 + x2) / 2, y + 0.006, txt, ha="center", fontsize=11.5, color=NAVY)

    ymax = max(ag.max(), rs.max(), base.max())
    bracket(1, 3, ymax + 0.018, f"p < 0,0001  ({int((ag > base).sum())}/{len(ag)})")
    bracket(2, 3, ymax + 0.004, f"p = {p_rs:.3f}".replace(".", ",") + f"  ({int((ag > rs).sum())}/{len(ag)}" + (", n.s.)" if p_rs >= 0.05 else ")"))
    ax.set_ylabel("F1-macro (30 execuções)", fontsize=13); ax.set_xticks([]); ax.set_xlim(0.5, 3.6)
    ax.set_ylim(min(base) - 0.012, ymax + 0.032); ax.tick_params(labelsize=12)
    for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRAY, alpha=0.25)
    fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(os.path.join(saida, f"Fig6_AG_vs_Random_vs_Baseline.{ext}"), dpi=200)
    return p_rs


if __name__ == "__main__":
    h, r30, rs, saida = sys.argv[1:5]
    os.makedirs(saida, exist_ok=True)
    hist = pd.read_csv(h); r = pd.read_csv(r30); q = pd.read_csv(rs)
    assert len(r) == 30 and len(q) == 30 and len(hist) == 10
    fig5_convergencia(hist, saida)
    p = fig6_raincloud(r["f1_ag"], r["f1_baseline"], q["f1_rs"], saida)
    print("ok; p AG x RS =", round(p, 4), "| AG > RS:", int((r["f1_ag"].values > q["f1_rs"].values).sum()),
          "| orçamento RS:", q["orcamento"].mean().round(2), q["orcamento"].min(), q["orcamento"].max())
