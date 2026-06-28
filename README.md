# Categorização semântica da agenda governamental — Mensagens ao Congresso (2023–2026)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ferdinandrafols/Mensagens-ao-Congresso-Nacional-2023-2026-/blob/main/AG_RafolsFerdinand_Otimizacao_Hiperparametros_v9_final.ipynb)

Pipeline reprodutível de **categorização semântica supervisionada** de parágrafos de documentos governamentais, demonstrado sobre as **Mensagens ao Congresso Nacional (2023–2026)** — instrumentos constitucionais (Art. 84 da CF) que expressam a *agenda de governo* do Executivo, e não retórica pessoal.

Material de apoio ao artigo submetido à **RITA — Revista de Informática Teórica e Aplicada**.

## O que o pipeline faz

1. **Extração** dos 4 PDFs das Mensagens (pdfplumber)
2. **Limpeza** estrutural (remoção de cabeçalhos recorrentes e elementos editoriais)
3. **Rotulagem** por léxico temático (supervisão fraca, 9 classes)
4. **Vetorização** TF-IDF
5. **Classificação** (Regressão Logística, SVM linear, Random Forest)
6. **Otimização de hiperparâmetros** por Algoritmo Genético, como etapa auditável
7. **Avaliação** por validação cruzada (F1-macro) e teste de Wilcoxon (30 execuções independentes)
8. **Análise diacrônica** da composição temática da agenda ao longo do mandato

## Principais resultados

- Melhor modelo: **SVM linear, F1-macro = 0,807** (9 classes temáticas)
- Otimização (AG): **+13% sobre a configuração-padrão**, porém **estatisticamente equivalente** a uma busca aleatória de mesmo orçamento (p = 0,059) — um achado de calibração reportado com transparência
- Agenda de governo: **forte continuidade temática**, crescimento de *educação e ciência*, queda na proeminência de *governança institucional* após 2023 e **ausência de inflexão pré-eleitoral** em 2026

## Como executar

Clique no badge **Open in Colab** acima, ou abra o notebook `AG_RafolsFerdinand_Otimizacao_Hiperparametros_v9_final.ipynb` no Google Colab.

Antes de rodar:

- Faça upload dos 4 PDFs das Mensagens ao Congresso para `/content` (ou ajuste `PDF_DIR_BASE` para uma pasta do Drive, evitando reenviar a cada sessão).
- Ajuste `DRIVE_BASE`, na célula de **Configuração V9**, para a sua pasta do Google Drive.
- Execute as células de cima para baixo. A validação estatística de 30 execuções leva ~1h30; os checkpoints são salvos no Drive, permitindo retomar após reinícios do runtime.

**Ambiente:** Python 3.12 · scikit-learn 1.6.1 · scipy 1.16.3 · numpy 2.0.2 · pandas 2.2.2 · matplotlib 3.10.0 · pdfplumber.

## Dados

O corpus provém de quatro documentos públicos — as Mensagens ao Congresso Nacional de 2023 a 2026 —, integralmente recuperáveis a partir de suas fontes oficiais.

**Fontes oficiais (PDF):**

- 2023: https://www.gov.br/planalto/pt-br/acesso-a-informacao/acoes-e-programas/governanca/mensagem-ao-congresso-nacional/MensagemaoCongressoNacional2023.pdf
- 2024: https://www.gov.br/planalto/pt-br/acesso-a-informacao/acoes-e-programas/governanca/mensagem-ao-congresso-nacional/mensagemaocongressonacional2024_vf.pdf
- 2025: https://www.gov.br/planalto/pt-br/acesso-a-informacao/acoes-e-programas/governanca/mensagem-ao-congresso-nacional/mcn2025digitalv1.pdf
- 2026: https://www.gov.br/casacivil/pt-br/.arquivos/mensagem-ao-congresso-nacional-2026.pdf
 Os artefatos intermediários e finais (corpus rotulado, métricas por classe, matriz de confusão, proporções diacrônicas e os vetores das 30 execuções) são exportados em formato aberto pelo próprio notebook.

> **Nota sobre supervisão fraca:** como os rótulos de treino e de avaliação derivam de uma mesma fonte lexical, as métricas devem ser lidas como um *limite inferior de consistência*; sua validação plena requer um conjunto-ouro validado por anotação humana, em construção.

## Estrutura sugerida do repositório

```
.
├── AG_RafolsFerdinand_Otimizacao_Hiperparametros_v9_final.ipynb   # notebook principal
├── figuras/      # Fig1–Fig7 (.png/.pdf)
├── dados/        # CSVs exportados (corpus, métricas, matriz, diacrônica, 30 execuções)
└── README.md
```

## Autores

Ferdinand Rafols, Márcio José da Cunha, Danielli Araújo Lima, Keiji Yamanaka e Alexandre Cardoso — Programa de Pós-Graduação em Engenharia Elétrica (PPGEELT), Universidade Federal de Uberlândia (UFU).

## Citação

Artigo submetido à RITA (Revista de Informática Teórica e Aplicada). O DOI dos artefatos será adicionado mediante depósito permanente (Zenodo).

## Licença

Defina uma licença antes de tornar o repositório público. Sugestão usual para artefatos de pesquisa: **MIT** para o código e **CC BY 4.0** para dados e figuras.
