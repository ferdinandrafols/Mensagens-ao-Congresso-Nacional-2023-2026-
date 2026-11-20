#!/usr/bin/env python3
"""Seleção da amostra para o conjunto-ouro (artigo RITA, V3).

Uso:
    python3 amostra_ouro.py corpus_v3.csv saida/

Desenho (decisões registradas na reunião de escopo, brief de 19/10/2026):
  - Quadro amostral: corpus limpo em nível de parágrafo, com rótulo do léxico V3.
  - Rodada piloto: N_PILOTO itens, sorteados primeiro e EXCLUÍDOS da medição.
  - Amostra principal: N_ROTULADOS parágrafos rotulados pelo léxico,
    estratificados por classe (alocação igual entre as 9 classes) e por ano
    (proporcional dentro da classe, com mínimo por célula), mais N_RESIDUO
    parágrafos do resíduo institucional, estratificados por ano.
  - Semente fixa. A ordem de apresentação ao anotador é aleatória e o arquivo
    do anotador NÃO contém rótulo nem ano.

Saídas (em `saida/`):
  piloto_anotador.csv, piloto_gabarito.csv,
  principal_anotador.csv, principal_gabarito.csv,
  resumo_alocacao.csv, parametros.json
"""
import sys, os, json, re, hashlib
import numpy as np
import pandas as pd

# ── Parâmetros ───────────────────────────────────────────────────────────────
SEED         = 42
N_PILOTO     = 50          # ~5 por classe + ~5 do resíduo
N_ROTULADOS  = 450         # 50 por classe
N_RESIDUO    = 90          # fatia do resíduo (20% do total rotulado)
MIN_POR_CELULA = 5         # mínimo por célula classe × ano, quando houver itens
MIN_PALAVRAS = 15          # abaixo disso a unidade é tratada como fragmento
RESIDUAL     = "outros_institucional"

_RE_FIM = re.compile(r"[.!?:;][\"'”’)\]]?\s*$")


def marcar_qualidade(df):
    """Sinais de segmentação defeituosa, para decisão explícita (não exclusão silenciosa)."""
    t = df["text"].astype(str)
    df["sem_pontuacao_final"] = ~t.str.contains(_RE_FIM.pattern, regex=True)
    df["inicia_minuscula"]    = t.str.match(r"^[a-záàâãéêíóôõúç]")
    df["parentese_aberto"]    = t.str.count(r"\(") > t.str.count(r"\)")
    df["fragmento"]           = (df["n_words"] < MIN_PALAVRAS) | df["parentese_aberto"]
    return df


def alocar(contagens: pd.Series, n: int, minimo: int) -> pd.Series:
    """Alocação proporcional com mínimo por estrato, limitada ao disponível."""
    contagens = contagens[contagens > 0]
    aloc = pd.Series(0, index=contagens.index, dtype=int)
    # 1) mínimo
    aloc[:] = np.minimum(minimo, contagens)
    resto = n - aloc.sum()
    if resto > 0:
        prop = contagens / contagens.sum()
        extra = np.floor(prop * resto).astype(int)
        aloc += extra
        aloc = np.minimum(aloc, contagens)
        # 2) distribui o que faltou pelos estratos com maior resto fracionário
        falta = n - aloc.sum()
        ordem = (prop * resto - extra).sort_values(ascending=False).index
        for idx in list(ordem) * 3:
            if falta <= 0:
                break
            if aloc[idx] < contagens[idx]:
                aloc[idx] += 1; falta -= 1
    return aloc


def sortear(df, rng, por_classe, n_res, minimo):
    """Sorteia itens estratificados; devolve DataFrame com coluna 'estrato'."""
    partes = []
    rot = df[df["label_v3"] != RESIDUAL]
    for classe, g in rot.groupby("label_v3"):
        aloc = alocar(g.groupby("year").size(), por_classe, minimo)
        for ano, k in aloc.items():
            cel = g[g["year"] == ano]
            idx = rng.choice(cel.index.values, size=int(k), replace=False)
            partes.append(df.loc[idx].assign(estrato=f"{classe}|{ano}"))
    res = df[df["label_v3"] == RESIDUAL]
    aloc = alocar(res.groupby("year").size(), n_res, minimo)
    for ano, k in aloc.items():
        cel = res[res["year"] == ano]
        idx = rng.choice(cel.index.values, size=int(k), replace=False)
        partes.append(df.loc[idx].assign(estrato=f"{RESIDUAL}|{ano}"))
    return pd.concat(partes)


def main(caminho_corpus, saida):
    os.makedirs(saida, exist_ok=True)
    df = pd.read_csv(caminho_corpus)
    df = df.reset_index(drop=True)
    df["id_corpus"] = df.index
    df = marcar_qualidade(df)

    sha = hashlib.sha256(open(caminho_corpus, "rb").read()).hexdigest()[:16]
    rng = np.random.default_rng(SEED)

    quadro = df[~df["fragmento"]].copy()
    excluidos = int(df["fragmento"].sum())

    # Piloto primeiro (≈ N_PILOTO/10 por classe e para o resíduo), depois principal sem o piloto
    por_classe_pil = max(1, round(N_PILOTO / 10))
    piloto = sortear(quadro, rng, por_classe=por_classe_pil, n_res=N_PILOTO - 9 * por_classe_pil, minimo=1)
    quadro_p = quadro.drop(piloto.index)
    principal = sortear(quadro_p, rng, por_classe=N_ROTULADOS // 9, n_res=N_RESIDUO, minimo=MIN_POR_CELULA)

    def exportar(amostra, nome):
        amostra = amostra.sample(frac=1.0, random_state=SEED).reset_index(drop=True)  # ordem aleatória
        amostra["id_item"] = [f"{nome[:3].upper()}{i+1:04d}" for i in range(len(amostra))]
        amostra[["id_item", "text"]].rename(columns={"text": "texto"}) \
            .to_csv(os.path.join(saida, f"{nome}_anotador.csv"), index=False)
        amostra[["id_item", "id_corpus", "year", "label_v3", "estrato", "n_words",
                 "sem_pontuacao_final", "inicia_minuscula"]] \
            .to_csv(os.path.join(saida, f"{nome}_gabarito.csv"), index=False)
        return amostra

    piloto = exportar(piloto, "piloto")
    principal = exportar(principal, "principal")

    resumo = (principal.assign(classe=principal["estrato"].str.split("|").str[0])
              .pivot_table(index="classe", columns="year", values="id_item", aggfunc="count", fill_value=0))
    resumo["total"] = resumo.sum(axis=1)
    resumo.to_csv(os.path.join(saida, "resumo_alocacao.csv"))

    params = {"seed": SEED, "corpus": os.path.basename(caminho_corpus), "corpus_sha256_16": sha,
              "n_corpus": int(len(df)), "n_quadro": int(len(quadro)), "fragmentos_excluidos": excluidos,
              "min_palavras": MIN_PALAVRAS, "n_piloto": int(len(piloto)), "n_principal": int(len(principal)),
              "n_principal_rotulados": int((principal["label_v3"] != RESIDUAL).sum()),
              "n_principal_residuo": int((principal["label_v3"] == RESIDUAL).sum()),
              "min_por_celula": MIN_POR_CELULA}
    json.dump(params, open(os.path.join(saida, "parametros.json"), "w"), indent=2, ensure_ascii=False)

    print(json.dumps(params, indent=2, ensure_ascii=False))
    print("\nAlocação da amostra principal (classe × ano):")
    print(resumo.to_string())
    print(f"\nSinais de qualidade na amostra principal: sem pontuação final = "
          f"{int(principal['sem_pontuacao_final'].sum())}, inicia em minúscula = "
          f"{int(principal['inicia_minuscula'].sum())}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2])
