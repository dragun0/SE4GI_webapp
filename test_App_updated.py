from flask import Flask, render_template, request, redirect, url_for, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from psycopg2 import connect


app = Flask(__name__,template_folder='templates')
app.secret_key = '!@3QWeASdZXc'


#This function creates a connection to the database saved in Database.txt

def conn_db():
    if 'db' not in g:
        
        g.db =  connect("dbname=student user=postgres password=user")
    
    return g.db

def enddb_conn():
    if 'db' in g:
        g.db.close()
        g.pop('db')

@app.route('/')
@app.route('/home')
def index():
    conn = connect("dbname=student user=postgres password=user")
    cur = conn.cursor()
    cur.execute(
            """SELECT sys_table.username, post.post_id, post.created, post.body 
               FROM sys_table, post WHERE  
                    sys_table.userid = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    mysession()

    return render_template('blog/comment_order.html', posts=posts)

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
            error = 'Please fill out this field.'
        elif not password:
            error = 'Please fill out this field.'
        else :
            conn = conn_db()
            cur = conn.cursor()
            cur.execute('SELECT userid FROM sys_table WHERE username = %s', (username,))
            if cur.fetchone() is not None:
                error = 'Username already used! try another one please!'
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
            error = 'Login failed! Wrong Username!'
        elif not check_password_hash(sys[2], password):
            error = 'Login failed! Wrong Password!'
            
        if error is None:
            session.clear()
            session['userid'] = sys[0]
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('sign_in.html')

@app.route('/Logout')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def mysession():
    userid = session.get('userid')

    if userid is None:
        g.user = None
    else:
        conn = connect("dbname=student user=postgres password=user")
        cur = conn.cursor()
        cur.execute('SELECT * FROM sys_table WHERE userid = %s', (userid,))
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
    if g.user is not None:
        return True
    else: 
        return False
    


@app.route('/comment', methods=('GET', 'POST'))
def comment():
    if mysession():
        if request.method == 'POST' :
            body = request.form['comment']
            error = None
            
            if not body :
                error = 'body is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('home'))
            else : 
                    conn =connect("dbname=student user=postgres password=user")
                    cur = conn.cursor()
                    cur.execute('INSERT INTO post (body, author_id) VALUES ( %s, %s)', 
                               (body, g.user[0])
                               )
                    cur.close()
                    conn.commit()
                    conn.close()
                    return redirect(url_for('index'))
        else :
            return render_template('create_comment.html')
    else:
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))

def get_post(id):
    
    conn = connect("dbname=student user=postgres password=user")
    cur = conn.cursor()
    cur.execute(
        """SELECT *
           FROM post
           WHERE post.post_id = %s""",
        (id,)
    )
    post = cur.fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if post[1] != g.user[0]:
        abort(403)

    return post

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
                return redirect(url_for('index'))
            else : 
               
                conn = connect("dbname=student user=postgres password=user")
                cur = conn.cursor()
                cur.execute('UPDATE post SET  body = %s'
                               'WHERE post_id = %s', 
                               (body, id)
                               )
                cur.close()
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
        else :
            return render_template('blog/update.html', post=post)
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    
    
    conn = connect("dbname=student user=postgres password=user")
                
    cur = conn.cursor()
    cur.execute('DELETE FROM post WHERE post_id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))                           


if (__name__)=='__main__':
    app.run(debug=True,use_reloader=False)
