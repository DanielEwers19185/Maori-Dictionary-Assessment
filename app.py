from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = 'C:/Users/School/OneDrive - Wellington College/13DTS/Maori Dictionary Assessment/Templates/smile.db'

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "peepeepoopoobumbum"

def create_connection(db_file: object) -> object:
    try:
        connection = sqlite3.connect(db_file)
        return connection

    except Error as e:
        print(e)
    return None


def is_logged_in():
    if session.get("email") is None:
       print("Not logged in")
       return False
    else:
       print("Logged in")
       return True

def render_cat_lev_menus(catlev):
    con = create_connection(DATABASE)
    query = "SELECT id, title FROM categories WHERE type=?"
    cur = con.cursor()
    cur.execute(query, (catlev))
    cat_list = cur.fetchall()
    con.close()
    return cat_list

@app.route('/')
def render_homepage():

    return render_template('home.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())


@app.route('/dictionary')
def render_dictionary_page():
    con = create_connection(DATABASE)
    query = "SELECT word, definition, cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), category, level FROM english_words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    con.close()
    print(word_list)
    # first_name = ""
    # if is_logged_in () :
    #    first_name = session['fname']
    return render_template('dictionary.html', cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), word_list=word_list, logged_in=is_logged_in())


@app.route('/contact')
def render_content_page():
    return render_template('contact.html', cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())

@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if is_logged_in():
        return redirect('/dictionary/1')
    print('logging in')
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        query = """SELECT id, fname, password FROM user WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        user_data = cur.fetchall()
        con.close()

        if user_data is None:
            return redirect('/login?error=Emial+invalid+or+password+incorrect')
        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect('/login?error=Emial+invalid+or+password+incorrect')

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + '?error=Emial+invalid+or+password+incorrect')

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name

        return redirect('/')
    return render_template('login.html', cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())

@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time')

@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if is_logged_in():
        return redirect('/dictionary/1?message=Already+logged+in')
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            return redirect("\signup?error=Passwords+Do+Not+Match")
        if len(password) < 8:
            return redirect("\signup?error=Password+Must+Be+At+Least+8+Characters")

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(DATABASE)
        query = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('\signup?error=Email+is+already+used')

        con.commit()
        con.close

        return redirect('\login')

    return render_template('signup.html', cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())

@app.route('/admin')
def render_admin():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "SELECT name, description, volume, image, price FROM products WHERE cat_id=?"
    cur = con.cursor()
    cur.execute(query)
    product_list = cur.fetchall()
    query = 'SELECT id FROM category'
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return render_template("admin.html", cat_list=render_cat_lev_menus(), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in(), categories=category_list)

@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        cat_name = request.form.get('name').lower().strip()
        print(cat_name)
        con = create_connection(DATABASE)
        query = "INSERT INTO caegory ('name') VALUES (?)"
        cur = con.cursor()
        cur.execute(query, (cat_name, ))
        con.commit()
        con.close()
        return redirect('/admin')

@app.route('/delete_category', methods=['POST'])
def render_delete_category():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        category = request.form.get('cat_id')
        print(category)
        category = category.split(', ')
        cat_id = category[0]
        cat_name = category[1]
        return render_template("delete_confirm.html", cat_id=cat_id, name=cat_name, type='category')
    return redirect('/admin')

@app.route('/delete_category_confirm/<cat_id>')
def delete_category_confirm(cat_id):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "DELETE FROM category WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (cat_id, ))
    con.commit()
    con.close()
    return redirect('/admin')



app.run(host='0.0.0.0', debug=True)
