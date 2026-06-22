from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app

from database.models import GuideArticle, GuideCategory, News


seo_bp = Blueprint("seo", __name__)


@seo_bp.route("/robots.txt")
def robots():
    base_url = current_app.config["BASE_URL"]
    content = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@seo_bp.route("/sitemap.xml")
def sitemap():
    base_url = current_app.config["BASE_URL"]
    urls = []
    for lang in ("fi", "ru", "en"):
        urls.extend([
            f"/{lang}/",
            f"/{lang}/about",
            f"/{lang}/news",
            f"/{lang}/guide",
            f"/{lang}/interpreting",
            f"/{lang}/contacts",
        ])

    published_news = News.query.filter_by(is_published=True).all()
    for news_item in published_news:
        urls.append(f"/{news_item.language}/news/{news_item.slug}")

    active_categories = GuideCategory.query.filter_by(is_active=True).all()
    for category in active_categories:
        urls.append(f"/{category.language}/guide/{category.slug}")

    published_articles = (
        GuideArticle.query
        .join(GuideCategory)
        .filter(
            GuideArticle.is_published.is_(True),
            GuideCategory.is_active.is_(True),
            GuideArticle.language == GuideCategory.language,
        )
        .all()
    )
    for article in published_articles:
        urls.append(
            f"/{article.language}/guide/{article.category.slug}/{article.slug}"
        )

    entries = "\n".join(
        f"  <url><loc>{escape(f'{base_url}{url}')}</loc></url>"
        for url in urls
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>"
    )
    return Response(content, mimetype="application/xml")
