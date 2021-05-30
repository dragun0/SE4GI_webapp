from flask import Flask, render_template, request, redirect, url_for, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from psycopg2 import connect


app = Flask(__name__,template_folder='templates')
app.secret_key = '!@3QWeASdZXc'


#This function creates a connection to the database saved in Database.txt

def conn_db():
    if 'db' not in g:
        g.db =  connect(dbname="SE4GI", user="postgres", password="kotxino35", port="5433")
    return g.db

def enddb_conn():
    if 'db' in g:
        g.db.close()
        g.pop('db')

@app.route("/")
@app.route("/Home")
@app.route("/home")
def home():
    
    mysession()
    return '''
<h2>This is a TEST web app for HOME:</h2>
<a href=/Portfolio>Portfolio</a><br>
<a href=/login>login</a><br>
<a href=/Register>Sign UP</a>
'''   

@app.route("/")
@app.route("/Portfolio")
@app.route("/portfolio")
def portfolio():
    
    alpha = get_alpha('69')
    
    mysession()
    return render_template('portfolio.html', alphas=alpha)

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
            return redirect(url_for('home'))
        
        flash(error)
        
    return render_template('sign_in.html')

@app.route('/Logout')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


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



if (__name__)=='__main__':
    app.run(debug=True,use_reloader=False)
