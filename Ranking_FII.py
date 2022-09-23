#Ranking_FII #10/07/22 -- GOMES^2
#----------------------------------------------------------------------------------------------------------
# GAME PLAN
# FII´s with P/VPA between 0.8% and 1%
# Have liquidity bigger then 10000 per day
# Found rentable yields//around 1% per month(mean)
# Found FII´s with variable assets//safety

#----------------------------------------------------------------------------------------------------------
# import the libraries
from statistics import mean
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def main():
    url_1 = "https://www.fundsexplorer.com.br/ranking"
    path_1 = "//*[@id='table-ranking']"
    columns_1 = ['Código do fundo', 'Setor', 'Preço Atual', 'P/VPA', 'Liquidez Diária', 'Dividendo', 'Dividend Yield', 'DY (12M) Média', 'Vacância Física', 'Quantidade Ativos']
    new_columns_1 = ['CÓDIGO', 'SETOR', 'PREÇO ATUAL', 'P/VPA', 'LIQUIDEZ', 'DIVIDENDO', 'DY(1)', 'DY(12)', 'VACÂNCIA', 'ATIVOS']
    
    tabela_SITE_1 = webscrapping(url_1, path_1)
    tabela_original = read_HTML(tabela_SITE_1, columns_1, new_columns_1)
    tabela_modificada, mean_sector = optmizer_the_DATA(tabela_original, new_columns_1)
    
    # //input the sector and gives the data_sector//
    for i in range(9):
        print(tabela_modificada['SETOR'].unique())
        sector = input()
        
        if sector == 'quit':
            break
        if sector == 'assets':
            for x in input("Enter the code: ").split(','):
                print(tabela_original.loc[tabela_original['CÓDIGO']==x])
            break
        
        data_sector = filter_per_sector(tabela_modificada, sector, mean_sector)
        print("DY(12) mean is %s%%" % round(mean_sector.loc[sector, ('DY(12)', 'mean')], 2))
        print(data_sector)
        
        create_files(data_sector)
        
#-----------------------------------------------------------------------------------------------------------
# Web Scrapping
def webscrapping(url, path):
    
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    driver.get(url)
    element = driver.find_element("xpath", path)
    html_content = element.get_attribute('outerHTML')
    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find(name='table')
    return table

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
# Read the HTML
def read_HTML(table, columns, new_columns):
    df_full = pd.read_html( str(table) )[0]
    df = df_full[columns]
    df.columns = new_columns
    return df

#---------------------------------------------------------------------------------------------------------------------------------------------------
# Optimizer the HTML
def optmizer_the_DATA(df, new_columns):
    df[new_columns] = df[new_columns].fillna(0) # change the NaN to 0

    # prepare the data
    col_floats = list(df.iloc[:,3:].columns)
    df[col_floats] = df[col_floats].applymap(lambda x: str(x).replace('R$', ' ').replace(',', '.').replace('%', ' '))
    df[col_floats] = df[col_floats].astype('float')
    df['P/VPA'] = df['P/VPA']/100
    
    # take the mean of each sector
    df_study = df[['SETOR', 'P/VPA', 'LIQUIDEZ', 'DIVIDENDO', 'DY(1)', 'DY(12)']] 
    mean_sector = df_study.groupby('SETOR').agg(['mean'])
    
    return df, mean_sector

# -----------------------------------------------------------------------------------------------------
# filter the data per sector
def filter_per_sector(df, sector, mean_sector, label_sector = 'SETOR'):
    # create a new data
    df_sector = df[df[label_sector].isin([sector])] 
    
    # applying the filter in the data
    filter_ = \
        (df_sector['P/VPA'].between(0.80, 1.00, inclusive = 'both')) &\
        (df_sector['LIQUIDEZ'] > 10000) &\
        (df_sector['DY(12)'] > 1.2 * mean_sector.loc[sector, ('DY(12)', 'mean')]) 
    
    return df_sector[filter_]  
    
#-------------------------------------------------------------------------------------------------------
#Create the files
def create_files(data):
    data.to_csv('Ranking_FII.csv')
    
    analizar = {}
    analizar['Ranking'] = data.to_dict('records')

    js = json.dumps(analizar)
    fp = open('Ranking_FII.json', 'w')
    fp.write(js)
    fp.close()
                  
main()

