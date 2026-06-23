from flask import Blueprint, render_template, redirect

from database.models import GuideArticle, GuideCategory, News

home_bp = Blueprint("home", __name__)


LOCALIZED_HOME_GUIDE_CONTENT = {
    "fi": {
        "categories": [
            {"slug": "dvv", "title": "DVV", "description": "Henkilötunnus, rekisteröinti, osoite ja henkilötiedot."},
            {"slug": "kela", "title": "Kela", "description": "Etuudet, OmaKela, tuki ja tulkkauspalvelu."},
            {"slug": "te", "title": "TE-palvelut", "description": "Työnhaku, työnhakijaksi ilmoittautuminen ja koulutus."},
            {"slug": "migri", "title": "Migri", "description": "Oleskelulupa, jatkolupa ja kansalaisuus."},
            {"slug": "health", "title": "Terveydenhuolto", "description": "Terveyskeskus, hammashoito ja kiireellinen apu."},
            {"slug": "family", "title": "Perhe", "description": "Avioliitto, lapset, perheen rekisteröinti ja sosiaalinen tuki."},
        ],
        "articles": [
            {"slug": "henkilotunnus", "category": "dvv", "title": "Miten saat henkilötunnuksen", "summary": "Mikä henkilötunnus on ja miksi sitä tarvitaan."},
            {"slug": "registration", "category": "dvv", "title": "Rekisteröityminen Suomessa", "summary": "Miten rekisteröit asumisesi ja osoitteesi."},
            {"slug": "omakela", "category": "kela", "title": "Kelan etuudet", "summary": "Mitä etuuksia voit hakea Kelasta."},
            {"slug": "interpreter", "category": "kela", "title": "Tulkkauspalvelu Kelan kautta", "summary": "Miten haet oikeutta tulkkauspalveluun."},
        ],
    },
    "en": {
        "categories": [
            {"slug": "dvv", "title": "DVV", "description": "Personal identity code, registration, address, and personal details."},
            {"slug": "kela", "title": "Kela", "description": "Benefits, OmaKela, support, and interpreting services."},
            {"slug": "te", "title": "TE services", "description": "Job search, registering as a jobseeker, and training."},
            {"slug": "migri", "title": "Migri", "description": "Residence permits, extensions, and citizenship."},
            {"slug": "health", "title": "Healthcare", "description": "Health centres, dental care, and emergency help."},
            {"slug": "family", "title": "Family", "description": "Marriage, children, family registration, and social support."},
        ],
        "articles": [
            {"slug": "henkilotunnus", "category": "dvv", "title": "How to get a personal identity code", "summary": "What a personal identity code is and why you need one."},
            {"slug": "registration", "category": "dvv", "title": "Registering in Finland", "summary": "How to register your residence and address."},
            {"slug": "benefits", "category": "kela", "title": "Kela benefits", "summary": "Which benefits you can apply for through Kela."},
            {"slug": "interpreter", "category": "kela", "title": "Interpreting services through Kela", "summary": "How to apply for the right to interpreting services."},
        ],
    },
}


def localized_home_guide_content(lang):
    content = LOCALIZED_HOME_GUIDE_CONTENT.get(lang)
    if not content:
        return [], []

    categories = [dict(category) for category in content["categories"]]
    categories_by_slug = {category["slug"]: category for category in categories}
    articles = [
        {
            "slug": article["slug"],
            "title": article["title"],
            "summary": article["summary"],
            "category": categories_by_slug[article["category"]],
        }
        for article in content["articles"]
    ]
    return categories, articles


@home_bp.route("/")
def index():
    return redirect("/fi/")


@home_bp.route("/<lang>/")
def home(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/fi/")

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

    if lang in LOCALIZED_HOME_GUIDE_CONTENT and not categories:
        categories, fallback_articles = localized_home_guide_content(lang)
        if not popular_articles:
            popular_articles = fallback_articles

    localized_page = {
        "fi": {
            "template": "public/home_localized.html",
            "meta_title": "SKMY – Tietoa ja tukea kuuroille maahanmuuttajille Suomessa",
            "meta_description": "SKMY auttaa kuuroja ja viittomakielisiä maahanmuuttajia löytämään palvelut, oikeudet ja käytännön ohjeet Suomessa.",
            "navigation_labels": {
                "home": "Etusivu", "about": "Tietoa meistä", "news": "Uutiset",
                "guide": "Opas", "interpreting": "Viittomakielen tulkkaus",
                "contacts": "Yhteystiedot",
            },
            "footer_name": "Suomen Kuurojen Maahanmuuttajayhdistys ry",
        },
        "en": {
            "template": "public/home_localized.html",
            "meta_title": "SKMY – Information and Support for Deaf Immigrants in Finland",
            "meta_description": "SKMY helps Deaf and sign-language immigrants navigate services, rights, and practical information in Finland.",
            "navigation_labels": {
                "home": "Home", "about": "About us", "news": "News", "guide": "Guide",
                "interpreting": "Sign language interpreting", "contacts": "Contact",
            },
            "footer_name": "Finnish Association of Deaf Immigrants",
        },
    }.get(lang, {})

    template_context = {
        "lang": lang,
        "categories": categories,
        "latest_news": latest_news,
        "popular_articles": popular_articles,
    }
    template_context.update(
        {key: value for key, value in localized_page.items() if key != "template"}
    )

    return render_template(
        localized_page.get("template", "public/home.html"),
        **template_context,
    )
