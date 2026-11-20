#!/usr/bin/env python3
"""Material da reunião de calibração do piloto (conjunto-ouro RITA V3).

Uso: python3 calibracao_piloto.py <saida_medir/> <gabarito.csv> <destino/>
Lê desacordos.csv e resumo.json produzidos por medir_concordancia.py e grava:
  - calibracao_piloto_interno.xlsx  (com a classe do léxico; uso do autor)
  - calibracao_piloto_anotadores.xlsx (sem o léxico; para a reunião com os anotadores)
Cada desacordo recebe um tipo (NC, RES, classe×classe) e uma coluna amarela "decisão da reunião".
"""
import sys, os, json
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

FONTE = "Arial"
AMARELO = PatternFill("solid", fgColor="FFF2CC"); CINZA = PatternFill("solid", fgColor="EDEDED")
FINO = Side(style="thin", color="BFBFBF"); BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
CODIGOS = ["ECO", "SOC", "SAU", "EDU", "AGR", "EXT", "INF", "AMB", "GOV", "RES", "NC"]


def tipo(r):
    if r.classe_a1 == "NC" or r.classe_a2 == "NC":
        return "1. NC × classe"
    if r.classe_a1 == "RES" or r.classe_a2 == "RES":
        return "2. RES × classe"
    return "3. classe × classe"


def escreve_tabela(ws, linha, cabecalho, linhas, larguras=None, amarelas=()):
    for j, h in enumerate(cabecalho, 1):
        c = ws.cell(row=linha, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, row in enumerate(linhas, 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(row=linha + i, column=j, value=(None if pd.isna(v) else v)); c.border = BORDA
            c.font = Font(name=FONTE); c.alignment = Alignment(wrap_text=True, vertical="top")
            if j in amarelas: c.fill = AMARELO
    if larguras:
        for j, w in enumerate(larguras, 1):
            ws.column_dimensions[ws.cell(row=1, column=j).column_letter].width = w
    return linha + len(linhas) + 1


def main(saida_medir, gabarito, destino):
    os.makedirs(destino, exist_ok=True)
    r = json.load(open(os.path.join(saida_medir, "resumo.json")))
    d = pd.read_csv(os.path.join(saida_medir, "desacordos.csv"))
    d["tipo"] = d.apply(tipo, axis=1)
    d = d.sort_values(["tipo", "id_item"]).reset_index(drop=True)

    for versao, com_lexico in (("interno", True), ("anotadores", False)):
        wb = Workbook(); ws = wb.active; ws.title = "Resumo"
        ws["A1"] = "Piloto do conjunto-ouro RITA V3: medidas de concordância"; ws["A1"].font = Font(name=FONTE, bold=True, size=14)
        linhas = [
            ("Itens do piloto", r["n_itens"]),
            ("Itens com NC em pelo menos um anotador (excluídos das medidas)", f'{r["n_excluidos_nc"]} (anotador 1: {r["nc_a1"]}; anotador 2: {r["nc_a2"]})'),
            ("Itens válidos", r["n_validos"]),
            ("Concordância bruta", f'{r["concordancia_bruta"]:.2f}'),
            ("Kappa de Cohen (IC 95% bootstrap)", f'{r["kappa_cohen"]:.3f} [{r["kappa_ic95"][0]:.3f}; {r["kappa_ic95"][1]:.3f}]'),
            ("Alfa de Krippendorff (nominal)", f'{r["alfa_krippendorff"]:.3f}'),
            ("Kappa nos itens com confiança 3 pelos dois", f'{r["kappa_alta_confianca"]:.3f} (n = {r["n_alta_confianca"]})'),
            ("Limiar do protocolo para a amostra principal", "kappa ≥ 0,60"),
            ("Desacordos", f'{len(d)}: {d.tipo.value_counts().sort_index().to_dict()}'),
            ("Uso de RES nos itens válidos", f'anotador 1: {r["kappa_por_classe"].get("RES", {}).get("n_a1", 0)}; anotador 2: {r["kappa_por_classe"].get("RES", {}).get("n_a2", 0)}'),
            ("Uso de 'misto'", f'anotador 1: {r["misto_usado"]["a1"]}; anotador 2: {r["misto_usado"]["a2"]}'),
            ("Observações preenchidas", f'anotador 1: {r["observacoes"]["a1"]}; anotador 2: {r["observacoes"]["a2"]}'),
            ("Confiança média", f'anotador 1: {r["confianca_media"]["a1"]:.2f}; anotador 2: {r["confianca_media"]["a2"]:.2f}'),
        ]
        if com_lexico:
            lx = r["lexico"]
            linhas += [("Acordo com o léxico (itens rotulados, n = %d)" % lx["n_rotulados"],
                        f'anotador 1: {lx["acordo_a1_lexico"]:.2f} (kappa {lx["kappa_a1_lexico"]:.3f}); anotador 2: {lx["acordo_a2_lexico"]:.2f} (kappa {lx["kappa_a2_lexico"]:.3f})'),
                       ("Resíduo do léxico (n = %d)" % r["residuo"]["n"], f'os dois atribuíram classe aos {r["residuo"]["ambos_classificam_igual"]} itens, e a mesma classe')]
        fim = escreve_tabela(ws, 3, ["Medida", "Valor"], linhas, larguras=[58, 70])
        ws.cell(row=fim + 1, column=1, value="Kappa binário por classe (presença/ausência da classe)").font = Font(name=FONTE, bold=True, size=12)
        pc = [(c, v["kappa_binario"], v["n_a1"], v["n_a2"]) for c, v in r["kappa_por_classe"].items()]
        escreve_tabela(ws, fim + 2, ["Classe", "Kappa binário", "Usos anotador 1", "Usos anotador 2"], pc)

        ws2 = wb.create_sheet("Desacordos")
        ws2["A1"] = "Itens em desacordo, agrupados por tipo. Preencha a coluna amarela na reunião (classe acordada ou 'manter divergência')."
        ws2["A1"].font = Font(name=FONTE, bold=True); ws2.merge_cells("A1:N1")
        cab = ["tipo", "id_item", "texto"] + (["léxico"] if com_lexico else []) + [
            "classe A1", "conf. A1", "misto A1", "subtipo A1", "obs. A1",
            "classe A2", "conf. A2", "misto A2", "subtipo A2", "obs. A2", "decisão da reunião", "regra a ajustar"]
        cols = ["tipo", "id_item", "texto"] + (["lexico"] if com_lexico else []) + [
            "classe_a1", "confianca_a1", "misto_a1", "subtipo_a1", "observacoes_a1",
            "classe_a2", "confianca_a2", "misto_a2", "subtipo_a2", "observacoes_a2"]
        linhas = [list(x) + ["", ""] for x in d[cols].itertuples(index=False)]
        n_amar = len(cab) - 1
        escreve_tabela(ws2, 2, cab, linhas, amarelas=(n_amar, n_amar + 1))
        larg = {"A": 16, "B": 10, "C": 90}
        for L, w in larg.items(): ws2.column_dimensions[L].width = w
        for j in range(4, len(cab) + 1):
            L = ws2.cell(row=2, column=j).column_letter
            ws2.column_dimensions[L].width = 30 if cab[j - 1].startswith("obs") else 12
        ws2.column_dimensions[ws2.cell(row=2, column=n_amar).column_letter].width = 20
        ws2.column_dimensions[ws2.cell(row=2, column=n_amar + 1).column_letter].width = 16
        dv = DataValidation(type="list", formula1='"' + ",".join(CODIGOS + ["manter divergência"]) + '"', allow_blank=True)
        ws2.add_data_validation(dv)
        Ld = ws2.cell(row=2, column=n_amar).column_letter
        dv.add(f"{Ld}3:{Ld}{2 + len(d)}")
        ws2.freeze_panes = "D3"; ws2.auto_filter.ref = f"A2:{ws2.cell(row=2, column=len(cab)).column_letter}{2 + len(d)}"
        for i in range(3, 3 + len(d)): ws2.row_dimensions[i].height = 110

        nome = os.path.join(destino, f"calibracao_piloto_{versao}.xlsx")
        wb.save(nome); print("gravado", nome)


if __name__ == "__main__":
    main(*sys.argv[1:4])
