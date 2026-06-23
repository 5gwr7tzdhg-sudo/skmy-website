from flask import Blueprint, render_template, redirect
from routes.public.fi import fi_context

about_bp = Blueprint("about", __name__)


@about_bp.route("/<lang>/about")
def about(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    if lang == "fi":
        return render_template(
            "public/about_fi.html",
            lang=lang,
            **fi_context(
                "Tietoa SKMY:stä — tukea kuuroille maahanmuuttajille",
                "SKMY tukee kuuroja ja viittomakielisiä maahanmuuttajia Suomessa tarjoamalla tietoa, ohjausta ja yhteisön.",
            ),
        )
    return render_template("public/about.html", lang=lang)
