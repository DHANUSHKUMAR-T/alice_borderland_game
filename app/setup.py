from app import db
from app.models import User, GameProgress
from werkzeug.security import generate_password_hash


def create_default_user():
    username = "dhanush"
    password = "kumar"

    user = User.query.filter_by(username=username).first()

    if user is None:
        hashed = generate_password_hash(password)
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        progress = GameProgress(user_id=new_user.id)
        db.session.add(progress)
        db.session.commit()

        print("Default user created: dhanush / kumar")
    else:
        print("Default user already exists.")
