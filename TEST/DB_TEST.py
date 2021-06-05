# -*- coding: utf-8 -*-
"""
Politecnico di Milano – Software Engineering for Geoinformatics 2021
WEB-BASED APPLICATION FOR THE VISUALISATION AND ANALYSIS OF THE ALPHA 
CITIZEN SCIENCE STUDY IN LAGOS, NIGERIA
@authors: M. Abd Alslam Mohammed Elkhalifa, M. Abdalla Eldouma Mohamed, 
D. Aguirre, L. Dragun
"""
# -------------------------------- DB_TEST -----------------------------------#
# The current script allows the creation of the users sys_table and the comment
# table in the SQL manager, in this case PostgreSQL. This script is executed
# once prior the pilot test of the web application.
# ----------------------------------------------------------------------------#

# Needed libraries import
from psycopg2 import connect

# Cleanup instruction drops existing tables
cleanup = (
        'DROP TABLE IF EXISTS sys_table CASCADE',
        'DROP TABLE IF EXISTS post'
        )

# Commands instruction creates the tables
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
        CREATE TABLE post (
            comment_id SERIAL PRIMARY KEY,
            author_id INTEGER NOT NULL,
            created TIMESTAMP DEFAULT NOW(),
            comment VARCHAR(500) NOT NULL,
            FOREIGN KEY (author_id) REFERENCES sys_table (userid)
        )
        """)

# Establishing the Database connection trough psycopg2 and txt file conection details
DBfile = open('Database/dbConfig.txt')
connection = DBfile.readline()
conn = connect(connection)
cur = conn.cursor()

# Executing all commands in cleanup and commands instructions
for command in cleanup:
    cur.execute(command)
for command in commands:
    cur.execute(command)

# Closing, commiting the commands and ending the connection to DB
cur.close()
conn.commit()
conn.close()