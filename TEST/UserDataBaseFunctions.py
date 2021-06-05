# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 17:24:28 2021

@author: leoni
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from psycopg2 import connect
from werkzeug.exceptions import abort



#This function creates a connection to the database for the tables created
def conn_db():
    if 'db' not in g:
        DBfile = open('Database/dbConfig.txt')
        connection = DBfile.readline()
        g.db =  connect(connection)
    return g.db

#This function closes the connection to the database
def enddb_conn():
    if 'db' in g:
        g.db.close()
        g.pop('db')
        

def mysession():
    userid = session.get('userid')
    if userid is None:
        g.user = None
    else:
        conn = conn_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM sys_table WHERE userid = %s', (userid,))
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
    if g.user is not None:
        return True
    else: 
        return False


def get_post(id):
    conn = conn_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM post WHERE post.comment_id = %s", (id,))
    post = cur.fetchone()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if post[1] != g.user[0]:
        abort(403)
    return post
