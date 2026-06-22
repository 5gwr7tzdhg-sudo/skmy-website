from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from database.db import db
from database.models import AdminLog, GuideArticle, GuideCategory


admin_guide_bp = Blueprint(
    "admin_guide",
    __name__,
    url_prefix="/admin/guide"
)


def log_admin_action(action, entity_type, entity_id, description):
    db.session.add(
        AdminLog(
            user_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description
        )
    )


@admin_guide_bp.before_request
@login_required
def require_admin():
    if current_user.role != "admin":
        abort(403)


@admin_guide_bp.route("")
@admin_guide_bp.route("/")
def dashboard():
    return render_template("admin/guide_dashboard.html", lang="ru")


@admin_guide_bp.route("/categories")
def categories():
    categories = (
        GuideCategory.query
        .order_by(GuideCategory.language, GuideCategory.sort_order, GuideCategory.title)
        .all()
    )

    return render_template(
        "admin/guide_categories.html",
        categories=categories,
        lang="ru"
    )


@admin_guide_bp.route("/categories/new", methods=["GET", "POST"])
def new_category():
    if request.method == "POST":
        language = request.form.get("language", "").strip()
        slug = request.form.get("slug", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "").strip()
        sort_order_value = request.form.get("sort_order", "").strip()

        errors = []
        if not language:
            errors.append("Укажите язык.")
        if not slug:
            errors.append("Укажите slug.")
        if not title:
            errors.append("Укажите название категории.")

        if sort_order_value:
            try:
                sort_order = int(sort_order_value)
            except ValueError:
                errors.append("Порядок сортировки должен быть целым числом.")
                sort_order = 0
        else:
            sort_order = 0

        if not errors:
            category = GuideCategory(
                language=language,
                slug=slug,
                title=title,
                description=description or None,
                icon=icon or None,
                sort_order=sort_order,
                is_active="is_active" in request.form
            )
            db.session.add(category)
            db.session.flush()
            log_admin_action(
                "Создание",
                "category",
                category.id,
                f"Создана категория «{category.title}»."
            )
            db.session.commit()

            return redirect(url_for("admin_guide.categories"))

        return render_template(
            "admin/guide_category_form.html",
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/guide_category_form.html",
        errors=[],
        form_data={},
        lang="ru"
    )


@admin_guide_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    category = GuideCategory.query.get_or_404(category_id)

    if request.method == "POST":
        language = request.form.get("language", "").strip()
        slug = request.form.get("slug", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        icon = request.form.get("icon", "").strip()
        sort_order_value = request.form.get("sort_order", "").strip()

        errors = []
        if not language:
            errors.append("Укажите язык.")
        if not slug:
            errors.append("Укажите slug.")
        if not title:
            errors.append("Укажите название категории.")

        if sort_order_value:
            try:
                sort_order = int(sort_order_value)
            except ValueError:
                errors.append("Порядок сортировки должен быть целым числом.")
                sort_order = 0
        else:
            sort_order = 0

        if not errors:
            category.language = language
            category.slug = slug
            category.title = title
            category.description = description or None
            category.icon = icon or None
            category.sort_order = sort_order
            category.is_active = "is_active" in request.form
            log_admin_action(
                "Редактирование",
                "category",
                category.id,
                f"Отредактирована категория «{category.title}»."
            )
            db.session.commit()

            return redirect(url_for("admin_guide.categories"))

        return render_template(
            "admin/guide_category_form.html",
            category=category,
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/guide_category_form.html",
        category=category,
        errors=[],
        form_data={
            "language": category.language,
            "slug": category.slug,
            "title": category.title,
            "description": category.description or "",
            "icon": category.icon or "",
            "sort_order": category.sort_order,
            "is_active": "on" if category.is_active else None,
        },
        lang="ru"
    )


@admin_guide_bp.route("/categories/<int:category_id>/toggle-active", methods=["POST"])
def toggle_category_active(category_id):
    category = GuideCategory.query.get_or_404(category_id)
    category.is_active = not category.is_active
    action = "Показ" if category.is_active else "Скрытие"
    description = (
        f"Показана категория «{category.title}»."
        if category.is_active
        else f"Скрыта категория «{category.title}»."
    )
    log_admin_action(action, "category", category.id, description)
    db.session.commit()

    return redirect(url_for("admin_guide.categories"))


@admin_guide_bp.route("/articles")
def articles():
    articles = (
        GuideArticle.query
        .order_by(GuideArticle.language, GuideArticle.sort_order, GuideArticle.title)
        .all()
    )

    return render_template(
        "admin/guide_articles.html",
        articles=articles,
        lang="ru"
    )


@admin_guide_bp.route("/articles/new", methods=["GET", "POST"])
def new_article():
    categories = (
        GuideCategory.query
        .order_by(GuideCategory.language, GuideCategory.sort_order, GuideCategory.title)
        .all()
    )

    if request.method == "POST":
        category_id_value = request.form.get("category_id", "").strip()
        language = request.form.get("language", "").strip()
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        sort_order_value = request.form.get("sort_order", "").strip()

        errors = []
        category = None
        if not category_id_value:
            errors.append("Выберите категорию.")
        else:
            try:
                category = db.session.get(GuideCategory, int(category_id_value))
            except ValueError:
                category = None

            if category is None:
                errors.append("Выберите существующую категорию.")

        if not language:
            errors.append("Укажите язык.")
        if not title:
            errors.append("Укажите название статьи.")
        if not slug:
            errors.append("Укажите slug.")

        if sort_order_value:
            try:
                sort_order = int(sort_order_value)
            except ValueError:
                errors.append("Порядок сортировки должен быть целым числом.")
                sort_order = 0
        else:
            sort_order = 0

        if not errors:
            article = GuideArticle(
                category_id=category.id,
                language=language,
                title=title,
                slug=slug,
                summary=request.form.get("summary", "").strip() or None,
                content=request.form.get("content", "").strip() or None,
                keywords=request.form.get("keywords", "").strip() or None,
                official_links=request.form.get("official_links", "").strip() or None,
                video_url=request.form.get("video_url", "").strip() or None,
                sort_order=sort_order,
                is_published="is_published" in request.form
            )
            db.session.add(article)
            db.session.flush()
            log_admin_action(
                "Создание",
                "article",
                article.id,
                f"Создана статья «{article.title}»."
            )
            db.session.commit()

            return redirect(url_for("admin_guide.articles"))

        return render_template(
            "admin/guide_article_form.html",
            categories=categories,
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/guide_article_form.html",
        categories=categories,
        errors=[],
        form_data={"is_published": "on"},
        lang="ru"
    )


@admin_guide_bp.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
def edit_article(article_id):
    article = GuideArticle.query.get_or_404(article_id)
    categories = (
        GuideCategory.query
        .order_by(GuideCategory.language, GuideCategory.sort_order, GuideCategory.title)
        .all()
    )


    if request.method == "POST":
        category_id_value = request.form.get("category_id", "").strip()
        language = request.form.get("language", "").strip()
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        sort_order_value = request.form.get("sort_order", "").strip()

        errors = []
        category = None
        if not category_id_value:
            errors.append("Выберите категорию.")
        else:
            try:
                category = db.session.get(GuideCategory, int(category_id_value))
            except ValueError:
                category = None

            if category is None:
                errors.append("Выберите существующую категорию.")

        if not language:
            errors.append("Укажите язык.")
        if not title:
            errors.append("Укажите название статьи.")
        if not slug:
            errors.append("Укажите slug.")

        if sort_order_value:
            try:
                sort_order = int(sort_order_value)
            except ValueError:
                errors.append("Порядок сортировки должен быть целым числом.")
                sort_order = 0
        else:
            sort_order = 0

        if not errors:
            article.category_id = category.id
            article.language = language
            article.title = title
            article.slug = slug
            article.summary = request.form.get("summary", "").strip() or None
            article.content = request.form.get("content", "").strip() or None
            article.keywords = request.form.get("keywords", "").strip() or None
            article.official_links = request.form.get("official_links", "").strip() or None
            article.video_url = request.form.get("video_url", "").strip() or None
            article.sort_order = sort_order
            article.is_published = "is_published" in request.form
            log_admin_action(
                "Редактирование",
                "article",
                article.id,
                f"Отредактирована статья «{article.title}»."
            )
            db.session.commit()

            return redirect(url_for("admin_guide.articles"))

        return render_template(
            "admin/guide_article_form.html",
            article=article,
            categories=categories,
            errors=errors,
            form_data=request.form,
            lang="ru"
        )

    return render_template(
        "admin/guide_article_form.html",
        article=article,
        categories=categories,
        errors=[],
        form_data={
            "category_id": str(article.category_id),
            "language": article.language,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary or "",
            "content": article.content or "",
            "keywords": article.keywords or "",
            "official_links": article.official_links or "",
            "video_url": article.video_url or "",
            "sort_order": article.sort_order,
            "is_published": "on" if article.is_published else None,
        },
        lang="ru"
    )


@admin_guide_bp.route(
    "/articles/<int:article_id>/toggle-published",
    methods=["POST"]
)
def toggle_article_published(article_id):
    article = GuideArticle.query.get_or_404(article_id)
    article.is_published = not article.is_published
    action = "Публикация" if article.is_published else "Скрытие"
    description = (
        f"Опубликована статья «{article.title}»."
        if article.is_published
        else f"Скрыта статья «{article.title}»."
    )
    log_admin_action(action, "article", article.id, description)
    db.session.commit()

    return redirect(url_for("admin_guide.articles"))
