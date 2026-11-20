#!/usr/bin/env python3
"""Gera o notebook V15.3 (parágrafo) a partir do V15.2, aplicando as oito correções
do relatório de 19/10/2026. Cada substituição é verificada: se o trecho original
não for encontrado, o script falha em vez de gerar um notebook parcialmente remendado."""
import json, sys, copy

SRC = sys.argv[1]
DST = sys.argv[2]
nb = json.load(open(SRC, encoding="utf-8"))
cells = nb["cells"]
LOG = []


def src(i):
    return "".join(cells[i]["source"])


def setsrc(i, text):
    cells[i]["source"] = text.splitlines(keepends=True)


def rep(i, old, new, count=1, tag=""):
    s = src(i)
    n = s.count(old)
    assert n == count, f"célula {i}: esperado {count} ocorrência(s) de {old[:60]!r}, achei {n}"
    setsrc(i, s.replace(old, new))
    LOG.append(f"cél. {i}: {tag or old[:50]!r}")


def check_head(i, text):
    assert text in src(i), f"célula {i} não começa como esperado: {text!r}"


# ── Cabeçalho (cél. 0): registro das alterações ──────────────────────────────
check_head(0, "# Algoritmos Genéticos")
setsrc(0, src(0).rstrip("\n") + """


### V15.3 (19/10/2026) · correções da auditoria pré-revisão (RITA, revisão maior)
1. 6D/6E: LR e RF passam a usar o **TF-IDF do AG** (`params_finais`), o C ótimo do LR e o
   melhor RF da grade. A V15.2 fixava `max_features=2995`, `C=10` e `max_depth=30`.
2. 6B/6C: o número de **avaliações únicas do AG por semente** é registrado, e o Random
   Search recebe exatamente esse orçamento na mesma semente (a V15.2 fixava 38).
3. V15.2 (circularidade): vocabulário de referência da hifenização reconstruído antes de
   reconstruir os corpora; as 30 medidas por condição são persistidas (JSON e CSV).
4. 7.4: respeita `UNIDADE_ANALISE` e restaura o vocabulário de referência ao final.
5. Nova célula 6F-b: rotulados, resíduo e total por ano (denominadores da Tabela 7).
6. Sentinelas de **parágrafo** declaradas a partir da execução V15.1 de 19/08/2026;
   as grandezas que dependem do orçamento pareado do RS entram como registro novo.
7. Textos fixos substituídos por conclusões derivadas dos dados; Fig. 5 lê o baseline da
   execução; Fig. 6 escreve "n.s." em vez de "equiv.".
8. Resumo e contraste (cél. final) regenerados na mesma sessão.
""")
LOG.append("cél. 0: changelog V15.3")

# ── Cél. 2: versão e referência de parágrafo ─────────────────────────────────
rep(2, 'VERSAO          = "v15.1"', 'VERSAO          = "v15.3"', tag="versão")
rep(2, 'REFERENCIA_V14 = os.path.join(DRIVE_BASE, "checkpoints")',
    'REFERENCIA_V14 = os.path.join(DRIVE_BASE, "checkpoints")\n'
    '# V15.3 · referência da execução de parágrafo (V15.1, 19/08/2026) — LEITURA APENAS.\n'
    'REFERENCIA_V151_PARAGRAFO = os.path.join(DRIVE_BASE, "v15.1_paragrafo", "checkpoints")',
    tag="referência parágrafo")

# ── Cél. 4: diff de parágrafo contra a V15.1 ─────────────────────────────────
rep(4, '''if UNIDADE_ANALISE == "paragrafo":
    print("Modo 'paragrafo': sem referência anterior por construção "
          "(a unidade mudou; comparar com a V14 não faria sentido).")''',
'''if ARQUIVO_ANTERIOR is None and EXECUCAO_DE_REGISTRO and UNIDADE_ANALISE == "paragrafo":
    # V15.3 · a execução V15.1 de parágrafo (19/08/2026) passa a ser a referência
    if os.path.isdir(REFERENCIA_V151_PARAGRAFO) and os.listdir(REFERENCIA_V151_PARAGRAFO):
        ARQUIVO_ANTERIOR = REFERENCIA_V151_PARAGRAFO
        print(f"Diff será contra os checkpoints da V15.1 (parágrafo): {ARQUIVO_ANTERIOR}")
    else:
        print("⚠️  Checkpoints da V15.1 (parágrafo) não encontrados — diff ficará 'não verificável'.")''',
    tag="referência de diff para parágrafo")

# ── Cél. 15 (markdown): texto da era página ──────────────────────────────────
check_head(15, "# Fase 1B")
setsrc(15, """---
# Fase 1B — Limpeza Estrutural do Corpus

## Por que esta fase existe

Uma auditoria de qualidade dos dados revelou que a extração dos PDFs deixou passar
dois tipos de contaminação que não pertencem ao conteúdo legítimo da agenda governamental:

**1. Cabeçalho/rodapé de página infiltrado.** A string *"Mensagem ao Congresso
Nacional [ano]"* é concatenada ao texto real pela extração; sua remoção é higiene
metodológica (o TF-IDF já a tratava como ruído de fundo, por ser uniforme).

**2. Elementos editoriais não-discursivos.** Sumários (linhas com pontilhados),
títulos de seção em maiúsculas, legendas de gráficos/tabelas, blocos densos de
números (tabelas extraídas como texto), página de catalogação (CDU/ISBN) e listas
de autoridades (ministros). Muitos desses elementos eram títulos-gabarito, triviais
de classificar, que inflavam a métrica; o corpus limpo mede o conteúdo efetivo da agenda.

> **Nota V15.3:** os números desta fase dependem da unidade de análise e são os
> impressos pela célula seguinte. Os valores da V14 (1.851 parágrafos com cabeçalho,
> 146 editoriais, F1 de ~0,814 para ~0,785) referem-se ao corpus de PÁGINA e não valem
> para a execução em parágrafo.
""")
LOG.append("cél. 15: markdown reescrito")

# ── Cél. 19 (markdown) ───────────────────────────────────────────────────────
rep(19, "Rotular manualmente 2.089 parágrafos seria inviável.",
    "Rotular manualmente todo o corpus seria inviável.", tag="2.089")

# ── Cél. 26: conclusão derivada ──────────────────────────────────────────────
rep(26, '''print("\\n→ CONCLUSÃO: ~48% puramente ambiente, ~38% puramente infraestrutura.")
print("  A fusão não reflete coerência semântica — é uma limitação do léxico V1.")''',
'''_pa = 100 * sg_counts.get("amb_pura", 0) / len(sub_ia)
_pi = 100 * sg_counts.get("infra_pura", 0) / len(sub_ia)
print(f"\\n→ CONCLUSÃO (derivada): {_pa:.0f}% puramente ambiente, {_pi:.0f}% puramente infraestrutura.")
print("  A fusão não reflete coerência semântica — é uma limitação do léxico V1.")''',
    tag="conclusão derivada")
rep(26, '''# ⚠️ TEXTO FIXO — as linhas de "CONCLUSÃO"/"Observação"/"Leitura" desta
# célula foram escritas à mão para o corpus de PÁGINA da V14. Confira
# contra os números impressos antes de citar qualquer uma delas.
''', '# V15.3 · conclusão calculada dos números impressos (antes era texto fixo da V14).\n', tag="aviso")

# ── Cél. 27: conclusão derivada ──────────────────────────────────────────────
rep(27, '''print("\\n→ CONCLUSÃO: 92% do resíduo vem de EMPATE (conteúdo temático existe, mas dois")
print("  léxicos empatam). Os zero_hits revelam um tema ausente do V1: governança/")
print("  institucional (decreto, transparência, direitos, ministério, indígenas...).")''',
'''_pe = 100 * motivos.get("empate", 0) / len(res_sub)
_pz = 100 * motivos.get("zero_hits", 0) / len(res_sub)
print(f"\\n→ CONCLUSÃO (derivada): {_pe:.0f}% do resíduo vem de EMPATE e {_pz:.0f}% de AUSÊNCIA de âncora.")
print("  Os tokens mais frequentes nos zero_hits indicam o tema ausente do V1 (ver lista acima);")
print("  a Fase 4 responde a isso com a classe governanca_institucional.")''',
    tag="conclusão derivada")
rep(27, '''# ⚠️ TEXTO FIXO — as linhas de "CONCLUSÃO"/"Observação"/"Leitura" desta
# célula foram escritas à mão para o corpus de PÁGINA da V14. Confira
# contra os números impressos antes de citar qualquer uma delas.
''', '# V15.3 · conclusão calculada dos números impressos (antes era texto fixo da V14).\n', tag="aviso")
rep(27, "# ── Diagnóstico 3: por que 23% vai para residual?", "# ── Diagnóstico 3: por que tanto vai para residual?", tag="23%")

# ── Cél. 45: registrar avaliações únicas do AG por semente ───────────────────
rep(45, '''f1_ag_runs       = []
f1_baseline_runs = []''',
'''f1_ag_runs       = []
f1_baseline_runs = []
n_aval_ag_runs   = []   # V15.3 · avaliações únicas do AG em cada semente (orçamento efetivo)''',
    tag="vetor de orçamento")
rep(45, '''    f1_ag = max(fits_final_run)
    f1_ag_runs.append(f1_ag)
''',
'''    f1_ag = max(fits_final_run)
    f1_ag_runs.append(f1_ag)
    n_aval_ag_runs.append(len(cache_run))   # V15.3
''', tag="append orçamento")
rep(45, '''print(f"Resumo baseline : média={np.mean(f1_baseline_runs):.4f} ± {np.std(f1_baseline_runs):.4f}")''',
'''print(f"Resumo baseline : média={np.mean(f1_baseline_runs):.4f} ± {np.std(f1_baseline_runs):.4f}")
print(f"Orçamento do AG : {np.mean(n_aval_ag_runs):.1f} ± {np.std(n_aval_ag_runs):.1f} avaliações únicas por semente "
      f"(mín {min(n_aval_ag_runs)}, máx {max(n_aval_ag_runs)}; limite estrutural {POP_EXP + GEN_EXP*(POP_EXP-ELITE_EXP)})")''',
    tag="print orçamento")
rep(45, '''    "f1_baseline": f1_baseline_runs,
}).to_csv(os.path.join(CKPT_DIR, "fase6b_ag_baseline.csv"), index=False)''',
'''    "f1_baseline": f1_baseline_runs,
    "n_aval_ag": n_aval_ag_runs,          # V15.3
}).to_csv(os.path.join(CKPT_DIR, "fase6b_ag_baseline.csv"), index=False)''', tag="csv orçamento")

# ── Cél. 48 (markdown) ───────────────────────────────────────────────────────
rep(48, "**107 avaliações de fitness são suficientes, ou o AG teve sorte?**",
    "**as avaliações de fitness que o AG gasta são suficientes, ou o AG teve sorte?**", tag="107")
rep(48, "usou as 107 avaliações melhor do que a amostragem", "usou as mesmas avaliações melhor do que a amostragem", tag="107b")
rep(48, '''- Orçamento idêntico: cada Random Search faz o mesmo número de avaliações que
  o AG realizou por execução (na configuração P=8, G=6 das 30 execuções)''',
'''- Orçamento idêntico e **medido**: em cada semente, o Random Search recebe exatamente o
  número de avaliações únicas que o AG daquela semente consumiu (registrado na Fase 6B).
  A V15.2 fixava 38; o limite estrutural de P=8, G=6 com 2 elites é 44, e o valor típico
  fica entre 40 e 44, de modo que o valor fixo subestimava o orçamento do AG.''', tag="protocolo")

# ── Cél. 49: orçamento pareado por semente ───────────────────────────────────
rep(49, '''_faltando = [v for v in ("X_train", "y_train", "individuo_aleatorio", "decodificar")
             if v not in globals()]''',
'''_faltando = [v for v in ("X_train", "y_train", "individuo_aleatorio", "decodificar", "n_aval_ag_runs")
             if v not in globals()]''', tag="guarda")
rep(49, '''N_EXECUCOES = 30
ORCAMENTO_RS = 38   # espelha o AG em P=8, G=6
f1_rs_runs = []

print(f"Random Search: {N_EXECUCOES} execuções × {ORCAMENTO_RS} avaliações cada")''',
'''N_EXECUCOES = 30
# V15.3 · orçamento PAREADO: o RS da semente i recebe o número de avaliações únicas do AG da semente i
ORCAMENTOS_RS = [int(v) for v in n_aval_ag_runs]
ORCAMENTO_RS  = float(np.mean(ORCAMENTOS_RS))      # só para rótulos de figura
f1_rs_runs = []
orcamento_rs_runs = []

print(f"Random Search: {N_EXECUCOES} execuções × orçamento pareado ao AG "
      f"(média {ORCAMENTO_RS:.1f}, mín {min(ORCAMENTOS_RS)}, máx {max(ORCAMENTOS_RS)})")''', tag="orçamento pareado")
rep(49, '''    melhor_rs = max(fitness_rs(individuo_aleatorio()) for _ in range(ORCAMENTO_RS))
    f1_rs_runs.append(melhor_rs)''',
'''    _orc = ORCAMENTOS_RS[run]
    melhor_rs = -1.0
    while len(cache_rs) < _orc:               # conta avaliações ÚNICAS, como no AG
        melhor_rs = max(melhor_rs, fitness_rs(individuo_aleatorio()))
    f1_rs_runs.append(melhor_rs)
    orcamento_rs_runs.append(len(cache_rs))''', tag="laço RS")
rep(49, '''    pd.DataFrame({"seed": list(range(N_EXECUCOES)), "f1_rs": f1_rs_runs}).to_csv(
        os.path.join(CKPT_DIR, "fase6c_rs.csv"), index=False)''',
'''    pd.DataFrame({"seed": list(range(N_EXECUCOES)), "f1_rs": f1_rs_runs,
                  "orcamento": orcamento_rs_runs}).to_csv(
        os.path.join(CKPT_DIR, "fase6c_rs.csv"), index=False)''', tag="csv RS")

# ── Cél. 50: recarga inclui o orçamento ──────────────────────────────────────
rep(50, '''f1_rs_runs       = _carregar_checkpoint("f1_rs_runs",       "fase6c_rs.csv",          "f1_rs")''',
'''f1_rs_runs       = _carregar_checkpoint("f1_rs_runs",       "fase6c_rs.csv",          "f1_rs")
n_aval_ag_runs   = _carregar_checkpoint("n_aval_ag_runs",   "fase6b_ag_baseline.csv", "n_aval_ag")   # V15.3''',
    tag="recarga")

# ── Cél. 52: rótulo da figura ────────────────────────────────────────────────
rep(52, '''    f"Teste de Suficiência — AG vs Random Search (orçamento idêntico: {ORCAMENTO_RS} aval./exec.)\\n"''',
'''    f"Teste de Suficiência — AG vs Random Search (orçamento pareado por semente: média {ORCAMENTO_RS:.1f} aval./exec.)\\n"''',
    tag="suptitle")

# ── Cél. 53 (markdown) ───────────────────────────────────────────────────────
rep(53, '''A vetorização TF-IDF é fixada nos valores ótimos encontrados pelo AG (max_features=2.995,
sublinear_tf=True, ngram=1), garantindo que a comparação isole o efeito do classificador.''',
'''A vetorização TF-IDF é fixada nos valores ótimos encontrados pelo AG nesta execução
(`params_finais`: max_features, ngram_max e sublinear_tf), garantindo que a comparação isole
o efeito do classificador. **V15.3:** a V15.2 usava `max_features=2995` fixo, valor de uma
execução antiga, e por isso LR e RF não compartilhavam o vetorizador do SVM.''', tag="2995")

# ── Cél. 54: TF-IDF do AG ────────────────────────────────────────────────────
rep(54, '''def make_tfidf_otimo():
    return TfidfVectorizer(max_features=2995, ngram_range=(1, 1),
                           sublinear_tf=True, strip_accents="unicode")''',
'''def make_tfidf_otimo():
    # V15.3 · vetorizador do AG desta execução (a V15.2 fixava 2995 / (1,1) / True)
    return TfidfVectorizer(max_features=params_finais["max_features"],
                           ngram_range=(1, params_finais["ngram_max"]),
                           sublinear_tf=params_finais["sublinear_tf"],
                           strip_accents="unicode")
print(f"TF-IDF comum aos três classificadores: max_features={params_finais['max_features']}, "
      f"ngram=(1,{params_finais['ngram_max']}), sublinear_tf={params_finais['sublinear_tf']}")''', tag="make_tfidf_otimo")

# ── Cél. 55: observação derivada ─────────────────────────────────────────────
rep(55, '''print(f"\\nBaseline (referência): {F1_BASELINE:.4f}")
print(f"\\nObservação: todos os três superam o baseline. O SVM Linear mantém-se")
print(f"superior mesmo após otimização dos três, confirmando a separabilidade")
print(f"linear do espaço TF-IDF da agenda governamental.")''',
'''print(f"\\nBaseline (referência): {F1_BASELINE:.4f}  |  LR: melhor C = {melhor_lr_C}")
_todos_sup = all(f > F1_BASELINE for f in (F1_SVM, F1_LR, F1_RF))
_lider = comparacao_3.iloc[0]["Algoritmo"]
print(f"\\nObservação (derivada): {'todos os três superam' if _todos_sup else 'NEM todos superam'} o baseline;")
print(f"o melhor dos três é {_lider}. A leitura de separabilidade linear (H1) depende do teste pareado da Fase 7.2,")
print(f"e não desta tabela de pontos únicos.")''', tag="observação derivada")
rep(55, '''# ⚠️ TEXTO FIXO — as linhas de "CONCLUSÃO"/"Observação"/"Leitura" desta
# célula foram escritas à mão para o corpus de PÁGINA da V14. Confira
# contra os números impressos antes de citar qualquer uma delas.
''', '# V15.3 · observação calculada dos números (antes era texto fixo da V14).\n', tag="aviso")

# ── Cél. 56: título, eixo e leitura ──────────────────────────────────────────
rep(56, '''ax.set_title("Três Algoritmos Otimizados — Discurso Presidencial Lula III",''',
'''ax.set_title("Três Algoritmos Otimizados — agenda governamental (Mensagens ao Congresso)",''', tag="título")
rep(56, '''ax.set_ylim(0.65, 0.86)''', '''ax.set_ylim(min(f1s + [F1_BASELINE]) - 0.05, max(f1s) + 0.03)''', tag="ylim")
rep(56, '''print("Leitura: o SVM Linear vence os classificadores baseados em árvores (Random Forest),")
print("evidência de que as classes temáticas são linearmente separáveis no espaço TF-IDF.")''',
'''print(f"Leitura (derivada): ranking nesta execução: {' > '.join(algos)}.")
print("A evidência estatística de separabilidade linear vem do teste pareado da Fase 7.2.")''', tag="leitura")
rep(56, '''# ⚠️ TEXTO FIXO — as linhas de "CONCLUSÃO"/"Observação"/"Leitura" desta
# célula foram escritas à mão para o corpus de PÁGINA da V14. Confira
# contra os números impressos antes de citar qualquer uma delas.
''', '# V15.3 · leitura calculada dos números (antes era texto fixo da V14).\n', tag="aviso")

# ── Cél. 59: tempos com o TF-IDF do AG e hiperparâmetros ótimos ─────────────
rep(59, '''    pipe = Pipeline([
        ("vec", TfidfVectorizer(max_features=2995, ngram_range=(1, 1),
                                sublinear_tf=True, strip_accents="unicode")),
        ("clf", clf)
    ])
    t0 = _time.time()''',
'''    pipe = Pipeline([("vec", make_tfidf_otimo()), ("clf", clf)])   # V15.3 · TF-IDF do AG
    t0 = _time.time()''', tag="tfidf tempos")
rep(59, '''    medir_tempos("Regressão Logística", LogisticRegression(C=10.0, max_iter=300, random_state=RANDOM_SEED)),
    medir_tempos("Random Forest", RandomForestClassifier(n_estimators=300, max_depth=30,
                 max_features="sqrt", random_state=RANDOM_SEED, n_jobs=-1)),''',
'''    medir_tempos("Regressão Logística", LogisticRegression(C=melhor_lr_C, max_iter=300, random_state=RANDOM_SEED)),
    medir_tempos("Random Forest", RandomForestClassifier(
        n_estimators=int(melhor_rf["n_estimators"]),
        max_depth=(None if str(melhor_rf["max_depth"]) == "None" else int(melhor_rf["max_depth"])),
        max_features=melhor_rf["max_features"], random_state=RANDOM_SEED, n_jobs=-1)),''', tag="hiperparâmetros tempos")
rep(59, '''print(f"\\n(Split holdout 75/25 estratificado, TF-IDF fixo nos valores ótimos do AG)")''',
'''print(f"\\n(Split holdout 75/25 estratificado; TF-IDF do AG; LR com C={melhor_lr_C}; "
      f"RF n={int(melhor_rf['n_estimators'])}, depth={melhor_rf['max_depth']}, mf={melhor_rf['max_features']})")''', tag="nota tempos")

# ── Cél. 60: sobreajuste idem + limiar coerente ──────────────────────────────
rep(60, '''    pipe = Pipeline([
        ("vec", TfidfVectorizer(max_features=2995, ngram_range=(1, 1),
                                sublinear_tf=True, strip_accents="unicode")),
        ("clf", clf)
    ])
    # F1 no treino completo (mesmo conjunto de fit)''',
'''    pipe = Pipeline([("vec", make_tfidf_otimo()), ("clf", clf)])   # V15.3 · TF-IDF do AG
    # F1 no treino completo (mesmo conjunto de fit)''', tag="tfidf overfit")
rep(60, '''    gap_treino_validacao("Regressão Logística", LogisticRegression(C=10.0, max_iter=300, random_state=RANDOM_SEED)),
    gap_treino_validacao("Random Forest", RandomForestClassifier(n_estimators=300, max_depth=30,
                         max_features="sqrt", random_state=RANDOM_SEED, n_jobs=-1)),''',
'''    gap_treino_validacao("Regressão Logística", LogisticRegression(C=melhor_lr_C, max_iter=300, random_state=RANDOM_SEED)),
    gap_treino_validacao("Random Forest", RandomForestClassifier(
        n_estimators=int(melhor_rf["n_estimators"]),
        max_depth=(None if str(melhor_rf["max_depth"]) == "None" else int(melhor_rf["max_depth"])),
        max_features=melhor_rf["max_features"], random_state=RANDOM_SEED, n_jobs=-1)),''', tag="hiperparâmetros overfit")
rep(60, '''print("  Gap pequeno (<0,05) → boa generalização, sem overfitting relevante.")
print("  Gap grande         → modelo memoriza o treino (overfitting).")
for r in overfit:
    if r["Gap (overfit)"] > 0.15:''',
'''LIMIAR_GAP = 0.15   # V15.3 · um único limiar, impresso e aplicado (a V15.2 dizia 0,05 e aplicava 0,15)
print(f"  Gap abaixo de {LIMIAR_GAP:.2f} → leitura comparativa preservada; acima → sobreajuste a discutir.")
print("  (CV sobre o conjunto rotulado inteiro, não sobre a partição de treino do holdout.)")
for r in overfit:
    if r["Gap (overfit)"] > LIMIAR_GAP:''', tag="limiar")

# ── Nova célula após a 63: denominadores por ano ────────────────────────────
nova_63 = {
    "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
    "source": '''# ── 6F-b · V15.3 — Denominadores da análise temporal (Tabela 7) ─────────────
# O revisor pediu os denominadores anuais, o tratamento dos casos excluídos e a
# origem das predições. As predições são FORA DA DOBRA (cross_val_predict, CV de
# 3 dobras estratificadas, seed 42), sobre as unidades ROTULADAS pelo léxico; o
# resíduo institucional fica fora das proporções. Esta célula registra tudo isso.
_den = pd.crosstab(df_corpus["year"], df_corpus["label_v3"] == RESIDUAL_V3)
_den = _den.rename(columns={False: "rotulados", True: "residuo"})
for _c in ("rotulados", "residuo"):
    if _c not in _den.columns:
        _den[_c] = 0
_den["total"] = _den["rotulados"] + _den["residuo"]
_den["residuo_pct"] = (100 * _den["residuo"] / _den["total"]).round(1)
_den.loc["TOTAL"] = [_den["rotulados"].sum(), _den["residuo"].sum(), _den["total"].sum(),
                     round(100 * _den["residuo"].sum() / _den["total"].sum(), 1)]
print("DENOMINADORES DA TABELA 7 (unidade:", UNIDADE_ANALISE.upper() + ")")
print("=" * 60)
print(_den.to_string())
print("\\nOrigem das predições: cross_val_predict, StratifiedKFold(3, shuffle, seed=42),")
print("sobre as unidades rotuladas; o resíduo não entra nas proporções.")

# Divergência entre a composição do léxico e a composição predita (p.p. por classe e ano)
_div_tab = (prop_modelo - prop_lexico).round(2)
print("\\nDivergência predito − léxico (p.p.):")
print(_div_tab.to_string())
print(f"\\nMaior divergência absoluta: {float(_div_tab.abs().max().max()):.2f} p.p.")

_den.to_csv(os.path.join(DIR_DADOS, "denominadores_por_ano.csv"))
_div_tab.to_csv(os.path.join(DIR_DADOS, "divergencia_lexico_modelo.csv"))
prop_lexico.round(2).to_csv(os.path.join(DIR_DADOS, "proporcoes_lexico.csv"))
print("\\n✓ Exportados: denominadores_por_ano.csv, divergencia_lexico_modelo.csv, proporcoes_lexico.csv")
'''.splitlines(keepends=True),
}
cells.insert(64, nova_63)
LOG.append("nova célula 64: denominadores por ano")
# A partir daqui os índices originais ≥ 64 deslocam-se em +1
S = 1

# ── Cél. 65 (markdown, agora 66): Fase 8 da era página ──────────────────────
check_head(65 + S, "# Fase 8")
setsrc(65 + S, """---
# Fase 8 — Conclusões e Próximos Passos

> **Nota V15.3:** o texto desta fase foi escrito para a execução de PÁGINA (V14) e
> descrevia números daquela execução (faixa de `max_features`, F1 médio da população,
> gerações de melhora). Para a unidade de PARÁGRAFO, as conclusões são as impressas
> pelas células das Fases 6, 6B, 6C, 6D, 7 e V15.2, e são elas que alimentam o artigo.
> Nenhuma frase desta célula deve ser citada sem conferência contra essas saídas.

## O que o AG encontrou? (leitura a partir das saídas)

- Fase 6: cromossomo vencedor, ganho sobre o baseline e número de avaliações únicas.
- Fase 6B: 30 execuções pareadas AG × baseline, Wilcoxon e tamanho de efeito.
- Fase 6C: AG × Random Search com orçamento pareado por semente.
- Fase 7.1/7.2: estimativa aninhada e comparação dos classificadores sobre o mesmo TF-IDF.
- V15.2: teste de circularidade léxico ↔ avaliação (2 unidades × 3 condições).

## Próximos passos

1. Conjunto-ouro humano (livro de códigos, piloto, dois anotadores, kappa, contaminação).
2. Resultados contra o ouro e veredito de H6.
3. Ampliar o espaço de busca (incluir Random Forest) para testar onde a busca evolutiva compensa.

---

*Notebook desenvolvido para a disciplina de Algoritmos Genéticos — PPGEELT/UFU · 2026/1*
*Ferdinand Rafols · Prof. Keiji Yamanaka*
""")
LOG.append(f"cél. {65+S}: Fase 8 reescrita")

# ── Cél. 66 (agora 67): exportar o orçamento também ─────────────────────────
rep(66 + S, '''        "execucoes_ag_maior":   int(sum(d > 0 for d in diferencas)),
    },''',
'''        "execucoes_ag_maior":   int(sum(d > 0 for d in diferencas)),
        "orcamento_ag_media":   round(float(np.mean(n_aval_ag_runs)), 2),   # V15.3
        "orcamento_ag_dp":      round(float(np.std(n_aval_ag_runs)), 2),
        "orcamento_ag_min":     int(min(n_aval_ag_runs)),
        "orcamento_ag_max":     int(max(n_aval_ag_runs)),
    },''', tag="json orçamento")

# ── Cél. 69 (agora 70): fig5 e fig6 ─────────────────────────────────────────
rep(69 + S, '''    ax.axhline(0.7129, color=AMBER, ls="--", lw=1.3, label="Baseline (0,713)")''',
'''    _bl = float(F1_BASELINE)   # V15.3 · lido da execução (a V15.2 fixava 0,7129)
    ax.axhline(_bl, color=AMBER, ls="--", lw=1.3, label=f"Baseline ({_bl:.3f})".replace(".", ","))
    ax.set_ylim(min(min(med), _bl) - 0.03, max(best) + 0.02)''', tag="fig5 baseline")
rep(69 + S, '''(", equiv.)" if p_rs >= 0.05 else ", signif.)")''',
'''(", n.s.)" if p_rs >= 0.05 else ", signif.)")''', tag="fig6 n.s.")

# ── Cél. 75 (agora 76): "(reforca H1)" condicional ───────────────────────────
rep(75 + S, '''print(f"  SVM selecionado em {svm_n}/5 dobras externas (reforca H1)")''',
'''print(f"  SVM selecionado em {svm_n}/5 dobras externas "
      + ("(SVM predominante entre os lineares)" if svm_n >= 3 else "(LR predominante entre os lineares)"))
print("  Obs.: a aninhada estima a generalizacao do PROCEDIMENTO de selecao (busca aleatoria, 20 configs);")
print("  nao subtrair dela o F1 do AG como 'otimismo de selecao' — sao seletores diferentes.")''', tag="reforca H1")

# ── Cél. 85 (agora 86): 7.4 respeita a unidade e restaura o vocabulário ─────
rep(85 + S, '''    AUDITORIA_HIFEN = {"ocorrencias": 0, "amostras": []}
    linhas = []
    for m in MENSAGENS:
        y = m["year"]
        if y not in RAW_PDF_TEXT:
            continue
        linhas.extend(segmentar_paragrafos(normalize_text(RAW_PDF_TEXT[y]), y))
    df = pd.DataFrame(linhas)''',
'''    AUDITORIA_HIFEN = {"ocorrencias": 0, "amostras": []}
    linhas = []
    if UNIDADE_ANALISE == "pagina":
        for m in MENSAGENS:
            y = m["year"]
            if y not in RAW_PDF_TEXT:
                continue
            linhas.extend(segmentar_paragrafos(normalize_text(RAW_PDF_TEXT[y]), y))
    else:
        # V15.3 · a V15.2 usava o caminho de PÁGINA mesmo em modo parágrafo
        for k in AUDITORIA_SEG: AUDITORIA_SEG[k] = 0
        for m in MENSAGENS:
            y = m["year"]
            if y not in RAW_PDF_LINES:
                continue
            linhas.extend(segmentar_paragrafos_geom(RAW_PDF_LINES[y], y))
    df = pd.DataFrame(linhas)''', tag="7.4 unidade")
rep(85 + S, '''CORRIGIR_HIFENIZACAO = _estado_original   # restaura''',
'''CORRIGIR_HIFENIZACAO = _estado_original   # restaura
if CORRIGIR_HIFENIZACAO:                   # V15.3 · restaura também o vocabulário de referência
    construir_vocabulario_referencia(RAW_PDF_TEXT.values())''', tag="7.4 restaura vocab")
rep(85 + S, '''print(f"\\n\\n{'='*70}\\nROBUSTEZ À CORREÇÃO DE HIFENIZAÇÃO (V12)\\n{'='*70}")''',
'''print(f"\\n\\n{'='*70}\\nROBUSTEZ À CORREÇÃO DE HIFENIZAÇÃO (V12) — unidade: {UNIDADE_ANALISE.upper()}\\n{'='*70}")''', tag="7.4 título")

# ── Cél. 87 (agora 88): sentinelas de parágrafo ──────────────────────────────
rep(87 + S, '''SENTINELAS = SENTINELAS_PAGINA if UNIDADE_ANALISE == "pagina" else {}
EMITIR_CERTIFICADO = bool(SENTINELAS)''',
'''# V15.3 · Sentinelas de PARÁGRAFO, declaradas a partir da execução V15.1 de 19/08/2026
# (checkpoints arquivados em v15.1_paragrafo/checkpoints_arquivado_20260819T0101 e
# saídas impressas do notebook). As grandezas que dependem do Random Search NÃO entram
# como sentinela, porque o orçamento do RS passou a ser pareado ao do AG nesta versão:
# ficam como REGISTRO NOVO, gravadas no certificado para servirem de referência adiante.
SENTINELAS_PARAGRAFO = {
    "remontagens": 2679, "residuo": 3, "vocabulario": 21358,
    "paragrafos_limpos": 10757, "treinamento": 6370, "residual_v3": 4387,
    "ag_max_features": 2352, "ag_ngram": 1, "ag_sublinear": True,
    "ag_C": 0.8245, "f1_baseline_unico": 0.8534,
    "runs_ag_media": 0.9169, "runs_bl_media": 0.8528,
    "W_ag_bl": 465, "r_ag_bl": 1.000,
}
REGISTROS_NOVOS_PARAGRAFO = ("runs_rs_media", "W_ag_rs", "p_ag_rs", "r_ag_rs", "vitorias_ag_rs")
if UNIDADE_ANALISE == "pagina":
    SENTINELAS, REGISTROS_NOVOS = SENTINELAS_PAGINA, ()
else:
    SENTINELAS, REGISTROS_NOVOS = SENTINELAS_PARAGRAFO, REGISTROS_NOVOS_PARAGRAFO
EMITIR_CERTIFICADO = bool(SENTINELAS)''', tag="sentinelas parágrafo")
rep(87 + S, '''def _add(nome, obtido):
    obtidos[nome] = obtido
    if obtido is None:
        cheques.append((nome, "--", "não verificável")); return
    esp = SENTINELAS[nome]; tol = TOL.get(nome, 0)''',
'''def _add(nome, obtido):
    obtidos[nome] = obtido
    if obtido is None:
        cheques.append((nome, "--", "não verificável")); return
    if nome in REGISTROS_NOVOS or nome not in SENTINELAS:   # V15.3
        cheques.append((nome, "NOVO", f"registrado {obtido} (sem esperado nesta versão)")); return
    esp = SENTINELAS[nome]; tol = TOL.get(nome, 0)''', tag="_add novo")
rep(87 + S, '''        _dmax = 0.0
        for _f in ("fase6b_ag_baseline.csv", "fase6c_rs.csv"):
            _novo = _pd.read_csv(os.path.join(CKPT_DIR, _f)).select_dtypes("number")
            _ant  = _pd.read_csv(os.path.join(ARQUIVO_ANTERIOR, _f)).select_dtypes("number")
            _dmax = max(_dmax, float((_novo - _ant).abs().to_numpy().max()))
        diff_msg = ("REPRODUÇÃO EXATA (Δmax = 0)" if _dmax == 0
                    else f"Δmax = {_dmax:.2e}" + (" — dentro de precisão de float"
                    if _dmax < 1e-9 else " — DIVERGÊNCIA REAL, investigar"))
        cheques.append(("diff_vs_arquivado", "OK" if _dmax < 1e-9 else "FALHOU", diff_msg))''',
'''        _dmax = 0.0
        # V15.3 · só as colunas comuns entram no diff (fase6b ganhou 'n_aval_ag'); o RS com
        # orçamento pareado diverge POR DESENHO do arquivo anterior e é reportado à parte.
        _f = "fase6b_ag_baseline.csv"
        _novo = _pd.read_csv(os.path.join(CKPT_DIR, _f)).select_dtypes("number")
        _ant  = _pd.read_csv(os.path.join(ARQUIVO_ANTERIOR, _f)).select_dtypes("number")
        _cols = [c for c in _ant.columns if c in _novo.columns]
        _dmax = float((_novo[_cols] - _ant[_cols]).abs().to_numpy().max())
        diff_msg = ("REPRODUÇÃO EXATA (Δmax = 0) em fase6b" if _dmax == 0
                    else f"Δmax = {_dmax:.2e} em fase6b" + (" — dentro de precisão de float"
                    if _dmax < 1e-9 else " — DIVERGÊNCIA REAL, investigar"))
        cheques.append(("diff_vs_arquivado", "OK" if _dmax < 1e-9 else "FALHOU", diff_msg))
        try:
            _rs_n = _pd.read_csv(os.path.join(CKPT_DIR, "fase6c_rs.csv"))
            _rs_a = _pd.read_csv(os.path.join(ARQUIVO_ANTERIOR, "fase6c_rs.csv"))
            _drs = float((_rs_n["f1_rs"] - _rs_a["f1_rs"]).abs().max())
            cheques.append(("diff_rs_informativo", "NOVO",
                            f"RS com orçamento pareado: Δmax = {_drs:.2e} vs. arquivo anterior (divergência esperada)"))
        except Exception:
            pass''', tag="diff fase6b")
rep(87 + S, '''_falhas = [c for c in cheques if c[1] == "FALHOU"]
_nv     = [c for c in cheques if c[1] == "--"]''',
'''_falhas = [c for c in cheques if c[1] == "FALHOU"]
_nv     = [c for c in cheques if c[1] == "--"]
_novos  = [c for c in cheques if c[1] == "NOVO"]''', tag="novos")
rep(87 + S, '''elif not _falhas and len(_nv) <= 2:
    veredito = "APROVADA — execução reproduz a referência"''',
'''elif not _falhas and len(_nv) <= 2:
    veredito = ("APROVADA — execução reproduz a referência"
                + (f" ({len(_novos)} grandeza(s) registrada(s) como referência nova)" if _novos else ""))''', tag="veredito")
rep(87 + S, '''        "sentinelas_esperadas": SENTINELAS, "obtidos": obtidos,''',
'''        "sentinelas_esperadas": SENTINELAS, "obtidos": obtidos,
        "registros_novos": {k: obtidos.get(k) for k in REGISTROS_NOVOS},
        "unidade": UNIDADE_ANALISE, "versao": VERSAO,
        "orcamento_ag_por_semente": [int(v) for v in n_aval_ag_runs] if "n_aval_ag_runs" in globals() else None,''', tag="certificado")

# ── Cél. 89 (agora 90): circularidade ────────────────────────────────────────
rep(89 + S, '''ANCORAS_TOK = _normalizar_ancoras(LEXICON_V3)''',
'''ANCORAS_TOK = _normalizar_ancoras(LEXICON_V3)

# V15.3 · a reconstrução dos corpora depende do estado da hifenização. A célula 7.4
# deixava VOCAB_REF vazio ao restaurar a flag, e os corpora saíam com ±1 unidade em
# relação aos registrados. Aqui o estado é garantido explicitamente.
CORRIGIR_HIFENIZACAO = True
construir_vocabulario_referencia(RAW_PDF_TEXT.values())
AUDITORIA_HIFEN = {"ocorrencias": 0, "amostras": []}
_N_REGISTRADO = {"pagina": None, "paragrafo": int(len(X_train)) if UNIDADE_ANALISE == "paragrafo" else None}
if UNIDADE_ANALISE == "pagina":
    _N_REGISTRADO["pagina"] = int(len(X_train))''', tag="circ vocab")
rep(89 + S, '''    _X, _y = _d["text"].values, _d["label_v3"].values
    print(f"\\n{'='*74}\\nUNIDADE: {_uni.upper()}  ({len(_d):,} unidades rotuladas)\\n{'='*74}")''',
'''    _X, _y = _d["text"].values, _d["label_v3"].values
    print(f"\\n{'='*74}\\nUNIDADE: {_uni.upper()}  ({len(_d):,} unidades rotuladas)\\n{'='*74}")
    # V15.3 · sanidade: o corpus reconstruído tem de coincidir com o registrado
    _esp = _N_REGISTRADO.get(_uni) or (1518 if _uni == "pagina" else 6370)
    if len(_d) != _esp:
        print(f"  ⚠️  n reconstruído ({len(_d)}) difere do registrado ({_esp}) — teste INVÁLIDO para esta unidade; pulando.")
        continue
    print(f"  ✓ n coincide com o corpus registrado ({_esp})")''', tag="circ sanidade")
rep(89 + S, '''    _dest = _os.path.join(DIR_CONTRASTE, "circularidade_2x3.json")
    with open(_dest, "w", encoding="utf-8") as _f:
        _js.dump({u: {k: (list(map(float, v)) if hasattr(v, "tolist") else v)
                      for k, v in d.items()} for u, d in CIRCULARIDADE.items()},
                 _f, indent=2, ensure_ascii=False)
    print(f"\\n✓ gravado: {_dest}")''',
'''    # V15.3 · serialização correta (a V15.2 falhava em numpy.float64) + CSV longo das 30 medidas
    def _serial(v):
        if isinstance(v, _np.ndarray):
            return [float(x) for x in v.ravel()]
        if isinstance(v, (_np.floating, _np.integer)):
            return float(v)
        return v
    _saida = {}
    for _u, _dd in CIRCULARIDADE.items():
        _saida[_u] = {k: _serial(v) for k, v in _dd.items()}
        for _cond in ("completo", "sem_ancoras", "so_ancoras"):
            _arr = _np.asarray(_dd[_cond], dtype=float)
            _saida[_u][_cond + "_media"] = float(_arr.mean())
            _saida[_u][_cond + "_dp"] = float(_arr.std())
    _dest = _os.path.join(DIR_CONTRASTE, "circularidade_2x3.json")
    with open(_dest, "w", encoding="utf-8") as _f:
        _js.dump(_saida, _f, indent=2, ensure_ascii=False)
    _linhas = []
    for _u, _dd in CIRCULARIDADE.items():
        for _cond in ("completo", "sem_ancoras", "so_ancoras"):
            for _i, _v in enumerate(_np.asarray(_dd[_cond], dtype=float)):
                _linhas.append({"unidade": _u, "condicao": _cond, "repeticao": _i // 3,
                                "dobra": _i % 3, "f1_macro": float(_v)})
    pd.DataFrame(_linhas).to_csv(_os.path.join(DIR_CONTRASTE, "circularidade_2x3_medidas.csv"), index=False)
    print(f"\\n✓ gravado: {_dest}")
    print(f"✓ gravado: {_os.path.join(DIR_CONTRASTE, 'circularidade_2x3_medidas.csv')} ({len(_linhas)} medidas)")''',
    tag="circ serialização")
# Observação sobre W = 0 / p mínimo
rep(89 + S, '''    print(f"  → QUEDA ao remover âncoras: {_queda:+.4f} ({_rel:.1f}%)  "
          f"Wilcoxon W={_W:.0f}, p={_p:.2e}")''',
'''    print(f"  → QUEDA ao remover âncoras: {_queda:+.4f} ({_rel:.1f}%)  "
          f"Wilcoxon W={_W:.0f}, p={_p:.2e}")
    if _W == 0:
        print(f"    (W = 0: as {len(_a)} diferenças têm o mesmo sinal; p é o mínimo possível para n = {len(_a)})")''',
    tag="circ W=0")

# ── Cél. 91 (agora 92): resumo inclui orçamento ──────────────────────────────
rep(91 + S, '''    ("runs_rs_media",  lambda: round(float(np.mean(f1_rs_runs)), 4)),
]:''',
'''    ("runs_rs_media",  lambda: round(float(np.mean(f1_rs_runs)), 4)),
    ("orcamento_ag_media", lambda: round(float(np.mean(n_aval_ag_runs)), 2)),   # V15.3
    ("orcamento_ag_dp",    lambda: round(float(np.std(n_aval_ag_runs)), 2)),
    ("n_avaliacoes_execucao_principal", lambda: int(len(fitness_cache))),
    ("versao", lambda: VERSAO),
]:''', tag="resumo")

# ── Remover a célula de remendo (92, agora 93) ───────────────────────────────
assert "PATCH · grava circularidade_2x3.json" in src(92 + S)
del cells[92 + S]
LOG.append("cél. 93 (remendo obsoleto) removida")

# ── Limpar saídas e contagens de execução ────────────────────────────────────
for c in cells:
    if c["cell_type"] == "code":
        c["outputs"] = []
        c["execution_count"] = None

json.dump(nb, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"✓ {DST} gerado com {len(cells)} células")
print("\n".join(" - " + l for l in LOG))
