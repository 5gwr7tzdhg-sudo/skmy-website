import json
import re
from urllib.parse import urlparse

from flask import Blueprint, render_template, redirect
from database.models import GuideCategory, GuideArticle
from routes.public.fi import fi_context
from routes.public.page_seo import page_seo

guide_bp = Blueprint("guide", __name__)

VALID_LANGS = ["fi", "ru", "en"]


def split_content_and_faq(content):
    content = content or ""
    faq_marker = re.search(r"^## (?:FAQ|UKK)\s*$", content, flags=re.MULTILINE)
    if not faq_marker:
        return content, []

    article_content = content[:faq_marker.start()].strip()
    faq_content = content[faq_marker.end():].strip()
    faq_items = []
    for faq_pattern in (
        re.compile(
            r"Вопрос:\s*(.+?)\s*\nОтвет:\s*(.+?)(?=\n\s*Вопрос:|\Z)",
            flags=re.DOTALL,
        ),
        re.compile(
            r"Kysymys:\s*(.+?)\s*\nVastaus:\s*(.+?)(?=\n\s*Kysymys:|\Z)",
            flags=re.DOTALL,
        ),
    ):
        for match in faq_pattern.finditer(faq_content):
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                faq_items.append({"question": question, "answer": answer})
        if faq_items:
            break

    return article_content, faq_items


def build_faq_schema(faq_items):
    if not faq_items:
        return None

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"]
                }
            }
            for item in faq_items
        ]
    }
    return json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")


def parse_official_links(value):
    links = []
    for line in (value or "").splitlines():
        title, separator, url = line.partition("|")
        url = (url if separator else title).strip()
        title = title.strip() if separator else url
        if urlparse(url).scheme in ("http", "https"):
            links.append({"title": title or url, "url": url})
    return links


GUIDE_ARTICLES = {
    "dvv": {
        "henkilotunnus": {
            "title": "Как получить henkilötunnus",
            "summary": "Что такое henkilötunnus и зачем он нужен.",
            "content": "Здесь будет простая инструкция: куда обращаться, какие документы нужны и что делать после регистрации."
        },
        "registration": {
            "title": "Регистрация в Финляндии",
            "summary": "Как зарегистрировать проживание и адрес.",
            "content": "Здесь будет инструкция по регистрации адреса и личных данных через DVV."
        }
    },
    "kela": {
        "benefits": {
            "title": "Пособия Kela",
            "summary": "Какие пособия можно оформить через Kela.",
            "content": "Здесь будет объяснение по OmaKela, заявлениям и документам."
        },
        "interpreter": {
            "title": "Сурдоперевод через Kela",
            "summary": "Как получить право на сурдоперевод.",
            "content": "Здесь будет инструкция по заявке на услугу сурдоперевода."
        }
    }
}


@guide_bp.route("/<lang>/guide")
@guide_bp.route("/<lang>/guide/")
def guide(lang):
    categories = (
        GuideCategory.query
        .filter_by(
            language=lang,
            is_active=True
        )
        .order_by(GuideCategory.sort_order)
        .all()
    )

    if lang == "fi":
        return render_template(
            "public/guide_fi.html", lang=lang, categories=categories,
            **fi_context(**page_seo("guide", lang)),
        )
    return render_template(
        "public/guide.html", lang=lang, categories=categories,
        **page_seo("guide", lang),
    )


@guide_bp.route("/<lang>/guide/<category_slug>")
def guide_category(lang, category_slug):

    category = GuideCategory.query.filter_by(
        slug=category_slug,
        language=lang,
        is_active=True
    ).first()

    if not category:
        return redirect(f"/{lang}/guide")

    articles = (
        GuideArticle.query
        .filter_by(
            category_id=category.id,
            language=lang,
            is_published=True
        )
        .order_by(GuideArticle.sort_order)
        .all()
    )

    if lang == "fi":
        return render_template(
            "public/guide_category_fi.html", lang=lang, category=category, articles=articles,
            **fi_context(f"{category.title} | SKMY:n opas", category.description),
        )
    return render_template("public/guide_category.html", lang=lang, category=category, articles=articles)

@guide_bp.route("/<lang>/guide/<category_slug>/<article_slug>")
def guide_article(lang, category_slug, article_slug):

    category = GuideCategory.query.filter_by(
        slug=category_slug,
        language=lang,
        is_active=True
    ).first()

    if not category:
        return redirect(f"/{lang}/guide")

    article = GuideArticle.query.filter_by(
        category_id=category.id,
        slug=article_slug,
        language=lang,
        is_published=True
    ).first()

    if not article:
        return redirect(f"/{lang}/guide/{category_slug}")

    article_content, faq_items = split_content_and_faq(article.content)

    if lang == "fi":
        return render_template(
            "public/guide_article_fi.html", lang=lang, category=category, article=article,
            article_content=article_content, faq_items=faq_items,
            faq_schema=build_faq_schema(faq_items), official_links=parse_official_links(article.official_links),
            **fi_context(f"{article.title} | SKMY:n opas", article.summary),
        )
    return render_template(
        "public/guide_article.html", lang=lang, category=category, article=article,
        article_content=article_content, faq_items=faq_items,
        faq_schema=build_faq_schema(faq_items), official_links=parse_official_links(article.official_links),
    )
