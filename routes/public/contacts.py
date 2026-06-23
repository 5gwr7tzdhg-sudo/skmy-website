from flask import Blueprint, redirect, render_template, request

from database.db import db
from database.models import ContactMessage
from routes.public.fi import fi_context

contacts_bp = Blueprint("contacts", __name__)


INTERPRETING_SUPPORT_SUBJECT = "Нужна помощь с сурдопереводом"
INTERPRETING_SUPPORT_MESSAGE = """Здравствуйте.

Мне нужна помощь с вопросом сурдоперевода.

У меня пока нет оформленного права на переводческие услуги через Kela, или я не знаю, с чего начать оформление.

Пожалуйста, помогите мне понять:

• куда обращаться;
• какие документы нужны;
• как оформить право на сурдоперевод;
• что делать, если переводчик нужен уже сейчас.

С уважением,"""

FI_INTERPRETING_SUPPORT_SUBJECT = "Tarvitsen apua tulkkauspalvelussa"
FI_INTERPRETING_SUPPORT_MESSAGE = """Hei,

Tarvitsen apua viittomakielen tulkkauspalvelua koskevassa asiassa.

Minulla ei vielä ole Kelan myöntämää oikeutta tulkkauspalveluun, tai en tiedä, mistä hakeminen aloitetaan.

Voitteko auttaa minua ymmärtämään:

• mihin minun tulee ottaa yhteyttä;
• mitä asiakirjoja tarvitaan;
• miten tulkkauspalveluoikeutta haetaan;
• mitä tehdä, jos tulkkia tarvitaan jo nyt.

Ystävällisin terveisin,"""


@contacts_bp.route("/<lang>/contacts", methods=["GET", "POST"])
def contacts(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        errors = []
        error_text = (
            ("Kirjoita nimesi.", "Kirjoita sähköpostiosoitteesi.", "Kirjoita viestin aihe.", "Kirjoita viestisi.")
            if lang == "fi"
            else ("Укажите имя.", "Укажите email.", "Укажите тему обращения.", "Введите сообщение.")
        )
        if not name:
            errors.append(error_text[0])
        if not email:
            errors.append(error_text[1])
        if not subject:
            errors.append(error_text[2])
        if not message:
            errors.append(error_text[3])

        if errors:
            context = {"lang": lang, "errors": errors, "form_data": request.form}
            if lang == "fi":
                context.update(fi_context("Yhteystiedot | SKMY", "Ota yhteyttä SKMY:hyn saadaksesi tietoa ja tukea Suomessa."))
                return render_template("public/contacts_fi.html", **context)
            return render_template("public/contacts.html", **context)

        contact_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            language=lang,
            status="new"
        )
        db.session.add(contact_message)
        db.session.commit()

        context = {"lang": lang, "success_message": "Kiitos! Viestisi on lähetetty." if lang == "fi" else "Спасибо! Ваше сообщение отправлено.", "form_data": {}}
        if lang == "fi":
            context.update(fi_context("Yhteystiedot | SKMY", "Ota yhteyttä SKMY:hyn saadaksesi tietoa ja tukea Suomessa."))
            return render_template("public/contacts_fi.html", **context)
        return render_template("public/contacts.html", **context)

    form_data = {}
    if request.args.get("topic") == "interpreting":
        form_data = ({"subject": FI_INTERPRETING_SUPPORT_SUBJECT, "message": FI_INTERPRETING_SUPPORT_MESSAGE}
                     if lang == "fi" else {"subject": INTERPRETING_SUPPORT_SUBJECT, "message": INTERPRETING_SUPPORT_MESSAGE})

    if lang == "fi":
        return render_template(
            "public/contacts_fi.html", lang=lang, errors=[], form_data=form_data,
            **fi_context("Yhteystiedot | SKMY", "Ota yhteyttä SKMY:hyn saadaksesi tietoa ja tukea Suomessa."),
        )
    return render_template("public/contacts.html", lang=lang, errors=[], form_data=form_data)
