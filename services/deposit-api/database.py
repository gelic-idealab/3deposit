from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

if os.environ.get('DATABASE') == 'sqlite':
    engine = create_engine('sqlite:///threedeposit.sqlite', convert_unicode=True)
if os.environ.get('DATABASE') == 'mysql':
    engine = create_engine('mysql+pymysql://root:root@db:3306/threedeposit')

db_session = scoped_session(sessionmaker(autocommit=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    key = Column(String(120))
    value = Column(String(256))


class Deposit(Base):
    __tablename__ = 'deposit'
    id = Column(Integer, primary_key=True)
    deposit_netid = Column(String(120))
    deposit_submitted = Column(String(50))
    deposit_author = Column(String(120))
    deposit_title = Column(String(120))
    deposit_description = Column(String(120))
    deposit_tags = Column(String(120))
    deposit_url = Column(String(120))
    deposit_collection_id = Column(String(120))
    sketchfab_uid = Column(String(120))
    sketchfab_url = Column(String(120))
    sketchfab_thumbnail = Column(String(120), default='/static/default-thumbnail.jpg', nullable=False)
    box_model_path = Column(String(120))

    def __repr__(self):
        return f'{self.id}, {self.deposit_netid}, {self.deposit_submitted}, {self.sketchfab_uid}'


class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(120))
    email = Column(String(50))
    password_hash = Column(String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def init_db():
    Base.metadata.create_all(bind=engine)
