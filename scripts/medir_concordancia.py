#!/usr/bin/env python3
"""Medidas de concordância do conjunto-ouro (piloto ou principal).

Uso:
    python3 medir_concordancia.py <anotador1.xlsx> <anotador2.xlsx> <gabarito.csv> <saida/> [--desempate]

Lê a aba "Anotação" das duas planilhas devolvidas, cruza com o gabarito (classe do léxico,
ano, estrato) e produz:
  - resumo.json: concordância bruta, kappa de Cohen (IC 95% bootstrap), alfa de Krippendorff,
    kappa por classe, kappa de cada anotador com o léxico, NC, confiança, origem do ouro.
  - desacordos.csv e desacordos.xlsx: itens em desacordo, com textos, rótulos, confianças e
    observações (material da reunião de calibração / adjudicação).
  - matriz_a1_a2.csv: tabulação cruzada anotador 1 × anotador 2.
  - comparacao_lexico.csv: cada anotador × rótulo do léxico, nos itens rotulados.
  - com --desempate: planilha_desempate.xlsx para o terceiro voto cego (só id e texto,
    ordem aleatória, sem rótulos) e gabarito_desempate.csv (fechado).
NC é excluído das medidas de concordância e reportado à parte (protocolo, Seção 8).
"""
import sys, os, json
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

MAPA_LEXICO = {
    "economia_desenvolvimento": "ECO", "programas_sociais": "SOC", "saude": "SAU",
    "educacao_ciencia": "EDU", "reforma_agraria_agropecuaria": "AGR", "politica_externa": "EXT",
    "infraestrutura_logistica": "INF", "meio_ambiente_energia": "AMB",
    "governanca_institucional": "GOV", "outros_institucional": "RES",
}
CODIGOS = ["ECO", "SOC", "SAU", "EDU", "AGR", "EXT", "INF", "AMB", "GOV", "RES"]
SEED = 42


def ler_planilha(caminho, sufixo):
    df = pd.read_excel(caminho, sheet_name="Anotação", header=0)
    df = df[df["id_item"].astype(str).str.match(r"^(PIL|PRI|DES)\d{4}$", na=False)].copy()
    for c in ("classe", "misto", "subtipo", "observacoes"):
        df[c] = df[c].astype("string").str.strip()
    df["classe"] = df["classe"].str.upper()
    df["confianca"] = pd.to_numeric(df["confianca"], errors="coerce")
    df = df[["id_item", "texto", "classe", "confianca", "misto", "subtipo", "observacoes"]]
    return df.rename(columns={c: f"{c}_{sufixo}" for c in df.columns if c not in ("id_item", "texto")})


def alfa_krippendorff_nominal(a, b):
    """Alfa de Krippendorff nominal para dois codificadores sem faltantes."""
    a, b = np.asarray(a), np.asarray(b)
    vals = sorted(set(a) | set(b))
    idx = {v: i for i, v in enumerate(vals)}
    k = len(vals)
    coinc = np.zeros((k, k))
    for x, y in zip(a, b):
        coinc[idx[x], idx[y]] += 1
        coinc[idx[y], idx[x]] += 1
    n = coinc.sum()
    nc = coinc.sum(axis=1)
    Do = (n - np.trace(coinc)) / n
    De = (n**2 - (nc**2).sum()) / (n * (n - 1))
    return 1 - Do / De if De > 0 else float("nan")


def kappa_ic(a, b, n_boot=2000, seed=SEED):
    a, b = np.asarray(a), np.asarray(b)
    k = cohen_kappa_score(a, b)
    rng = np.random.default_rng(seed)
    bs = []
    n = len(a)
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        if len(set(a[i]) | set(b[i])) < 2:
            continue
        bs.append(cohen_kappa_score(a[i], b[i]))
    lo, hi = np.percentile(bs, [2.5, 97.5]) if bs else (float("nan"), float("nan"))
    return float(k), float(lo), float(hi)


def main(p1, p2, gab, saida, desempate=False):
    os.makedirs(saida, exist_ok=True)
    a1 = ler_planilha(p1, "a1")
    a2 = ler_planilha(p2, "a2").drop(columns=["texto"])
    g = pd.read_csv(gab)
    g["lexico"] = g["label_v3"].map(MAPA_LEXICO)
    df = a1.merge(a2, on="id_item", how="outer").merge(
        g[["id_item", "id_corpus", "year", "lexico", "estrato", "n_words"]], on="id_item", how="left")
    n = len(df)

    faltam = df[df["classe_a1"].isna() | df["classe_a2"].isna()]
    inval = df[~df["classe_a1"].isin(CODIGOS + ["NC"]) | ~df["classe_a2"].isin(CODIGOS + ["NC"])]
    nc1, nc2 = (df["classe_a1"] == "NC").sum(), (df["classe_a2"] == "NC").sum()
    nc_any = (df["classe_a1"] == "NC") | (df["classe_a2"] == "NC")

    val = df[~nc_any & df["classe_a1"].isin(CODIGOS) & df["classe_a2"].isin(CODIGOS)].copy()
    bruta = float((val["classe_a1"] == val["classe_a2"]).mean())
    k, lo, hi = kappa_ic(val["classe_a1"], val["classe_a2"])
    alfa = float(alfa_krippendorff_nominal(val["classe_a1"], val["classe_a2"]))

    por_classe = {}
    for c in CODIGOS:
        x, y = (val["classe_a1"] == c).astype(int), (val["classe_a2"] == c).astype(int)
        if x.sum() + y.sum() == 0:
            continue
        kc = cohen_kappa_score(x, y) if (x.nunique() > 1 or y.nunique() > 1) else float("nan")
        por_classe[c] = {"kappa_binario": round(float(kc), 3), "n_a1": int(x.sum()), "n_a2": int(y.sum())}

    # alta confiança nos dois
    alta = val[(val["confianca_a1"] == 3) & (val["confianca_a2"] == 3)]
    k_alta = cohen_kappa_score(alta["classe_a1"], alta["classe_a2"]) if len(alta) > 5 and alta["classe_a1"].nunique() > 1 else None

    # contra o léxico (só rotulados pelo léxico, i.e. estrato não residual)
    rot = val[val["lexico"].isin([c for c in CODIGOS if c != "RES"])]
    k_a1_lex = cohen_kappa_score(rot["classe_a1"], rot["lexico"]) if len(rot) else None
    k_a2_lex = cohen_kappa_score(rot["classe_a2"], rot["lexico"]) if len(rot) else None
    ac_a1_lex = float((rot["classe_a1"] == rot["lexico"]).mean()) if len(rot) else None
    ac_a2_lex = float((rot["classe_a2"] == rot["lexico"]).mean()) if len(rot) else None

    # resíduo: recuperação
    res = val[val["lexico"] == "RES"]
    rec = {
        "n": int(len(res)),
        "a1_classifica": int((res["classe_a1"] != "RES").sum()),
        "a2_classifica": int((res["classe_a2"] != "RES").sum()),
        "ambos_classificam_igual": int(((res["classe_a1"] != "RES") & (res["classe_a1"] == res["classe_a2"])).sum()),
        "subtipos_a1": res["subtipo_a1"].dropna().value_counts().to_dict(),
        "subtipos_a2": res["subtipo_a2"].dropna().value_counts().to_dict(),
    }

    # origem do ouro (sem desempate ainda)
    concord = val["classe_a1"] == val["classe_a2"]
    desac = df[~(df["classe_a1"] == df["classe_a2"])].copy()

    resumo = {
        "n_itens": int(n), "n_faltantes": int(len(faltam)), "n_codigos_invalidos": int(len(inval)),
        "nc_a1": int(nc1), "nc_a2": int(nc2), "n_excluidos_nc": int(nc_any.sum()),
        "n_validos": int(len(val)),
        "concordancia_bruta": round(bruta, 4),
        "kappa_cohen": round(k, 4), "kappa_ic95": [round(lo, 4), round(hi, 4)],
        "alfa_krippendorff": round(alfa, 4),
        "kappa_alta_confianca": (round(float(k_alta), 4) if k_alta is not None else None), "n_alta_confianca": int(len(alta)),
        "kappa_por_classe": por_classe,
        "lexico": {"n_rotulados": int(len(rot)),
                   "kappa_a1_lexico": (round(float(k_a1_lex), 4) if k_a1_lex is not None else None),
                   "kappa_a2_lexico": (round(float(k_a2_lex), 4) if k_a2_lex is not None else None),
                   "acordo_a1_lexico": (round(ac_a1_lex, 4) if ac_a1_lex is not None else None),
                   "acordo_a2_lexico": (round(ac_a2_lex, 4) if ac_a2_lex is not None else None)},
        "residuo": rec,
        "confianca_media": {"a1": round(float(df["confianca_a1"].mean()), 2), "a2": round(float(df["confianca_a2"].mean()), 2)},
        "misto_usado": {"a1": int(df["misto_a1"].notna().sum()), "a2": int(df["misto_a2"].notna().sum())},
        "observacoes": {"a1": int(df["observacoes_a1"].notna().sum()), "a2": int(df["observacoes_a2"].notna().sum())},
        "origem_ouro_parcial": {"concordancia_direta": int(concord.sum()), "em_desacordo": int(len(desac))},
    }
    json.dump(resumo, open(os.path.join(saida, "resumo.json"), "w"), indent=2, ensure_ascii=False)

    pd.crosstab(val["classe_a1"], val["classe_a2"]).to_csv(os.path.join(saida, "matriz_a1_a2.csv"))
    rot[["id_item", "lexico", "classe_a1", "classe_a2"]].to_csv(os.path.join(saida, "comparacao_lexico.csv"), index=False)

    cols = ["id_item", "texto", "lexico", "classe_a1", "confianca_a1", "misto_a1", "subtipo_a1", "observacoes_a1",
            "classe_a2", "confianca_a2", "misto_a2", "subtipo_a2", "observacoes_a2", "year", "n_words"]
    desac[cols].to_csv(os.path.join(saida, "desacordos.csv"), index=False)
    desac[cols].to_excel(os.path.join(saida, "desacordos.xlsx"), index=False)

    if desempate:
        rng = np.random.default_rng(SEED)
        d = desac[["id_item", "texto"]].sample(frac=1.0, random_state=SEED).reset_index(drop=True)
        d.insert(0, "id_desempate", [f"DES{i+1:04d}" for i in range(len(d))])
        chave = d[["id_desempate", "id_item"]].merge(desac[["id_item", "classe_a1", "classe_a2", "lexico"]], on="id_item")
        chave.to_csv(os.path.join(saida, "gabarito_desempate.csv"), index=False)
        out = d.drop(columns=["id_item"]).rename(columns={"id_desempate": "id_item"}).copy()
        out["classe"] = ""; out["confianca"] = ""; out["observacoes"] = ""
        out.to_excel(os.path.join(saida, "planilha_desempate.xlsx"), index=False)

    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    return resumo, desac


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], args[1], args[2], args[3], desempate="--desempate" in sys.argv)
