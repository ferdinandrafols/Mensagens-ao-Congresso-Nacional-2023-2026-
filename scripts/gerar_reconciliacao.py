#!/usr/bin/env python3
"""Planilhas de reconciliação escrita dos itens sem maioria (substitui a reunião ao vivo dos três).

Uso:
  python3 gerar_reconciliacao.py <itens_sem_maioria.csv> <saida/> [prazo]

Entrada: itens_sem_maioria.csv gerado por construir_ouro.py
         (id_item, texto, lexico, classe_a1, classe_a2, voto3, obs_3).
Saída:   reconciliacao_anotador1.xlsx, reconciliacao_anotador2.xlsx (idênticas; cada anotador recebe a sua),
         reconciliacao_gabarito.csv (chave REC -> PRI e qual leitura é de quem; NÃO compartilhar).

Desenho (Protocolo, Seção 8, desvio datado): as três leituras de cada item são mostradas anonimizadas
(Leitura A, B, C), em ordem sorteada por item (semente 42); o anotador não sabe qual é a sua, qual é
a do outro externo e qual é o terceiro voto. Cada externo decide de forma independente, com justificativa
obrigatória. Regra de decisão: códigos finais dos dois externos coincidem -> ouro (origem
'reconciliacao_escrita'); divergem -> segunda e última rodada com troca de justificativas; ainda
divergem -> fora do ouro ('sem_consenso'). O primeiro autor não vota nesta etapa.
"""
import sys, os
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_planilhas_anotacao import (CLASSES, REGRAS, SUBTIPOS, VERSAO, AMARELO, CINZA, BORDA, FONTE,
                                      aba_categorias)

NOME = dict(CLASSES)
SEED = 42

PASSOS = [
    "Leia o parágrafo como na anotação original: só o texto apresentado, com as regras da aba Regras e as definições da aba Categorias (instrumento v1.1, o mesmo que você usou).",
    "Leia as três leituras (A, B, C). Elas estão em ordem sorteada e sem identificação: uma é a sua, uma é a do outro anotador e uma é o voto de desempate. Não há leitura 'oficial' entre elas.",
    "Decida o código final. Você pode manter a sua leitura, adotar uma das outras duas ou dar um quarto código (inclusive NC, se o texto não permitir juízo). O critério é a regra, e não a contagem de leituras.",
    "Escreva a justificativa: uma linha, com o número da regra aplicada. Exemplo: 'Regra 2: a obra serve ao saneamento, INF'. Sem justificativa a linha não conta.",
    "Preencha confiança (1 a 3). 'misto' só em empate real (Regra 3), 'subtipo' só para RES e NC, como antes.",
    "Trabalhe sozinho: não converse com o outro anotador sobre os itens, não consulte internet, o artigo ou listas de termos. O que você já sabe sobre siglas e programas vale (Regra 7).",
    "Registre as sessões no fim desta aba e devolva a planilha com o seu nome no arquivo.",
]

REGRA_DECISAO = [
    "Os códigos finais dos dois anotadores externos definem o resultado de cada parágrafo.",
    "Se coincidirem, o parágrafo entra no conjunto-ouro com a origem 'reconciliação escrita'.",
    "Se divergirem, haverá uma segunda e última rodada, só com esses parágrafos: cada um lê a justificativa do outro (sem o nome) e pode mudar o código uma vez.",
    "Se ainda assim divergirem, o parágrafo fica fora do conjunto-ouro, registrado como 'sem consenso'. Isso é um resultado legítimo: diz que o esquema de classes não decide aquele texto.",
    "O voto de desempate não participa desta etapa, e o primeiro autor não vota.",
    "Esta etapa não altera a sua anotação original nem as medidas de concordância já calculadas; ela só completa o conjunto-ouro.",
]

COLS = ["id_item", "texto", "leitura_A", "leitura_B", "leitura_C",
        "codigo_final", "confianca", "misto", "subtipo", "justificativa", "observacoes"]
DICAS = ["", "leia só este texto", "sorteada", "sorteada", "sorteada",
         "um código (lista): ECO SOC SAU EDU AGR EXT INF AMB GOV RES NC",
         "3 alta · 2 média · 1 baixa", "só em empate real (Regra 3)",
         "só RES e NC", "obrigatória: uma linha com o número da regra", "opcional"]


def aba_instrucoes(wb, n, prazo):
    ws = wb.active; ws.title = "Instruções"
    ws["A1"] = f"Conjunto-ouro RITA V3 · Reconciliação dos parágrafos com três leituras ({n} parágrafos)"
    ws["A1"].font = Font(name=FONTE, bold=True, size=14)
    ws["A2"] = f"Instrumento {VERSAO}. Prazo de devolução: {prazo}. Tempo estimado: cerca de uma hora."
    ws["A2"].font = Font(name=FONTE, italic=True, color="595959"); ws.merge_cells("A2:C2")
    r = 4
    ws.cell(row=r, column=1, value="Por que esta planilha").font = Font(name=FONTE, bold=True, size=12); r += 1
    txt = ("Na amostra principal, 540 parágrafos foram anotados por vocês dois. Em 343 houve acordo direto. Nos desacordos, "
           "um terceiro voto cego decidiu por maioria em 153. Em {n} parágrafos as três leituras foram diferentes entre si, "
           "e nenhuma maioria se formou. O protocolo previa uma reunião dos três para esses casos; em vez da reunião, cada um "
           "de vocês reavalia os {n} parágrafos por escrito, de forma independente, vendo as três leituras. A decisão escrita "
           "deixa registro, evita que a conversa seja decidida por quem fala mais e mantém o primeiro autor fora do voto.").format(n=n)
    c = ws.cell(row=r, column=1, value=txt); c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); ws.row_dimensions[r].height = 80; r += 2
    ws.cell(row=r, column=1, value="Passo a passo").font = Font(name=FONTE, bold=True, size=12); r += 1
    for i, t in enumerate(PASSOS, 1):
        c = ws.cell(row=r, column=1, value=f"{i}. {t}"); c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); ws.row_dimensions[r].height = 34; r += 1
    r += 1
    ws.cell(row=r, column=1, value="Como o resultado é decidido (regra fixada antes de abrir as planilhas)").font = Font(name=FONTE, bold=True, size=12); r += 1
    for t in REGRA_DECISAO:
        c = ws.cell(row=r, column=1, value="• " + t); c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); ws.row_dimensions[r].height = 30; r += 1
    r += 1
    ws.cell(row=r, column=1, value="O que cada coluna significa").font = Font(name=FONTE, bold=True, size=12); r += 1
    for j, h in enumerate(["Coluna", "Quem preenche", "Significado"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    desc = [
        ("id_item", "sistema", "Identificador REC0001… Não alterar. Não corresponde ao número da planilha original."),
        ("texto", "sistema", "Texto do parágrafo, o mesmo da anotação original. Única base para a decisão."),
        ("leitura_A / B / C", "sistema", "As três leituras do parágrafo (código e nome da classe), em ordem sorteada e sem identificação."),
        ("codigo_final", "anotador", "Obrigatória. Um código da lista. Pode coincidir com qualquer leitura ou ser outro."),
        ("confianca", "anotador", "Obrigatória. 1 baixa, 2 média, 3 alta."),
        ("misto", "anotador", "Opcional. Só em empate real entre dois temas (Regra 3): a segunda classe."),
        ("subtipo", "anotador", "Só para RES (geral ou tema fora do esquema) e NC (fragmento, editorial, outro)."),
        ("justificativa", "anotador", "Obrigatória. Uma linha com o número da regra e o motivo. É o que o outro anotador lerá se houver segunda rodada."),
        ("observacoes", "anotador", "Opcional: defeito do texto (truncado, cabeçalho misturado), termo desconhecido, discordância com o esquema."),
    ]
    for col, quem, d in desc:
        for j, v in enumerate((col, quem, d), 1):
            c = ws.cell(row=r, column=j, value=v); c.border = BORDA; c.alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Exemplo de preenchimento (ilustrativo, não é item da amostra)").font = Font(name=FONTE, bold=True, size=12); r += 1
    for j, h in enumerate(COLS, 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    ex = ["EX0001", "O BNDES liberou R$ 2 bilhões para obras de saneamento em 120 municípios, com prioridade às regiões de maior déficit.",
          "ECO (Economia e desenvolvimento)", "INF (Infraestrutura logística)", "GOV (Governança institucional)",
          "INF", 3, "", "", "Regra 2: o crédito é instrumento; a finalidade é saneamento, INF", ""]
    for j, v in enumerate(ex, 1):
        c = ws.cell(row=r, column=j, value=v); c.border = BORDA; c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = 48; r += 2
    ws.cell(row=r, column=1, value="Registro de sessões").font = Font(name=FONTE, bold=True, size=12); r += 1
    for j, h in enumerate(["Data", "Início", "Fim", "Itens", "Observações"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for k in range(1, 5):
        for j in range(1, 6):
            c = ws.cell(row=r + k, column=j); c.fill = AMARELO; c.border = BORDA
    ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 60; ws.column_dimensions["C"].width = 80
    for col in "DEFGHIJK": ws.column_dimensions[col].width = 14
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and not c.font.bold: c.font = Font(name=FONTE)
    return ws


def aba_regras(wb):
    ws = wb.create_sheet("Regras")
    ws["A1"] = "Regras de decisão (aplique na ordem: 1, 2 e só então 3)"; ws["A1"].font = Font(name=FONTE, bold=True, size=14)
    for j, h in enumerate(["Regra", "O que diz", "Exemplo (ilustrativo; não é item da amostra)"], 1):
        c = ws.cell(row=3, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for i, (nome, texto, exemplo) in enumerate(REGRAS, start=4):
        for j, v in enumerate((nome, texto, exemplo), 1):
            c = ws.cell(row=i, column=j, value=v); c.border = BORDA; c.font = Font(name=FONTE, bold=(j == 1))
            c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 26; ws.column_dimensions["B"].width = 70; ws.column_dimensions["C"].width = 80
    ws.freeze_panes = "A4"
    return ws


def aba_reconciliacao(wb, df):
    ws = wb.create_sheet("Reconciliação")
    for j, h in enumerate(COLS, 1):
        c = ws.cell(row=1, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for j, d in enumerate(DICAS, 1):
        c = ws.cell(row=2, column=j, value=d); c.font = Font(name=FONTE, italic=True, size=9, color="595959")
        c.fill = CINZA; c.border = BORDA; c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[2].height = 30
    for i, (_, row) in enumerate(df.iterrows(), start=3):
        vals = [row["id_rec"], row["texto"]] + [f"{row[k]} ({NOME[row[k]]})" for k in ("leitura_A", "leitura_B", "leitura_C")]
        for j, v in enumerate(vals, 1): ws.cell(row=i, column=j, value=v)
        for j in range(1, len(COLS) + 1):
            c = ws.cell(row=i, column=j); c.border = BORDA; c.font = Font(name=FONTE)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j >= 6: c.fill = AMARELO
    n = len(df); ult = n + 2
    dv_classe = DataValidation(type="list", formula1='"' + ",".join(c for c, _ in CLASSES) + '"', allow_blank=True,
                               showErrorMessage=True, errorTitle="Código inválido", error="Escolha um código da lista.")
    dv_conf = DataValidation(type="list", formula1='"1,2,3"', allow_blank=True, showErrorMessage=True,
                             errorTitle="Valor inválido", error="Use 1, 2 ou 3.")
    dv_misto = DataValidation(type="list", formula1='"' + ",".join(c for c, _ in CLASSES[:9]) + '"', allow_blank=True)
    dv_sub = DataValidation(type="list", formula1='"' + ",".join(SUBTIPOS) + '"', allow_blank=True, showErrorMessage=False)
    for dv, col in ((dv_classe, "F"), (dv_conf, "G"), (dv_misto, "H"), (dv_sub, "I")):
        dv.add(f"{col}3:{col}{ult}"); ws.add_data_validation(dv)
    ws.cell(row=ult + 2, column=1, value="Decididos:").font = Font(name=FONTE, bold=True)
    ws.cell(row=ult + 2, column=2, value=f'=COUNTA(F3:F{ult})&" de {n}  ·  justificativas: "&COUNTA(J3:J{ult})&" de {n}"').font = Font(name=FONTE)
    for col, w in zip("ABCDEFGHIJK", (10, 80, 24, 24, 24, 12, 10, 8, 14, 50, 30)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "C3"; ws.auto_filter.ref = f"A2:K{ult}"
    return ws


def preparar(df, seed=SEED):
    rng = np.random.default_rng(seed)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df["id_rec"] = [f"REC{i:04d}" for i in range(1, len(df) + 1)]
    quem = ["a1", "a2", "voto3"]; cols = {"a1": "classe_a1", "a2": "classe_a2", "voto3": "voto3"}
    ordem = []
    for _ in range(len(df)):
        o = list(rng.permutation(quem)); ordem.append(o)
    for letra, k in zip("ABC", range(3)):
        df[f"leitura_{letra}"] = [r[cols[o[k]]] for r, o in zip(df.to_dict("records"), ordem)]
        df[f"quem_{letra}"] = [o[k] for o in ordem]
    return df


if __name__ == "__main__":
    entrada, saida = sys.argv[1], sys.argv[2]
    prazo = sys.argv[3] if len(sys.argv) > 3 else "13/11/2026"
    os.makedirs(saida, exist_ok=True)
    df = preparar(pd.read_csv(entrada))
    assert (df[["classe_a1", "classe_a2", "voto3"]].nunique(axis=1) == 3).all(), "item com leituras repetidas"
    for anot in (1, 2):
        wb = Workbook(); aba_instrucoes(wb, len(df), prazo); aba_regras(wb); aba_categorias(wb); aba_reconciliacao(wb, df)
        dest = os.path.join(saida, f"reconciliacao_anotador{anot}.xlsx"); wb.save(dest); print("✓", dest)
    gab = df[["id_rec", "id_item", "lexico", "classe_a1", "classe_a2", "voto3", "leitura_A", "leitura_B", "leitura_C",
              "quem_A", "quem_B", "quem_C"]]
    gab.to_csv(os.path.join(saida, "reconciliacao_gabarito.csv"), index=False); print("✓ gabarito (não compartilhar)")
