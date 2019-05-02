from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from wtforms import Form, StringField, validators
from flask_mysqldb import MySQL
from form import RegistrationForm, LoginForm
from functools import wraps
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'this_is_a_secret_key'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'smh23813456'
app.config['MYSQL_DB'] = 'vote_system'

mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT game_name, game_description, Votes FROM game_title order by Votes DESC')
    data = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT log_time FROM log order by log_id DESC limit 1')
    data1 = cur.fetchall()
    cur.close()
    return render_template('index.html', title=data, time=data1)


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    form = LoginForm(request.form)
    if request.method == 'POST':
        useaccount = request.form['email']
        password = str(request.form['password'])

        if useaccount == "admin" and password == "admin123" and request.form['admin_log_in'] == 'admin':
            session['log_in'] = True
            session['admin_log_in'] = True
            session['user'] = "admin"
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO log (log_usr_account, log_game_name, log_time) "
                        "VALUES(%s, %s, %s)",
                        (useaccount, "log in", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            mysql.connection.commit()
            return redirect(url_for('admin'))

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
                session['user'] = useaccount
                cur.execute("INSERT INTO log (log_usr_account, log_game_name, log_time) "
                            "VALUES(%s, %s, %s)",
                            (useaccount, "log in", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                mysql.connection.commit()
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


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'log_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in first', 'danger')
            return redirect(url_for('log_in'))
    return wrap


def admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_log_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please log in as administrator first', 'danger')
            return redirect(url_for('log_in'))
    return wrap


@app.route('/log-out')
def logout():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM voted_game")
    mysql.connection.commit()
    cur.close()

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
        check = cur.execute("SELECT * FROM usr_table WHERE usr_account = %s", [email])
        if check > 0:
            flash(f'account is used', 'danger')
            return redirect(url_for('sign_up'))
        else:
            cur.execute("INSERT INTO usr_table(usr_account, usr_password, usr_usrname) "
                    "VALUES(%s, %s, %s)",
                    (email, password, username))

            # commit and close connection
            mysql.connection.commit()
            cur.close()
            flash(f'account for {form.username.data} are created', 'success')
            if 'admin_log_in' in session:
                return redirect(url_for('admin'))
            return redirect(url_for('log_in'))

    return render_template("sign-up.html", form=form)


class NewVoteForm(Form):
    title = StringField('title', [validators.Length(min=1, max=50)])
    description = StringField('description', [validators.Length(min=1, max=100)])


@app.route('/New_vote', methods=['GET', 'POST', 'DELETE'])
@is_logged_in
def create():
    form = NewVoteForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data
        init_votes = 0

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT game_name from game_title where game_name='%s'" % title)
        # mysql.connection.commit()
        if cursor.rowcount == 1:
            return redirect(url_for('create'))
        cursor.close()

        # Connect to sql and insert values
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO game_title(game_name, game_description, user, Votes) "
                    "VALUES(%s, %s, %s, %s)",
                    (title, description, session['user'], int(init_votes)))

        # commit and close connection
        mysql.connection.commit()
        cur.close()

        flash(f'topic {form.title.data} were created', 'success')
        if 'admin_log_in' in session:
            return redirect(url_for('admin'))
        return redirect(url_for('index'))
    return render_template('New-vote.html', form=form)


@app.route('/addVote', methods=['POST'])
def addVote():
    title = request.form.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT game_name from voted_game where game_name='%s'" % title)
    # mysql.connection.commit()
    if cursor.rowcount == 1:
        return
    cursor.close()

    cur = mysql.connection.cursor()
    cur.execute("UPDATE game_title SET Votes=Votes+1 WHERE game_name='%s'" % title)
    cur.execute("INSERT INTO voted_game(game_name) VALUES('%s')" % title)
    cur.execute("INSERT INTO log (log_usr_account, log_game_name, log_time) "
                "VALUES(%s, %s, %s)",
                (session['user'], title, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # commit and close connection
    mysql.connection.commit()
    cur.close()
    return 'success'


@app.route('/intro')
def intro():
    return render_template('introduction.html')


@app.route('/edit_topics', methods=['POST'])
def edit_topics():
    title = request.form['title']
    game_name = request.form['game_name']
    game_description = request.form['game_description']
    tickets = request.form['tickets']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE game_title SET game_name=%s, game_description=%s, Votes=%s WHERE game_name=%s", (game_name,
                                                                                     game_description, tickets, title))
    mysql.connection.commit()
    cur.close()

    return 'success'


@app.route('/delete_topics/<string:name>', methods=['POST'])
@is_logged_in
def delete_topics(name):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM game_title WHERE game_title.game_name = %s", [name])
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin'))


@app.route('/delete_users/<string:usraccount>', methods=['POST'])
@is_logged_in
def delete_users(usraccount):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usr_table WHERE usr_table.usr_account = %s", [usraccount])
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin'))


@app.route('/delete_logs/<string:log_array>', methods=['POST'])
@is_logged_in
def delete_logs(log_array):
    log_list = log_array.split(",")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM log WHERE log.log_game_name = %s AND log.log_usr_account = %s AND log_time = %s",
                [log_list[0], log_list[1], log_list[2]])
    if log_list[0] != "log in":
        cur.execute("UPDATE game_title SET Votes=Votes-1 WHERE game_name='%s'" % log_list[0])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('admin'))


@app.route('/admin')
@admin_logged_in
def admin():
    cur = mysql.connection.cursor()
    data = cur.execute('SELECT game_name, game_description, user, Votes FROM game_title order by Votes DESC')
    topics = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    data1 = cur.execute('SELECT usr_usrname, usr_account, usr_password FROM usr_table')
    account = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    data2 = cur.execute('SELECT log_usr_account, log_game_name, log_time FROM log')
    loog = cur.fetchall()
    cur.close()

    if data > 0 and data1 >0 and data2 > 0:
        return render_template('admin.html', topics=topics, account=account, loog=loog)
    elif data > 0 and data1 <= 0 and data2 <=0:
        return render_template('admin.html', topics=topics)
    elif data <= 0 and data2<=0 and data1 > 0:
        return render_template('admin.html', account=account)
    elif data <= 0 and data1 <= 0 and data2 >0:
        return render_template('admin.html', loog=loog)
    elif data > 0 and data1 > 0 and data2 <= 0:
        return render_template('admin.html', topics=topics, account=account)
    elif data > 0 and data1 <= 0 and data2 > 0:
        return render_template('admin.html', topics=topics, loog=loog)
    elif data <= 0 and data1 > 0 and data2 > 0:
        return render_template('admin.html', account=account, loog=loog)
    else:
        return render_template('admin.html')


if __name__ == '__main__':
    app.run()
