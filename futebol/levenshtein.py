from fuzzywuzzy import fuzz
import pandas as pd

# Função para calcular a similaridade entre duas strings
def calcular_similaridade(string1, string2):
    return fuzz.ratio(string1.lower(), string2.lower())

# Função para juntar os DataFrames com base na similaridade entre as colunas name1 e name2
def juntar_por_similaridade(df1, df2, limiar_similaridade):
    resultados = []
    
    # Iterar sobre as linhas do primeiro DataFrame
    for index1, row1 in df1.iterrows():
        # Iterar sobre as linhas do segundo DataFrame
        for index2, row2 in df2.iterrows():
            # Calcular a similaridade entre os valores das colunas name1 e name2
            similaridade_name1 = calcular_similaridade(row1['name1'], row2['name2'])
            similaridade_name2 = calcular_similaridade(row1['name2'], row2['name1'])
            
            # Verificar se a similaridade atende ao limiar
            if similaridade_name1 >= limiar_similaridade or similaridade_name2 >= limiar_similaridade:
                # Juntar as linhas dos dois DataFrames
                resultado = {
                    'name1_df1': row1['name1'],
                    'name2_df1': row1['name2'],
                    'name1_df2': row2['name1'],
                    'name2_df2': row2['name2'],
                    'odd1_df1': row1['odd1'],
                    'odd2_df1': row1['odd2'],
                    'odd3_df1': row1['odd3'],
                    'odd1_df2': row2['odd1'],
                    'odd2_df2': row2['odd2'],
                    'odd3_df2': row2['odd3']
                }
                resultados.append(resultado)
    
    # Criar um DataFrame com os resultados
    df_resultado = pd.DataFrame(resultados)
    return df_resultado

# Exemplo de DataFrames de entrada
df1 = pd.DataFrame({
    'name1': ['Atletico Mineiro', 'Atletico Goianiense', 'Flamengo'],
    'name2': ['Fluminense', 'Botafogo', 'Santos'],
    'odd1': [2.0, 1.8, 2.5],
    'odd2': [1.5, 2.0, 1.6],
    'odd3': [1.2, 1.4, 2.0]
})

df2 = pd.DataFrame({
    'name1': ['Atletico MG', 'Atletico GO', 'Flamengo'],
    'name2': ['Fluminense', 'Botafogo', 'Santos'],
    'odd1': [1.9, 1.7, 2.3],
    'odd2': [1.4, 2.1, 1.8],
    'odd3': [1.1, 1.3, 1.9]
})

# Definir o limiar de similaridade
limiar_similaridade = 40

# Juntar os DataFrames por similaridade
df_resultado = juntar_por_similaridade(df1, df2, limiar_similaridade)

# Exibir o DataFrame resultante
print(df_resultado)
