#!/usr/bin/env python3
"""Consolida a reconciliação escrita dos itens sem maioria.

Uso:
  rodada 1: python3 consolidar_reconciliacao.py <rec_anotador1.xlsx> <rec_anotador2.xlsx> <reconciliacao_gabarito.csv> <saida/>
  rodada 2: python3 consolidar_reconciliacao.py <rec2_anotador1.xlsx> <rec2_anotador2.xlsx> <reconciliacao_gabarito.csv> <saida/> --rodada2 <resultado_rodada1.csv>

Regra de decisão (fixada antes de abrir as planilhas; Protocolo, Seção 8, desvio datado):
  - códigos finais dos dois externos coincidem -> ouro, origem 'reconciliacao_escrita' (rodada 1 ou 2);
  - divergem na rodada 1 -> gera planilhas da rodada 2 com a justificativa do outro (sem nome);
  - divergem na rodada 2 -> 'sem_consenso', fora do ouro;
  - NC de qualquer um dos dois -> 'excluido_NC' (mesma regra da amostra principal).
Saída: reconciliacao_resultado.csv (id_item, final_a1, final_a2, ouro_rec, origem_rec, rodada), que
construir_ouro.py lê como argumento opcional. O primeiro autor não vota.
"""
import sys, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_planilhas_anotacao import CLASSES, SUBTIPOS, AMARELO, CINZA, BORDA, FONTE, aba_categorias
from gerar_reconciliacao import aba_regras, NOME

VALIDOS = {c for c, _ in CLASSES}


def ler(path, suf):
    d = pd.read_excel(path, sheet_name="Reconciliação", header=0)
    d = d[d["id_item"].astype(str).str.match(r"^REC\d{4}$", na=False)].copy()
    d["codigo_final"] = d["codigo_final"].astype(str).str.strip().str.upper().replace({"NAN": None})
    inval = d[d["codigo_final"].notna() & ~d["codigo_final"].isin(VALIDOS)]
    if len(inval): print(f"AVISO {suf}: códigos inválidos:", inval[["id_item", "codigo_final"]].values.tolist())
    falt = d[d["codigo_final"].isna()]["id_item"].tolist()
    if falt: print(f"AVISO {suf}: {len(falt)} itens sem código final:", falt)
    sem_just = d[d["codigo_final"].notna() & d["justificativa"].isna()]["id_item"].tolist()
    if sem_just: print(f"AVISO {suf}: {len(sem_just)} itens sem justificativa (não contam):", sem_just)
    d.loc[d["justificativa"].isna(), "codigo_final"] = None
    return d.rename(columns={"id_item": "id_rec"})[["id_rec", "texto", "codigo_final", "confianca", "misto", "justificativa", "observacoes"]].rename(
        columns={c: f"{c}_{suf}" for c in ("codigo_final", "confianca", "misto", "justificativa", "observacoes")})


def planilha_rodada2(df, saida, anot, prazo="16/11/2026"):
    """Para o anotador `anot`: itens divergentes com a justificativa do outro, sem nome."""
    outro = "a2" if anot == 1 else "a1"; meu = "a1" if anot == 1 else "a2"
    wb = Workbook(); ws = wb.active; ws.title = "Instruções"
    ws["A1"] = f"Reconciliação, segunda e última rodada ({len(df)} parágrafos)"; ws["A1"].font = Font(name=FONTE, bold=True, size=14)
    linhas = [
        f"Nestes parágrafos os códigos finais dos dois anotadores divergiram na primeira rodada. Prazo: {prazo}.",
        "Você vê o seu código e a sua justificativa, e o código e a justificativa do outro anotador (sem nome). Releia o texto e as duas justificativas à luz das regras.",
        "Pode manter o seu código ou mudar uma vez. Preencha 'codigo_final_2' e 'justificativa_2' (obrigatórias), mesmo que mantenha.",
        "Se os dois códigos coincidirem, o parágrafo entra no conjunto-ouro. Se divergirem, fica fora, registrado como 'sem consenso'. Não há terceira rodada e não há voto do primeiro autor.",
        "Mesmas condições: sozinho, sem internet, sem conversar com o outro anotador sobre os itens.",
    ]
    for i, t in enumerate(linhas, start=3):
        c = ws.cell(row=i, column=1, value="• " + t); c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = Font(name=FONTE)
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3); ws.row_dimensions[i].height = 32
    ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 40; ws.column_dimensions["C"].width = 40
    aba_regras(wb); aba_categorias(wb)
    ws = wb.create_sheet("Rodada 2")
    cols = ["id_item", "texto", "meu_codigo", "minha_justificativa", "codigo_do_outro", "justificativa_do_outro",
            "codigo_final_2", "confianca_2", "justificativa_2"]
    for j, h in enumerate(cols, 1):
        c = ws.cell(row=1, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for i, r in enumerate(df.to_dict("records"), start=2):
        vals = [r["id_rec"], r["texto"], f'{r[f"codigo_final_{meu}"]} ({NOME[r[f"codigo_final_{meu}"]]})', r[f"justificativa_{meu}"],
                f'{r[f"codigo_final_{outro}"]} ({NOME[r[f"codigo_final_{outro}"]]})', r[f"justificativa_{outro}"], None, None, None]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=i, column=j, value=v); c.border = BORDA; c.font = Font(name=FONTE)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j >= 7: c.fill = AMARELO
    ult = len(df) + 1
    dv = DataValidation(type="list", formula1='"' + ",".join(VALIDOS) + '"', allow_blank=True); dv.add(f"G2:G{ult}"); ws.add_data_validation(dv)
    dv2 = DataValidation(type="list", formula1='"1,2,3"', allow_blank=True); dv2.add(f"H2:H{ult}"); ws.add_data_validation(dv2)
    for col, w in zip("ABCDEFGHI", (10, 70, 22, 40, 22, 40, 14, 10, 45)): ws.column_dimensions[col].width = w
    ws.freeze_panes = "C2"
    dest = os.path.join(saida, f"reconciliacao_rodada2_anotador{anot}.xlsx"); wb.save(dest); print("✓", dest)


def main(p1, p2, gab, saida, rodada2=None):
    os.makedirs(saida, exist_ok=True)
    g = pd.read_csv(gab)
    if rodada2 is None:
        d = ler(p1, "a1").merge(ler(p2, "a2").drop(columns=["texto"]), on="id_rec").merge(g, on="id_rec")
        rod = 1
    else:
        r1 = pd.read_csv(rodada2)
        def ler2(path, suf):
            x = pd.read_excel(path, sheet_name="Rodada 2")
            x = x[x["id_item"].astype(str).str.match(r"^REC\d{4}$", na=False)]
            x["codigo_final_2"] = x["codigo_final_2"].astype(str).str.strip().str.upper().replace({"NAN": None})
            x.loc[x["justificativa_2"].isna(), "codigo_final_2"] = None
            return x.rename(columns={"id_item": "id_rec", "codigo_final_2": f"codigo_final_{suf}", "justificativa_2": f"justificativa_{suf}"})[
                ["id_rec", f"codigo_final_{suf}", f"justificativa_{suf}"]]
        d = ler2(p1, "a1").merge(ler2(p2, "a2"), on="id_rec").merge(g, on="id_rec")
        d = d.merge(r1[["id_rec", "texto"]], on="id_rec", how="left") if "texto" in r1.columns else d
        rod = 2
    a, b = d["codigo_final_a1"], d["codigo_final_a2"]
    d["origem_rec"] = "pendente"
    d.loc[a.notna() & b.notna() & (a == b) & (a != "NC"), "origem_rec"] = "reconciliacao_escrita"
    d.loc[(a == "NC") | (b == "NC"), "origem_rec"] = "excluido_NC"
    d.loc[a.notna() & b.notna() & (a != b) & (a != "NC") & (b != "NC"), "origem_rec"] = "divergente" if rod == 1 else "sem_consenso"
    d["ouro_rec"] = d["codigo_final_a1"].where(d["origem_rec"] == "reconciliacao_escrita")
    d["rodada"] = rod
    cont = d["origem_rec"].value_counts().to_dict(); print(f"Rodada {rod}:", cont)
    for suf, col in (("a1", "classe_a1"), ("a2", "classe_a2")):
        manteve = int((d[f"codigo_final_{suf}"] == d[col]).sum()); adotou3 = int((d[f"codigo_final_{suf}"] == d["voto3"]).sum())
        outro = "classe_a2" if suf == "a1" else "classe_a1"; adotou_outro = int((d[f"codigo_final_{suf}"] == d[outro]).sum())
        print(f"  {suf}: manteve a própria leitura {manteve}; adotou a do outro externo {adotou_outro}; adotou o voto de desempate {adotou3}")
    if rod == 1:
        div = d[d["origem_rec"] == "divergente"]
        if len(div):
            for anot in (1, 2): planilha_rodada2(div, saida, anot)
    out = d[["id_rec", "id_item", "texto", "classe_a1", "classe_a2", "voto3", "codigo_final_a1", "codigo_final_a2",
             "justificativa_a1", "justificativa_a2", "origem_rec", "ouro_rec", "rodada"]] if "texto" in d.columns else d
    if rod == 2:
        r1 = pd.read_csv(rodada2)
        fechados = r1[r1["origem_rec"] != "divergente"]
        out = pd.concat([fechados, out[out["id_rec"].isin(r1[r1["origem_rec"] == "divergente"]["id_rec"])]], ignore_index=True)
    dest = os.path.join(saida, "reconciliacao_resultado.csv"); out.to_csv(dest, index=False); print("✓", dest)


if __name__ == "__main__":
    args = sys.argv[1:]
    r2 = args[args.index("--rodada2") + 1] if "--rodada2" in args else None
    main(*args[:4], rodada2=r2)
