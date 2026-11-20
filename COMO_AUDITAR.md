# Como auditar: roteiro de recomputação

Roteiro usado nas três rodadas de conferência da versão revisada (novembro de 2026). A auditoria vale quando recalcula; conferir transcrição é o mínimo. Caminhos relativos à raiz do repositório.

## Roteiro (faça, não leia)

1. **Ouro e F1.** A partir de `ouro/saidas/conjunto_ouro.csv`: recalcule o F1-macro do SVM contra o ouro nos itens rotulados (coluna `svm_oof` não nula), com dez códigos e com nove; o F1 do léxico contra o ouro nos 516; os ICs por bootstrap (2.000 reamostras, semente 42); a acurácia ponderada por pós-estratificação (pesos N_classe/n_classe, com N do `dados/corpus_v3_paragrafo.csv`). Compare com a Tabela 8 e o texto da Seção 6.6; inclua o treino no ouro (`scripts/treinar_no_ouro.py`).
2. **Concordância.** A partir das duas planilhas de `ouro/principal/` (aba "Anotação"): kappa de Cohen, alfa de Krippendorff e kappa por classe, excluindo itens com NC. Use uma implementação de referência para o alfa (o script implementa o alfa à mão) e compare com `ouro/saidas/resumo_concordancia_principal.json`.
3. **Origem do ouro.** Reconstrua os 343 / 153 / 20 / 14 / 10 a partir das planilhas, da chave de desempate, do terceiro voto e das planilhas de reconciliação (`ouro/reconciliacao/`). Verifique que nenhum item fora de desacordo recebeu voto, e que a regra de maioria foi aplicada como descrita.
4. **Predições fora da dobra.** Reproduza `svm_oof` com o notebook (TF-IDF 2.352 unigramas, sublinear, strip_accents unicode; LinearSVC C = 0,8245163637337287, max_iter 800, random_state 42; StratifiedKFold 3 dobras, shuffle, semente 42, sobre os 6.370 rotulados) e meça quantas predições diferem das da coluna.
5. **30 execuções.** A partir de `execucao/resultados_30_execucoes.csv` e `execucao/fase6c_rs.csv`: médias, desvios, Wilcoxon unilateral (alternative="greater"), rank-biserial, contagem de vitórias, orçamento médio. Compare com a Seção 6.2 e a Figura 3; o histórico do AG (`execucao/historico_ag.csv`) com a Figura 2.
6. **Tabelas 1 e 5 e Figura 5.** Recompute parágrafos, rotulados e resíduo por ano a partir do corpus; confira a Tabela 5 e as proporções por ano (Figura 5) contra o log (relatório por classe e proporções por ano).
7. **Segmentação.** Recompute a fração de parágrafos iniciados em minúscula no corpus e os 110 itens com defeito na amostra (critérios: início em minúscula, ausência de pontuação final, cabeçalho de 2023 interpolado em maiúsculas).

## Pontos que merecem juízo, não só conta

- **H6 em dez códigos.** A regra pré-registrada avalia o SVM num espaço de dez códigos em que ele nunca prediz RES, o que embute uma classe com F1 zero. As sensibilidades de nove classes (0,643 e 0,672) estão reportadas. Pergunta: a comparação principal deveria ser a de nove? O veredito muda?
- **Terceiro voto.** O voto cego coincidiu com o anotador 1 em 100 desacordos e com o 2 em 53. O artigo declara isso e reporta a sensibilidade "só acordo direto" (0,649). Pergunta: a assimetria compromete o ouro, e a sensibilidade basta?
- **14 itens sem consenso.** Se todos fossem acertos do SVM, o F1 ultrapassaria 0,75? Faça a conta (o artigo reporta 0,589).
- **Pós-estratificação (0,384).** Os pesos usam só a classe do léxico. O sorteio estratificou também por ano. Os pesos deveriam incluir o ano? O número muda?
- **Dependência nas 30 execuções.** As 30 observações reutilizam o mesmo corpus; só a partição muda. O artigo declara isso e limita a inferência ao corpus sob repartição. É suficiente, ou o teste de Wilcoxon está sendo usado além do que a dependência permite?
- **Bootstrap do F1-macro** com 419 itens e classes de 33 a 62 itens: a cobertura do IC é razoável? Há alternativa melhor?
- **Circularidade (Tabela 8).** As âncoras são removidas como stop words após a normalização do vetorizador. Os cinco termos do léxico com hífen ou espaço (nunca casáveis como palavra única) escapam do filtro? Isso afeta o resultado?
- **Leitura teórica.** O artigo conclui que "o classificador reproduz o léxico" (91% de coincidência SVM × léxico nos itens do ouro; acurácias contra o ouro de 61,5% e 61,8%) e que "a métrica contra o léxico superestima a qualidade semântica em cerca de 0,25 a 0,34 de F1". Essas afirmações seguem dos dados? Há alguma passagem que afirme mais do que os dados permitem?
- **H1 a H5.** H3 e H4 foram reclassificadas como "observada / não observada" (exploratórias). H5 mudou de leitura em relação à versão anterior. Os vereditos da Tabela 10 são consistentes com as Seções 6.1 a 6.5?
- **Versões de software.** A execução de parágrafo usou Python 3.13.16, numpy 2.1.3 e pandas 2.2.3, diferentes da versão anterior, com reprodução exata declarada. Verifique no log que as 15 sentinelas passaram e que o diff foi zero.

