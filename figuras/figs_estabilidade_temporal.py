"""Duas figuras da V3 a partir dos artefatos da execução certificada (V15.3):
  Fig8_Estabilidade_AG: F1 por geração e genes do melhor indivíduo por geração (historico_ag.csv).
  Fig7_Diacronica_Agenda: composição temática por ano, com destaque orientado por dados
     (classes com variação absoluta >= 5 p.p. entre 2023 e 2026), fontes para a largura da RITA.
Uso: python3 figs_estabilidade_temporal.py <historico_ag.csv> <saida/>
As proporções por ano vêm do log da execução certificada (célula das proporções, 20/10/2026).
Mudanças a replicar no notebook: DESTAQUE deixa de ser conjunto fixo; fig de estabilidade nova."""
import sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY, GRAY, AMBER, GREEN = "#0D1B2A", "#94A3B8", "#F59E0B", "#2E7D32"
F1_BASELINE = 0.8534
BOUNDS = {"max_features": (500, 3000), "C_log": (-2, 1)}
plt.rcParams.update({"font.family": "serif", "font.size": 11})

PROP = pd.DataFrame({  # log da execução certificada, "Proporções temáticas por ano (%) — predição do SVM"
    "2023": [21.6, 7.1, 19.7, 1.9, 16.6, 3.8, 15.2, 6.2, 8.1],
    "2024": [21.6, 9.8, 12.2, 10.3, 16.7, 8.0, 11.5, 4.5, 5.4],
    "2025": [16.8, 14.1, 10.2, 8.5, 16.8, 8.2, 11.1, 5.3, 8.9],
    "2026": [17.1, 14.1, 11.3, 9.1, 15.9, 8.6, 10.9, 4.4, 8.6]},
    index=["Economia e desenvolvimento", "Educação e ciência", "Governança institucional", "Infraestrutura logística",
           "Meio ambiente e energia", "Política externa", "Programas sociais", "Reforma agrária e agropecuária", "Saúde"])
LIMIAR_DESTAQUE = 5.0  # p.p. entre 2023 e 2026


def fig_estabilidade(h, saida):
    g = h["geracao"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 3.9))
    a.plot(g, h["melhor_f1"], color=NAVY, lw=2.2, marker="o", ms=5, label="Melhor F1")
    a.plot(g, h["medio_f1"], color=GRAY, lw=1.8, marker="s", ms=4, label="F1 médio")
    a.plot(g, h["pior_f1"], color=GRAY, lw=1.2, ls=":", marker="^", ms=4, label="Pior F1")
    a.axhline(F1_BASELINE, color=AMBER, ls="--", lw=1.5, label=f"Baseline ({F1_BASELINE:.3f})".replace(".", ","))
    a.set_ylim(0.82, 0.935); a.set_xticks(range(1, 11)); a.set_xlabel("Geração"); a.set_ylabel("F1-macro (3 dobras)")
    a.legend(frameon=False, fontsize=9.5, loc="lower right"); a.set_title("(a) Aptidão da população", fontsize=11)
    mf = (h["melhor_maxf"] - BOUNDS["max_features"][0]) / (BOUNDS["max_features"][1] - BOUNDS["max_features"][0])
    cl = (np.log10(h["melhor_C"]) - BOUNDS["C_log"][0]) / (BOUNDS["C_log"][1] - BOUNDS["C_log"][0])
    clf = (h["melhor_clf"] == "SVM").astype(float)
    b.plot(g, mf, color=NAVY, lw=2.2, marker="o", ms=5, label="max\\_features (500–3.000)".replace("\\_", "_"))
    b.plot(g, cl, color=AMBER, lw=2.2, marker="s", ms=5, label="log$_{10}$ C ($-$2 a 1)")
    b.plot(g, clf, color=GREEN, lw=1.6, marker="^", ms=5, label="classificador (1 = SVM)")
    b.plot(g, h["diversidade"], color=GRAY, lw=1.6, ls="--", marker="d", ms=4, label="diversidade da população")
    b.set_ylim(-0.05, 1.08); b.set_xticks(range(1, 11)); b.set_xlabel("Geração"); b.set_ylabel("Valor normalizado [0, 1]")
    b.axvspan(5.5, 10.5, color=GRAY, alpha=0.10, lw=0)
    b.annotate("estável a partir da geração 6\n(2.352 termos; C = 0,825)", (5.7, 0.84), fontsize=9.5, color=NAVY)
    b.legend(frameon=False, fontsize=9.5, loc="center left", bbox_to_anchor=(0.0, 0.40)); b.set_title("(b) Melhor indivíduo e diversidade", fontsize=11)
    for ax in (a, b):
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        ax.grid(axis="y", color=GRAY, alpha=0.25)
    fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(os.path.join(saida, f"Fig8_Estabilidade_AG.{ext}"), dpi=200)


def fig_temporal(saida):
    anos = list(PROP.columns)
    delta = PROP["2026"] - PROP["2023"]
    destaque = set(delta[delta.abs() >= LIMIAR_DESTAQUE].index)
    ordem = PROP.mean(axis=1).sort_values(ascending=False).index.tolist()
    fig, axes = plt.subplots(3, 3, figsize=(10.0, 6.6), sharex=True, sharey=True)
    for ax, classe in zip(axes.flat, ordem):
        v = PROP.loc[classe, anos].values.astype(float)
        cor = AMBER if classe in destaque else NAVY; lw = 2.6 if classe in destaque else 1.6
        ax.plot(anos, v, color=cor, lw=lw, marker="o", ms=5, mfc=cor, mec="white", mew=0.8, zorder=3)
        ax.fill_between(anos, v, 0, color=cor, alpha=0.08)
        if classe in destaque:
            for x, y, dx in ((anos[0], v[0], -2), (anos[-1], v[-1], 2)):
                ax.annotate(f"{y:.1f}".replace(".", ","), (x, y), textcoords="offset points", xytext=(dx, 7),
                            fontsize=10, color=cor, fontweight="bold", ha="left" if dx < 0 else "right")
        ax.set_title(classe, fontsize=10.5); ax.set_ylim(0, 27); ax.tick_params(labelsize=9.5)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        ax.grid(axis="y", color=GRAY, alpha=0.25)
    fig.supylabel("% dos parágrafos rotulados do ano", fontsize=11)
    fig.tight_layout()
    for ext in ("pdf", "png"): fig.savefig(os.path.join(saida, f"Fig7_Diacronica_Agenda.{ext}"), dpi=200)
    return destaque, delta


if __name__ == "__main__":
    h = pd.read_csv(sys.argv[1]); saida = sys.argv[2]; os.makedirs(saida, exist_ok=True)
    assert len(h) == 10
    fig_estabilidade(h, saida)
    d, delta = fig_temporal(saida)
    print("destaque:", sorted(d)); print(delta.round(1).sort_values().to_string())
    cons = PROP.diff(axis=1).abs().max(axis=1).sort_values(ascending=False)
    print("maior variação entre anos consecutivos:\n", cons.head(3).round(1).to_string())
