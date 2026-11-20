"""Experimento complementar (não pré-registrado): SVM treinado nos rótulos humanos do conjunto-ouro,
validação cruzada estratificada repetida 5 x 10. Vetorizador do pipeline (TF-IDF, max_features 2.352,
unigramas, sublinear, strip_accents unicode), com vocabulário e IDF ajustados no corpus inteiro, sem
supervisão (os textos dos itens de teste entram no ajuste do vocabulário, não no treino do classificador);
C do AG. Reporta média e amplitude entre repetições e IC 95% por bootstrap sobre itens (2.000 reamostras,
semente 42) das predições fora da dobra. Variantes: C = 1, vocabulário ajustado só nas dobras de treino,
nove classes; referência (o rótulo do léxico como alvo) e curva de aprendizado.
Uso: python3 treinar_no_ouro.py conjunto_ouro.csv corpus_v3_paragrafo.csv"""
import sys, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import f1_score, accuracy_score
g = pd.read_csv(sys.argv[1]); corpus = pd.read_csv(sys.argv[2])
C_AG = 0.8245163637337287; SEED = 42
def vec_pipeline(): return TfidfVectorizer(max_features=2352, ngram_range=(1, 1), sublinear_tf=True, strip_accents="unicode")
def run(df, label, C=C_AG, vocab_corpus=True, n_rep=10, boot=False):
    X = df["texto"].values; y = df[label].values
    rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_rep, random_state=SEED)
    oofs, accs = [], []; oof = np.empty(len(df), dtype=object)
    for i, (tr, te) in enumerate(rskf.split(X, y)):
        vec = vec_pipeline(); vec.fit(corpus["text"].values if vocab_corpus else X[tr])
        clf = LinearSVC(C=C, max_iter=2000, random_state=SEED).fit(vec.transform(X[tr]), y[tr])
        oof[te] = clf.predict(vec.transform(X[te]))
        if (i + 1) % 5 == 0: oofs.append(oof.copy()); accs.append(accuracy_score(y, oof))
    f1s = np.array([f1_score(y, o, average="macro") for o in oofs])
    ic = None
    if boot:
        rng = np.random.default_rng(SEED); bs = []
        for _ in range(2000):
            idx = rng.choice(len(df), len(df)); bs.append(np.mean([f1_score(y[idx], o[idx], average="macro") for o in oofs]))
        ic = np.percentile(bs, [2.5, 97.5])
    return f1s.mean(), f1s.std(), f1s.min(), f1s.max(), np.mean(accs), ic
print("n itens:", len(g), "| classes:", g["ouro"].value_counts().to_dict())
for nome, df in [("10 códigos, 496 itens", g), ("9 classes, 457 itens (sem RES-ouro)", g[g["ouro"] != "RES"].reset_index(drop=True))]:
    for C in (C_AG, 1.0):
        for vc in (True, False):
            m, s, lo, hi, acc, ic = run(df, "ouro", C, vc, boot=(C == C_AG and vc))
            print(f"{nome.split(',')[0]}, {len(df)} itens | C={C:.3f} | vocab {'corpus' if vc else 'dobra'} | F1-macro {m:.3f} ± {s:.3f} amplitude [{lo:.3f}; {hi:.3f}] | acc {acc:.3f}" + (f" | IC bootstrap itens [{ic[0]:.3f}; {ic[1]:.3f}]" if ic is not None else ""))
m, s, lo, hi, acc, _ = run(g[g["lexico"] != "RES"].reset_index(drop=True), "lexico")
print(f"referência: alvo = rótulo do léxico, {int((g['lexico']!='RES').sum())} itens rotulados | F1 {m:.3f} ± {s:.3f} | acc {acc:.3f}")
rng = np.random.default_rng(SEED)
for frac in (0.5, 0.75):
    vals = []
    for rep in range(10):
        idx = rng.choice(len(g), int(frac * len(g)), replace=False)
        vals.append(run(g.iloc[idx].reset_index(drop=True), "ouro", n_rep=1)[0])
    print(f"curva: {int(frac*100)}% dos itens | F1 {np.mean(vals):.3f} ± {np.std(vals):.3f}")
