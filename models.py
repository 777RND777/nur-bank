from server import Base, db, session


class User(Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    first_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250))
    debt = db.Column(db.Float, default=0)
    requested = db.Column(db.Float, default=0)
    approving = db.Column(db.Float, default=0)

    def __init__(self, user_id, first_name, last_name):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = f"{first_name} {last_name}"

    @classmethod
    def get_list(cls):
        try:
            users = cls.query.filter().all()
            session.commit()
            return users
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get(cls, user_id):
        try:
            user = cls.query.filter(cls.id == user_id).one()
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
