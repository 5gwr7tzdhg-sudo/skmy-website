from flask import Blueprint, render_template, redirect

from database.models import GuideArticle, GuideCategory, News

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return redirect("/ru/")


@home_bp.route("/<lang>/")
def home(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    categories = (
        GuideCategory.query
        .filter_by(language=lang, is_active=True)
        .order_by(GuideCategory.sort_order, GuideCategory.title)
        .all()
    )
    latest_news = (
        News.query
        .filter_by(language=lang, is_published=True)
        .order_by(News.published_at.desc(), News.created_at.desc())
        .limit(3)
        .all()
    )
    popular_articles = (
        GuideArticle.query
        .join(GuideCategory)
        .filter(
            GuideArticle.language == lang,
            GuideArticle.is_published.is_(True),
            GuideCategory.is_active.is_(True),
        )
        .order_by(GuideArticle.sort_order, GuideArticle.created_at.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "public/home.html",
        lang=lang,
        categories=categories,
        latest_news=latest_news,
        popular_articles=popular_articles
    )
