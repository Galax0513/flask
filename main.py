import json
import threading
import socket
from time import sleep

from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from turbo_flask import Turbo
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
#from settings import SERVER_HOST, SERVER_PORT, SERVER_PORT_WEB
from data.api import GetPos

from data import db_session
from data.blog_post import Posts
from forms.forms import RegisterForm as UserForm, LoginForm, RegisterForm, PostForm
#from settings import SERVER_HOST, SERVER_PORT
from data.stats import Stats
from data.users import User
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
#sock.connect((SERVER_HOST, int(SERVER_PORT)))
api = Api(app)
api.add_resource(GetPos, '/api/getpos')
turbo = Turbo(app)


def main():
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash("Login Succesfull!")
                return redirect(url_for('dashboard'))
            else:
                # flash("Wrong Login or Password - Try Again!")
                return render_template('login2.html',
                                       message="Неправильный логин или пароль!",
                                       form=form)
        return render_template('login2.html', title='Авторизация', form=form)

    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():

        form = UserForm()
        id = current_user.id
        name_to_update = db_sess.query(User).get(id)
        # добавляем с формы в ьазу данных
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            name_to_update.nickname = request.form['nickname']
            try:
                db_sess.commit()
                flash("User Updated")
                return render_template("dashboard.html", form=form,
                                       name_to_update=name_to_update)
            except:
                flash("Error! Looks like there was a problem... Try again!")
                return render_template("dashboard.html", form=form,
                                       name_to_update=name_to_update)
        else:
            return render_template("dashboard.html", form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        return render_template('dashboard.html')

    @login_manager.user_loader
    def load_user(user_id):
        return db_sess.query(User).get(user_id)

    @app.route("/info")
    def info():
        return render_template("information.html")

    @app.before_first_request
    def before_first_request():
        threading.Thread(target=update_load).start()

    def inject_load():
        try:
            sock.send(json.dumps({'info': None}).encode())
            info = json.loads(sock.recv(2 ** 20).decode())
            for i in range(len(info)):
                deaths = 1 if info[i][2]['deaths'] == 0 else info[i][2]['deaths']
                info[i][2]['KD'] = round(info[i][2]['kills'] / deaths, 2)
                info[i][2]['damage'] = round(info[i][2]['damage'], 2)
                user = db_sess.query(User).filter(User.email == info[i][0]).first()
                info[i].append(user.id)
        except Exception:
            info = []
        return info

    def update_load():
        with app.app_context():
            while True:
                # inject_load()
                turbo.push(turbo.replace(render_template('loadvg.html', info=inject_load()), 'load'))
                sleep(0.4)


    class PasswordForm(FlaskForm):
        email = StringField("What's Your Email", validators=[DataRequired()])
        password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
        submit = SubmitField('Submit')


    @app.route('/posts')
    def posts():
        db_sess = db_session.create_session()
        # Grab all the posts from the database
        posts = db_sess.query(Posts).order_by(Posts.date_posted)

        return render_template("posts.html",
                               posts=posts)

    # Add Post Page
    @app.route('/add-post', methods=['GET', 'POST'])
    def add_post():
        form = PostForm()

        if form.validate_on_submit():
            poster = current_user.id

            post = Posts(title=form.title.data, content=form.content.data, slug=form.slug.data, place=form.place.data,
                         poster_id=poster)
            # Clear The Form
            form.title.data = ''
            form.content.data = ''
            form.slug.data = ''
            form.place.data = ''

            # Add post data to database
            db_sess.add(post)
            db_sess.commit()

            # Return a Message
            flash("Blog Post Submitted Successfully!")

        # Redirect to the webpage
        return render_template("add_post.html", form=form)


    # возвращает обратно к посту
    @app.route('/posts/<int:id>')
    def post(id):
        post = db_sess.query(Posts).get(id)
        return render_template('post.html', post=post)

    @app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
    def edit_post(id):
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).get(id)
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.slug = form.slug.data
            post.content = form.content.data
            db_sess.add(post)
            db_sess.commit()
            flash("Post has been updated")
            return redirect(url_for('post', id=post.id))
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)

    # Delete Post
    @app.route('/post/delete/<int:id>')
    @login_required
    def delete_post(id):
        db_sess = db_session.create_session()
        post_to_delete = db_sess.query(Posts).get(id)
        id = current_user.id
        if id == post_to_delete.poster.id:
            try:
                db_sess.delete(post_to_delete)
                db_sess.commit()
                flash("Blog Post was deleted!")
                posts = db_sess.query(Posts).order_by(Posts.date_posted)
                return render_template("posts.html",
                                       posts=posts, id=id)

            except:
                posts = db_sess.query(Posts).order_by(Posts.date_posted)
                flash("WHoops! There was a problem... Try again")
                return render_template("posts.html",
                                       posts=posts, id=id)
        else:
            flash("You dumb beach!")
            posts = db_sess.query(Posts).order_by(Posts.date_posted)
            return render_template("posts.html",
                                   posts=posts, id=id)

    @app.route('/delete/<int:id>')
    def delete(id):
        db_sess = db_session.create_session()
        form = UserForm()
        name = None
        user_to_delete = db_sess.query(User).get(id)
        try:
            db_sess.delete(user_to_delete)
            db_sess.commit()
            flash("User Deleted")
            our_users = db_sess.query(User).order_by(User.date_added)
            return render_template("add_user.html", form=form, name=name,
                                   our_users=our_users)
        except:
            our_users = db_sess.query(User).order_by(User.date_added)
            flash("Error! Looks like there was a problem... Try again!")
            return render_template("add_user.html", form=form, name=name,
                                   our_users=our_users)

    # Update Database Record
    @app.route('/update/<int:id>', methods=['GET', 'POST'])
    def update(id):
        db_sess = db_session.create_session()
        form = UserForm()
        name_to_update = db_sess.query(User).get(id)
        # добавляем с формы в ьазу данных
        if request.method == "POST":
            name_to_update.name = request.form['name']
            name_to_update.email = request.form['email']
            name_to_update.nickname = request.form['nickname']
            try:
                db_sess.commit()
                flash("User Updated")
                return render_template("update.html", form=form,
                                       name_to_update=name_to_update)
            except:
                flash("Error! Looks like there was a problem... Try again!")
                return render_template("update.html", form=form,
                                       name_to_update=name_to_update)
        else:
            return render_template("update.html", form=form,
                                   name_to_update=name_to_update,
                                   id=id)

    @app.route('/user/add', methods=['GET', 'POST'])
    def add_user():
        name = None
        form = UserForm()
        if form.validate_on_submit():
            user = db_sess.query(User).filter_by(email=form.email.data).first()
            if user is None:
                # Hash the password!
                hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
                user = User(name=form.name.data, email=form.email.data,
                            password_hash=hashed_pw, nickname=form.nickname.data)
                db_sess.add(user)
                stat = Stats(player_mail=form.email.data, kills=0, deaths=0, damage=0, hits=0, rik=0, fires=0)
                db_sess.add(stat)
                db_sess.commit()
            name = form.name.data
            form.name.data = ''
            form.nickname.data = ''
            form.email.data = ''
            form.password_hash.data = ''
            flash("User Added Successfully")
        our_users = db_sess.query(User).order_by(User.date_added)
        return render_template("add_user.html", form=form, name=name,
                               our_users=our_users)


    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Никнейм уже занят")
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                age=int(form.age.data),
                email=form.email.data,
                nickname=form.nickname.data)
            stat = Stats(player_mail=form.email.data, kills=0, deaths=0, damage=0, hits=0, rik=0, fires=0)
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.add(stat)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route("/")
    @app.route("/players")
    def index():
        return render_template("players.html")

    @app.route("/player/<int:id>")
    def player(id):
        user = db_sess.query(User).filter(User.id == id).first()
        stat = db_sess.query(Stats).filter(Stats.player_mail == user.email).first()
        deaths = 1 if stat.deaths == 0 else stat.deaths
        kd = round(stat.kills / deaths, 2)
        return render_template("player.html", stat=stat, kd=kd, user=user)

    @app.route('/user/<name>')
    def user(name):
        return render_template("user.html", user_name=name)

    # Create Custom Error Pages

    # Invalid URl
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"), 500


    # Create Password Test Page
    @app.route('/test_pw', methods=['GET', 'POST'])
    def test_pw():
        email = None
        password = None
        pw_to_check = None
        passed = None
        form = PasswordForm()
        db_sess = db_session.create_session()
        # validate Form
        if form.validate_on_submit():
            email = form.email.data
            password = form.password_hash.data
            # Clear the form
            form.email.data = ''
            form.password_hash.data = ''

            # Lookup User By Email Address
            pw_to_check = db_sess.query(User).filter_by(email=email).first()

            # Check Hashed Password
            passed = check_password_hash(pw_to_check.password_hash, password)

            # flash("Form Submitted Successfully")
        return render_template("test_pw.html",
                               email=email,
                               password=password,
                               pw_to_check=pw_to_check,
                               passed=passed,
                               form=form)

    app.run(port=5001)
    # app.run(host=SERVER_HOST, port=int(SERVER_PORT_WEB))


if __name__ == '__main__':
    main()
