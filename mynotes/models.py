from datetime import datetime
from mynotes import db, loginManager, app
from flask_login import UserMixin
from sqlalchemy import Boolean, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)
    activated = db.Column(db.Boolean,nullable=False,default=False)
    articles = db.relationship('Article',backref='author',lazy=True)
    tags = db.relationship('Tag',backref='owner',lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Association(db.Model):
    __tablename__ = "associations"
    id = db.Column(db.Integer,primary_key=True)
    tag_id = db.Column(db.Integer,db.ForeignKey('tag.id'),nullable=False)
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'),nullable=False)

    def __repr__(self):
        return f"Association: association_id:{self.id}, article_id:{self.article_id}, tag_id:{self.tag_id}"

class Tag(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(100),nullable=False)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    articles = db.relationship('Article',secondary='associations')

    def __repr__(self):
        return f"Tag('{self.name}','{self.description}')"
    

class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text(length=(2 ** 24) - 1) ,nullable=False)
    shared = db.Column(db.Boolean,nullable=False,default=False)
    encrypted = db.Column(db.Boolean,nullable=False,default=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    tags = db.relationship('Tag',secondary='associations')          

    def __repr__(self):
        return f"Article('{self.id}','{self.title}','{self.shared}','{self.date_posted}')"

class ArticleImage(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    content = db.Column(db.LargeBinary(length= (2 ** 24) - 1),nullable=False)
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'),nullable=True)
    temporary_id = db.Column(db.String(32),nullable=True)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
