import os

import click
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import generate_password_hash

from config import Config
from database.db import db
from database import models

from routes.public.home import home_bp
from routes.public.about import about_bp
from routes.public.news import news_bp
from routes.public.guide import guide_bp
from routes.public.interpreting import interpreting_bp
from routes.public.contacts import contacts_bp
from routes.public.search import search_bp
from routes.public.seo import seo_bp
from routes.admin.auth import admin_auth_bp, admin_required
from routes.admin.contacts import admin_contacts_bp
from routes.admin.guide import admin_guide_bp
from routes.admin.news import admin_news_bp
from database.models import AdminLog, User


app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

db.init_app(app)


@app.context_processor
def inject_base_url():
    return {"base_url": app.config["BASE_URL"]}

login_manager = LoginManager()
login_manager.login_view = "admin_auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template(
        "admin/csrf_error.html",
        reason=error.description,
        lang="ru"
    ), 400

app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(news_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(interpreting_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(search_bp)
app.register_blueprint(seo_bp)
app.register_blueprint(admin_auth_bp)
app.register_blueprint(admin_contacts_bp)
app.register_blueprint(admin_guide_bp)
app.register_blueprint(admin_news_bp)


@app.route("/admin")
@app.route("/admin/")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html", lang="ru")


@app.route("/admin/logs")
@admin_required
def admin_logs():
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).all()
    return render_template("admin/logs.html", logs=logs, lang="ru")


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database tables created.")


@app.cli.command("create-admin")
def create_admin():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    if not email or not password:
        raise click.ClickException(
            "ADMIN_EMAIL and ADMIN_PASSWORD environment variables must be set."
        )

    db.create_all()
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("Administrator already exists.")
        return

    admin = User(
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
        name="Administrator",
        is_active=True,
    )
    db.session.add(admin)
    db.session.commit()
    print("Administrator created: admin@skmy.local")

@app.cli.command("seed-db")
def seed_db():
    from database.models import GuideCategory, GuideArticle

    categories_data = [
        {
            "slug": "dvv",
            "language": "ru",
            "title": "DVV",
            "description": "Henkilötunnus, регистрация, адрес и личные данные.",
            "sort_order": 1,
        },
        {
            "slug": "kela",
            "language": "ru",
            "title": "Kela",
            "description": "Пособия, OmaKela, поддержка и сурдоперевод.",
            "sort_order": 2,
        },
        {
            "slug": "te",
            "language": "ru",
            "title": "TE-palvelut",
            "description": "Поиск работы, регистрация безработным и обучение.",
            "sort_order": 3,
        },
        {
            "slug": "migri",
            "language": "ru",
            "title": "Migri",
            "description": "Вид на жительство, продление и гражданство.",
            "sort_order": 4,
        },
        {
            "slug": "health",
            "language": "ru",
            "title": "Здравоохранение",
            "description": "Поликлиника, стоматология, экстренная помощь.",
            "sort_order": 5,
        },
        {
            "slug": "family",
            "language": "ru",
            "title": "Семья",
            "description": "Брак, дети, регистрация семьи и социальная помощь.",
            "sort_order": 6,
        },
    ]

    for item in categories_data:
        exists = GuideCategory.query.filter_by(
            slug=item["slug"],
            language=item["language"]
        ).first()

        if not exists:
            category = GuideCategory(**item)
            db.session.add(category)

    db.session.commit()

    dvv = GuideCategory.query.filter_by(slug="dvv", language="ru").first()
    kela = GuideCategory.query.filter_by(slug="kela", language="ru").first()

    articles_data = [
        {
            "category_id": dvv.id,
            "language": "ru",
            "title": "Как получить henkilötunnus",
            "slug": "henkilotunnus",
            "summary": "Что такое henkilötunnus и зачем он нужен.",
            "content": "Henkilötunnus — это финский личный идентификационный номер. Он нужен для регистрации, банковских услуг, Kela, работы и многих государственных сервисов.",
            "sort_order": 1,
        },
        {
            "category_id": dvv.id,
            "language": "ru",
            "title": "Регистрация в Финляндии",
            "slug": "registration",
            "summary": "Как зарегистрировать проживание и адрес.",
            "content": "Регистрация обычно проходит через DVV. Нужно подтвердить личность, адрес и основание проживания в Финляндии.",
            "sort_order": 2,
        },
        {
            "category_id": kela.id,
            "language": "ru",
            "title": "Пособия Kela",
            "slug": "benefits",
            "summary": "Какие пособия можно оформить через Kela.",
            "content": "Kela отвечает за многие виды социальной поддержки. Заявления обычно подаются через OmaKela или в офисе Kela.",
            "sort_order": 1,
        },
        {
            "category_id": kela.id,
            "language": "ru",
            "title": "Сурдоперевод через Kela",
            "slug": "interpreter",
            "summary": "Как получить право на сурдоперевод.",
            "content": "Глухие и слабослышащие люди могут иметь право на услугу сурдоперевода через Kela. Для этого нужно подать заявление.",
            "sort_order": 2,
        },
    ]

    for item in articles_data:
        exists = GuideArticle.query.filter_by(
            slug=item["slug"],
            language=item["language"],
            category_id=item["category_id"]
        ).first()

        if not exists:
            article = GuideArticle(**item)
            db.session.add(article)

    db.session.commit()

    print("Seed data created.")


if __name__ == "__main__":
    app.run(debug=True)
