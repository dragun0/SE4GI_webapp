# -*- coding: utf-8 -*-
"""
Politecnico di Milano – Software Engineering for Geoinformatics 2021
WEB-BASED APPLICATION FOR THE VISUALISATION AND ANALYSIS OF THE ALPHA 
CITIZEN SCIENCE STUDY IN LAGOS, NIGERIA
@authors: M. Abd Alslam Mohammed Elkhalifa, M. Abdalla Eldouma Mohamed, 
D. Aguirre, L. Dragun
"""
# --------------------------- test_App_updated -------------------------------#
# The current script allows the web app to start running on the localhost adress
# ----------------------------------------------------------------------------#

# Needed libraries import
from flask import (Flask, render_template, request, flash, redirect, abort, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from UserDataBaseFunctions import *
from Mapping_tool import *
from Synchronizer import *

# App Flask object creation
app = Flask(__name__,template_folder='templates')
app.secret_key = '!@3QWeASdZXc'




# Decorator to establish the route for the main page and its function
@app.route('/')
@app.route('/start')
@app.route('/Start')
def start():
    return render_template('welcome.html')

# Decorator to establish the route for the contact page and its function
@app.route('/contact')
@app.route('/Contact')
def contact():
    mysession() 
    return render_template('contact.html')

         
@app.route('/', methods=('GET', 'POST'))
@app.route('/Register', methods=('GET', 'POST'))
@app.route('/register', methods=('GET', 'POST'))
def Register():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        age      = request.form['age']
        error    = None
        if not username:
            error = 'please fill out this field.'
        elif not password:
            error = 'please fill out this field.'
        if not email:
            error= 'please fill out this field.'
        if not age:
            error= 'please fill out this field.'
        else :
            conn = conn_db()
            cur = conn.cursor()
            cur.execute('SELECT userid FROM sys_table WHERE username = %s', (username,))
            if cur.fetchone() is not None:
                error = 'Username already used! try another one please!'
                cur.close()
            else:
                conn = conn_db()
                cur = conn.cursor()
                cur.execute('SELECT userid FROM sys_table WHERE email = %s', (email,))
                if cur.fetchone() is not None:
                   error = 'Email already used! try another one please!'
                   cur.close()   
        if error is None:
            conn = conn_db()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO sys_table (username, password, email, age) VALUES (%s, %s,%s, %s)',
                (username, generate_password_hash(password), email, age))
            cur.close()
            conn.commit()
            return redirect(url_for('login'))

        flash(error)
    
     return render_template('sign_UP.html')
    

@app.route('/Login', methods=('GET', 'POST'))
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        conn = conn_db()
        cur = conn.cursor()
        error = None
        cur.execute('SELECT * FROM sys_table WHERE username = %s', (username,))
        sys = cur.fetchone()
        cur.close()
        conn.commit()
        if sys is None:
            error = 'Incorrect Username!'
        elif not check_password_hash(sys[2], password):
            error = 'Incorrect Password!'
            
        if error is None:
            session.clear()
            session['userid'] = sys[0]
            return redirect(url_for('HomeWithMap'))
        flash(error)
        
    return render_template('sign_in.html')


@app.route('/HomeWithMap')
def HomeWithMap(): 
    
    mysession()
    make_plot()
    return render_template('Map_home.html')
    

@app.route("/portfolio")
@app.route("/Portfolio")
def portfolio():
    mysession()
    
    selectedID = request.args.get('id')
    alpha = get_alpha(selectedID)
      
    return render_template('Extend_portfolio.html', alphas=alpha)

def get_alpha(id):
    conn = conn_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM public."Lagos_ALPhA_Survey"
           WHERE "ID" = %s""",
        (id,)
    )
    alpha = cur.fetchall()
    cur.close()
    if alpha is None:
        abort(404, "Alpha ID {0} doesn't exist.".format(id))

    return alpha

# Decorator to establish the route for the about page and its function
@app.route('/about')
@app.route('/About')
def About():
    if mysession():
           return render_template('About.html')
    return render_template('About.html')



# Decorator to establish the route for the show comment page and its function
@app.route('/show_comment')
def show_comment():
    mysession()
    conn = conn_db()
    cur = conn.cursor()
    cur.execute(
            """SELECT sys_table.username, post.comment_id, post.created, post.comment 
               FROM sys_table, post WHERE sys_table.userid = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    
    return render_template('blog/comment_order.html', posts=posts)


@app.route('/comment', methods=('GET', 'POST'))
def comment():
    if mysession():
        if request.method == 'POST' :
            body = request.form['comment']
            error = None
            
            if not body :
                error = 'comment can not be empty'
            if error is not None :
                flash(error)
                return redirect(url_for('show_comment'))
            else : 
                    conn = conn_db()
                    cur = conn.cursor()
                    cur.execute('INSERT INTO post (comment, author_id) VALUES ( %s, %s)', 
                               (body, g.user[0]))
                    cur.close()
                    conn.commit()
                    conn.close()
                    return redirect(url_for('show_comment'))
        else :
            return render_template('Extend.html')
    else:
        error = 'You must be logged in to comment!'
        flash(error)
        return redirect(url_for('login'))




# Decorator to establish the route for the register page and its function

# Decorator to establish the route for the log in page and its function

# Decorator to establish the route for the log out page and its function
@app.route('/Logout')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('HomeWithMap'))





# Decorator to establish the route for the comment update page and its function
@app.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    if mysession():
        post = get_post(id)
        if request.method == 'POST' :
            body = request.form['comment']
            error = None
            
            if not body :
                error = 'comment can not be empty!'
            if error is not None :
                flash(error)
                return redirect(url_for('show_comment'))
            else : 
               
                conn = conn_db()
                cur = conn.cursor()
                cur.execute('UPDATE post SET  comment = %s'
                               'WHERE comment_id = %s', 
                               (body, id)
                               )
                cur.close()
                conn.commit()
                conn.close()
                return redirect(url_for('show_comment'))
        else :
            return render_template('blog/update.html', post=post)
    else :
        error = 'Only logged users can insert posts!'
        flash(error)
        return redirect(url_for('login'))

# Decorator to establish the route for the comment delete page and its function
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = conn_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM post WHERE comment_id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('show_comment'))                           

# Running the app in standalone mode, in debug mode and without the windows reloader
if (__name__)=='__main__':
    app.run(debug=True,use_reloader=True)
