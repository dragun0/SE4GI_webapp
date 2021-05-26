
from psycopg2 import connect
import json
import requests
# import geopandas as gpd
import pandas as pd
# import fiona
from sqlalchemy import create_engine


cleanup = (
        'DROP TABLE IF EXISTS sys_table CASCADE',
        'DROP TABLE IF EXISTS comment_table',
        'DROP TABLE IF EXISTS data_table'
        )

commands =(
        """
        CREATE TABLE sys_table (
            userid SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            age INTEGER
        )
        """
        ,
        """
        CREATE TABLE comment_table (
            comment_id SERIAL PRIMARY KEY,
            userid INTEGER NOT NULL UNIQUE,
            created TIMESTAMP DEFAULT NOW(),
            comment VARCHAR(500) NOT NULL,
            FOREIGN KEY (userid)
                    REFERENCES sys_table (userid)
 
        )
        """)

conn = connect("dbname=student user=postgres password=user")
cur = conn.cursor()

for command in cleanup:
    cur.execute(command)
for command in commands:
    cur.execute(command)



cur.close()
conn.commit()
conn.close()




#engine = create_engine('postgresql://postgres:user@localhost:5432/student')

