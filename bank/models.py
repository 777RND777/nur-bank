# TODO add rework application with relationship
from . import Base, db, session


class Application(Base):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    value = db.Column(db.Float)
    request_date = db.Column(db.DateTime)
    answer_date = db.Column(db.DateTime)
    approved = db.Column(db.Boolean, default=False)

    @classmethod
    def get_list(cls):
        try:
            applications = cls.query.all()
            session.commit()
            return applications
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get_user_list(cls, user_id):
        try:
            applications = cls.query.filter(cls.user_id == user_id).all()
            session.commit()
            return applications
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get(cls, user_id, application_id):
        try:
            user = cls.query.filter(cls.user_id == user_id, cls.id == application_id).one()
            session.commit()
            return user
        except Exception:
            session.rollback()
            raise

    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise


class User(Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    first_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    username = db.Column(db.String(250))
    debt = db.Column(db.Float, default=0)

    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = f"{first_name} {last_name}"

    @classmethod
    def get_list(cls):
        try:
            users = cls.query.all()
            session.commit()
            return users
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get(cls, user_id):
        try:
            user = cls.query.filter(cls.user_id == user_id).one()
            session.commit()
            return user
        except Exception:
            session.rollback()
            raise

    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise
