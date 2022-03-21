from app import db, Category, Posts


def filter_special(name_of_category):
    id_of_name_of_category = db.session.query(Category).filter_by(name=name_of_category).first().id
    final = db.session.query(Posts).all().order_by(db.session.query(Posts.date)).filter_by(
        category_id=id_of_name_of_category).all()
    return final
