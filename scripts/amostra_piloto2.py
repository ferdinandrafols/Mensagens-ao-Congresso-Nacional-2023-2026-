#!/usr/bin/env python3
"""Segundo piloto (confirmação da calibração): 20 parágrafos novos, fora do piloto e da principal.

Uso: python3 amostra_piloto2.py <corpus.csv> <pasta_da_amostra_v1>
Grava piloto2_anotador.csv e piloto2_gabarito.csv na mesma pasta (ids PIL0101…), com os mesmos
critérios de quadro de amostra_ouro.py (MIN_PALAVRAS, parêntese aberto) e semente própria.
Alocação: 2 por classe (proporcional por ano) e 2 do resíduo.
"""
import sys, os, json, hashlib
import numpy as np
import pandas as pd
import amostra_ouro as ao

SEED2 = 43
POR_CLASSE = 2
N_RES = 2
ID_INICIO = 101


def main(caminho_corpus, pasta):
    df = pd.read_csv(caminho_corpus).reset_index(drop=True)
    df["id_corpus"] = df.index
    df = ao.marcar_qualidade(df)
    sha = hashlib.sha256(open(caminho_corpus, "rb").read()).hexdigest()[:16]
    params_v1 = json.load(open(os.path.join(pasta, "parametros.json")))
    assert params_v1["corpus_sha256_16"] == sha, "corpus diferente do usado na amostra v1"

    usados = set()
    for nome in ("piloto", "principal"):
        usados |= set(pd.read_csv(os.path.join(pasta, f"{nome}_gabarito.csv"))["id_corpus"])
    quadro = df[~df["fragmento"] & ~df["id_corpus"].isin(usados)].copy()

    rng = np.random.default_rng(SEED2)
    # 1 item de 2023–2024 e 1 de 2025–2026 por classe e para o resíduo, para cobrir os dois
    # regimes de extração (o cabeçalho interpolado só ocorre em 2023)
    partes = []
    for classe, g in quadro.groupby("label_v3"):
        for anos in ((2023, 2024), (2025, 2026)):
            cel = g[g["year"].isin(anos)]
            idx = rng.choice(cel.index.values, size=1, replace=False)
            partes.append(quadro.loc[idx].assign(estrato=f"{classe}|{'-'.join(map(str, anos))}"))
    # Dois itens de ruído de extração, para testar a Regra 6: um com cabeçalho de página interpolado
    # (só em 2023) e um truncado na quebra de página (começa em minúscula). Vão identificados no gabarito.
    ja = pd.concat(partes).index
    cab = quadro[quadro["text"].str.contains("DESAFIOS À|RECONSTRUÇÃO|DO PAÍS E DO", regex=True) & ~quadro.index.isin(ja)]
    trunc = quadro[quadro["inicia_minuscula"] & ~quadro.index.isin(ja) & ~quadro.index.isin(cab.index)]
    partes.append(quadro.loc[rng.choice(cab.index.values, size=1)].assign(estrato="ruido|cabecalho"))
    partes.append(quadro.loc[rng.choice(trunc.index.values, size=1)].assign(estrato="ruido|truncado"))
    amostra = pd.concat(partes)
    amostra = amostra.sample(frac=1.0, random_state=SEED2).reset_index(drop=True)
    amostra["id_item"] = [f"PIL{ID_INICIO + i:04d}" for i in range(len(amostra))]
    amostra[["id_item", "text"]].rename(columns={"text": "texto"}) \
        .to_csv(os.path.join(pasta, "piloto2_anotador.csv"), index=False)
    amostra[["id_item", "id_corpus", "year", "label_v3", "estrato", "n_words",
             "sem_pontuacao_final", "inicia_minuscula"]] \
        .to_csv(os.path.join(pasta, "piloto2_gabarito.csv"), index=False)

    params = {"seed": SEED2, "corpus_sha256_16": sha, "n_quadro_disponivel": int(len(quadro)),
              "excluidos_por_ja_sorteados": int(len(usados)), "n_piloto2": int(len(amostra)),
              "por_classe": POR_CLASSE, "n_residuo": N_RES, "ids": f"PIL{ID_INICIO:04d}..PIL{ID_INICIO + len(amostra) - 1:04d}",
              "estratos": amostra["estrato"].value_counts().sort_index().to_dict(),
              "inicia_minuscula": int(amostra["inicia_minuscula"].sum())}
    json.dump(params, open(os.path.join(pasta, "parametros_piloto2.json"), "w"), indent=2, ensure_ascii=False)
    print(json.dumps(params, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
