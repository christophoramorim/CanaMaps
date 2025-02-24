from api import fazerRequisicao
from fazenda import *
from config import *
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def gerarDatas(inicio: str, fim: str):
    data_inicio = datetime.strptime(inicio, '%Y-%m-%d')
    data_fim = datetime.strptime(fim, '%Y-%m-%d')

    listaDatas = []
    while data_inicio <= data_fim:
        ultimo_dia_mes = data_inicio + pd.offsets.MonthEnd(0)
        listaDatas.append((
            data_inicio.strftime('%Y-%m-%dT00:01'), 
            ultimo_dia_mes.strftime('%Y-%m-%dT23:59')
        )) # transforma as data em string
        
        data_inicio = ultimo_dia_mes + timedelta(days=1) # pula para o proximo dia do mês

    return listaDatas

def obterArmadilha() -> pd.DataFrame:

    try:
        url = f"{"https://aprovale.com.br/api/externo/consulta/formularios-armadilhas"}?created_inicial={'23-01-01T00:01'}" #&created_final={data_fim}
        resposta = fazerRequisicao(url)
        if resposta and 'result' in resposta and resposta['result']:
            #Normaliza a resposta em JSON transformando em um dataFrame
            dfTemp = pd.json_normalize(resposta['result'], 
                    "formularios_armadilhas_dados",  # Esta é a chave com a lista de dicionários
                    ["propriedade_id", "observacoes", "usuario_id"],  # Colunas extras a serem mantidas
                    errors='ignore', # Ignora erros caso algum campo não exista
                    meta_prefix='result_' # é o prefixo que irá adicionar nas colunas de nivel superior
                    )  
            #Removendo as colunas desnecessarias
            dfTemp = dfTemp.drop(
                columns=['variedade_id', 'area', 'talhao', 'variedade', "broca_bainha", "canas_coletadas", "data_sincronizacao", "modified", "id_local"], 
                errors='ignore' # este erros é para não quebrar o codigo caso alguma coluna não exista no dataframe
                )

            #Renomeando as Colunas
            dfTemp = dfTemp.rename(columns={
                'id': 'ID_FORM',
                "formularios_armadilha_id": 'ID',
                'propriedade_talhao_id': 'ID_TALHAO',
                "armadilha": "ARMADILHA",
                "maripoza": 'MARIPOZA',
                'status': 'STT',
                'created': 'DATA',
                'latitude': 'LAT',
                'longitude': 'LONG',
                'result_propriedade_id': 'ID_FA',
                'result_observacoes': 'OBSERVACAO',
                'result_usuario_id': 'ID_USUARIO'
            })

            #convertendo as colunas para o tipo correto
            dfTemp['DATA'] = pd.to_datetime(dfTemp['DATA'], errors="coerce")
            dfTemp['DATA'] = dfTemp['DATA'].dt.tz_localize(None)
            dfTemp['DATA'] = dfTemp['DATA'].dt.normalize()

            return dfTemp
        else:
            print(f'Resposta inválida ou sem resultado')
            return pd.DataFrame() #retorna um dataframe vazio

    except Exception as e:
        print(f"Erro ao fazer requisição ou processar dados: {e}")
        return pd.DataFrame() #retorna um dataframe vazio

def obterBrocaMaior() -> pd.DataFrame:

    try:
        url = f"{"https://aprovale.com.br/api/externo/consulta/formularios-brocas"}?created_inicial={'23-01-01T00:01'}" #&created_final={data_fim}
        resposta = fazerRequisicao(url)
        if resposta and 'result' in resposta and resposta['result']:
            #Normaliza a resposta em JSON transformando em um dataFrame
            dfTemp = pd.json_normalize(resposta['result'], 
                    'formularios_brocas_unidades',  # Esta é a chave com a lista de dicionários
                    ["propriedade_id", "observacoes", "usuario_id"],  # Colunas extras a serem mantidas
                    errors='ignore', # Ignora erros caso algum campo não exista
                    meta_prefix='result_' # é o prefixo que irá adicionar nas colunas de nivel superior
                    )  
            #Removendo as colunas desnecessarias
            dfTemp = dfTemp.drop(
                columns=['variedade_id', 'area', 'talhao', 'variedade', "data_sincronizacao", "modified", "id_local"], 
                errors='ignore' # este erros é para não quebrar o codigo caso alguma coluna não exista no dataframe
                )

            #Renomeando as Colunas
            dfTemp = dfTemp.rename(columns={
                'id': 'ID_FORM',
                'formularios_brocas_id': 'ID',
                'propriedade_talhao_id': 'ID_TALHAO',
                'brocas_menor': 'BROCA_MENOR',
                'brocas_maior': 'BROCA_MAIOR',
                'crisada': 'CRISADA',
                'metros': 'METROS',
                'status': 'STT',
                'col_brocas_ha': 'BROCAS_HA',
                'created': 'DATA',
                'latitude': 'LAT',
                'longitude': 'LONG',
                'result_propriedade_id': 'ID_FA',
                'result_observacoes': 'OBSERVACAO',
                'result_usuario_id': 'ID_USUARIO'
            })

            #convertendo as colunas para o tipo correto
            dfTemp['DATA'] = pd.to_datetime(dfTemp['DATA'], errors="coerce")
            dfTemp['DATA'] = dfTemp['DATA'].dt.tz_localize(None)
            dfTemp['DATA'] = dfTemp['DATA'].dt.normalize()
            dfTemp['ID_TALHAO'] = pd.to_numeric(dfTemp['ID_TALHAO'], errors='coerce')
            dfTemp['ID_FA'] = pd.to_numeric(dfTemp['ID_FA'], errors='coerce')
            dfTemp['ID_USUARIO'] = pd.to_numeric(dfTemp['ID_USUARIO'], errors='coerce')

            return dfTemp
        else:
            print(f'Resposta inválida ou sem resultado')
            return pd.DataFrame() #retorna um dataframe vazio

    except Exception as e:
        print(f"Erro ao fazer requisição ou processar dados: {e}")
        return pd.DataFrame() #retorna um dataframe vazio

def obterBrocaBainha() -> pd.DataFrame:
    
    try:
        url = f'{"https://aprovale.com.br/api/externo/consulta/formularios-brocas-bainhas"}?created_inicial={'23-01-01T00:01'}' # &created_final={data_fim}
        resposta = fazerRequisicao(url)
        if resposta and 'result' in resposta and resposta['result']:
            #Normaliza a resposta em JSON transformando em um dataFrame
            dfTemp = pd.json_normalize(resposta['result'], 
                    "formularios_brocas_bainhas_dados",  # Esta é a chave com a lista de dicionários
                    ["propriedade_id", "observacoes", "usuario_id"],  # Colunas extras a serem mantidas
                    errors='ignore', # Ignora erros caso algum campo não exista
                    meta_prefix='result_' # é o prefixo que irá adicionar nas colunas de nivel superior
                    )  
            #Removendo as colunas desnecessarias
            dfTemp = dfTemp.drop(
                columns=['variedade_id', 'area', 'talhao', 'variedade', "data_sincronizacao", "modified", "id_local", "armadilha", "maripoza"], 
                errors='ignore' # este erros é para não quebrar o codigo caso alguma coluna não exista no dataframe
                )

            #Renomeando as Colunas
            dfTemp = dfTemp.rename(columns={
                'id': 'ID_FORM',
                "formularios_brocas_bainha_id": 'ID',
                'propriedade_talhao_id': 'ID_TALHAO',
                "broca_bainha": "BROCA_BAINHA",
                "canas_coletadas": "CANAS",
                'status': 'STT',
                'created': 'DATA',
                'latitude': 'LAT',
                'longitude': 'LONG',
                'result_propriedade_id': 'ID_FA',
                'result_observacoes': 'OBSERVACAO',
                'result_usuario_id': 'ID_USUARIO'
            })

            #convertendo as colunas para o tipo correto
            dfTemp['DATA'] = pd.to_datetime(dfTemp['DATA'], errors="coerce")
            dfTemp['DATA'] = dfTemp['DATA'].dt.tz_localize(None)
            dfTemp['DATA'] = dfTemp['DATA'].dt.normalize()

            return dfTemp
        else:
            print(f'Resposta inválida ou sem resultado')
            return pd.DataFrame() #retorna um dataframe vazio

    except Exception as e:
        print(f"Erro ao fazer requisição ou processar dados: {e}")
        return pd.DataFrame() #retorna um dataframe vazio

def broquinha() -> pd.DataFrame:
    
    dfArmadilha = obterArmadilha()
    dfBrocaMaior = obterBrocaMaior()
    dfBrocaBainha = obterBrocaBainha()

    dfArmadilha['FORMULARIO'] = 'ARMADILHA'
    dfBrocaMaior['FORMULARIO'] = 'BROCA MAIOR'
    dfBrocaBainha['FORMULARIO'] = 'BROCA BAINHA'

    dfArmadilha = dfArmadilha[['FORMULARIO', 'ID', 'ID_FORM','ID_TALHAO', 'ID_USUARIO', 'DATA', 'STT', 'MARIPOZA']].rename(columns={'MARIPOZA': 'INDICE'})
    dfBrocaMaior = dfBrocaMaior[['FORMULARIO', 'ID', 'ID_FORM', 'ID_TALHAO', 'ID_USUARIO', 'DATA', 'STT', 'BROCA_MAIOR']].rename(columns={'BROCA_MAIOR': 'INDICE'})
    dfBrocaBainha = dfBrocaBainha[['FORMULARIO', 'ID', 'ID_FORM', 'ID_TALHAO', 'ID_USUARIO', 'DATA', 'STT', 'BROCA_BAINHA']].rename(columns={'BROCA_BAINHA': 'INDICE'})

    dfFinal = pd.concat([dfArmadilha, dfBrocaMaior, dfBrocaBainha], ignore_index=True)
    dfFinal['INDICE'] = pd.to_numeric(dfFinal['INDICE'], errors='coerce')
    dfFinal = dfFinal.sort_values('DATA', ascending=False)

    return dfFinal

def aplicacao() -> pd.DataFrame:
    resposta = fazerRequisicao("https://aprovale.com.br/api/externo/consulta/formularios-aplicacoes")
    if resposta and 'result' in resposta and resposta['result']:
        dfTemp = pd.DataFrame(resposta['result'])
        dfTemp = dfTemp.drop(columns=['proprietario_codigo', 'observacao', 'data_sincronizacao', 'data_criacao'], axis=1)
        dfTemp.columns = ['ID', 'ID_FORN', 'FORNECEDOR', 'ID_FA', 'COD_FA', 'FAZENDA', 'ID_OPER', 'OPERACAO', 'DATA', 'ID_USUARIO', 
                          'USUARIO', 'STT', 'ID_TALHAO', 'TALHAO', 'AREA', 'ID_PRODUTO', 'PRODUTO', 'DOSE']
        #convertendo as colunas para o tipo correto
        dfTemp['DATA'] = pd.to_datetime(dfTemp['DATA'], errors="coerce")
        dfTemp['DATA'] = dfTemp['DATA'].dt.tz_localize(None)
        dfTemp['DATA'] = dfTemp['DATA'].dt.normalize()
        dfTemp = dfTemp.astype({"ID_PRODUTO": 'int64', "ID_TALHAO": 'int64'})
    return dfTemp

def monitoramento() -> pd.DataFrame:

    # Baixando os dataFrame que irão ser utilizados
    dfFazenda = carregarFazenda()
    dfTemp = pd.read_excel('data/monitoramento.xlsx', sheet_name='BROQUINHA')
    dfResponsavel = pd.read_excel('data/monitoramento.xlsx', sheet_name='RESPONSAVEL')
    dfResidual = pd.read_excel('data/monitoramento.xlsx', sheet_name='RESIDUAL')
    dfBroquinha = broquinha()
    dfAplicacao = aplicacao()

    # Criando a colunas que irá servir de chave explicita para corresponder com a camada do mapa
    dfTemp['CODIGO'] = dfTemp['CD_FA'].astype(str) + '-' + dfTemp['TALHAO'].astype(str)


    # Realizando os MERGES
    dfFazenda = dfFazenda.sort_values(by=['CD_FA', 'TALHAO', 'SAFRA'])
    dfFazenda['ID_ANO_ANTERIOR'] = dfFazenda.groupby(['CD_FA', 'TALHAO'])['ID_TALHAO'].shift(1)

    dfTemp = pd.merge(
        dfTemp, 
        dfFazenda[['CD_FA', 'TALHAO', 'SAFRA', 'ID_TALHAO', 'ID_ANO_ANTERIOR', 'FAZENDA', 'FORNECEDOR', 'USINA', 'AREA', 'VARIEDADE', 'DT_PLANTIO']],
        on=['CD_FA', 'TALHAO', 'SAFRA'],
        how='left'
    )
    
    dfTemp = dfTemp.merge(
        dfResponsavel,
        on=['SAFRA', 'CD_FA'],
        how='left'
    )

    # trazer a data da ultima colheita
    dfTemp['DT_COLHEITA'] = dfTemp['ID_ANO_ANTERIOR'].map(dfFazenda.set_index('ID_TALHAO')['DT_FINALIZADO'].to_dict())

    # Trazer os ultimos levantamentos de broquinha
    dfBroquinha = pd.merge(
        dfBroquinha,
        dfTemp[['ID_TALHAO', 'BLOCO']],
        on=['ID_TALHAO'],
        how='left'
    )
    ultimo_levantamento = dfBroquinha.groupby('BLOCO').agg(
        FORMULARIO=('FORMULARIO', 'first'),
        DT_LEVANTAMENTO=('DATA', 'first'),
        INDICE=('INDICE', 'first')
    ).reset_index()

    dfTemp = dfTemp.merge(
        ultimo_levantamento,
        on=['BLOCO'],
        how='left'
    )
    
    # Acrescentando Se deu indice ou não
    def calcular_indice(row):
        if pd.isna(row['INDICE']) or row['INDICE'] == "":
            return ""
        elif row['FORMULARIO'] == "ARMADILHA":
            return 'NAO' if row['INDICE'] < 10 else 'SIM'
        else:
            return 'NAO' if row['INDICE'] < 3 else 'SIM'
        
    dfTemp['B_INDICE'] = dfTemp.apply(calcular_indice, axis=1)

    # Acrescentando a coluna de Data de Aplicação e o Produto
    dfAplicacao = dfAplicacao[['ID', 'DATA', 'PRODUTO', 'ID_TALHAO']]
    dfAplicacao = dfAplicacao.merge(dfResidual, on='PRODUTO', how='left') # trazendo as colunas do Resiual
    dfAplicacao = dfAplicacao[dfAplicacao['PRAGA'].notnull()] # filtrando os produtos que são para infestação de Broca e Cigarrinha
    dfAplicacao = dfAplicacao.merge(dfTemp[['ID_TALHAO', 'BLOCO']], on='ID_TALHAO',how='left') # trazendo a coluna bloco para aplicação
    # no caso a baixo estou trazendo o Rotulo (index) da data mais recente do agrupamento (BLOCO, PRAGA), e depois faço o faciamento a nivel de linha com LOC
    dfAplicacao = dfAplicacao.loc[dfAplicacao.groupby(['BLOCO', 'PRAGA'])['DATA'].idxmax()]
    # realizando o filtro que quero apenas as aplicação de BROQUINHA e realizo o merge trazendo as colunas desejadas.
    dfTemp = dfTemp.merge(dfAplicacao[dfAplicacao['PRAGA'] == 'BROQUINHA'][['BLOCO', 'DATA', 'PRODUTO', 'RESIDUAL']].rename(columns={'DATA': 'DT_APLICACAO'}), on='BLOCO', how='left')

    # Definir a data de hoje uma vez
    hoje = pd.to_datetime('today')
    def classificador_broquinha(row):
        dt_levant = pd.to_datetime(row['DT_LEVANTAMENTO'], errors='coerce')
        diasColheita = (hoje - row['DT_COLHEITA']).days if pd.notna(row['DT_COLHEITA']) else None
        diasLevantamento = (hoje - row['DT_LEVANTAMENTO']).days if pd.notna(row['DT_LEVANTAMENTO']) else None
        dtResidual = row['DT_APLICACAO'] + pd.Timedelta(row['RESIDUAL'], unit='day') if pd.notna(row['DT_APLICACAO']) else None

        # Condições para o classificador
        if pd.isna(row[['DT_COLHEITA', 'DT_LEVANTAMENTO', 'DT_APLICACAO']]).all(): return "BRANCO"
        elif diasColheita is not None and diasColheita < 90 and pd.isna(row[['DT_LEVANTAMENTO', 'DT_APLICACAO']]).all(): return "CINZA"
        elif (diasLevantamento is not None) and ((dtResidual is not None and dt_levant > dtResidual) or pd.isna(dtResidual)) and (diasLevantamento <= 15 and row['B_INDICE'] == "NAO"): return "AZUL"
        elif (diasLevantamento is not None) and ((dtResidual is not None and dt_levant > dtResidual) or pd.isna(dtResidual)) and (diasLevantamento <= 7 and row['B_INDICE'] == "SIM"): return "AMARELO"
        elif dtResidual is not None and row['DT_LEVANTAMENTO'] < dtResidual and dtResidual >= hoje: return "VERDE"
        else: return "VERMELHO"

    dfTemp['CLASSE'] = dfTemp.apply(classificador_broquinha, axis=1)

    return dfTemp
