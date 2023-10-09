from flask import Flask, render_template,session, redirect, url_for, request, flash
import psycopg2
import psycopg2.extras
import re  #regular expression
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = 'mysecretkey'

#adding database parameters
db_params = {
    'dbname': 'project2',
    'user': 'postgres',
    'password': '*Shivangi123',
    'host': 'localhost',  # Change this if your database is running on a different host
    'port': '5432',       # Change this if your PostgreSQL port is different
}

conn = psycopg2.connect(**db_params)

@app.route('/', methods = ['GET','POST'])
def home():
    return render_template("home.html")


#***************************************************LOGIN*************************************************
@app.route('/login', methods = ['GET','POST'])
def login():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cur.execute('SELECT * FROM usertable WHERE username = %s',(username,))
        account = cur.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)

            # If account exists in users table in out database
            if check_password_hash(password_rs,password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['username'] = account['username']

                return redirect(url_for('profile'))
            else :
                #account doesn't exist or username/password is incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    cur.close()
    return render_template('login.html')

@app.route('/newrecipe', methods = ['GET','POST'])
def newentry():

    #checking if the user is trying to fill form without logging in
    if not session['username']:
        return redirect(url_for('login'))

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        recipename = request.form['recipename']
        ingredients = request.form['ingredients']
        diet = request.form['diet']
        servings = request.form['servings']
        instructions = request.form['instructions']
        course = request.form['course']
        cuisine = request.form['cuisine']
        cookingtime = request.form['cookingtime']
        preptime = request.form['preptime']
        link = request.form['link']
        totaltime = int(preptime) + int(cookingtime)
        username = session['username']

        # print(username)
        cur.execute("""Insert into Recipetable ("RecipeName","Ingredients","PrepTimeInMins",
                     "CookTimeInMins","TotalTimeInMins","Servings",
                    "Cuisine","Course","Diet","Instructions",
                    "URL","AuthorId") VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s) """,
                    (recipename, ingredients, preptime,cookingtime,totaltime,servings, cuisine, course, diet, instructions, link, username))
        
        conn.commit()
        cur.close()
      
        flash("You have successfully added your new recipe here")
        redirect(url_for('profile'))

        # print(totaltime)
       
    return render_template('newrecipe.html')


#***************************************************REGISTER***********************************************************
@app.route('/register',methods=['GET','POST'])
def register():
    # # Establish a connection to the PostgreSQL database
    # conn = psycopg2.connect(**db_params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    

    #user submitted form
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)

        #Check if account exists using MySQL
        cur.execute("select * from usertable where username = %s", (username,))
        account  = cur.fetchone()
        print(account)
        # If account exists show error and validation checks

        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cur.execute("INSERT INTO usertable (name, email, username, password) VALUES (%s, %s, %s, %s)", (name,email,username, _hashed_password))
            conn.commit()
            cur.close()
            flash('You have successfully registered!!!')
            return redirect(url_for('login'))
  
     
    elif request.method == 'POST':
        #form is empty 
        flash('Please fill out the form')

        cur.close()
        # conn.close()

        # if account:
        #     session['account_info'] = username 
        #     # return redirect(url_for(""))
        # else:
        #     return "Login failed!"

    return render_template('register.html')


@app.route('/profile',methods = ['GET','POST'])
def profile():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('select "RecipeId","RecipeName","AuthorId","Servings"  from recipetable order by random() limit 9;')
    topresult = cur.fetchall()
    # print(topresult)
    cur.close()
    # recipeids = [i[0] for i in topresult]
    # ['recipeid': (authorid, serving)]
    # data = [{i[0]:(i[1],i[2])} for i in topresult]
    data = [[i[0],i[1],i[2]] for i in topresult]
    
    for i in data:
        print(i)

    # data = ['recipeid' = {''}]

    return render_template('profile.html',data = data)


# url_for('recipe',id = jaha se call hoga waha ka variable)
@app.route('/recipe/<id>',methods=['GET','POST'])
def recipe(id):

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('select *  from recipetable where "RecipeId" = %s', (id,))
    data = cur.fetchone()
    print(data)
    cur.close()

    return render_template('recipe.html',data = data)




if __name__ == '__main__':
    app.run(debug=True)