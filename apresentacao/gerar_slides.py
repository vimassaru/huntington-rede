"""Gera duas apresentacoes curtas (Marcos e Vinicius) sobre a rede do HTT na Doenca de Huntington."""
import math
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

AQUI = Path(__file__).parent
IMG = AQUI.parent / "relatorio" / "imagens"

DARK, TEAL, CORAL = "14213D", "1F8A87", "D9482B"
LIGHT, TEXT, MUTED, WHITE = "EEF3F7", "1F2933", "52606D", "FFFFFF"
FONT = "Calibri"
W, H = 13.333, 7.5
AVISOS = []


def rgb(h):
    return RGBColor.from_string(h)


def nova():
    p = Presentation()
    p.slide_width, p.slide_height = Inches(W), Inches(H)
    return p


def fundo(slide, cor):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(cor)


def linhas_estimadas(texto, pt, largura):
    cpl = max(1, int(largura * 72 / (pt * 0.53)))
    return sum(max(1, math.ceil(len(par) / cpl)) for par in texto.split("\n"))


def caixa(slide, x, y, w, h, paragrafos, pt=16, cor=TEXT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          espaco=6, nome=None):
    """paragrafos: str ou lista de str | (str, dict(pt, cor, bold))."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if nome:
        tb.name = nome
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    if isinstance(paragrafos, str):
        paragrafos = [paragrafos]
    total = 0.06
    for i, item in enumerate(paragrafos):
        txt, o = (item, {}) if isinstance(item, str) else item
        tam = o.get("pt", pt)
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = align
        par.space_after = Pt(espaco)
        r = par.add_run()
        r.text = txt
        r.font.name, r.font.size, r.font.bold = FONT, Pt(tam), o.get("bold", bold)
        r.font.color.rgb = rgb(o.get("cor", cor))
        total += linhas_estimadas(txt, tam, w - 0.1) * tam * 1.2 / 72 + espaco / 72
    if total > h + 0.02:
        AVISOS.append(f"possivel overflow ({total:.2f}in > {h}in): {str(paragrafos[0])[:50]}")
    return tb


def forma(slide, x, y, w, h, cor, tipo=MSO_SHAPE.ROUNDED_RECTANGLE, nome=None, raio=0.08):
    s = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(cor)
    s.line.fill.background()
    s.shadow.inherit = False
    if tipo == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = raio
    if nome:
        s.name = nome
    return s


def imagem(slide, arquivo, x, y, w, h, alt, centro=True):
    """Encaixa a imagem na caixa (x,y,w,h) mantendo a proporcao."""
    iw, ih = Image.open(IMG / arquivo).size
    esc = min(w / iw, h / ih)
    pw, ph = iw * esc, ih * esc
    px = x + (w - pw) / 2 if centro else x
    py = y + (h - ph) / 2 if centro else y
    pic = slide.shapes.add_picture(str(IMG / arquivo), Inches(px), Inches(py), Inches(pw), Inches(ph))
    pic.name = alt
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic


def titulo(slide, txt, num, total_txt="Introdução à Biologia de Sistemas, UNIFESP, 2026"):
    fundo(slide, WHITE)
    caixa(slide, 0.6, 0.35, 12.1, 0.9, txt, pt=32, cor=DARK, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome="Título")
    if len(txt) > 52:
        AVISOS.append(f"titulo longo ({len(txt)} car.): {txt}")
    caixa(slide, 0.6, 7.05, 9, 0.3, total_txt, pt=10, cor=MUTED, nome="Rodapé")
    caixa(slide, 11.7, 7.05, 1.0, 0.3, str(num), pt=10, cor=MUTED, align=PP_ALIGN.RIGHT, nome="Número")


def cartao(slide, x, y, w, h, grande, legenda, cor=TEAL, pt_g=40):
    forma(slide, x, y, w, h, LIGHT, nome="Cartão")
    caixa(slide, x + 0.1, y + 0.1, w - 0.2, h * 0.5, grande, pt=pt_g, cor=cor, bold=True, anchor=MSO_ANCHOR.MIDDLE,
          nome="Número em destaque")
    caixa(slide, x + 0.1, y + h * 0.55, w - 0.2, h * 0.42, legenda, pt=14, cor=TEXT, nome="Legenda do cartão")


def notas(slide, txt):
    slide.notes_slide.notes_text_frame.text = txt


def capa(pres, titulo_txt, sub, autor, parte):
    s = pres.slides.add_slide(pres.slide_layouts[6])
    fundo(s, DARK)
    forma(s, 0.6, 0.55, 3.0, 1.05, WHITE, nome="Cartão do logo")
    pic = s.shapes.add_picture(str(IMG / "Unifesp_completa_policromia_RGB.png"), Inches(0.75), Inches(0.62),
                               height=Inches(0.9))
    pic._element.nvPicPr.cNvPr.set("descr", "Logo da UNIFESP")
    caixa(s, 0.6, 2.2, 11.8, 2.2, titulo_txt, pt=44, cor=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome="Título")
    caixa(s, 0.6, 4.5, 11.8, 0.7, sub, pt=22, cor="9AD1CF", nome="Subtítulo")
    caixa(s, 0.6, 5.7, 11.8, 1.1, [(autor, {"pt": 20, "bold": True, "cor": WHITE}),
                                   (parte, {"pt": 16, "cor": "C9D3DD"})], nome="Autor")
    return s


# =====================================================================  MARCOS
def parte_marcos(p):
    # 2 pergunta
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Um gene, vários processos ao mesmo tempo", 2)
    caixa(s, 0.6, 1.5, 5.6, 3.9, [
        ("Doença de Huntington", {"pt": 22, "bold": True, "cor": TEAL}),
        "Hereditária e neurodegenerativa, causada por repetições CAG no gene HTT.",
        "A partir de 40 repetições a doença se manifesta com certeza.",
        "Sinais: coreia, rigidez, perda cognitiva e emocional. Prevalência de cerca de 4,9 por 100 mil.",
    ], pt=18, espaco=10)
    forma(s, 0.6, 5.55, 5.6, 1.3, DARK, nome="Cartão da pergunta")
    caixa(s, 0.75, 5.6, 5.3, 1.2, "Nossa pergunta: quais proteínas sustentam essa rede e o que ocorre quando uma delas falha?",
          pt=18, cor=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome="Pergunta")
    imagem(s, "fig_cag.png", 6.5, 2.3, 6.3, 2.8, "Faixas de repetições CAG no gene HTT: normal até 26, intermediária 27 a 35, penetrância reduzida 36 a 39 e completa a partir de 40")
    caixa(s, 6.5, 5.2, 6.3, 0.5, "Fonte: elaborada pelos autores, com base no GeneReviews (Caron et al.)", pt=11, cor=MUTED)
    notas(s, "A huntingtina participa de transporte, transcrição, cálcio, mitocôndria, morte celular e autofagia. Por isso estudar só um gene não basta, o que importa é a rede ao redor dele.")

    # 3 metodo
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Como montamos a rede", 3)
    passos = [("1", "KEGG", "Mapa da Doença de Huntington (hsa05016): 7 grupos de proteínas"),
              ("2", "STRING", "Cada grupo consultado e expandido uma vez: 67 proteínas, mais o HTT"),
              ("3", "Filtro", "Só interações de alta confiança, pontuação ≥ 0,7"),
              ("4", "Cytoscape", "Rede final com 66 proteínas e 207 interações, layout e métricas")]
    for i, (n, t, d) in enumerate(passos):
        x = 0.6 + i * 3.1
        forma(s, x, 1.7, 2.85, 3.7, LIGHT, nome=f"Cartão passo {n}")
        c = forma(s, x + 0.2, 1.9, 0.7, 0.7, TEAL, tipo=MSO_SHAPE.OVAL, nome=f"Círculo {n}")
        caixa(s, x + 0.2, 1.9, 0.7, 0.7, n, pt=24, cor=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        caixa(s, x + 0.2, 2.8, 2.45, 0.6, t, pt=24, cor=DARK, bold=True, nome=f"Passo {n}")
        caixa(s, x + 0.2, 3.5, 2.45, 1.8, d, pt=16, nome=f"Descrição {n}")
    caixa(s, 0.6, 5.8, 12.1, 0.9, "As interações do STRING indicam associação funcional: a rede não tem direção nem sinal. O HTT foi adicionado manualmente. Dados do KEGG e do STRING acessados em 13 e 14 de novembro de 2026.",
          pt=16, cor=MUTED)
    notas(s, "O filtro de 0,7 vale para alta confiança. Sem ele eram 367 interações, com ele ficam 207. Conferimos os números no Cytoscape e depois em Python, e deram iguais.")

    # 4 rede
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "A rede do HTT", 4)
    imagem(s, "rede_modulos_h.png", 0.4, 1.25, 8.6, 5.7, "Rede PPI do HTT com 66 proteínas, colorida por módulo funcional e com o HTT no centro")
    stats = [("66", "proteínas"), ("207", "interações"), ("2,95", "passos entre duas proteínas, em média"),
             ("0,64", "agrupamento: vizinhos se ligam entre si")]
    for i, (g, l) in enumerate(stats):
        y = 1.4 + i * 1.12
        forma(s, 9.3, y, 3.45, 1.0, LIGHT, nome=f"Cartão {g}")
        caixa(s, 9.4, y + 0.05, 1.35, 0.9, g, pt=30, cor=TEAL, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome=f"Valor {g}")
        caixa(s, 10.75, y + 0.05, 1.95, 0.9, l, pt=13, anchor=MSO_ANCHOR.MIDDLE, nome=f"Legenda {g}")
    caixa(s, 9.3, 5.95, 3.45, 0.95, "O HTT, em preto, fica no centro e liga todos os módulos.", pt=15, cor=DARK, bold=True, nome="Leitura da figura")
    notas(s, "Tamanho do nó é a betweenness: quanto maior, mais caminhos passam por ele. O HTT é o maior. A rede é conexa e compacta: o diâmetro é 6 e o raio 3.")

    # 5 modulos
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Módulos funcionais, hubs e pontes", 5)
    imagem(s, "fig_grau.png", 0.6, 1.4, 7.6, 3.4, "Distribuição de graus e gráfico de grau contra betweenness das proteínas")
    cartao(s, 8.5, 1.5, 4.2, 1.6, "Q = 0,60", "modularidade dos 7 módulos funcionais (Louvain acha Q = 0,61)")
    cartao(s, 8.5, 3.3, 4.2, 1.6, "75%", "das arestas ficam dentro dos módulos (156 de 207)")
    caixa(s, 0.6, 5.1, 12.1, 1.8, [
        "TP53 tem mais conexões (grau 18), mas o HTT tem a maior betweenness (0,399), o dobro do TP53.",
        "SLC1A2, dos astrócitos, é a 3ª maior betweenness com apenas 7 conexões: é uma ponte.",
    ], pt=18, espaco=10, nome="Mensagem")
    notas(s, "Passo a palavra ao Vinícius: o que acontece se tirarmos essas pontes? A figura mostra que ter muitas conexões não é o mesmo que ser ponte.")


# =====================================================================  VINICIUS
def parte_vinicius(p):
    # 2 robustez
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Falha ao acaso é tolerada, ataque às pontes não", 2)
    imagem(s, "fig_robustez.png", 0.6, 1.4, 8.0, 3.4, "Maior componente conexo e eficiência da rede ao remover nós ao acaso, por grau e por betweenness")
    cartao(s, 9.0, 1.5, 3.7, 1.6, "82%", "da rede continua conectada após remover 10 nós ao acaso")
    cartao(s, 9.0, 3.3, 3.7, 1.6, "20%", "após remover os 10 nós de maior betweenness", cor=CORAL)
    caixa(s, 0.6, 5.2, 12.1, 1.6, [
        "Removemos nós de três formas e medimos quanto da rede continua conectada.",
        "É o comportamento esperado de redes com hubs: robustas ao acaso, frágeis a ataques dirigidos.",
    ], pt=18, espaco=10, nome="Mensagem")
    notas(s, "Ao acaso a rede quase não sente. Atacando as proteínas que são pontes, ela se desfaz em poucos passos. Isso aponta quais proteínas importam.")

    # 3 pontos criticos
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Os pontos críticos têm função fisiológica", 3)
    imagem(s, "rede_impacto_h.png", 0.4, 1.25, 8.0, 5.7, "Rede colorida pelo impacto da remoção de cada nó, com os pontos de articulação em losango")
    itens = [("SLC1A2", "Transportador (EAAT2) dos astrócitos que retira glutamato da sinapse. Sem ele, entra cálcio demais no neurônio.", "11,5%"),
             ("PPARGC1A", "Controla a produção de mitocôndrias. Sem ele, o neurônio perde energia (ATP).", "11,0%"),
             ("HTT", "Proteína de andaime do transporte, da transcrição e da sobrevivência neuronal.", "9,1%")]
    for i, (n, d, v) in enumerate(itens):
        y = 1.4 + i * 1.75
        forma(s, 8.6, y, 4.2, 1.6, LIGHT, nome=f"Cartão {n}")
        caixa(s, 8.7, y + 0.08, 1.6, 0.45, n, pt=17, cor=DARK, bold=True, nome=f"Nome {n}")
        caixa(s, 8.7, y + 0.6, 1.4, 0.7, v, pt=24, cor=CORAL, bold=True, nome=f"Valor {n}")
        caixa(s, 10.15, y + 0.08, 2.6, 1.45, d, pt=12, nome=f"Papel {n}")
    caixa(s, 8.6, 6.65, 4.2, 0.4, "Vermelho: perda de eficiência da rede ao remover o nó (TP53: 4,1%).", pt=10, cor=MUTED)
    notas(s, "Aqui entra a fisiologia. SLC1A2 e PPARGC1A são pontos de articulação: tirando qualquer um, uma parte da rede se separa. O SLC1A2 tem só 7 conexões e mesmo assim é o mais importante. Isso liga com excitotoxicidade e com o metabolismo energético do neurônio.")

    # 4 cascata
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Uma falha pode se espalhar pela rede", 4)
    imagem(s, "fig_cascata.png", 0.6, 1.4, 5.8, 5.4, "Tamanho médio da cascata de falha para quatro limiares")
    caixa(s, 6.8, 1.6, 5.9, 4.9, [
        ("Regra: um nó falha quando uma fração φ dos vizinhos já falhou.", {"bold": True}),
        "φ = 0,2: em média 19,9 nós falham. Começando pelo HTT, caem os 66.",
        "φ = 0,3: média de 3,0 nós.",
        "φ ≥ 0,4: a falha quase não se propaga.",
        ("A rede passa de estável a frágil em uma faixa estreita. O limiar é uma suposição nossa, por isso testamos vários.", {"cor": MUTED}),
    ], pt=18, espaco=10, nome="Resultados da cascata")
    notas(s, "É uma simulação de propagação, não um modelo da fisiologia. Mostra onde a rede é sensível.")

    # 5 solucao
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "Solução proposta: proteger o núcleo crítico", 5)
    caixa(s, 0.6, 1.3, 12.1, 0.6, "Em vez de perguntar o que cai, perguntamos o que proteger.", pt=20, cor=TEAL, bold=True, nome="Ideia")
    imagem(s, "fig_protecao.png", 0.6, 2.0, 7.6, 3.3, "Tamanho médio da cascata ao proteger de 0 a 5 proteínas, escolhidas ao acaso, por grau, por betweenness ou de forma gulosa")
    cartao(s, 8.5, 2.1, 4.2, 1.5, "−66%", "na cascata ao proteger 5 hubs: TP53, HTT, BECN1, MTOR e PPARGC1A", cor=TEAL, pt_g=36)
    cartao(s, 8.5, 3.75, 4.2, 1.5, "−17%", "ao proteger 5 proteínas sorteadas", cor=MUTED, pt_g=36)
    caixa(s, 0.6, 5.5, 12.1, 1.4, [
        "Resultado com φ = 0,2, o regime frágil. Proteger só o HDAC1 já reduz a cascata em 27%.",
        "A escolha gulosa, que testa proteína por proteína, não superou a escolha por grau com 5 proteínas.",
    ], pt=16, espaco=8, nome="Detalhes")
    notas(s, "Proteger significa manter a proteína funcionando, ou seja, ela não pode falhar na simulação. Biologicamente é uma hipótese de prioridade de alvos: preservar a função mitocondrial, sustentar a captação de glutamato, reduzir a fonte do problema, que é o HTT mutado. A figura compara quatro formas de escolher quem proteger.")

    # 6 limites
    s = p.slides.add_slide(p.slide_layouts[6]); titulo(s, "O que propomos e os limites", 6)
    forma(s, 0.6, 1.5, 6.0, 3.9, LIGHT, nome="Cartão propostas")
    caixa(s, 0.8, 1.6, 5.6, 0.6, "Hipóteses para testar no laboratório", pt=20, cor=TEAL, bold=True, nome="Título propostas")
    caixa(s, 0.8, 2.3, 5.6, 3.0, [
        "1. Preservar a função mitocondrial (PPARGC1A).",
        "2. Sustentar a captação de glutamato pelos astrócitos (SLC1A2).",
        "3. Reduzir a fonte do problema (HTT) e apoiar a autofagia (MTOR, BECN1).",
    ], pt=18, espaco=14, nome="Propostas")
    forma(s, 6.9, 1.5, 5.8, 3.9, LIGHT, nome="Cartão limites")
    caixa(s, 7.1, 1.6, 5.4, 0.6, "Limites", pt=22, cor=CORAL, bold=True, nome="Título limites")
    caixa(s, 7.1, 2.3, 5.4, 3.0, [
        "É uma análise computacional da estrutura, não um tratamento.",
        "A mutação age por ganho de função tóxico: remover o HTT testa a dependência da rede, não reproduz a doença.",
        "A rede não tem direção nem sinal, e o limiar da cascata é suposição.",
    ], pt=16, espaco=10, nome="Limites")
    forma(s, 0.6, 5.75, 12.1, 1.05, DARK, nome="Faixa final")
    caixa(s, 0.8, 5.8, 11.7, 0.95, "A rede indica onde olhar. A literatura experimental precisa confirmar.", pt=22, cor=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome="Mensagem final")
    notas(s, "Fechar dizendo: a rede indica onde olhar, e a literatura experimental precisa confirmar. Abrir para perguntas.")


def encerramento(p):
    s = p.slides.add_slide(p.slide_layouts[6])
    fundo(s, DARK)
    caixa(s, 0.6, 2.2, 12.1, 1.3, "Perguntas?", pt=54, cor=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, nome="Título")
    caixa(s, 0.6, 3.7, 12.1, 2.35, [
        ("A rede do HTT é robusta ao acaso e frágil nas pontes: HTT, PPARGC1A e SLC1A2.", {"pt": 22, "cor": "9AD1CF"}),
        ("Proteger o núcleo crítico contém a cascata na simulação. É uma hipótese para o laboratório.", {"pt": 22, "cor": "9AD1CF"}),
    ], espaco=10, nome="Resumo")
    caixa(s, 0.6, 6.2, 12.1, 0.6, "Vinícius Massaru Oliveira Tanaka e Marcos Magalhães", pt=16, cor="C9D3DD", nome="Autores")
    notas(s, "Fechar retomando as três pontes e a ideia de proteger o núcleo crítico. Abrir para perguntas.")


def montar():
    p = nova()
    s = capa(p, "Rede de interação do gene HTT na Doença de Huntington",
             "Hubs, robustez e uma estratégia de proteção",
             "Vinícius Massaru Oliveira Tanaka e Marcos Magalhães",
             "Introdução à Biologia de Sistemas, Prof. André Zelanis")
    notas(s, "Apresentação em dupla. O Marcos mostra como montamos a rede e como ela é por dentro. Eu mostro o que acontece quando ela falha e a solução que propomos.")
    n0 = len(p.slides)
    parte_marcos(p)
    n1 = len(p.slides)
    parte_vinicius(p)
    encerramento(p)
    # renumera e identifica a parte de cada slide
    for i, sl in enumerate(p.slides):
        parte = "Parte 1: Marcos" if n0 <= i < n1 else ("Parte 2: Vinícius" if n1 <= i < len(p.slides) - 1 else "")
        for sh in sl.shapes:
            if sh.name == "Número":
                sh.text_frame.paragraphs[0].runs[0].text = str(i + 1)
            if sh.name == "Rodapé" and parte:
                sh.text_frame.paragraphs[0].runs[0].text += f"  |  {parte}"
    p.save(AQUI / "Apresentacao_Huntington_unificada.pptx")


montar()
print("avisos:", AVISOS or "nenhum")
