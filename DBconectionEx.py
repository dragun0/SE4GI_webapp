# -*- coding: utf-8 -*-
"""
Created on Tue May 4 20:17:14 2021

@author: daene
"""

# import packages
import requests
import json
import pandas as pd
import geopandas as gpd
import numpy as np
from scipy import stats
from sqlalchemy import create_engine

# Function 'Update_LAGOS_DB' loads the raw data from the Epicollect 5 API 
# corresponding project, organizes, process it and cleans it to send it to the
# local server database management system postgreSQL

def Update_LAGOS_DB():
    # ------------------------- REQUEST FOR EPICOLLECT5 DATA -----------------------
    # send the request for the ALPhA Dataset
    response = requests.get('https://five.epicollect.net/api/export/entries/lagos-alpha-study-on-public-space-exercise?per_page=200')
    # store the raw text of the response in a variable
    r_data = response.text
    # parse the raw text response 
    data = json.loads(r_data)
    # from JSON to Pandas DataFrame
    whole_df = pd.json_normalize(data['data']['entries'])
    
    # ------------------------- DATA MANIPULATION AND CLEANING -----------------------
    
    # reversing the row order, to make the var ID_EPC5 consistent with the first to last entries
    whole_df = whole_df.iloc[::-1]
    whole_df.insert(0,"ID_EPC5", np.arange(len(whole_df)))
    whole_df = whole_df.iloc[::-1]
    # extracting the last ID_EPC5 and upload time
    last_upload = [whole_df['ID_EPC5'][0],whole_df['uploaded_at'][0]]
    
    # establishing pre-established categories of the columns
    col_df = pd.read_csv(r'C:\Users\daene\Dropbox\POLIMI\Semestre 1\Software Engineering for Geoinformatics\Project\col_description.txt')
    # removing unuseful columns as defined in column dataframe col_df
    unuseful = list(col_df.loc[col_df['type'].isin(['unuseful'])].autoname)
    whole_df = whole_df.drop(unuseful, axis = 1)
    # updating dataframe col_df for assembling a dictionary of new names for columns
    col_df = col_df.dropna(subset=['name'])
    old_colnames = list(col_df['autoname'])
    new_colnames =list(col_df['name'])
    col_rename_dict = {i:j for i,j in zip(old_colnames,new_colnames)}
    # renaming the columns according to dictionary
    whole_df.rename(columns=col_rename_dict, inplace=True)
    
    # creating new columns with numeric coordinate and accuracy values
    whole_df['Latitude'] = pd.to_numeric(whole_df['7_5a1_Record_locatio.latitude'], errors='coerce')
    whole_df['Longitude'] = pd.to_numeric(whole_df['7_5a1_Record_locatio.longitude'], errors='coerce')
    whole_df['Accuracy'] = pd.to_numeric(whole_df['7_5a1_Record_locatio.accuracy'], errors='coerce')
    
    # removing the row data that doesn't have any location
    data_df = whole_df.dropna(subset=['Latitude','Longitude']).copy()
    data_df = data_df.drop(['7_5a1_Record_locatio.latitude','7_5a1_Record_locatio.longitude','7_5a1_Record_locatio.accuracy'], axis = 1)
    
    # outlier removal due to misconfiguration of user location (VPNs, mobile phone errors,etc.)
    data_df1 = data_df[(np.abs(stats.zscore(data_df[['Latitude','Longitude']])) < 3).all(axis=1)]
    data_df = data_df1[(np.abs(stats.zscore(data_df1[['Latitude','Longitude']])) < 3).all(axis=1)]
    
    # reversing the row order, to make the var ID consistent with the valid first to last entries
    data_df = data_df.iloc[::-1]
    data_df.insert(1,"ID", np.arange(len(data_df)))
    data_df = data_df.iloc[::-1]
    
    # from Pandas DataFrame to GeoPandas GeoDataFrame
    data_geodf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['Longitude'], data_df['Latitude']))
    
    
    # setup db connection (generic connection path to be update with your credentials: 
    # 'postgresql://user:password@localhost:5432/mydatabase')
    engine = create_engine('postgresql://postgres:kotxino35@localhost:5433/SE4GI')
    # data_df.to_sql('Lagos ALPhA Survey', engine, if_exists = 'replace', index=False)
    data_geodf.to_postgis('Lagos ALPhA Survey', engine, if_exists = 'replace', index=False)
    
    print('Lagos ALPhA Survey Updated to server. Last upload entry:', last_upload)
    return

def Load_gdf_LAGOS_DB():
    # ---------------------- REQUEST DATA IN SERVER SE4GI -----------------------
    engine = create_engine('postgresql://postgres:kotxino35@localhost:5433/SE4GI')
    # read the dataframe from a postgreSQL table
    # data_df = pd.read_sql_table('Lagos ALPhA Survey', engine)
    data_geodf = gpd.read_postgis('Lagos ALPhA Survey', engine, geom_col='geometry')
    return data_geodf

#data_df = Load_gdf_LAGOS_DB()
data_geodf = Load_gdf_LAGOS_DB()
