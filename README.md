# Um pipeline reprodutível para a categorização semântica supervisionada de documentos governamentais

Artefatos do artigo **"Um pipeline reprodutível para a categorização semântica supervisionada de documentos governamentais: estudo de caso nas Mensagens ao Congresso Nacional (2023–2026)"**, versão revisada submetida à Revista de Informática Teórica e Aplicada (RITA, UFRGS) em novembro de 2026.

Autores: Ferdinand Rafols (autor correspondente, ferdinand.rafols@ufu.br), Márcio José da Cunha, Danielli Araújo Lima, Keiji Yamanaka, Alexandre Cardoso. Programa de Pós-Graduação em Engenharia Elétrica (PPGEELT), Universidade Federal de Uberlândia.

Este repositório contém tudo o que o artigo cita: o corpus limpo, o léxico, o notebook com a execução certificada, as saídas numéricas de cada tabela e figura, o protocolo e as planilhas do conjunto-ouro (anotação, desempate e reconciliação), os scripts que recomputam cada número e o fonte LaTeX do manuscrito. A versão submetida em julho de 2026 (unidade de página; notebooks v9 e v10) está preservada em `historico/`.

## Resultados centrais

| Resultado (seção do artigo) | Valor | Arquivo que o produz |
| --- | --- | --- |
| F1-macro do SVM contra os rótulos do léxico, validação cruzada de 3 dobras (6.1, Tabela 3) | 0,921 | `execucao/log_execucao_v15_3_20_10.txt`, notebook |
| Validação cruzada aninhada 5 × 3 (6.1) | 0,913 ± 0,003 | log, notebook |
| AG × busca aleatória de orçamento pareado, 30 execuções (6.2, Figura 3) | 24/30, p unilateral 0,020 | `execucao/resultados_30_execucoes.csv`, `execucao/fase6c_rs.csv` |
| Teste de circularidade 2 × 3 (6.6, Tabela 7) | 0,918 → 0,544 sem âncoras | log, `execucao/contraste_pagina/circularidade_2x3.json` |
| Concordância entre os anotadores externos (6.6) | kappa 0,606 [0,558; 0,649], alfa 0,605 | `ouro/saidas/resumo_concordancia_principal.json` |
| F1-macro do SVM contra o conjunto-ouro, 516 itens (6.6, Tabela 8; H6) | 0,579 [0,536; 0,616] | `ouro/saidas/resumo_ouro.json` |
| SVM treinado nos rótulos humanos, VC 5 × 10 (6.6, Tabela 8) | 0,635 [0,595; 0,667] | `ouro/saidas/resultado_treino_no_ouro.txt` |

## Estrutura

```
artigo/        fonte LaTeX (artigo_v3.tex, SelfArx.cls, referencias.bib) e PDF da versão revisada
notebook/      AG_RafolsFerdinand_Otimizacao_Hiperparametros_v15_3_Paragrafos.ipynb (código, sem saídas)
execucao/      o mesmo notebook com as saídas da execução certificada de 20/10/2026 (AG_v15_3_Paragrafos_executado_20261020.ipynb);
               log completo dessa execução; CSVs das 30 execuções, da busca aleatória e do histórico do AG;
               contraste_pagina/ (unidade de página: resumos, circularidade, temporal); certificado inválido de 18/08 (ver CHANGELOG)
dados/         corpus_v3_paragrafo.csv (10.757 parágrafos; label_v3 = rótulo do léxico), lexico_v3_ancoras.json (229 entradas),
               pdfs/ (cópias dos quatro PDFs oficiais e seus hashes)
ouro/          instrumento/ (planilhas em branco v1.0 e v1.1), pilotos/, principal/, desempate/, reconciliacao/, saidas/
               e as notas de resultados (Conjunto_ouro_pilotos.md, Conjunto_ouro_resultados_principal.md)
scripts/       amostragem, instrumento, concordância, construção do ouro, reconciliação, treino no ouro, patch do notebook
figuras/       scripts das figuras do artigo, dados que usam (dados/) e saídas (saida/)
auditoria/     briefing e relatório das rodadas de auditoria independente da redação
historico/     versão submetida (notebooks v9 e v10, README original)
```

## Mapa: número do artigo → arquivo → como recomputar

| Seção | O que | Arquivo | Como recomputar |
| --- | --- | --- | --- |
| 3, Tabela 1 | parágrafos, rotulados e resíduo por ano | `dados/corpus_v3_paragrafo.csv` | agrupar por `year` e `label_v3` |
| 3 | 630 parágrafos iniciados em minúscula; 298 com cabeçalho interpolado em 2023 | corpus | ver `COMO_AUDITAR.md`, passo 7 |
| 4.2 | 229 entradas do léxico, 223 casáveis | `dados/lexico_v3_ancoras.json` | contar entradas com espaço ou hífen |
| 4.4, Figura 2 | estabilidade do AG por geração | `execucao/historico_ag.csv` | `python3 figuras/figs_estabilidade_temporal.py` |
| 6.1, Tabelas 3 a 6 | classificadores, tempos, por classe, sobreajuste | `execucao/log_execucao_v15_3_20_10.txt` | células correspondentes do notebook |
| 6.2, Figura 3 | 30 execuções e busca aleatória | `execucao/resultados_30_execucoes.csv`, `fase6c_rs.csv` | `python3 figuras/figs_3_4_legiveis.py` |
| 6.3, Figura 4 | matriz de confusão | log (relatório por classe) e `scripts/construir_ouro.py` (predições fora da dobra) | |
| 6.5, Figura 5 | composição por ano | log (proporções por ano) | `figs_estabilidade_temporal.py` |
| 6.6, Tabela 7 | circularidade 2 × 3 | log; `execucao/contraste_pagina/circularidade_2x3.json` | notebook |
| 6.6 | concordância, origem do ouro, Tabela 8, pós-estratificação | `ouro/saidas/` | passos 1 a 3 de `COMO_AUDITAR.md` |
| 6.6 | treino no ouro | `ouro/saidas/resultado_treino_no_ouro.txt` | `python3 scripts/treinar_no_ouro.py ouro/saidas/conjunto_ouro.csv dados/corpus_v3_paragrafo.csv` |
| 7 | certificado de 20/10 (15 sentinelas, Δmax = 0) | `execucao/AG_v15_3_Paragrafos_executado_20261020.ipynb` (saída da última célula) e `execucao/log_execucao_v15_3_20_10.txt` | reexecutar o notebook |

## Como reproduzir

1. Ambiente: Python 3.13 e as versões de `requirements.txt` (a execução certificada usou Python 3.13.16, scikit-learn 1.6.1, numpy 2.1.3, pandas 2.2.3; a versão submetida usou Python 3.12, numpy 2.0.2 e pandas 2.2.2, e a reprodução foi exata mesmo assim).
2. Pipeline completo: abrir o notebook no Colab ou no Jupyter, apontar os caminhos dos PDFs para `dados/pdfs/` e executar na ordem. A execução certificada leva cerca de um dia de máquina em CPU; a célula final compara as 15 sentinelas declaradas com os valores obtidos e emite o certificado.
3. Conjunto-ouro, do zero, em minutos:

```
cd scripts
python3 medir_concordancia.py ../ouro/principal/principal_anotador1.xlsx ../ouro/principal/principal_anotador2.xlsx ../ouro/principal/principal_gabarito.csv ../ouro/saidas_recomputadas
python3 consolidar_reconciliacao.py ../ouro/reconciliacao/reconciliacao_rodada1_anotador1.xlsx ../ouro/reconciliacao/reconciliacao_rodada1_anotador2.xlsx ../ouro/reconciliacao/reconciliacao_gabarito.csv ../ouro/saidas_recomputadas
python3 consolidar_reconciliacao.py ../ouro/reconciliacao/reconciliacao_rodada2_anotador1.xlsx ../ouro/reconciliacao/reconciliacao_rodada2_anotador2.xlsx ../ouro/reconciliacao/reconciliacao_gabarito.csv ../ouro/saidas_recomputadas --rodada2 ../ouro/saidas_recomputadas/reconciliacao_resultado.csv
python3 construir_ouro.py ../ouro/principal/principal_anotador1.xlsx ../ouro/principal/principal_anotador2.xlsx ../ouro/desempate/desempate_terceiro_voto_final.xlsx ../ouro/desempate/desempate_gabarito.csv ../ouro/principal/principal_gabarito.csv ../dados/corpus_v3_paragrafo.csv ../ouro/saidas_recomputadas ../ouro/saidas_recomputadas/reconciliacao_resultado.csv
python3 treinar_no_ouro.py ../ouro/saidas_recomputadas/conjunto_ouro.csv ../dados/corpus_v3_paragrafo.csv
```

4. Figuras: `python3 figuras/figs_3_4_legiveis.py`, `python3 figuras/figs_estabilidade_temporal.py` e `python3 figuras/fig1_pipeline.py` (ver o cabeçalho de cada script para os argumentos).
5. Auditoria: `COMO_AUDITAR.md` traz o roteiro de sete passos usado nas três rodadas de conferência; `auditoria/` traz o briefing e o relatório.

## Conjunto-ouro: o que cada pasta contém

- `instrumento/`: as planilhas em branco entregues aos anotadores (v1.0 no primeiro piloto; v1.1, com as regras revisadas na calibração, no segundo piloto e na amostra principal). As mudanças entre versões estão na aba "Mudanças" da v1.1 e em `scripts/gerar_planilhas_anotacao.py`.
- `pilotos/`: as planilhas devolvidas nos dois pilotos (50 e 22 itens), os gabaritos do sorteio e as planilhas de calibração.
- `principal/`: as 540 planilhas devolvidas pelos dois anotadores externos, tal como entregues, o gabarito do sorteio (id no corpus, estrato, ano) e os parâmetros da amostra.
- `desempate/`: o terceiro voto cego do primeiro autor sobre os 196 desacordos, em versões sucessivas (as três checagens de regra, documentadas em `Conjunto_ouro_resultados_principal.md`), a versão final e a chave DES → PRI.
- `reconciliacao/`: as planilhas enviadas e devolvidas nas duas rodadas de reconciliação escrita dos 34 itens sem maioria, inclusive a primeira devolução do anotador 1 sem justificativas, recusada pela regra; e o gabarito das leituras anonimizadas.
- `saidas/`: o conjunto-ouro (516 itens, com a origem de cada rótulo e a predição fora da dobra do SVM), o resumo das métricas, as métricas por classe, a matriz léxico × ouro, os itens sem consenso e os excluídos, o resultado da reconciliação e o do treino no ouro.

Os anotadores são identificados como anotador 1 e anotador 2 em todos os arquivos. Nenhum dado pessoal consta do repositório.

## Licenças e citação

Código: MIT (`LICENSE`). Dados derivados, anotações e protocolo: CC BY 4.0. Os quatro PDFs das Mensagens ao Congresso Nacional são documentos públicos do Governo Federal do Brasil, redistribuídos aqui sem alteração, com os hashes em `dados/pdfs/`. Para citar, use `CITATION.cff`.
