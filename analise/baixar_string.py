"""Reconstroi a rede PPI do HTT (Huntington) pela API publica do STRING.

Entrada: as 67 proteinas listadas no documento do colega + HTT.
Saida: string_htt_score000.tsv (todas as arestas) e string_htt_score700.tsv (score >= 0,7).
"""
import csv
import io
import urllib.parse
import urllib.request
from pathlib import Path

PROTEINAS = """BMERB1 DCTN1 DCTN4 DCTN5 DCTN6 DNM1 HAP1 HIP1 KIF5A KLC4 BRMS1 CREBBP GSE1 HDAC1
PHF21B RCOR1 REST SAP30 SAP30L SIN3A CAMK2D DLG4 GRM1 GRM5 HOMER1 HOMER2 HOMER3 ITPR1 PLCB1
STX1A GABPB1 GPX5 GPX6 NRF1 PPARGC1A SOD1 SOD2 TFAM UCP3 BAD BAX BBC3 BCL2L2 BID CASP3 CASP9
HRK RTL10 TP53 ATG101 ATG14 BECN1 BECN2 MTOR NRBF2 PIK3C3 RUBCN ULK1 ULK2 ALDH1L1 GJB6
KCNJ10 MLC1 SLC1A2 SLC1A3 SLC6A11 SLC6A13""".split() + ["HTT"]

AQUI = Path(__file__).parent
url = "https://string-db.org/api/tsv/network"
dados = urllib.parse.urlencode({
    "identifiers": "\r".join(PROTEINAS),
    "species": 9606,
    "required_score": 0,
    "caller_identity": "unifesp_biosistemas",
}).encode()

with urllib.request.urlopen(urllib.request.Request(url, data=dados), timeout=60) as r:
    texto = r.read().decode("utf-8")

(AQUI / "string_htt_score000.tsv").write_text(texto, encoding="utf-8")
linhas = list(csv.DictReader(io.StringIO(texto), delimiter="\t"))
forte = [l for l in linhas if float(l["score"]) >= 0.7]
with open(AQUI / "string_htt_score700.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=linhas[0].keys(), delimiter="\t")
    w.writeheader()
    w.writerows(forte)

nos0 = {l["preferredName_A"] for l in linhas} | {l["preferredName_B"] for l in linhas}
nos7 = {l["preferredName_A"] for l in forte} | {l["preferredName_B"] for l in forte}
print("pedidas:", len(PROTEINAS))
print("score>=0:   nos", len(nos0), "arestas", len(linhas))
print("score>=0.7: nos", len(nos7), "arestas", len(forte))
print("nao retornadas:", sorted(set(PROTEINAS) - nos0))
