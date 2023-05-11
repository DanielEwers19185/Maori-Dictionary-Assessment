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


@app.route('/dictionary/<cat_id>')
def render_dictionary_page(cat_id):
    cat_id = cat_id.strip("<")
    cat_id = cat_id.strip(">")
    con = create_connection(DATABASE)
    query = "SELECT mri_word, eng_word, definition, category, level FROM words WHERE category =? OR level = ?"
    cur = con.cursor()
    cur.execute(query, (cat_id, cat_id,))
    word_list = cur.fetchall()
    for i in range(len(word_list)):
        query = "SELECT title FROM categories WHERE id =? "
        cur.execute(query, (word_list[i][3], ))
        word_list[i] = word_list[i] + (cur.fetchall()[0])
        cur.execute(query, (word_list[i][4], ))
        word_list[i] = word_list[i] + (cur.fetchall()[0])
    con.close()
    print(cat_id)
    print(word_list)
    # first_name = ""
    # if is_logged_in () :
    #    first_name = session['fname']
    return render_template('dictionary.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), word_list=word_list, logged_in=is_logged_in())


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
    return render_template('login.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())

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

    return render_template('signup.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in())

@app.route('/admin')
def render_admin():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "SELECT mri_word, eng_word, definition, category, level, id FROM words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    query = 'SELECT id, title, type FROM categories'
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    con.close()
    return render_template("admin.html", cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in(), categories=category_list, word_list=word_list)

@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        cat_name = request.form.get('name').lower().strip()
        cat_des = request.form.get('description').lower().strip()
        cat_type = request.form.get('cat_lev')
        print(cat_name)
        con = create_connection(DATABASE)
        query = "INSERT INTO categories  ('title', 'description', 'type') VALUES (?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (cat_name, cat_des, cat_type,))
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
        return render_template("delete_confirm.html", sub_id=cat_id, name=cat_name, type = "cat")
    return redirect('/admin')

@app.route('/delete_confirm/<sub_id>/<type>')
def delete_confirm(sub_id, type):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    con = create_connection(DATABASE)
    if type == "cat":
        query = "DELETE FROM categories WHERE id = ?"
    elif type == "word":
        query = "DELETE FROM words WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (sub_id, ))
    con.commit()
    con.close()
    return redirect('/admin')

@app.route('/add_word', methods=['POST'])
def add_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        m_tans = request.form.get('m_trans').lower().strip()
        e_trans = request.form.get('e_trans').lower().strip()
        word_def = request.form.get('word_def').lower().strip()
        w_cat = request.form.get('w_cat')
        w_lev = request.form.get('w_lev')
        con = create_connection(DATABASE)
        query = "INSERT INTO words  ('eng_word', 'category', 'definition', 'level', 'mri_word') VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_tans,))
        con.commit()
        con.close()
        return redirect('/admin')

@app.route('/edit_delete_word', methods=['POST'])
def edit_delete_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        category = request.form.get('e_d_word_cat')
        con = create_connection(DATABASE)
        query = "SELECT mri_word, eng_word, definition, category, level, id FROM words WHERE category=? OR level=?"
        cur = con.cursor()
        cur.execute(query, (category, category,))
        word_list = cur.fetchall()
        query = 'SELECT id, title, type FROM categories'
        cur = con.cursor()
        cur.execute(query)
        category_list = cur.fetchall()
        con.close()
        return render_template("edit_delete_word.html", word_list=word_list, categories=category_list)
    return redirect('/admin')

@app.route('/delete_word', methods=['POST'])
def render_delete_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        print(request.form)
        word = request.form.get('word')
        print(word)
        word = word.split(', ')
        word_id = word[0]
        word_name = word[1]+'/'+word[2]
        return render_template("delete_confirm.html", sub_id=word_id, name=word_name, type = "word")
    return redirect('/admin')


@app.route('/edit_word', methods=['POST'])
def render_edit_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    if request.method == "POST":
        m_tans = request.form.get('m_trans').lower().strip()
        e_trans = request.form.get('e_trans').lower().strip()
        word_def = request.form.get('word_def').lower().strip()
        w_cat = request.form.get('w_cat')
        w_lev = request.form.get('w_lev')
        print(request.form)
        word = request.form.get('word')
        print(word)
        word = word.split(', ')
        word_id = word[0]
        word_name = word[1]+'/'+word[2]
        return render_template("edit_confirm.html", sub_id=word_id, name=word_name, e_trans=e_trans, w_cat=w_cat, word_def=word_def, w_lev=w_lev, m_tans=m_tans)
    return redirect('/admin')

@app.route('/edit_confirm/<sub_id>/<e_trans>+<w_cat>+<word_def>+<w_lev>+<m_trans>')
def edit_confirm(sub_id, e_trans, w_cat, word_def, w_lev, m_tans):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in')
    con = create_connection(DATABASE)
    query = "DELETE FROM words WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (sub_id, ))
    con.commit()
    query = "INSERT INTO words  ('eng_word', 'category', 'definition', 'level', 'mri_word', 'id') VALUES (?, ?, ?, ?, ?, ?)"
    cur = con.cursor()
    cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_tans, sub_id,))
    con.commit()
    con.close()
    return redirect('/admin')

app.run(host='0.0.0.0', debug=True)
