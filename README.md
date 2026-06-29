# Otimização de Hiperparâmetros via Algoritmos Genéticos para Classificação de Texto

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1KMx_GrS5JC5r4O4jY8QrmjkCJnADPXFJ)

Evidência computacional reprodutível do artigo **"Um pipeline reprodutível para a categorização semântica supervisionada de documentos governamentais: estudo de caso nas Mensagens ao Congresso Nacional (2023–2026)"**, submetido à revista **RITA** (UFRGS).

O trabalho propõe um pipeline auditável de classificação supervisionada de parágrafos — representação por TF-IDF, classificadores clássicos (Regressão Logística, SVM linear, Random Forest) e otimização de hiperparâmetros por Algoritmo Genético (AG) — e o demonstra sobre a **agenda governamental** expressa nas Mensagens ao Congresso Nacional do mandato 2023–2026, rotuladas em nove classes temáticas.

> Pesquisa de mestrado no PPGEELT/UFU (EL142A, 2026/1). Discente: Ferdinand Rafols. Orientação: Prof. Dr. Márcio José da Cunha. Este notebook é um dos vértices de uma pesquisa que, sobre um corpus comum, atravessa quatro disciplinas e culmina na comparação entre arquiteturas cognitivas governadas por linguagem (baseline × A1 × A2).

### Créditos acadêmicos

| Papel | Docente |
|---|---|
| Orientação e revisão | Prof. Dr. Márcio José da Cunha |
| Aprendizado de Máquinas — corpus, léxico e pipeline supervisionado | Profa. Dra. Danielli Araújo Lima |
| Visualização da Informação — identidade visual e princípios de visualização | Prof. Dr. Alexandre Cardoso |
| Algoritmos Genéticos — otimização de hiperparâmetros (foco deste notebook) | Prof. Dr. Keiji Yamanaka |

Todos vinculados ao PPGEELT/FEELT/UFU.

## Principais resultados

Todos os números provêm da execução canônica do notebook (`seed = 42`, scikit-learn 1.6.1) e estão consolidados em `resultados_v10.json`.

| Resultado | Valor |
|---|---|
| Melhor modelo (configuração selecionada) | SVM linear, **F1-macro 0,807** |
| Generalização sem viés de seleção (CV aninhada 5×3) | **0,786 ± 0,017** |
| Otimismo de seleção | +0,016 |
| Ganho do AG sobre a configuração-padrão | 0,713 → 0,807 (≈ +13%); Wilcoxon W = 465, p < 0,0001, r = 1,00 |
| AG vs. Random Search (mesmo orçamento) | estatisticamente equivalente: p = 0,059, r = 0,33 |

**Comparação controlada entre classificadores** (mesmo vetorizador TF-IDF; 30 dobras repetidas pareadas):

| Algoritmo | F1-macro (média ± DP) |
|---|---|
| SVM linear | 0,802 ± 0,016 |
| Regressão Logística | 0,794 ± 0,018 |
| Random Forest | 0,754 ± 0,019 |

Wilcoxon pareado: SVM > Regressão Logística (p = 0,0009; r = 0,63) e ambos > Random Forest (p < 0,001).

O estudo de caso diacrônico revela forte continuidade temática da agenda governamental ao longo do mandato e **ausência de inflexão pré-eleitoral**. Os achados são reportados com a ressalva de que os rótulos derivam de um léxico, de modo que as métricas medem a consistência do pipeline frente a esse léxico (limite inferior de consistência), e não uma anotação humana independente.

## Conteúdo do repositório

| Arquivo | Descrição |
|---|---|
| `AG_RafolsFerdinand_Otimizacao_Hiperparametros_v10.ipynb` | Notebook completo e autocontido (Fases 0–7), incluindo a Fase 7 com as validações da revisão |
| `corpus_v3.csv` | Corpus limpo e rotulado (1.943 parágrafos; coluna `label_v3`, com o resíduo institucional marcado como `outros_institucional`) |
| `dados/resultados_v10.json` | Consolidação dos resultados da Fase 7 (generalização, Tabela 2, tamanhos de efeito) |
| `dados/tabela2_dispersao_v10.csv` | Médias e desvios da comparação controlada entre classificadores |
| `dados/scores_30dobras_v10.csv` | F1-macro das 30 dobras pareadas, por classificador (base dos testes de Wilcoxon) |
| `figuras/` | Figuras do artigo em `.pdf` e `.png` (identidade visual navy/âmbar) |

## Estrutura do notebook

| Fase | Conteúdo |
|---|---|
| 0 | Setup do ambiente |
| 1 | Extração do corpus a partir dos PDFs (autocontida) |
| 2 | Léxico V1 — rotulagem e diagnóstico |
| 3 | Diagnóstico crítico do V1 → motivação para o refinamento |
| 4 | Léxico V3 — refinado; comparação V1 → V3 |
| 5 | Fundamentos e implementação do Algoritmo Genético |
| 6 | Resultados: comparação de classificadores, otimização, estudo diacrônico, confronto das hipóteses |
| 7 | **(V10)** Validações da revisão: CV aninhada, Tabela 2 com dispersão e Wilcoxon, tamanhos de efeito |

## Como reproduzir

1. Abra o notebook no Colab pelo selo acima ou pelo [link direto](https://colab.research.google.com/drive/1KMx_GrS5JC5r4O4jY8QrmjkCJnADPXFJ).
2. Ajuste `DRIVE_BASE` (célula de configuração) para a sua pasta no Google Drive e disponibilize os quatro PDFs das Mensagens ao Congresso Nacional na pasta indicada.
3. Execute as células em ordem (`Ambiente de execução → Executar tudo`). A semente aleatória está fixada em 42 em toda a cadeia experimental.
4. A Fase 7 reconstrói o corpus a partir de `corpus_v3.csv` caso o estado da sessão se perca, de modo que roda de forma autônoma. Tempo aproximado: a CV aninhada leva ~3–5 min e a comparação controlada ~2–3 min em CPU padrão.

### Ambiente

Python 3.12 · scikit-learn 1.6.1 · scipy 1.16.3 · numpy 2.0.2 · pandas 2.2.2 · matplotlib 3.10.0 · pdfplumber. A validação estatística segue as recomendações de Demšar (2006) e García et al. (2010): 30 execuções, teste de Wilcoxon de postos sinalizados e tamanho de efeito rank-biserial.

## Notas metodológicas

- **Honestidade de calibração.** O resultado AG ≈ Random Search é reportado como contribuição (auditabilidade, reprodutibilidade e eficiência), não como superioridade.
- **Estimativa não enviesada.** O F1-macro de 0,807 corresponde à configuração selecionada; a generalização do pipeline é estimada por validação cruzada aninhada (0,786 ± 0,017), que separa a seleção de hiperparâmetros da avaliação.
- **Terminologia.** O objeto de estudo é a *agenda governamental* (instrumento do Art. 84 da Constituição), não o discurso presidencial.

## Como citar

> RAFOLS, F.; CUNHA, M. J. da. Um pipeline reprodutível para a categorização semântica supervisionada de documentos governamentais: estudo de caso nas Mensagens ao Congresso Nacional (2023–2026). *Manuscrito submetido à RITA — Revista de Informática Teórica e Aplicada* (UFRGS), 2026.

