# Conjunto-ouro RITA V3: resultados dos pilotos de anotação

Anotadores externos: anotador 1 (anotador 1) e anotadora 2 (anotadora 2), Ciências Sociais. O autor não anota; dá só o terceiro voto cego nos desacordos da principal. Medidas por `medir_concordancia.py`; NC excluído das medidas e reportado à parte.

## Piloto 1 (50 parágrafos, instrumento v0, devolvido 22/10)

- Itens com NC em pelo menos um anotador: 15 (anotador 1 3, anotadora 2 15); válidos 35.
- Concordância bruta 0,40; kappa de Cohen 0,339 [0,165; 0,511]; alfa de Krippendorff 0,329; kappa com confiança 3 pelos dois 0,534 (n = 19).
- 33 desacordos: 12 NC × classe; 10 RES × classe (anotadora 2 usou RES 10 vezes nos válidos, anotador 1 nenhuma); 11 classe × classe (SOC × SAU/AGR, GOV × áreas, INF × AMB). Sem NC e sem RES: 25 itens, acordo 0,56, kappa 0,50 [0,26; 0,71]. Em 4 itens a classe de um era o misto do outro; contando classe ou misto, 20 acordos em 35.
- Preenchimento mecânico 100% correto nos dois (códigos, confiança, subtipo só em RES/NC, misto nunca em RES/NC). Registro de sessões em branco.
- Acordo de cada anotador com o léxico, nos 32 itens rotulados: 0,53 e 0,53 (kappa 0,47 e 0,49). Nos 3 itens do resíduo, os dois deram a mesma classe.
- Achado de corpus: 172 parágrafos de 2023 (24% do ano) têm o cabeçalho corrido da página interpolado no texto ("– DESAFIOS À … RECONSTRUÇÃO … DO PAÍS E DO"); 628 parágrafos (5,8%) começam em minúscula (truncados na quebra de página). Vai para as limitações do artigo.

## Calibração (reunião 22/10) e instrumento v1.0

Decisões, todas incorporadas em `gerar_planilhas_anotacao.py` (quadro "O que mudou nesta versão" na aba Instruções):
1. Ordem das regras: 1 (predominância, com o teste do título), 2 (finalidade) e só então 3; "tema que abre" é só desempate.
2. Regra 3: misto só em empate real, depois do teste do título; com misto, confiança 1 ou 2.
3. Regra 4: balanço, crítica, compromisso ou opinião sobre uma área pertence à área; ação operacional conta como a área servida; RES só quando nenhuma das nove áreas aparece.
4. Regra 5: "comunicações" passa a "radiodifusão e telecomunicações como setor"; tecnologia e IA seguem a Regra 2 (área aplicada).
5. Regra 6: critério único, sobra tema ou não. Cabeçalho misturado e início truncado são ignorados; título ou legenda com área identificável recebe a classe, confiança 1 e "título"/"legenda" em observações; NC só sem tema reconhecível.
6. Regra 7: conhecer os termos é vocabulário e vale; não usar suposições sobre capítulo ou ano; sem internet ou outras fontes durante a anotação; termo desconhecido vai para observações.
7. Fronteiras novas na aba Categorias: benefício em dinheiro é SOC, assistência e medicamento é SAU; fila do INSS é SOC; startups e inovação é EDU; GOV restrito a organização do Estado, integridade e gestão fiscal; energia é AMB mesmo como obra; fundo de infraestrutura "sustentável" é INF; insumos e assistência técnica rural é AGR.
8. Registro de sessões a cada sessão; em dúvida entre duas classes, observação com as duas candidatas.

## Piloto 2 (22 parágrafos novos, v1.0, devolvido 23/10)

Sorteio por `amostra_piloto2.py` (semente 43, fora do piloto 1 e da principal): 1 item de 2023–2024 e 1 de 2025–2026 por classe e para o resíduo (20), mais 2 itens de ruído inseridos de propósito (PIL0113 cabeçalho interpolado; PIL0101 truncado). Ids PIL0101..PIL0122.

- NC: 0. Faltantes: 0. Válidos: 22.
- Concordância bruta 0,77 (17 de 22); kappa 0,732 [0,496; 0,938]; alfa 0,737; kappa com confiança 3 pelos dois 0,744 (n = 14).
- Misto: anotador 1 0, anotadora 2 1. Observações: 0 e 3. Registro de sessões preenchido pelos dois: 17 min (anotador 1) e 40 min (anotador 2) para 22 itens.
- Ruído: PIL0113 recebeu ECO dos dois; PIL0101 foi classificado pelos dois (GOV × ECO), sem NC. PIL0119 (legenda truncada): anotadora 2 aplicou a regra nova ("título", confiança 1).
- 5 desacordos, todos classe × classe: PIL0101 GOV × ECO; PIL0102 ECO × EXT; PIL0103 AMB × EXT (misto AMB); PIL0110 INF × GOV; PIL0119 GOV × AMB.
- Léxico: acordo 0,47 (anotador 1) e 0,53 (anotador 2) nos 19 itens rotulados. Dos 17 itens em que os dois concordaram, 9 coincidem com o léxico, 3 são resíduo recuperado e 5 contradizem o léxico com os dois de acordo.
- Ponto de regra detectado: PIL0118 (obras de UBS do Novo PAC Saúde) recebeu INF dos dois; a Regra 2 leva a SAU. Incorporado como v1.1: obra de equipamento setorial vai para a área servida (UBS e hospital SAU, escola EDU, unidade do SUAS SOC); obra de transporte, saneamento e mobilidade INF; energia AMB.

Decisão (23/10): seguir para a principal com o instrumento v1.1 (limiar combinado era kappa ≥ 0,50).

## Expectativa para a H6

Nos dois pilotos, cada anotador concordou com o rótulo do léxico em cerca de metade dos itens rotulados. Se a proporção se mantiver nos 540, o F1 do pipeline contra o ouro deve ficar na faixa de 0,5 a 0,6, e a H6 (F1 ≥ 0,75, regra pré-registrada) não se confirma. O artigo deve reportar o resultado como está, em contraste com os 0,92 da validação cruzada contra os próprios rótulos do léxico. Amostras pequenas (32 e 19 itens rotulados); a principal é que decide.

## Cronograma da principal

Envio 23/10; devolução das planilhas fechadas até 28/10 (a confirmar com a anotadora 2, pelo ritmo do piloto 2: 7 a 16 h por anotador); medidas e planilha de desempate cego em 28–29/10; F1 contra o ouro em 29–30/10; reescrita até 03/11; coautores 04/11; submissão 05/11.
