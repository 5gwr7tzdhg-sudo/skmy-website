from flask import Blueprint, render_template, redirect
from routes.public.fi import fi_context

interpreting_bp = Blueprint("interpreting", __name__)


@interpreting_bp.route("/<lang>/interpreting")
def interpreting(lang):
    if lang not in ["fi", "ru", "en"]:
        return redirect("/ru/")

    navigation_labels = {
        "fi": {
            "home": "Etusivu",
            "about": "Tietoa meistä",
            "news": "Uutiset",
            "guide": "Opas",
            "interpreting": "Viittomakielen tulkkaus",
            "contacts": "Yhteystiedot",
        },
        "en": {
            "home": "Home",
            "about": "About us",
            "news": "News",
            "guide": "Guide",
            "interpreting": "Sign language interpreting",
            "contacts": "Contact",
        },
    }.get(lang)
    template_name = (
        "public/interpreting.html"
        if lang == "ru"
        else "public/interpreting_localized.html"
    )
    context = {"lang": lang, "navigation_labels": navigation_labels}
    if lang == "fi":
        context.update(fi_context(
            "Viittomakielen tulkkaus | SKMY",
            "Tietoa Kelan tulkkauspalvelusta, tulkin tilaamisesta ja tapaamisiin valmistautumisesta Suomessa.",
        ))
    return render_template(template_name, **context)
