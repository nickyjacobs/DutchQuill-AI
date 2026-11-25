"use strict";
/* DutchQuill Studio. Praat alleen met de lokale dq-server; alles wat de gebruiker invoert gaat via textContent. */

// ------------------------------------------------------------------ token en API
const TOKEN = (() => {
  const uitHash = new URLSearchParams(location.hash.slice(1)).get("t");
  try {
    if (uitHash) sessionStorage.setItem("dq-token", uitHash);
    return uitHash || sessionStorage.getItem("dq-token");
  } catch (e) { return uitHash; }
})();
const START_SCHERM = new URLSearchParams(location.hash.slice(1)).get("s");
const START_MENU = new URLSearchParams(location.hash.slice(1)).get("m");
const START_TAAL = new URLSearchParams(location.hash.slice(1)).get("l");
if (location.hash) history.replaceState(null, "", location.pathname);

async function api(methode, pad, body) {
  const r = await fetch(pad, {
    method: methode,
    headers: { "X-DQ-Token": TOKEN || "", "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = {};
  try { data = await r.json(); } catch (e) { /* leeg */ }
  if (!r.ok) throw new Error(data.fout || T("fout_algemeen"));
  return data;
}

// ------------------------------------------------------------------ teksten
const TEKST = {
  nl: {
    studio: "Studio",
    terugdraaien: "Terugdraaien", bekijkopslaan: "Bekijken en opslaan", opslaan: "Opslaan",     sluiten: "Sluiten", volgende: "Volgende", vorige: "Vorige", beginnen: "Beginnen",
    fout_algemeen: "Er ging iets mis. Probeer het opnieuw.",
    geen_token: "Deze pagina hoort bij een Studio-sessie. Open de Studio opnieuw via /dutchquill:instellen.",
    installatie: "Installatie", instellingen: "Instellingen",
    s_welkom: "Welkom", s_werkmap: "Werkmap", s_profiel: "Profiel", s_controles: "Controles", s_toon: "Toon",
    s_uitvoer: "Uitvoer", s_templates: "Templates", s_stem: "Mijn stem", s_privacy: "Privacy",
    s_student: "Student", s_onderhoud: "Onderhoud", s_afronden: "Afronden",
    g_start: "Start", g_schrijven: "Hoe je schrijft", g_uitvoer: "Wat je krijgt", g_jij: "Jij en je gegevens",
    g_systeem: "Systeem", s_over: "Over DutchQuill", menu_open: "Menu openen", menu_dicht: "Menu inklappen",
    over_titel: "Over DutchQuill",
    over_1: "DutchQuill begon op de hogeschool. Mijn rapporten moesten volgens APA en op academisch niveau, en ik wilde precies weten wat dat betekende. Dat werd een flinke rabbit hole. De meeste mensen denken bij APA alleen aan bronvermelding, maar het gaat ook over de marges van je pagina, hoe je titelblad eruitziet, hoe je tabellen, figuren en bijlagen opneemt, het inspringen van elke alinea (ook de eerste) en de hangende inspringing in je literatuurlijst. En dan heb je nog de vraag wat academisch schrijven echt is, en hoe je AI daarbij gebruikt zonder jezelf voorbij te lopen.",
    over_2: "Het begon met een Word-template die alles meteen goed zette. Daarna liet ik mijn rapporten nakijken, en met wat daaruit kwam maakte ik er volwaardige rapporten van.",
    over_3: "Toen wilde ik meer. Sneller mails beantwoorden, makkelijker een LinkedIn-post schrijven, procesdocumentatie voor mijn werk of de README van een repo, allemaal vanuit ruwe notities, tekst en screenshots die ik al had verzameld. DutchQuill maakt daar een mooi eindresultaat van.",
    over_4: "Op het eerste gezicht lijkt het misschien een tool van iemand die alles makkelijk wil. Deels klopt dat ook wel 😉 Maar voor mij was het vooral een leerproject. Ik weet nu meer over APA dan ik ooit had verwacht; soms wist ik dingen over inspringen, het juiste gebruik van bijlagen en andere APA-regels die docenten en medestudenten ook niet wisten. Ik leerde hoe AI tekst maakt, hoe plagiaatcontrole werkt en wat goed academisch schrijven is. Er zit veel tijd in, en het resultaat deel ik graag.",
    over_5: "DutchQuill is open source (MIT). Zie je een fout of heb je een idee, open dan een issue op GitHub.",
        kop_socials: "Socials",
        f1_naam: "Flesch-Douma",
    f1: "de Nederlandse leesbaarheidsformule: 206,84 − 77 × lettergrepen per woord − 0,93 × woorden per zin. Hoe hoger, hoe makkelijker de tekst; een hbo-rapport zit meestal tussen 30 en 50.",
    f2_naam: "MATTR",
    f2: "Moving Average Type-Token Ratio: hoeveel verschillende woorden je gebruikt, gemeten over steeds verschuivende stukken van 100 woorden. Een lage score betekent veel herhaling.",
    f3_naam: "Spreiding van de zinslengte",
    f3: "mensen wisselen korte en lange zinnen af; AI-tekst heeft vaak zinnen die bijna allemaal even lang zijn.",
    over_naam: "- Nicky Jacobs", l_repo: "GitHub Repo: DutchQuill AI", l_github: "My GitHub Page", l_site: "My Website", l_linkedin: "My LinkedIn",
    weergave: "Weergave", wolken: "Bewegende wolken", wolken_uitleg: "Wolken die rustig langs de zijkanten drijven.",
    nu_controleren: "Nu controleren", controleren_bezig: "Bezig met controleren, dat duurt ongeveer een halve minuut...",
    controle_ok: "Alles is actueel. De volgende herinnering komt over een maand.",
    controle_gewijzigd: "Deze bronnen zijn veranderd. Typ in Claude /dutchquill:bijwerken om de gidsen bij te werken:",
    controle_fouten: "Niet alle bronnen waren bereikbaar:",
    m_fout: "Dat lukte niet",
    m_info: "Goed om te weten",
    m_succes: "Gelukt",
    m_letop: "Let op",
    m_sluiten: "Melding sluiten",
    m_eigen_titel: "Eigen profiel gemaakt",
    eigen_kopie: "Je past nu je eigen profiel %s aan. Het meegeleverde profiel %s blijft zoals het was. Vergeet niet op te slaan.",
    m_opgeslagen_titel: "Instellingen opgeslagen",
    m_opgeslagen_tekst: "Je wijzigingen staan in dutchquill.yaml en gelden vanaf je volgende opdracht.",
    m_geen_titel: "Niets om op te slaan",
    geen_wijzigingen: "Er is niets veranderd sinds de laatste keer opslaan.",
    m_map_titel: "Werkmap aangemaakt",
    map_gemaakt: "Je mappen staan klaar. Kies nu je profiel.",
    m_gekopieerd_titel: "Gekopieerd",
    gekopieerd: "Plak /dutchquill:bijwerken in Claude om de gidsen te laten nakijken.",
        m_formaat_tekst: "Kies minstens één bestandsformaat voor je documenten.",
    m_template_titel: "Template toegevoegd",
    m_template_mist: "Template toegevoegd, maar er ontbreken kopstijlen. Kijk bij Controleer wat er mist.",
    m_aanpas_titel: "Template gemaakt",
    m_aanpas_tekst: "%s is je nieuwe standaardtemplate. Vergeet niet op te slaan.",
    m_profiel_titel: "Profiel gemaakt",
    m_profiel_tekst: "%s is nu actief. Vergeet niet op te slaan.",
    m_stem_titel: "Tekst toegevoegd",
    m_stem_tekst: "%s staat in mijn-stijl. Klik op Meet mijn stem om je stemprofiel bij te werken.",
    m_gemeten_titel: "Stem gemeten",
    m_gemeten_tekst: "Je stemprofiel is bijgewerkt. DutchQuill gebruikt het bij je volgende tekst.",
    m_vak_titel: "Bestand toegevoegd",
    m_vak_tekst: "%s voor %s staat klaar. Bij een review wordt je rapport hierop gecontroleerd.",
    m_upload_titel: "Afbeelding toegevoegd",
        m_sjabloon_titel: "Sjabloon opgeslagen",
    m_sjabloon_tekst: "DutchQuill gebruikt nu jouw sjabloon voor %s.",
    m_herstel_titel: "Standaard teruggezet",
    m_herstel_tekst: "%s gebruikt weer het meegeleverde sjabloon. Je eigen versie staat bewaard in templates/genres/oud.",
    m_map_kiezen: "Mapkiezer",
    upload: "Uploaden",
    voorbeeld_kop: "Voorbeeld",
    voorbeeld_mix: "Een benadering: bij het schrijven past Claude je mix volledig toe.",
    vb_aan: "Aan: het projectteam",
    berichten: "Berichten",
    documenten: "Documenten",
    s_professioneel: "Professioneel",
    prof_titel: "Professionele gegevens",
    prof_uitleg: "Voor de afsluiting en handtekening van je mails. Alles is optioneel.",
    prof_afb: "Handtekening en banner",
    prof_afb_uitleg: "Een handtekening of mailbanner (met bijvoorbeeld je naam, foto, telefoon en organisatie) komt onder je mail. DutchQuill noemt hem bij het schrijven; plaatsen doe je in je mailprogramma.",
    handtekening: "handtekening",
    banner: "banner",
    upload_handtekening: "Handtekening uploaden",
    upload_banner: "Banner uploaden",
    prof_voorbeeld: "Zo sluit een zakelijke mail af",
    sjablonen_titel: "Sjablonen per soort tekst",
    sjablonen_uitleg: "Een sjabloon bepaalt de opbouw van een soort tekst: wat er in een mail, notitie of rapport hoort. Pas het meegeleverde sjabloon aan of upload je eigen versie (.md of .txt).",
    andere_soorten: "Andere soorten tekst",
    standaard: "Standaard",
    eigen_sjabloon: "Eigen",
    aanpassen: "Aanpassen",
    terug_standaard: "Terug naar standaard",
    opslaan_sjabloon: "Opslaan als eigen sjabloon",
    herstel_vraag: "Terug naar het meegeleverde sjabloon? Je eigen versie wordt bewaard in templates/genres/oud.",
    kop_formules: "Wat de humanizer meet",
    formules_intro: "Onderweg leerde ik ook rekenen aan tekst. Drie formules die de humanizer gebruikt:",
    m_upload_tekst: "Je %s staat in templates/email. Sla je instellingen op om hem te gebruiken.",
    f_docx: "Om verder te bewerken",
    f_pdf: "Klaar om te delen",
    f_md: "Voor GitHub en Obsidian",
    f_txt: "Platte tekst, overal te openen",
    f_html: "Voor web en mail",
    berichten_uitleg: "Kort en snel, meestal direct te plakken.",
    documenten_uitleg: "Langere stukken; meestal wil je hier een bestand.",
    geen_bestand: "Nog geen afbeelding.",
    upload_sjabloon: "Uploaden",
    annuleren: "Annuleren",
    m_formaat_titel: "Minstens één formaat",
    kop_verhaal: "Het verhaal",
    mv_werkmap: "je werkmap",
    mv_in: "Hier zet jij je materiaal neer",
    mv_uit: "Hier vind je het resultaat",
    mv_pijl: "DutchQuill leest, schrijft en controleert",
    mv_notities: "Losse aantekeningen en ideeën",
    mv_rapporten: "Teksten om te herschrijven of na te kijken",
    mv_beeld: "Screenshots, foto's en figuren",
    mv_bronnen: "Pdf's, artikelen en een lijst met links",
    mv_mijn_stijl: "Eigen teksten, zodat het klinkt als jij",
    mv_schrijven: "Nieuwe teksten",
    mv_herschrijven: "Verbeterde versies van je teksten",
    mv_reviewen: "Feedback, je tekst zelf blijft gelijk",
    mv_humaniseren: "Teksten die menselijker klinken",
    mv_versies: "Per titel een eigen map, met v1, v2 en verder voor elke nieuwe ronde.",
    mv_ook: "Ook in je werkmap",
    mv_yaml: "Je instellingen: wat je hier in de Studio kiest",
    mv_templates: "Je eigen Word-templates en sjablonen",
    mv_regels: "Woorden die je wel of juist niet wilt",
    gidsen_kop: "Referentiegidsen",
    of_in_claude: "Gidsen bijwerken: typ dit in Claude.",
    taal_versies: "Taal en versies",
    vak_eerst: "Voeg hierboven eerst een vak toe.",
    welkom_titel: "Welkom bij DutchQuill",
    welkom_1: "DutchQuill schrijft, herschrijft, reviewt en humaniseert je teksten: een rapport, een mail, een LinkedIn-post of een README.",
    welkom_2: "Jij bepaalt hoe het klinkt, waarop het let en in welk formaat het terugkomt. Dat stel je hier in; later kan alles ook in een gesprek met Claude.",
    welkom_3: "Het instellen duurt een paar minuten. Er gaat niets naar internet.",
    w_schrijven: "Schrijven", w_schrijven_u: "Rapporten, mails, posts en README's vanuit je eigen materiaal.",
    w_herschrijven: "Herschrijven", w_herschrijven_u: "Korter, helderder, anders van toon of vertaald.",
    w_reviewen: "Reviewen", w_reviewen_u: "Feedback op taal, opbouw, APA en de rubric van je vak.",
    w_humaniseren: "Humaniseren", w_humaniseren_u: "AI-patronen eruit, en klinken zoals jij.",
    w_duur: "Klaar in een paar minuten", w_lokaal: "Alles blijft op je computer",
    thema_licht_l: "Licht", thema_auto_l: "Automatisch", thema_donker_l: "Donker",
    werkmap_titel: "Waar komt je DutchQuill-map?",
    werkmap_uitleg: "In deze map zet je je materiaal (notities, rapporten, afbeeldingen, bronnen) en daar komen je documenten terecht, per versie.",
    bureaublad: "Op het bureaublad", zelf: "Zelf kiezen",
    kies_map: "Kies een map", of_typ: "Of typ het pad", taal: "Taal van je teksten",
    taal_nl: "Nederlands", taal_en: "Engels", taal_auto: "Automatisch (volgt je materiaal)",
    map_aanmaken: "Map aanmaken",     zo_ziet: "Zo ziet de map eruit:", huidige_map: "Je werkmap",
    map_verplaatsen: "Verplaatsen kan via Claude: zeg \"verplaats mijn DutchQuill-map naar ...\".",
    versies: "Versies bijhouden", versies_uitleg: "Elke nieuwe ronde over dezelfde titel komt in een eigen map: v1, v2, v3.",
    profiel_titel: "Waarvoor gebruik je DutchQuill vooral?",
    profiel_uitleg: "Een profiel is een startpunt. Alles is daarna los aan te passen, en je kunt eigen profielen maken.",
    eigen_profielen: "Eigen profielen", nieuw_profiel: "Nieuw profiel", naam: "Naam", bouwt_op: "Bouwt voort op",
    beschrijving: "Beschrijving", maken: "Maken", verwijderen: "Verwijderen", bouwt_op_kort: "bouwt op",
    naam_regel: "Kleine letters, cijfers en streepjes, bijvoorbeeld mijn-linkedin.",
    naam_bestaat: "Die naam bestaat al.",
    genre_titel: "Automatisch een profiel per soort tekst",
    genre_uitleg: "Bijvoorbeeld: mails altijd met het profiel zakelijk, LinkedIn-posts met je eigen profiel.",
    volgt_actief: "Volgt het actieve profiel",
    actief_profiel: "Je past het profiel %s aan.",
        controles_titel: "Waar moet DutchQuill op letten?",
    controles_uitleg: "Zet aan wat bij jouw teksten past. Een student wil alles, een LinkedIn-post heeft geen APA nodig.",
    vb_apa: "(Jansen, 2024) in de tekst, en een literatuurlijst volgens APA 7",
    vb_academische_stijl: "\"De resultaten zijn gunstig\" in plaats van \"Je zult zien dat het meevalt\"",
    vb_taalregels: "\"Hij vindt\" in plaats van \"hij vind\"; zinnen die je in één keer leest",
    vb_humaniseren: "Geen \"in de huidige digitale wereld\", wel een concreet voorbeeld",
    toon_titel: "Hoe moet het klinken?",
    toon_uitleg: "Schuif en kijk hoe dezelfde mail verandert.",
    aanspreekvorm: "Aanspreekvorm", mix: "Eigen mix", mix_uitleg: "Bijvoorbeeld: zakelijk, maar met een luchtige afsluiting.",
    aan_auto: "Automatisch", aan_je: "je", aan_u: "u", aan_geen: "Lezer niet aanspreken",
    uitvoer_titel: "Wat krijg je terug?",
    formaten: "Bestandsformaten", chat_voor: "Alleen in de chat, zonder bestand",
    chat_voor_uitleg: "Deze teksten verschijnen gewoon in het gesprek. Zeg \"sla op\" als je toch een bestand wilt.",
    template: "Template",
    templates_titel: "Templates",
    templates_uitleg: "Een template bepaalt hoe je Word- en pdf-bestanden eruitzien. Je kunt je eigen huisstijl toevoegen.",
    meegeleverd: "meegeleverd", eigen: "eigen", actief: "actief", controleer: "Controleer", maak_standaard: "Maak standaard",
    upload_template: "Eigen Word-template toevoegen", kies_bestand: "Kies een bestand",
    aanpassen_titel: "Een template aanpassen", aanpassen_uitleg: "Maakt een kopie met jouw lettertype, kleur en marges. Het origineel blijft.",
    van: "Uitgangspunt", nieuwe_naam: "Naam van de kopie", kop_font: "Lettertype koppen", kop_grootte: "Grootte kop 1",
    kop_kleur: "Kleur koppen", tekst_font: "Lettertype tekst", tekst_grootte: "Grootte tekst", regelafstand: "Regelafstand",
    marge: "Marges (cm)", kopie_maken: "Kopie maken",
    check_ok: "Deze template is bruikbaar.", check_mapping: "Bruikbaar met een kleine vertaling van stijlnamen:",
    check_mist: "Hier ontbreken kopstijlen. Maak in Word de stijlen Kop 1 en Kop 2 aan, of kies een andere template.",
    stem_titel: "Klinkt als jij",
    stem_uitleg: "Zet een paar teksten neer die je zelf schreef: een verslag, een blog, een paar mails. DutchQuill meet je zinslengte, je leestekens en hoe je zinnen begint, en schrijft zo meer zoals jij.",
    stem_bestanden: "Jouw teksten", stem_leeg: "Nog geen eigen teksten.", stem_toevoegen: "Teksten toevoegen",
    stem_meten: "Meet mijn stem", stem_gebruiken: "Schrijf in mijn stem",
    st_woorden: "Woorden gemeten", st_zinslengte: "Gemiddelde zinslengte", st_kort: "Korte zinnen (minder dan 8 woorden)",
    st_streepjes: "Gedachtestreepjes per 1000 woorden", st_dubbelepunt: "Dubbele punten per 1000 woorden",
    st_begin: "Zo begin je vaak een zin", st_jeu: "je / u",
    privacy_titel: "Wat gaat er naar buiten?",
    privacy_uitleg: "Standaard blijft alles op je computer, behalve wat Claude zelf verwerkt.",
    lt_extra: "Je tekst gaat dan naar api.languagetool.org. Zet dit uit voor vertrouwelijk werk.",
    student_titel: "Studentgegevens",
    student_uitleg: "Voor de titelpagina van een hbo-rapport. Alles is optioneel.",
    vakken: "Vakken", vak: "Vak", code: "Code", toevoegen: "Toevoegen", docenten: "Docenten", rol: "Rol",
    vak_bestanden: "Inlevereisen en beoordelingscriteria",
    vak_uitleg: "Upload per vak de checklist of rubric. Bij een review beoordeelt DutchQuill je rapport dan ook daarop.",
    inlevereisen: "Inlevereisen", rubric: "Beoordelingscriteria",
    onderhoud_titel: "Onderhoud",
    gidsen_stand: "De gidsen (APA, taal, humaniseren) zijn gecontroleerd op %s.",
    bijwerken_uitleg: "Eén keer per maand herinnert DutchQuill je eraan om ze na te kijken. Met Nu controleren zie je meteen of er bronnen veranderd zijn; het bijwerken zelf doet Claude.",
    kopieer: "Kopieer", herinnering: "Herinnering na (dagen)",
    versie: "Versie", klaar_sluiten: "Klaar en Studio sluiten",
    afronden_titel: "Klaar om op te slaan",
    afronden_uitleg: "Dit wordt je startinstelling. Je kunt alles later aanpassen, hier of in een gesprek.",
    verder_instellen: "Opslaan en verder instellen", opslaan_klaar: "Opslaan en klaar",
    wijzigingen: "%s wijziging(en) nog niet opgeslagen.", opgeslagen: "Opgeslagen.",
    voorbeeld_titel: "Dit verandert er",     fouten_titel: "Zo kan het niet worden opgeslagen",
    onopgeslagen: "Je hebt nog wijzigingen die niet zijn opgeslagen. Toch sluiten?",
    toch_sluiten: "Toch sluiten",
    gesloten_titel: "De Studio is gesloten",
    gesloten_uitleg: "Je kunt dit tabblad sluiten. Claude ziet wat er veranderd is.",
    bezig: "Bezig...",
  },
  en: {
    studio: "Studio",
    terugdraaien: "Undo changes", bekijkopslaan: "Review and save", opslaan: "Save",     sluiten: "Close", volgende: "Next", vorige: "Back", beginnen: "Get started",
    fout_algemeen: "Something went wrong. Try again.",
    geen_token: "This page belongs to a Studio session. Open the Studio again with /dutchquill:instellen.",
    installatie: "Setup", instellingen: "Settings",
    s_welkom: "Welcome", s_werkmap: "Workspace", s_profiel: "Profile", s_controles: "Checks", s_toon: "Tone",
    s_uitvoer: "Output", s_templates: "Templates", s_stem: "My voice", s_privacy: "Privacy",
    s_student: "Student", s_onderhoud: "Maintenance", s_afronden: "Finish",
    g_start: "Start", g_schrijven: "How you write", g_uitvoer: "What you get", g_jij: "You and your data",
    g_systeem: "System", s_over: "About DutchQuill", menu_open: "Open menu", menu_dicht: "Collapse menu",
    over_titel: "About DutchQuill",
    over_1: "DutchQuill started at university. My reports had to follow APA and meet an academic standard, and I wanted to know exactly what that meant. It turned into quite a rabbit hole. Most people think APA is only about citations, but it also covers your page margins, what your title page looks like, how you add tables, figures and appendices, indenting every paragraph (the first one too) and the hanging indent in your reference list. Then there is the question of what academic writing really is, and how to use AI for it without fooling yourself.",
    over_2: "It started with a Word template that got all of that right from the start. Next I had my reports reviewed, and used the feedback to turn them into proper, finished reports.",
    over_3: "Then I wanted more. Answering emails faster, writing a LinkedIn post more easily, process documentation for work or the README of a repo, all from rough notes, text and screenshots I had already collected. DutchQuill turns that into a polished result.",
    over_4: "At first glance it may look like a tool made by someone who wants everything to be easy. That's partly true 😉 But for me it was mostly a learning project. I now know more about APA than I ever expected; sometimes I knew things about indentation, using appendices the right way and other APA rules that teachers and classmates didn't. I learned how AI generates text, how plagiarism checks work and what good academic writing is. A lot of time went into it, and I am happy to share the result.",
    over_5: "DutchQuill is open source (MIT). Found a bug or have an idea? Open an issue on GitHub.",
        kop_socials: "Socials",
        f1_naam: "Flesch-Douma and Flesch Reading Ease",
    f1: "readability formulas for Dutch (206.84 − 77 × syllables per word − 0.93 × words per sentence) and English (206.835 − 84.6 × syllables per word − 1.015 × words per sentence). Higher means easier to read.",
    f2_naam: "MATTR",
    f2: "Moving Average Type-Token Ratio: how many different words you use, measured over a sliding window of 100 words. A low score means a lot of repetition.",
    f3_naam: "Sentence length spread",
    f3: "people mix short and long sentences; AI text often has sentences of almost the same length.",
    over_naam: "- Nicky Jacobs", l_repo: "GitHub Repo: DutchQuill AI", l_github: "My GitHub Page", l_site: "My Website", l_linkedin: "My LinkedIn",
    weergave: "Display", wolken: "Moving clouds", wolken_uitleg: "Clouds that drift slowly along the sides.",
    nu_controleren: "Check now", controleren_bezig: "Checking, this takes about half a minute...",
    controle_ok: "Everything is up to date. The next reminder comes in a month.",
    controle_gewijzigd: "These sources have changed. Type /dutchquill:bijwerken in Claude to update the guides:",
    controle_fouten: "Not every source could be reached:",
    m_fout: "That didn't work",
    m_info: "Good to know",
    m_succes: "Done",
    m_letop: "Heads up",
    m_sluiten: "Close notification",
    m_eigen_titel: "Own profile created",
    eigen_kopie: "You are now editing your own profile %s. The built-in profile %s stays as it was. Remember to save.",
    m_opgeslagen_titel: "Settings saved",
    m_opgeslagen_tekst: "Your changes are in dutchquill.yaml and apply from your next request.",
    m_geen_titel: "Nothing to save",
    geen_wijzigingen: "Nothing has changed since you last saved.",
    m_map_titel: "Workspace created",
    map_gemaakt: "Your folders are ready. Now pick your profile.",
    m_gekopieerd_titel: "Copied",
    gekopieerd: "Paste /dutchquill:bijwerken in Claude to have the guides checked.",
        m_formaat_tekst: "Choose at least one file format for your documents.",
    m_template_titel: "Template added",
    m_template_mist: "Template added, but heading styles are missing. Use Check to see what's missing.",
    m_aanpas_titel: "Template created",
    m_aanpas_tekst: "%s is your new default template. Remember to save.",
    m_profiel_titel: "Profile created",
    m_profiel_tekst: "%s is now active. Remember to save.",
    m_stem_titel: "Text added",
    m_stem_tekst: "%s is in my-style. Click Measure my voice to update your voice profile.",
    m_gemeten_titel: "Voice measured",
    m_gemeten_tekst: "Your voice profile is updated. DutchQuill uses it for your next text.",
    m_vak_titel: "File added",
    m_vak_tekst: "%s for %s is ready. A review will check your report against it.",
    m_upload_titel: "Image added",
        m_sjabloon_titel: "Template saved",
    m_sjabloon_tekst: "DutchQuill now uses your template for %s.",
    m_herstel_titel: "Default restored",
    m_herstel_tekst: "%s uses the built-in template again. Your own version is kept in templates/genres/oud.",
    m_map_kiezen: "Folder picker",
    upload: "Upload",
    voorbeeld_kop: "Example",
    voorbeeld_mix: "An approximation: when writing, Claude applies your mix in full.",
    vb_aan: "To: the project team",
    berichten: "Messages",
    documenten: "Documents",
    s_professioneel: "Professional",
    prof_titel: "Professional details",
    prof_uitleg: "For the sign-off and signature of your emails. Everything is optional.",
    prof_afb: "Signature and banner",
    prof_afb_uitleg: "A signature or email banner (for example your name, photo, phone and organisation) goes below your email. DutchQuill mentions it when writing; you place it in your email app.",
    handtekening: "signature",
    banner: "banner",
    upload_handtekening: "Upload signature",
    upload_banner: "Upload banner",
    prof_voorbeeld: "How a business email ends",
    sjablonen_titel: "Templates per kind of text",
    sjablonen_uitleg: "A template sets the structure of a kind of text: what belongs in an email, a note or a report. Adjust the built-in template or upload your own (.md or .txt).",
    andere_soorten: "Other kinds of text",
    standaard: "Default",
    eigen_sjabloon: "Yours",
    aanpassen: "Adjust",
    terug_standaard: "Back to default",
    opslaan_sjabloon: "Save as my template",
    herstel_vraag: "Go back to the built-in template? Your own version is kept in templates/genres/oud.",
    kop_formules: "What the humanizer measures",
    formules_intro: "Along the way I also learned to measure text. Three formulas the humanizer uses:",
    m_upload_tekst: "Your %s is in templates/email. Save your settings to use it.",
    f_docx: "To keep editing",
    f_pdf: "Ready to share",
    f_md: "For GitHub and Obsidian",
    f_txt: "Plain text, opens anywhere",
    f_html: "For web and email",
    berichten_uitleg: "Short and quick, usually ready to paste.",
    documenten_uitleg: "Longer pieces; here you usually want a file.",
    geen_bestand: "No image yet.",
    upload_sjabloon: "Upload",
    annuleren: "Cancel",
    m_formaat_titel: "At least one format",
    kop_verhaal: "The story",
    mv_werkmap: "your workspace",
    mv_in: "You put your material here",
    mv_uit: "Here you find the result",
    mv_pijl: "DutchQuill reads, writes and checks",
    mv_notities: "Loose notes and ideas",
    mv_rapporten: "Texts to rewrite or review",
    mv_beeld: "Screenshots, photos and figures",
    mv_bronnen: "PDFs, articles and a list of links",
    mv_mijn_stijl: "Your own texts, so it sounds like you",
    mv_schrijven: "New texts",
    mv_herschrijven: "Improved versions of your texts",
    mv_reviewen: "Feedback, your text stays the same",
    mv_humaniseren: "Texts that sound more human",
    mv_versies: "One folder per title, with v1, v2 and so on for every new round.",
    mv_ook: "Also in your workspace",
    mv_yaml: "Your settings: what you choose here in the Studio",
    mv_templates: "Your own Word templates and templates per kind of text",
    mv_regels: "Words you do or don't want",
    gidsen_kop: "Reference guides",
    of_in_claude: "To update the guides, type this in Claude.",
    taal_versies: "Language and versions",
    vak_eerst: "Add a course above first.",
    welkom_titel: "Welcome to DutchQuill",
    welkom_1: "DutchQuill writes, rewrites, reviews and humanizes your texts: a report, an email, a LinkedIn post or a README.",
    welkom_2: "You decide how it sounds, what it checks and which format you get back. You set that up here; later you can also just tell Claude.",
    welkom_3: "Setup takes a few minutes. Nothing goes to the internet.",
    w_schrijven: "Write", w_schrijven_u: "Reports, emails, posts and READMEs from your own material.",
    w_herschrijven: "Rewrite", w_herschrijven_u: "Shorter, clearer, another tone, or translated.",
    w_reviewen: "Review", w_reviewen_u: "Feedback on language, structure, APA and your course rubric.",
    w_humaniseren: "Humanize", w_humaniseren_u: "AI patterns out, and sounding like you.",
    w_duur: "Done in a few minutes", w_lokaal: "Everything stays on your computer",
    thema_licht_l: "Light", thema_auto_l: "Automatic", thema_donker_l: "Dark",
    werkmap_titel: "Where should your DutchQuill folder go?",
    werkmap_uitleg: "You put your material here (notes, reports, images, sources) and your documents land here, one folder per version.",
    bureaublad: "On the desktop", zelf: "Choose myself",
    kies_map: "Choose a folder", of_typ: "Or type the path", taal: "Language of your texts",
    taal_nl: "Dutch", taal_en: "English", taal_auto: "Automatic (follows your material)",
    map_aanmaken: "Create folder",     zo_ziet: "This is what it looks like:", huidige_map: "Your workspace",
    map_verplaatsen: "To move it, tell Claude: \"move my DutchQuill folder to ...\".",
    versies: "Keep versions", versies_uitleg: "Every new round on the same title gets its own folder: v1, v2, v3.",
    profiel_titel: "What will you mostly use DutchQuill for?",
    profiel_uitleg: "A profile is a starting point. You can change everything afterwards and create your own profiles.",
    eigen_profielen: "Your profiles", nieuw_profiel: "New profile", naam: "Name", bouwt_op: "Based on",
    beschrijving: "Description", maken: "Create", verwijderen: "Remove", bouwt_op_kort: "based on",
    naam_regel: "Lowercase letters, digits and hyphens, for example my-linkedin.",
    naam_bestaat: "That name already exists.",
    genre_titel: "A profile per kind of text",
    genre_uitleg: "For example: emails always with the business profile, LinkedIn posts with your own profile.",
    volgt_actief: "Follows the active profile",
    actief_profiel: "You are editing the profile %s.",
        controles_titel: "What should DutchQuill check?",
    controles_uitleg: "Switch on what fits your texts. A student wants everything; a LinkedIn post needs no APA.",
    vb_apa: "(Jansen, 2024) in the text and an APA 7 reference list",
    vb_academische_stijl: "\"The results are favourable\" instead of \"You'll see it's fine\"",
    vb_taalregels: "Correct spelling and grammar; sentences you read in one go",
    vb_humaniseren: "No \"in today's digital world\", but a concrete example",
    toon_titel: "How should it sound?",
    toon_uitleg: "Move the slider and see how the same email changes.",
    aanspreekvorm: "Form of address (Dutch)", mix: "Your own mix", mix_uitleg: "For example: businesslike, with a light closing line.",
    aan_auto: "Automatic", aan_je: "je (informal)", aan_u: "u (formal)", aan_geen: "Don't address the reader",
    uitvoer_titel: "What do you get back?",
    formaten: "File formats", chat_voor: "Chat only, no file",
    chat_voor_uitleg: "These texts simply appear in the conversation. Say \"save it\" if you want a file anyway.",
    template: "Template",
    templates_titel: "Templates",
    templates_uitleg: "A template sets how your Word and PDF files look. You can add your own house style.",
    meegeleverd: "built in", eigen: "yours", actief: "active", controleer: "Check", maak_standaard: "Make default",
    upload_template: "Add your own Word template", kies_bestand: "Choose a file",
    aanpassen_titel: "Adjust a template", aanpassen_uitleg: "Makes a copy with your font, colour and margins. The original stays.",
    van: "Start from", nieuwe_naam: "Name of the copy", kop_font: "Heading font", kop_grootte: "Heading 1 size",
    kop_kleur: "Heading colour", tekst_font: "Body font", tekst_grootte: "Body size", regelafstand: "Line spacing",
    marge: "Margins (cm)", kopie_maken: "Make copy",
    check_ok: "This template works.", check_mapping: "Works with a small translation of style names:",
    check_mist: "Heading styles are missing. Create Heading 1 and Heading 2 in Word, or pick another template.",
    stem_titel: "Sounds like you",
    stem_uitleg: "Add a few texts you wrote yourself: a report, a blog post, some emails. DutchQuill measures your sentence length, punctuation and how you start sentences, and writes more like you.",
    stem_bestanden: "Your texts", stem_leeg: "No texts of your own yet.", stem_toevoegen: "Add texts",
    stem_meten: "Measure my voice", stem_gebruiken: "Write in my voice",
    st_woorden: "Words measured", st_zinslengte: "Average sentence length", st_kort: "Short sentences (under 8 words)",
    st_streepjes: "Dashes per 1000 words", st_dubbelepunt: "Colons per 1000 words",
    st_begin: "You often start a sentence with", st_jeu: "je / u",
    privacy_titel: "What leaves your computer?",
    privacy_uitleg: "By default everything stays on your computer, apart from what Claude itself processes.",
    lt_extra: "Your text is then sent to api.languagetool.org. Switch this off for confidential work.",
    student_titel: "Student details",
    student_uitleg: "For the title page of an academic report. Everything is optional.",
    vakken: "Courses", vak: "Course", code: "Code", toevoegen: "Add", docenten: "Teachers", rol: "Role",
    vak_bestanden: "Submission requirements and grading criteria",
    vak_uitleg: "Upload the checklist or rubric per course. A review then also checks your report against it.",
    inlevereisen: "Requirements", rubric: "Grading criteria",
    onderhoud_titel: "Maintenance",
    gidsen_stand: "The guides (APA, language, humanizing) were checked on %s.",
    bijwerken_uitleg: "Once a month DutchQuill reminds you to check them. Check now shows right away whether sources have changed; Claude does the updating itself.",
    kopieer: "Copy", herinnering: "Reminder after (days)",
    versie: "Version", klaar_sluiten: "Done, close the Studio",
    afronden_titel: "Ready to save",
    afronden_uitleg: "This becomes your starting setup. You can change everything later, here or in a conversation.",
    verder_instellen: "Save and keep going", opslaan_klaar: "Save and finish",
    wijzigingen: "%s unsaved change(s).", opgeslagen: "Saved.",
    voorbeeld_titel: "What will change",     fouten_titel: "This can't be saved yet",
    onopgeslagen: "You have unsaved changes. Close anyway?",
    toch_sluiten: "Close anyway",
    gesloten_titel: "The Studio is closed",
    gesloten_uitleg: "You can close this tab. Claude can see what changed.",
    bezig: "Working...",
  },
};

const VOORBEELD = {
  nl: {
    aanhef: ["Geacht projectteam,", "Beste projectteam,", "Hallo allemaal,", "Hoi allemaal,", "Hé team,"],
    kern: ["Het overleg van donderdag 28 november is verplaatst naar vrijdag 29 november om 10.00 uur.",
      "We verplaatsen het overleg van donderdag naar vrijdag 29 november, 10.00 uur.",
      "Het overleg schuift van donderdag naar vrijdag 29 november, 10.00 uur.",
      "Het overleg van donderdag wordt vrijdag, om tien uur.",
      "Donderdag wordt vrijdag: zelfde overleg, tien uur, verse koffie."],
    kort: "Het overleg is nu op vrijdag 29 november, 10.00 uur.",
    vraag: {
      u: ["Wij verzoeken u te bevestigen of dit tijdstip u schikt.", "Kunt u laten weten of dat past?", "Past dat voor u?", "Lukt dat bij u?", "Bent u erbij?"],
      je: ["Wil je bevestigen of dit tijdstip je schikt?", "Kun je laten weten of dat past?", "Past dat voor je?", "Lukt dat bij jou?", "Ben je erbij?"],
      geen: ["Een bevestiging van het nieuwe tijdstip wordt op prijs gesteld.", "Graag een reactie of dit tijdstip past.",
        "Graag een korte reactie of dat past.", "Een seintje of het lukt, is fijn.", "Wie schuift er aan?"],
    },
    warm: { u: "Dank voor uw flexibiliteit.", je: "Dank voor je flexibiliteit.", geen: "Dank voor de flexibiliteit." },
    groet: ["Met vriendelijke groet,", "Met vriendelijke groet,", "Groet,", "Groetjes,", "Tot vrijdag!"],
    naam: "Sam",
  },
  en: {
    aanhef: ["Dear project team,", "Dear project team,", "Hello all,", "Hi all,", "Hey team,"],
    kern: ["The meeting of Thursday 28 November has been moved to Friday 29 November at 10:00.",
      "We are moving Thursday's meeting to Friday 29 November, 10:00.",
      "The meeting moves from Thursday to Friday 29 November, 10:00.",
      "Thursday's meeting is now on Friday at ten.",
      "Thursday became Friday: same meeting, ten o'clock, fresh coffee."],
    kort: "The meeting is now on Friday 29 November, 10:00.",
    vraag: {
      u: ["Please confirm whether this time suits you.", "Could you let me know if that works?", "Does that work for you?", "Can you make it?", "You in?"],
      je: ["Please confirm whether this time suits you.", "Could you let me know if that works?", "Does that work for you?", "Can you make it?", "You in?"],
      geen: ["Confirmation of the new time would be appreciated.", "A reply on whether this time works would be appreciated.",
        "A quick reply on whether that works is welcome.", "A heads-up if it works would be great.", "Who's in?"],
    },
    warm: { u: "Thanks for being flexible.", je: "Thanks for being flexible.", geen: "Thanks for the flexibility." },
    groet: ["Kind regards,", "Kind regards,", "Best,", "Cheers,", "See you Friday!"],
    naam: "Sam",
  },
};
// Bouwt de voorbeeldmail uit niveau, aanspreekvorm en (benaderd) de eigen mix.
function voorbeeldMail(i, aan, mix) {
  const V = VOORBEELD[S.taal];
  const vorm = aan === "auto" || !aan ? (i <= 1 ? "u" : "je") : aan;
  const m = (mix || "").toLowerCase();
  const heeft = (...w) => w.some((x) => m.includes(x));
  const niveauIn = () => {
    const woorden = [["formeel", "formal"], ["zakelijk", "business"], ["neutraal", "neutral"], ["informeel", "informal"],
      ["luchtig", "light", "grappig", "playful", "humor"]];
    let gevonden = -1;
    woorden.forEach((ws, j) => { if (ws.some((w) => new RegExp(`(^|[^a-z])${w}`).test(m))) gevonden = j; });
    return gevonden;
  };
  const kern = heeft("kort", "beknopt", "short", "brief", "concise") ? V.kort : V.kern[i];
  let groet = V.groet[i];
  if (heeft("afsluit", "groet", "slot", "closing", "sign-off", "ending")) { const j = niveauIn(); if (j >= 0) groet = V.groet[j]; }
  const zinnen = [kern, heeft("warm", "persoonlijk", "vriendelijk", "dank", "personal", "friendly", "thank") ? V.warm[vorm] : null,
    V.vraag[vorm][i]].filter(Boolean);
  let tekst = zinnen.join(" ");
  if (heeft("emoji")) tekst += " 🙂";
  const prof = S.ruw.professioneel || {};
  return { aanhef: V.aanhef[i], tekst, groet: (i <= 1 && prof.groet) ? prof.groet : groet, naam: prof.naam || V.naam };
}
const NIVEAUS = ["formeel", "zakelijk", "neutraal", "informeel", "luchtig"];
const NIVEAU_NAAM = { nl: ["Formeel", "Zakelijk", "Neutraal", "Informeel", "Luchtig"],
                      en: ["Formal", "Business", "Neutral", "Informal", "Light"] };
const FORMAAT_NAAM = { docx: "Word (.docx)", pdf: "PDF", md: "Markdown (.md)", txt: "Tekst (.txt)", html: "Webpagina (.html)" };

// ------------------------------------------------------------------ toestand
const S = {
  taal: (() => {
    if (START_TAAL === "nl" || START_TAAL === "en") return START_TAAL;
    try { return localStorage.getItem("dq-taal") || "nl"; } catch (e) { return "nl"; }
  })(),
  scherm: null, installatie: false, status: null, schema: null, ingebouwd: {}, standaard: {},
  ruw: {}, origineel: "{}", templates: [], stem: null, vakken: {}, installKeuze: { optie: "documenten", pad: "", taal: "nl" },
};
const T = (k, ...args) => {
  let s = (TEKST[S.taal] && TEKST[S.taal][k]) || TEKST.nl[k] || k;
  args.forEach((a) => { s = s.replace("%s", a); });
  return s;
};
const lab = (obj) => (obj && (obj[S.taal] || obj.nl)) || "";
const kopie = (o) => JSON.parse(JSON.stringify(o));

// ------------------------------------------------------------------ DOM-hulp
function el(tag, attrs, ...kinderen) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "tekst") n.textContent = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "klasse") n.className = v;
    else if (v === true) n.setAttribute(k, "");
    else n.setAttribute(k, v);
  }
  for (const k of kinderen.flat(Infinity)) {
    if (k === null || k === undefined || k === false) continue;
    n.append(k instanceof Node ? k : document.createTextNode(String(k)));
  }
  return n;
}
let idTeller = 0;
const nieuwId = () => `v${++idTeller}`;

const MELDING_ICOON = {
  succes: "M5 12.5l4.2 4.2L19 7",
  info: "M12 8h.01M11 12h1v5h1",
  letop: "M12 8v5M12 16.5h.01",
  fout: "M8 8l8 8M16 8l-8 8",
};
function melding(titel, tekst = "", soort = "info") {
  const houder = document.getElementById("meldingen");
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none"); svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2.2"); svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("aria-hidden", "true");
  const pad = document.createElementNS(NS, "path"); pad.setAttribute("d", MELDING_ICOON[soort] || MELDING_ICOON.info); svg.append(pad);
  const kaart = el("div", { klasse: `melding melding-${soort}`, role: soort === "fout" ? "alert" : "status" },
    el("span", { klasse: "melding-icoon" }, svg),
    el("div", { klasse: "melding-tekst" }, el("strong", { tekst: titel }), tekst ? el("p", { tekst }) : null),
    el("button", { type: "button", klasse: "melding-sluit", "aria-label": T("m_sluiten"), tekst: "×",
      onclick: () => weg() }));
  // Leestijd: minstens 7 seconden, langer bij meer tekst. Pauzeert zolang de muis erop staat.
  let resterend = Math.max(7000, (titel.length + tekst.length) * 75);
  let timer, gestart;
  kaart.style.setProperty("--duur", `${resterend}ms`);
  const weg = () => { clearTimeout(timer); kaart.classList.add("weg"); setTimeout(() => kaart.remove(), 250); };
  const start = () => { gestart = Date.now(); timer = setTimeout(weg, resterend); };
  kaart.addEventListener("mouseenter", () => { clearTimeout(timer); resterend -= Date.now() - gestart; });
  kaart.addEventListener("mouseleave", start);
  houder.prepend(kaart);
  while (houder.children.length > 3) houder.lastChild.remove();
  start();
}
const fout = (e) => melding(T("m_fout"), e.message || String(e), "fout");

function dialoog(titel, inhoud, knoppen) {
  const d = document.getElementById("dialoog");
  document.getElementById("dialoogtitel").textContent = titel;
  const i = document.getElementById("dialooginhoud");
  i.replaceChildren(...[inhoud].flat());
  const k = document.getElementById("dialoogknoppen");
  k.replaceChildren(...knoppen.map((b) => el("button", { type: b.type || "button", klasse: b.klasse || "tweede",
    value: b.waarde || "", tekst: b.tekst, onclick: b.actie ? (ev) => { ev.preventDefault(); b.actie(); } : null })));
  d.showModal();
  return d;
}
const sluitDialoog = () => document.getElementById("dialoog").close();

// ------------------------------------------------------------------ profielen
function profielStandaard() {
  const uit = {};
  const p = S.schema.$defs.profiel.properties;
  for (const sectie of ["controles", "toon", "uitvoer"]) {
    uit[sectie] = {};
    for (const [k, v] of Object.entries(p[sectie].properties)) uit[sectie][k] = kopie(v.default);
  }
  return uit;
}
function alleProfielen() { return { ...S.ingebouwd, ...(S.ruw.profielen || {}) }; }
function actiefNaam() { return S.ruw.profiel || S.standaard.profiel || "zakelijk"; }
function isIngebouwd(n) { return Object.prototype.hasOwnProperty.call(S.ingebouwd, n) && !(S.ruw.profielen || {})[n]; }
function effProfiel(naam) {
  const keten = [];
  const gezien = new Set();
  let n = naam;
  const alle = alleProfielen();
  while (n && alle[n] && !gezien.has(n)) { gezien.add(n); keten.unshift(alle[n]); n = alle[n].basis; }
  const uit = profielStandaard();
  for (const deel of keten) {
    for (const sectie of ["controles", "toon", "uitvoer"]) Object.assign(uit[sectie], kopie(deel[sectie] || {}));
    if (deel.taal) uit.taal = deel.taal;
  }
  return uit;
}
function bewerkbaar() {
  const actief = actiefNaam();
  if (!isIngebouwd(actief)) return S.ruw.profielen[actief];
  const naam = `${actief}-eigen`;
  S.ruw.profielen = S.ruw.profielen || {};
  if (!S.ruw.profielen[naam]) S.ruw.profielen[naam] = { basis: actief };
  S.ruw.profiel = naam;
  melding(T("m_eigen_titel"), T("eigen_kopie", naam, actief), "info");
  return S.ruw.profielen[naam];
}
function zetProfiel(sectie, sleutel, waarde) {
  const p = bewerkbaar();
  p[sectie] = p[sectie] || {};
  p[sectie][sleutel] = waarde;
  gewijzigd();
}

// ------------------------------------------------------------------ wijzigingen
function isLeeg(v) {
  if (v === undefined || v === null || v === "") return true;
  if (Array.isArray(v)) return v.length === 0;
  if (typeof v === "object") return Object.values(v).every(isLeeg);
  return false;
}
function telVerschillen(a, b) {
  if (JSON.stringify(a) === JSON.stringify(b) || (isLeeg(a) && isLeeg(b))) return 0;
  if (typeof a !== "object" || typeof b !== "object" || !a || !b || Array.isArray(a) || Array.isArray(b)) return 1;
  let n = 0;
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) n += telVerschillen(a[k], b[k]);
  return n;
}
function gewijzigd() {
  const n = telVerschillen(JSON.parse(S.origineel), S.ruw);
  const balk = document.getElementById("opslagbalk");
  balk.hidden = n === 0 || S.installatie;
  document.getElementById("opslagtekst").textContent = T("wijzigingen", n);
}
async function bekijkEnOpslaan(daarna) {
  const v = await api("POST", "/api/config/voorbeeld", { ruw: S.ruw });
  if (v.fouten.length) {
    dialoog(T("fouten_titel"), el("ul", {}, v.fouten.map((f) => el("li", { klasse: "fout", tekst: f }))),
      [{ tekst: T("sluiten"), actie: sluitDialoog }]);
    return false;
  }
  if (!v.samenvatting.length) { melding(T("m_geen_titel"), T("geen_wijzigingen"), "info"); if (daarna) daarna(); return true; }
  return new Promise((klaar) => {
    dialoog(T("voorbeeld_titel"), el("ul", {}, v.samenvatting.map((s) => el("li", { tekst: s }))), [
      { tekst: T("annuleren"), actie: () => { sluitDialoog(); klaar(false); } },
      { tekst: T("opslaan"), klasse: "eerste", actie: async () => {
        try {
          await api("POST", "/api/config/opslaan", { ruw: S.ruw });
          S.origineel = JSON.stringify(S.ruw);
          sluitDialoog(); melding(T("m_opgeslagen_titel"), T("m_opgeslagen_tekst"), "succes"); gewijzigd();
          if (daarna) daarna();
          klaar(true);
        } catch (e) { fout(e); }
      } },
    ]);
  });
}

// ------------------------------------------------------------------ laden
async function laadConfig() {
  const c = await api("GET", "/api/config");
  S.schema = c.schema; S.ingebouwd = c.ingebouwd; S.standaard = c.standaard;
  S.ruw = c.ruw || {}; S.origineel = JSON.stringify(S.ruw);
}
async function laadTemplates() { try { S.templates = (await api("GET", "/api/templates")).templates; } catch (e) { S.templates = []; } }

// ------------------------------------------------------------------ bouwstenen
function schakelaar(label, uitleg, aan, bij, voorbeeld) {
  const id = nieuwId();
  return el("div", { klasse: "schakelaar" },
    el("input", { type: "checkbox", role: "switch", id, checked: !!aan, onchange: (e) => bij(e.target.checked) }),
    el("div", {}, el("label", { for: id, tekst: label }),
      uitleg ? el("p", { klasse: "uitleg", tekst: uitleg }) : null,
      voorbeeld ? el("p", { klasse: "voorbeeld", tekst: voorbeeld }) : null));
}
function keuzeRij(naam, waarde, gekozen, titel, uitleg, bij, extra) {
  return el("label", { klasse: "keuze" },
    el("input", { type: "radio", name: naam, value: waarde, checked: gekozen, onchange: () => bij(waarde) }),
    el("strong", { tekst: titel }), uitleg ? el("span", { klasse: "uitleg", tekst: uitleg }) : null, extra || null);
}
function veld(label, invoer, uitleg) {
  const id = invoer.id || nieuwId();
  invoer.id = id;
  return el("div", { klasse: "veld" }, el("label", { for: id, tekst: label }),
    uitleg ? el("p", { klasse: "uitleg", tekst: uitleg }) : null, invoer);
}
function leesBestand(bestand) {
  return new Promise((ok, nee) => {
    const r = new FileReader();
    r.onload = () => ok(String(r.result).split(",")[1]);
    r.onerror = nee;
    r.readAsDataURL(bestand);
  });
}
const NS_SVG = "http://www.w3.org/2000/svg";
function lijnIcoon(d, dikte = 1.9) {
  const svg = document.createElementNS(NS_SVG, "svg");
  svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("fill", "none"); svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", String(dikte)); svg.setAttribute("stroke-linecap", "round"); svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  const pad = document.createElementNS(NS_SVG, "path"); pad.setAttribute("d", d); svg.append(pad);
  return svg;
}
const ICOON_UPLOAD = "M12 15V4M7.5 8.5L12 4l4.5 4.5M5 15v3.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V15";
function bestandKnop(label, accept, meerdere, bij, klasse = "tweede") {
  const id = nieuwId();
  const invoer = el("input", { type: "file", id, accept, multiple: meerdere, hidden: true,
    onchange: async (e) => { for (const f of e.target.files) await bij(f); e.target.value = ""; } });
  return el("span", {}, invoer, el("button", { type: "button", klasse: `${klasse} upload`, onclick: () => invoer.click() },
    lijnIcoon(ICOON_UPLOAD), el("span", { tekst: label })));
}
const FORMAAT_KLEUR = { docx: ["#185abd", "W"], pdf: ["#d9342b", "PDF"], md: ["#3d4a52", "MD"], txt: ["#6b7c83", "TXT"], html: ["#e44d26", "</>"] };
function formaatIcoon(f) {
  const [kleur, letters] = FORMAAT_KLEUR[f];
  const svg = document.createElementNS(NS_SVG, "svg");
  svg.setAttribute("viewBox", "0 0 32 32"); svg.setAttribute("aria-hidden", "true");
  const vel = document.createElementNS(NS_SVG, "path");
  vel.setAttribute("d", "M8 2.5h11.5L26 9v19a1.5 1.5 0 0 1-1.5 1.5h-16A1.5 1.5 0 0 1 7 28V4a1.5 1.5 0 0 1 1-1.5z");
  vel.setAttribute("fill", kleur);
  const hoek = document.createElementNS(NS_SVG, "path");
  hoek.setAttribute("d", "M19.5 2.5V9H26z"); hoek.setAttribute("fill", "#ffffff"); hoek.setAttribute("fill-opacity", ".35");
  const t = document.createElementNS(NS_SVG, "text");
  t.setAttribute("x", "16.5"); t.setAttribute("y", "22.5"); t.setAttribute("text-anchor", "middle"); t.setAttribute("fill", "#fff");
  t.setAttribute("font-size", letters.length > 2 ? "6.6" : "8.5"); t.setAttribute("font-weight", "700");
  t.setAttribute("font-family", "Geist, system-ui, sans-serif"); t.textContent = letters;
  svg.append(vel, hoek, t);
  return svg;
}
function sjabloonRij(sj) {
  const genres = S.schema.$defs.genre;
  const vak = el("textarea", { klasse: "sjabloon-tekst", spellcheck: "false", "aria-label": lab(genres["x-labels"][sj.genre]) }, sj.inhoud);
  const editor = el("div", { klasse: "sjabloon-editor", hidden: true }, vak,
    el("div", { klasse: "knoppen" },
      el("button", { type: "button", klasse: "eerste", tekst: T("opslaan_sjabloon"), onclick: () => bewaarSjabloon(sj.genre, vak.value) }),
      el("button", { type: "button", klasse: "tweede", tekst: T("annuleren"), onclick: () => { vak.value = sj.inhoud; editor.hidden = true; } })));
  return el("li", { klasse: "sjabloon" },
    el("div", { klasse: "sjabloon-rij" },
      el("span", {}, el("strong", { tekst: lab(genres["x-labels"][sj.genre]) }), " ",
        el("span", { klasse: sj.eigen ? "badge eigen" : "badge", tekst: T(sj.eigen ? "eigen_sjabloon" : "standaard") })),
      el("span", { klasse: "rij-knoppen" },
        el("button", { type: "button", klasse: "link", tekst: T("aanpassen"), onclick: () => { editor.hidden = !editor.hidden; if (!editor.hidden) vak.focus(); } }),
        bestandKnop(T("upload_sjabloon"), ".md,.txt", false, async (bestand) => bewaarSjabloon(sj.genre, await bestand.text()), "link"),
        sj.eigen ? el("button", { type: "button", klasse: "link", tekst: T("terug_standaard"), onclick: () => {
          dialoog(T("terug_standaard"), el("p", { tekst: T("herstel_vraag") }), [
            { tekst: T("annuleren"), actie: sluitDialoog },
            { tekst: T("terug_standaard"), klasse: "eerste", actie: async () => {
              sluitDialoog();
              try {
                await api("POST", "/api/sjablonen/herstel", { genre: sj.genre });
                S.sjablonen = (await api("GET", "/api/sjablonen")).sjablonen; toon();
                melding(T("m_herstel_titel"), T("m_herstel_tekst", lab(genres["x-labels"][sj.genre])), "succes");
              } catch (e) { fout(e); }
            } }]);
        } }) : null)),
    editor);
}
async function bewaarSjabloon(genre, inhoud) {
  try {
    await api("POST", "/api/sjablonen/opslaan", { genre, inhoud });
    S.sjablonen = (await api("GET", "/api/sjablonen")).sjablonen; toon();
    melding(T("m_sjabloon_titel"), T("m_sjabloon_tekst", lab(S.schema.$defs.genre["x-labels"][genre])), "succes");
  } catch (e) { fout(e); }
}
const GENRE_GROEPEN = { berichten: ["mail", "linkedin", "social", "kort"],
  documenten: ["rapport", "onderzoeksrapport", "adviesrapport", "zakelijk-rapport", "technisch-rapport", "sop", "research-notitie", "memo", "readme"] };
const ICOON_MAP = "M3.5 7.5A1.5 1.5 0 0 1 5 6h4.2l1.8 2H19a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 19 19H5a1.5 1.5 0 0 1-1.5-1.5z";
const ICOON_BESTAND = "M13.5 3.5H7A1.5 1.5 0 0 0 5.5 5v14A1.5 1.5 0 0 0 7 20.5h10a1.5 1.5 0 0 0 1.5-1.5V8.5zM13.5 3.5v5h5";
function mapBoom(mappen) {
  const m = { input: "1-input", output: "2-output", notities: "notities", rapporten: "rapporten", beeld: "beeld",
    bronnen: "bronnen", mijn_stijl: "mijn-stijl", schrijven: "schrijven", herschrijven: "herschrijven",
    reviewen: "reviewen", humaniseren: "humaniseren", templates: "templates", ...(mappen || {}) };
  if (!mappen && S.installKeuze.taal === "en") Object.assign(m, { notities: "notes", rapporten: "reports",
    beeld: "images", bronnen: "sources", mijn_stijl: "my-style", schrijven: "write", herschrijven: "rewrite",
    reviewen: "review", humaniseren: "humanize" });
  const rij = (sleutel, icoon = ICOON_MAP) => el("li", {}, lijnIcoon(icoon, 1.6),
    el("span", {}, el("strong", { tekst: m[sleutel] || sleutel }), el("span", { tekst: T(`mv_${sleutel}`) })));
  const kaart = (soort, naam, uitleg, sub) => el("section", { klasse: `mapkaart map-${soort}` },
    el("div", { klasse: "mapkaart-kop" }, lijnIcoon(ICOON_MAP, 1.8),
      el("span", {}, el("strong", { tekst: `${naam}/` }), el("span", { tekst: uitleg }))),
    el("ul", {}, sub.map((k) => rij(k))));
  return el("div", { klasse: "mapvis" },
    el("p", { klasse: "mapvis-kop" }, lijnIcoon(ICOON_MAP, 1.8), el("strong", { tekst: "DutchQuill/" }), el("span", { tekst: T("mv_werkmap") })),
    el("div", { klasse: "mapvis-stroom" },
      kaart("in", m.input, T("mv_in"), ["notities", "rapporten", "beeld", "bronnen", "mijn_stijl"]),
      el("div", { klasse: "mapvis-pijl" }, lijnIcoon("M5 12h14M13 6l6 6-6 6", 2), el("span", { tekst: T("mv_pijl") })),
      el("div", { klasse: "mapvis-uitkolom" },
        kaart("uit", m.output, T("mv_uit"), ["schrijven", "herschrijven", "reviewen", "humaniseren"]),
        el("p", { klasse: "mapvis-versies", tekst: T("mv_versies") }))),
    el("p", { klasse: "groepkop" }, el("strong", { tekst: T("mv_ook") })),
    el("ul", { klasse: "mapvis-extra" },
      el("li", {}, lijnIcoon(ICOON_BESTAND, 1.6), el("span", {}, el("strong", { tekst: "dutchquill.yaml" }), el("span", { tekst: T("mv_yaml") }))),
      el("li", {}, lijnIcoon(ICOON_MAP, 1.6), el("span", {}, el("strong", { tekst: `${m.templates}/` }), el("span", { tekst: T("mv_templates") }))),
      el("li", {}, lijnIcoon(ICOON_BESTAND, 1.6), el("span", {}, el("strong", { tekst: "eigen-regels.md" }), el("span", { tekst: T("mv_regels") })))));
}
function kop(titel, inleiding) {
  return [el("h1", { tekst: titel }), inleiding ? el("p", { klasse: "inleiding", tekst: inleiding }) : null];
}
function stapknoppen() {
  const lijst = schermen();
  const i = lijst.indexOf(S.scherm);
  return el("div", { klasse: "knoppen" },
    i > 0 ? el("button", { type: "button", klasse: "tweede", tekst: T("vorige"), onclick: () => ga(lijst[i - 1]) }) : null,
    i < lijst.length - 1 ? el("button", { type: "button", klasse: "eerste", tekst: T("volgende"),
      onclick: () => ga(lijst[i + 1]) }) : null);
}

// ------------------------------------------------------------------ schermen
const SCHERMEN = {
  welkom() {
    const acties = ["schrijven", "herschrijven", "reviewen", "humaniseren"];
    return el("section", { klasse: "welkom" },
      el("div", {},
        el("div", { klasse: "welkom-merk" }, el("img", { src: "icon.png", alt: "" })),
        el("h1", { tekst: T("welkom_titel") }),
        el("p", { klasse: "inleiding", tekst: `${T("welkom_1")} ${T("welkom_2")}` })),
      el("div", { klasse: "acties" }, acties.map((a) => el("div", {},
        el("strong", { tekst: T(`w_${a}`) }), el("span", { tekst: T(`w_${a}_u`) })))),
      el("div", { klasse: "welkom-voet" },
        el("button", { type: "button", klasse: "eerste groot", tekst: T("beginnen"), onclick: () => ga("werkmap") }),
        el("p", { tekst: `${T("w_duur")}. ${T("w_lokaal")}.` })));
  },

  werkmap() {
    if (S.status.ingesteld) {
      return [
        ...kop(T("huidige_map")),
        el("p", { klasse: "werkmap-pad" }, el("strong", { tekst: S.status.werkmap })),
        el("p", { klasse: "uitleg", tekst: T("map_verplaatsen") }),
        mapBoom((S.ruw || {}).mappen),
        el("h2", { tekst: T("taal_versies") }),
        veld(T("taal"), el("select", { onchange: (e) => { S.ruw.taal = e.target.value; gewijzigd(); } },
          ["nl", "en", "auto"].map((t) => el("option", { value: t, selected: (S.ruw.taal || "nl") === t, tekst: T(`taal_${t}`) })))),
        el("div", { klasse: "schakelaars" }, schakelaar(T("versies"), T("versies_uitleg"), S.ruw.versies !== false,
          (v) => { S.ruw.versies = v; gewijzigd(); })),
        S.installatie ? stapknoppen() : null,
      ];
    }
    const k = S.installKeuze;
    const padVak = el("input", { type: "text", value: k.pad, placeholder: "~/Documents/DutchQuill",
      oninput: (e) => { k.pad = e.target.value; k.optie = "zelf"; } });
    const opties = [
      ["bureaublad", T("bureaublad"), S.status.snelkeuzes.bureaublad],
      ["documenten", T("documenten"), S.status.snelkeuzes.documenten],
    ];
    const kiesKnop = el("button", { type: "button", klasse: "tweede", tekst: T("kies_map"), onclick: async () => {
      try {
        const r = await api("POST", "/api/kies-map");
        if (r.pad) { k.pad = `${r.pad}/DutchQuill`; k.optie = "zelf"; toon(); }
        else if (r.melding) melding(T("m_map_kiezen"), r.melding, "info");
      } catch (e) { fout(e); }
    } });
    return [
      ...kop(T("werkmap_titel"), T("werkmap_uitleg")),
      el("div", { klasse: "keuzes", role: "radiogroup" },
        opties.map(([w, t, p]) => keuzeRij("werkmap", w, k.optie === w, t, p, (v) => { k.optie = v; toon(); })),
        keuzeRij("werkmap", "zelf", k.optie === "zelf", T("zelf"), null, (v) => { k.optie = v; toon(); },
          el("span", { klasse: "uitleg" }, kiesKnop))),
      k.optie === "zelf" ? veld(T("of_typ"), padVak) : null,
      veld(T("taal"), el("select", { onchange: (e) => { k.taal = e.target.value; toon(); } },
        ["nl", "en", "auto"].map((t) => el("option", { value: t, selected: k.taal === t, tekst: T(`taal_${t}`) })))),
      el("p", { tekst: T("zo_ziet") }), mapBoom(),
      el("div", { klasse: "knoppen" },
        el("button", { type: "button", klasse: "tweede", tekst: T("vorige"), onclick: () => ga("welkom") }),
        el("button", { type: "button", klasse: "eerste", tekst: T("map_aanmaken"), onclick: async (e) => {
          const pad = k.optie === "zelf" ? k.pad : S.status.snelkeuzes[k.optie];
          e.target.disabled = true; e.target.textContent = T("bezig");
          try {
            await api("POST", "/api/werkmap", { pad, taal: k.taal, profiel: "zakelijk", languagetool: false });
            S.status = await api("GET", "/api/status");
            await laadConfig(); await laadTemplates();
            melding(T("m_map_titel"), T("map_gemaakt"), "succes");
            ga("profiel");
          } catch (err) { fout(err); e.target.disabled = false; e.target.textContent = T("map_aanmaken"); }
        } })),
    ];
  },

  profiel() {
    const actief = actiefNaam();
    const eigen = S.ruw.profielen || {};
    const kies = (n) => { S.ruw.profiel = n; gewijzigd(); toon(); };
    const rijen = Object.entries(S.ingebouwd).map(([n, p]) =>
      keuzeRij("profiel", n, actief === n, n, p.beschrijving, kies));
    const eigenRijen = Object.entries(eigen).map(([n, p]) => keuzeRij("profiel", n, actief === n, n,
      `${p.beschrijving || ""} (${T("bouwt_op_kort")} ${p.basis || "zakelijk"})`.trim(), kies,
      el("span", { klasse: "uitleg" }, el("button", { type: "button", klasse: "link", tekst: T("verwijderen"),
        onclick: (ev) => {
          ev.preventDefault();
          const basis = eigen[n].basis || "zakelijk";
          delete eigen[n];
          if (S.ruw.profiel === n) S.ruw.profiel = basis;
          for (const [g, p2] of Object.entries(S.ruw.genre_profielen || {})) if (p2 === n) delete S.ruw.genre_profielen[g];
          gewijzigd(); toon();
        } }))));
    const naamVak = el("input", { type: "text", placeholder: "mijn-linkedin" });
    const basisVak = el("select", {}, Object.keys(alleProfielen()).map((n) => el("option", { value: n, tekst: n, selected: n === actief })));
    const beschrVak = el("input", { type: "text" });
    const fout = el("p", { klasse: "fout", role: "alert" });
    const nieuw = el("details", {}, el("summary", { tekst: T("nieuw_profiel") }),
      el("div", { klasse: "kader" }, veld(T("naam"), naamVak, T("naam_regel")), veld(T("bouwt_op"), basisVak),
        veld(T("beschrijving"), beschrVak), fout,
        el("button", { type: "button", klasse: "eerste", tekst: T("maken"), onclick: () => {
          const n = naamVak.value.trim();
          if (!/^[a-z0-9][a-z0-9-]{1,40}$/.test(n)) { fout.textContent = T("naam_regel"); return; }
          if (alleProfielen()[n]) { fout.textContent = T("naam_bestaat"); return; }
          S.ruw.profielen = S.ruw.profielen || {};
          S.ruw.profielen[n] = { basis: basisVak.value, ...(beschrVak.value ? { beschrijving: beschrVak.value } : {}) };
          S.ruw.profiel = n; gewijzigd(); toon();
          melding(T("m_profiel_titel"), T("m_profiel_tekst", n), "succes");
        } })));
    const genres = S.schema.$defs.genre;
    const gp = S.ruw.genre_profielen || {};
    const genreTabel = el("details", {}, el("summary", { tekst: T("genre_titel") }),
      el("p", { klasse: "uitleg", tekst: T("genre_uitleg") }),
      el("table", { klasse: "cijfers" }, genres.enum.map((g) => el("tr", {},
        el("td", { tekst: lab(genres["x-labels"][g]) }),
        el("td", {}, el("select", { "aria-label": lab(genres["x-labels"][g]), onchange: (e) => {
          S.ruw.genre_profielen = S.ruw.genre_profielen || {};
          if (e.target.value) S.ruw.genre_profielen[g] = e.target.value; else delete S.ruw.genre_profielen[g];
          if (!Object.keys(S.ruw.genre_profielen).length) delete S.ruw.genre_profielen;
          gewijzigd();
        } }, el("option", { value: "", tekst: T("volgt_actief") }),
          Object.keys(alleProfielen()).map((n) => el("option", { value: n, tekst: n, selected: gp[g] === n }))))))));
    return [
      ...kop(T("profiel_titel"), T("profiel_uitleg")),
      el("div", { klasse: "keuzes", role: "radiogroup" }, rijen),
      Object.keys(eigen).length ? [el("h2", { tekst: T("eigen_profielen") }),
        el("div", { klasse: "keuzes", role: "radiogroup" }, eigenRijen)] : null,
      S.installatie ? null : [nieuw, genreTabel],
      S.installatie ? stapknoppen() : null,
    ];
  },

  controles() {
    const p = effProfiel(actiefNaam());
    const props = S.schema.$defs.profiel.properties.controles.properties;
    return [
      ...kop(T("controles_titel"), T("controles_uitleg")),
      el("p", { klasse: "label-klein", tekst: T("actief_profiel", actiefNaam()) }),
      el("div", { klasse: "schakelaars" }, Object.entries(props).map(([k, d]) => schakelaar(lab(d["x-label"]),
        lab(d["x-uitleg"]), p.controles[k], (v) => { zetProfiel("controles", k, v); }, T(`vb_${k}`)))),
    ];
  },

  toon() {
    const p = effProfiel(actiefNaam());
    let i = Math.max(0, NIVEAUS.indexOf(p.toon.niveau));
    let aan = p.toon.aanspreekvorm || "auto";
    let mix = p.toon.mix || "";
    const aanhef = el("p", { klasse: "aanhef" });
    const brief = el("p", { klasse: "brief" });
    const slot = el("p", { klasse: "slot" });
    const mixNoot = el("p", { klasse: "label-klein mixnoot", tekst: T("voorbeeld_mix") });
    const teken = (anim) => {
      const v = voorbeeldMail(i, aan, mix);
      aanhef.textContent = v.aanhef; brief.textContent = v.tekst;
      slot.replaceChildren(v.groet, el("br"), v.naam);
      mixNoot.hidden = !mix.trim();
      if (anim) { brief.classList.remove("wissel"); void brief.offsetWidth; brief.classList.add("wissel"); }
    };
    const stappen = el("div", { klasse: "toonstappen", "aria-hidden": "true" },
      NIVEAU_NAAM[S.taal].map((n, j) => el("span", { klasse: j === i ? "actief" : "", tekst: n })));
    const schuif = el("input", { type: "range", min: 0, max: 4, step: 1, value: i, "aria-label": T("toon_titel"),
      "aria-valuetext": NIVEAU_NAAM[S.taal][i], oninput: (e) => {
        i = Number(e.target.value); teken(true);
        e.target.setAttribute("aria-valuetext", NIVEAU_NAAM[S.taal][i]);
        [...stappen.children].forEach((s, j) => { s.className = j === i ? "actief" : ""; });
      }, onchange: (e) => zetProfiel("toon", "niveau", NIVEAUS[Number(e.target.value)]) });
    teken(false);
    return [
      ...kop(T("toon_titel"), T("toon_uitleg")),
      el("p", { klasse: "label-klein", tekst: T("actief_profiel", actiefNaam()) }),
      el("div", { klasse: "toon" }, el("div", { klasse: "toonschaal" }, schuif, stappen)),
      el("div", { klasse: "veld" }, el("span", { klasse: "label", tekst: T("aanspreekvorm") }),
        el("div", { klasse: "vinkjes", role: "radiogroup" }, ["auto", "je", "u", "geen"].map((w) => el("label", {},
          el("input", { type: "radio", name: "aan", value: w, checked: aan === w,
            onchange: () => { aan = w; teken(true); zetProfiel("toon", "aanspreekvorm", w); } }), T(`aan_${w}`))))),
      veld(T("mix"), el("textarea", { oninput: (e) => { mix = e.target.value; teken(false); },
        onchange: (e) => zetProfiel("toon", "mix", e.target.value) }, p.toon.mix || ""), T("mix_uitleg")),
      el("h2", { tekst: T("voorbeeld_kop") }),
      el("div", { klasse: "papiertje" },
        el("p", { klasse: "aan", tekst: T("vb_aan") }), aanhef, brief, slot), mixNoot,
    ];
  },

  uitvoer() {
    const p = effProfiel(actiefNaam());
    const genres = S.schema.$defs.genre;
    const zetLijst = (sleutel, waarde, aan) => {
      const nu = new Set(effProfiel(actiefNaam()).uitvoer[sleutel]);
      if (aan) nu.add(waarde); else nu.delete(waarde);
      if (sleutel === "formaten" && nu.size === 0) { melding(T("m_formaat_titel"), T("m_formaat_tekst"), "letop"); toon(); return; }
      zetProfiel("uitvoer", sleutel, [...nu]);
    };
    const formaten = el("div", { klasse: "formaten" }, Object.entries(FORMAAT_NAAM).map(([f, n]) =>
      el("label", { klasse: `formaat formaat-${f}` },
        el("input", { type: "checkbox", checked: p.uitvoer.formaten.includes(f),
          onchange: (e) => zetLijst("formaten", f, e.target.checked) }),
        formaatIcoon(f), el("span", { klasse: "formaat-tekst" }, el("strong", { tekst: n }), el("span", { tekst: T(`f_${f}`) })),
        el("span", { klasse: "vink", "aria-hidden": "true" }, lijnIcoon("M5 12.5l4.2 4.2L19 7", 2.6)))));
    const groep = (naam) => el("div", { klasse: "genregroep" },
      el("p", { klasse: "groepkop" }, el("strong", { tekst: T(naam) }), el("span", { tekst: T(`${naam}_uitleg`) })),
      el("div", { klasse: "vinkjes raster-vinkjes" }, GENRE_GROEPEN[naam].filter((g) => genres.enum.includes(g)).map((g) =>
        el("label", {}, el("input", { type: "checkbox", checked: p.uitvoer.chat_voor.includes(g),
          onchange: (e) => zetLijst("chat_voor", g, e.target.checked) }), lab(genres["x-labels"][g])))));
    return [
      ...kop(T("uitvoer_titel")),
      el("p", { klasse: "label-klein", tekst: T("actief_profiel", actiefNaam()) }),
      el("h2", { tekst: T("formaten") }), formaten,
      el("h2", { tekst: T("chat_voor") }), el("p", { klasse: "uitleg", tekst: T("chat_voor_uitleg") }),
      groep("berichten"), groep("documenten"),
      veld(T("template"), el("select", { onchange: (e) => zetProfiel("uitvoer", "template", e.target.value) },
        S.templates.map((t) => el("option", { value: t.naam, selected: t.naam === p.uitvoer.template,
          tekst: `${t.naam} (${T(t.soort === "eigen" ? "eigen" : "meegeleverd")})` })))),
    ];
  },

  templates() {
    const uitkomst = el("div", { "aria-live": "polite" });
    const toonCheck = (c) => {
      const delen = [];
      if (c.bruikbaar && !Object.keys(c.voorstel_mapping).length) delen.push(el("p", { tekst: T("check_ok") }));
      else if (c.bruikbaar) {
        delen.push(el("p", { tekst: T("check_mapping") }),
          el("ul", {}, Object.entries(c.voorstel_mapping).map(([k, v]) => el("li", { tekst: `${k}: ${v}` }))));
        S.ruw.stijlen = { ...(S.ruw.stijlen || {}), ...c.voorstel_mapping }; gewijzigd();
      } else delen.push(el("p", { klasse: "fout", tekst: T("check_mist") }));
      uitkomst.replaceChildren(el("div", { klasse: "kader" }, delen));
    };
    const lijst = el("ul", { klasse: "lijst" }, S.templates.map((t) => el("li", {},
      el("span", {}, el("strong", { tekst: t.naam }), " ",
        el("span", { klasse: "label-klein", tekst: `${T(t.soort === "eigen" ? "eigen" : "meegeleverd")}${t.naam === effProfiel(actiefNaam()).uitvoer.template ? `, ${T("actief")}` : ""}` })),
      el("span", {},
        el("button", { type: "button", klasse: "link", tekst: T("controleer"), onclick: async () => {
          try { toonCheck(await api("POST", "/api/templates/check", { naam: t.naam })); } catch (e) { fout(e); }
        } }), " ",
        el("button", { type: "button", klasse: "link", tekst: T("maak_standaard"), onclick: () => {
          zetProfiel("uitvoer", "template", t.naam); toon();
        } })))));
    const fonts = ["Calibri", "Arial", "Aptos", "Georgia", "Garamond", "Times New Roman", "Verdana", "Helvetica"];
    const f = {
      van: el("select", {}, S.templates.map((t) => el("option", { value: t.naam, tekst: t.naam }))),
      naar: el("input", { type: "text", placeholder: "mijn-huisstijl" }),
      kopFont: el("select", {}, fonts.map((x) => el("option", { tekst: x }))),
      kopGrootte: el("input", { type: "number", value: 16, min: 10, max: 36 }),
      kopKleur: el("input", { type: "color", value: "#1f4e5f" }),
      tekstFont: el("select", {}, fonts.map((x) => el("option", { tekst: x }))),
      tekstGrootte: el("input", { type: "number", value: 11, min: 8, max: 16, step: 0.5 }),
      regel: el("select", {}, ["1.0", "1.15", "1.5", "2.0"].map((x) => el("option", { tekst: x, selected: x === "1.15" }))),
      marge: el("input", { type: "number", value: 2.5, min: 1, max: 4, step: 0.25 }),
    };
    const aanpasFout = el("p", { klasse: "fout", role: "alert" });
    return [
      ...kop(T("templates_titel"), T("templates_uitleg")),
      lijst, uitkomst,
      el("div", { klasse: "knoppen" }, bestandKnop(T("upload_template"), ".docx", false, async (bestand) => {
        try {
          const r = await api("POST", "/api/templates/upload", { bestandsnaam: bestand.name, data: await leesBestand(bestand) });
          await laadConfig(); await laadTemplates(); toon();
          if (r.check.bruikbaar) melding(T("m_template_titel"), `${r.naam}: ${T("check_ok")}`, "succes");
          else melding(T("m_template_titel"), T("m_template_mist"), "letop");
        } catch (e) { fout(e); }
      })),
      el("h2", { tekst: T("aanpassen_titel") }), el("p", { klasse: "uitleg", tekst: T("aanpassen_uitleg") }),
      el("div", { klasse: "kader" },
        el("div", { klasse: "raster raster-4 vast" },
          el("div", { klasse: "breed" }, veld(T("van"), f.van)), el("div", { klasse: "breed" }, veld(T("nieuwe_naam"), f.naar)),
          veld(T("kop_font"), f.kopFont), veld(T("kop_grootte"), f.kopGrootte), veld(T("kop_kleur"), f.kopKleur), el("div"),
          veld(T("tekst_font"), f.tekstFont), veld(T("tekst_grootte"), f.tekstGrootte),
          veld(T("regelafstand"), f.regel), veld(T("marge"), f.marge)), aanpasFout,
        el("button", { type: "button", klasse: "eerste", tekst: T("kopie_maken"), onclick: async () => {
          const naar = f.naar.value.trim();
          if (!/^[a-z0-9][a-z0-9-]{1,40}$/.test(naar)) { aanpasFout.textContent = T("naam_regel"); return; }
          const kleur = f.kopKleur.value.replace("#", "").toUpperCase();
          const stijlen = ["kop1", "kop2", "kop3"].flatMap((k) => [`${k}.font=${f.kopFont.value}`, `${k}.kleur=${kleur}`])
            .concat([`kop1.grootte=${f.kopGrootte.value}`, `normaal.font=${f.tekstFont.value}`,
              `normaal.grootte=${f.tekstGrootte.value}`, `normaal.regelafstand=${f.regel.value}`]);
          try {
            await api("POST", "/api/templates/aanpas", { van: f.van.value, naar, stijlen, marge: Number(f.marge.value) });
            await laadConfig(); await laadTemplates();
            zetProfiel("uitvoer", "template", naar); toon();
            melding(T("m_aanpas_titel"), T("m_aanpas_tekst", naar), "succes");
          } catch (e) { aanpasFout.textContent = e.message; }
        } })),
      el("h2", { tekst: T("sjablonen_titel") }), el("p", { klasse: "uitleg", tekst: T("sjablonen_uitleg") }),
      ["berichten", "documenten"].map((groepNaam) => [
        el("p", { klasse: "groepkop" }, el("strong", { tekst: T(groepNaam) })),
        el("ul", { klasse: "lijst sjablonen" }, GENRE_GROEPEN[groepNaam].map((g) => (S.sjablonen || []).find((x) => x.genre === g))
          .filter(Boolean).map(sjabloonRij)),
      ]),
    ];
  },

  professioneel() {
    const pr = () => S.ruw.professioneel || {};
    const zet = (k, v) => {
      const nieuw = { ...pr() };
      if (v) nieuw[k] = v; else delete nieuw[k];
      if (Object.keys(nieuw).length) S.ruw.professioneel = nieuw; else delete S.ruw.professioneel;
      gewijzigd();
    };
    const props = S.schema.properties.professioneel.properties;
    const vb = el("div", { klasse: "papiertje handtekening-vb" });
    const teken = () => {
      const x = pr();
      const regels = [x.functie, [x.organisatie, x.afdeling].filter(Boolean).join(", "), x.telefoon, x.email, x.website, x.linkedin]
        .filter(Boolean);
      vb.replaceChildren(...[
        el("p", { klasse: "brief", tekst: S.taal === "nl" ? "…en dan hoor ik graag of vrijdag past." : "…so let me know if Friday works." }),
        el("p", { klasse: "slot" }, x.groet || lab(props.groet.default ? { nl: props.groet.default, en: "Kind regards," } : null)),
        el("p", { klasse: "sig-naam", tekst: x.naam || "Sam Jansen" }),
        regels.length ? el("p", { klasse: "sig-regels" }, regels.flatMap((r, j) => j ? [el("br"), r] : [r])) : null,
        (S.profVb || {}).handtekening ? el("img", { src: S.profVb.handtekening, alt: T("handtekening"), klasse: "sig-afb" }) : null,
        (S.profVb || {}).banner ? el("img", { src: S.profVb.banner, alt: T("banner"), klasse: "sig-banner" }) : null].filter(Boolean));
    };
    teken();
    const tekstveld = (k) => veld(lab(props[k]["x-label"]), el("input", { type: k === "email" ? "email" : "text",
      value: pr()[k] || (k === "groet" ? "" : ""), placeholder: k === "groet" ? props.groet.default : null,
      oninput: (e) => { zet(k, e.target.value.trim()); teken(); } }), props[k]["x-uitleg"] ? lab(props[k]["x-uitleg"]) : null);
    const afbKaart = (soort) => el("div", { klasse: "afbkaart" },
      el("div", { klasse: "afbkaart-voorbeeld" }, (S.profVb || {})[soort]
        ? el("img", { src: S.profVb[soort], alt: T(soort) }) : el("span", { klasse: "uitleg", tekst: T("geen_bestand") })),
      el("div", { klasse: "knoppen" },
        bestandKnop(T(`upload_${soort}`), ".png,.jpg,.jpeg,.gif,.webp", false, async (bestand) => {
          try {
            const r = await api("POST", "/api/professioneel/upload", { soort, bestandsnaam: bestand.name, data: await leesBestand(bestand) });
            S.profVb = { ...(S.profVb || {}), [soort]: r.voorbeeld }; zet(soort, r.pad); toon();
            melding(T("m_upload_titel"), T("m_upload_tekst", T(soort)), "succes");
          } catch (e) { fout(e); }
        }),
        pr()[soort] ? el("button", { type: "button", klasse: "link", tekst: T("verwijderen"), onclick: () => {
          zet(soort, ""); if (S.profVb) delete S.profVb[soort]; toon();
        } }) : null));
    return [
      ...kop(T("prof_titel"), T("prof_uitleg")),
      el("div", { klasse: "raster raster-4" }, ["naam", "functie", "organisatie", "afdeling", "telefoon", "email", "website", "linkedin"].map(tekstveld),
        el("div", { klasse: "breed" }, tekstveld("groet"))),
      el("h2", { tekst: T("prof_afb") }), el("p", { klasse: "uitleg", tekst: T("prof_afb_uitleg") }),
      el("div", { klasse: "afbkaarten" }, afbKaart("handtekening"), afbKaart("banner")),
      el("h2", { tekst: T("prof_voorbeeld") }), vb,
    ];
  },

  stem() {
    const s = S.stem || { bestanden: [], profiel: null };
    const p = s.profiel;
    const cijfers = p ? el("table", { klasse: "cijfers" }, [
      [T("st_woorden"), p.woorden], [T("st_zinslengte"), `${p.gem_zinslengte} ± ${p.stdev_zinslengte}`],
      [T("st_kort"), `${p.korte_zinnen_pct}%`], [T("st_streepjes"), p.streepjes_per_1000],
      [T("st_dubbelepunt"), p.dubbelepunt_per_1000], [T("st_begin"), (p.top_zinsbegin || []).slice(0, 4).join(", ")],
      [T("st_jeu"), `${p.je_u.je} / ${p.je_u.u}`],
    ].map(([a, b]) => el("tr", {}, el("td", { tekst: a }), el("td", { tekst: b })))) : null;
    return [
      ...kop(T("stem_titel"), T("stem_uitleg")),
      el("div", { klasse: "schakelaars" }, schakelaar(T("stem_gebruiken"), null, (S.ruw.stem || {}).gebruiken !== false,
        (v) => { S.ruw.stem = { ...(S.ruw.stem || {}), gebruiken: v }; gewijzigd(); })),
      el("h2", { tekst: T("stem_bestanden") }),
      s.bestanden.length ? el("ul", { klasse: "lijst" }, s.bestanden.map((b) => el("li", { tekst: b })))
        : el("p", { klasse: "uitleg", tekst: T("stem_leeg") }),
      el("div", { klasse: "knoppen" },
        bestandKnop(T("stem_toevoegen"), ".md,.txt,.docx,.pdf", true, async (bestand) => {
          try {
            await api("POST", "/api/stem/upload", { bestandsnaam: bestand.name, data: await leesBestand(bestand) });
            melding(T("m_stem_titel"), T("m_stem_tekst", bestand.name), "succes");
          } catch (e) { fout(e); }
          S.stem = await api("GET", "/api/stem"); toon();
        }),
        el("button", { type: "button", klasse: "eerste", tekst: T("stem_meten"), disabled: !s.bestanden.length,
          onclick: async () => {
            try {
              await api("POST", "/api/stem/analyse"); S.stem = await api("GET", "/api/stem"); toon();
              melding(T("m_gemeten_titel"), T("m_gemeten_tekst"), "succes");
            }
            catch (e) { fout(e); }
          } })),
      cijfers,
    ];
  },

  privacy() {
    const pr = S.ruw.privacy || {};
    const zet = (k, v) => { S.ruw.privacy = { ...(S.ruw.privacy || {}), [k]: v }; gewijzigd(); };
    const props = S.schema.properties.privacy.properties;
    const hist = S.schema.properties.historie.properties.tekst_bewaren;
    const hs = S.ruw.historie || {};
    return [
      ...kop(T("privacy_titel"), T("privacy_uitleg")),
      el("div", { klasse: "schakelaars" }, schakelaar(lab(props.languagetool["x-label"]),
        lab(props.languagetool["x-uitleg"]), pr.languagetool, (v) => zet("languagetool", v), T("lt_extra")),
        schakelaar(lab(hist["x-label"]), lab(hist["x-uitleg"]), hs.tekst_bewaren !== false, (v) => {
          S.ruw.historie = { ...(S.ruw.historie || {}), tekst_bewaren: v }; gewijzigd(); })),
      S.installatie ? stapknoppen() : null,
    ];
  },

  student() {
    const st = () => S.ruw.student || {};
    const zetSt = (k, v) => {
      const nieuw = { ...st() };
      if (v === undefined || v === "" || (Array.isArray(v) && !v.length)) delete nieuw[k]; else nieuw[k] = v;
      if (Object.keys(nieuw).length) S.ruw.student = nieuw; else delete S.ruw.student;
      gewijzigd();
    };
    const tekstveld = (k, label) => veld(label, el("input", { type: "text", value: st()[k] || "",
      oninput: (e) => zetSt(k, e.target.value.trim()) }));
    const vakken = st().vakken || [];
    const nivSchema = S.schema.properties.student.properties.niveau;
    const vakNaam = el("input", { type: "text" });
    const vakCode = el("input", { type: "text", placeholder: "SYS" });
    const vakkenLijst = vakken.length ? el("ul", { klasse: "lijst" }, vakken.map((v, i) => el("li", {},
      el("span", { tekst: `${v.naam || ""} (${v.code || ""})` }),
      el("button", { type: "button", klasse: "link", tekst: T("verwijderen"), onclick: () => {
        zetSt("vakken", vakken.filter((_, j) => j !== i)); toon();
      } })))) : null;
    const bestaand = S.vakken || {};
    const upload = (code, soort) => bestandKnop(soort === "quick-scan" ? T("inlevereisen") : T("rubric"),
      ".md,.txt,.docx,.pdf", false, async (bestand) => {
        try {
          await api("POST", "/api/vakken/upload", { vakcode: code, soort, bestandsnaam: bestand.name,
            data: await leesBestand(bestand) });
          S.vakken = (await api("GET", "/api/vakken")).vakken; toon();
          melding(T("m_vak_titel"), T("m_vak_tekst", bestand.name, code), "succes");
        } catch (e) { fout(e); }
      });
    return [
      ...kop(T("student_titel"), T("student_uitleg")),
      el("div", { klasse: "raster raster-4" },
      tekstveld("voornaam", S.taal === "nl" ? "Voornaam" : "First name"),
      tekstveld("tussenvoegsel", S.taal === "nl" ? "Tussenvoegsel" : "Prefix (van, de)"),
      tekstveld("achternaam", S.taal === "nl" ? "Achternaam" : "Last name"),
      tekstveld("studentnummer", S.taal === "nl" ? "Studentnummer" : "Student number"),
      tekstveld("instelling", S.taal === "nl" ? "Hogeschool of universiteit" : "University"),
      tekstveld("faculteit", S.taal === "nl" ? "Faculteit of instituut" : "Faculty"),
      tekstveld("opleiding", S.taal === "nl" ? "Opleiding" : "Programme"),
      veld(lab(nivSchema["x-label"]), el("select", { onchange: (e) => zetSt("niveau", e.target.value) },
        nivSchema.enum.map((n) => el("option", { value: n, tekst: lab(nivSchema["x-labels"][n]),
          selected: n === (st().niveau || nivSchema.default) }))), lab(nivSchema["x-uitleg"]))),
      el("h2", { tekst: T("vakken") }), vakkenLijst,
      el("div", { klasse: "kader rij-invoer" }, veld(T("vak"), vakNaam), veld(T("code"), vakCode),
        el("button", { type: "button", klasse: "tweede", tekst: T("toevoegen"), onclick: () => {
          if (!vakNaam.value && !vakCode.value) return;
          zetSt("vakken", [...vakken, { naam: vakNaam.value.trim(), code: vakCode.value.trim().toUpperCase() }]); toon();
        } })),
      el("h2", { tekst: T("vak_bestanden") }), el("p", { klasse: "uitleg", tekst: T("vak_uitleg") }),
      vakken.some((v) => v.code) ? null : el("p", { klasse: "label-klein", tekst: T("vak_eerst") }),
      vakken.filter((v) => v.code).map((v) => el("div", { klasse: "veld" },
        el("span", { klasse: "label", tekst: `${v.naam || v.code} (${v.code})` }),
        el("p", { klasse: "uitleg", tekst: (bestaand[v.code] || []).join(", ") }),
        el("div", { klasse: "knoppen" }, upload(v.code, "quick-scan"), upload(v.code, "beoordelingscriteria")))),
    ];
  },

  onderhoud() {
    const bw = S.ruw.bijwerken || {};
    const opdracht = "/dutchquill:bijwerken";
    const uitkomst = el("div", { "aria-live": "polite" });
    return [
      ...kop(T("onderhoud_titel")),
      el("h2", { tekst: T("gidsen_kop") }),
      el("p", { tekst: T("gidsen_stand", S.status.gidsen_gecontroleerd) }),
      el("p", { klasse: "uitleg", tekst: T("bijwerken_uitleg") }),
      el("div", { klasse: "knoppen" }, el("button", { type: "button", klasse: "eerste", tekst: T("nu_controleren"),
        onclick: async (e) => {
          const knop = e.target; knop.disabled = true;
          uitkomst.replaceChildren(el("p", { klasse: "uitleg", tekst: T("controleren_bezig") }));
          try {
            const r = await api("POST", "/api/bronnen/check");
            const delen = [];
            if (r.gewijzigd.length) delen.push(el("p", { tekst: T("controle_gewijzigd") }),
              el("ul", {}, r.gewijzigd.map((g) => el("li", { tekst: `${g.gidsen.join(", ")}: ${g.reden}` }))));
            if (r.fouten.length) delen.push(el("p", { tekst: T("controle_fouten") }),
              el("ul", {}, r.fouten.map((f) => el("li", { klasse: "fout", tekst: f }))));
            if (r.gemarkeerd) { delen.push(el("p", { tekst: T("controle_ok") })); S.status.gidsen_gecontroleerd = r.gecontroleerd_op; }
            uitkomst.replaceChildren(el("div", { klasse: "kader controle-uitkomst" }, delen));
          } catch (err) { uitkomst.replaceChildren(el("p", { klasse: "fout", tekst: err.message })); }
          knop.disabled = false;
        } })),
      uitkomst,
      el("p", { klasse: "label-klein los", tekst: T("of_in_claude") }),
      el("div", { klasse: "knoppen" }, el("code", { klasse: "boom", tekst: opdracht }),
        el("button", { type: "button", klasse: "tweede", tekst: T("kopieer"), onclick: async () => {
          try { await navigator.clipboard.writeText(opdracht); melding(T("m_gekopieerd_titel"), T("gekopieerd"), "succes"); }
          catch (e) { melding(T("m_info"), opdracht, "info"); }
        } })),
      veld(T("herinnering"), el("input", { type: "number", min: 7, max: 365, value: bw.herinnering_dagen || 30,
        onchange: (e) => { S.ruw.bijwerken = { ...bw, herinnering_dagen: Number(e.target.value) }; gewijzigd(); } })),
      el("h2", { tekst: T("weergave") }),
      el("div", { klasse: "schakelaars" }, schakelaar(T("wolken"), T("wolken_uitleg"), !document.body.classList.contains("wolken-stil"),
        (v) => { document.body.classList.toggle("wolken-stil", !v); try { localStorage.setItem("dq-wolken", v ? "aan" : "uit"); } catch (e) { /* */ } })),
      el("div", { klasse: "knoppen knoppen-eind" }, el("button", { type: "button", klasse: "eerste", tekst: T("klaar_sluiten"), onclick: klaar })),
    ];
  },

  over() {
    const NS = "http://www.w3.org/2000/svg";
    const icoon = (soort) => {
      const svg = document.createElementNS(NS, "svg");
      svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true");
      const pad = document.createElementNS(NS, "path");
      if (soort === "globe") {
        svg.setAttribute("fill", "none"); svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "1.7");
        pad.setAttribute("d", "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3.5 9h17M3.5 15h17M12 3c2.5 2.6 3.7 5.6 3.7 9s-1.2 6.4-3.7 9c-2.5-2.6-3.7-5.6-3.7-9S9.5 5.6 12 3z");
      } else if (soort === "pijl") {
        svg.setAttribute("fill", "none"); svg.setAttribute("stroke", "currentColor"); svg.setAttribute("stroke-width", "1.8");
        svg.setAttribute("stroke-linecap", "round"); pad.setAttribute("d", "M8 16L16 8M9 8h7v7");
      } else {
        svg.setAttribute("fill", "currentColor");
        pad.setAttribute("d", soort === "github"
          ? "M12 .3a12 12 0 0 0-3.8 23.38c.6.12.83-.26.83-.57L9 21.07c-3.34.72-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.08-.74.09-.73.09-.73 1.2.09 1.83 1.24 1.83 1.24 1.07 1.83 2.81 1.3 3.5 1 .1-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.14-.3-.54-1.52.1-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6 0C17.3 4.97 18.3 5.3 18.3 5.3c.65 1.65.24 2.87.12 3.17.77.84 1.23 1.91 1.23 3.22 0 4.61-2.8 5.62-5.48 5.92.43.37.82 1.1.82 2.22l-.01 3.29c0 .32.21.69.82.57A12 12 0 0 0 12 .3"
          : "M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z");
      }
      svg.append(pad); return svg;
    };
    const links = [
      ["l_repo", "https://github.com/nickyjacobs/DutchQuill-AI", "github", "github"],
      ["l_github", "https://github.com/nickyjacobs", "github", "github"],
      ["l_site", "https://nickyjacobs.nl", "globe", "website"],
      ["l_linkedin", "https://www.linkedin.com/in/N-O-Jacobs", "linkedin", "linkedin"],
    ];
    return [
      el("div", { klasse: "over-kop" }, el("h1", { tekst: T("over_titel") }),
        el("p", { klasse: "versie", tekst: `${T("versie")} ${S.status.versie}` })),
      el("div", { klasse: "over-raster" },
        el("section", { klasse: "verhaal" }, el("h2", { tekst: T("kop_verhaal") }),
          [1, 2, 3, 4, 5].map((n) => el("p", { tekst: T(`over_${n}`) })),
          el("p", { klasse: "ondertekening", tekst: T("over_naam") })),
        el("aside", { klasse: "over-zij" },
          el("h2", { tekst: T("kop_formules") }), el("p", { klasse: "uitleg", tekst: T("formules_intro") }),
          el("dl", { klasse: "formules" }, [1, 2, 3].map((n) => [el("dt", { tekst: T(`f${n}_naam`) }), el("dd", { tekst: T(`f${n}`) })])),
          el("h2", { tekst: T("kop_socials") }),
          el("ul", { klasse: "merklinks" }, links.map(([k, url, ic, merk]) => el("li", {},
            el("a", { href: url, target: "_blank", rel: "noopener noreferrer", klasse: `merk-${merk}` },
              icoon(ic), el("span", { tekst: T(k) }), icoon("pijl"))))))),
    ];
  },

  afronden() {
    return [
      ...kop(T("afronden_titel"), T("afronden_uitleg")),
      el("div", { klasse: "kader" }, el("p", {}, el("strong", { tekst: `${T("s_werkmap")}: ` }), S.status.werkmap || ""),
        el("p", {}, el("strong", { tekst: `${T("s_profiel")}: ` }), actiefNaam()),
        el("p", {}, el("strong", { tekst: `${T("s_privacy")}: ` }),
          (S.ruw.privacy || {}).languagetool ? "LanguageTool" : (S.taal === "nl" ? "alles lokaal" : "everything local"))),
      el("div", { klasse: "knoppen" },
        el("button", { type: "button", klasse: "tweede", tekst: T("vorige"), onclick: () => ga("privacy") }),
        el("button", { type: "button", klasse: "tweede", tekst: T("verder_instellen"), onclick: async () => {
          const ok = await bekijkEnOpslaan();
          if (ok !== false) { S.installatie = false; ga("controles"); }
        } }),
        el("button", { type: "button", klasse: "eerste", tekst: T("opslaan_klaar"), onclick: async () => {
          const ok = await bekijkEnOpslaan(klaar);
          if (ok === false) return;
        } })),
    ];
  },
};

// ------------------------------------------------------------------ navigatie
const GROEPEN = [
  { kop: "g_start", schermen: ["werkmap", "profiel"] },
  { kop: "g_schrijven", schermen: ["toon", "controles", "stem"] },
  { kop: "g_uitvoer", schermen: ["uitvoer", "templates"] },
  { kop: "g_jij", schermen: ["privacy", "student", "professioneel"] },
  { kop: "g_systeem", schermen: ["onderhoud", "over"] },
];
function schermen() {
  return S.installatie ? ["welkom", "werkmap", "profiel", "privacy", "afronden"]
    : GROEPEN.flatMap((g) => g.schermen);
}
function navKnop(s, i, lijst) {
  return el("li", {}, el("button", { type: "button", "aria-current": s === S.scherm ? (S.installatie ? "step" : "page") : null,
    "data-klaar": S.installatie && lijst.indexOf(S.scherm) > i ? "ja" : null,
    disabled: S.installatie && !S.status.ingesteld && i > 1 ? true : null, onclick: () => ga(s) },
    S.installatie ? el("span", { klasse: "nr", tekst: String(i + 1) }) : null, el("span", { tekst: T(`s_${s}`) })));
}
function tekenNav() {
  const nav = document.getElementById("nav");
  if (S.installatie) {
    const lijst = schermen();
    nav.replaceChildren(el("p", { klasse: "nav-kop", tekst: T("installatie") }),
      el("ol", {}, lijst.map((s, i) => navKnop(s, i, lijst))));
    return;
  }
  nav.replaceChildren(...GROEPEN.flatMap((g) => [el("p", { klasse: "nav-kop", tekst: T(g.kop) }),
    el("ul", {}, g.schermen.map((s) => navKnop(s, 0, [])))]));
}
async function ga(scherm) {
  S.scherm = scherm;
  if (scherm === "stem" && !S.stem) { try { S.stem = await api("GET", "/api/stem"); } catch (e) { S.stem = null; } }
  if (scherm === "templates" && !S.sjablonen) { try { S.sjablonen = (await api("GET", "/api/sjablonen")).sjablonen; } catch (e) { S.sjablonen = []; } }
  if (scherm === "professioneel" && !S.profVb) { try { S.profVb = (await api("GET", "/api/professioneel")).voorbeeld; } catch (e) { S.profVb = {}; } }
  if (scherm === "student") { try { S.vakken = (await api("GET", "/api/vakken")).vakken; } catch (e) { S.vakken = {}; } }
  toon();
  document.getElementById("inhoud").focus({ preventScroll: true });
  window.scrollTo(0, 0);
}
function toon() {
  tekenNav();
  const scherm = document.getElementById("scherm");
  scherm.replaceChildren(...[SCHERMEN[S.scherm]()].flat(3).filter(Boolean));
  gewijzigd();
}
async function klaar() {
  if (telVerschillen(JSON.parse(S.origineel), S.ruw) && !S.installatie) {
    dialoog(T("onopgeslagen"), [], [
      { tekst: T("annuleren"), actie: sluitDialoog },
      { tekst: T("toch_sluiten"), klasse: "eerste", actie: () => { sluitDialoog(); sluit(); } },
    ]);
    return;
  }
  sluit();
}
async function sluit() {
  try { await api("POST", "/api/klaar"); } catch (e) { /* server is misschien al weg */ }
  document.getElementById("opslagbalk").hidden = true;
  document.getElementById("nav").replaceChildren();
  document.getElementById("scherm").replaceChildren(...kop(T("gesloten_titel"), T("gesloten_uitleg")));
  // Een tabblad dat de browser zelf opende, met één pagina in de geschiedenis, mag het script sluiten.
  setTimeout(() => { window.close(); }, 600);
}

// ------------------------------------------------------------------ thema en taal
function zetThema(t) {
  if (t === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t;
  try { localStorage.setItem("dq-thema", t); } catch (e) { /* geen opslag */ }
  document.querySelectorAll("#themakeuze button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.thema === t)));
}
function vertaalVast() {
  document.documentElement.lang = S.taal;
  document.querySelectorAll("[data-t]").forEach((n) => { n.textContent = T(n.dataset.t); });
  document.querySelectorAll("#taalkeuze button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.taal === S.taal)));
  const namen = { light: T("thema_licht_l"), auto: T("thema_auto_l"), dark: T("thema_donker_l") };
  document.querySelectorAll("#themakeuze button").forEach((b) => {
    b.setAttribute("aria-label", namen[b.dataset.thema]); b.title = namen[b.dataset.thema];
  });
}

// ------------------------------------------------------------------ start
// De wolken lopen op de klok: bij opnieuw openen staan ze waar ze waren, in plaats van opnieuw te beginnen.
function wolkenOpDeKlok() {
  const nu = Date.now() / 1000;
  document.querySelectorAll(".wolk").forEach((w) => {
    const duur = parseFloat(getComputedStyle(w).animationDuration) || 150;
    w.style.animationDelay = `-${(nu % duur).toFixed(1)}s`;
  });
}

function zetMenu(open) {
  document.body.classList.toggle("ingeklapt", !open);
  document.getElementById("menuopen").hidden = open;
  document.getElementById("menudicht").setAttribute("aria-expanded", String(open));
  document.getElementById("menuopen").setAttribute("aria-expanded", String(open));
  try { localStorage.setItem("dq-menu", open ? "open" : "dicht"); } catch (e) { /* */ }
}

async function start() {
  wolkenOpDeKlok();
  try { if (localStorage.getItem("dq-wolken") === "uit") document.body.classList.add("wolken-stil"); } catch (e) { /* */ }
  let menu = "open";
  try { menu = localStorage.getItem("dq-menu") || "open"; } catch (e) { /* */ }
  zetMenu((START_MENU || menu) !== "dicht");
  document.getElementById("menudicht").addEventListener("click", () => { zetMenu(false); document.getElementById("menuopen").focus(); });
  document.getElementById("menuopen").addEventListener("click", () => { zetMenu(true); document.getElementById("menudicht").focus(); });
  let thema = "auto";
  try { thema = localStorage.getItem("dq-thema") || "auto"; } catch (e) { /* */ }
  zetThema(thema);
  document.querySelectorAll("#themakeuze button").forEach((b) => b.addEventListener("click", () => zetThema(b.dataset.thema)));
  document.querySelectorAll("#taalkeuze button").forEach((b) => b.addEventListener("click", () => {
    S.taal = b.dataset.taal;
    try { localStorage.setItem("dq-taal", S.taal); } catch (e) { /* */ }
    vertaalVast(); if (S.status) toon();
  }));
  document.getElementById("terugdraaien").addEventListener("click", () => { S.ruw = JSON.parse(S.origineel); toon(); gewijzigd(); });
  document.getElementById("bekijk").addEventListener("click", () => bekijkEnOpslaan());
  vertaalVast();
  if (!TOKEN) {
    document.getElementById("scherm").replaceChildren(el("p", { klasse: "let-op", tekst: T("geen_token") }));
    return;
  }
  try {
    S.status = await api("GET", "/api/status");
    await laadConfig();
    await laadTemplates();
  } catch (e) {
    document.getElementById("scherm").replaceChildren(el("p", { klasse: "let-op", tekst: e.message }));
    return;
  }
  S.installatie = !S.status.ingesteld;
  S.installKeuze.taal = S.taal === "en" ? "en" : "nl";
  const gevraagd = START_SCHERM && schermen().includes(START_SCHERM) ? START_SCHERM : null;
  ga(gevraagd || (S.installatie ? "welkom" : "profiel"));
}
start();
