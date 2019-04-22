from flask import Flask, render_template, request, redirect, url_for, flash, session
from wtforms import Form, StringField, validators
from flask_mysqldb import MySQL
from form import RegistrationForm, LoginForm


app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_a_secret_key'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Gfj123456'
app.config['MYSQL_DB'] = 'vote_system'

mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT game_name, game_description FROM game_title order by Votes DESC')
    data = cur.fetchall()
    return render_template('index.html', title=data)


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    form = LoginForm(request.form)
    if request.method == 'POST':
        useaccount = request.form['email']
        password = str(request.form['password'])

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM usr_table WHERE usr_account = %s", [useaccount])

        if result > 0:
            # data = cur.fetchone()
            # REALpassword = data['usr_password']
            result = cur.fetchall()
            REALpassword = result[0][2]

            if REALpassword == password:
                app.logger.info('right password')
                session['log_in'] = True

                return redirect(url_for('index'))
            else:
                flash(f'this password is not correct', 'danger')
            cur.close()
        else:
            cur.close()
            app.logger.info('invalid account')
            flash(f'this account is invalid', 'danger')
            return render_template('log_in.html', form=form)

    return render_template('log_in.html', form=form)


@app.route('/log-out')
def logout():
    session.clear()
    flash(f'log out safely', 'success')
    return redirect(url_for('index'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        email = form.email.data

        # Connect to sql and insert values
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usr_table(usr_account, usr_password, usr_usrname) "
                    "VALUES(%s, %s, %s)",
                    (email, password, username))

        # commit and close connection
        mysql.connection.commit()
        cur.close()

        flash(f'account for {form.username.data} are created', 'success')
        return redirect(url_for('log_in'))
    return render_template("sign-up.html", form=form)


class NewVoteForm(Form):
    title = StringField('title', [validators.Length(min=1, max=50)])
    description = StringField('description', [validators.Length(min=1, max=50)])


@app.route('/New_vote', methods=['GET', 'POST', 'DELETE'])
def create():
    form = NewVoteForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        init_votes = 0

        # Connect to sql and insert values
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO game_title(game_name, game_description, Votes) "
                    "VALUES(%s, %s, %s)",
                    (title, description, int(init_votes)))

        # commit and close connection
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))
    return render_template('New-vote.html', form=form)


@app.route('/addVote', methods=['POST'])
def addVote():
    title = request.form.get('id')
    cur = mysql.connection.cursor()

    cur.execute("UPDATE game_title SET Votes=Votes+1 WHERE game_name='%s'" % title)

    # commit and close connection
    mysql.connection.commit()
    cur.close()

    return


# @app.route('/rank', methods=['POST', 'GET'])
# def rank():
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM game_title order by Votes DESC')
#     data = cur.fetchall()
#

if __name__ == '__main__':
    app.run(debug=True)
