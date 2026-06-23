import os

import click
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

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
from database.models import (
    AdminLog,
    ContactMessage,
    GuideArticle,
    GuideCategory,
    News,
    User,
)


app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

csrf = CSRFProtect(app)

db.init_app(app)


@app.context_processor
def inject_base_url():
    return {
        "base_url": app.config["BASE_URL"],
        "ga_measurement_id": app.config["GA_MEASUREMENT_ID"],
    }

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
    dashboard_stats = {
        "categories": GuideCategory.query.count(),
        "articles": GuideArticle.query.count(),
        "published_articles": GuideArticle.query.filter_by(is_published=True).count(),
        "news": News.query.count(),
        "published_news": News.query.filter_by(is_published=True).count(),
        "new_messages": ContactMessage.query.filter_by(status="new").count(),
    }
    language_article_counts = {
        lang: GuideArticle.query.filter_by(language=lang).count()
        for lang in ("ru", "fi", "en")
    }
    return render_template(
        "admin/dashboard.html",
        lang="ru",
        dashboard_stats=dashboard_stats,
        recent_logs=AdminLog.query.order_by(AdminLog.created_at.desc()).limit(5).all(),
        recent_messages=(
            ContactMessage.query
            .order_by(ContactMessage.created_at.desc())
            .limit(5)
            .all()
        ),
        recent_articles=(
            GuideArticle.query
            .order_by(GuideArticle.created_at.desc())
            .limit(5)
            .all()
        ),
        language_article_counts=language_article_counts,
    )


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


FI_HENKILOTUNNUS_SUMMARY = (
    "Selkeä opas henkilötunnukseen Suomessa: miksi sitä tarvitaan, "
    "miten haet sitä DVV:n kautta ja miten valmistaudut tapaamiseen."
)

FI_HENKILOTUNNUS_CONTENT = """## Mikä henkilötunnus on?

Henkilötunnus on suomalainen henkilökohtainen tunniste. Se auttaa viranomaisia ja palveluita tunnistamaan sinut luotettavasti.

Numeroa tarvitaan usein heti, kun rakennat arkea Suomessa. Ilman sitä monet palvelut ja verkkopalvelut eivät avaudu tai eteneminen hidastuu.

Henkilötunnus on henkilökohtainen tieto, jota ei saa jakaa turhaan.

## Mihin henkilötunnusta tarvitaan?

Henkilötunnus voi olla tarpeen esimerkiksi:

• Kelan etuuksien hakemisessa
• pankkitilin avaamisessa
• työsuhteessa ja palkan maksamisessa
• terveydenhuollossa
• veroasioiden hoitamisessa Verohallinnossa
• Suomen viranomaispalveluissa

Ilman henkilötunnusta voit joutua toistamaan samoja vaiheita useassa paikassa. Selvitä hakemisen polku ajoissa.

## Kuka voi saada henkilötunnuksen?

Saaminen riippuu siitä, miksi oleskelet Suomessa ja mitä asiakirjoja sinulla on.

Yleensä henkilötunnus voidaan myöntää:

• EU- ja ETA-maiden kansalaisille, jotka muuttavat Suomeen
• henkilöille, joilla on voimassa oleva oleskelulupa tai muu asumiseen oikeuttava asiakirja
• Suomeen muuttaville, jotka rekisteröivät oleskelunsa ja täyttävät DVV:n tai Migrin vaatimukset

Joissakin tilanteissa asia käsitellään Migrin kautta, toisissa DVV:n kautta. Tarkista aina virallinen ohje.

## Mikä on DVV?

DVV (Digi- ja väestötietovirasto) ylläpitää väestötietoja ja rekisteröi henkilötiedot sekä osoitteet.

DVV:hen otetaan yhteyttä, kun sinun täytyy rekisteröidä tietosi Suomeen tai saada henkilötunnus. Sivuilla näet, mikä palvelu sopii tilanteeseesi.

## Vaiheittaiset ohjeet

### Vaihe 1. Valmistele asiakirjat

Ota mukaan passi tai henkilökortti ja asiakirja, jolla osoitat oikeuden oleskella Suomessa. Pidä työ- tai opiskelusopimus saatavilla, jos se liittyy oleskeluusi.

### Vaihe 2. Varaa aika tai tarkista DVV:n ohjeet

Tarkista DVV:n ohjeesta, tarvitsetko ajanvarauksen.

[[action: Avaa DVV:n ohje henkilötunnuksesta|https://dvv.fi/henkilotunnus]]

[[action: Varaa aika DVV:hen|https://secure.vihta.com/public-ng/dvv/#/reservation?service=HLO]]

Jos ohje on vaikea ymmärtää, pyydä apua tai tulkkausta ennen tapaamista.

### Vaihe 3. Käy DVV:ssä

Saavu ajoissa ja ota alkuperäiset asiakirjat mukaan. Kerro tarvittaessa, että tarvitset viittomakielen tulkin.

### Vaihe 4. Todista henkilöllisyytesi

DVV tarkistaa henkilöllisyytesi ja asiakirjat. Jos jokin puuttuu, saat yleensä tietoa siitä, mitä vielä tarvitaan.

### Vaihe 5. Odota rekisteröintiä

Kun tiedot on käsitelty, sinulle voidaan myöntää henkilötunnus. Päivitä tarvittavat tiedot Kelaan ja pankkiin.

[[action: Tutustu Kelaan|/fi/guide/kela]]

## Mitä asiakirjoja tarvitaan?

Usein tarvitaan:

• passi tai voimassa oleva henkilökortti
• oleskelulupa tai muu asiakirja, joka osoittaa oikeuden oleskella Suomessa
• tiedot Suomen osoitteesta
• työsopimus tai opiskelutodistus, jos ne liittyvät oleskeluusi
• perheenjäsenten asiakirjat, jos rekisteröidään koko perhettä

Tarkista ajantasainen lista virallisesta ohjeesta ennen käyntiä.

## Hyödyllistä tietää

• Säilytä henkilötunnus turvallisessa paikassa. Älä lähetä sitä tuntemattomille.
• Ilmoita osoitteenmuutoksesta viipymättä DVV:lle.
• Tarkista omat tiedot OmaSuomi-palvelusta, kun tunnistautuminen on käytössä.
• Henkilötunnus pysyy yleensä samana myös muuton jälkeen, mutta osoite pitää päivittää.
• Jos saat kirjeen, jonka et ymmärrä, säilytä se. SKMY voi auttaa ymmärtämään sen.

[[action: Lue osoitteen rekisteröinnistä|/fi/guide/dvv/registration]]

## Viittomakielen tulkkaus

Jos tarvitset viittomakielen tulkin DVV-tapaamiseen, tilaus kannattaa tehdä etukäteen. Kun sinulla on Kelan myöntämä oikeus, palvelun voi tilata virallisen järjestelmän kautta.

[[action: Avaa viittomakielen tulkkaus|/fi/interpreting]]

[[action: Lue Kelan tulkkauspalvelusta|/fi/guide/kela/interpreter]]

## Tarvitsetko apua?

Jos et ole varma, mihin ottaa yhteyttä tai mitä asiakirjoja tarvitaan, kirjoita SKMY:lle. Autamme löytämään tiedon ja seuraavan askeleen.

[[action: Ota yhteyttä SKMY:hyn|/fi/contacts]]

## UKK

Kysymys: Kuinka kauan käsittely kestää?
Vastaus: Käsittelyaika riippuu tilanteestasi ja asiakirjoista. Tarkista ajankohtainen tieto DVV:n tai Migrin virallisesta ohjeesta.

Kysymys: Voinko saada henkilötunnuksen ilman pankkitunnuksia?
Vastaus: Kyllä. Henkilötunnuksen saaminen ja pankkitunnukset ovat erillisiä asioita. Pankkitunnuksia tarvitaan usein myöhemmin verkkopalveluihin.

Kysymys: Tarvitsenko ajanvarauksen?
Vastaus: Usein kyllä, mutta se riippuu palvelusta. Tarkista DVV:n virallisesta ohjeesta, tarvitseeko sinun varata aika.

Kysymys: Mitä teen, jos tietoni muuttuvat?
Vastaus: Ilmoita muutoksesta DVV:lle ja tarvittaessa muille viranomaisille. Henkilötunnus itsessään ei yleensä muutu."""

FI_HENKILOTUNNUS_OFFICIAL_LINKS = """DVV:n ohje: henkilötunnus|https://dvv.fi/henkilotunnus
Ulkomaalaisen rekisteröinti|https://dvv.fi/ulkomaalaisen-rekisterointi
Ajanvaraus DVV:hen|https://secure.vihta.com/public-ng/dvv/#/reservation?service=HLO"""

FI_HENKILOTUNNUS_KEYWORDS = (
    "henkilötunnus, DVV, rekisteröinti Suomessa, henkilötunnuksen saaminen, väestötiedot"
)


@app.cli.command("seed-fi-guide")
def seed_fi_guide():
    """Create or update the Finnish guide categories and minimum article set."""
    category_data = [
        ("dvv", "DVV", "Henkilötunnus, rekisteröinti, osoite ja henkilötiedot."),
        ("kela", "Kela", "Etuudet, OmaKela, tuki ja tulkkauspalvelu."),
        ("te", "TE-palvelut", "Työnhaku, työnhakijaksi ilmoittautuminen ja koulutus."),
        ("migri", "Migri", "Oleskelulupa, jatkolupa ja kansalaisuus."),
        ("health", "Terveydenhuolto", "Terveysasema, hammashoito ja kiireellinen apu."),
        ("family", "Perhe", "Avioliitto, lapset, perheen rekisteröinti ja sosiaalinen tuki."),
    ]
    categories = {}
    for order, (slug, title, description) in enumerate(category_data, start=1):
        category = GuideCategory.query.filter_by(language="fi", slug=slug).first()
        if not category:
            category = GuideCategory(language="fi", slug=slug)
            db.session.add(category)
        category.title = title
        category.description = description
        category.sort_order = order
        category.is_active = True
        categories[slug] = category
    db.session.flush()

    articles = [
        ("dvv", "henkilotunnus", "Henkilötunnus", FI_HENKILOTUNNUS_SUMMARY, FI_HENKILOTUNNUS_CONTENT),
        ("dvv", "registration", "Osoitteen rekisteröinti", "Miten ilmoitat osoitteesi ja rekisteröit asumisesi Suomessa.", "## Miksi osoite rekisteröidään?\nOsoitetiedot auttavat viranomaisia ja palveluja tavoittamaan sinut.\n\n## Näin etenet\nIlmoita muutosta tai Suomen osoitteesta DVV:lle. Tarvitset yleensä henkilöllisyystodistuksen ja tiedot asumisesta.\n\n[[Ilmoita muutosta DVV:lle|https://dvv.fi/muutto]]"),
        ("kela", "omakela", "OmaKela", "Näin käytät OmaKelaa etuuksien hakemiseen ja omien tietojen tarkistamiseen.", "## Mikä OmaKela on?\nOmaKela on Kelan verkkopalvelu. Siellä voit hakea etuuksia, lähettää liitteitä ja seurata hakemuksiasi.\n\n## Kirjautuminen\nTarvitset yleensä vahvan tunnistautumisen, esimerkiksi pankkitunnukset tai mobiilivarmenteen.\n\n[[Avaa OmaKela|https://www.kela.fi/omakela]]"),
        ("kela", "interpreter", "Tulkkauspalvelu", "Miten haet oikeutta Kelan tulkkauspalveluun ja tilaat tulkin.", "## Kenelle palvelu on tarkoitettu?\nKela voi järjestää tulkkauspalvelua henkilölle, jolla on kuulon, näön tai puheen vuoksi vaikeuksia viestiä.\n\n## Hae oikeutta palveluun\nTutustu Kelan ohjeisiin ja toimita tarvittavat selvitykset. Kun oikeus on myönnetty, tulkin voi tilata tapaamisiin.\n\n[[Kelan tulkkauspalvelu|https://www.kela.fi/vammaisten-tulkkauspalvelu]]"),
        ("te", "job-search", "Työnhaku", "Mistä aloittaa työnhaku ja miten saat tukea Suomessa.", "## Aloita työnhaku\nEtsi avoimia työpaikkoja ja pidä ansioluettelosi ajan tasalla. Työllisyyspalvelut voivat neuvoa työnhaussa ja koulutuksessa.\n\n## Hyödyllistä valmistautumista\n• tee selkeä CV\n• kerää todistukset ja aiemmat työtiedot\n• selvitä, tarvitsetko tulkkausta tapaamiseen\n\n[[Työmarkkinatori|https://tyomarkkinatori.fi/]]"),
        ("migri", "residence-permit", "Oleskelulupa", "Perustiedot ensimmäisestä oleskeluluvasta ja luvan jatkamisesta.", "## Milloin oleskelulupaa tarvitaan?\nOleskelulupaa tarvitaan tilanteissa, joissa Suomen oleskelun peruste sitä edellyttää. Tarkista oma tilanteesi Migrin ohjeista.\n\n## Hakeminen\nTäytä hakemus huolellisesti, liitä vaaditut asiakirjat ja seuraa hakemuksen käsittelyä Enter Finland -palvelussa.\n\n[[Migri: oleskeluluvat|https://migri.fi/oleskelulupa]]"),
        ("health", "health-station", "Terveysasema", "Miten käytät terveysaseman palveluja Suomessa.", "## Milloin terveysasemalle?\nTerveysasema auttaa tavallisissa terveysongelmissa, pitkäaikaissairauksissa ja hoidon tarpeen arvioinnissa.\n\n## Varaa aika\nOta yhteyttä oman alueesi terveysasemaan. Kerro, jos tarvitset viittomakielen tulkin tapaamiseen. Hätätilanteessa soita numeroon 112.\n\n[[Tietoa terveyspalveluista|https://www.suomi.fi/]]"),
        ("family", "family-registration", "Perheen rekisteröinti Suomessa", "Miten perheen tiedot ja elämäntilanne voivat vaikuttaa viranomaisasiointiin Suomessa.", "## Perheen tiedot\nPerheenjäsenet, avioliitto ja lasten tiedot voivat edellyttää rekisteröintiä Suomessa. Tarvittavat asiakirjat riippuvat tilanteesta.\n\n## Mistä saat apua?\nDVV neuvoo väestötietoihin liittyvissä asioissa. Migri neuvoo oleskelulupiin liittyvissä perhetilanteissa.\n\n[[DVV:n palvelut|https://dvv.fi/]]"),
    ]
    for order, (category_slug, slug, title, summary, content) in enumerate(articles, start=1):
        category = categories[category_slug]
        article = GuideArticle.query.filter_by(category_id=category.id, language="fi", slug=slug).first()
        if not article:
            article = GuideArticle(category_id=category.id, language="fi", slug=slug)
            db.session.add(article)
        article.title = title
        article.summary = summary
        article.content = content
        article.sort_order = order
        article.is_published = True
        if slug == "henkilotunnus" and category_slug == "dvv":
            article.official_links = FI_HENKILOTUNNUS_OFFICIAL_LINKS
            article.keywords = FI_HENKILOTUNNUS_KEYWORDS
    db.session.commit()
    print("Finnish guide data created or updated.")


if __name__ == "__main__":
    app.run(debug=True)
