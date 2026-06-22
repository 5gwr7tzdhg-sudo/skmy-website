from flask import Blueprint, render_template, redirect

about_bp = Blueprint("about", __name__)


@about_bp.route("/<lang>/about")
def about(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    return render_template("public/about.html", lang=lang)