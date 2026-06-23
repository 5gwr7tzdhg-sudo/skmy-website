import os
from datetime import datetime

import click
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from database.db import db
from database import models
from database.migrations.translation_keys_20260623 import upgrade as upgrade_translation_keys
from database.migrations.news_translation_groups import upgrade as upgrade_news_translation_groups

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
        "draft_articles": GuideArticle.query.filter_by(is_published=False).count(),
        "draft_news": News.query.filter_by(is_published=False).count(),
        "drafts": (
            GuideArticle.query.filter_by(is_published=False).count()
            + News.query.filter_by(is_published=False).count()
        ),
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


@app.cli.command("migrate-translation-keys")
def migrate_translation_keys():
    upgrade_translation_keys(db.engine)
    print("Translation-key migration applied.")


@app.cli.command("migrate-news-translation-groups")
def migrate_news_translation_groups():
    """Allow translated news versions to share a translation key."""
    upgrade_news_translation_groups(db.engine)
    print("News translation-group migration applied.")


INITIAL_NEWS_TRANSLATION_GROUPS = (
    {
        "fi": "skmy-perustettiin-27-10-2025",
        "ru": "skmy-osnovana-27-10-2025",
        "en": "skmy-founded-27-10-2025",
    },
    {
        "fi": "kiitos-kuurojen-liitolle-yhteistyosta-ja-tuesta",
        "ru": "spasibo-kuurojen-liitto-za-sotrudnichestvo-i-podderzhku",
        "en": "thank-you-kuurojen-liitto-for-cooperation-and-support",
    },
    {
        "fi": "skmy-n-verkkosivusto-julkaistu",
        "ru": "veb-sait-skmy-opublikovan",
        "en": "skmy-website-launched",
    },
)


@app.cli.command("link-initial-news-translations")
def link_initial_news_translations():
    """Link only the three verified FI/RU/EN initial news groups."""
    grouped_items = []
    for group in INITIAL_NEWS_TRANSLATION_GROUPS:
        items = {
            language: News.query.filter_by(language=language, slug=slug).one_or_none()
            for language, slug in group.items()
        }
        missing_languages = [language for language, item in items.items() if item is None]
        if missing_languages:
            raise click.ClickException(
                "Cannot link a news group with missing languages: "
                + ", ".join(missing_languages)
            )
        grouped_items.append(items)

    for items in grouped_items:
        shared_key = items["fi"].translation_key
        for language in ("ru", "en"):
            items[language].translation_key = shared_key

    db.session.commit()
    print("Three verified initial FI/RU/EN news groups linked.")


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

RU_HENKILOTUNNUS_SUMMARY = (
    "Понятная инструкция: что такое henkilötunnus, зачем он нужен, "
    "где его получить и как подготовиться к обращению в DVV."
)

RU_HENKILOTUNNUS_CONTENT = """## Что такое henkilötunnus?

Henkilötunnus — это финский личный идентификационный номер. Он помогает подтвердить личность при обращении в государственные службы и многие частные организации.

Это личная информация: не передавайте номер незнакомым людям без необходимости.

## Для чего он нужен?

Henkilötunnus может понадобиться для:

• регистрации места жительства и личных данных
• обращения в Kela
• открытия банковского счёта
• трудоустройства и получения зарплаты
• получения медицинских услуг
• использования государственных электронных сервисов

## Где его получить?

В зависимости от вашей ситуации номер могут присвоить через Migri при рассмотрении заявления о разрешении на проживание или через DVV (Digital and Population Data Services Agency). DVV ведёт реестр населения и помогает зарегистрировать данные после переезда в Финляндию.

Проверьте на официальной странице DVV, подходит ли вам обращение в DVV и нужно ли записываться на приём.

[[action: Открыть официальную инструкцию DVV|https://dvv.fi/en/foreigner-registration]]

## Что взять с собой?

Обычно полезно иметь:

• паспорт или другое действующее удостоверение личности
• документ о праве на пребывание в Финляндии
• адрес проживания в Финляндии, если он уже известен
• договор о работе или справку от работодателя, если вы работаете
• документ об учёбе, если вы учитесь
• документы о семье, если вы регистрируетесь вместе с семьёй

DVV может попросить дополнительные документы. Перед визитом проверьте актуальный список в официальной инструкции.

## Как действовать?

### Шаг 1. Подготовьте документы

Соберите оригиналы документов и проверьте, что они действительны. Если вам нужна помощь с письмом или формой, попросите объяснить текст до посещения DVV.

### Шаг 2. Запишитесь на приём, если это нужно

Выберите услугу и время через официальную систему DVV. Заполняйте данные внимательно.

[[action: Записаться на приём в DVV|https://secure.vihta.com/public-ng/dvv/#/reservation?service=HLO]]

### Шаг 3. Подготовьтесь к общению

Если для приёма нужен сурдопереводчик, закажите его заранее. Если право на переводческие услуги ещё не оформлено, посмотрите инструкции SKMY.

[[action: Открыть раздел «Сурдоперевод»|/ru/interpreting]]

### Шаг 4. Посетите DVV

Сотрудник проверит личность и документы. Если чего-то не хватает, вам объяснят, какие сведения или документы нужно добавить.

## Что делать дальше?

После присвоения henkilötunnus сохраните решение и используйте номер только там, где он действительно нужен. При необходимости обновите сведения в Kela, банке, у работодателя или в других службах.

Номер обычно остаётся тем же даже при переезде в другой город, но новый адрес нужно сообщать в нужные службы.

Если письмо или решение непонятно, сохраните его и обратитесь в SKMY за помощью в понимании дальнейших шагов.

## FAQ

Вопрос: Можно ли получить henkilötunnus сразу после приезда?
Ответ: Это зависит от вашей ситуации и документов. Проверьте подходящий порядок на официальном сайте DVV или Migri.

Вопрос: Нужно ли получать новый номер после переезда?
Ответ: Нет, номер обычно не меняется. Но новый адрес важно сообщить в нужные службы.

Вопрос: Что делать, если я не понимаю форму или письмо?
Ответ: Попросите объяснить текст простыми словами. Можно обратиться в DVV, Migri, SKMY или к человеку, которому вы доверяете."""

EN_HENKILOTUNNUS_SUMMARY = (
    "A clear guide to what a personal identity code is, why you need it, "
    "where to get it and how to prepare for DVV."
)

EN_HENKILOTUNNUS_CONTENT = """## What is a personal identity code?

A Finnish personal identity code (henkilötunnus) is a personal identifier used to confirm your identity with public authorities and many private services.

Treat it as personal information and do not share it unnecessarily.

## What do you need it for?

You may need a personal identity code for:

• registering your personal details and address
• applying for Kela benefits
• opening a bank account
• employment and salary payments
• healthcare services
• using public online services

## Where can you get it?

Depending on your situation, the code may be issued by Migri while your residence-permit application is processed, or by DVV (the Digital and Population Data Services Agency). DVV maintains population data and can register your details after you move to Finland.

Check DVV's official instructions to see which route applies to you and whether you need an appointment.

[[action: Open DVV's official guidance|https://dvv.fi/en/foreigner-registration]]

## What should you take with you?

It is usually helpful to bring:

• a passport or other valid identity document
• proof of your right to stay in Finland
• your Finnish address, if known
• a work contract or employer's certificate, if you work
• proof of studies, if you study
• family documents, if you register with family members

DVV may ask for further documents, so check its current guidance before visiting.

## What happens next?

Prepare your documents, book an appointment if needed, and attend DVV with the original documents. If you need a sign-language interpreter for the appointment, arrange it in advance.

[[action: Book a DVV appointment|https://secure.vihta.com/public-ng/dvv/#/reservation?service=HLO]]

After your details have been processed, use the code only where it is needed. You may also need to update your details with Kela, your bank or employer. The code normally stays the same when you move, but your address should be kept up to date.

## FAQ

Question: Can I get a personal identity code immediately after arriving?
Answer: It depends on your situation and documents. Check the official guidance from DVV or Migri for the route that applies to you.

Question: Do I need a new code after moving to another city?
Answer: No. The code normally stays the same, but you should report your new address to the relevant services."""

HENKILOTUNNUS_OFFICIAL_LINKS = (
    "DVV: registration of a foreigner|https://dvv.fi/en/foreigner-registration"
)


def upsert_henkilotunnus_article(language, title, summary, content):
    category = GuideCategory.query.filter_by(language=language, slug="dvv").first()
    if not category:
        category = GuideCategory(
            language=language,
            slug="dvv",
            title="DVV",
            description="Personal identity codes, registration, addresses and personal data.",
            sort_order=1,
            is_active=True,
        )
        db.session.add(category)
        db.session.flush()

    article = GuideArticle.query.filter_by(
        category_id=category.id, language=language, slug="henkilotunnus"
    ).first()
    if not article:
        article = GuideArticle(category_id=category.id, language=language, slug="henkilotunnus")
        db.session.add(article)

    article.title = title
    article.summary = summary
    article.content = content
    article.official_links = HENKILOTUNNUS_OFFICIAL_LINKS
    article.keywords = "henkilötunnus, personal identity code, DVV, registration in Finland"
    article.is_published = True
    article.sort_order = 1


@app.cli.command("seed-henkilotunnus-localizations")
def seed_henkilotunnus_localizations():
    """Create or update the Russian and English henkilötunnus guide articles."""
    upsert_henkilotunnus_article(
        "ru", "Как получить henkilötunnus", RU_HENKILOTUNNUS_SUMMARY, RU_HENKILOTUNNUS_CONTENT
    )
    upsert_henkilotunnus_article(
        "en", "How to get a personal identity code", EN_HENKILOTUNNUS_SUMMARY, EN_HENKILOTUNNUS_CONTENT
    )
    db.session.commit()
    print("Russian and English henkilötunnus articles created or updated.")


FI_NEWS_ITEMS = [
    {
        "slug": "skmy-perustettiin-27-10-2025",
        "title": "SKMY perustettiin 27.10.2025",
        "summary": "SKMY aloittaa toimintansa yhteisönä, joka kokoaa ihmisiä, tietoa ja tukea yhteen.",
        "content": """27.10.2025 on SKMY:lle merkittävä päivä: yhdistys perustettiin vahvistamaan yhteisöllisyyttä, osallisuutta ja arjen mahdollisuuksia Suomessa. Perustaminen on samalla lupaus siitä, että jokaisella on oikeus saada tietoa ymmärrettävästi, tulla kuulluksi ja löytää oma paikkansa yhteisössä.

SKMY:n toiminnan lähtökohtana ovat ihmiset ja heidän todelliset elämäntilanteensa. Uuteen maahan asettuminen, palvelujen käyttäminen ja omien oikeuksien selvittäminen voivat herättää paljon kysymyksiä. Haluamme olla mukana tekemässä näistä asioista selkeämpiä: jakaa luotettavaa tietoa, ohjata oikeiden palvelujen äärelle ja luoda kohtaamisia, joissa kokemuksia voi vaihtaa turvallisesti.

Yhdistystä rakennetaan yhdessä jäsenien, vapaaehtoisten ja yhteistyökumppaneiden kanssa. Toiminta kehittyy vähitellen tarpeiden ja palautteen perusteella. Tavoitteena on tarjota tilaa vertaistuelle, osallistumiselle ja uusille ideoille sekä vahvistaa yhteyksiä eri toimijoiden välillä.

Perustamispäivä on alku pitkälle yhteiselle matkalle. Kiitämme kaikkia, jotka ovat olleet mukana ajatuksen syntymisessä ja tukeneet ensimmäisiä askeleita. Toivomme, että mahdollisimman moni löytää SKMY:stä hyödyllistä tietoa, tuttua seuraa ja mahdollisuuden vaikuttaa. Seuraa uutisiamme ja tule mukaan rakentamaan yhdistyksen seuraavia vaiheita.

Tulevina kuukausina kerromme sivustolla tarkemmin toiminnan suunnasta, mahdollisuuksista osallistua ja tavoista olla yhteydessä. Haluamme rakentaa toimintaa avoimesti: pienetkin havainnot ja ehdotukset ovat tervetulleita. Yhdistyksen vahvuus syntyy erilaisista ihmisistä, kielistä, taustoista ja taidoista. Kun tietoa ja kokemuksia jaetaan, useampi voi löytää arjessaan varmuutta ja mahdollisuuksia. Tämä on SKMY:n yhteinen lähtöpiste, josta rakennetaan kestävää toimintaa yhdessä kaikkien kanssa.""",
        "published_at": datetime(2025, 10, 27, 12, 0),
    },
    {
        "slug": "kiitos-kuurojen-liitolle-yhteistyosta-ja-tuesta",
        "title": "Kiitos Kuurojen Liitolle yhteistyöstä ja tuesta",
        "summary": "Kuurojen Liiton yhteistyö ja tuki ovat olleet SKMY:lle arvokkaita toiminnan käynnistämisessä.",
        "content": """SKMY haluaa lämpimästi kiittää Kuurojen Liittoa yhteistyöstä ja tuesta yhdistyksen toiminnan alkuvaiheessa. Uutta yhteisöä rakennettaessa kannustus, asiantuntemus ja mahdollisuus keskustella kokemuksista merkitsevät paljon. Kuurojen Liiton tuki on auttanut meitä ottamaan ensimmäisiä askelia määrätietoisesti ja luottavaisesti.

Yhteistyössä tärkeintä on yhteinen tavoite: että kuurot ihmiset voivat osallistua yhteiskuntaan omilla ehdoillaan, saada tietoa saavutettavasti ja kohdata palveluissa yhdenvertaisesti. SKMY:n näkökulmasta erityisen tärkeää on huomioida myös ne ihmiset, joiden arjessa yhdistyvät kuurous, maahanmuutto ja uuden elämän rakentaminen Suomessa. Näissä tilanteissa selkeä tieto, vertaisverkostot ja toimivat yhteydet voivat tehdä suuren eron.

Arvostamme Kuurojen Liiton pitkää työtä viittomakielisten ja kuurojen ihmisten oikeuksien, osallisuuden ja hyvinvoinnin puolesta. Saamamme tuki rohkaisee SKMY:tä kehittämään omaa toimintaansa vastuullisesti ja kuuntelemaan yhteisön tarpeita tarkasti. Samalla se muistuttaa siitä, että kestäviä muutoksia syntyy parhaiten yhteistyöllä.

Toivomme, että yhteistyö jatkuu myös tulevaisuudessa eri muodoissa: tiedon jakamisena, kokemusten vaihtamisena ja yhteisten mahdollisuuksien tunnistamisena. Kiitos Kuurojen Liitolle luottamuksesta, ajasta ja tuesta. Rakennamme yhdessä avoimempaa, saavutettavampaa ja yhdenvertaisempaa Suomea.

SKMY sitoutuu pitämään yhteistyön käytännöllisenä ja vuorovaikutteisena. Kuuntelemme yhteisön ääntä, jaamme oppimaamme sekä etsimme ratkaisuja tilanteisiin, joissa tieto tai palvelut eivät vielä kohtaa ihmisten tarpeita. Yhteinen työ voi näkyä joskus pieninä tekoina, joskus laajempina avauksina, mutta jokainen askel kohti parempaa saavutettavuutta on arvokas. Meille on tärkeää, että yhteistyö rakentuu kunnioitukselle, selkeälle viestinnälle ja aidolle halulle oppia toisiltamme.""",
        "published_at": datetime.utcnow(),
    },
    {
        "slug": "skmy-n-verkkosivusto-julkaistu",
        "title": "SKMY:n verkkosivusto on julkaistu",
        "summary": "SKMY:n uusi verkkosivusto kokoaa yhdistyksen uutiset, tiedon ja yhteydenpitokanavat yhteen paikkaan.",
        "content": """SKMY:n verkkosivusto on nyt julkaistu. Sivusto on uusi yhteinen paikka, josta löydät yhdistyksen ajankohtaiset uutiset, perustiedot ja yhteystiedot. Haluamme tehdä tiedon löytämisestä mahdollisimman helppoa sekä jäsenille, yhteistyökumppaneille että kaikille SKMY:n toiminnasta kiinnostuneille.

Sivustolla kerromme yhdistyksen toiminnasta, julkaistavista tapahtumista ja muista tärkeistä ilmoituksista. Uutisosio auttaa seuraamaan, mitä SKMY:ssä tapahtuu juuri nyt, ja yhteystietosivun kautta voi ottaa meihin yhteyttä. Sivustoa kehitetään jatkuvasti, joten sisältöä ja toimintoja lisätään sitä mukaa, kun toiminta kasvaa ja käyttäjiltä saadaan palautetta.

Saavutettavuus ja selkeys ovat sivuston suunnittelussa tärkeitä lähtökohtia. Pyrimme kirjoittamaan asiat ymmärrettävästi ja pitämään rakenteen rauhallisena, jotta tarvittava tieto löytyy ilman turhaa etsimistä. Jos jokin tieto puuttuu, on epäselvää tai sivuston käyttö tuntuu hankalalta, kerro siitä meille. Palaute auttaa tekemään palvelusta paremman kaikille.

Verkkosivusto ei korvaa kohtaamisia, mutta se auttaa pitämään yhteyttä myös niiden välillä. Toivomme, että sivuista tulee hyödyllinen väline arkeen: paikka, johon voi palata hakemaan tietoa, seuraamaan uutisia ja löytämään reitin mukaan toimintaan. Tervetuloa tutustumaan SKMY:n verkkosivustoon ja seuraamaan, kuinka yhteisömme kasvaa.

Julkaisu on ensimmäinen versio, ei valmis päätepiste. Seuraamme, mitkä sisällöt ovat hyödyllisimpiä ja missä kohtaa tietoa tarvitaan lisää. Päivitämme sivustoa säännöllisesti, jotta se pysyy ajantasaisena ja palvelee käyttäjiään mahdollisimman hyvin. Voit myös jakaa sivuston sellaiselle ihmiselle, jolle SKMY:n toiminta voisi olla tärkeää. Yhdessä tieto kulkee pidemmälle ja yhteisö on helpompi löytää.""",
        "published_at": datetime.utcnow(),
    },
]


LOCALIZED_NEWS_ITEMS = [
    {
        "language": "ru",
        "slug": "skmy-osnovana-27-10-2025",
        "title": "SKMY была основана 27.10.2025",
        "summary": "SKMY начинает работу как сообщество, объединяющее людей, знания и поддержку.",
        "content": """27 октября 2025 года стало важной датой для SKMY: в этот день была основана наша организация. Мы создаём сообщество, в котором ценятся участие, взаимная поддержка и возможность строить повседневную жизнь в Финляндии с большей уверенностью. Для нас это также обещание: каждый человек должен иметь возможность получать понятную информацию, быть услышанным и чувствовать себя частью сообщества.

В центре работы SKMY находятся люди и реальные ситуации, с которыми они сталкиваются. Переезд в новую страну, обращение в государственные службы и защита своих прав часто вызывают множество вопросов. Мы хотим сделать эти шаги понятнее: делиться надёжной информацией, помогать находить нужные услуги и создавать безопасные встречи для обмена опытом.

Организация будет развиваться вместе с участниками, волонтёрами и партнёрами. Мы будем внимательно слушать потребности сообщества и на их основе выстраивать деятельность. Наша цель — создать пространство для взаимной поддержки, участия и новых идей, а также укреплять связи между людьми и организациями.

Дата основания — это начало долгого общего пути. Мы благодарим всех, кто помог этой идее появиться и поддержал первые шаги SKMY. Надеемся, что здесь многие найдут полезную информацию, знакомых людей и возможность влиять на общее дело. Следите за новостями и присоединяйтесь к тому, что мы строим вместе.""",
        "published_at": datetime(2025, 10, 27, 12, 0),
    },
    {
        "language": "ru",
        "slug": "spasibo-kuurojen-liitto-za-sotrudnichestvo-i-podderzhku",
        "title": "Спасибо Kuurojen Liitto за сотрудничество и поддержку",
        "summary": "Сотрудничество и поддержка Kuurojen Liitto очень важны для начала работы SKMY.",
        "content": """SKMY сердечно благодарит Kuurojen Liitto за сотрудничество и поддержку на начальном этапе работы нашей организации. Когда создаётся новое сообщество, особенно ценны участие, профессиональный опыт и возможность обсудить первые решения с теми, кто хорошо знает сферу. Поддержка Kuurojen Liitto помогла нам сделать первые шаги уверенно и последовательно.

В основе нашего сотрудничества лежит общая цель: глухие люди должны иметь возможность участвовать в жизни общества на своих условиях, получать доступную информацию и встречать равное отношение в службах. Для SKMY особенно важно учитывать опыт людей, в жизни которых соединяются глухота, миграция и устройство жизни в Финляндии. В таких ситуациях понятная информация, поддержка равных и работающие контакты могут существенно изменить повседневную жизнь.

Мы высоко ценим многолетнюю работу Kuurojen Liitto в защиту прав, участия и благополучия глухих и пользователей жестовых языков. Полученная поддержка вдохновляет SKMY развивать деятельность ответственно, внимательно слушать сообщество и учиться у партнёров. Она также напоминает, что устойчивые изменения чаще всего рождаются в сотрудничестве.

Надеемся, что наше взаимодействие будет продолжаться в обмене знаниями, опытом и совместных инициативах. Спасибо Kuurojen Liitto за доверие, время и поддержку. Вместе мы помогаем делать Финляндию более открытой, доступной и равной для всех.""",
        "published_at": datetime.utcnow(),
    },
    {
        "language": "ru",
        "slug": "veb-sait-skmy-opublikovan",
        "title": "Веб-сайт SKMY опубликован",
        "summary": "Новый сайт SKMY собирает новости, информацию и каналы связи организации в одном месте.",
        "content": """Веб-сайт SKMY опубликован и открыт для посетителей. Это новое общее пространство, где можно найти актуальные новости организации, основную информацию и контактные данные. Мы хотим, чтобы нужная информация была легко доступна участникам, партнёрам и всем, кому интересна деятельность SKMY.

На сайте мы будем рассказывать о работе организации, предстоящих мероприятиях и важных объявлениях. Раздел новостей поможет следить за тем, что происходит в SKMY, а через страницу контактов можно связаться с нами. Сайт будет развиваться вместе с организацией: мы будем добавлять материалы и функции по мере роста деятельности и на основе отзывов пользователей.

При создании сайта для нас важны доступность и ясность. Мы стремимся писать понятно и сохранять спокойную, логичную структуру, чтобы информацию не приходилось долго искать. Если чего-то не хватает, формулировка остаётся неясной или пользоваться сайтом неудобно, пожалуйста, сообщите нам об этом. Ваш отзыв поможет сделать сайт лучше для всех.

Сайт не заменяет личные встречи, но помогает оставаться на связи между ними. Надеемся, что он станет полезным инструментом в повседневной жизни: местом, куда можно вернуться за информацией, новостями и возможностью присоединиться к деятельности SKMY. Добро пожаловать на сайт SKMY — будем расти вместе.""",
        "published_at": datetime.utcnow(),
    },
    {
        "language": "en",
        "slug": "skmy-founded-27-10-2025",
        "title": "SKMY was founded on 27 October 2025",
        "summary": "SKMY begins its work as a community that brings people, information and support together.",
        "content": """27 October 2025 is an important date for SKMY: our association was founded to strengthen community, participation and everyday opportunities in Finland. Its founding is also a promise that everyone should be able to receive clear information, be heard and find their place in a community.

SKMY starts with people and their real-life situations. Settling in a new country, using public services and understanding one’s rights can raise many questions. We want to make these matters easier to approach by sharing reliable information, guiding people to the right services and creating safe opportunities to exchange experiences.

The association will be built together with members, volunteers and partners. Its activities will develop gradually through needs and feedback. Our aim is to provide room for peer support, participation and new ideas, while strengthening links between people and organisations.

The founding date is the beginning of a long shared journey. We thank everyone who helped the idea take shape and supported SKMY’s first steps. We hope that many people will find useful information, familiar company and a chance to make a difference through SKMY. Follow our news and join us as we build the next stages of the association together.""",
        "published_at": datetime(2025, 10, 27, 12, 0),
    },
    {
        "language": "en",
        "slug": "thank-you-kuurojen-liitto-for-cooperation-and-support",
        "title": "Thank you to Kuurojen Liitto for cooperation and support",
        "summary": "Kuurojen Liitto’s cooperation and support have been valuable as SKMY begins its work.",
        "content": """SKMY warmly thanks Kuurojen Liitto for its cooperation and support during the first stage of our association’s work. When a new community is being built, encouragement, professional knowledge and the chance to discuss early decisions are especially meaningful. Kuurojen Liitto’s support has helped us take our first steps with confidence and purpose.

Our cooperation is based on a shared goal: deaf people should be able to participate in society on their own terms, receive accessible information and be treated equally when using services. For SKMY, it is particularly important to recognise the experiences of people whose daily lives include deafness, migration and building a new life in Finland. In these situations, clear information, peer networks and working connections can make a real difference.

We value Kuurojen Liitto’s long-standing work for the rights, participation and wellbeing of deaf and sign-language users. The support we have received encourages SKMY to develop its activities responsibly, listen carefully to the community and learn from its partners. It also reminds us that lasting change is usually created through cooperation.

We hope our cooperation will continue through shared information, exchange of experience and new joint opportunities. Thank you to Kuurojen Liitto for your trust, time and support. Together, we are helping to build a more open, accessible and equal Finland.""",
        "published_at": datetime.utcnow(),
    },
    {
        "language": "en",
        "slug": "skmy-website-launched",
        "title": "SKMY’s website has been launched",
        "summary": "SKMY’s new website brings together the association’s news, information and contact channels.",
        "content": """SKMY’s website has now been launched. It is a shared place where you can find current news, key information about the association and contact details. We want information to be easy to find for members, partners and everyone interested in SKMY’s work.

The website will share information about our activities, upcoming events and other important announcements. The news section makes it easier to follow what is happening at SKMY, and the contact page provides a direct way to reach us. The site will continue to develop as the association grows and as we receive feedback from its users.

Accessibility and clarity are important starting points in the design of this website. We aim to write in plain language and keep the structure calm and logical, so that visitors can find what they need without unnecessary searching. If information is missing, unclear or difficult to use, please let us know. Your feedback will help us improve the service for everyone.

The website does not replace meeting in person, but it helps us stay connected between meetings. We hope it becomes a useful everyday resource: a place to return to for information, news and ways to take part in SKMY’s activities. Welcome to the SKMY website, and follow how our community grows.""",
        "published_at": datetime.utcnow(),
    },
]


def upsert_news_item(item):
    matches = (
        News.query
        .filter_by(language=item["language"], slug=item["slug"])
        .order_by(News.id.asc())
        .all()
    )
    news_item = matches[0] if matches else News(
        language=item["language"], slug=item["slug"]
    )
    if not matches:
        db.session.add(news_item)

    for duplicate in matches[1:]:
        db.session.delete(duplicate)

    news_item.title = item["title"]
    news_item.summary = item["summary"]
    news_item.content = item["content"]
    news_item.is_published = True
    news_item.published_at = item["published_at"]


@app.cli.command("seed-fi-news")
def seed_fi_news():
    """Create or update the three initial Finnish SKMY news articles."""
    for item in FI_NEWS_ITEMS:
        upsert_news_item({"language": "fi", **item})

    db.session.commit()
    print("Three Finnish SKMY news articles created or updated.")


@app.cli.command("seed-localized-news")
def seed_localized_news():
    """Create or update the Russian and English versions of the initial news."""
    for item in LOCALIZED_NEWS_ITEMS:
        upsert_news_item(item)

    db.session.commit()
    print("Six Russian and English SKMY news articles created or updated.")


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
            "summary": RU_HENKILOTUNNUS_SUMMARY,
            "content": RU_HENKILOTUNNUS_CONTENT,
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


PRIORITY_GUIDE_CATEGORIES = {
    "fi": {
        "dvv": ("DVV", "Henkilötunnus, kotikunta, osoite ja väestötiedot."),
        "kela": ("Kela", "Etuudet, OmaKela ja vammaisten tulkkauspalvelu."),
        "te": ("TE-palvelut", "Työnhaku ja työnhakijaksi ilmoittautuminen."),
        "migri": ("Migri", "Oleskelulupa, hakemus ja Enter Finland."),
    },
    "ru": {
        "dvv": ("DVV", "Henkilötunnus, муниципалитет проживания, адрес и данные населения."),
        "kela": ("Kela", "Пособия, OmaKela и услуга сурдоперевода."),
        "te": ("TE-palvelut", "Поиск работы и регистрация соискателем."),
        "migri": ("Migri", "ВНЖ, заявление и Enter Finland."),
    },
    "en": {
        "dvv": ("DVV", "Personal identity code, municipality of residence, address and population data."),
        "kela": ("Kela", "Benefits, OmaKela and disability interpreting services."),
        "te": ("TE-palvelut", "Job search and jobseeker registration."),
        "migri": ("Migri", "Residence permits, applications and Enter Finland."),
    },
}

PRIORITY_GUIDE_TOPICS = (
    ("dvv", "municipality-of-residence", "https://dvv.fi/en/municipality-of-residence"),
    ("kela", "applying-for-benefits", "https://www.kela.fi/"),
    ("kela", "interpreting-service", "https://www.kela.fi/disability-interpreting-service"),
    ("migri", "enter-finland", "https://migri.fi/en/enter-finland"),
    ("te", "jobseeker-registration", "https://tyomarkkinatori.fi/en"),
)

PRIORITY_GUIDE_COPY = {
    "fi": {
        "municipality-of-residence": ("Kotikunta Suomessa: näin aloitat", "Mitä kotikunta tarkoittaa ja miten valmistaudut DVV:n palveluun.", "Kotikunta voi vaikuttaa siihen, mitä julkisia palveluja voit käyttää. Tarkista oma tilanteesi aina DVV:n ajantasaisesta ohjeesta.", "Tarkista ensin, täyttyvätkö kotikunnan ehdot omassa tilanteessasi.", "Ota mukaan henkilöllisyystodistus ja asumiseen liittyvät asiakirjat.", "Tee ilmoitus tai varaa aika DVV:n ohjeen mukaisesti.", "Mitä asiakirjoja tarvitsen?", "Asiakirjat riippuvat tilanteestasi. Tarkista DVV:n ohje ennen asiointia."),
        "applying-for-benefits": ("Kelan etuuksien hakeminen: vaiheittainen opas", "Näin valmistaudut Kelan hakemukseen ja seuraat sitä OmaKelassa.", "Etuus ja liitteet riippuvat elämäntilanteestasi. Käytä aina Kelan omaa ohjetta kyseiseen etuuteen.", "Valitse etuus Kelan palvelusta ja lue ehdot ennen hakemista.", "Kerää pyydetyt liitteet ja pidä niistä kopiot.", "Lähetä hakemus OmaKelassa tai Kelan ohjeen mukaisella tavalla.", "Voinko lähettää liitteet myöhemmin?", "Tarkista OmaKelasta tai Kelan ohjeesta, mitä hakemuksesi tarvitsee."),
        "interpreting-service": ("Kelan tulkkauspalvelu: oikeus ja tulkin tilaaminen", "Perusopas vammaisten tulkkauspalveluun hakemiseen ja tulkkauksen tilaamiseen.", "Tulkkauspalvelu on henkilökohtainen palvelu. Oikeus ja käytännöt arvioidaan Kelan ohjeiden mukaan.", "Tutustu Kelan hakemusohjeeseen ja selvitä, mitä lausuntoja tai tietoja tarvitaan.", "Hae oikeutta palveluun ennen kuin alat käyttää tilaustapaa.", "Kun päätös on tehty, käytä Kelan ohjeistamaa tilaustapaa.", "Voinko tilata tulkin viranomaiskäyntiin?", "Jos sinulla on myönnetty oikeus, tarkista tilausohjeesta sopiva tapa ja aikataulu."),
        "enter-finland": ("Enter Finland: oleskelulupahakemuksen vaiheet", "Näin valmistaudut Enter Finland -palvelussa tehtävään hakemukseen.", "Lupaperuste, liitteet ja asiointivaiheet vaihtelevat. Tarkista aina Migrin ohje juuri omalle hakemuksellesi.", "Valitse oikea hakemustyyppi Migrin sivuilta.", "Valmistele liitteet ennen kuin aloitat verkkohakemuksen.", "Seuraa hakemuksen viestejä ja mahdollisia lisäselvityspyyntöjä Enter Finlandissa.", "Voinko muuttaa hakemusta lähettämisen jälkeen?", "Tarkista Enter Finlandin ja Migrin ohjeista, miten lisätietoja toimitetaan."),
        "jobseeker-registration": ("Työnhakijaksi ilmoittautuminen Suomessa", "Näin aloitat työnhaun ja valmistaudut asiointiin Työmarkkinatorilla.", "Työnhakijaksi ilmoittautumisen käytännöt riippuvat tilanteestasi ja asuinalueestasi. Tarkista ajantasainen ohje Työmarkkinatorilta.", "Luo tai käytä tunnistautumistasi Työmarkkinatorin palvelussa.", "Kerää tiedot koulutuksesta, työkokemuksesta ja työnhakutilanteesta.", "Tallenna vahvistus ja seuraa palvelun viestejä sekä määräaikoja.", "Tarvitsenko tulkin asiointiin?", "Kerro palvelulle saavutettavuus- ja tulkkaustarpeestasi mahdollisimman varhain."),
    },
    "ru": {
        "municipality-of-residence": ("Муниципалитет проживания в Финляндии: с чего начать", "Что означает kotikunta и как подготовиться к обращению в DVV.", "Муниципалитет проживания может влиять на доступ к государственным услугам. Всегда проверяйте свою ситуацию по актуальной инструкции DVV.", "Проверьте условия получения муниципалитета проживания для вашей ситуации.", "Подготовьте удостоверение личности и документы о проживании.", "Подайте уведомление или запишитесь в DVV по официальной инструкции.", "Какие документы нужны?", "Набор документов зависит от ситуации; уточните его у DVV до обращения."),
        "applying-for-benefits": ("Как подать заявление на пособие Kela", "Пошаговая подготовка заявления и отслеживание его в OmaKela.", "Вид пособия и приложения зависят от вашей ситуации. Используйте инструкцию Kela именно для нужного пособия.", "Выберите пособие на сайте Kela и прочитайте условия.", "Соберите запрошенные приложения и сохраните копии.", "Подайте заявление через OmaKela или способом, указанным Kela.", "Можно ли прислать приложения позже?", "Проверьте в OmaKela или в инструкции Kela, какие документы требуются по вашему заявлению."),
        "interpreting-service": ("Услуга сурдоперевода Kela: право и заказ переводчика", "Основные шаги для подачи заявления на tulkkauspalvelu и заказа переводчика.", "Это персональная услуга. Право на неё и порядок использования определяются по правилам Kela.", "Изучите инструкцию Kela и уточните необходимые сведения или заключения.", "Сначала подайте заявление на право пользоваться услугой.", "После решения используйте указанный Kela способ заказа.", "Можно ли заказать переводчика для визита в ведомство?", "При наличии решения проверьте в инструкции способ заказа и срок подачи заявки."),
        "enter-finland": ("Enter Finland: этапы заявления на вид на жительство", "Как подготовить заявление на ВНЖ через сервис Enter Finland.", "Основание ВНЖ, приложения и этапы зависят от ситуации. Сверяйтесь с инструкцией Migri для вашего типа заявления.", "Выберите подходящий тип заявления на сайте Migri.", "Подготовьте приложения до начала заполнения онлайн-анкеты.", "Следите за сообщениями и запросами дополнительных сведений в Enter Finland.", "Можно ли дополнить заявление после отправки?", "Проверьте инструкции Migri и Enter Finland о передаче дополнительных данных."),
        "jobseeker-registration": ("Регистрация соискателем работы в Финляндии", "Как начать поиск работы и подготовиться к работе с Työmarkkinatori.", "Порядок регистрации зависит от вашей ситуации и региона. Проверяйте актуальные инструкции на Työmarkkinatori.", "Войдите в сервис Työmarkkinatori с доступным способом идентификации.", "Подготовьте сведения об образовании, опыте и поиске работы.", "Сохраните подтверждение и следите за сообщениями и сроками.", "Нужен ли переводчик для обращения?", "Сообщите о потребности в доступности или переводчике как можно раньше."),
    },
    "en": {
        "municipality-of-residence": ("Municipality of residence in Finland: how to start", "What a municipality of residence means and how to prepare for DVV.", "A municipality of residence may affect access to public services. Check DVV's current guidance for your own situation.", "Check the eligibility conditions for your situation.", "Prepare your identity document and documents about your residence.", "Submit the notification or book an appointment following DVV guidance.", "Which documents do I need?", "The documents depend on your situation. Check DVV guidance before you visit."),
        "applying-for-benefits": ("Applying for Kela benefits: a step-by-step guide", "How to prepare an application and follow it in OmaKela.", "The benefit and attachments depend on your circumstances. Use Kela's current instructions for the specific benefit.", "Choose the benefit on Kela's service and read the conditions.", "Collect the requested attachments and keep copies.", "Send the application in OmaKela or by the method specified by Kela.", "Can I submit attachments later?", "Check OmaKela or Kela guidance for the documents required for your application."),
        "interpreting-service": ("Kela interpreting service: entitlement and booking", "A practical introduction to applying for disability interpreting services and booking an interpreter.", "This is a personal service. Entitlement and use are assessed under Kela's current instructions.", "Read Kela's application guidance and identify the information needed.", "Apply for entitlement before using the booking service.", "After a decision, use Kela's instructed booking method.", "Can I book an interpreter for an authority appointment?", "If you have entitlement, check the booking guidance for the appropriate method and timing."),
        "enter-finland": ("Enter Finland: residence permit application steps", "How to prepare a residence permit application in Enter Finland.", "The permit basis, attachments and process vary. Always use Migri guidance for your exact application type.", "Choose the correct application type on Migri's website.", "Prepare your attachments before beginning the online application.", "Follow messages and requests for further information in Enter Finland.", "Can I add information after submitting?", "Check Migri and Enter Finland instructions for submitting additional information."),
        "jobseeker-registration": ("Registering as a jobseeker in Finland", "How to start job search and prepare for Työmarkkinatori services.", "Registration steps depend on your situation and area. Check current guidance in Työmarkkinatori.", "Sign in to Työmarkkinatori using an available identification method.", "Prepare details of your education, work history and job search.", "Save the confirmation and follow service messages and deadlines.", "Do I need an interpreter for an appointment?", "Tell the service about accessibility or interpreting needs as early as possible."),
    },
}


@app.cli.command("seed-priority-guide-content")
def seed_priority_guide_content():
    """Create priority SEO guide articles without altering existing URLs."""
    categories = {}
    for language, values in PRIORITY_GUIDE_CATEGORIES.items():
        for order, (slug, (title, description)) in enumerate(values.items(), start=1):
            category = GuideCategory.query.filter_by(language=language, slug=slug).first()
            if not category:
                category = GuideCategory(language=language, slug=slug)
                db.session.add(category)
            category.title, category.description = title, description
            category.sort_order, category.is_active = order, True
            categories[language, slug] = category
    db.session.flush()

    for language, copy in PRIORITY_GUIDE_COPY.items():
        for category_slug, slug, official_url in PRIORITY_GUIDE_TOPICS:
            title, summary, intro, step_one, step_two, step_three, question, answer = copy[slug]
            category = categories[language, category_slug]
            article = GuideArticle.query.filter_by(category_id=category.id, language=language, slug=slug).first()
            if not article:
                article = GuideArticle(category_id=category.id, language=language, slug=slug)
                db.session.add(article)
            related = f"/{language}/guide/{category_slug}"
            article.title, article.summary = title, summary
            article.content = f"""## {title}\n\n{intro}\n\n### 1. Valmistaudu / Prepare\n\n{step_one}\n\n### 2. Kerää tiedot / Collect information\n\n{step_two}\n\n### 3. Toimi virallisessa palvelussa / Use the official service\n\n{step_three}\n\n## Related materials\n\n[[Open related SKMY guide|{related}]]\n\n## FAQ\n\nQuestion: {question}\nAnswer: {answer}\n\nKysymys: {question}\nVastaus: {answer}\n\nВопрос: {question}\nОтвет: {answer}"""
            article.official_links = f"Official service|{official_url}"
            article.keywords = f"{title}, {category.title}, Finland, Suomi, Финляндия, Deaf immigrants, viittomakieli, sign language"
            article.is_published, article.sort_order = True, 20
    db.session.commit()
    print("Priority multilingual guide content created or updated.")


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
