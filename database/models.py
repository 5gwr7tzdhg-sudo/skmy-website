from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin
from database.db import db


def generate_translation_key():
    return str(uuid4())


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="admin")
    name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_admin(self):
        return self.role == "admin"


class AdminLog(db.Model):
    __tablename__ = "admin_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="admin_logs")


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="new")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(10), nullable=False)
    translation_key = db.Column(
        db.String(36), nullable=False, default=generate_translation_key, index=True
    )
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(150), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    image_path = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GuideCategory(db.Model):
    __tablename__ = "guide_categories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    translation_key = db.Column(
        db.String(36), nullable=False, unique=True, default=generate_translation_key
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles = db.relationship(
        "GuideArticle",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan"
    )


class GuideArticle(db.Model):
    __tablename__ = "guide_articles"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("guide_categories.id"),
        nullable=False
    )

    language = db.Column(db.String(10), nullable=False)
    translation_key = db.Column(
        db.String(36), nullable=False, unique=True, default=generate_translation_key
    )
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(150), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    keywords = db.Column(db.Text)
    official_links = db.Column(db.Text)
    video_url = db.Column(db.String(500))

    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
