from flask import Blueprint, redirect, render_template, request

from database.db import db
from database.models import ContactMessage

contacts_bp = Blueprint("contacts", __name__)


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
        if not name:
            errors.append("Укажите имя.")
        if not email:
            errors.append("Укажите email.")
        if not subject:
            errors.append("Укажите тему обращения.")
        if not message:
            errors.append("Введите сообщение.")

        if errors:
            return render_template(
                "public/contacts.html",
                lang=lang,
                errors=errors,
                form_data=request.form
            )

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

        return render_template(
            "public/contacts.html",
            lang=lang,
            success_message="Спасибо! Ваше сообщение отправлено.",
            form_data={}
        )

    return render_template("public/contacts.html", lang=lang, errors=[], form_data={})
