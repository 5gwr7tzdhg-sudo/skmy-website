"""Editorial SEO content for the four core Guide categories.

This is deliberately kept outside the CMS: it enriches existing category pages
without changing their URLs, route structure, database model or admin UI.
"""

import json


_FI = {
    "dvv": {
        "title": "DVV henkilötunnus ja rekisteröinti Suomessa | SKMY",
        "description": "Ohje kuuroille ja viittomakielisille maahanmuuttajille: henkilötunnus, DVV-rekisteröinti, osoite ja tulkkaus Suomessa.",
        "h1": "DVV: henkilötunnus ja rekisteröinti Suomessa",
        "sections": [
            ("DVV auttaa alkuun Suomessa", "DVV eli Digi- ja väestötietovirasto ylläpitää Suomessa väestötietoja. Kuuro maahanmuuttaja tai viittomakielinen maahanmuuttaja tarvitsee DVV:n palveluja usein henkilötunnusta, osoitetta tai omien tietojen rekisteröintiä varten. Henkilötunnus helpottaa asiointia esimerkiksi Kelassa, pankissa, terveydenhuollossa ja työssä. Oma tilanteesi ratkaisee, hoidetaanko asia DVV:ssä vai Migrin kautta."),
            ("Valmistaudu käyntiin", "Tarkista ennen käyntiä virallisesta ohjeesta, tarvitsetko ajanvarauksen ja mitä alkuperäisiä asiakirjoja sinun pitää ottaa mukaan. Passi tai muu henkilöllisyystodistus, oleskeluun liittyvät asiakirjat sekä tieto Suomen osoitteesta ovat tavallisia lähtökohtia. Jos asiakirja, lomake tai kirje on epäselvä, pyydä sisältö selitettäväksi ennen tapaamista. Näin voit keskittyä itse asiaan käynnillä."),
            ("Tulkkaus ja seuraavat askeleet", "Jos tarvitset viittomakielen tulkin DVV-tapaamiseen, selvitä tulkkauspalvelu ajoissa. Kelan myöntämän tulkkauspalvelun avulla tulkki voidaan tilata viranomaisasiointiin. Kun henkilötunnus tai osoite on rekisteröity, tarkista seuraavaksi Kelaan, työhön tai pankkiin liittyvät asiat. Jos oleskelulupa on vielä kesken, katso myös Migrin ohjeet. SKMY auttaa löytämään oikean seuraavan vaiheen."),
            ("Pidä tiedot ajan tasalla", "Tallenna käynnistä saadut päätökset ja muistiinpanot turvallisesti. Ilmoita osoitteen, nimen tai perhetilanteen muutoksista oikealle viranomaiselle, koska vanhentunut tieto voi hidastaa myöhempää asiointia. Henkilötunnus on henkilökohtainen tieto: anna se vain luotettavalle palvelulle, joka tarvitsee sitä. Virallisella sivulla tarkistettu tieto on aina parempi kuin sosiaalisessa mediassa kiertävä neuvo."),
            ("Kun tarvitset lisäapua", "Voit valmistautua käyntiin kirjoittamalla etukäteen kolme asiaa: mitä haluat rekisteröidä, mitä asiakirjoja sinulla on ja mitä et vielä ymmärrä. Ota muistiinpanot mukaan. Jos tulkki tai muu tuki on tarpeen, kerro siitä varauksessa mahdollisimman selkeästi. Näin palvelu voi varautua tilanteeseen ja sinulla on parempi mahdollisuus saada vastaus omiin kysymyksiisi."),
            ("Luotettava tieto", "DVV:n menettelyt voivat muuttua henkilökohtaisen tilanteen, kansalaisuuden tai Suomeen muuton perusteen mukaan. Tämä opas auttaa hahmottamaan kokonaisuutta, mutta ei korvaa viranomaisen päätöstä. Avaa aina virallinen linkki ennen käyntiä, tarkista palvelupaikka ja pidä yhteystiedot saatavilla. SKMY:n kautta voit pyytää tukea silloin, kun ohjeen kieli tai seuraava askel tuntuu vaikealta."),
            ("Muista oma tilanteesi", "Jokainen rekisteröinti arvioidaan oman tilanteen ja asiakirjojen perusteella. Siksi kannattaa kertoa DVV:lle rehellisesti, miksi olet Suomessa ja mitä olet jo hoitanut. Selkeä valmistautuminen tekee käynnistä rauhallisemman ja auttaa työntekijää ohjaamaan sinut oikeaan palveluun."),
        ],
        "faq": [
            ("Mihin henkilötunnusta tarvitaan?", "Sitä tarvitaan usein viranomaispalveluissa, Kelassa, pankissa, työssä ja terveydenhuollossa."),
            ("Tarvitsenko ajan DVV:hen?", "Se riippuu palvelusta. Tarkista aina DVV:n ajantasainen ohje ennen käyntiä."),
            ("Voinko saada tulkin DVV-käynnille?", "Jos sinulla on oikeus tulkkauspalveluun, tulkki voidaan tilata tapaamista varten. Katso SKMY:n tulkkaussivu."),
            ("Mitä teen muuton jälkeen?", "Ilmoita uusi osoite DVV:lle ja tarkista, pitääkö tiedot päivittää myös muille palveluille."),
        ],
    },
    "kela": {
        "title": "Kela maahanmuuttajalle: etuudet, OmaKela ja tulkkaus | SKMY",
        "description": "Selkeä Kela-opas kuuroille ja viittomakielisille maahanmuuttajille: etuudet, OmaKela ja Kelan tulkkauspalvelu.",
        "h1": "Kela maahanmuuttajalle: etuudet, OmaKela ja tulkkaus",
        "sections": [
            ("Kela ja arki Suomessa", "Kela hoitaa monia Suomessa asumiseen liittyviä etuuksia ja korvauksia. Kuuro maahanmuuttaja voi tarvita Kelan tietoa esimerkiksi asumiseen, sairauteen, opiskeluun, perheeseen tai työnhakutilanteeseen liittyen. Oikeus etuuteen riippuu aina omasta elämäntilanteesta, asumisesta ja tarvittavista selvityksistä. Siksi kannattaa tarkistaa virallinen ohje ennen hakemuksen lähettämistä."),
            ("OmaKela ja asiakirjat", "OmaKelassa voit hakea etuuksia, lähettää liitteitä ja nähdä päätöksiä. Vahva tunnistautuminen voi vaatia pankkitunnuksia tai muuta hyväksyttyä tunnistautumistapaa. Säilytä saamasi päätökset ja viestit. Jos et ymmärrä päätöstä, älä jätä asiaa sikseen: pyydä selitys, tarkista määräajat ja hae tukea. Henkilötunnus ja DVV:hen rekisteröidyt tiedot ovat usein tärkeitä ennen palvelujen käyttöä."),
            ("Kelan tulkkauspalvelu", "Kela voi järjestää tulkkauspalvelua henkilölle, jolla on kuulon, näön tai puheen vuoksi vaikeuksia viestiä. Oikeus haetaan erikseen, ja myönnetyn oikeuden jälkeen tulkki voidaan tilata esimerkiksi DVV-, Migri-, Kela- tai TE-palvelujen tapaamiseen. Tutustu ensin tulkkauspalvelun ohjeeseen ja valmistele tarvittavat selvitykset. SKMY voi auttaa ohjeiden ymmärtämisessä ja seuraavan askeleen löytämisessä."),
            ("Tarkista päätös ja määräajat", "Jokaisessa hakemuksessa kannattaa tarkistaa, mitä tietoja Kela vielä tarvitsee ja mihin päivään mennessä ne pitää toimittaa. Pidä kopio lähetetyistä liitteistä ja kirjaa ylös, milloin asiaa on hoidettu. Jos elämäntilanne muuttuu, esimerkiksi työ, osoite tai perhetilanne, se voi vaikuttaa etuuteen. Kysy mieluummin ajoissa kuin odota päätöstä epäselvässä tilanteessa."),
            ("Valmistaudu yhteydenottoon", "Ennen kuin otat yhteyttä Kelaan, kerää päätöksen numero, hakemuksen nimi ja kysymys mahdollisimman selkeästi. Voit esimerkiksi kysyä, mikä liite puuttuu tai mihin päivään mennessä vastaus tarvitaan. Pyydä tarvittaessa viesti tai selitys tavalla, joka on sinulle saavutettava. Muista, että Kela tekee päätöksen omien sääntöjensä mukaan; SKMY voi auttaa sinua ymmärtämään ohjetta."),
            ("Yhdistä palvelut oikeassa järjestyksessä", "Monessa tilanteessa ensin tarvitaan DVV:n henkilötunnus ja rekisteröidyt tiedot, sitten Kelan hakemus. Työnhakija voi tarvita lisäksi yhteyden työllisyyspalveluihin, ja oleskelulupaan liittyvä kysymys kuuluu Migrille. Kun pidät nämä roolit erillään, löydät nopeammin oikean palvelun. Käytä tämän sivun sisäisiä linkkejä oman tilanteesi seuraavan vaiheen valitsemiseen."),
            ("Pidä oma arkisto", "Tallenna päätökset, hakemukset ja liitteet turvalliseen paikkaan. Niitä voidaan pyytää myöhemmin uudelleen tai niitä voi tarvita, kun selvität asiaa toisessa palvelussa. Oma arkisto helpottaa myös sitä, että voit kertoa tilanteesi selkeästi tulkille tai neuvojalle."),
        ],
        "faq": [
            ("Voinko hakea etuuksia heti Suomeen muuton jälkeen?", "Se riippuu asumisesta ja elämäntilanteesta. Tarkista aina Kelan ajantasainen ohje."),
            ("Mihin OmaKelaa käytetään?", "OmaKelassa voi tehdä hakemuksia, lähettää liitteitä ja seurata päätöksiä."),
            ("Miten haen tulkkauspalvelua?", "Tutustu Kelan ohjeeseen ja hae oikeutta palveluun tarvittavilla selvityksillä."),
            ("Mitä teen, jos en ymmärrä Kelan päätöstä?", "Tarkista määräajat, pyydä päätöksestä selitys ja ota tarvittaessa yhteyttä SKMY:hyn."),
        ],
    },
    "migri": {
        "title": "Migri maahanmuuttajalle: oleskelulupa ja jatkolupa | SKMY",
        "description": "Käytännön opas kuuroille ja viittomakielisille maahanmuuttajille: Migrin oleskelulupa, jatkolupa, Enter Finland ja tulkkaus.",
        "h1": "Migri maahanmuuttajalle Suomessa",
        "sections": [
            ("Migri ja oleskelu Suomessa", "Migri käsittelee oleskelulupiin, jatkolupiin ja kansalaisuuteen liittyviä asioita. Maahanmuuttajan kannattaa selvittää oman oleskelun peruste ja hakea lupaa hyvissä ajoin. Kuuro maahanmuuttaja tai viittomakielinen maahanmuuttaja voi käyttää samaa virallista hakupolkua kuin muut hakijat, mutta tarvitsee joskus enemmän aikaa viestintään, asiakirjojen ymmärtämiseen tai tulkin järjestämiseen."),
            ("Hakemus ja Enter Finland", "Täytä hakemus huolellisesti ja liitä vain pyydetyt, ajantasaiset asiakirjat. Enter Finland -palvelussa voit seurata hakemusta ja vastaanottaa lisäselvityspyyntöjä. Tarkista jokainen viesti ja määräaika. Jos tarvitset henkilökohtaista käyntiä, ota mukaan alkuperäiset asiakirjat. Älä perusta päätöstä vanhoihin ohjeisiin: vaatimukset ja käsittelyajat voivat muuttua, joten käytä aina Migrin virallista lähdettä."),
            ("Tulkki, DVV ja Kela", "Jos tarvitset viittomakielen tulkin Migri-tapaamiseen, järjestä se mahdollisimman aikaisin. Kelan tulkkauspalvelu voi auttaa, jos sinulle on myönnetty oikeus palveluun. Oleskeluluvan jälkeen seuraavat käytännön vaiheet voivat olla henkilötunnus ja osoitteen rekisteröinti DVV:ssä sekä Kelan etuuksien selvittäminen. Näiden palvelujen linkittäminen omaan tilanteeseen tekee Suomeen asettumisesta selkeämpää."),
            ("Pidä hakemus hallinnassa", "Tee itsellesi lista hakemuksen vaiheista: mitä on lähetetty, mitä vielä puuttuu ja milloin viesti pitää tarkistaa seuraavan kerran. Käytä omaa sähköpostia ja palvelun ilmoituksia säännöllisesti. Jos asiakirja on toisella kielellä, selvitä etukäteen hyväksytäänkö se ja tarvitaanko käännös. Älä luovuta alkuperäisiä asiakirjoja ilman virallista ohjetta tai kuittia."),
            ("Valmistaudu henkilökohtaiseen käyntiin", "Varaa käyntiin riittävästi aikaa ja ota mukaan kutsu, passi sekä hakemukseen liittyvät alkuperäiset asiakirjat. Kirjoita etukäteen lyhyt lista kysymyksistä, jotta tärkeä asia ei unohdu. Jos tarvitset saavutettavaa viestintää, pyydä järjestelyä mahdollisimman varhain. Tulkki ei tee päätöstä puolestasi, mutta auttaa varmistamaan, että voit ymmärtää keskustelun ja kertoa oman asiasi."),
            ("Muut palvelut luvan jälkeen", "Oleskelulupa ei automaattisesti ratkaise kaikkia Suomeen asettumisen asioita. Sen jälkeen voit joutua hoitamaan henkilötunnuksen, osoitteen, pankin, Kelan tai työnhaun vaiheita. Avaa DVV:n, Kelan ja TE-palvelujen ohjeet yksi kerrallaan. Näin tehtävät eivät kasaannu, ja tiedät aina, mikä viranomainen vastaa seuraavasta asiasta."),
            ("Kysy ennen kuin määräaika päättyy", "Jos viesti, liitepyyntö tai päätös ei ole selvä, hae neuvoa heti. Viranomainen voi kertoa, mistä saat ajantasaisen tiedon, ja SKMY voi auttaa ymmärtämään käytännön ohjetta. Ajoissa kysyminen on usein helpompaa kuin puuttuvan asiakirjan selvittäminen myöhemmin."),
        ],
        "faq": [
            ("Milloin jatkolupaa pitää hakea?", "Hae ennen nykyisen luvan päättymistä ja tarkista määräaika aina Migrin ohjeesta."),
            ("Voinko seurata hakemusta verkossa?", "Kyllä, hakemuksen vaiheita ja mahdollisia lisäselvityksiä voi seurata Enter Finlandissa."),
            ("Tarvitsenko tulkin Migri-käynnille?", "Jos tarvitset viittomakielen tulkkia, järjestä se etukäteen tulkkauspalvelun ohjeiden mukaan."),
            ("Mitä teen luvan myöntämisen jälkeen?", "Selvitä henkilötunnus ja rekisteröinti DVV:ssä sekä oma Kela-tilanteesi."),
        ],
    },
    "te": {
        "title": "TE-palvelut maahanmuuttajalle: työnhaku ja tuki | SKMY",
        "description": "Ohje kuuroille ja viittomakielisille maahanmuuttajille työnhakuun Suomessa: työnhakijaksi ilmoittautuminen, koulutus ja tulkkaus.",
        "h1": "TE-palvelut ja työnhaku maahanmuuttajalle",
        "sections": [
            ("Työnhaun ensimmäiset askeleet", "TE-palvelut ja alueelliset työllisyyspalvelut auttavat työnhaussa, koulutukseen hakeutumisessa ja oman tilanteen suunnittelussa. Maahanmuuttajalle ensimmäinen tärkeä askel voi olla työnhakijaksi ilmoittautuminen. Kuuro maahanmuuttaja tai viittomakielinen maahanmuuttaja voi pyytää viestintään liittyviä järjestelyjä, jotta tapaaminen ja ohjeet ovat saavutettavia. Pidä yhteystietosi ajan tasalla ja reagoi palvelun viesteihin määräajassa."),
            ("Valmistaudu tapaamiseen", "Tee selkeä CV ja kerää todistukset aiemmasta työstä, koulutuksesta ja kielitaidosta. Kirjaa valmiiksi, millaista työtä etsit ja millaista tukea tarvitset. Työllistymissuunnitelma auttaa sopimaan seuraavista toimista, kuten työnhausta, kurssista tai koulutuksesta. Jos et ymmärrä asiakirjaa tai digitaalista palvelua, pyydä selitystä ajoissa. Näin vältät sen, että tärkeä määräaika jää huomaamatta."),
            ("Yhteys Kelaan, Migriin ja tulkkaukseen", "Työnhakijan etuudet voivat liittyä Kelaan, joten tarkista oma oikeutesi ja ilmoitusten vaikutus ennen päätöksiä. Oleskelulupaan liittyvissä kysymyksissä oikea viranomainen on Migri. Jos tarvitset viittomakielen tulkin TE-palvelujen tapaamiseen, selvitä Kelan tulkkauspalvelu hyvissä ajoin. SKMY:n tulkkaussivulta löydät käytännön apua ja viestipohjan tapaamisen varaamista varten."),
            ("Etene pienin askelin", "Työnhaku voi viedä aikaa, joten tee viikoittainen suunnitelma: hae sopivia paikkoja, päivitä CV:tä ja seuraa sovittuja tehtäviä. Tallenna hakemukset ja kutsut yhteen paikkaan. Koulutus, kieliopinnot tai työharjoittelu voivat olla hyödyllisiä seuraavia askelia. Kerro palvelulle, jos tarvitset saavutettavaa viestintää tai tulkin, jotta voit osallistua tasavertaisesti tapaamiseen ja suunnitelman tekemiseen."),
            ("Pidä yhteys palveluun", "Työllisyyspalvelu voi lähettää viestejä, kutsuja tai tehtäviä, joihin pitää reagoida tiettyyn päivään mennessä. Tarkista palvelu säännöllisesti ja säilytä kopiot viesteistä. Jos et pääse tapaamiseen tai tarvitset tulkin, ilmoita muutoksesta heti. Avoin viestintä auttaa palvelua ehdottamaan tilanteeseesi sopivaa tukea ja vähentää väärinkäsitysten riskiä."),
            ("Rakenna oma työnhakupolku", "Kaikille ei löydy työtä samalla tavalla tai samalla aikataululla. Aloita omasta osaamisesta, kiinnostuksen kohteista ja siitä, millainen työympäristö on sinulle saavutettava. Kysy koulutusvaihtoehdoista ja seuraa avoimia paikkoja useasta lähteestä. Kun saat kutsun haastatteluun tai neuvontaan, valmistele tarvittaessa tulkkaus ja kerro käytännön tarpeistasi hyvissä ajoin."),
            ("Hyödynnä oma osaaminen", "Kerro työnhaussa myös kielistä, työkokemuksesta ja viittomakieleen liittyvästä osaamisesta. Ne voivat olla vahvuuksia työssä. Selkeästi kuvattu oma osaaminen helpottaa työnantajaa ja neuvojaa näkemään, millaiset tehtävät, koulutus tai tuki sopivat juuri sinulle."),
        ],
        "faq": [
            ("Miten ilmoittaudun työnhakijaksi?", "Aloita oman alueesi työllisyyspalvelun tai Työmarkkinatorin ajantasaisesta ohjeesta."),
            ("Mitä otan mukaan tapaamiseen?", "CV, todistukset, henkilöllisyysasiakirjat ja omat kysymykset ovat yleensä hyödyllisiä."),
            ("Voinko saada tulkin tapaamiseen?", "Jos sinulla on oikeus tulkkauspalveluun, tulkki voidaan järjestää tapaamista varten."),
            ("Vaikuttaako työnhaku Kelaan?", "Työnhakijan tilanne voi vaikuttaa etuuksiin; tarkista oma tilanteesi Kelasta."),
        ],
    },
}


def _localized(category, lang, fi_content):
    """Provide non-fallback metadata and concise localized editorial copy."""
    names = {
        "ru": {
            "dvv": ("DVV: henkilötunnus и регистрация в Финляндии | SKMY", "Инструкция для глухих и жестоязычных иммигрантов: DVV, henkilötunnus, адрес и переводчик в Финляндии."),
            "kela": ("Kela для иммигрантов: пособия, OmaKela и переводчик | SKMY", "Понятный гид для глухих и жестоязычных иммигрантов: пособия Kela, OmaKela и услуги сурдоперевода."),
            "migri": ("Migri для иммигрантов: ВНЖ и продление | SKMY", "Практическая информация для глухих и жестоязычных иммигрантов: Migri, ВНЖ, Enter Finland и переводчик."),
            "te": ("TE-palvelut для иммигрантов: поиск работы и поддержка | SKMY", "Инструкция для глухих и жестоязычных иммигрантов: поиск работы, регистрация и сурдоперевод в Финляндии."),
        },
        "en": {
            "dvv": ("DVV personal identity code and registration in Finland | SKMY", "Guidance for Deaf and sign-language immigrants: DVV, a personal identity code, address registration and interpreting in Finland."),
            "kela": ("Kela for immigrants: benefits, OmaKela and interpreting | SKMY", "Clear guidance for Deaf and sign-language immigrants: Kela benefits, OmaKela and interpreting services in Finland."),
            "migri": ("Migri for immigrants: residence permits and extensions | SKMY", "Practical guidance for Deaf and sign-language immigrants: Migri, residence permits, Enter Finland and interpreting."),
            "te": ("TE services for immigrants: job search and support | SKMY", "Guidance for Deaf and sign-language immigrants: jobseeker registration, employment support and interpreting in Finland."),
        },
    }
    title, description = names[lang][category]
    # Finnish category body remains visible only on Finnish pages.  RU/EN pages
    # use a concise, language-appropriate introduction while retaining FAQ and links.
    intro = {
        "ru": f"Этот раздел объясняет, как {category.upper()} связан с жизнью глухих и жестоязычных иммигрантов в Финляндии. Проверьте официальные инструкции, подготовьте документы заранее и используйте ссылки на связанные службы ниже.",
        "en": f"This section explains how {category.upper()} relates to life in Finland for Deaf and sign-language immigrants. Check official guidance, prepare documents early, and use the related-service links below.",
    }[lang]
    return {"title": title, "description": description, "h1": title.split(" | ")[0], "sections": [("Information", intro)], "faq": fi_content["faq"]}


def category_seo(category_slug, lang):
    """Return content only for the four SEO-priority categories."""
    content = _FI.get(category_slug)
    if not content:
        return None
    if lang == "fi":
        return content
    if lang in ("ru", "en"):
        return _localized(category_slug, lang, content)
    return None


def faq_schema(items):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question", "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        } for question, answer in items],
    }, ensure_ascii=False).replace("</", "<\\/")
