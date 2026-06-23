FI_NAVIGATION = {
    "home": "Etusivu",
    "about": "Tietoa meistä",
    "news": "Uutiset",
    "guide": "Opas",
    "interpreting": "Viittomakielen tulkkaus",
    "contacts": "Yhteystiedot",
}


def fi_context(meta_title, meta_description):
    return {
        "navigation_labels": FI_NAVIGATION,
        "footer_name": "Suomen Kuurojen Maahanmuuttajayhdistys ry",
        "meta_title": meta_title,
        "meta_description": meta_description,
    }
