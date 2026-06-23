from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from database.db import db
from database.models import AdminLog, News
from routes.admin.auth import admin_required


admin_news_bp = Blueprint("admin_news", __name__, url_prefix="/admin/news")


@admin_news_bp.before_request
@admin_required
def require_admin():
    return None


def parse_published_at(value, is_published, errors):
    if value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            errors.append("Дата публикации имеет неверный формат.")
            return None

    return datetime.utcnow() if is_published else None


def log_news_action(action, news_item, description):
    db.session.add(
        AdminLog(
            user_id=current_user.id,
            action=action,
            entity_type="news",
            entity_id=news_item.id,
            description=description
        )
    )


@admin_news_bp.route("")
@admin_news_bp.route("/")
def news_list():
    news_items = News.query.order_by(News.created_at.desc()).all()
    return render_template("admin/news.html", news_items=news_items, lang="ru")


@admin_news_bp.route("/new", methods=["GET", "POST"])
def new_news():
    if request.method == "POST":
        language = request.form.get("language", "").strip()
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        is_published = "is_published" in request.form
        published_at_value = request.form.get("published_at", "").strip()

        errors = []
        if not language:
            errors.append("Укажите язык.")
        if not title:
            errors.append("Укажите заголовок новости.")
        if not slug:
            errors.append("Укажите slug.")

        published_at = parse_published_at(published_at_value, is_published, errors)

        if not errors:
            news_item = News(
                language=language,
                title=title,
                slug=slug,
                summary=request.form.get("summary", "").strip() or None,
                content=request.form.get("content", "").strip() or None,
                image_path=request.form.get("image_path", "").strip() or None,
                is_published=is_published,
                published_at=published_at
            )
            db.session.add(news_item)
            db.session.flush()
            log_news_action(
                "Создание",
                news_item,
                f"Создана новость «{news_item.title}»."
            )
            db.session.commit()
            return redirect(url_for("admin_news.news_list"))

        return render_template(
            "admin/news_form.html",
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/news_form.html",
        errors=[],
        form_data={"is_published": "on"},
        lang="ru"
    )


@admin_news_bp.route("/<int:news_id>/edit", methods=["GET", "POST"])
def edit_news(news_id):
    news_item = News.query.get_or_404(news_id)

    if request.method == "POST":
        language = request.form.get("language", "").strip()
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        is_published = "is_published" in request.form
        published_at_value = request.form.get("published_at", "").strip()

        errors = []
        if not language:
            errors.append("Укажите язык.")
        if not title:
            errors.append("Укажите заголовок новости.")
        if not slug:
            errors.append("Укажите slug.")

        published_at = parse_published_at(published_at_value, is_published, errors)

        if not errors:
            news_item.language = language
            news_item.title = title
            news_item.slug = slug
            news_item.summary = request.form.get("summary", "").strip() or None
            news_item.content = request.form.get("content", "").strip() or None
            news_item.image_path = request.form.get("image_path", "").strip() or None
            news_item.is_published = is_published
            news_item.published_at = published_at
            log_news_action(
                "Редактирование",
                news_item,
                f"Отредактирована новость «{news_item.title}»."
            )
            db.session.commit()
            return redirect(url_for("admin_news.news_list"))

        return render_template(
            "admin/news_form.html",
            news_item=news_item,
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/news_form.html",
        news_item=news_item,
        errors=[],
        form_data={
            "language": news_item.language,
            "title": news_item.title,
            "slug": news_item.slug,
            "summary": news_item.summary or "",
            "content": news_item.content or "",
            "image_path": news_item.image_path or "",
            "published_at": (
                news_item.published_at.strftime("%Y-%m-%dT%H:%M")
                if news_item.published_at else ""
            ),
            "is_published": "on" if news_item.is_published else None,
        },
        lang="ru"
    )


@admin_news_bp.route("/<int:news_id>/toggle-published", methods=["POST"])
def toggle_published(news_id):
    news_item = News.query.get_or_404(news_id)
    news_item.is_published = not news_item.is_published

    if news_item.is_published and news_item.published_at is None:
        news_item.published_at = datetime.utcnow()

    action = "Публикация" if news_item.is_published else "Скрытие"
    description = (
        f"Опубликована новость «{news_item.title}»."
        if news_item.is_published
        else f"Скрыта новость «{news_item.title}»."
    )
    log_news_action(action, news_item, description)
    db.session.commit()

    return redirect(url_for("admin_news.news_list"))


@admin_news_bp.route("/<int:news_id>/delete", methods=["GET", "POST"])
def delete_news(news_id):
    news_item = News.query.get_or_404(news_id)

    if request.method == "POST":
        news_id = news_item.id
        news_title = news_item.title
        db.session.add(
            AdminLog(
                user_id=current_user.id,
                action="Удаление",
                entity_type="news",
                entity_id=news_id,
                description=f"Удалена новость «{news_title}»."
            )
        )
        db.session.delete(news_item)
        db.session.commit()
        return redirect(url_for("admin_news.news_list"))

    return render_template(
        "admin/confirm_delete.html",
        entity_label="новость",
        entity_title=news_item.title,
        cancel_url=url_for("admin_news.news_list"),
        lang="ru"
    )
