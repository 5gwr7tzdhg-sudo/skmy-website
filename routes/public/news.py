from flask import Blueprint, render_template, redirect

from database.models import News
from routes.public.fi import fi_context

news_bp = Blueprint("news", __name__)


@news_bp.route("/<lang>/news")
def news(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    news_items = (
        News.query
        .filter_by(language=lang, is_published=True)
        .order_by(News.published_at.desc(), News.created_at.desc())
        .all()
    )

    if lang == "fi":
        return render_template(
            "public/news_fi.html", lang=lang, news_items=news_items,
            **fi_context("SKMY:n uutiset", "SKMY:n uutiset, tapahtumat ja ajankohtaiset ilmoitukset."),
        )
    return render_template("public/news.html", lang=lang, news_items=news_items)


@news_bp.route("/<lang>/news/<slug>")
def news_detail(lang, slug):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    news_item = News.query.filter_by(
        language=lang,
        slug=slug,
        is_published=True
    ).first()

    if not news_item:
        return redirect(f"/{lang}/news")

    if lang == "fi":
        return render_template(
            "public/news_detail_fi.html", lang=lang, news_item=news_item,
            **fi_context(f"{news_item.title} | SKMY", news_item.summary or "SKMY:n uutinen"),
        )
    return render_template("public/news_detail.html", lang=lang, news_item=news_item)
