# Huntington como rede

Análise de redes da Doença de Huntington: rede de interação proteica (PPI) do gene **HTT**, com hubs, robustez, cascata de falhas, uma estratégia de proteção e propriedades *small-world*. Projeto da disciplina Introdução à Biologia de Sistemas (UNIFESP, Prof. André Zelanis).

**Página interativa:** https://vimassaru.github.io/huntington-rede/

## Pergunta e conclusão

Quais proteínas sustentam a rede do HTT, o que acontece quando elas falham e o que vale proteger?

- Rede com 66 proteínas e 207 interações (STRING ≥ 0,7), agrupada (C = 0,64) e com caminhos curtos (L = 2,95): **small-world** (σ ≈ 5,6 contra rede aleatória).
- Organizada em 7 módulos funcionais (Q = 0,60; Louvain 0,61).
- **Robusta a falhas ao acaso, frágil às pontes**: HTT, SLC1A2 e PPARGC1A são pontos de articulação. O SLC1A2 tem só 7 conexões e remove 11,5% da eficiência; o TP53 (grau 18) remove 4,1%.
- Cascata com limiar φ = 0,2: caem em média 19,9 nós, e uma falha iniciada no HTT derruba os 66.
- **Solução:** proteger 5 hubs reduz a cascata em 66%, contra 17% com 5 proteínas sorteadas; só o HDAC1 já reduz 27%.
- É uma **hipótese computacional** para priorizar alvos, não um tratamento.

## Como chegamos a isso (reprodução)

```
pip install networkx pandas matplotlib numpy adjustText
cd analise
python baixar_string.py        # baixa a rede do STRING (os TSV já estão no repositório)
python analise_robustez.py     # métricas, módulos, robustez e cascata -> saida/
python protecao.py             # estratégia de proteção -> saida/protecao_resultados.csv
python figuras_rede.py         # figuras da rede (usa saida/posicoes_cytoscape.csv)
python exportar_site.py        # recalcula small-world e gera os dados de docs/data
```

`cytoscape_figuras.py` precisa do Cytoscape aberto e `py4cytoscape`; `saida/rede_HTT.cys` abre direto no Cytoscape.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `docs/` | Site (GitHub Pages): HTML, CSS, JS e d3; recalcula tudo no navegador |
| `analise/` | Scripts em Python, dados brutos do STRING (`*.tsv`) e `saida/` com tabelas e figuras |
| `relatorio/` | Relatório em LaTeX (`main.tex`) e imagens |
| `apresentacao/` | Slides e o script que os gera |
| `material_de_estudo/` | Mapa mental e cheat sheet |

## Métodos em resumo

1. **Dados.** Proteínas do mapa KEGG hsa05016 (7 grupos), consultadas no STRING (humano) com expansão de uma camada; o HTT foi acrescentado manualmente. Filtro de confiança ≥ 0,7. Acesso em 13 e 14 de novembro de 2026.
2. **Estrutura.** Grau, betweenness, agrupamento, caminho médio, diâmetro, pontos de articulação, modularidade.
3. **Robustez.** Remoção ao acaso (200 repetições), por grau e por betweenness; medimos o maior componente e a eficiência global.
4. **Cascata.** Modelo de limiar: o nó falha quando a fração φ de vizinhos falhos é atingida; testamos φ = 0,2 a 0,5 em todas as sementes.
5. **Proteção.** Repetimos a cascata com k nós que não podem falhar (aleatória, por grau, por betweenness, escolha gulosa).
6. **Small-world.** C e L comparados com 300 redes Erdős–Rényi e 300 com a mesma sequência de graus.

## Limitações

A mutação do HTT age por ganho de função tóxico (remover o HTT testa a dependência da rede, não reproduz a doença); a PPI não tem direção nem sinal; o limiar φ é uma suposição; com 66 nós não afirmamos que a rede é livre de escala; não há validação experimental.

## Fontes

- Mapa KEGG hsa05016 (Kanehisa Laboratories).
- STRING v12 (Szklarczyk et al., 2023), dados sob CC BY 4.0.
- GeneReviews: Huntington disease (Caron et al.).
- Medina et al. 2022 (prevalência).

## Licença e como citar

Código, dados processados, figuras e texto estão sob a licença MIT (arquivo `LICENSE`). Ao reutilizar qualquer parte, mantenha o aviso de copyright e credite os autores: Vinícius Massaru Oliveira Tanaka e Marcos Vinícius Magalhães Alves (UNIFESP, Introdução à Biologia de Sistemas, 2026). Os dados de interação vêm do STRING e do KEGG, que têm termos próprios de uso.
