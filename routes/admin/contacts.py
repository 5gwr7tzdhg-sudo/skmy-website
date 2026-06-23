from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from database.db import db
from database.models import AdminLog, ContactMessage
from routes.admin.auth import admin_required


admin_contacts_bp = Blueprint(
    "admin_contacts",
    __name__,
    url_prefix="/admin/contacts"
)


@admin_contacts_bp.before_request
@admin_required
def require_admin():
    return None


@admin_contacts_bp.route("")
@admin_contacts_bp.route("/")
def messages():
    messages = (
        ContactMessage.query
        .order_by(ContactMessage.status, ContactMessage.created_at.desc())
        .all()
    )
    return render_template("admin/contacts.html", messages=messages, lang="ru")


@admin_contacts_bp.route("/<int:message_id>")
def message_detail(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    return render_template("admin/contact_detail.html", message=message, lang="ru")


@admin_contacts_bp.route("/<int:message_id>/mark-read", methods=["POST"])
def mark_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)

    if message.status != "read":
        message.status = "read"
        db.session.add(
            AdminLog(
                user_id=current_user.id,
                action="Прочитано",
                entity_type="contact_message",
                entity_id=message.id,
                description=f"Прочитано обращение «{message.subject}» от {message.name}."
            )
        )
        db.session.commit()

    return redirect(url_for("admin_contacts.message_detail", message_id=message.id))
