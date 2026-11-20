#!/usr/bin/env python3
"""Monta o conjunto-ouro da amostra principal e calcula o F1 do pipeline contra ele.

Uso:
  python3 construir_ouro.py <a1.xlsx> <a2.xlsx> <desempate.xlsx> <gabarito_desempate.csv>
                            <principal_gabarito.csv> <corpus.csv> <saida/> [reconciliacao_resultado.csv]

Regras (Protocolo, Seções 3 e 8):
  - NC de qualquer anotador externo: item fora das medidas, reportado à parte.
  - Acordo direto entre os externos: ouro.
  - Desacordo: terceiro voto cego; coincide com um externo -> maioria; não coincide -> sem maioria.
  - Sem maioria: reconciliação escrita dos dois externos (consolidar_reconciliacao.py), duas rodadas;
    consenso -> ouro (origem 'reconciliacao_escrita'); sem consenso -> fora do ouro. Argumento opcional.
  - Espaço de classes: 9 + RES. F1-macro do SVM contra o ouro com predições fora da dobra
    (StratifiedKFold 3, shuffle, seed 42) sobre os rotulados; IC 95% por bootstrap (2.000).
  - H6: confirmada se F1 e limite superior < 0,75; refutada se F1 e limite inferior > 0,75;
    inconclusiva se o IC contém 0,75.
"""
import sys, os, json
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score, precision_recall_fscore_support, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from medir_concordancia import ler_planilha, MAPA_LEXICO, CODIGOS, kappa_ic

SEED = 42
PARAMS = {"max_features": 2352, "ngram_max": 1, "sublinear_tf": True, "C": 0.8245163637337287}
RESIDUAL = "outros_institucional"
INV = {v: k for k, v in MAPA_LEXICO.items()}
N_BOOT = 2000


def f1_ic(y, p, labels, n_boot=N_BOOT, seed=SEED):
    y, p = np.asarray(y), np.asarray(p)
    f = f1_score(y, p, labels=labels, average="macro", zero_division=0)
    rng = np.random.default_rng(seed); n = len(y); bs = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        bs.append(f1_score(y[i], p[i], labels=labels, average="macro", zero_division=0))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return round(float(f), 4), round(float(lo), 4), round(float(hi), 4)


def veredito_h6(f, lo, hi, limiar=0.75):
    if hi < limiar: return "confirmada"
    if lo > limiar: return "refutada"
    return "inconclusiva"


def main(p1, p2, pdes, gab_des, gab_pri, corpus, saida, reconc=None):
    os.makedirs(saida, exist_ok=True)
    a1 = ler_planilha(p1, "a1"); a2 = ler_planilha(p2, "a2").drop(columns=["texto"])
    g = pd.read_csv(gab_pri); g["lexico"] = g["label_v3"].map(MAPA_LEXICO)
    df = a1.merge(a2, on="id_item").merge(g, on="id_item")

    # terceiro voto
    d3 = pd.read_excel(pdes, sheet_name="Anotação")
    d3 = d3[d3["id_item"].astype(str).str.match(r"^DES\d{4}$", na=False)].copy()
    chave = pd.read_csv(gab_des)  # id_desempate, id_item, classe_a1, classe_a2, lexico
    d3 = d3.rename(columns={"id_item": "id_desempate"}).merge(chave[["id_desempate", "id_item"]], on="id_desempate")
    d3["voto3"] = d3["classe"].astype(str).str.strip().str.upper()
    d3["conf3"] = pd.to_numeric(d3["confianca"], errors="coerce")
    df = df.merge(d3[["id_item", "voto3", "conf3", "misto", "subtipo", "observacoes"]].rename(
        columns={"misto": "misto_3", "subtipo": "subtipo_3", "observacoes": "obs_3"}), on="id_item", how="left")

    nc_ext = (df["classe_a1"] == "NC") | (df["classe_a2"] == "NC")
    acordo = (df["classe_a1"] == df["classe_a2"]) & ~nc_ext

    def origem(r):
        if r["classe_a1"] == "NC" or r["classe_a2"] == "NC": return "excluido_NC"
        if r["classe_a1"] == r["classe_a2"]: return "acordo_direto"
        if r["voto3"] == r["classe_a1"] or r["voto3"] == r["classe_a2"]: return "maioria_voto_cego"
        return "sem_maioria_reuniao"
    df["origem"] = df.apply(origem, axis=1)
    df["ouro"] = np.where(df["origem"] == "acordo_direto", df["classe_a1"],
                 np.where(df["origem"] == "maioria_voto_cego", df["voto3"], None))
    if reconc:  # reconciliação escrita dos itens sem maioria
        rc = pd.read_csv(reconc)[["id_item", "origem_rec", "ouro_rec"]]
        df = df.merge(rc, on="id_item", how="left")
        sm = df["origem"] == "sem_maioria_reuniao"
        df.loc[sm & df["origem_rec"].notna(), "origem"] = df.loc[sm & df["origem_rec"].notna(), "origem_rec"].replace(
            {"excluido_NC": "excluido_NC_reconciliacao", "divergente": "sem_consenso", "pendente": "sem_maioria_reuniao"})
        df.loc[df["origem"] == "reconciliacao_escrita", "ouro"] = df.loc[df["origem"] == "reconciliacao_escrita", "ouro_rec"]
        df = df.drop(columns=["origem_rec", "ouro_rec"])

    ouro = df[df["ouro"].notna()].copy()
    n = len(df)
    contagem = df["origem"].value_counts().to_dict()

    # kappas de controle: voto 3 × cada externo (só nos desempatados sem NC)
    des = df[df["voto3"].notna() & ~nc_ext]
    k3_a1 = cohen_kappa_score(des["voto3"], des["classe_a1"]); k3_a2 = cohen_kappa_score(des["voto3"], des["classe_a2"])
    coincide_a1 = int((des["voto3"] == des["classe_a1"]).sum()); coincide_a2 = int((des["voto3"] == des["classe_a2"]).sum())

    # externo × léxico, rotulados (sem NC)
    rot = df[~nc_ext & (df["lexico"] != "RES")]
    k_lex = {"a1": round(cohen_kappa_score(rot["classe_a1"], rot["lexico"]), 4),
             "a2": round(cohen_kappa_score(rot["classe_a2"], rot["lexico"]), 4), "n": int(len(rot))}

    # ---- predições fora da dobra do SVM (reprodução do notebook, célula da matriz de confusão) ----
    c = pd.read_csv(corpus).reset_index(drop=True); c["id_corpus"] = c.index
    tr = c[c["label_v3"] != RESIDUAL].reset_index()
    pipe = Pipeline([("vec", TfidfVectorizer(max_features=PARAMS["max_features"], ngram_range=(1, PARAMS["ngram_max"]),
                                             sublinear_tf=PARAMS["sublinear_tf"], strip_accents="unicode")),
                     ("clf", LinearSVC(C=PARAMS["C"], max_iter=800, random_state=SEED))])
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    yp = cross_val_predict(pipe, tr["text"].tolist(), tr["label_v3"].tolist(), cv=cv)
    f1_cv = f1_score(tr["label_v3"], yp, average="macro")
    pred = pd.DataFrame({"id_corpus": tr["id_corpus"].values, "svm_oof": pd.Series(yp).map(MAPA_LEXICO).values})
    ouro = ouro.merge(pred, on="id_corpus", how="left")
    # pipeline completo: rótulo do léxico (classe ou RES) é o que o artigo categoriza
    ouro["pipeline"] = ouro["lexico"]

    labels10 = CODIGOS  # 9 + RES
    labels9 = [c_ for c_ in CODIGOS if c_ != "RES"]
    res = {}
    # (1) pré-registrado: SVM OOF × ouro nos rotulados, espaço 10 códigos
    o_rot = ouro[ouro["svm_oof"].notna()]
    res["svm_vs_ouro_rotulados_10"] = dict(zip(("f1", "ic_lo", "ic_hi"), f1_ic(o_rot["ouro"], o_rot["svm_oof"], labels10)))
    res["svm_vs_ouro_rotulados_10"]["n"] = int(len(o_rot)); res["svm_vs_ouro_rotulados_10"]["acuracia"] = round(float((o_rot["ouro"] == o_rot["svm_oof"]).mean()), 4)
    # (2) sensibilidade: só itens cujo ouro é uma das nove classes
    o9 = o_rot[o_rot["ouro"].isin(labels9)]
    res["svm_vs_ouro_rotulados_9"] = dict(zip(("f1", "ic_lo", "ic_hi"), f1_ic(o9["ouro"], o9["svm_oof"], labels9))); res["svm_vs_ouro_rotulados_9"]["n"] = int(len(o9))
    # (3) pipeline completo (léxico, classe ou RES) × ouro, todos os itens do ouro
    res["lexico_vs_ouro_todos_10"] = dict(zip(("f1", "ic_lo", "ic_hi"), f1_ic(ouro["ouro"], ouro["pipeline"], labels10)))
    res["lexico_vs_ouro_todos_10"]["n"] = int(len(ouro)); res["lexico_vs_ouro_todos_10"]["acuracia"] = round(float((ouro["ouro"] == ouro["pipeline"]).mean()), 4)
    # (4) sensibilidade: só acordo direto
    od = o_rot[o_rot["origem"] == "acordo_direto"]
    res["svm_vs_ouro_acordo_direto_10"] = dict(zip(("f1", "ic_lo", "ic_hi"), f1_ic(od["ouro"], od["svm_oof"], labels10))); res["svm_vs_ouro_acordo_direto_10"]["n"] = int(len(od))
    # (5) sensibilidade: itens sem defeito de segmentação
    t = ouro["texto"].astype(str)
    ouro["ruido"] = ouro["inicia_minuscula"].astype(bool) | ouro["sem_pontuacao_final"].astype(bool) | t.str.contains("DESAFIOS À|RECONSTRUÇÃO|DO PAÍS E DO|O BRASIL AO|FINAL DE 2022", regex=True)
    ol = o_rot.merge(ouro[["id_item", "ruido"]], on="id_item"); ol = ol[~ol["ruido"]]
    res["svm_vs_ouro_limpos_10"] = dict(zip(("f1", "ic_lo", "ic_hi"), f1_ic(ol["ouro"], ol["svm_oof"], labels10))); res["svm_vs_ouro_limpos_10"]["n"] = int(len(ol))
    # (6) acurácia ponderada por pós-estratificação (estratos = classe do léxico)
    N_cls = c["label_v3"].map(MAPA_LEXICO).value_counts()
    n_cls = ouro["lexico"].value_counts()
    w = ouro["lexico"].map(lambda k: N_cls[k] / n_cls[k])
    res["acuracia_lexico_vs_ouro_ponderada_corpus"] = round(float(np.average((ouro["ouro"] == ouro["pipeline"]).astype(float), weights=w)), 4)
    # H6
    f, lo, hi = (res["svm_vs_ouro_rotulados_10"][k] for k in ("f1", "ic_lo", "ic_hi"))
    res["H6"] = {"regra": "F1-macro SVM OOF x ouro, 10 códigos, limiar 0,75", "veredito": veredito_h6(f, lo, hi)}
    res["f1_cv_lexico_reproduzido"] = round(float(f1_cv), 4)

    # por classe (pipeline completo × ouro)
    P, R, F, S = precision_recall_fscore_support(ouro["ouro"], ouro["pipeline"], labels=labels10, zero_division=0)
    por_classe = pd.DataFrame({"classe": labels10, "precisao": P.round(3), "revocacao": R.round(3), "f1": F.round(3), "n_ouro": S})
    P2, R2, F2, S2 = precision_recall_fscore_support(o_rot["ouro"], o_rot["svm_oof"], labels=labels10, zero_division=0)
    por_classe["f1_svm_rotulados"] = F2.round(3); por_classe["n_ouro_rotulados"] = S2
    por_classe.to_csv(os.path.join(saida, "por_classe.csv"), index=False)
    pd.DataFrame(confusion_matrix(ouro["ouro"], ouro["pipeline"], labels=labels10), index=[f"ouro_{l}" for l in labels10],
                 columns=[f"lex_{l}" for l in labels10]).to_csv(os.path.join(saida, "matriz_lexico_vs_ouro.csv"))

    # resíduo
    rs = ouro[ouro["lexico"] == "RES"]
    residuo = {"n_residuo_no_ouro": int(len(rs)), "recebe_classe": int((rs["ouro"] != "RES").sum()),
               "distribuicao_ouro": rs["ouro"].value_counts().to_dict()}

    resumo = {"n_itens": int(n), "origem_do_ouro": contagem, "n_ouro": int(len(ouro)),
              "taxa_desempate": {"maioria_voto_cego": round(contagem.get("maioria_voto_cego", 0) / n, 4),
                                 "sem_maioria": round(contagem.get("sem_maioria_reuniao", 0) / n, 4)},
              "voto3": {"n_desempatados": int(len(des)), "coincide_a1": coincide_a1, "coincide_a2": coincide_a2,
                        "kappa_voto3_a1": round(k3_a1, 4), "kappa_voto3_a2": round(k3_a2, 4),
                        "nc_voto3": int((df["voto3"] == "NC").sum())},
              "kappa_externo_lexico": k_lex, "residuo": residuo, "metricas": res,
              "distribuicao_ouro": ouro["ouro"].value_counts().to_dict(),
              "n_ruido_no_ouro_rotulado": int(ol.shape[0]) and int((o_rot.merge(ouro[["id_item", "ruido"]], on="id_item")["ruido"]).sum())}
    json.dump(resumo, open(os.path.join(saida, "resumo_ouro.json"), "w"), indent=2, ensure_ascii=False)
    cols = ["id_item", "id_corpus", "year", "lexico", "classe_a1", "confianca_a1", "classe_a2", "confianca_a2", "voto3", "conf3",
            "origem", "ouro", "svm_oof", "ruido", "n_words", "texto"]
    ouro[cols].to_csv(os.path.join(saida, "conjunto_ouro.csv"), index=False)
    df[df["origem"] == "sem_maioria_reuniao"][["id_item", "texto", "lexico", "classe_a1", "classe_a2", "voto3", "obs_3"]].to_csv(
        os.path.join(saida, "itens_sem_maioria.csv"), index=False)
    df[df["origem"] == "sem_consenso"][["id_item", "texto", "lexico", "classe_a1", "classe_a2", "voto3"]].to_csv(
        os.path.join(saida, "itens_sem_consenso.csv"), index=False)
    df[df["origem"] == "excluido_NC"][["id_item", "texto", "lexico", "classe_a1", "classe_a2", "voto3"]].to_csv(
        os.path.join(saida, "itens_excluidos_nc.csv"), index=False)
    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    print(por_classe.to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:9])
