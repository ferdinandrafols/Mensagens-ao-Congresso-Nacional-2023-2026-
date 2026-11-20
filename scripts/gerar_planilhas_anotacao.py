#!/usr/bin/env python3
"""Gera as planilhas de anotação do conjunto-ouro a partir dos CSVs sorteados por amostra_ouro.py.

Uso: python3 gerar_planilhas_anotacao.py <pasta_da_amostra> <pasta_de_saida>

Saída: piloto_anotador1.xlsx, piloto_anotador2.xlsx, principal_anotador1.xlsx, principal_anotador2.xlsx
Cada arquivo tem três abas: "Instruções" (como usar, colunas, regras), "Categorias" (definições completas) e "Anotação"
(id, texto e as colunas que o anotador preenche, com listas suspensas). Nenhum rótulo nem ano.
"""
import sys, os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

CLASSES = [
    ("ECO", "Economia e desenvolvimento"),
    ("SOC", "Programas sociais"),
    ("SAU", "Saúde"),
    ("EDU", "Educação e ciência"),
    ("AGR", "Reforma agrária e agropecuária"),
    ("EXT", "Política externa"),
    ("INF", "Infraestrutura logística"),
    ("AMB", "Meio ambiente e energia"),
    ("GOV", "Governança institucional"),
    ("RES", "Resíduo institucional (geral ou tema fora do esquema)"),
    ("NC", "Não classificável (fragmento, editorial)"),
]
# Definições completas (mesmo conteúdo da Seção 5 do livro de códigos)
DEFINICOES = [
    ("ECO", "Economia e desenvolvimento",
     "Política macroeconômica, fiscal e tributária; indústria, comércio interno, inovação produtiva, crédito e investimento em geral; emprego e renda como política econômica.",
     "Reforma tributária, arcabouço fiscal, política industrial, microcrédito para empresas, salário mínimo, mercado de trabalho.",
     "Transferência de renda a famílias (SOC); crédito rural (AGR); comércio exterior e acordos comerciais (EXT); obras (INF); ciência e tecnologia (EDU)."),
    ("SOC", "Programas sociais",
     "Proteção e assistência social, transferência de renda, combate à fome e à pobreza, previdência, benefícios a pessoas e famílias.",
     "Bolsa Família, BPC, SUAS, segurança alimentar, previdência social e atendimento do INSS (fila, perícia), pensões e benefícios em dinheiro a pessoas, habitação popular quando apresentada como política social.",
     "Assistência, medicamentos e atendimento de saúde (SAU); educação (EDU); direitos de grupos e cidadania (GOV); emprego e renda como política econômica (ECO); produção, assistência técnica e insumos rurais, mesmo para famílias pobres (AGR)."),
    ("SAU", "Saúde",
     "Sistema de saúde, atenção básica e hospitalar, vigilância, vacinação, medicamentos, profissionais de saúde.",
     "SUS, Mais Médicos, Farmácia Popular, assistência farmacêutica e Rename, saúde indígena, saúde mental, complexo industrial da saúde quando o foco é o atendimento.",
     "Pensão ou benefício em dinheiro a pacientes (SOC); pesquisa biomédica como ciência (EDU); produção industrial de insumos como política industrial (ECO); saneamento (INF)."),
    ("EDU", "Educação e ciência",
     "Educação básica, profissional e superior; ciência, tecnologia e pesquisa; formação de professores e estudantes.",
     "Fundeb, Pé-de-Meia, Prouni, Fies, universidades e institutos federais, CNPq, Capes, política de C&T, fomento à pesquisa e à inovação, aceleração de startups por programas de C&T.",
     "Política industrial e produtividade de setores (ECO); inclusão digital como infraestrutura (INF); bolsas como transferência de renda sem vínculo escolar (SOC); IA aplicada a outra área segue a Regra 2."),
    ("AGR", "Reforma agrária e agropecuária",
     "Agricultura, pecuária, agricultura familiar, reforma agrária, assentamentos, crédito e seguro rural, abastecimento.",
     "Plano Safra, Pronaf, Incra, Embrapa, PAA quando apresentado como política agrícola, defesa agropecuária, assistência técnica rural, viveiros e insumos para produção, fertilizantes.",
     "Alimentação escolar e segurança alimentar de famílias (SOC); desmatamento e biomas (AMB); exportações do agro como comércio exterior (EXT); terras indígenas (GOV)."),
    ("EXT", "Política externa",
     "Relações internacionais, diplomacia, integração regional, organismos multilaterais, comércio exterior, cooperação internacional.",
     "Mercosul, Brics, G20, ONU, acordos comerciais, presidências de fóruns, cooperação Sul-Sul.",
     "Cooperação setorial cujo assunto predomina (SAU, AMB, EDU); defesa nacional (RES, tema fora do esquema)."),
    ("INF", "Infraestrutura logística",
     "Transportes, logística, obras públicas, saneamento, mobilidade urbana, concessões e parcerias de infraestrutura, conectividade física.",
     "Novo PAC em obras e modais, rodovias, ferrovias, portos, aeroportos, hidrovias, saneamento básico, banda larga como rede física, fundos e financiamento de infraestrutura regional (mesmo com o adjetivo 'sustentável').",
     "Obra de equipamento setorial: UBS e hospital (SAU), escola e creche (EDU), unidade do SUAS (SOC); energia e transição energética, mesmo quando é obra (AMB); habitação como política social (SOC); política fiscal em geral (ECO)."),
    ("AMB", "Meio ambiente e energia",
     "Política ambiental, clima, biomas, desmatamento, biodiversidade, resíduos; política energética, petróleo e gás, renováveis, transição energética.",
     "Fundo Amazônia, PPCDAm, COP, licenciamento, hidrelétricas, eólica e solar, pré-sal, combustíveis, transição e segurança energética, operações de combate a incêndios florestais e a desastres ambientais.",
     "Obras de transporte e saneamento (INF); regularização fundiária agrícola (AGR); povos indígenas como direitos (GOV); negociação internacional do clima quando o foco é a diplomacia (EXT); desinformação sobre políticas públicas (GOV)."),
    ("GOV", "Governança institucional",
     "Organização e funcionamento do Estado: transparência, controle, integridade, gestão pública e patrimonial, servidores, gestão fiscal e revisão de gastos, federalismo, democracia, Poderes, migração e cidadania; direitos de grupos específicos (indígenas, quilombolas, mulheres, LGBTQIA+); combate a crimes contra a administração.",
     "CGU, TCU, concursos, reforma administrativa, participação social, conselhos, demarcação de terras, políticas de igualdade, enfrentamento à desinformação, governo digital e IA na gestão pública.",
     "Programa com público e finalidade setorial vai para a área: fila e atendimento do INSS (SOC), startups e inovação (EDU), obra (INF). Benefícios a grupos vulneráveis como assistência (SOC); segurança pública e defesa (RES, tema fora do esquema); relação com o Congresso em introduções gerais (RES)."),
    ("RES", "Resíduo institucional",
     "Ação de governo em geral em que nenhuma das nove áreas aparece (introduções de capítulo, balanço do governo como um todo, relação com o Parlamento), OU tema fora do esquema de nove classes. Balanço, crítica, compromisso ou ação operacional SOBRE UMA ÁREA pertence à área (Regra 4).",
     "Subtipo 'geral'; ou o tema: segurança pública, cultura, esporte, direitos humanos, defesa, radiodifusão e telecomunicações, turismo, trabalho, outro tema.",
     "Crítica a governos anteriores sobre uma área (a área); operação ou força-tarefa setorial (a área); tecnologia e IA aplicadas a uma área (a área, Regra 2). RES é classe de conteúdo, não de dúvida: dúvida entre duas classes se resolve pelas Regras 1 a 3."),
    ("NC", "Não classificável",
     "O texto não permite juízo mesmo ignorando cabeçalho misturado e início truncado: sequência de números, lista de nomes sem assunto, trecho ilegível, título ou legenda sem área identificável.",
     "Subtipo: fragmento, editorial, outro (descrever em observações).",
     "Parágrafo truncado ou com cabeçalho de página misturado, mas com área identificável no restante (a área, Regra 6); título ou legenda com área identificável (a área, confiança 1, 'título' ou 'legenda' em observações)."),
]
COLUNAS = [
    ("id_item", "sistema", "Identificador do parágrafo (PIL0001… no piloto; PRI0001… na principal). Não alterar."),
    ("texto", "sistema", "Texto do parágrafo, isolado do contexto. Não alterar. É a única base para a decisão."),
    ("classe", "anotador", "Obrigatória. Um código da lista: ECO, SOC, SAU, EDU, AGR, EXT, INF, AMB, GOV, RES ou NC. Ver a aba Categorias."),
    ("confianca", "anotador", "Obrigatória. 1 = baixa (dúvida real entre classes), 2 = média, 3 = alta (sem dúvida)."),
    ("misto", "anotador", "Opcional. Só quando a Regra 3 foi aplicada: a segunda classe de um parágrafo em que dois temas empatam mesmo após o teste do título (Regra 1). A coluna 'classe' fica com o tema que abre o parágrafo. Tema secundário apenas mencionado não é misto."),
    ("subtipo", "anotador", "Só para RES e NC. Para RES: 'geral' ou o nome do tema fora do esquema. Para NC: 'fragmento', 'editorial' ou 'outro'. Vazio nas demais classes."),
    ("observacoes", "anotador", "Opcional. Uma linha: dúvida, regra aplicada, discordância com o esquema. É lida na adjudicação; não altera a classe."),
]

SUBTIPOS = ["geral", "segurança pública", "cultura", "esporte", "direitos humanos", "defesa",
            "radiodifusão e telecomunicações", "turismo", "trabalho", "outro tema", "fragmento", "editorial", "outro"]
VERSAO = "v1.1 (23/10/2026, após o segundo piloto; v1.0 em 22/10, após a calibração)"
REGRAS = [
    ("1. Predominância", "A classe é a da área a que o parágrafo como um todo serve: o tema que ocupa mais texto, ou ao qual os outros elementos estão subordinados. Teste: se este parágrafo tivesse um título de uma linha, de que área seria o título? A ordem em que os temas aparecem não importa; a presença de uma palavra também não basta. Um tema secundário apenas mencionado não entra em 'misto'.",
     "\"O crédito do Pronaf para a agricultura familiar alcançou R$ 70 bilhões, com juros menores e mais renda no campo.\" Fala de crédito, juros e renda; o título seria sobre política agrícola: AGR. \"O Programa investe em capacitação de agentes e, com isso, ampliou em 40% a cobertura vacinal.\" Abre com capacitação, mas o parágrafo serve à vacinação: SAU."),
    ("2. Finalidade sobre instrumento", "Quando o parágrafo descreve um instrumento (lei, decreto, verba, empréstimo, acordo, obra, concurso, comissão, operação) a serviço de uma área, prevalece a área servida, e não o tipo do instrumento. Tecnologia digital e inteligência artificial também são instrumento: vão para a área em que são aplicadas.",
     "\"Foi sancionada a lei que cria o programa de bolsas para estudantes do ensino médio.\" Instrumento: lei; finalidade: EDU (e não GOV). \"O BNDES liberou R$ 2 bilhões para obras de saneamento.\" INF (e não ECO). \"Das 1,3 mil obras de UBS retomadas, 408 foram concluídas.\" Obra de equipamento de saúde: SAU (e não INF); o mesmo vale para escola (EDU) e hospital (SAU). Obra de transporte, saneamento e mobilidade: INF; de energia: AMB. \"Acordo com a OMS para produção de vacinas.\" SAU (e não EXT). \"Uso de inteligência artificial para reduzir prazos no atendimento ao migrante.\" GOV. \"Debates sobre IA na educação para preparar a escola pública.\" EDU."),
    ("3. Parágrafo misto (empate real)", "Aplique a Regra 1 primeiro. Só quando, mesmo após o teste do título, não dá para dizer qual dos dois temas predomina, use o tema que abre o parágrafo como 'classe' e registre o outro em 'misto'. 'Misto' é para empate, e empate pede confiança 1 ou 2.",
     "\"Foram contratadas 3 mil escolas em tempo integral e 500 unidades básicas de saúde nos municípios do Norte.\" Dois temas com o mesmo peso: classe EDU (abre o parágrafo), misto SAU, confiança 2. Se o parágrafo seguisse falando só das unidades de saúde, a Regra 1 decidiria: SAU, sem misto."),
    ("4. Resíduo institucional (RES)", "As classes são áreas temáticas. Balanço, diagnóstico, crítica a governos anteriores, compromisso genérico ou opinião sobre uma área pertencem a essa área; ação operacional (operação, força-tarefa, obra, comissão) conta como a área que serve, mesmo sem ser uma política formal. RES só quando nenhuma das nove áreas aparece: introduções de capítulo, balanço do governo como um todo, relação com o Congresso. Subtipo 'geral'.",
     "\"Este capítulo apresenta as principais realizações do governo em 2025, em diálogo permanente com o Congresso Nacional.\" RES, subtipo geral. \"De forma perversa, não houve destinação de novas áreas para a reforma agrária.\" Crítica sobre uma área: AGR. \"A Operação Pantanal 2 deu apoio logístico ao combate aos incêndios florestais.\" Ação operacional ambiental: AMB. \"O Governo manterá o compromisso com o desenvolvimento econômico sustentável e o controle da inflação.\" Compromisso sobre uma área: ECO."),
    ("5. Tema fora do esquema", "Segurança pública, cultura, esporte, direitos humanos, defesa, radiodifusão e telecomunicações como setor, turismo e trabalho não têm classe própria: classe RES e o tema na coluna 'subtipo'. Tecnologia, governo digital e IA não são tema fora do esquema: seguem a Regra 2.",
     "\"O programa de combate ao crime organizado ampliou a presença da Polícia Federal nas fronteiras.\" RES, subtipo 'segurança pública'. \"Renovação das concessões de rádio e TV e regulação da telefonia.\" RES, subtipo 'radiodifusão e telecomunicações'."),
    ("6. Não classificável (NC)", "Critério único: sobra tema ou não. Ignore cabeçalhos de página em maiúsculas misturados ao texto e o início truncado do fragmento; se o que resta permite identificar a área, classifique, com a confiança que o texto permitir. Título solto ou legenda de tabela com área identificável também recebe a classe, com confiança 1 e a palavra 'título' ou 'legenda' em observações. NC só quando não há tema reconhecível: sequência de números, lista de nomes sem assunto, trecho ilegível. Dúvida entre duas classes não é NC (Regras 1 a 3).",
     "\"– DESAFIOS À vel ao controle social e à gestão participativa no SUS; a retomada das RECONSTRUÇÃO conferências nacionais de saúde…\" Cabeçalho misturado; o restante é sobre o SUS: SAU. \"a produção nacional de fertilizantes aumentasse em mais de 6%. A meta é aumentar a capacidade em 18% até 2026.\" Começa truncado; o tema é claro: AGR. \"O BRASIL AO Tabela 1 – Demandas da transição para a LOA\" Legenda com tema de orçamento: ECO, confiança 1, observação 'legenda'. \"Tabela 3.2 Valores em R$ milhões 2023 2024 2025\" Sem tema: NC, subtipo 'editorial'."),
    ("7. Só o texto apresentado", "Use o que você sabe sobre os termos (siglas, programas, instituições, leis): isso é vocabulário, e é esperado. Não use suposições sobre o capítulo em que o parágrafo estava nem sobre o ano, e não consulte internet, o artigo ou outras fontes durante a anotação. Termo desconhecido: classifique pelo restante, com confiança menor, e registre 'termo desconhecido: X' em observações.",
     "\"Demandas da transição para a LOA\": saber que LOA é a lei orçamentária é vocabulário, e vale: ECO. Se o parágrafo fala de \"a ministra\" sem dizer de quê, não deduza a pasta pelo ano: julgue pelo que o texto diz sobre a ação."),
]
MUDANCAS = [  # (ponto, como era no piloto, como fica na v1.0)
    ("Ordem das regras", "As regras eram lidas de forma independente; a Regra 3 (tema que abre o parágrafo) acabava decidindo sozinha.",
     "Aplique na ordem: 1 (predominância), 2 (finalidade) e só então 3. 'Tema que abre' é apenas desempate."),
    ("Regra 1, predominância", "'A classe é a da política de que o parágrafo trata predominantemente.'",
     "Teste do título: se o parágrafo tivesse um título de uma linha, de que área seria? A ordem de aparição dos temas não importa. Tema só mencionado não entra em 'misto'."),
    ("Regra 3, misto", "Dois temas com peso equivalente: classe do tema que abre, segunda classe em 'misto'.",
     "Só em empate real, depois do teste do título. Com 'misto', confiança 1 ou 2."),
    ("Regra 4, RES", "'Ação de governo em geral, sem política setorial: balanços, compromissos genéricos…'",
     "Balanço, crítica, compromisso ou opinião SOBRE UMA ÁREA pertence à área; ação operacional (operação, comissão, obra) conta como a área que serve. RES só quando nenhuma das nove áreas aparece."),
    ("Regra 5, tema fora do esquema", "Lista incluía 'comunicações', lida como tecnologia e IA.",
     "'Comunicações' vira 'radiodifusão e telecomunicações como setor'. Tecnologia, governo digital e IA vão para a área em que são aplicadas (Regra 2)."),
    ("Regra 6, NC", "'Fragmento ilegível, sequência de números, trecho editorial.'",
     "Critério único: sobra tema, classifica. Ignore cabeçalho misturado e início truncado. Título ou legenda com área identificável recebe a classe, confiança 1 e 'título' ou 'legenda' em observações. NC só sem tema reconhecível."),
    ("Regra 7, só o texto", "'Não use conhecimento sobre o capítulo nem sobre o ano.'",
     "Conhecer os termos (LOA, SUS, Pronaf) é vocabulário e vale. Não use suposições sobre capítulo ou ano; não consulte internet, o artigo ou outras fontes durante a anotação. Termo desconhecido: observação 'termo desconhecido: X' e confiança menor."),
    ("Aba Categorias, fronteiras", "Fronteiras genéricas.",
     "Novas fronteiras: benefício em dinheiro é SOC e assistência ou medicamento é SAU; fila do INSS é SOC; startups e inovação é EDU; GOV restrito a organização do Estado, integridade e gestão fiscal; energia é AMB mesmo como obra; fundo de infraestrutura 'sustentável' é INF; insumos e assistência técnica rural é AGR."),
    ("Registro de sessões", "Ficou em branco no piloto.", "Preencher a cada sessão (data, início, fim, itens anotados), no fim desta aba."),
    ("Observações", "Opcional.", "Em dúvida entre duas classes, uma linha com as duas candidatas. Dúvida de regra: anotar e seguir."),
    ("Obras (v1.1, após o segundo piloto)", "A definição de INF dizia 'obras públicas' sem distinguir o que a obra serve.",
     "Obra de equipamento setorial vai para a área servida: UBS e hospital (SAU), escola (EDU), unidade do SUAS (SOC). Obra de transporte, saneamento e mobilidade é INF; de energia é AMB. É a Regra 2 aplicada a obras."),
]
COMO_USAR = [
    "Preencha apenas as colunas em amarelo (classe, confiança, misto, subtipo, observações). Não altere id_item nem texto.",
    "Uma classe por parágrafo, escolhida na lista suspensa. 'confianca': 1 baixa, 2 média, 3 alta.",
    "'misto': só em empate real entre dois temas, depois de aplicar a Regra 1 (Regra 3): a classe vai para o tema que abre o parágrafo e a segunda classe vai em 'misto'. 'subtipo': só para RES (geral ou tema fora do esquema) e NC (fragmento, editorial, outro).",
    "Trabalhe na ordem das linhas (já está aleatória). Sessões de no máximo 90 minutos. Preencha o registro de sessões no fim desta aba a cada sessão (data, início, fim, itens anotados): ele documenta o esforço de anotação no artigo.",
    "Não consulte o outro anotador, o artigo, a internet ou qualquer lista de termos durante a anotação; o que você já sabe sobre os termos vale (Regra 7). Dúvida de regra: anote em 'observacoes' e siga. Dúvida entre duas classes: uma linha em 'observacoes' com as duas candidatas.",
    "Ao terminar, salve com o seu nome no arquivo e devolva. O gabarito só é cruzado depois que as duas planilhas estiverem fechadas.",
]

AMARELO = PatternFill("solid", fgColor="FFF2CC")
CINZA = PatternFill("solid", fgColor="EDEDED")
FINO = Side(style="thin", color="BFBFBF")
BORDA = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)
FONTE = "Arial"


def aba_instrucoes(wb, nome_amostra, n):
    ws = wb.active
    ws.title = "Instruções"
    ws["A1"] = f"Conjunto-ouro RITA V3 · {nome_amostra} ({n} parágrafos)"
    ws["A1"].font = Font(name=FONTE, bold=True, size=14)
    ws["A2"] = f"Instrumento {VERSAO}."
    ws["A2"].font = Font(name=FONTE, italic=True, color="595959"); ws.merge_cells("A2:C2")
    ws["A3"] = "O que mudou nesta versão, em relação às planilhas do piloto (decidido na reunião de calibração de 22/10)"
    ws["A3"].font = Font(name=FONTE, bold=True, size=12)
    r = 4
    for j, h in enumerate(["Ponto", "Como era no piloto", "Como fica agora"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    for ponto, antes, agora in MUDANCAS:
        for j, v in enumerate((ponto, antes, agora), 1):
            c = ws.cell(row=r, column=j, value=v); c.border = BORDA
            c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = Font(name=FONTE, bold=(j == 1))
            if j == 3: c.fill = PatternFill("solid", fgColor="E2F0D9")
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Regras de decisão (aplique na ordem: 1, 2 e só então 3)").font = Font(name=FONTE, bold=True, size=12)
    r += 1
    for j, h in enumerate(["Regra", "O que diz", "Exemplo (ilustrativo; não é item da amostra)"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    for nome, texto, exemplo in REGRAS:
        for j, v in enumerate((nome, texto, exemplo), 1):
            c = ws.cell(row=r, column=j, value=v); c.border = BORDA
            c.alignment = Alignment(wrap_text=True, vertical="top"); c.font = Font(name=FONTE, bold=(j == 1))
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Como usar a planilha").font = Font(name=FONTE, bold=True, size=12); r += 1
    for t in COMO_USAR:
        ws.cell(row=r, column=1, value="• " + t).alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3); r += 1
    r += 1
    ws.cell(row=r, column=1, value="O que cada coluna significa").font = Font(name=FONTE, bold=True, size=12); r += 1
    for j, h in enumerate(["Coluna", "Quem preenche", "Significado e valores admitidos"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    for col, quem, desc in COLUNAS:
        for j, v in enumerate((col, quem, desc), 1):
            c = ws.cell(row=r, column=j, value=v); c.border = BORDA
            c.alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Códigos (definições completas na aba Categorias)").font = Font(name=FONTE, bold=True, size=12); r += 1
    for cod, nome in CLASSES:
        ws.cell(row=r, column=1, value=cod).font = Font(name=FONTE, bold=True); ws.cell(row=r, column=2, value=nome); r += 1
    r += 1
    ws.cell(row=r, column=1, value="Exemplo de preenchimento (ilustrativo, não é item da amostra)").font = Font(name=FONTE, bold=True, size=12); r += 1
    cab = ["id_item", "texto", "classe", "confianca", "misto", "subtipo", "observacoes"]
    for j, h in enumerate(cab, 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    r += 1
    ex = ["EX0001", "O Plano Safra destinou R$ 400 bilhões ao crédito rural, com juros reduzidos para a agricultura familiar e ampliação do seguro rural.",
          "AGR", 3, "", "", "fala de crédito e juros, mas o assunto é política agrícola (Regra 1)"]
    for j, v in enumerate(ex, 1):
        c = ws.cell(row=r, column=j, value=v); c.border = BORDA; c.alignment = Alignment(wrap_text=True, vertical="top")
    r += 2
    ws.cell(row=r, column=1, value="Registro de sessões").font = Font(name=FONTE, bold=True, size=12); r += 1
    for j, h in enumerate(["Data", "Início", "Fim", "Itens anotados", "Observações"], 1):
        c = ws.cell(row=r, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for k in range(1, 9):
        for j in range(1, 6):
            c = ws.cell(row=r + k, column=j); c.fill = AMARELO; c.border = BORDA
    ws.column_dimensions["A"].width = 24; ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 80
    for col in "DEFG": ws.column_dimensions[col].width = 14
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and not c.font.bold: c.font = Font(name=FONTE)
    return ws


def aba_categorias(wb):
    ws = wb.create_sheet("Categorias")
    ws["A1"] = "As nove classes, o resíduo e o não classificável"
    ws["A1"].font = Font(name=FONTE, bold=True, size=14)
    ws["A2"] = ("Julgue o assunto do parágrafo, e não a presença de palavras. 'Trata de' define a classe; 'Inclui' dá exemplos típicos. "
                "'Fronteiras' lista os casos limítrofes: assuntos que parecem desta classe mas pertencem a outra, com o código da classe "
                "correta entre parênteses. Exemplo: em ECO, 'crédito rural (AGR)' significa que um parágrafo sobre crédito rural vai para AGR, "
                "mesmo falando de crédito. Em caso de dúvida entre duas classes, aplique as Regras 1 a 3 da aba Instruções.")
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top"); ws["A2"].font = Font(name=FONTE)
    ws.merge_cells("A2:E2"); ws.row_dimensions[2].height = 64
    cab = ["Código", "Classe", "Trata de", "Inclui", "Fronteiras: parece esta classe, mas vai para (código)"]
    for j, h in enumerate(cab, 1):
        c = ws.cell(row=4, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
    for i, linha in enumerate(DEFINICOES, start=5):
        for j, v in enumerate(linha, 1):
            c = ws.cell(row=i, column=j, value=v); c.border = BORDA; c.font = Font(name=FONTE, bold=(j == 1))
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for col, w in zip("ABCDE", (9, 26, 55, 55, 55)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"
    return ws


def aba_anotacao(wb, df):
    ws = wb.create_sheet("Anotação")
    cab = ["id_item", "texto", "classe", "confianca", "misto", "subtipo", "observacoes"]
    for j, h in enumerate(cab, 1):
        c = ws.cell(row=1, column=j, value=h); c.font = Font(name=FONTE, bold=True); c.fill = CINZA; c.border = BORDA
        c.alignment = Alignment(vertical="center")
    DICAS = ["", "leia só este texto", "um código (lista): ECO SOC SAU EDU AGR EXT INF AMB GOV RES NC",
             "3 alta · 2 média · 1 baixa", "só em empate real entre dois temas (Regra 3): a 2ª classe",
             "só RES (geral / tema fora do esquema) e NC (fragmento / editorial / outro)", "dúvida, regra aplicada, discordância (uma linha)"]
    for j, d in enumerate(DICAS, 1):
        c = ws.cell(row=2, column=j, value=d); c.font = Font(name=FONTE, italic=True, size=9, color="595959")
        c.fill = CINZA; c.border = BORDA; c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[2].height = 30
    for i, (_, row) in enumerate(df.iterrows(), start=3):
        ws.cell(row=i, column=1, value=row["id_item"])
        ws.cell(row=i, column=2, value=row["texto"])
        for j in range(1, 8):
            c = ws.cell(row=i, column=j); c.border = BORDA; c.font = Font(name=FONTE)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if j >= 3: c.fill = AMARELO
    n = len(df)
    ult = n + 2
    dv_classe = DataValidation(type="list", formula1='"' + ",".join(c for c, _ in CLASSES) + '"', allow_blank=True,
                               showErrorMessage=True, errorTitle="Código inválido", error="Escolha um código da lista.")
    dv_conf = DataValidation(type="list", formula1='"1,2,3"', allow_blank=True, showErrorMessage=True,
                             errorTitle="Valor inválido", error="Use 1, 2 ou 3.")
    dv_misto = DataValidation(type="list", formula1='"' + ",".join(c for c, _ in CLASSES[:9]) + '"', allow_blank=True)
    dv_sub = DataValidation(type="list", formula1='"' + ",".join(SUBTIPOS) + '"', allow_blank=True, showErrorMessage=False)
    for dv, col in ((dv_classe, "C"), (dv_conf, "D"), (dv_misto, "E"), (dv_sub, "F")):
        dv.add(f"{col}3:{col}{ult}"); ws.add_data_validation(dv)
    # progresso
    ws.cell(row=ult + 2, column=1, value="Anotados:").font = Font(name=FONTE, bold=True)
    ws.cell(row=ult + 2, column=2, value=f'=COUNTA(C3:C{ult})&" de {n}"').font = Font(name=FONTE)
    ws.column_dimensions["A"].width = 10; ws.column_dimensions["B"].width = 90
    ws.column_dimensions["C"].width = 9; ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 8; ws.column_dimensions["F"].width = 16; ws.column_dimensions["G"].width = 40
    ws.freeze_panes = "C3"
    ws.auto_filter.ref = f"A2:G{ult}"
    return ws


def gerar(csv_path, saida, nome_amostra, nome_arquivo):
    df = pd.read_csv(csv_path)
    for anot in (1, 2):
        wb = Workbook()
        aba_instrucoes(wb, nome_amostra, len(df))
        aba_categorias(wb)
        aba_anotacao(wb, df)
        dest = os.path.join(saida, f"{nome_arquivo}_anotador{anot}.xlsx")
        wb.save(dest); print("✓", dest)


AMOSTRAS = {  # nome do csv (sem _anotador.csv) -> rótulo no cabeçalho
    "piloto": "Rodada piloto",
    "piloto2": "Segundo piloto (confirmação da calibração)",
    "principal": "Amostra principal",
    "desempate": "Terceiro voto cego: desacordos da amostra principal",
}

if __name__ == "__main__":
    # Uso: gerar_planilhas_anotacao.py <pasta_da_amostra> <pasta_de_saida> [nome ...]
    # Sem nomes, gera todas as amostras cujo csv existir na pasta.
    pasta, saida = sys.argv[1], sys.argv[2]
    nomes = sys.argv[3:] or list(AMOSTRAS)
    os.makedirs(saida, exist_ok=True)
    for nome in nomes:
        csv = os.path.join(pasta, f"{nome}_anotador.csv")
        if os.path.exists(csv):
            gerar(csv, saida, AMOSTRAS.get(nome, nome), nome)
