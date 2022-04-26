import datetime
import json
import threading
import socket
from time import sleep
import requests
from flask import Flask, render_template, flash, request, redirect, url_for
from turbo_flask import Turbo
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from settings import SERVER_HOST, SERVER_PORT, SERVER_PORT_WEB
from data.api.api import GetPos, PostsResource, PostsListResource, UsersListResource, UsersResource, StatsResource, \
    StatsListResource
from data.Sql import db_session
from data.Models.blog_post import Posts
from data.Forms.SearchForm import SearchForm
from data.Forms.EditPostForm import EditPostForm
from data.Forms.PostForm import PostForm
from data.Forms.LoginForm import LoginForm
from data.Forms.PasswordForm import PasswordForm
from data.Forms.RegisterForm import RegisterForm
from data.Forms.DeleteProfileForm import DeleteProfileForm
from data.Forms.UpdateUserForm import UpdateUserForm
from settings import SERVER_HOST, SERVER_PORT
from data.Models.stats import Stats
from data.Models.users import User
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config["UPLOAD_FOLDER"] = r"static/posts_files/"
app.config["ALLOWED_FILE_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif", "mp4", "avi", "mov"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect((SERVER_HOST, int(SERVER_PORT)))

api = Api(app)
api.add_resource(GetPos, '/api/getpos')
api.add_resource(PostsResource, '/api/posts/<int:post_id>')
api.add_resource(PostsListResource, '/api/posts')
api.add_resource(UsersResource, '/api/users/<int:user_id>')
api.add_resource(UsersListResource, '/api/users')
api.add_resource(StatsResource, '/api/stats/<int:user_id>')
api.add_resource(StatsListResource, '/api/stats')
turbo = Turbo(app)

db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()


@app.errorhandler(401)
def login_error(error):
    return render_template('error.html', error="Недоступно для незарегистрированных пользователей")


@app.route("/map")
@login_required
def map():
    pixels_d = 2.858532
    pixels_sh = 5.78852867
    ll = [99.012606, 64.186239]  # координаты России
    data, data_marks = [], []
    for object in db_sess.query(Posts).all():
        try:
            data_marks.append(f"{object.coords.split(',')[0]},{object.coords.split(',')[1]}" + ',comma')
            coords = [object.id, [float(el) for el in object.coords.split(',')]]
            data.append(
                [coords[0], [225 + (ll[1] - coords[1][1]) * pixels_sh, 325 - (ll[0] - coords[1][0]) * pixels_d]])
        except Exception:
            pass
    map_request = "http://static-maps.yandex.ru/1.x"
    response = requests.get(map_request, params={"size": "650,450",
                                                 'll': f'{ll[0]},{ll[1]}',
                                                 'spn': '35,35',
                                                 'l': 'map',
                                                 'pt': '~'.join(data_marks),
                                                 'scale': '1',
                                                 "apikey": "40d1649f-0493-4b70-98ba-98533de7710b"}
                            )
    map_file = "static/map/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    print(data)
    return render_template("map.html", data=data)


@app.route("/map_new")
@login_required
def map_new():
    return render_template("test_map_java.html", posts=db_sess.query(Posts).all(), size=['100%', "600px"],
                           zoom=2, center=[55.76, 37.64])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # flash("Login Succesfull!")
            return redirect(url_for('dashboard', delete_user=0))
        else:
            # flash("Wrong Login or Password - Try Again!")
            return render_template('login2.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template('login2.html', title='Авторизация', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard/<int:delete_user>', methods=['GET', 'POST'])
@login_required
def dashboard(delete_user):
    form1 = UpdateUserForm()
    form2 = DeleteProfileForm()
    id = current_user.id
    name_to_update = db_sess.query(User).get(id)
    # добавляем с формы в ьазу данных
    if form1.validate_on_submit():
        name_to_update.name = form1.name.data
        name_to_update.email = form1.email.data
        name_to_update.nickname = form1.nickname.data
        name_to_update.surname = form1.surname.data
        try:
            db_sess.commit()
            # flash("User Updated")
            return render_template("dashboard.html", form=form1,
                                   name_to_update=name_to_update, message="User Updated")
        except:
            flash("Error! Looks like there was a problem... Try again!")
            return render_template("dashboard.html", form=form1,
                                   name_to_update=name_to_update, message="Error! Looks like there was a problem... Try again!")
    elif user and form2.validate_on_submit():
        if form2.password.data == form2.password_again.data:
            return redirect(f"/delete/{current_user.id}")
        else:
            # flash("Пароли не совпадают")
            return render_template("dashboard.html", form=form1, form2=form2,
                                   name_to_update=name_to_update,
                                   message="Пароли не совпадают")
    else:
        if delete_user:
            return render_template("dashboard.html", form=form1,
                                   name_to_update=name_to_update,
                                   id=id, form2=form2)
        return render_template("dashboard.html", form=form1,
                               name_to_update=name_to_update,
                               id=id)


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
            turbo.push(turbo.replace(render_template('loadvg.html', info=inject_load()), 'load'))
            sleep(0.2)


@app.route('/posts', methods=["GET", "POST"])
def posts():
    posts = db_sess.query(Posts).order_by(Posts.date_posted).all()

    form = SearchForm()
    if form.validate_on_submit():
        posts = db_sess.query(Posts).filter((Posts.title == form.search.data.lower()) |
                                            Posts.title.like(f"%{form.search.data}%")).all()
        if posts:
            return render_template("posts.html",
                                   posts=posts, form=form)
        else:
            pass
            # flash("По данному запросу постов не найдено")
    return render_template("posts.html", posts=posts, form=form)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        from data.api.yandex_api_func import coords
        coords = coords(form.address.data)

        post = Posts(title=form.title.data, content=form.content.data, slug=form.slug.data,
                     poster_id=poster, address=form.address.data, coords=coords)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        file_names = []
        for file in form.files.data:
            if file:
                if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS"]:
                    return render_template(
                        "add_post.html",
                        message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS"])}',
                        form=form
                    )
                file_name = f'{app.config["UPLOAD_FOLDER"]}{datetime.datetime.now().date()}_{current_user.id}.{file.filename.split(".")[-1]}'
                file_names.append(file_name)
                file.save(file_name)
        post.files = "|".join(file_names)
        # Add post data to database
        db_sess.add(post)
        db_sess.commit()

        # Return a Message
        # flash("Blog Post Submitted Successfully!")

        return redirect(f"posts/{post.id}")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


# возвращает обратно к посту
@app.route('/posts/<int:id>')
def post(id):
    post = db_sess.query(Posts).get(id)
    if post.coords:
        coords = [float(coord) for coord in post.coords.split(',')][-1::-1]
        print(coords)
    return render_template('post.html', post=post, posts=[post], center=coords, size=["100%", "400px"], zoom=8)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = db_sess.query(Posts).get(id)
    form = EditPostForm()
    if form.validate_on_submit():
        file_names = []
        print(form.images)
        for file in form.images.data:
            if file:
                if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS"]:
                    return render_template(
                        "add_post.html",
                        message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS"])}',
                        form=form
                    )
                file_name = f'{app.config["UPLOAD_FOLDER"]}{datetime.datetime.now().date()}_{current_user.id}.{file.filename.split(".")[-1]}'
                file_names.append(file_name)
                file.save(file_name)
        if post.files:
            if file_names:
                post.files += "|" + "|".join(file_names)
        else:
            post.files = "|".join(file_names)
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        db_sess.merge(post)
        db_sess.commit()
        # flash("Post has been updated")
        return redirect(url_for('posts', id=post.id))
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
    if current_user.id == post_to_delete.poster.id:
        try:
            db_sess.delete(post_to_delete)
            db_sess.commit()
            # flash("Blog Post was deleted!")
            return redirect("/posts")

        except:
            # flash("WHoops! There was a problem... Try again")
            return render_template("error.html", error="WHoops! There was a problem... Try again")
    else:
        # flash("You dumb beach!")
        return render_template("error.html", error="you are not the creator of this post")


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    db_sess = db_session.create_session()
    name = None
    user_to_delete = db_sess.query(User).get(id)
    mail = user_to_delete.email
    stat_to_delete = db_sess.query(Stats).filter(Stats.player_mail == mail).first()
    if current_user.id == user_to_delete.id:
        try:
            db_sess.delete(user_to_delete)
            db_sess.delete(stat_to_delete)
            db_sess.commit()
            # flash("User Deleted")
            return redirect("/register")
        except Exception:
            # flash("Error! Looks like there was a problem... Try again!")
            return redirect("/dashboard")
    else:
        return render_template("error.html", error="You can't do this")


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UpdateUserForm()
    name_to_update = db_sess.query(User).get(id)

    if form.validate_on_submit():
        name_to_update.name = form.name.data
        name_to_update.email = form.email.data
        name_to_update.nickname = form.nickname.data
        name_to_update.surname = form.surname.data
        try:
            db_sess.commit()
            # flash("User Updated")
            return render_template("update.html", form=form,
                                   name_to_update=name_to_update, message="User Updated")
        except:
            # flash("Error! Looks like there was a problem... Try again!")
            return render_template("update.html", form=form,
                                   name_to_update=name_to_update, message="Error! Looks like there was a problem... Try again!")
    return render_template("update.html", form=form,
                               name_to_update=name_to_update,
                               id=id)


# @app.route('/user/add', methods=['GET', 'POST'])
# def add_user():
#     name = None
#     form = UserForm()
#     if form.validate_on_submit():
#         user = db_sess.query(User).filter_by(email=form.email.data).first()
#         if user is None:
#             # Hash the password!
#             hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
#             user = User(name=form.name.data, email=form.email.data,
#                         password_hash=hashed_pw, nickname=form.nickname.data)
#             db_sess.add(user)
#             stat = Stats(player_mail=form.email.data, kills=0, deaths=0, damage=0, hits=0, rik=0, fires=0)
#             db_sess.add(stat)
#             db_sess.commit()
#         name = form.name.data
#         form.name.data = ''
#         form.nickname.data = ''
#         form.email.data = ''
#         form.password_hash.data = ''
#         flash("User Added Successfully")
#     our_users = db_sess.query(User).order_by(User.date_added)
#     return render_template("add_user.html", form=form, name=name,
#                            our_users=our_users)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            # flash("Пароли не совпадают")
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            # flash("Такой пользователь уже есть")
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Такой пользователь уже есть")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            # flash("Никнейм уже занят")
            return render_template('register.html', title='Регистрация',
                                   form=form, message="Никнейм уже занят")
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
# @app.route('/test_pw', methods=['GET', 'POST'])
# def test_pw():
#     email = None
#     password = None
#     pw_to_check = None
#     passed = None
#     form = PasswordForm()
#     db_sess = db_session.create_session()
#     # validate Form
#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password_hash.data
#         # Clear the form
#         form.email.data = ''
#         form.password_hash.data = ''
#
#         # Lookup User By Email Address
#         pw_to_check = db_sess.query(User).filter_by(email=email).first()
#
#         # Check Hashed Password
#         passed = check_password_hash(pw_to_check.password_hash, password)
#
#         # flash("Form Submitted Successfully")
#     return render_template("test_pw.html",
#                            email=email,
#                            password=password,
#                            pw_to_check=pw_to_check,
#                            passed=passed,
#                            form=form)


def main():
    app.run(host=SERVER_HOST, port=int(SERVER_PORT_WEB))


if __name__ == '__main__':
    main()
