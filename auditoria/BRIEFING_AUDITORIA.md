# Briefing de auditoria: artigo RITA V3 (revisão maior)

Data do pacote: 05/11/2026. Prazo da revista: 20/11/2026. Este pacote foi montado para uma auditoria independente do manuscrito revisado. Quem audita não participou da redação e não deve receber os rascunhos nem a carta de resposta: só o PDF, os artefatos e este roteiro.

## 1. O que auditar

Três perguntas, nesta ordem de prioridade:

1. **Os dados estão corretos?** Cada número do PDF deve ser recomputável a partir dos artefatos da pasta `dados/`, `anotacao/` e `execucao_v15_3/`. A auditoria vale quando recalcula; conferir transcrição (PDF contra JSON) é o mínimo, e não basta.
2. **A análise é válida?** Testes, intervalos, regras de decisão e pesos foram usados de forma apropriada, e as conclusões não vão além do que os números sustentam.
3. **Há erros teóricos ou de leitura?** Em especial na relação entre supervisão fraca, circularidade e o conjunto-ouro (Seções 4.2, 4.6, 6.6, 6.7 e 8).

Fora do escopo: estilo, formatação e a carta de resposta.

## 2. Conteúdo do pacote

| Pasta | Arquivo | O que é |
| --- | --- | --- |
| `artigo/` | `Artigo_RITA_v3_rascunho.pdf` | manuscrito a auditar |
| `artigo/` | `Artigo_RITA_v2_versao_anterior.pdf` | versão submetida (unidade de página); só para os números que a V3 atribui explicitamente à versão anterior |
| `dados/` | `corpus_v3_paragrafo.csv` | corpus limpo (10.757 parágrafos; colunas text, year, n_words, label_v1, label_v3); `outros_institucional` é o resíduo |
| `dados/` | `conjunto_ouro.csv` | os 496 itens do ouro: rótulo do léxico, dos dois anotadores, do terceiro voto, origem do rótulo, predição fora da dobra do SVM, sinal de defeito de segmentação |
| `dados/` | `resumo_ouro.json`, `por_classe.csv`, `matriz_lexico_vs_ouro.csv` | métricas contra o ouro, como calculadas por `scripts/construir_ouro.py` |
| `dados/` | `resumo_concordancia_principal.json`, `matriz_a1_a2.csv` | concordância entre os anotadores (540 itens), por `scripts/medir_concordancia.py` |
| `dados/` | `itens_sem_maioria.csv`, `itens_excluidos_nc.csv` | os 34 itens sem adjudicação e os 10 excluídos |
| `anotacao/` | `principal_anotador1.xlsx`, `principal_anotador2.xlsx` | planilhas devolvidas pelos dois anotadores externos, como entregues |
| `anotacao/` | `desempate_terceiro_voto_final.xlsx`, `desempate_gabarito.csv` | o terceiro voto cego (ids DES) e a chave DES → PRI |
| `anotacao/` | `principal_gabarito.csv`, `parametros.json`, `piloto_gabarito.csv`, `piloto2_gabarito.csv` | sorteio da amostra (estratos, ano, id no corpus) |
| `anotacao/` | `instrumento_v1_1_em_branco.xlsx` | o instrumento (regras e categorias) que os anotadores receberam |
| `execucao_v15_3/` | notebook `.ipynb` e `log_execucao_v15_3_20_10.txt` | código do pipeline e saída completa da execução certificada de 20/10/2026 |
| `execucao_v15_3/` | `historico_ag.csv`, `resultados_30_execucoes.csv`, `fase6c_rs.csv` | convergência do AG, 30 execuções AG/baseline, 30 da busca aleatória com orçamento |
| `scripts/` | `medir_concordancia.py`, `construir_ouro.py`, `amostra_ouro.py`, `amostra_piloto2.py`, `gerar_planilhas_anotacao.py`, `figs_3_4_legiveis.py` | scripts do conjunto-ouro e das figuras |
| raiz | `Resultados_V15_3_paragrafo.md`, `Conjunto_ouro_resultados_principal.md`, `Conjunto_ouro_pilotos.md` | notas de resultados; são secundárias, os artefatos acima têm precedência |

Lacunas conhecidas do pacote: o `matriz_confusao.csv` e o certificado JSON da execução de 20/10 estão no Drive e não aqui; o log traz o relatório por classe e as sentinelas. As frações da matriz de confusão citadas na Seção 6.3 vêm de uma reprodução local das predições fora da dobra (F1 0,9202 contra 0,9209 do notebook) e devem ser conferidas contra o arquivo do Drive. O léxico V3 (`lexico_v3_ancoras.json`) está no notebook (célula da rotulagem), não como arquivo separado.

## 3. Roteiro de recomputação (faça, não leia)

1. **Ouro e F1.** A partir de `conjunto_ouro.csv`: recalcule o F1-macro do SVM contra o ouro nos itens rotulados (coluna `svm_oof` não nula), com dez códigos e com nove; o F1 do léxico contra o ouro nos 496; os ICs por bootstrap (2.000 reamostras, semente 42); a acurácia ponderada por pós-estratificação (pesos N_classe/n_classe, com N do `corpus_v3_paragrafo.csv`). Compare com a Tabela 9 e o texto da Seção 6.6.
2. **Concordância.** A partir das duas planilhas de `anotacao/` (aba "Anotação"): kappa de Cohen, alfa de Krippendorff e kappa por classe, excluindo itens com NC. Use uma implementação de referência para o alfa (o script implementa o alfa à mão) e compare com `resumo_concordancia_principal.json`.
3. **Origem do ouro.** Reconstrua os 343 / 153 / 34 / 10 a partir das planilhas, da chave de desempate e do terceiro voto. Verifique que nenhum item fora de desacordo recebeu voto, e que a regra de maioria foi aplicada como descrita.
4. **Predições fora da dobra.** Reproduza `svm_oof` com o notebook (TF-IDF 2.352 unigramas, sublinear, strip_accents unicode; LinearSVC C = 0,8245163637337287, max_iter 800, random_state 42; StratifiedKFold 3 dobras, shuffle, semente 42, sobre os 6.370 rotulados) e meça quantas predições diferem das da coluna.
5. **30 execuções.** A partir de `resultados_30_execucoes.csv` e `fase6c_rs.csv`: médias, desvios, Wilcoxon unilateral (alternative="greater"), rank-biserial, contagem de vitórias, orçamento médio. Compare com a Seção 6.2 e a Figura 3.
6. **Tabelas 1, 5 e 7.** Recompute parágrafos, rotulados e resíduo por ano a partir do corpus; confira a Tabela 5 e a Tabela 7 contra o log (relatório por classe e proporções por ano).
7. **Segmentação.** Recompute a fração de parágrafos iniciados em minúscula no corpus e os 110 itens com defeito na amostra (critérios: início em minúscula, ausência de pontuação final, cabeçalho de 2023 interpolado em maiúsculas).

## 4. Pontos que merecem juízo, não só conta

- **H6 em dez códigos.** A regra pré-registrada avalia o SVM num espaço de dez códigos em que ele nunca prediz RES, o que embute uma classe com F1 zero. A sensibilidade de nove classes (0,684) está reportada. Pergunta: a comparação principal deveria ser a de nove? O veredito muda?
- **Terceiro voto.** O voto cego coincidiu com o anotador 1 em 100 desacordos e com o 2 em 53. O artigo declara isso e reporta a sensibilidade "só acordo direto" (0,649). Pergunta: a assimetria compromete o ouro, e a sensibilidade basta?
- **34 itens sem adjudicação.** Se todos fossem acertos do SVM, o F1 ultrapassaria 0,75? Faça a conta.
- **Pós-estratificação (0,384).** Os pesos usam só a classe do léxico. O sorteio estratificou também por ano. Os pesos deveriam incluir o ano? O número muda?
- **Dependência nas 30 execuções.** As 30 observações reutilizam o mesmo corpus; só a partição muda. O artigo declara isso e limita a inferência ao corpus sob repartição. É suficiente, ou o teste de Wilcoxon está sendo usado além do que a dependência permite?
- **Bootstrap do F1-macro** com 419 itens e classes de 33 a 62 itens: a cobertura do IC é razoável? Há alternativa melhor?
- **Circularidade (Tabela 8).** As âncoras são removidas como stop words após a normalização do vetorizador. Os cinco termos do léxico com hífen ou espaço (nunca casáveis como palavra única) escapam do filtro? Isso afeta o resultado?
- **Leitura teórica.** O artigo conclui que "o classificador reproduz o léxico" (91% de coincidência SVM × léxico nos itens do ouro; acurácias contra o ouro de 63,0% e 63,2%) e que "a métrica contra o léxico superestima a qualidade semântica em cerca de 0,33 de F1". Essas afirmações seguem dos dados? Há alguma passagem que afirme mais do que os dados permitem?
- **H1 a H5.** H3 e H4 foram reclassificadas como "observada / não observada" (exploratórias). H5 mudou de leitura em relação à versão anterior. Os vereditos da Tabela 10 são consistentes com as Seções 6.1 a 6.5?
- **Versões de software.** A execução de parágrafo usou Python 3.13.16, numpy 2.1.3 e pandas 2.2.3, diferentes da versão anterior, com reprodução exata declarada. Verifique no log que as 15 sentinelas passaram e que o diff foi zero.

## 5. Formato do relatório esperado

Três listas, em português: (a) erros (número do manuscrito, valor recomputado, arquivo e linha ou célula usados); (b) problemas de validade ou de leitura, com a passagem citada e a objeção; (c) o que foi verificado e conferiu, por seção. Sem reescrita do artigo e sem sugestões de estilo.

---

## Prompt sugerido para o chat de auditoria

> Você é um auditor independente de um artigo científico em revisão (anexo: `Artigo_RITA_v3_rascunho.pdf`) e dos artefatos que o sustentam (zip anexo, com o `BRIEFING_AUDITORIA.md` na raiz). Leia o briefing primeiro e siga o roteiro da Seção 3 recomputando cada número a partir dos artefatos, com código, e não lendo os resumos. Depois responda aos pontos da Seção 4 com juízo próprio. Entregue o relatório no formato da Seção 5. Não reescreva o artigo. Quando um número não puder ser recomputado com o que está no pacote, diga qual arquivo falta. Trabalhe de forma cética: o objetivo é encontrar o que está errado, e não confirmar o que está escrito.
