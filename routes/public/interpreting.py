from flask import Blueprint, render_template, redirect
from routes.public.fi import fi_context
from routes.public.page_seo import page_seo

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
    context = {
        "lang": lang,
        "navigation_labels": navigation_labels,
        **page_seo("interpreting", lang),
    }
    if lang == "fi":
        context.update(fi_context(**page_seo("interpreting", lang)))
    return render_template(template_name, **context)
