from flask import Blueprint, render_template, redirect
from routes.public.fi import fi_context
from routes.public.page_seo import page_seo
from routes.public.category_seo import faq_schema

interpreting_bp = Blueprint("interpreting", __name__)


INTERPRETING_FAQ = {
    "fi": [
        ("Kuka voi hakea Kelan tulkkauspalvelua?", "Kela arvioi oikeuden palveluun hakemuksen ja tarvittavien selvitysten perusteella."),
        ("Miten tilaan viittomakielen tulkin?", "Kun oikeus palveluun on myönnetty, tulkki tilataan Kelan virallisen palvelun kautta."),
        ("Voinko saada tulkin DVV-, Migri- tai TE-palvelujen tapaamiseen?", "Kyllä, tulkkauspalvelua voi käyttää viranomaisasiointiin myönnetyn oikeuden mukaisesti."),
        ("Mitä teen, jos en ymmärrä ohjetta tai päätöstä?", "Säilytä viesti ja ota yhteyttä SKMY:hyn, jos tarvitset apua seuraavan askeleen ymmärtämiseen."),
    ],
    "ru": [
        ("Кто может подать заявление на услугу перевода Kela?", "Kela оценивает право на услугу по заявлению и необходимым подтверждающим документам."),
        ("Как заказать сурдопереводчика?", "После предоставления права на услугу переводчика заказывают через официальный сервис Kela."),
        ("Можно ли получить переводчика для DVV, Migri или TE-palvelut?", "Да, услугу можно использовать для общения с государственными службами в рамках предоставленного права."),
        ("Что делать, если я не понимаю инструкцию или решение?", "Сохраните сообщение и обратитесь в SKMY, если нужна помощь с пониманием следующего шага."),
    ],
    "en": [
        ("Who can apply for Kela interpreting services?", "Kela assesses the right to the service based on an application and the required supporting information."),
        ("How do I book a sign language interpreter?", "Once the right has been granted, book an interpreter through Kela's official service."),
        ("Can I use an interpreter for DVV, Migri or TE services?", "Yes, interpreting services can be used for public-authority appointments within the granted right."),
        ("What if I do not understand an instruction or decision?", "Keep the message and contact SKMY if you need help understanding the next step."),
    ],
}


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
        "interpreting_faq": INTERPRETING_FAQ[lang],
        "faq_schema": faq_schema(INTERPRETING_FAQ[lang]),
        **page_seo("interpreting", lang),
    }
    if lang == "fi":
        context.update(fi_context(**page_seo("interpreting", lang)))
    return render_template(template_name, **context)
