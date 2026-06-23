from flask import Blueprint, redirect, render_template, request
from sqlalchemy import or_

from database.models import GuideArticle, GuideCategory
from routes.public.fi import fi_context


search_bp = Blueprint("search", __name__)


@search_bp.route("/<lang>/search")
def search(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    query = request.args.get("q", "").strip()
    articles = []
    message = None

    if not query:
        message = "Kirjoita hakusana" if lang == "fi" else "Введите поисковый запрос"
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

        if not articles:
            message = "Hakutuloksia ei löytynyt" if lang == "fi" else "Ничего не найдено"

    if lang == "fi":
        return render_template(
            "public/search_fi.html", lang=lang, query=query, articles=articles, message=message,
            **fi_context("Haku oppaasta | SKMY", "Hae SKMY:n Suomen oppaasta tietoa palveluista ja oikeuksista."),
        )
    return render_template(
        "public/search.html",
        lang=lang,
        query=query,
        articles=articles,
        message=message
    )
