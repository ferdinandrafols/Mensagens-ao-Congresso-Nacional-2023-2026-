# CHANGELOG: da versão submetida (01/07/2026) à versão revisada (20/11/2026)

Datas de referência: submissão à RITA em 01/07/2026 (notebook v10, unidade de página, F1-macro 0,807); decisão de revisão maior em 17/10/2026; versão revisada em 20/11/2026 (notebook V15.3, unidade de parágrafo, execução certificada de 20/10/2026).

## Correções por iniciativa dos autores (encontradas em conferência própria, antes ou durante a revisão)

| Data | O que | Efeito |
| --- | --- | --- |
| 08/2026 | Hifenização de fim de linha: palavras partidas pela diagramação eram preservadas como fragmentos; correção com o próprio corpus como árbitro (2.679 remontagens, resíduo 3), controlada por flag | em página, F1 0,807 → 0,817; p AG × busca aleatória 0,059 → 0,118; sem mudança de veredito |
| 08/2026 | Primeira execução de registro com sentinelas (v14, página), certificado JSON com Δmax = 0 | passa a existir a execução certificada |
| 18/08/2026 | `Certificado_Registro_20260818T1846.json` (parágrafo) emitido por falha de lógica, sem sentinelas: diff e hash válidos, veredito inválido; mantido em `execucao/` com o prefixo INVALIDO_ | nenhum número do artigo depende dele |
| 09 a 10/2026 | Unidade de análise: o código segmentava páginas (2.089 unidades) e o texto dizia parágrafos; nova segmentação por geometria de linha (11.005 brutas, 10.757 limpas, 6.370 rotuladas); limpeza estrutural de 243 + 5 unidades | todos os números regenerados; resíduo de cerca de 22% para 40,8% |
| 10/2026 | Vetorizador da Tabela 3: Regressão Logística e Random Forest eram medidos com vetorizador diferente do SVM, apesar do que a Seção 4.3 afirmava; as três tabelas refeitas sobre o TF-IDF do AG | SVM 0,921, RF 0,917, LR 0,909 |
| 10/2026 | Orçamento da busca aleatória pareado ao orçamento efetivo do AG por semente (41,9 ± 1,2) em vez de 38 fixo; número de avaliações da execução principal 108 → 106 únicas | W, p e vitórias inalterados; magnitudes mudam |
| 20/10/2026 | Execução certificada V15.3 (15 sentinelas declaradas em 19/08, Δmax = 0 nos 60 valores das 30 execuções, Python 3.13.16 / numpy 2.1.3 / pandas 2.2.3) | base de todos os números das Seções 6.1 a 6.5 |

## Respostas aos revisores

| Ponto | O que mudou |
| --- | --- |
| H1 circularidade | teste 2 × 3 (0,918 → 0,544 sem âncoras em parágrafo); conjunto-ouro de 540 parágrafos anotados por dois externos (kappa 0,606), 516 adjudicados; métricas e H6 contra o ouro (0,579 [0,536; 0,616]) |
| H2 "limite inferior" | retirado; métricas contra o léxico descritas como concordância com a rotulagem automática |
| H3 p = 0,059 | "equivalente" retirado; "diferença não detectada"; direção dos testes declarada; em parágrafo p unilateral 0,020 e bilateral 0,040 |
| H4 30 observações | duas construções descritas; dependência declarada; orçamento pareado |
| H5 vocabulário por dobra | afirmado para todas as rotinas do pipeline; aninhada detalhada; "otimismo de seleção" retirado |
| H6 classificadores | mesma representação; limitação declarada |
| H7 inconsistências | 0,016 e "0,798 sem viés" explicados e corrigidos |
| H8, H9 temporal | denominadores, exclusões, origem das predições; tom exploratório; H3/H4 "observada / não observada"; ressalva sobre 2023 |
| H10 trabalhos relacionados | seis referências; contribuição reformulada; H6 delimitada; experimento complementar de treino no ouro |
| H11 figuras | Figura 2 nova (estabilidade do AG); Figuras 3 e 5 refeitas; figura por classe retirada |
| H12 ênfase | texto enxugado; 6.2 reduzida à metade; 6.5 a um parágrafo |

## Conjunto-ouro (cronologia)

| Data | Evento |
| --- | --- |
| 19 a 21/10/2026 | protocolo declarado; desenho revisado para dois anotadores externos e autor só como terceiro voto cego; aval do orientador em 21/10 |
| 22 a 24/10/2026 | piloto 1 (50 itens, instrumento v1.0): kappa 0,34; reunião de calibração; regras de resíduo, não classificável e parágrafo misto reescritas (v1.1) |
| 25 a 26/10/2026 | piloto 2 (22 itens, v1.1): kappa 0,73 |
| 27 a 30/10/2026 | amostra principal (540 itens) devolvida pelos dois anotadores |
| 31/10 a 04/11/2026 | terceiro voto cego sobre 196 desacordos, com três checagens de regra documentadas; ouro de 496 itens, 34 sem maioria |
| 10/11/2026 | desvio datado: a reunião dos três prevista no protocolo é substituída por reconciliação escrita entre os dois externos, sem voto do autor, com regra de decisão fixada antes do envio |
| 16 a 17/11/2026 | rodada 1: uma devolução sem justificativas recusada pela regra e reenviada com 8 códigos alterados; 17 acordos, 17 divergências |
| 19/11/2026 | rodada 2: 3 acordos, 14 sem consenso (3 cruzamentos); ouro final de 516 itens |
