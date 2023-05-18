# Code runs a maori-english dictionary website

# Importing all required modules
# Importing Flask modules including; Flask itself, "render_template" to render the HTML, "redirect" to redirect the user
# to different pages/functions, "request" to allow the code to fetch user inputs and "session" to store infomation from
# only this session
# Importing allows modules/features that are not generically part of the language to be used
from flask import Flask, render_template, redirect, request, session
# Import SQlite3 for the database portion
import sqlite3
# Importing "Error" from SQlite so if certain errors occurs the website doesn't just crash and we can make it print the
# error
from sqlite3 import Error
# Importing "Bcrypt" to encrypt passwords using a key specified later, this adds security
from flask_bcrypt import Bcrypt
# Importing "datetime" to add timestamps to the edit log.
from datetime import datetime

# Setting variables allows for  the variable name to stand for what is contained in the veriable, typically the stored
# infomation is a string of some sort however it can be other variables
# Setting the database's path as a variable for ease of coding (allows us to type "DATABASE" instead of the whole path)
DATABASE = 'C:/Users/School/OneDrive - Wellington College/13DTS/Maori Dictionary Assessment/Templates/smile.db'
# Setting "Flask(__name__)" to APP to allow ease of coding and reading
APP = Flask(__name__)
# Setting "Bcrypt(APP)" to BCRYPT to allow ease of coding and reading
BCRYPT = Bcrypt(APP)
# Setting the encryption key for passwords
APP.secret_key = "sjyglkeafgh23457767uhd4dgy"

# Creating a function to establish a connection with a given database
# Functions are section of code that can be referanced and when referanced, will run the functions code, this can
# include the use of variables that are given in the function call. The function will return any veriables stated.
def create_connection(db_file: object) -> object:
    # A try and except loop allows the code to attempt to execute a section of code provided after the "try" statement,
    # however if it is unable to execute the portion of code due to the error stated in the except statement, it allows
    # another peice of code to be ran
    # Attempting to estabish the connection and returning the connection if successfull
    try:
        connection = sqlite3.connect(db_file)
        return connection

    # If a connection is unable to be established, getting the error and printing it into the console
    except Error as e:
        print(e)
    # Returning no values if an error has occured
    return None

# Creating a function to check if the user is currently logged into the website and the permissions they possess
def is_logged_in():
    # If else loops allow certain peices of code to be ran depending on if a condition has been met
    # Checking if there has been an email associated with the session
    if session.get("email") is None:
        # Setting perms variable to avoid, setting to nothing as the user does not posses special permissions
        perms = ""
        return False, perms
    else:
        # If the user is logged in, fetching the user's permissions and storing them as "perms"
        perms = session.get('user_perms')
        return True, perms

# Creating a function to get a list of all categories or levels for the dropdown boxes on the menu
def render_cat_lev_menus(catlev):
    # Creating a connection to the main database
    con = create_connection(DATABASE)
    # The "SELECT" function fetches certain data values
    # Creating a query to fetch the values in the 'id' and 'title' rows from the categories table where the type is
    # corresponding to the dropdown button's title
    query = "SELECT id, title FROM categories WHERE type=?"
    # Executing the query
    cur = con.cursor()
    cur.execute(query, (catlev))
    # Setting the results from the query to a list to be used in the creation of the dropdown options in the HTML
    cat_list = cur.fetchall()
    # Closing the connection
    con.close()
    # Returning the list of results (of categories or levels depending on what has been requested)
    return cat_list

# Creating a function that adds an edit to the edit log
def log_edit(edited_id, edited_type, edit):
    # Getting the user ID
    user = session.get('user_id')
    # Getting the timestamp
    time = datetime.now()
    # Creating a connection to the main database
    con = create_connection(DATABASE)
    # Creating a query to fetch the editing user's first name
    query = "SELECT fname FROM user WHERE id =? "
    # Executing the query
    cur = con.cursor()
    cur.execute(query, (session.get('user_id'),))
    # Setting the editor's name as 'editor name'
    editor_name = cur.fetchall()[0][0]

    # Checking what type of data is being edited
    if edited_type == "Lev_Cat":
        # Creating a query to get the title of the edited category
        query = "SELECT title FROM categories WHERE id =? "
        # Executing the query
        cur.execute(query, (edited_id,))
    else:
        # Creating a query to get the title of the edited word
        query = "SELECT eng_word FROM words WHERE id =? "
        # Executing the query
        cur.execute(query, (edited_id,))

    # Setting the name of the edited data as "edited_title"
    edited_title = cur.fetchall()[0][0]
    # The "INSERT" function adds given values into given tables
    # Creating a query to add listed values into their respective (listed) categories
    query = "INSERT INTO edit_log ('edited_id', 'edited_type', 'edit', 'editor_id', 'date_time', 'editor_name'," \
            " 'edited_title') VALUES (?, ?, ?, ?, ?, ?, ?)"
    # Executing the query with listed data
    cur.execute(query, (edited_id, edited_type, edit, user, time, editor_name, edited_title,))
    # Commiting the changes to the database
    con.commit()
    # Closing the connection
    con.close()

# Creating an route/function to render the home page of the website
@APP.route('/')
def render_homepage():
    # Checking if the user is logged in
    if is_logged_in()[0]:
        # If the user is logged in, setting the homepage to greet the user by their first name
        hello=session.get("first_name")
    else:
        # If the user isn't logged in then they are reminded to create an account
        hello="Remember to create an account!"
    # Render the template and pass through the list of categories, list of levels, whether or not the user is logged in
    # the user permissions and what to say after "hello"
    return render_template('home.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           logged_in=is_logged_in()[0], perms=is_logged_in()[1], hello=hello)

# Creating an route/function to render the dictionary page of the website
@APP.route('/dictionary/<cat_id>')
def render_dictionary_page(cat_id):
    # Stripping the brackets off the category/level ID
    cat_id = cat_id.strip("<")
    cat_id = cat_id.strip(">")
    # Creating a connection to the main database
    con = create_connection(DATABASE)
    cur = con.cursor()

    # Checking if the page is a category page or if it is the entire dictionary
    if cat_id == "":
        # If the page selected is the entire dictionary, creating a query to fetch all the words and info on them
        query = "SELECT mri_word, eng_word, definition, category, level, image, id FROM words"
        # Executing the query
        cur.execute(query, )
        # Adding all the fetched words and info on the words to the wordlist that will be loaded by the HTML
        word_list = cur.fetchall()
        # Setting the Category info to be displayed
        cat_info = [("All Categories", "The whole undivided dictionary",)]
    else:
        # If the page selected is a specific category page, creating a query to fetch all words and info on them that
        # are in that category
        query = "SELECT mri_word, eng_word, definition, category, level, image, id FROM words WHERE category =? OR " \
                "level = ?"
        # Executing the query
        cur.execute(query, (cat_id, cat_id,))
        # Adding all the fetched words and info on the words to the wordlist that will be loaded by the HTML
        word_list = cur.fetchall()
        # Setting the query to select the title and description of the category selected
        query = "SELECT title, description FROM categories WHERE id =? "
        # Executing the query
        cur.execute(query, (cat_id,))
        # Setting the Category info to be displayed
        cat_info = cur.fetchall()

    # A for function repeats the embeded code a cerain ammount of times, this is specified in the function
    # Repeats code for each word in the word list to add values/info to each word
    for i in range(len(word_list)):
        # Setting the query to fetch the title of the category and/or level for each word
        query = "SELECT title FROM categories WHERE id =? "
        # Executing the query for categories
        cur.execute(query, (word_list[i][3], ))
        # Adding the info to the words list
        word_list[i] = word_list[i] + (cur.fetchall()[0])
        # Executing the query for levels
        cur.execute(query, (word_list[i][4], ))
        # Adding the info to the words list
        word_list[i] = word_list[i] + (cur.fetchall()[0])
    # Closing the connection
    con.close()
    # Returning info for HTML
    return render_template('dictionary.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           word_list=word_list, logged_in=is_logged_in()[0], cat_info=cat_info,
                           perms = is_logged_in()[1])

# This function logs the user in or denies the user for a particular error and gives the error message
@APP.route('/login', methods=['POST', 'GET'])
def render_login():
    # Checking if user is alreadly logged in
    if is_logged_in()[0]:
        return redirect('/dictionary/1')

    # Checking correct method being used
    if request.method == 'POST':
        # Gathers all user info from email as email is unique key
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        query = """SELECT id, fname, password, permissions FROM user WHERE email = ?"""
        # Creating a connection to the main database and executing the data
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        # Adding the user data to a veriable
        user_data = cur.fetchall()
        # Closing the connection
        con.close()

        # Checking if the enterd info is correct and matches an existing account
        # If infomation does not match up, returning an error message and not locking in
        if user_data is None:
            return redirect('/login?error=Emial+invalid+or+password+incorrect')
        try:
            user_id = user_data[0][0]
            first_name = user_data[0][1]
            db_password = user_data[0][2]
            user_perms = user_data[0][3]
        except IndexError:
            return redirect('/login?error=Emial+invalid+or+password+incorrect')

        # Checking pasword is correct
        if not BCRYPT.check_password_hash(db_password, password):
            return redirect(request.referrer + '?error=Emial+invalid+or+password+incorrect')

        # Setting the session info/logging in
        session['email'] = email
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['user_perms'] = user_perms

    # Rendering a page depending on if log in was succesfull or not
        return redirect('/')
    return render_template('login.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           logged_in=is_logged_in()[0], perms = is_logged_in()[1])

# Logout the user by clearing the session data
@APP.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys())]
    return redirect('/?message=See+you+next+time')

# Rendering the sign up page and allowing the user to sign up if they are not logged in
@APP.route('/signup', methods=['POST', 'GET'])
def render_signup():
    # Checking if user is alreadly logged in
    if is_logged_in()[0]:
        return redirect('/dictionary/1?message=Already+logged+in')

    if request.method == 'POST':
        # Getting account infomation off HTML (first name, email, etc.)
        fname = request.form.get('fname').title().strip()
        lname = request.form.get('lname').title().strip()
        email = request.form.get('email').lower().strip()
        user_perms = request.form.get('user_permission')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        # Checking both passwords match
        if password != password2:
            return redirect("\signup?error=Passwords+Do+Not+Match")
        if len(password) < 8:
            return redirect("\signup?error=Password+Must+Be+At+Least+8+Characters")
        # Hashing the password for security purposes
        hashed_password = BCRYPT.generate_password_hash(password)

        # Checking if the user requires permissions and setting it as appropriate
        if user_perms:
            user_perms = "admin"
        else:
            user_perms = "general"

        # Creating a connection to the main database
        con = create_connection(DATABASE)
        # Adding the user data into the user table
        query = "INSERT INTO user (fname, lname, email, password, permissions) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, user_perms))
        except sqlite3.IntegrityError:
            # Closing the connection if the email is already in use
            con.close()
            return redirect('\signup?error=Email+is+already+used')
        # Commiting the change to the user table
        con.commit()
        # Closing the connection
        con.close
        # Rendering the log-in page
        return redirect('\login')
    # Rendering the signup page again
    return render_template('signup.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           logged_in=is_logged_in()[0], perms = is_logged_in()[1])

# Rendering/running the admin page
@APP.route('/admin')
def render_admin():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Creating a connection to the main database
    con = create_connection(DATABASE)
    # Fetching infomation on all the words and assigning them to a variable (list of tuples) to pass to the HTML
    query = "SELECT mri_word, eng_word, definition, category, level, id FROM words"
    cur = con.cursor()
    cur.execute(query)
    word_list = cur.fetchall()
    # Fetching infomation on all the categories and assigning them to a variable (list of tuples) to pass to the HTML
    query = 'SELECT id, title, type FROM categories'
    cur = con.cursor()
    cur.execute(query)
    category_list = cur.fetchall()
    # Fetching infomation on all the edits and assigning them to a variable (list of tuples) to pass to the HTML
    # For edit log
    query = "SELECT edited_id, edited_type, edit, editor_id, date_time, editor_name, edited_title FROM edit_log"
    cur.execute(query, )
    edit_list = cur.fetchall()
    # Closing the connection and rendering the page
    con.close()
    return render_template("admin.html", cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           logged_in=is_logged_in()[0], categories=category_list, word_list=word_list,
                           perms=is_logged_in()[1], edit_list=edit_list)

# This Function adds categories
@APP.route('/add_category', methods=['POST'])
def add_category():
    # Checking if the user is logged in and has admin so is therefore able to access this action
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    if request.method == "POST":
        # Getting info that user has input about categories
        cat_name = request.form.get('name').lower().strip()
        cat_des = request.form.get('description').lower().strip()
        cat_type = request.form.get('cat_lev')
        # Creating a connection to the main database to add the new categories
        con = create_connection(DATABASE)
        # Adding new categories
        query = "INSERT INTO categories  ('title', 'description', 'type') VALUES (?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (cat_name, cat_des, cat_type,))
        # Comitting the changes to the database
        con.commit()
        # Setting values for the edit log by getting the id of the latest addition to the table
        query = "SELECT MAX(id) FROM categories"
        cur.execute(query, )
        edited_id = cur.fetchall()[0][0]
        # Closing the connection
        con.close()
        # Setting other infomation for the edit log
        edited_type = "Lev_Cat"
        edit = "Added"
        log_edit(edited_id, edited_type, edit)
        return redirect('/admin')

# This renders the "delete confirm page for categories with all the necessary infomation
@APP.route('/delete_category', methods=['POST'])
def render_delete_category():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    if request.method == "POST":
        # Fetching all the necessary infomation to display on the delete confirm page and to delete the word
        category = request.form.get('cat_id')
        category = category.split(', ')
        cat_id = category[0]
        cat_name = category[1]
        cat_type = category[2]
        # Rendering the delete confirm page
        return render_template("delete_confirm.html", sub_id=cat_id, name=cat_name, type=cat_type,
                               logged_in=is_logged_in()[0], perms = is_logged_in()[1])
    return redirect('/admin')

# Deleting subjects from their respective tables
@APP.route('/delete_confirm/<sub_id>/<type>')
def delete_confirm(sub_id, type):
    # Checking if the user is logged in and has admin so is therefore able to access this action
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Setting values for the edit log before they are deleted
    edited_id = sub_id
    edit = "Deleted"
    # Creating a connection to the main database
    con = create_connection(DATABASE)
    cur = con.cursor()
    # Checking if the subject is a category/level
    if type == "C" or type == "L":
        # Setting more edit log values
        edited_type = "Lev_Cat"
        log_edit(edited_id, edited_type, edit)

        # Deleting the categories
        query = "DELETE FROM categories WHERE id = ?"
        cur.execute(query, (sub_id,))
        con.commit()

        # Deleting all the words within the categories
        query = "SELECT id FROM words WHERE category = ? OR level = ?"
        cur.execute(query, (sub_id, sub_id,))
        word_list = cur.fetchall()
        for i in range(len(word_list)):
            query = "DELETE FROM words WHERE id = ?"
            cur.execute(query, ( word_list[i] ))
            con.commit()

    # Deleting the word if it is a word
    elif type == "word":
        edited_type = "Word"
        log_edit(edited_id, edited_type, edit)
        query = "DELETE FROM words WHERE id = ?"
        cur.execute(query, (sub_id, ))
        con.commit()

    # Closing the connection and redirecting to the admin page
    con.close()
    return redirect('/admin')

# This function adds words
@APP.route('/add_word', methods=['GET', 'POST'])
def add_word():
    # Checking if the user is logged in and has admin so is therefore able to access this action
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    if request.method == "POST":
        # Getting all user input values from HTML
        m_tans = request.form.get('m_trans').lower().strip()
        e_trans = request.form.get('e_trans').lower().strip()
        word_def = request.form.get('word_def').lower().strip()
        w_cat = request.form.get('w_cat')
        w_lev = request.form.get('w_lev')
        word_img = request.form.get('word_img')

        # Creating a connection to the main database and adding word to wordlist
        con = create_connection(DATABASE)
        query = "INSERT INTO words  ('eng_word', 'category', 'definition', 'level', 'mri_word', 'image')" \
                " VALUES (?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_tans, word_img,))
        con.commit()

        # Setting values for edit log and adding them to the edit log
        query = "SELECT MAX(id) FROM words"
        cur.execute(query, )
        edited_id = cur.fetchall()[0][0]
        # Closing the connection
        con.close()
        edited_type = "Word"
        edit = "Added"
        log_edit(edited_id, edited_type, edit)
        return redirect('/admin')

# This function/route loads the edit/delete word page with all nessisary information
@APP.route('/edit_delete_word', methods=['POST'])
def edit_delete_word():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Fetching all necessary information to display on the edit/delete page and to delete the word
    if request.method == "POST":
        category = request.form.get('e_d_word_cat')
        # Creating a connection to the main database
        con = create_connection(DATABASE)
        # Word info
        query = "SELECT mri_word, eng_word, definition, category, level, id FROM words WHERE category=? OR level=?"
        cur = con.cursor()
        cur.execute(query, (category, category,))
        word_list = cur.fetchall()

        # Category/level info for category/level list
        query = 'SELECT id, title, type FROM categories'
        cur = con.cursor()
        cur.execute(query)
        category_list = cur.fetchall()
        # Closing the connection
        con.close()
        return render_template("edit_delete_word.html", word_list=word_list, categories=category_list,
                               logged_in=is_logged_in()[0], perms = is_logged_in()[1],
                               cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'))
    return redirect('/admin')

# This function loads the page to confirm the deletion with all the nessisary infomation
@APP.route('/delete_word', methods=['POST'])
def render_delete_word():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Getting info to display on the delete confirmation page
    if request.method == "POST":
        word = request.form.get('word')
        word = word.split(', ')
        word_id = word[0]
        word_name = word[1]+'/'+word[2]
        # Rendering the deletion confirmation page
        return render_template("delete_confirm.html", sub_id=word_id, name=word_name, type="word")
    return redirect('/admin')

# This function loads the page to confirm editing of words with all nessisary infomation
@APP.route('/edit_word', methods=['POST'])
def render_edit_word():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    if request.method == "POST":
        # Getting required infomation for the edit of the word and the edit confirmation page
        m_trans = request.form.get('m_trans').lower().strip()
        e_trans = request.form.get('e_trans').lower().strip()
        word_def = request.form.get('word_def').lower().strip()
        w_cat = request.form.get('w_cat')
        w_lev = request.form.get('w_lev')
        word = request.form.get('word')
        word = word.split(', ')
        word_id = word[0]
        word_name = word[1]+'/'+word[2]
        # Rendering the edit confirm page
        return render_template("edit_confirm.html", sub_id=word_id, e_trans=e_trans, w_cat=w_cat, word_def=word_def,
                               w_lev=w_lev, m_trans=m_trans, word_name=word_name, sub_type="word")
    return redirect('/admin')

# Editing of words
@APP.route('/edit_confirm/<sub_id>/<e_trans>+<w_cat>+<word_def>+<w_lev>+<m_trans>')
def edit_confirm(sub_id, e_trans, w_cat, word_def, w_lev, m_trans):
    # Checking if the user is logged in and has admin so is therefore able to access this action
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Creating a connection to the main database and performing the edit
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "UPDATE words SET eng_word = ?, category = ?, definition = ?, level = ?, mri_word = ? WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (e_trans, w_cat, word_def, w_lev, m_trans, sub_id ))
    # Comitting the changes
    con.commit()
    # Closing the connection
    con.close()

    # Setting values for edit log
    edited_id = sub_id
    edited_type = "Word"
    edit = "Edited"
    log_edit(edited_id, edited_type, edit)

    return redirect('/admin')

# This function loads the page to confirm editing of categories with all nessisary infomation
@APP.route('/edit_category', methods=['POST'])
def render_edit_category():
    # Checking if the user is logged in and has admin so is therefore able to access this page
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    if request.method == "POST":
        # Getting category information
        e_cat = request.form.get('edited_category')
        e_title = request.form.get('cat_title').title().strip()
        cat_def = request.form.get('cat_def').title().strip()
        cat_lev = request.form.get('edited_cat_lev')

        # Rendering the edit confirmation page
        return render_template("edit_confirm.html", sub_id=e_cat, e_title=e_title, cat_def=cat_def, cat_lev=cat_lev,
                               sub_type="cat")
    return redirect('/admin')

# Editing of Categories
@APP.route('/edit_confirm_cat/<sub_id>/<e_title>+<cat_def>+<cat_lev>')
def edit_confirm_cat(sub_id, e_title, cat_def, cat_lev):
    # Checking if the user is logged in and has admin so is therefore able to access this action
    if not is_logged_in()[0]:
        return redirect('/?message=Need+to+be+logged+in')
    if is_logged_in()[1] != "admin":
        return redirect('/?message=Need+Admin+permissions')

    # Creating a connection to the main database and updating/editing the words
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "UPDATE categories SET title = ?, description = ?, type = ? WHERE id = ?"
    cur = con.cursor()
    cur.execute(query, (e_title, cat_def, cat_lev, sub_id ))
    # Comiting the change
    con.commit()
    # Closing the connection
    con.close()

    # Setting values for the edit log
    edited_id = sub_id
    edited_type = "Lev_Cat"
    edit = "Edited"
    log_edit(edited_id, edited_type, edit)
    return redirect('/admin')

# This function loads a word's individule page
@APP.route('/word_page/<word_id>')
def render_word_page(word_id):
    # Creating a connection to the main database
    con = create_connection(DATABASE)
    cur = con.cursor()

    # Getting word information
    query = "SELECT mri_word, eng_word, definition, category, level, image, id FROM words WHERE id = ?"
    cur.execute(query, (word_id,))
    word_list = cur.fetchall()

    # Getting category information
    query = "SELECT title, description FROM categories WHERE id =? "
    cur.execute(query, (word_list[0][3],))
    cat_info = cur.fetchall()[0]
    cur.execute(query, (word_list[0][4],))
    lev_info = cur.fetchall()[0]

    # Getting edit log
    if is_logged_in()[1] == "admin":
        query = "SELECT edited_id, edited_type, edit, editor_id, date_time, editor_name, edited_title FROM edit_log " \
                "WHERE edited_id=? or edited_id=? or edited_id=?"
        cur.execute(query, (word_id, word_list[0][3], word_list[0][4]))
        edit_list = cur.fetchall()
    else:
        edit_list = []

    # Closing the connection
    con.close()
    # Rendering the page
    return render_template('word_page.html', cat_list=render_cat_lev_menus('C'), lev_list=render_cat_lev_menus('L'),
                           logged_in=is_logged_in()[0], perms=is_logged_in()[1], word_list=word_list, cat_info=cat_info,
                           lev_info=lev_info, edit_list=edit_list)

# Running the website
APP.run(host='0.0.0.0', debug=True)
