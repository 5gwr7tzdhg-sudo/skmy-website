from flask import Blueprint, render_template, redirect

interpreting_bp = Blueprint("interpreting", __name__)


@interpreting_bp.route("/<lang>/interpreting")
def interpreting(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    return render_template("public/interpreting.html", lang=lang)