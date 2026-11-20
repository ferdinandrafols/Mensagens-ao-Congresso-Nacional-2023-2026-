# Conjunto-ouro RITA V3: resultados da amostra principal (04/11/2026)

Fontes: `principal_anotador1.xlsx` (anotador 1), `principal_anotador2.xlsx` (anotador 2), `desempate_terceiro_voto_final.xlsx` (primeiro autor, voto cego), gabaritos em `amostra_ouro_v1/`, corpus `corpus_v3_paragrafo.csv` (sha256[:16] e7f15cef91f89d26). Scripts: `medir_concordancia.py`, `construir_ouro.py`. Saídas em `principal_recebidas/ouro/` (conjunto_ouro.csv, resumo_ouro.json, por_classe.csv, matriz_lexico_vs_ouro.csv, itens_sem_maioria.csv, itens_excluidos_nc.csv).

## Anotação (540 parágrafos, instrumento v1.1)

- Entregas: anotador 1 27/10 (7 sessões, ~5 h, 540/540); anotadora 2 30/10 (8 sessões, ~9,6 h, 540/540; dois itens sem confiança e um NC sem subtipo, mantidos como entregues). Nenhum código inválido.
- NC: anotador 1 3, anotadora 2 8 (um em comum); 10 itens excluídos das medidas (1,9% da amostra, dentro do limite de 2% do protocolo).
- Concordância externo 1 × externo 2 (530 válidos): bruta 0,647; kappa de Cohen 0,606 [0,558; 0,649]; alfa de Krippendorff 0,605; kappa nos 391 itens com confiança 3 pelos dois: 0,701. Limiar do protocolo (0,60) atingido no ponto estimado; o IC cruza o limiar.
- Kappa binário por classe: SAU 0,87; EDU 0,80; EXT 0,73; AMB 0,69; AGR 0,61; INF 0,58; SOC 0,54; GOV 0,50; RES 0,44; ECO 0,34. Maiores confusões: GOV × RES (23), ECO × RES (12), SOC × GOV (10), AGR × SOC (9), INF × ECO (9), INF × GOV (8). RES: anotador 1 28, anotadora 2 76.
- Externo × léxico (444 rotulados sem NC): acordo 0,60 e 0,54; kappa 0,552 (anotador 1) e 0,495 (anotador 2).
- Defeitos de segmentação na amostra: 110 itens (20%) com cabeçalho interpolado, início truncado ou sem pontuação final; nesses, acordo 0,61 e kappa 0,56, contra 0,66 e 0,62 nos 430 limpos; NC em 8 dos 110 e em 2 dos 430.

## Terceiro voto cego (primeiro autor)

- 196 itens em desacordo, ids embaralhados, sem rótulos, léxico ou confiança. Checagem de regras (sem acesso à chave) após 12 itens (uma correção por erro de regra: cultura é RES) e após 29 itens (cinco correções: Regras 4, 6 e fronteiras de GOV); checagem final dos 167 restantes com 32 correções, mais uma alteração própria do votante (DES0113, ECO para EDU) registrada antes da abertura da chave; todas documentadas em versões sucessivas da planilha. Uso de misto 13%.
- Dos 187 desacordos sem NC: o voto coincidiu com anotador 1 em 100 e com anotadora 2 em 53 (kappa voto 3 × anotador 1 0,47; × anotadora 2 0,19); 34 itens sem maioria (três leituras distintas), que o protocolo encaminha a reunião dos três. Pares mais frequentes nos itens sem maioria: GOV × RES (7), SOC × GOV (3).

## Conjunto-ouro

- 496 itens: 343 por acordo direto (63,5% da amostra), 153 por maioria com o voto cego (28,3%); 34 pendentes de reunião (6,3%); 10 excluídos por NC (1,9%).
- Distribuição do ouro: GOV 78, AMB 64, EDU 54, SAU 53, INF 49, SOC 46, ECO 43, RES 39, AGR 36, EXT 34.
- Recuperação do resíduo: dos 77 itens do resíduo do léxico que entraram no ouro, 74 (96%) receberam uma das nove classes (GOV 16, AMB 12, ECO 10, SOC 9, EDU 8, INF 8, SAU 5, EXT 3, AGR 3); 3 ficaram RES.

## Desempenho do pipeline contra o ouro

Predições do SVM fora da dobra reproduzidas aqui (StratifiedKFold 3, shuffle, semente 42; TF-IDF 2.352 unigramas, sublinear; LinearSVC C = 0,8245): F1-macro contra o léxico 0,9202 (o notebook reporta 0,9208; diferença de ambiente de 6 × 10⁻⁴).

| Comparação | n | F1-macro | IC 95% | Acurácia |
| --- | --- | --- | --- | --- |
| **SVM (fora da dobra) × ouro, rotulados, 10 códigos (pré-registrada)** | 419 | **0,589** | [0,546; 0,625] | 0,633 |
| SVM × ouro, só itens cujo ouro é uma das nove classes | 383 | 0,684 | [0,634; 0,726] | |
| SVM × ouro, só acordo direto dos externos (sem participação do autor) | 299 | 0,649 | [0,600; 0,691] | |
| SVM × ouro, só itens sem defeito de segmentação | 337 | 0,578 | [0,531; 0,617] | |
| Léxico (classe ou RES) × ouro, todos os itens do ouro | 496 | 0,545 | [0,505; 0,581] | 0,538 |

- Acurácia do rótulo do léxico contra o ouro, ponderada por pós-estratificação para o corpus (pesos N_classe/n_classe): 0,384. A queda vem do resíduo (41% do corpus), em que 96% dos itens recebem uma classe no ouro.
- Por classe (léxico × ouro, F1): SAU 0,84; EDU 0,78; INF 0,66; AMB 0,64; AGR 0,60; EXT 0,56; SOC 0,47; GOV 0,44; ECO 0,43; RES 0,05. SVM × ouro nos rotulados: SAU 0,89; EDU 0,85; INF 0,76; AMB 0,76; AGR 0,63; EXT 0,56; SOC 0,51; ECO 0,48; GOV 0,47.
- Maiores confusões léxico → ouro: RES → GOV 16, RES → AMB 12, RES → ECO 10, RES → SOC 9, SOC → GOV 9, RES → INF 8, RES → EDU 8, EXT → GOV 7.
- Acerto do léxico por ano: 2023 0,67 (n 61); 2024 0,50 (91); 2025 0,51 (154); 2026 0,53 (190).

## H6

Regra pré-registrada (Protocolo, Seção 8): confirmada se o F1-macro do SVM contra o ouro e o limite superior do IC 95% ficam abaixo de 0,75. Resultado: 0,589 [0,546; 0,625]. **H6 confirmada.** O veredito se mantém em todas as análises de sensibilidade (limite superior máximo 0,726, na comparação restrita às nove classes).

## Leitura para o artigo

1. O F1 de 0,92 da validação cruzada mede concordância com o próprio léxico; contra leitores independentes, o mesmo classificador fica em 0,59 (0,68 excluindo o resíduo). A diferença é o custo da circularidade que o revisor H apontou, agora medido.
2. O resíduo do léxico não é "outros": 96% dos parágrafos que o léxico deixou sem classe têm uma classe para leitores humanos, o que derruba a acurácia estimada para o corpus a 0,38.
3. As classes com fronteira semântica nítida (SAU, EDU) são bem categorizadas pelo pipeline (F1 0,84 e 0,78 contra o ouro); as de fronteira difusa (GOV, ECO, SOC) são o problema, tanto entre humanos (kappa 0,34 a 0,54) quanto para o léxico.
4. O conjunto-ouro é reportado com sua origem (63,5% acordo direto; 28,3% maioria com voto cego; 6,3% sem maioria; 1,9% NC) e com a assimetria do voto cego (coincidiu mais com anotador 1 do que com anotadora 2), em nome da transparência.
5. A segmentação não explica o resultado: nos itens sem defeito o F1 é 0,578, igual ao geral dentro do IC.

## Pendências

- Reunião dos três sobre os 34 itens sem maioria (itens_sem_maioria.csv). Enquanto não ocorrer, o artigo declara os 34 como não adjudicados e reporta o ouro de 496 itens.
- Declarar no artigo a checagem de regras do terceiro votante (três checagens, 39 alterações, todas antes do cruzamento).
- Atualizar o Protocolo (Seção 8: taxa de desempate e sensibilidades realizadas; Seção 9: pendências encerradas) e a carta ao revisor H com os números acima.

## Reconciliação escrita dos 34 itens sem maioria (10 a 19/11/2026)

Desvio datado do Protocolo: a reunião dos três prevista na Seção 8 foi substituída por reconciliação escrita, independente, entre os dois anotadores externos (`gerar_reconciliacao.py`, `consolidar_reconciliacao.py`), com as três leituras anonimizadas em ordem sorteada (semente 42), justificativa obrigatória e duas rodadas; o primeiro autor não votou. Regra fixada antes de abrir as planilhas: códigos finais coincidentes → ouro (origem `reconciliacao_escrita`); divergentes na rodada 1 → rodada 2 com troca de justificativas (sem nome); divergentes na rodada 2 → `sem_consenso`, fora do ouro.

- Rodada 1 (devolvida 16 e 17/11): 17 coincidências, 17 divergências. O anotador 1 devolveu em 16/11 sem justificativas, o que a regra invalida; reenviou em 17/11 com justificativas e 8 códigos alterados (4 aproximaram do código do anotador 2, 4 afastaram), sem acesso aos códigos do outro; vale a segunda devolução; a primeira fica arquivada. Anotador 1: manteve 20, adotou a leitura do outro em 9, o voto cego em 5; anotador 2: manteve 20, adotou 9, voto cego 3.
- Rodada 2 (devolvida 19/11, 17 itens): 3 coincidências, 14 sem consenso; quatro cruzamentos (cada um adotou o código do outro). Anotador 1: manteve 8, adotou 4, voto cego 4; anotador 2: manteve 11, adotou 5, voto cego 0.
- Saldo: 20 itens entram no ouro (código acordado = leitura original do anotador 1 em 10, do anotador 2 em 8, do voto cego em 2); 14 sem consenso (economia em 9 deles, programas sociais em 8, governança em 6).

## Conjunto-ouro final (516 itens) e desempenho

Origem: 343 acordo direto (63,5%), 153 maioria com voto cego (28,3%), 20 reconciliação escrita (3,7%); 14 sem consenso (2,6%) e 10 NC (1,9%) fora. Distribuição: GOV 87, AMB 67, EDU 55, SAU 53, INF 50, SOC 46, ECO 43, RES 41, AGR 38, EXT 36. Resíduo: dos 90 sorteados, 82 no ouro; 79 (96%) recebem classe (GOV 17, AMB 13, ECO 10, SOC 9, EDU 9, INF 9, SAU 5, AGR 4, EXT 3); 3 RES.

| Comparação | n | F1-macro | IC 95% |
| --- | --- | --- | --- |
| **SVM OOF × ouro, rotulados, 10 códigos (pré-registrada)** | 434 | **0,579** | [0,536; 0,616]; acurácia 0,618 |
| nove classes, RES-ouro como erro | 434 | 0,643 | [0,595; 0,684] |
| nove classes, só ouro nas nove | 396 | 0,672 | [0,627; 0,713] |
| só acordo direto | 299 | 0,649 | [0,600; 0,691] |
| só itens sem defeito de segmentação | 351 | 0,569 | [0,522; 0,609] |
| SVM × anotador 1 / anotador 2 | 434 | 0,562 / 0,552 | [0,520; 0,598] / [0,509; 0,588] |
| Léxico × ouro, todos | 516 | 0,534 | [0,493; 0,569]; acurácia 0,523 |
| SVM treinado no ouro, VC 5×10, 10 códigos / 9 classes | 516 / 475 | 0,635 / 0,661 | [0,595; 0,667] / [0,624; 0,693] |

- Cenário máximo (14 sem consenso como acertos do SVM): 0,589. H6 confirmada; limite superior máximo nas sensibilidades 0,713.
- Acurácia ponderada do léxico para o corpus: 0,376 [0,344; 0,410] (bootstrap por estrato) = 0,592 × 0,610 + 0,408 × 0,037.
- Por classe (léxico × ouro, F1): SAU 0,84; EDU 0,77; INF 0,65; AMB 0,62; AGR 0,58; EXT 0,54; SOC 0,45; GOV 0,43; ECO 0,42; RES 0,05. SVM nos rotulados: SAU 0,89; EDU 0,85; INF 0,74; AMB 0,73; AGR 0,61; EXT 0,55; SOC 0,49; ECO 0,46; GOV 0,46.
- Léxico e SVM acertam o ouro em 61,5% e 61,8% dos 434 rotulados; coincidem em 91,5%.
- Treino no ouro: variantes (C = 1; vocabulário por dobra) entre 0,632 e 0,666; léxico aprendido a 0,708 com 434 itens; curva 0,554 (50%) e 0,598 (75%).
- Saídas em `conjunto_ouro_final_516.zip` (conjunto_ouro.csv, resumo_ouro.json, por_classe.csv, matriz_lexico_vs_ouro.csv, itens_sem_consenso.csv, itens_excluidos_nc.csv, reconciliacao_resultado.csv, resultado_treino_no_ouro.txt).

Pendência encerrada: não há mais itens sem adjudicação. As pendências de "reunião dos três" acima ficam como histórico.
