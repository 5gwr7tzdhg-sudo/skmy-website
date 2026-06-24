from flask import Blueprint, redirect, render_template, request
from sqlalchemy import or_

from database.models import GuideArticle, GuideCategory, News
from routes.public.fi import fi_context


search_bp = Blueprint("search", __name__)


@search_bp.route("/<lang>/search")
def search(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    query = request.args.get("q", "").strip()
    articles = []
    news_items = []
    message = None

    messages = {
        "fi": {
            "empty": "Kirjoita hakusana",
            "not_found": "Hakutuloksia ei löytynyt",
        },
        "ru": {
            "empty": "Введите поисковый запрос",
            "not_found": "Ничего не найдено",
        },
        "en": {
            "empty": "Enter a search term",
            "not_found": "No results found",
        },
    }
    if not query:
        message = messages[lang]["empty"]
    else:
        pattern = f"%{query}%"
        articles = (
            GuideArticle.query
            .join(GuideCategory)
            .filter(
                GuideArticle.language == lang,
                GuideArticle.is_published.is_(True),
                GuideCategory.is_active.is_(True),
                or_(
                    GuideArticle.title.ilike(pattern),
                    GuideArticle.summary.ilike(pattern),
                    GuideArticle.content.ilike(pattern),
                    GuideArticle.keywords.ilike(pattern),
                )
            )
            .order_by(GuideArticle.sort_order, GuideArticle.title)
            .all()
        )
        news_items = (
            News.query
            .filter(
                News.language == lang,
                News.is_published.is_(True),
                or_(
                    News.title.ilike(pattern),
                    News.summary.ilike(pattern),
                    News.content.ilike(pattern),
                ),
            )
            .order_by(News.published_at.desc(), News.created_at.desc())
            .all()
        )

        if not articles and not news_items:
            message = messages[lang]["not_found"]

    if lang == "fi":
        return render_template(
            "public/search_fi.html", lang=lang, query=query, articles=articles, news_items=news_items, message=message,
            **fi_context("Haku oppaasta | SKMY", "Hae SKMY:n Suomen oppaasta tietoa palveluista ja oikeuksista."),
        )
    return render_template(
        "public/search.html",
        lang=lang,
        query=query,
        articles=articles,
        news_items=news_items,
        message=message
    )
