from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import secure_filename
import os


def filter_special(name_of_category='programming and tips'):
    id_of_name_of_category = db.session.query(Category).filter_by(name=name_of_category).first().id
    final = db.session.query(Posts).filter_by(category_id=id_of_name_of_category).order_by(
        db.session.query(Posts.date)).all()
    return final


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myportfolio.db' + '?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = '08028301137'

db = SQLAlchemy(app)
from organize import *
from mydatabase import *

app.jinja_env.globals.update(my_filter_special=filter_special)


@app.context_processor
def universal():
    cat = db.session.query(Category.name).all()
    database_query = {
        'posts': db.session.query(Posts).order_by(db.session.query(Posts.date)).all(),
        'posts_size': len(db.session.query(Posts).order_by(db.session.query(Posts.date)).all()),
        'category': db.session.query(Category).all(),
        'category_size': len(db.session.query(Category).all()),
        'articles': db.session.query(Posts).filter_by(topic='anything'),
        'filter_special_size': len(filter_special())
    }
    return dict(navigation=navbar, socialicons=socialmedia, category=cat, my_database_query=database_query)


@app.route('/')
def hello_world():
    return render_template('run.html')


@app.route('/articles/<name_of_article>')
def articles(name_of_article):
    name = name_of_article
    article_instance = db.session.query(Posts).filter_by(topic=name).first()
    return render_template('articles.html', my_article_instance=article_instance)


@app.route('/filter_articles/<filtration>')
def article_filter(filtration):
    name = filtration
    cart = db.session.query(Category).filter_by(name=name).first()
    article_instance = db.session.query(Posts).filter_by(category_id=cart.id).all()
    number_of_article = len(article_instance)
    return render_template('articles_filter.html', my_article_instance=article_instance,
                           number_of_articles=number_of_article)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        middlename = request.form['middlename']
        username = request.form['username']
        emailaddress = request.form['email']
        password = request.form['password']
        msg = validation(firstname=firstname, lastname=lastname, middlename=middlename, username=username,
                         emailaddress=emailaddress, password=password)
        return msg

    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        def login(usernam=username):
            msg = ''
            try:
                if db.session.query(Author).filter_by(user_name=usernam, password=password).first():
                    session['username'] = usernam
                    msg = flash('successful', category='success')
                    return redirect('/postuploads')
                elif not db.session.query(Author).filter_by(user_name=usernam, password=password).first():
                    return redirect('/signup', code=302)

            except Exception as err:
                msg = str(err)
                return redirect('/')
            return msg

        msg = login()
        return msg

    return render_template('signin.html')


@app.route('/supplementary_pages/<name>')
def supplementary_pages(name):
    return render_template('supplementary_page.html', name_of_title=name)


@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')


@app.route('/postuploads', methods=['POST', 'GET'])
def postupload():
    if not session.get('username'):
        return redirect('/signin')

    if request.method == "POST":
        upload_folder = r"C:\Users\EDEANI JERRY GEORGE\OneDrive\Desktop\digital dreams\myportfolio\static\postimages"
        app.config['upload_folder'] = upload_folder
        topic = request.form['topic']
        desc = request.form['description']
        content = request.get_data()
        print(content)
        postimage = request.files['file']
        postimagename = secure_filename(postimage.filename)
        catalog = request.form['category']
        catalog1 = db.session.query(Category).filter_by(name=catalog).first()
        creator = request.form['author']
        content1 = request.form['post_url']
        print(content1)
        creator1 = db.session.query(Author).filter_by(user_name=creator).first()
        postimage.save(os.path.join(app.config['upload_folder'], postimagename))
        new_post = Posts(topic=topic, content=content1, image_name=postimagename, catalog=catalog1, creator=creator1
                         , description=desc)
        db.session.add(new_post)
        db.session.commit()
        return 'successful'

    return render_template('update.html')


@app.route('/categoryuploads', methods=['POST', 'GET'])
def categoryupload():
    # if not session.get('username'):
    #     return redirect('/signin')

    if request.method == "POST":
        upload_folder = r'C:\Users\EDEANI JERRY GEORGE\OneDrive\Desktop\digital dreams\myportfolio\static\categoryimages'
        app.config['upload_folder1'] = upload_folder
        category_name = request.form['categoryname']
        image = request.files['file']
        imagename = secure_filename(image.filename)
        image.save(os.path.join(app.config['upload_folder1'], imagename))
        category = Category(name=category_name, image_name=imagename)
        db.session.add(category)
        db.session.commit()

    return render_template('catagory.html')


@app.route('/postdownloads/<int:number>')
def post_download_file(number):
    upload_folder = r'../static/postimages'
    app.config['upload_folder'] = upload_folder
    name_of_image = db.session.query(Posts.image_name).filter_by(id=number).first()
    url = os.path.join(app.config['upload_folder'], name_of_image[0])
    return redirect(url)


@app.route('/categorydownloads/int:<number>')
def category_download_file(number):
    upload_folder = r'..\\static\categoryimages'
    app.config['upload_folder1'] = upload_folder
    name_of_image = db.session.query(Category.image_name).filter_by(id=number).first()
    url = os.path.join(app.config['upload_folder1'], name_of_image[0])
    return redirect(url)


@app.route('/pic')
def category():
    upload_folder = r'../static/assests/'
    app.config['upload_folder2'] = upload_folder
    # name_of_image = db.session.query(Category.image_name).filter_by(id=number).first()
    name_of_image = "istock.jpg"
    url = os.path.join(app.config['upload_folder2'], name_of_image)
    return redirect(url)


@app.route('/mobileauthor')
def author():
    return render_template('mobileauthor.html')


if __name__ == '__main__':
    app.run(debug=True)
