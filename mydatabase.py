from app import db, redirect, flash
from datetime import datetime


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image_name = db.Column(db.String)
    posts = db.relationship("Posts", backref="catalog", lazy=True)

    def __repr__(self):
        return f"{self.image_name, self.name}"


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    topic = db.Column(db.String, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    content = db.Column(db.String, index=True)
    image_name = db.Column(db.String, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), index=True)
    description = db.Column(db.String, index=True)

    def __repr__(self):
        return f'{self.topic, self.category_id, self.author_id, self.description, self.content, self.date}'


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    email_address = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = db.relationship("Posts", backref="creator", lazy=True)

    def __repr__(self):
        return f"{self.id, self.user_name, self.first_name, self.last_name, self.middle_name, self.email_address}"


db.create_all()


# validation
def validation(firstname, lastname, middlename, username, emailaddress, password):
    if not firstname or not lastname or not middlename or not username or not emailaddress or not password:
        msg = 'You damn idiot fill in the required field.'
        return f'<alert>{msg}</alert>'
    elif len(password) < 6:
        msg = 'You security hater ,will you choose a longer password.'
        return f'<alert>{msg}</alert>'
    elif db.session.query(Author).filter_by(user_name=username).first():
        msg = 'Choose another username you toad.'
        return f'<alert>{msg}</alert>'
    else:
        try:
            author = Author(email_address=emailaddress, first_name=firstname, last_name=lastname,
                            middle_name=middlename, password=password, user_name=username)
            db.session.add(author)
            db.session.commit()
            msg = 'ok'
            return redirect('/signin')
        except Exception as err:
            # print('Register error: ' + err)
            msg = str(err)
        return msg

# try:
#     def filter_special(name_of_category='programming and tips'):
#         id_of_name_of_category = db.session.query(Category).filter_by(name=name_of_category).first().id
#         final = db.session.query(Posts).filter_by(category_id=id_of_name_of_category).order_by(
#             db.session.query(Posts.date)).all()
#         return final
# except:
#     pass
