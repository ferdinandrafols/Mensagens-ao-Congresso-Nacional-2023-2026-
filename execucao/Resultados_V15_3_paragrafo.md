# Resultados da execução V15.3 em parágrafo (20/10/2026, certificado 03:40 UTC)

Fonte: notebook executado `AG_RafolsFerdinand_Otimizacao_Hiperparametros_v15_3_Paragrafos (4).ipynb`. Saídas no Drive em `Etapa4_RITA/v15.3_paragrafo/` e `Etapa4_RITA/v15.3_contraste/`.

## Certificado

- Veredito: APROVADA. 15 sentinelas de parágrafo (declaradas a partir da V15.1 de 19/08) todas OK; diff contra `v15.1_paragrafo/checkpoints` em `fase6b_ag_baseline.csv`: Δmax = 0.
- É a terceira reprodução exata dos 60 valores das 30 execuções de AG e baseline (18/08, 19/08, 20/10), a primeira com sentinelas declaradas.
- Ambiente efetivo: Python 3.13.16, scikit-learn 1.6.1, scipy 1.16.3, numpy 2.1.3, pandas 2.2.3, matplotlib 3.10.0, pdfplumber 0.11.10. Python, numpy e pandas diferem da Seção 5 do artigo (3.12, 2.0.2, 2.2.2) e a reprodução foi exata mesmo assim; a Seção 5 da V3 deve declarar as versões da execução de parágrafo e registrar o fato.
- Seis grandezas registradas como referência nova (dependem do orçamento pareado do RS): runs_rs_media 0,9151; W_ag_rs 332; p_ag_rs 0,0202; r_ag_rs 0,428; vitorias_ag_rs 24; diff do RS contra a V15.1 Δmax = 4,41e-3 (esperado).

## Corpus e rotulagem (idênticos à V15.1)

11.005 unidades brutas; 10.757 após limpeza; 6.370 rotuladas; 4.387 no resíduo (40,8%); 2.679 remontagens de hifenização; vocabulário 21.358 tipos; mediana 56 palavras (brutas), 5,25 unidades por página.

## Otimização

- Execução principal (P=12, G=10): 106 avaliações únicas; SVM linear, max_features 2.352, unigramas, sublinear_tf, C = 0,8245; F1 = 0,9208; baseline (LR, 1.000 termos) 0,8534; ganho +0,0674 (7,9%).
- 30 execuções (P=8, G=6): AG 0,9169 ± 0,0078; baseline 0,8528 ± 0,0028; W = 465, p < 10⁻⁶, r = 1,00, 30/30.
- Orçamento efetivo do AG por semente: 41,9 ± 1,2 avaliações únicas (mín 40, máx 44; limite estrutural 44). A V15.2 dava 38 ao Random Search.
- Random Search com orçamento pareado por semente: 0,9151 ± 0,0048. AG × RS: W = 332, p = 0,0202, 24/30, r = 0,428, Δ média +0,0018, Δ mediana +0,0035. Significativo a 0,05 e sob Bonferroni (0,025); magnitude pequena. Com o orçamento corrigido, W, p e contagem de vitórias coincidiram com os da V15.1 (orçamento 38); só as magnitudes mudaram (Δ média de +0,0021 para +0,0018).

## Classificadores sobre o mesmo TF-IDF (2.352 / unigramas / sublinear)

- Pontos únicos (CV seed 42): SVM 0,9208 (AG); RF 0,9170 (grade: 300 árvores, profundidade livre, log2); LR 0,9094 (C = 10).
- 30 dobras pareadas (3 × 10): SVM 0,9184 ± 0,0052; LR 0,9101 ± 0,0064; RF 0,9077 ± 0,0057. SVM > LR: W = 463, p < 10⁻⁴, 29/30, r = 0,991. SVM > RF: W = 461, 29/30, r = 0,983. LR > RF: p = 0,065, 17/30, r = 0,32 (não detectada).
- Holdout 75/25 (tempos): SVM 0,761 s treino, 0,171 s predição, F1 0,9240; LR 1,963 / 0,254 / 0,9142; RF 9,737 / 0,396 / 0,9258. Num único holdout o RF supera o SVM; o teste pareado em 30 dobras diz o contrário (29/30). Reportar os dois com essa leitura.
- Sobreajuste (treino vs CV): SVM 0,9989 / 0,9208 (gap 0,078); LR 1,000 / 0,9094 (0,091); RF 1,000 / 0,9170 (0,083).
- Aninhada: externo 5 dobras, interno 3 dobras com busca aleatória de 20 configurações: 0,9127 ± 0,0033; holdout 0,9176; seletor enviesado 0,9156; SVM escolhido em 3/5 dobras externas.
- Métricas agregadas do SVM (fora da dobra): acurácia 0,9234; precisão-macro 0,9256; revocação-macro 0,9169; F1-macro 0,9209. Por classe (F1): economia 0,92; educação 0,94; governança 0,91; infraestrutura 0,93; meio ambiente 0,94; política externa 0,91; programas sociais 0,92; reforma agrária 0,88 (revocação 0,84, a menor); saúde 0,95.

## Análise temporal (predições fora da dobra, só rotulados)

Denominadores (rotulados / resíduo / total): 2023: 422 / 301 / 723 (41,6%); 2024: 928 / 590 / 1.518 (38,9%); 2025: 2.196 / 1.573 / 3.769 (41,7%); 2026: 2.824 / 1.923 / 4.747 (40,5%). Divergência predito − léxico: no máximo 1,18 p.p. (média absoluta por classe 0,2 a 0,5 p.p.). H3: nenhuma classe varia 10 p.p. entre anos consecutivos (maior: governança 19,7 → 12,2). H4: programas sociais −1,7 p.p. e política externa +1,9 p.p. ante a média 2023–2025 (padrão previsto não observado).

## Circularidade léxico ↔ avaliação (2 × 3, 30 medidas por condição, corpora registrados: 1.518 e 6.370)

| Unidade | Completo | Sem âncoras | Só âncoras | Queda | Âncoras no vocabulário |
| --- | --- | --- | --- | --- | --- |
| Página | 0,8016 ± 0,0157 | 0,6693 ± 0,0146 | 0,8875 ± 0,0123 | 16,5% | 157 |
| Parágrafo | 0,9184 ± 0,0052 | 0,5440 ± 0,0076 | 0,9880 ± 0,0019 | 40,8% | 175 |

Wilcoxon W = 0, p = 1,86 × 10⁻⁹ nas duas unidades (todas as 30 diferenças com o mesmo sinal; p mínimo para n = 30). 180 medidas persistidas em `circularidade_2x3_medidas.csv`. Estes substituem os valores preliminares da V15.2 (0,9186 / 0,5454 / 0,9880 e 0,7977 / 0,6689 / 0,8891), que vinham de corpora reconstruídos com ±1 unidade; a causa (vocabulário de referência vazio após a 7.4) está confirmada pelo n coincidente.

## Robustez à hifenização, em parágrafo

Sem correção: 23.051 tipos, 2.679 resíduos, 6.343 rotulados, baseline 0,8516, AG 0,9173. Com correção: 21.358 tipos, 3 resíduos, 6.370 rotulados, baseline 0,8534, AG 0,9208. Efeito +0,0018 (baseline) e +0,0035 (AG); 27 parágrafos mudam de rótulo.

## Pendências desta execução

- O contraste final (célula 92) não imprimiu a tabela página × parágrafo porque `resumo_v15_pagina.json` está em `v15.1_contraste/`, e a V15.3 lê `v15.3_contraste/`. Copiar o arquivo para a pasta nova e reexecutar só a célula 92, ou montar a tabela a partir dos dois resumos (os números de página não mudaram).
- Seção 5 do artigo: declarar Python 3.13.16, numpy 2.1.3 e pandas 2.2.3 para a execução de parágrafo.
