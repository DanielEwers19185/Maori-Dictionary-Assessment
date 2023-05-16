from flask import Flask, render_template, redirect, request, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

DATABASE = 'C:/Users/School/OneDrive - Wellington College/13DTS/Maori Dictionary Assessment/Templates/smile.db'

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "peepeepoopoobumbum"
app.config['UPLOAD_FOLDER'] = 'C:/Users/School/OneDrive - Wellington College/13DTS/Maori Dictionary Assessment/Static/images'

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
        perms = ""
        return False, perms
    else:
        print("Logged in")
        perms = session.get('user_perms')
        return True, perms
def render_cat_lev_menus(catlev):
    con = create_connection(DATABASE)
    query = "SELECT id, title FROM categories WHERE type=?"
    cur = con.cursor()
    cur.execute(query, (catlev))
    cat_list = cur.fetchall()
    con.close()
    return cat_list

def log_edit(edited_id, edited_type, edit):
    user = session.get('user_id')
    time = datetime.now()
    con = create_connection(DATABASE)
    query = "SELECT fname FROM user WHERE id =? "
    cur = con.cursor()
    cur.execute(query, (session.get('user_id'),))
    editor_name = cur.fetchall()[0][0]
    if edited_type == "Lev_Cat":
        query = "SELECT title FROM categories WHERE id =? "
        cur.execute(query, (edited_id,))
    else:
        query = "SELECT eng_word FROM words WHERE id =? "
        cur.execute(query, (edited_id,))
    edited_title = cur.fetchall()[0][0]
    query = "INSERT INTO edit_log ('edited_id', 'edited_type', 'edit', 'editor_id', 'date_time', 'editor_name', 'edited_title') VALUES (?, ?, ?, ?, ?, ?, ?)"
    cur.execute(query, (edited_id, edited_type, edit, user, time, editor_name, edited_title,))
    con.commit()
    con.close()

@app.route('/')
def render_homepage():
    return render_template('home.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in()[0], perms = is_logged_in()[1])


@app.route('/dictionary/<cat_id>')
def render_dictionary_page(cat_id):
    cat_id = cat_id.strip("<")
    cat_id = cat_id.strip(">")
    con = create_connection(DATABASE)
    cur = con.cursor()
    if cat_id == "":
        query = "SELECT mri_word, eng_word, definition, category, level, image FROM words"
        cur.execute(query, )
        word_list = cur.fetchall()
        cat_info = [("All Categories", "The whole undivided dictionary",)]
    else:
        query = "SELECT mri_word, eng_word, definition, category, level, image FROM words WHERE category =? OR level = ?"
        cur.execute(query, (cat_id, cat_id,))
        word_list = cur.fetchall()
        query = "SELECT title, description FROM categories WHERE id =? "
        cur.execute(query, (cat_id,))
        cat_info = cur.fetchall()
    for i in range(len(word_list)):
        query = "SELECT title FROM categories WHERE id =? "
        cur.execute(query, (word_list[i][3], ))
        word_list[i] = word_list[i] + (cur.fetchall()[0])
        cur.execute(query, (word_list[i][4], ))
        word_list[i] = word_list[i] + (cur.fetchall()[0])
    con.close()
    print(word_list)
    print(cat_info)
    # first_name = ""
    # if is_logged_in () :
    #    first_name = session['fname']
    return render_template('dictionary.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), word_list=word_list, logged_in=is_logged_in()[0], cat_info=cat_info, perms = is_logged_in()[1])


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if is_logged_in()[0]:
        return redirect('/dictionary/1')
    print('logging in')
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        query = """SELECT id, fname, password, permissions FROM user WHERE email = ?"""
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
            user_perms = user_data[0][3]
        except IndexError:
            return redirect('/login?error=Emial+invalid+or+password+incorrect')

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + '?error=Emial+invalid+or+password+incorrect')

        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['user_perms'] = user_perms
        print(user_perms)

        return redirect('/')
    return render_template('login.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in()[0], perms = is_logged_in()[1])

@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time')

@app.route('/signup', methods=['POST', 'GET'])
def render_signup():
    if is_logged_in()[0]:
        return redirect('/dictionary/1?message=Already+logged+in')
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        user_perms = request.form.get('user_permission')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        print(user_perms)
        if password != password2:
            return redirect("\signup?error=Passwords+Do+Not+Match")
        if len(password) < 8:
            return redirect("\signup?error=Password+Must+Be+At+Least+8+Characters")
        hashed_password = bcrypt.generate_password_hash(password)

        if user_perms:
            user_perms = "admin"
        else:
            user_perms = "general"

        con = create_connection(DATABASE)
        query = "INSERT INTO user (fname, lname, email, password, permissions) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, user_perms))
        except sqlite3.IntegrityError:
            con.close()
            return redirect('\signup?error=Email+is+already+used')

        con.commit()
        con.close

        return redirect('\login')

    return render_template('signup.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in()[0], perms = is_logged_in()[1])

@app.route('/admin')
def render_admin():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    con = create_connection(DATABASE)
    query = "SELECT mri_word, eng_word, definition, category, level, id FROM words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    query = 'SELECT id, title, type FROM categories'
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    query = "SELECT edited_id, edited_type, edit, editor_id, date_time, editor_name, edited_title FROM edit_log"
    cur.execute(query, )
    edit_list = cur.fetchall()
    con.close()
    return render_template("admin.html", cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in()[0], categories=category_list, word_list=word_list, perms = is_logged_in()[1], edit_list=edit_list)

@app.route('/add_category', methods=['POST'])
def add_category():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
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
        query = "SELECT MAX(id) FROM categories"
        cur.execute(query, )
        edited_id = cur.fetchall()[0][0]
        con.close()
        edited_type = "Lev_Cat"
        edit = "Added"
        log_edit(edited_id, edited_type, edit)
        return redirect('/admin')

@app.route('/delete_category', methods=['POST'])
def render_delete_category():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    if request.method == "POST":
        category = request.form.get('cat_id')
        print(category)
        category = category.split(', ')
        cat_id = category[0]
        cat_name = category[1]
        cat_type = category[2]
        return render_template("delete_confirm.html", sub_id=cat_id, name=cat_name, type=cat_type, logged_in=is_logged_in()[0], perms = is_logged_in()[1])
    return redirect('/admin')

@app.route('/delete_confirm/<sub_id>/<type>')
def delete_confirm(sub_id, type):
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    edited_id = sub_id
    edit = "Deleted"
    con = create_connection(DATABASE)
    cur = con.cursor()
    if type == "C" or type == "L":
        edited_type = "Lev_Cat"
        log_edit(edited_id, edited_type, edit)
        query = "DELETE FROM categories WHERE id = ?"
        cur.execute(query, (sub_id,))
        con.commit()
        query = "SELECT id FROM words WHERE category = ? OR level = ?"
        cur.execute(query, (sub_id, sub_id,))
        word_list = cur.fetchall()
        for i in range(len(word_list)):
            query = "DELETE FROM words WHERE id = ?"
            cur.execute(query, ( word_list[i] ))
            con.commit()
    elif type == "word":
        edited_type = "Word"
        log_edit(edited_id, edited_type, edit)
        query = "DELETE FROM words WHERE id = ?"
        cur.execute(query, (sub_id, ))
        con.commit()
    con.close()
    return redirect('/admin')

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    if request.method == "POST":
        print(request.form)
        m_tans = request.form.get('m_trans').lower().strip()
        e_trans = request.form.get('e_trans').lower().strip()
        word_def = request.form.get('word_def').lower().strip()
        w_cat = request.form.get('w_cat')
        w_lev = request.form.get('w_lev')
        word_img = request.form.get('word_img')
        con = create_connection(DATABASE)
        query = "INSERT INTO words  ('eng_word', 'category', 'definition', 'level', 'mri_word', 'image') VALUES (?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_tans, word_img,))
        con.commit()
        query = "SELECT MAX(id) FROM words"
        cur.execute(query, )
        edited_id = cur.fetchall()[0][0]
        con.close()
        edited_type = "Word"
        edit = "Added"
        log_edit(edited_id, edited_type, edit)
        #if word_img != '':
        #    file = request.files['word_img']
        #    filename = secure_filename(file.filename)
        #    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/admin')

@app.route('/edit_delete_word', methods=['POST'])
def edit_delete_word():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
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
        return render_template("edit_delete_word.html", word_list=word_list, categories=category_list, logged_in=is_logged_in()[0], perms = is_logged_in()[1])
    return redirect('/admin')

@app.route('/delete_word', methods=['POST'])
def render_delete_word():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    if request.method == "POST":
        print(request.form)
        word = request.form.get('word')
        print(word)
        word = word.split(', ')
        word_id = word[0]
        word_name = word[1]+'/'+word[2]
        return render_template("delete_confirm.html", sub_id=word_id, name=word_name, type="word")
    return redirect('/admin')


@app.route('/edit_word', methods=['POST'])
def render_edit_word():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    if request.method == "POST":
        m_trans = request.form.get('m_trans').lower().strip()
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
        return render_template("edit_confirm.html", sub_id=word_id, e_trans=e_trans, w_cat=w_cat, word_def=word_def, w_lev=w_lev, m_trans=m_trans, sub_type="word")
    return redirect('/admin')

@app.route('/edit_confirm/<sub_id>/<e_trans>+<w_cat>+<word_def>+<w_lev>+<m_trans>')
def edit_confirm(sub_id, e_trans, w_cat, word_def, w_lev, m_trans):
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "UPDATE words SET eng_word = ?, category = ?, definition = ?, level = ?, mri_word = ? WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_trans, sub_id ))
    con.commit()
    con.close()
    edited_id = sub_id
    edited_type = "Word"
    edit = "Edited"
    log_edit(edited_id, edited_type, edit)

    return redirect('/admin')

@app.route('/edit_category', methods=['POST'])
def render_edit_category():
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    if request.method == "POST":
        print(request.form)
        e_cat = request.form.get('edited_category')
        e_title = request.form.get('cat_title').title().strip()
        cat_def = request.form.get('cat_def').title().strip()
        cat_lev = request.form.get('edited_cat_lev')
        return render_template("edit_confirm.html", sub_id=e_cat, e_title=e_title, cat_def=cat_def, cat_lev=cat_lev, sub_type="cat")
    return redirect('/admin')

@app.route('/edit_confirm/<sub_id>/<e_title>+<cat_def>+<cat_lev>')
def edit_confirm_cat(sub_id, e_title, cat_def, cat_lev):
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "UPDATE categories SET title = ?, description = ?, type = ? WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (e_title, cat_def, cat_lev, sub_id ))
    con.commit()
    con.close()
    edited_id = sub_id
    edited_type = "Lev_Cat"
    edit = "Edited"
    log_edit(edited_id, edited_type, edit)
    return redirect('/admin')

@app.route('/word_page/<word_id>')
def render_word_page(word_id):
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT mri_word, eng_word, definition, category, level, image, id FROM words WHERE id = ?"
    cur.execute(query, (word_id))
    word_list = cur.fetchall()
    query = "SELECT title, description FROM categories WHERE id =? "
    cur.execute(query, (word_list[0][3],))
    cat_info = cur.fetchall()[0]
    cur.execute(query, (word_list[0][4],))
    lev_info = cur.fetchall()[0]
    if is_logged_in()[1] != "admin":
        query = "SELECT edited_id, edited_type, edit, editor_id, date_time, editor_name, edited_title FROM edit_log WHERE edited_id=? or edited_id=? or edited_id=?"
        cur.execute(query, (word_id, word_list[0][3], word_list[0][4]))
        edit_list = cur.fetchall()
    else:
        edit_list = []
    con.close()
    print(lev_info)
    print(cat_info)
    return render_template('word_page.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'), logged_in=is_logged_in()[0], perms=is_logged_in()[1], word_list=word_list, cat_info=cat_info, lev_info=lev_info, edit_list=edit_list)

app.run(host='0.0.0.0', debug=True)
