from api import fazerRequisicao
from config import *
import pandas as pd

def carregarPropriedade() -> pd.DataFrame:
    
    dfPropriedade = pd.DataFrame(fazerRequisicao(URL_FAZENDA)['result'])
    dfPropriedade['id_fornecedor'] = dfPropriedade['proprietarios'].apply(lambda x: x[0]['id'] if x else None)
    dfPropriedade['fornecedor'] = dfPropriedade['proprietarios'].apply(lambda x: x[0]['nome'] if x else None)
    dfPropriedade['usina'] = dfPropriedade['usinas'].apply(lambda x: x[0]['nome'] if x else None)
    dfPropriedade = dfPropriedade.drop(['data_sincronizacao', 'created', 'modified', 'id_local', 'usinas', 'proprietarios'], axis=1)
    dfPropriedade.columns = ['ID_FA', 'FAZENDA', 'STT_FA', 'CD_FA', 'CIDADE', 'UF', 'KM', 'CODIGO_NOME', 'ID_FORN', 'FORNECEDOR', 'USINA']
    dfPropriedade = dfPropriedade[['ID_FA', 'CD_FA', 'FAZENDA', 'ID_FORN', 'FORNECEDOR', 'USINA', 'STT_FA', 'CIDADE', 'UF', 'KM', 'CODIGO_NOME']]
    dfPropriedade['CD_FA'] = dfPropriedade['CD_FA'].astype('int64')

    return dfPropriedade

def carregarSafra() -> pd.DataFrame:

    dfSafra = pd.DataFrame(fazerRequisicao(URL_SAFRA)['result'])
    dfSafra = dfSafra[['id', 'nome']].astype('int64')
    dfSafra.columns = ['ID_SAFRA', 'SAFRA']

    return dfSafra

def carregarEtapa() -> pd.DataFrame:

    dfEtapa = pd.DataFrame(fazerRequisicao(URL_ETAPA)['result'])
    dfEtapa = dfEtapa.drop(['propriedade_id', 'propriedade_producao_id', 'created', 'modified'], axis=1)
    #convertendo as colunas para o tipo correto
    dfEtapa['data_finalizado'] = pd.to_datetime(dfEtapa['data_finalizado'], errors="coerce")
    dfEtapa['data_finalizado'] = dfEtapa['data_finalizado'].dt.tz_localize(None)
    dfEtapa['data_finalizado'] = dfEtapa['data_finalizado'].dt.normalize()
    dfEtapa =  dfEtapa.drop(['status'], axis=1)
    dfEtapa.columns = ['ID_ETAPA', 'ETAPA', 'ATR', 'TON_REAL', 'AREA_COLHEITA', 'FINALIZADO', 'DT_FINALIZADO']
    dfEtapa = dfEtapa[['ID_ETAPA', 'ETAPA', 'AREA_COLHEITA', 'TON_REAL', 'ATR', 'FINALIZADO', 'DT_FINALIZADO']]

    return dfEtapa

def carregarTalhao() -> pd.DataFrame:

    dfTalhao = pd.DataFrame(fazerRequisicao(URL_TALHAO)['result'])
    dfTalhao = dfTalhao[dfTalhao['safra_id'] >= 6]
    dfTalhao['id_variedade'] = dfTalhao['variedades'].apply(lambda x: x[0]['id'] if x else None) # Pegando o campo de nome variedade
    dfTalhao['variedade'] = dfTalhao['variedades'].apply(lambda x: x[0]['nome'] if x else None)
    dfTalhao = dfTalhao.drop(['id_local', 'talhao_origem_id', 'created', 'modified', 'variedades'], axis=1) # excluindo as colunas indesejadas
    dfTalhao.fillna(value=0.0)   # substituindo NaN por vazio
    #convertendo as colunas para o tipo correto
    dfTalhao['data_plantio'] = pd.to_datetime(dfTalhao['data_plantio'], errors="coerce")
    dfTalhao['data_plantio'] = dfTalhao['data_plantio'].dt.tz_localize(None)
    dfTalhao['data_plantio'] = dfTalhao['data_plantio'].dt.normalize()

    nmColuna = [
        'ID_TALHAO', 'ID_FA', 'ID_SAFRA', 'TALHAO', 
        'AREA', 'AREA_MUDA', 'AREA_REFORMA', 'ID_ETAPA', 
        'ETAPA', 'STT_TALHAO', 'TCH_ESTIMADO', 'TON_ESTIM', 
        'AREA_BISADA', 'DT_PLANTIO', 'ID_VARIEDADE', 'VARIEDADE'
    ]
    dfTalhao.columns = nmColuna
    dfTalhao['TALHAO'] = pd.to_numeric(dfTalhao['TALHAO'], errors='coerce')

    return dfTalhao


def carregarFazenda() -> pd.DataFrame:
    dfFazenda = carregarTalhao()
    dfPropriedade = carregarPropriedade()
    dfSafra = carregarSafra()
    dfEtapa = carregarEtapa()

    dfFazenda = dfFazenda.merge(dfPropriedade, how='left', left_on='ID_FA', right_on='ID_FA')
    dfFazenda = dfFazenda.merge(dfSafra, how='left', left_on='ID_SAFRA', right_on='ID_SAFRA')
    dfFazenda = dfFazenda.merge(dfEtapa, how='left', left_on='ID_ETAPA', right_on='ID_ETAPA')
    

    return dfFazenda