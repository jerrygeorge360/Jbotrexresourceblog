from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os


def filter_special(name_of_category='programming and tips'):
    try:
        id_of_name_of_category = db.session.query(Category).filter_by(name=name_of_category).first().id
        if id_of_name_of_category is not None:
            final = db.session.query(Posts).filter_by(category_id=id_of_name_of_category).order_by(
                db.session.query(Posts.date)).all()
            return final
        else:
            return ''
    except:
        return ''


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myportfolio.db' + '?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = '08028301137'

mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'connectjerry2022@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = SQLAlchemy(app)
from organize import *
from mydatabase import *

app.jinja_env.globals.update(my_filter_special=filter_special)



@app.context_processor
def universal():
    cat = db.session.query(Category.name).all()
    page = request.args.get('page', 1, type=int)
    database_query = {
        'posts': Posts.query.paginate(page=page, per_page=6),
        'posts_size': len(db.session.query(Posts).order_by(db.session.query(Posts.date)).all()),
        'category': db.session.query(Category).all(),
        'articles': db.session.query(Posts).filter_by(topic='anything'),
        'filter_special_size': len(filter_special())
    }

    return dict(navigation=navbar, socialicons=socialmedia, category=cat, my_database_query=database_query)


# @app.route('/')
# def hello_world():
#     return render_template('run.html')


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
    page = request.args.get('page', 1, type=int)
    cart = db.session.query(Category).filter_by(name=name).first()
    article_instance = Posts.query.filter_by(category_id=cart.id).paginate(page=page, per_page=6)

    return render_template('articles_filter.html', my_article_instance=article_instance,
                           )


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
        topic = request.form['topic']
        desc = request.form['description']
        content = request.form['content']
        if topic or desc or content != '':
            path = 'static'
            upload_folder = os.path.join(path, 'postimages', '')
            app.config['upload_folder'] = upload_folder

            print(content)
            postimage = request.files['file']
            postimagename = secure_filename(postimage.filename)
            catalog = request.form['category']
            catalog1 = db.session.query(Category).filter_by(name=catalog).first()
            creator = request.form['author']
            creator1 = db.session.query(Author).filter_by(user_name=creator).first()
            postimage.save(os.path.join(app.config['upload_folder'], postimagename))
            new_post = Posts(topic=topic, content=content, image_name=postimagename, catalog=catalog1, creator=creator1
                             , description=desc)
            db.session.add(new_post)
            db.session.commit()
            flash(f'Post was successfully added', 'success')
            return redirect('/postuploads')
        else:
            error = 'Not successful'

        return render_template('update.html', error=error)
    return render_template('update.html')


@app.route('/categoryuploads', methods=['POST', 'GET'])
def categoryupload():
    # if not session.get('username'):
    #     return redirect('/signin')

    if request.method == "POST":
        category_name = request.form['categoryname']
        if category_name != '':
            path = 'static'
            upload_folder = os.path.join(path, 'categoryimages')
            app.config['upload_folder1'] = upload_folder

            image = request.files['file']
            imagename = secure_filename(image.filename)
            image.save(os.path.join(app.config['upload_folder1'], imagename))
            category = Category(name=category_name, image_name=imagename)
            db.session.add(category)
            db.session.commit()
            flash(f'Category was successfully added', 'success')
            return redirect('/categoryuploads')
        else:
            error = 'Not successful'

        return render_template('catagory.html', error=error)
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


@app.route('/subscribing_news_letter', methods=['GET', 'POST'])
def receive_subs():
    if request.method == 'POST':
        email = request.form['newsletteri']
        if email != '':
            db.session.add(Newsletter(email_address=email))
            db.session.commit()
            print('done with subscriber')
            flash(f'{email} was successfully added', 'success')
            return redirect('/')
        else:
            error = 'please add something'
        return render_template('run.html', error=error)


@app.route('/newsmail', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        newslist = []
        list_of_subscribers = db.session.query(Newsletter).all()

        def convert_to_list():
            for i in list_of_subscribers:
                newslist.append(str(i))

        convert_to_list()

        message = request.form['content']
        subject = request.form['subject']

        my_email = 'connectjerry2022@gmail.com'

        msg = Message(subject=subject, sender=my_email, recipients=newslist)
        msg.body = message
        mail.send(msg)
        return "sent"
    return render_template('newsletter.html')


@app.route('/search', methods=['POST'])
def search():
    posts = Posts.query
    what_to_search = request.form['search']
    filtered_posts = posts.filter(Posts.content.like('%' + what_to_search + '%'))
    arrange_posts = filtered_posts.order_by(Posts.topic).all()
    return render_template('searched.html', search=what_to_search, posts=arrange_posts)


@app.route('/deleteoperations', methods=['GET', 'POST'])
def deleteoperations():
    return render_template('deleteoperations.html')


@app.route('/categorydeletion', methods=['POST'])
def deletecategory():
    name_of_category = request.form['categoryname']
    category_to_be_deleted = Category.query.filter_by(name=name_of_category).first()
    accompained_post = Posts.query.filter_by(category_id=category_to_be_deleted.id).all()
    if category:
        db.session.delete(category_to_be_deleted)

        def delete_accomapained_post():
            for i in accompained_post:
                db.session.delete(i)

        delete_accomapained_post()
        db.session.commit()
        return 'successful'


@app.route('/postdeletion', methods=['POST'])
def deletepost():
    name_of_post = request.form['postname']
    post_to_be_deleted = Posts.query.filter_by(topic=name_of_post).first()

    if post_to_be_deleted:
        db.session.delete(post_to_be_deleted)

        db.session.commit()
        return 'sucessful'


@app.route('/authordeletion', methods=['POST'])
def deleteauthor():
    name_of_author = request.form['authorname']
    author_to_be_deleted = Author.query.filter_by(name=name_of_author).first()
    if author_to_be_deleted:
        db.session.delete(author_to_be_deleted)
        db.session.commit()
        return 'sucessful'


if __name__ == '__main__':
    app.run(debug=True)
