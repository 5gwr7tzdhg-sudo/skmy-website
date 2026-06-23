import re

from flask import Blueprint, redirect, render_template, request

from database.db import db
from database.models import ContactMessage
from routes.public.fi import fi_context
from routes.public.page_seo import page_seo
from services.rate_limit import rate_limiter

contacts_bp = Blueprint("contacts", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,253}$")
MAX_NAME_LENGTH = 120
MAX_EMAIL_LENGTH = 254
MAX_SUBJECT_LENGTH = 200
MAX_MESSAGE_LENGTH = 5000


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
        honeypot = request.form.get("website", "").strip()

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
        if email and (len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.fullmatch(email)):
            errors.append("Tarkista sähköpostiosoite." if lang == "fi" else "Проверьте email.")
        if len(name) > MAX_NAME_LENGTH:
            errors.append("Nimi on liian pitkä." if lang == "fi" else "Имя слишком длинное.")
        if len(subject) > MAX_SUBJECT_LENGTH:
            errors.append("Aihe on liian pitkä." if lang == "fi" else "Тема слишком длинная.")
        if len(message) > MAX_MESSAGE_LENGTH:
            errors.append("Viesti on liian pitkä." if lang == "fi" else "Сообщение слишком длинное.")

        if honeypot:
            errors = []
            success_message = "Kiitos! Viestisi on lähetetty." if lang == "fi" else "Спасибо! Ваше сообщение отправлено."
            context = {"lang": lang, "success_message": success_message, "form_data": {}, **page_seo("contacts", lang)}
            if lang == "fi":
                context.update(fi_context(**page_seo("contacts", lang)))
                return render_template("public/contacts_fi.html", **context)
            return render_template("public/contacts.html", **context)

        client_ip = request.remote_addr or "unknown"
        if not rate_limiter.allow(f"contacts:{client_ip}", limit=5, window_seconds=3600):
            errors.append("Yritä myöhemmin uudelleen." if lang == "fi" else "Попробуйте снова позднее.")

        if errors:
            context = {
                "lang": lang, "errors": errors, "form_data": request.form,
                **page_seo("contacts", lang),
            }
            if lang == "fi":
                context.update(fi_context(**page_seo("contacts", lang)))
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

        context = {"lang": lang, "success_message": "Kiitos! Viestisi on lähetetty." if lang == "fi" else "Спасибо! Ваше сообщение отправлено.", "form_data": {}, **page_seo("contacts", lang)}
        if lang == "fi":
            context.update(fi_context(**page_seo("contacts", lang)))
            return render_template("public/contacts_fi.html", **context)
        return render_template("public/contacts.html", **context)

    form_data = {}
    if request.args.get("topic") == "interpreting":
        form_data = ({"subject": FI_INTERPRETING_SUPPORT_SUBJECT, "message": FI_INTERPRETING_SUPPORT_MESSAGE}
                     if lang == "fi" else {"subject": INTERPRETING_SUPPORT_SUBJECT, "message": INTERPRETING_SUPPORT_MESSAGE})

    if lang == "fi":
        return render_template(
            "public/contacts_fi.html", lang=lang, errors=[], form_data=form_data,
            **fi_context(**page_seo("contacts", lang)),
        )
    return render_template(
        "public/contacts.html", lang=lang, errors=[], form_data=form_data,
        **page_seo("contacts", lang),
    )
