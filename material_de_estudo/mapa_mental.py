"""Mapa mental do projeto (HTT como rede). Saidas: mapa_mental.png e mapa_mental.pdf na mesma pasta."""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse

AQUI = Path(__file__).parent
W, H = 160, 124
fig = plt.figure(figsize=(19, 14.7))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

DARK = "#14213D"
BLOCOS = [
    # (numero, titulo, cor, linhas)
    (1, "BIOLOGIA: o gene HTT", "#4C78A8", [
        "Repetição CAG no HTT (cromossomo 4); a doença aparece com 36 ou mais repetições",
        "Efeito principal: ganho de função tóxico da huntingtina mutada (poliglutamina)",
        "Atinge neurônios do estriado: coreia, perda cognitiva e alterações de humor",
        "O mapa KEGG hsa05016 descreve 7 mecanismos, e cada um virou um módulo da rede"]),
    (2, "DADOS: como a rede foi montada", "#54A24B", [
        "KEGG dá as proteínas: 67 + HTT = 68 (consulta ao STRING, humano, 9606)",
        "STRING com score ≥ 0,7 (alta confiança): 66 nós e 207 arestas",
        "Grafo não direcionado e sem sinal: a aresta só diz que as proteínas interagem",
        "Python + networkx para as métricas; Cytoscape para o layout das figuras"]),
    (3, "TOPOLOGIA: quem é importante", "#F58518", [
        "Grau (nº de vizinhos): TP53 18, HTT 17, BECN1 15  →  são os hubs",
        "Betweenness (quanto passa por ele): HTT 0,40, TP53 0,20, SLC1A2 0,17",
        "Agrupamento 0,64, caminho médio 2,9, diâmetro 6, densidade 0,097",
        "Leitura: esparsa, mas muito agrupada; poucos passos ligam quase tudo"]),
    (4, "MÓDULOS: onde a rede se divide", "#B279A2", [
        "Modularidade Q = 0,60 (grupos funcionais) e 0,61 (Louvain, 7 comunidades)",
        "75% das arestas ficam dentro do mesmo módulo (156 de 207)",
        "Módulos: transporte, transcrição, cálcio, mitocôndria, apoptose, autofagia, astrócitos",
        "Quem liga um módulo a outro é ponto de articulação (HTT, SLC1A2, PPARGC1A)"]),
    (5, "ROBUSTEZ: remover nós", "#E45756", [
        "Remoção aleatória: a rede aguenta bem (há redundância)",
        "Ataque a hubs ou a nós de alta betweenness: a eficiência cai bem mais rápido",
        "SLC1A2 tem só 7 conexões e tira 11,5% da eficiência; TP53 tem 18 e tira 4,1%",
        "Conclusão: grau alto não é o mesmo que ser crítico para a conectividade"]),
    (6, "CASCATA: falha que se propaga", "#9D755D", [
        "Regra: o nó falha se a fração de vizinhos falhos for ≥ φ (limiar)",
        "φ = 0,2: semente média derruba ~20 dos 66; começar no HTT derruba os 66",
        "φ = 0,3: média de 3 nós, mas BAX sozinho derruba os 66 (atinge 8 módulos)",
        "φ ≥ 0,4: cascatas pequenas (máximo 9). Quem inicia a pior cascata nem sempre é hub"]),
    (7, "SOLUÇÃO INOVADORA: proteção", "#1F8A87", [
        "Pergunta: se eu proteger k proteínas (não falham), quanto a cascata diminui?",
        "φ = 0,2, k = 5: proteger os 5 maiores hubs reduz 66%; 5 aleatórias, só 17%",
        "Escolha gulosa: HDAC1 sozinho já reduz 27%; depois RUBCN, PLCB1, DCTN1, PPARGC1A",
        "Frentes biológicas: glutamato (SLC1A2), mitocôndria (PPARGC1A), transporte (DCTN1)",
        "É uma hipótese computacional para priorizar alvos, não um tratamento"]),
    (8, "LIMITES: diga antes que perguntem", "#6C757D", [
        "Mutação é ganho de função: remover o HTT testa a dependência da rede, não é a doença",
        "PPI sem direção nem sinal: não diz quem ativa ou inibe quem",
        "O limiar φ é uma suposição e os resultados dependem dele",
        "Com 66 nós não dá para afirmar rede livre de escala; sem validação experimental"]),
]


def bloco(x, y, w, h, num, titulo, cor, linhas):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.4", fc="white", ec=cor, lw=2.4, zorder=2))
    ax.add_patch(FancyBboxPatch((x, y + h - 4.2), w, 4.2, boxstyle="round,pad=0.0,rounding_size=1.4", fc=cor, ec=cor, zorder=3))
    ax.add_patch(plt.Rectangle((x, y + h - 4.2), w, 2.0, fc=cor, ec=cor, zorder=3))
    ax.text(x + 1.6, y + h - 2.1, f"{num}", color="white", fontsize=17, fontweight="bold", va="center", zorder=4)
    ax.text(x + 4.6, y + h - 2.1, titulo, color="white", fontsize=13.5, fontweight="bold", va="center", zorder=4)
    yy = y + h - 6.1
    for l in linhas:
        for i, p in enumerate(textwrap.wrap(l, 92)):
            ax.text(x + 1.6 if i == 0 else x + 3.6, yy, ("•  " + p) if i == 0 else p, fontsize=10.6, va="center",
                    color="#1a1a1a", zorder=4)
            yy -= 2.5
        yy -= 0.4


LX, RX, BW = 1.2, 93.8, 65.0
ys = [92.0, 68.6, 45.2, 21.8]
cx, cy = 80, 66
for i in range(4):
    bloco(LX, ys[i], BW, 22.6, *BLOCOS[i])
    ax.plot([LX + BW, cx - 12], [ys[i] + 10.4, cy + (ys[i] - 57) * 0.15], color=BLOCOS[i][2], lw=2.6, zorder=1, alpha=0.8)
    bloco(RX, ys[i], BW, 22.6, *BLOCOS[4 + i])
    ax.plot([RX, cx + 12], [ys[i] + 10.4, cy + (ys[i] - 57) * 0.15], color=BLOCOS[4 + i][2], lw=2.6, zorder=1, alpha=0.8)

ax.add_patch(Ellipse((cx, cy), 26, 17, fc=DARK, ec="#F6B26B", lw=3.5, zorder=5))
ax.text(cx, cy + 3.6, "Doença de\nHuntington", color="white", fontsize=15.5, fontweight="bold", ha="center", va="center", zorder=6, linespacing=1.05)
ax.text(cx, cy - 2.0, "como REDE", color="#F6B26B", fontsize=15, fontweight="bold", ha="center", va="center", zorder=6)
ax.text(cx, cy - 5.0, "66 proteínas · 207 interações", color="white", fontsize=9.6, ha="center", va="center", zorder=6)

ax.text(80, H - 2.0, "MAPA MENTAL: do gene à intervenção computacional", fontsize=22, fontweight="bold", ha="center", va="center", color=DARK)
ax.text(80, H - 6.0, "Ordem para contar: 1 → 8 (esquerda, depois direita). Cada bloco responde à pergunta do bloco seguinte.", fontsize=11.5,
        ha="center", va="center", color="#555")

# faixa inferior: fio condutor
ax.add_patch(FancyBboxPatch((1.2, 1.0), 157.6, 18.4, boxstyle="round,pad=0.0,rounding_size=1.4", fc="#EEF3F8", ec=DARK, lw=2.2, zorder=2))
ax.text(3.0, 17.0, "FIO CONDUTOR (como o conhecimento se conecta)", fontsize=12.5, fontweight="bold", color=DARK, va="center", zorder=4)
etapas = ["Sistema biológico\n(proteínas e vias)", "Rede\n(nó = proteína,\naresta = interação)", "Métricas\n(quem é central?)",
          "Perturbação\n(remover / falhar)", "Intervenção\n(proteger quem?)"]
xs = [14.5, 43, 71, 99, 127]
for i, (x, t) in enumerate(zip(xs, etapas)):
    ax.add_patch(FancyBboxPatch((x - 11.5, 5.3), 23, 8.0, boxstyle="round,pad=0.0,rounding_size=1.0", fc=DARK, ec=DARK, zorder=3))
    ax.text(x, 9.3, t, color="white", fontsize=9.6, ha="center", va="center", zorder=4, linespacing=1.15)
    if i < 4:
        ax.annotate("", xy=(xs[i + 1] - 11.7, 9.3), xytext=(x + 11.7, 9.3), arrowprops=dict(arrowstyle="-|>", color="#F58518", lw=2.6), zorder=4)
ax.text(147.5, 14.3, "Elo com Fisiologia:", fontsize=10.4, fontweight="bold", color=DARK, ha="center", va="center", zorder=4)
ax.text(147.5, 8.6, "cada módulo é um sistema\nfisiológico; a cascata mostra\ncomo a disfunção de um\nse espalha para os outros", fontsize=9.2,
        ha="center", va="center", color="#1a1a1a", zorder=4, linespacing=1.15)
ax.text(3.0, 2.6, "Fontes: KEGG hsa05016 · STRING (score ≥ 0,7) · cálculos próprios (networkx). Detalhes e referências no relatório.", fontsize=8.8,
        color="#555", va="center", zorder=4)

fig.savefig(AQUI / "mapa_mental.png", dpi=130, facecolor="white")
fig.savefig(AQUI / "mapa_mental.pdf", facecolor="white")
print("ok")
