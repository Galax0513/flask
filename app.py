import datetime
import json
import os
import threading
import socket
from time import sleep

import requests
from flask import Flask, render_template, redirect, url_for
from turbo_flask import Turbo
from flask_login import login_user, LoginManager, login_required, logout_user, current_user

from data.Models.comments import Comments
from data.Models.subscribers import Subs
from settings import SERVER_PORT_WEB
from data.api.api import GetPos, PostsResource, PostsListResource, UsersListResource, StatsResource, \
    StatsListResource, UsersResource
from data.Sql import db_session
from data.Models.blog_post import Posts
from data.Forms.SearchForm import SearchForm
from data.Forms.EditPostForm import EditPostForm
from data.Forms.PostForm import PostForm
from data.Forms.LoginForm import LoginForm
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
app.config["UPLOAD_FOLDER_AVATAR"] = r"static/avatars/"
app.config["ALLOWED_FILE_EXTENSIONS"] = ["png", "jpg", "jpeg", "gif", "mp4", "avi", "mov"]
app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"] = ["png", "jpg", "jpeg", "gif"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'error_login'

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


@app.route("/need_to_login")
def error_login():
    return render_template('error.html', error=f"Must Be Logged In...")

@app.route("/")
@app.route("/main")
def comments():
    return render_template("main.html")


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
    points = {}
    for post in db_sess.query(Posts).all():
        if post.coords:
            nickname = 'deleted_user'
            if post.poster and post.poster.nickname:
                nickname = post.poster.nickname
            if post.coords != 'error':
                if post.coords in points:
                    points[post.coords][nickname] = [post.id, post.title, post.poster_id]
                else:
                    points[post.coords] = {nickname: [post.id, post.title, post.poster_id]}
    return render_template("test_map_java.html", points=points, size=['100%', "600px"],
                           zoom=2, center=[55.76, 37.64])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # flash("Login Succesfull!")
            return redirect(url_for('dashboard', delete_user=0, user_id=current_user.id))
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


@app.route('/dashboard/<int:user_id>/<int:delete_user>', methods=['GET', 'POST', "PUT"])
def dashboard(delete_user, user_id):
    form1 = UpdateUserForm()
    form2 = DeleteProfileForm()
    user = db_sess.query(User).filter(User.id == user_id).first()
    subscribity = True
    # добавляем с формы в ьазу данных
    if user:
        for sub in user.subs:
            if sub.subscriber == current_user.id:
                subscribity = False
                break
        if form1.validate_on_submit():
            if current_user.id == user.id:
                file = form1.file.data
                if file:
                    if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"]:
                        return render_template(
                            "dashboard.html",
                            message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"])}',
                            form=form1, user=user, subscribity=subscribity, subs=len(user.subs))
                    file_name = f'{app.config["UPLOAD_FOLDER_AVATAR"]}{datetime.datetime.now().date()}_{datetime.datetime.now().timestamp()}.{file.filename.split(".")[-1]}'
                    file.save(file_name)
                    user.avatar = file_name
                user.name = form1.name.data
                user.email = form1.email.data
                user.surname = form1.surname.data
                try:
                    db_sess.commit()
                    # flash("User Updated")
                    return render_template("dashboard.html", form=form1,
                                           user=user, message="User Updated", subscribity=subscribity, subs=len(user.subs))
                except:
                    # flash("Error! Looks like there was a problem... Try again!")
                    return render_template("dashboard.html", form=form1,
                                           user=user,
                                           message="Error! Looks like there was a problem... Try again!",
                                           subscribity=subscribity, subs=len(user.subs))
            else:
                # flash("You dumb beach!")
                return render_template("error.html", error="you are not this user")
        elif user and form2.validate_on_submit():
            if form2.password.data == form2.password_again.data:
                return redirect(f"/delete/{current_user.id}")
            else:
                # flash("Пароли не совпадают")
                return render_template("dashboard.html", form=form1, form2=form2,
                                       user=user,
                                       message="Пароли не совпадают", subscribity=subscribity, subs=len(user.subs))
        else:
            if delete_user:
                return render_template("dashboard.html", form=form1,
                                       user=user, form2=form2, subscribity=subscribity, subs=len(user.subs))
            return render_template("dashboard.html", form=form1,
                                   user=user, subscribity=subscribity, subs=len(user.subs))
    return render_template("error.html", error="This user do not exist")


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


@app.route("/users/<int:cond_sub>", methods=['GET', 'POST'])
def users(cond_sub):
    subs = [user.id for user in db_sess.query(User).order_by(User.modified_date).all()]
    if cond_sub:
        subs = []
        for user in db_sess.query(User).all():
            for sub in user.subs:
                if sub.subscriber == current_user.id:
                    subs.append(sub.user)
    users = db_sess.query(User).filter(User.id.in_(subs)).order_by(User.modified_date).all()
    form = SearchForm()
    subscribity = {}
    for user in users:
        subscribity[user.id] = True
        for sub in user.subs:
            if not current_user.is_authenticated or sub.subscriber == current_user.id:
                subscribity[user.id] = False
                break
    if form.validate_on_submit():
        users = db_sess.query(User).filter(((User.nickname == form.search.data.lower()) |
                                            User.nickname.like(f"%{form.search.data}%") & User.id.in_(subs))).all()
        if users:
            return render_template("users.html",
                                   users=users, form=form, subscribity=subscribity, cond_sub=cond_sub)
        else:
            pass
            # flash("По данному запросу постов не найдено")
    return render_template("users.html", users=users, form=form, subscribity=subscribity, cond_sub=cond_sub)


@app.route('/posts/<int:cond_sub>', methods=["GET", "POST"])
def posts(cond_sub):
    posts = db_sess.query(Posts).order_by(Posts.date_posted).all()
    subs = []
    if cond_sub:
        for user in db_sess.query(User).all():
            for sub in user.subs:
                if sub.subscriber == current_user.id:
                    subs.append(sub.user)

        posts = db_sess.query(Posts).filter(Posts.poster_id.in_(subs)).order_by(Posts.date_posted).all()

    form = SearchForm()
    if form.validate_on_submit():
        posts = db_sess.query(Posts).filter((Posts.title == form.search.data.lower()) |
                                            Posts.title.like(f"%{form.search.data}%")).all()
        if cond_sub:
            posts = db_sess.query(Posts).filter(((Posts.title == form.search.data.lower()) |
                                 Posts.title.like(f"%{form.search.data}%")) & Posts.poster_id.in_(subs)).all()
        if posts:
            return render_template("posts.html",
                                   posts=posts, form=form, cond_sub=cond_sub)
        else:
            pass
            # flash("По данному запросу постов не найдено")
    return render_template("posts.html", posts=posts, form=form, cond_sub=cond_sub)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
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
                file_name = f'{app.config["UPLOAD_FOLDER"]}{datetime.datetime.now().date()}_{datetime.datetime.now().timestamp()}_{current_user.id}.{file.filename.split(".")[-1]}'
                file_names.append(file_name)
                file.save(file_name)
        post.files = "|".join(file_names)
        # Add post data to database
        db_sess.add(post)
        db_sess.commit()

        # Return a Message
        # flash("Blog Post Submitted Successfully!")

        return redirect(f"post/{post.id}")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


# возвращает обратно к посту
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    form = SearchForm()
    post = db_sess.query(Posts).get(id)
    comments = db_sess.query(Comments).all()
    if post:
        if form.validate_on_submit():
            comment = Comments(content=form.search.data,
                               user_id=post.poster_id,
                               post_id=id)
            db_sess.add(comment)
            db_sess.commit()
        if not post.coords == "error":
            coords = [float(coord) for coord in post.coords.split(',')][-1::-1]
        else:
            coords = [60, 100]
        post_files = []
        for file in post.files.split("|"):
            if os.path.exists(file):
                post_files.append(file)
            else:
                post_files.append(app.config["UPLOAD_FOLDER"] + "image_not_found.png")
        points = {}
        if post.coords:
            nickname = 'deleted_user'
            if post.poster and post.poster.nickname:
                nickname = post.poster.nickname

            points[post.coords] = {nickname: [post.id, post.title, post.poster_id]}
        return render_template('post.html', post=post, points=points, center=coords, size=["100%", "400px"],
                               zoom=8, post_files=post_files, form=form, comments=comments)
    return render_template("error.html", error="Post do not exist")


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = db_sess.query(Posts).get(id)
    form = EditPostForm()
    if form.validate_on_submit():
        file_names = []
        print(form.files.data)
        for file in form.files.data:
            if file:
                if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS"]:
                    return render_template(
                        "edit_post.html",
                        message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS"])}',
                        form=form
                    )
                file_name = f'{app.config["UPLOAD_FOLDER"]}{datetime.datetime.now().date()}_{datetime.datetime.now().timestamp()}_{current_user.id}.{file.filename.split(".")[-1]}'
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
            # for sub in db_sess.query(Subs).filter(Subs.user == id| Subs.subscriber == id).all():
            #     db_sess.delete(sub)
            db_sess.commit()
            # flash("User Deleted")
            return redirect("/register")
        except Exception:
            # flash("Error! Looks like there was a problem... Try again!")
            return redirect("/dashboard")
    else:
        return render_template("error.html", error="You can't do this")


@app.route('/unsubscribe/<int:user_id>', methods=['GET', 'POST'])
@login_required
def unsubscribe(user_id):
    if user_id == current_user.id:
        return render_template("error.html", error="You can't unsubscribe to yourself")
    user = db_sess.query(User).filter(User.id == user_id).first()
    sub_to_delete = db_sess.query(Subs).filter(Subs.user == user.id, Subs.subscriber == current_user.id).first()
    if sub_to_delete:
        db_sess.delete(sub_to_delete)
        db_sess.commit()
        return redirect("/users/1")
    else:
        return render_template("error.html", error="You are not subscribed to this user")


@app.route('/subscribe/<int:user_id>', methods=['GET', 'POST'])
@login_required
def subscribe(user_id):
    if user_id == current_user.id:
        return render_template("error.html", error="You can't subscribe to yourself")
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not db_sess.query(Subs).filter(Subs.user == user.id, Subs.subscriber == current_user.id).first():
        sub = Subs(user=user.id, subscriber=current_user.id)
        db_sess.add(sub)
        db_sess.commit()
        return redirect("/users/1")
    else:
        return render_template("error.html", error="You have already subscribed to this user")


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UpdateUserForm()
    name_to_update = db_sess.query(User).get(id)

    if form.validate_on_submit():
        if current_user.id == name_to_update.id:
            name_to_update.name = form.name.data
            name_to_update.email = form.email.data
            name_to_update.surname = form.surname.data
            file = form.file.data
            if file:
                if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"]:
                    return render_template(
                        "update.html",
                        message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"])}',
                        form=form, name_to_update=name_to_update)
                file_name = f'{app.config["UPLOAD_FOLDER_AVATAR"]}{datetime.datetime.now().date()}_{datetime.datetime.now().timestamp()}.{file.filename.split(".")[-1]}'
                file.save(file_name)
                name_to_update.avatar = file_name
            try:
                db_sess.commit()
                # flash("User Updated")
                return render_template("update.html", form=form,
                                       name_to_update=name_to_update, message="User Updated")
            except:
                # flash("Error! Looks like there was a problem... Try again!")
                return render_template("update.html", form=form,
                                       name_to_update=name_to_update, message="Error! Looks like there was a problem... Try again!")
        else:
            # flash("You dumb beach!")
            return render_template("error.html", error="you are not this user")
    return render_template("update.html", form=form,
                               name_to_update=name_to_update,id=id)


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

        file = form.file.data
        file_name = ''
        if file:
            if file.filename.split(".")[-1] not in app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"]:
                return render_template(
                    "register.html",
                    message=f'Разрешенные форматы: {" ".join(app.config["ALLOWED_FILE_EXTENSIONS_AVATAR"])}',
                    form=form
                )
            file_name = f'{app.config["UPLOAD_FOLDER_AVATAR"]}{datetime.datetime.now().date()}_{datetime.datetime.now().timestamp()}.{file.filename.split(".")[-1]}'
            file.save(file_name)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            age=int(form.age.data),
            email=form.email.data,
            nickname=form.nickname.data,
            avatar=file_name)
        stat = Stats(player_mail=form.email.data, kills=0, deaths=0, damage=0, hits=0, rik=0, fires=0)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.add(stat)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


def main():
    app.run(host=SERVER_HOST, port=int(SERVER_PORT_WEB))


if __name__ == '__main__':
    main()
