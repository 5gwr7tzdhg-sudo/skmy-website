PAGE_SEO = {
    "about": {
        "fi": (
            "Tietoa SKMY:stä | Kuurojen maahanmuuttajien tuki Suomessa",
            "Tutustu SKMY:hyn: tuemme Suomessa asuvia kuuroja ja viittomakielisiä maahanmuuttajia tiedolla, ohjauksella ja yhteisöllä.",
        ),
        "ru": (
            "О SKMY | Поддержка глухих иммигрантов в Финляндии",
            "Узнайте о SKMY: мы поддерживаем глухих и жестоязычных иммигрантов в Финляндии информацией, консультациями и сообществом.",
        ),
        "en": (
            "About SKMY | Support for Deaf immigrants in Finland",
            "Learn about SKMY and how we support Deaf and sign-language immigrants in Finland with information, guidance, and community.",
        ),
    },
    "guide": {
        "fi": (
            "Opas Suomeen | Palvelut ja oikeudet | SKMY",
            "Selkeä opas Suomessa asumiseen: DVV, Kela, työnhaku, Migri, terveydenhuolto, perhepalvelut ja oikeudet.",
        ),
        "ru": (
            "Путеводитель по Финляндии | Услуги и права | SKMY",
            "Понятные инструкции о жизни в Финляндии: DVV, Kela, работа, Migri, здравоохранение, семья и права.",
        ),
        "en": (
            "Guide to Finland | Services and rights | SKMY",
            "Clear practical guidance for living in Finland: DVV, Kela, work, Migri, healthcare, family services, and rights.",
        ),
    },
    "interpreting": {
        "fi": (
            "Viittomakielen tulkkaus Suomessa | SKMY",
            "Tietoa Kelan tulkkauspalvelusta, tulkin tilaamisesta ja tapaamisiin valmistautumisesta Suomessa.",
        ),
        "ru": (
            "Сурдоперевод в Финляндии | SKMY",
            "Информация об услугах сурдоперевода Kela, заказе переводчика и подготовке к встречам в Финляндии.",
        ),
        "en": (
            "Sign language interpreting in Finland | SKMY",
            "Information about Kela interpreting services, booking an interpreter, and preparing for appointments in Finland.",
        ),
    },
    "contacts": {
        "fi": (
            "Yhteystiedot | Ota yhteyttä SKMY:hyn",
            "Ota yhteyttä SKMY:hyn saadaksesi tietoa, ohjausta ja tukea kuuroille ja viittomakielisille maahanmuuttajille Suomessa.",
        ),
        "ru": (
            "Контакты | Связаться с SKMY",
            "Свяжитесь с SKMY, чтобы получить информацию, консультацию и поддержку для глухих и жестоязычных иммигрантов в Финляндии.",
        ),
        "en": (
            "Contact | Get in touch with SKMY",
            "Contact SKMY for information, guidance, and support for Deaf and sign-language immigrants in Finland.",
        ),
    },
}


def page_seo(page, lang):
    """Return page-specific metadata for the site's supported languages."""
    title, description = PAGE_SEO[page][lang]
    return {"meta_title": title, "meta_description": description}
