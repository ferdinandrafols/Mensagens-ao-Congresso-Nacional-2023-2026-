# Execução certificada (V15.3, 20/10/2026)

- `AG_v15_3_Paragrafos_executado_20261020.ipynb`: o notebook tal como baixado do Colab depois da execução certificada, com as saídas de todas as células gravadas; o código é idêntico ao de `notebook/`, e a última célula traz o veredito (APROVADA, Δmax = 0) e o nome do certificado emitido (`Certificado_Registro_20261020T0340.json`).
- `log_execucao_v15_3_20_10.txt`: as mesmas saídas em texto, inclusive o relatório por classe, as proporções por ano, o teste de circularidade e a célula de certificação (15 sentinelas declaradas em 19/08/2026, Δmax = 0 nos 60 valores das 30 execuções de AG e baseline).
- `resultados_30_execucoes.csv`: F1 do AG e do baseline por semente (0 a 29). `fase6c_rs.csv`: F1 e orçamento da busca aleatória pareada por semente. `historico_ag.csv`: melhor, médio e pior F1, genes do melhor indivíduo e diversidade por geração da execução principal.
- `contraste_pagina/`: resumos da unidade de página e de parágrafo, circularidade 2 × 3 e teste temporal, usados nas comparações entre unidades.
- `INVALIDO_Certificado_Registro_20260818T1846.json`: certificado emitido por falha de lógica, sem sentinelas (diff e hash válidos, veredito inválido); mantido por transparência. Ver CHANGELOG.
- Pendente para a versão final: o certificado JSON de 20/10 e a declaração das sentinelas de 19/08 (hoje no Drive do projeto) serão adicionados aqui.
