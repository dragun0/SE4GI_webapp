# -*- coding: utf-8 -*-
"""
Politecnico di Milano – Software Engineering for Geoinformatics 2021
WEB-BASED APPLICATION FOR THE VISUALISATION AND ANALYSIS OF THE ALPHA 
CITIZEN SCIENCE STUDY IN LAGOS, NIGERIA
@authors: M. Abd Alslam Mohammed Elkhalifa, M. Abdalla Eldouma Mohamed, 
D. Aguirre, L. Dragun
"""
# ------------------------------ Synchronizer --------------------------------#
# The current script allows the retrieval of Epicollect 5 Lagos and Yaunde(EN) 
# ALPhA surveys defining the fucntions to update them into the local DB, and the
# ones needed to load the geodataframes stored in the local DB. Updating functions
# are executed when the script is run, loading functions are not executed, but are
# expected to be imported from the application script. This script is executed
# once prior the pilot test of the web application.
# ----------------------------------------------------------------------------#

# Needed libraries import
import requests
import json
import os
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
    col_df = pd.read_csv(os.path.abspath('./Database/col_description.txt'))
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
    data_gdf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df['Longitude'], data_df['Latitude']))
    # setting up the reference system for the geodesic coordinates in WGS84
    data_gdf= data_gdf.set_crs(epsg=4326, inplace=True)
    
    # ------------------------- EXPORTING DATA TO DBMS -----------------------
    # setup db connection (generic connection path to be update with your credentials: 
    DBfile = open('Database/dbConfig.txt')
    connection = DBfile.readline()
    engine = create_engine(connection)
    # data_df.to_sql('Lagos ALPhA Survey', engine, if_exists = 'replace', index=False)
    data_gdf.to_postgis('Lagos_ALPhA_Survey', engine, if_exists = 'replace', index=False)
    print('Lagos ALPhA Survey Updated to server. Last upload entry:', last_upload)
    # a back-up database is stored in a csv file
    data_df.to_csv('Database/LAGOS_DB.txt')
    return

# Function to load the database from PostgreSQL
def Load_gdf_LAGOS_DB():
    # ---------------------- REQUEST DATA FROM SERVER SE4GI -----------------------
    DBfile = open('Database/dbConfig.txt')
    connection = DBfile.readline()
    engine = create_engine(connection)
    # read the geodataframe from a postgreSQL table
    data_geodf = gpd.read_postgis('Lagos_ALPhA_Survey', engine, geom_col='geometry')
    return data_geodf

# Function 'Update_YAOUNDE_DB' loads the raw data from the Epicollect 5 API 
# corresponding project, organizes, process it and cleans it to send it to the
# local server database management system postgreSQL
def Update_YAOUNDE_DB():
    # ------------------------- REQUEST FOR EPICOLLECT5 DATA -----------------------
    # send the request for the ALPhA Dataset
    response = requests.get('https://five.epicollect.net/api/export/entries/yaounde-alpha-study-on-public-space-exercise?per_page=200')
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
    col_df = pd.read_csv(os.path.abspath('Database/col_descriptionY.txt'))
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
        
    # ------------------------- EXPORTING DATA TO DBMS -----------------------
    # setup db connection (generic connection path to be update with your credentials: 
    DBfile = open('Database/dbConfig.txt')
    connection = DBfile.readline()
    engine = create_engine(connection)
    # data_df.to_sql('Lagos ALPhA Survey', engine, if_exists = 'replace', index=False)
    data_geodf.to_postgis('Yaounde_ALPhA_Survey', engine, if_exists = 'replace', index=False)
    print('Yaoundé ALPhA Survey Updated to server. Last upload entry:', last_upload)
    # a back-up database is stored in a csv file
    data_df.to_csv('Database/YAOUNDE_DB.txt')
    return

# Function to load the database from PostgreSQL
def Load_gdf_YAOUNDE_DB():
    # ---------------------- REQUEST DATA FROM SERVER SE4GI -----------------------
    DBfile = open('Database/dbConfig.txt')
    connection = DBfile.readline()
    engine = create_engine(connection)
    # read the geodataframe from a postgreSQL table
    data_geodf = gpd.read_postgis('Yaounde_ALPhA_Survey', engine, geom_col='geometry')
    return data_geodf

# Updating Lagos Database 'Lagos_ALPhA_Survey'
Update_LAGOS_DB()
# Updating Yaundé Database 'Yaounde_ALPhA_Survey'
# Update_YAOUNDE_DB()