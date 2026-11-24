"""Figura original: faixas de repeticoes CAG do gene HTT (fonte: GeneReviews, NBK1305)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

AQUI = Path(__file__).parent
faixas = [  # (inicio, fim, rotulo, cor)
    (0, 26, "Normal\n(≤ 26)", "#54A24B"),
    (27, 35, "Intermediária\n(27–35)", "#F2C94C"),
    (36, 39, "Reduzida\n(36–39)", "#F58518"),
    (40, 50, "Completa\n(≥ 40)", "#C0392B"),
]
fig, ax = plt.subplots(figsize=(8, 1.9), dpi=200)
for ini, fim, rot, cor in faixas:
    ax.add_patch(Rectangle((ini, 0), fim - ini + 1, 1, color=cor, ec="white", lw=2))
    ax.text((ini + fim + 1) / 2, 0.5, rot, ha="center", va="center", fontsize=8,
            color="white" if cor in ("#C0392B", "#54A24B") else "#1a1a1a", fontweight="bold")
ax.set_xlim(0, 51)
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_xticks([0, 10, 20, 26, 35, 39, 45, 50])
ax.set_xticklabels(["0", "10", "20", "26", "35", "39", "45", "≥ 50"], fontsize=8)
ax.set_xlabel("Número de repetições CAG no gene HTT (4p16.3). Laranja e vermelho: penetrância da doença", fontsize=9)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(AQUI / "saida" / "fig_cag.png", facecolor="white")
print("ok")
