from sqlalchemy.orm import relationship
from . import Base, session
import sqlalchemy as db


class Application(Base):
    __tablename__ = "applications"
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.String(50), nullable=False)
    answer_date = db.Column(db.String(50))
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
    def get_user_list(cls, user_id: int):
        try:
            applications = cls.query.filter(cls.user_id == user_id).all()
            session.commit()
            return applications
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get(cls, application_id: int):
        try:
            user = cls.query.filter(cls.id == application_id).first()
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
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, unique=True, nullable=False)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250))
    debt = db.Column(db.Integer, default=0)
    applications = relationship("Application", backref="author", lazy=True)

    def __init__(self, id: int, first_name: str, last_name: str, username: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

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
    def get(cls, user_id: int):
        try:
            user = cls.query.filter(cls.id == user_id).first()
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
