from flask import render_template, request, redirect, url_for, flash, session
from project import app, db
from project.database import game_info, user_info, voted_info, log
from wtforms import Form, StringField, validators
from project.form import RegistrationForm, LoginForm
from functools import wraps
from datetime import datetime


@app.route('/')
def index():
    data = game_info.query.all()
    data1 = log.query.all()
    if len(data1) != 0:
        time = data1[-1].time
    else:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', title=data, time=time)


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    form = LoginForm(request.form)
    if request.method == 'POST':
        usraccount = request.form['email']
        password = str(request.form['password'])
        Admin = request.form.get('admin_log_in')

        if usraccount == "admin" and password == "admin123":
            if(Admin == 'admin'):
                session['log_in'] = True
                session['admin_log_in'] = True
                session['user'] = "admin"

                new_log = log(user_account=usraccount, game_name="log in", time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.session.add(new_log)
                db.session.commit()
                return redirect(url_for('admin'))

            flash('dont forget that checkbox', 'danger')
            return render_template('log_in.html', form=form)

        if Admin == 'admin':
            if usraccount != "admin":
                flash("not an admin account", 'danger')
                return render_template('log_in.html', form=form)
            if password != "admin123":
                flash("admin password not correct", "danger")
                return render_template('log_in.html', form=form)

        result = user_info.query.filter_by(user_account=usraccount).first()
        if result:
            REALpassword = result.user_password
            if REALpassword == password:
                app.logger.info('right password')
                session['log_in'] = True
                session['user'] = usraccount

                new_log = log(user_account=usraccount, game_name="log in", time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.session.add(new_log)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                flash(f'this password is not correct', 'danger')
            # cur.close()
        else:
            # cur.close()
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

    # delete = voted_info.query.all()
    # if len(delete) != 0:
    db.session.query(voted_info).delete()
    db.session.commit()

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

        check = user_info.query.filter_by(user_account=email)
        check = db.session.query(check.exists()).scalar()
        # Connect to sql and insert values
        # cur = mysql.connection.cursor()
        # check = cur.execute("SELECT * FROM usr_table WHERE usr_account = %s", [email])

        if check is True:
            flash(f'account is used', 'danger')
            return redirect(url_for('sign_up'))
        else:

            new_user = user_info(user_account=email, user_password=password, user_name=username)
            db.session.add(new_user)
            db.session.commit()

            # cur.execute("INSERT INTO usr_table(usr_account, usr_password, usr_usrname) "
            #         "VALUES(%s, %s, %s)",
            #         (email, password, username))

            # commit and close connection
            # mysql.connection.commit()
            # cur.close()
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
        game_name = form.title.data
        description = form.description.data
        init_votes = 0

        game_name_list = game_info.query.filter_by(game_name=game_name)
        check = db.session.query(game_name_list.exists()).scalar()
        # mysql.connection.commit()
        if check is True:
            flash(f'game exits', 'danger')
            return redirect(url_for('create'))

        new_game = game_info(game_name=game_name, game_description=description, user=session['user'], Tickets=init_votes)
        db.session.add(new_game)
        db.session.commit()

        flash(f'topic {form.title.data} were created', 'success')
        if 'admin_log_in' in session:
            return redirect(url_for('admin'))
        return redirect(url_for('index'))
    return render_template('New-vote.html', form=form)


@app.route('/addVote', methods=['POST'])
def addVote():
    game_name = request.form.get('id')

    game_name_list = voted_info.query.filter_by(game_name=game_name)
    check = db.session.query(game_name_list.exists()).scalar()
    if check is True:
        return

    update = game_info.query.filter_by(game_name=game_name).first()
    update.Tickets += 1

    voted_game = voted_info(game_name=game_name)

    log_info = log(user_account=session['user'],game_name=game_name,time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.add(voted_game)
    db.session.add(log_info)
    db.session.commit()

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

    update = game_info.query.filter_by(game_name=title).first()
    update.game_name = game_name
    update.game_description = game_description
    update.Tickets = tickets
    db.session.commit()

    return 'success'


@app.route('/delete_topics/<string:name>', methods=['POST'])
@is_logged_in
def delete_topics(name):

    delete = game_info.query.filter_by(game_name=name).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/delete_users/<string:usraccount>', methods=['POST'])
@is_logged_in
def delete_users(usraccount):

    delete = user_info.query.filter_by(user_account=usraccount).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/delete_logs/<string:log_array>', methods=['POST'])
@is_logged_in
def delete_logs(log_array):
    log_list = log_array.split(",")
    delete = log.query.filter_by(game_name=log_list[1], user_account=log_list[0], time=log_list[2]).first()
    db.session.delete(delete)

    if log_list[1] != "log in":
        update = game_info.query.filter_by(game_name=log_list[1]).first()
        # check = db.session.query(update.exists()).scalar()
        if update is not None and update.Tickets>0:
            update.Tickets -= 1
        db.session.commit()

    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin')
@admin_logged_in
def admin():

    data = game_info.query.all()
    data1 = user_info.query.all()
    data2 = log.query.all()

    if len(data) > 0 and len(data1) >0 and len(data2) > 0:
        return render_template('admin.html', topics=data, account=data1, loog=data2)
    elif len(data) > 0 and len(data1) <= 0 and len(data2) <=0:
        return render_template('admin.html', topics=data)
    elif len(data) <= 0 and len(data2)<=0 and len(data1) > 0:
        return render_template('admin.html', account=data1)
    elif len(data) <= 0 and len(data1) <= 0 and len(data2) >0:
        return render_template('admin.html', loog=data2)
    elif len(data) > 0 and len(data1) > 0 and len(data2) <= 0:
        return render_template('admin.html', topics=data, account=data1)
    elif len(data) > 0 and len(data1) <= 0 and len(data2) > 0:
        return render_template('admin.html', topics=data, loog=data2)
    elif len(data) <= 0 and len(data1) > 0 and len(data2) > 0:
        return render_template('admin.html', account=data1, loog=data2)
    else:
        return render_template('admin.html')

