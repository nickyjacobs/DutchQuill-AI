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
    terugdraaien: "Terugdraaien", bekijkopslaan: "Bekijken en opslaan", opslaan: "Opslaan", annuleren: "Annuleren",
    sluiten: "Sluiten", volgende: "Volgende", vorige: "Vorige", beginnen: "Beginnen",
    fout_algemeen: "Er ging iets mis. Probeer het opnieuw.",
    geen_token: "Deze pagina hoort bij een Studio-sessie. Open de Studio opnieuw via /dutchquill:instellen.",
    installatie: "Installatie", instellingen: "Instellingen",
    s_welkom: "Welkom", s_werkmap: "Werkmap", s_profiel: "Profiel", s_controles: "Controles", s_toon: "Toon",
    s_uitvoer: "Uitvoer", s_templates: "Templates", s_stem: "Mijn stem", s_privacy: "Privacy",
    s_student: "Student", s_onderhoud: "Onderhoud", s_afronden: "Afronden",
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
    bureaublad: "Op het bureaublad", documenten: "In Documenten", zelf: "Zelf kiezen",
    kies_map: "Kies een map", of_typ: "Of typ het pad", taal: "Taal van je teksten",
    taal_nl: "Nederlands", taal_en: "Engels", taal_auto: "Automatisch (volgt je materiaal)",
    map_aanmaken: "Map aanmaken", map_gemaakt: "Je werkmap staat klaar.",
    zo_ziet: "Zo ziet de map eruit:", huidige_map: "Je werkmap",
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
    eigen_kopie: "%s is meegeleverd en blijft zoals het is. Je wijzigingen staan in je eigen profiel %s.",
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
    bijwerken_uitleg: "Eén keer per maand herinnert DutchQuill je eraan om ze te laten nakijken. Typ dan in Claude:",
    kopieer: "Kopieer", gekopieerd: "Gekopieerd.", herinnering: "Herinnering na (dagen)",
    versie: "Versie", klaar_sluiten: "Klaar en Studio sluiten",
    afronden_titel: "Klaar om op te slaan",
    afronden_uitleg: "Dit wordt je startinstelling. Je kunt alles later aanpassen, hier of in een gesprek.",
    verder_instellen: "Opslaan en verder instellen", opslaan_klaar: "Opslaan en klaar",
    wijzigingen: "%s wijziging(en) nog niet opgeslagen.", opgeslagen: "Opgeslagen.",
    voorbeeld_titel: "Dit verandert er", geen_wijzigingen: "Er is niets veranderd.",
    fouten_titel: "Zo kan het niet worden opgeslagen",
    onopgeslagen: "Je hebt nog wijzigingen die niet zijn opgeslagen. Toch sluiten?",
    toch_sluiten: "Toch sluiten",
    gesloten_titel: "De Studio is gesloten",
    gesloten_uitleg: "Je kunt dit tabblad sluiten. Claude ziet wat er veranderd is.",
    bezig: "Bezig...",
  },
  en: {
    studio: "Studio",
    terugdraaien: "Undo changes", bekijkopslaan: "Review and save", opslaan: "Save", annuleren: "Cancel",
    sluiten: "Close", volgende: "Next", vorige: "Back", beginnen: "Get started",
    fout_algemeen: "Something went wrong. Try again.",
    geen_token: "This page belongs to a Studio session. Open the Studio again with /dutchquill:instellen.",
    installatie: "Setup", instellingen: "Settings",
    s_welkom: "Welcome", s_werkmap: "Workspace", s_profiel: "Profile", s_controles: "Checks", s_toon: "Tone",
    s_uitvoer: "Output", s_templates: "Templates", s_stem: "My voice", s_privacy: "Privacy",
    s_student: "Student", s_onderhoud: "Maintenance", s_afronden: "Finish",
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
    bureaublad: "On the desktop", documenten: "In Documents", zelf: "Choose myself",
    kies_map: "Choose a folder", of_typ: "Or type the path", taal: "Language of your texts",
    taal_nl: "Dutch", taal_en: "English", taal_auto: "Automatic (follows your material)",
    map_aanmaken: "Create folder", map_gemaakt: "Your workspace is ready.",
    zo_ziet: "This is what it looks like:", huidige_map: "Your workspace",
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
    eigen_kopie: "%s is built in and stays as it is. Your changes are in your own profile %s.",
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
    bijwerken_uitleg: "Once a month DutchQuill reminds you to have them checked. Then type in Claude:",
    kopieer: "Copy", gekopieerd: "Copied.", herinnering: "Reminder after (days)",
    versie: "Version", klaar_sluiten: "Done, close the Studio",
    afronden_titel: "Ready to save",
    afronden_uitleg: "This becomes your starting setup. You can change everything later, here or in a conversation.",
    verder_instellen: "Save and keep going", opslaan_klaar: "Save and finish",
    wijzigingen: "%s unsaved change(s).", opgeslagen: "Saved.",
    voorbeeld_titel: "What will change", geen_wijzigingen: "Nothing changed.",
    fouten_titel: "This can't be saved yet",
    onopgeslagen: "You have unsaved changes. Close anyway?",
    toch_sluiten: "Close anyway",
    gesloten_titel: "The Studio is closed",
    gesloten_uitleg: "You can close this tab. Claude can see what changed.",
    bezig: "Working...",
  },
};

const VOORBEELD = {
  nl: [
    "Het overleg van donderdag 28 november is verplaatst naar vrijdag 29 november om 10.00 uur. Wij verzoeken u te bevestigen of dit tijdstip u schikt.",
    "We verplaatsen het overleg van donderdag naar vrijdag 29 november, 10.00 uur. Kunt u laten weten of dat past?",
    "Het overleg schuift van donderdag naar vrijdag 29 november, 10.00 uur. Past dat voor je?",
    "Het overleg van donderdag wordt vrijdag, om tien uur. Lukt dat bij jou?",
    "Donderdag wordt vrijdag: zelfde overleg, tien uur, verse koffie. Ben je erbij?",
  ],
  en: [
    "The meeting of Thursday 28 November has been moved to Friday 29 November at 10:00. Please confirm whether this time suits you.",
    "We are moving Thursday's meeting to Friday 29 November, 10:00. Could you let me know if that works?",
    "The meeting moves from Thursday to Friday 29 November, 10:00. Does that work for you?",
    "Thursday's meeting is now on Friday at ten. Can you make it?",
    "Thursday became Friday: same meeting, ten o'clock, fresh coffee. You in?",
  ],
};
const NIVEAUS = ["formeel", "zakelijk", "neutraal", "informeel", "luchtig"];
const NIVEAU_NAAM = { nl: ["Formeel", "Zakelijk", "Neutraal", "Informeel", "Luchtig"],
                      en: ["Formal", "Business", "Neutral", "Informal", "Light"] };
const FORMAAT_NAAM = { docx: "Word (.docx)", pdf: "PDF", md: "Markdown (.md)", txt: "Tekst (.txt)", html: "Webpagina (.html)" };

// ------------------------------------------------------------------ toestand
const S = {
  taal: (() => { try { return localStorage.getItem("dq-taal") || "nl"; } catch (e) { return "nl"; } })(),
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
  for (const k of kinderen.flat()) {
    if (k === null || k === undefined || k === false) continue;
    n.append(k instanceof Node ? k : document.createTextNode(String(k)));
  }
  return n;
}
let idTeller = 0;
const nieuwId = () => `v${++idTeller}`;

function melding(tekst) {
  const m = document.getElementById("melding");
  m.textContent = tekst;
  m.hidden = false;
  clearTimeout(melding.t);
  melding.t = setTimeout(() => { m.hidden = true; }, 3500);
}

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
  melding(T("eigen_kopie", actief, naam));
  return S.ruw.profielen[naam];
}
function zetProfiel(sectie, sleutel, waarde) {
  const p = bewerkbaar();
  p[sectie] = p[sectie] || {};
  p[sectie][sleutel] = waarde;
  gewijzigd();
}

// ------------------------------------------------------------------ wijzigingen
function telVerschillen(a, b) {
  if (JSON.stringify(a) === JSON.stringify(b)) return 0;
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
  if (!v.samenvatting.length) { melding(T("geen_wijzigingen")); if (daarna) daarna(); return true; }
  return new Promise((klaar) => {
    dialoog(T("voorbeeld_titel"), el("ul", {}, v.samenvatting.map((s) => el("li", { tekst: s }))), [
      { tekst: T("annuleren"), actie: () => { sluitDialoog(); klaar(false); } },
      { tekst: T("opslaan"), klasse: "eerste", actie: async () => {
        try {
          await api("POST", "/api/config/opslaan", { ruw: S.ruw });
          S.origineel = JSON.stringify(S.ruw);
          sluitDialoog(); melding(T("opgeslagen")); gewijzigd();
          if (daarna) daarna();
          klaar(true);
        } catch (e) { melding(e.message); }
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
function bestandKnop(label, accept, meerdere, bij) {
  const id = nieuwId();
  const invoer = el("input", { type: "file", id, accept, multiple: meerdere, hidden: true,
    onchange: async (e) => { for (const f of e.target.files) await bij(f); e.target.value = ""; } });
  return el("span", {}, invoer, el("button", { type: "button", klasse: "tweede", tekst: label,
    onclick: () => invoer.click() }));
}
function mapBoom(mappen) {
  const m = { input: "1-input", output: "2-output", notities: "notities", rapporten: "rapporten", beeld: "beeld",
    bronnen: "bronnen", mijn_stijl: "mijn-stijl", schrijven: "schrijven", herschrijven: "herschrijven",
    reviewen: "reviewen", humaniseren: "humaniseren", templates: "templates", ...(mappen || {}) };
  if (!mappen && S.installKeuze.taal === "en") Object.assign(m, { notities: "notes", rapporten: "reports",
    beeld: "images", bronnen: "sources", mijn_stijl: "my-style", schrijven: "write", herschrijven: "rewrite",
    reviewen: "review", humaniseren: "humanize" });
  return el("div", { klasse: "boom", tekst:
`DutchQuill/
  dutchquill.yaml
  ${m.input}/
    ${m.notities}/   ${m.rapporten}/   ${m.beeld}/   ${m.bronnen}/   ${m.mijn_stijl}/
  ${m.output}/
    ${m.schrijven}/   ${m.herschrijven}/   ${m.reviewen}/   ${m.humaniseren}/
  ${m.templates}/
  eigen-regels.md` });
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
        el("p", {}, el("strong", { tekst: S.status.werkmap })),
        mapBoom((S.ruw || {}).mappen),
        el("p", { klasse: "uitleg", tekst: T("map_verplaatsen") }),
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
        else if (r.melding) melding(r.melding);
      } catch (e) { melding(e.message); }
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
            melding(T("map_gemaakt"));
            ga("profiel");
          } catch (err) { melding(err.message); e.target.disabled = false; e.target.textContent = T("map_aanmaken"); }
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
    const brief = el("p", { klasse: "brief", tekst: VOORBEELD[S.taal][i] });
    const stappen = el("div", { klasse: "toonstappen", "aria-hidden": "true" },
      NIVEAU_NAAM[S.taal].map((n, j) => el("span", { klasse: j === i ? "actief" : "", tekst: n })));
    const schuif = el("input", { type: "range", min: 0, max: 4, step: 1, value: i, "aria-label": T("toon_titel"),
      "aria-valuetext": NIVEAU_NAAM[S.taal][i], oninput: (e) => {
        i = Number(e.target.value);
        brief.classList.remove("wissel"); void brief.offsetWidth; brief.classList.add("wissel");
        brief.textContent = VOORBEELD[S.taal][i];
        e.target.setAttribute("aria-valuetext", NIVEAU_NAAM[S.taal][i]);
        [...stappen.children].forEach((s, j) => { s.className = j === i ? "actief" : ""; });
      }, onchange: (e) => zetProfiel("toon", "niveau", NIVEAUS[Number(e.target.value)]) });
    const aan = p.toon.aanspreekvorm;
    return [
      ...kop(T("toon_titel"), T("toon_uitleg")),
      el("p", { klasse: "label-klein", tekst: T("actief_profiel", actiefNaam()) }),
      el("div", { klasse: "toon" }, el("div", { klasse: "toonschaal" }, schuif, stappen),
        el("div", { klasse: "papiertje" },
          el("p", { klasse: "aan", tekst: S.taal === "nl" ? "Aan: het projectteam" : "To: the project team" }), brief)),
      el("div", { klasse: "veld" }, el("span", { klasse: "label", tekst: T("aanspreekvorm") }),
        el("div", { klasse: "vinkjes", role: "radiogroup" }, ["auto", "je", "u", "geen"].map((w) => el("label", {},
          el("input", { type: "radio", name: "aan", value: w, checked: aan === w,
            onchange: () => zetProfiel("toon", "aanspreekvorm", w) }), T(`aan_${w}`))))),
      veld(T("mix"), el("textarea", { onchange: (e) => zetProfiel("toon", "mix", e.target.value) }, p.toon.mix || ""),
        T("mix_uitleg")),
    ];
  },

  uitvoer() {
    const p = effProfiel(actiefNaam());
    const genres = S.schema.$defs.genre;
    const zetLijst = (sleutel, waarde, aan) => {
      const nu = new Set(effProfiel(actiefNaam()).uitvoer[sleutel]);
      if (aan) nu.add(waarde); else nu.delete(waarde);
      if (sleutel === "formaten" && nu.size === 0) { melding("Kies minstens één formaat."); toon(); return; }
      zetProfiel("uitvoer", sleutel, [...nu]);
    };
    return [
      ...kop(T("uitvoer_titel")),
      el("p", { klasse: "label-klein", tekst: T("actief_profiel", actiefNaam()) }),
      el("div", { klasse: "veld" }, el("span", { klasse: "label", tekst: T("formaten") }),
        el("div", { klasse: "vinkjes" }, Object.entries(FORMAAT_NAAM).map(([f, n]) => el("label", {},
          el("input", { type: "checkbox", checked: p.uitvoer.formaten.includes(f),
            onchange: (e) => zetLijst("formaten", f, e.target.checked) }), n)))),
      el("div", { klasse: "veld" }, el("span", { klasse: "label", tekst: T("chat_voor") }),
        el("p", { klasse: "uitleg", tekst: T("chat_voor_uitleg") }),
        el("div", { klasse: "vinkjes" }, genres.enum.map((g) => el("label", {},
          el("input", { type: "checkbox", checked: p.uitvoer.chat_voor.includes(g),
            onchange: (e) => zetLijst("chat_voor", g, e.target.checked) }), lab(genres["x-labels"][g]))))),
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
          try { toonCheck(await api("POST", "/api/templates/check", { naam: t.naam })); } catch (e) { melding(e.message); }
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
          melding(`${r.naam}: ${r.check.bruikbaar ? T("check_ok") : T("check_mist")}`);
        } catch (e) { melding(e.message); }
      })),
      el("h2", { tekst: T("aanpassen_titel") }), el("p", { klasse: "uitleg", tekst: T("aanpassen_uitleg") }),
      el("div", { klasse: "kader" },
        el("div", { klasse: "raster" }, veld(T("van"), f.van), veld(T("nieuwe_naam"), f.naar, T("naam_regel"))),
        el("div", { klasse: "raster" }, veld(T("kop_font"), f.kopFont), veld(T("kop_grootte"), f.kopGrootte),
          veld(T("kop_kleur"), f.kopKleur)),
        el("div", { klasse: "raster" }, veld(T("tekst_font"), f.tekstFont), veld(T("tekst_grootte"), f.tekstGrootte),
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
          } catch (e) { aanpasFout.textContent = e.message; }
        } })),
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
          try { await api("POST", "/api/stem/upload", { bestandsnaam: bestand.name, data: await leesBestand(bestand) }); }
          catch (e) { melding(e.message); }
          S.stem = await api("GET", "/api/stem"); toon();
        }),
        el("button", { type: "button", klasse: "eerste", tekst: T("stem_meten"), disabled: !s.bestanden.length,
          onclick: async () => {
            try { await api("POST", "/api/stem/analyse"); S.stem = await api("GET", "/api/stem"); toon(); }
            catch (e) { melding(e.message); }
          } })),
      cijfers,
    ];
  },

  privacy() {
    const pr = S.ruw.privacy || {};
    const zet = (k, v) => { S.ruw.privacy = { ...(S.ruw.privacy || {}), [k]: v }; gewijzigd(); };
    const props = S.schema.properties.privacy.properties;
    return [
      ...kop(T("privacy_titel"), T("privacy_uitleg")),
      el("div", { klasse: "schakelaars" }, schakelaar(lab(props.languagetool["x-label"]),
        lab(props.languagetool["x-uitleg"]), pr.languagetool, (v) => zet("languagetool", v), T("lt_extra"))),
      S.installatie ? stapknoppen() : null,
    ];
  },

  student() {
    const st = S.ruw.student = S.ruw.student || {};
    const tekstveld = (k, label) => veld(label, el("input", { type: "text", value: st[k] || "",
      onchange: (e) => { if (e.target.value) st[k] = e.target.value; else delete st[k]; gewijzigd(); } }));
    const vakken = st.vakken = st.vakken || [];
    const vakNaam = el("input", { type: "text" });
    const vakCode = el("input", { type: "text", placeholder: "SYS" });
    const vakkenLijst = el("ul", { klasse: "lijst" }, vakken.map((v, i) => el("li", {},
      el("span", { tekst: `${v.naam || ""} (${v.code || ""})` }),
      el("button", { type: "button", klasse: "link", tekst: T("verwijderen"), onclick: () => {
        vakken.splice(i, 1); gewijzigd(); toon();
      } }))));
    const bestaand = S.vakken || {};
    const upload = (code, soort) => bestandKnop(soort === "quick-scan" ? T("inlevereisen") : T("rubric"),
      ".md,.txt,.docx,.pdf", false, async (bestand) => {
        try {
          await api("POST", "/api/vakken/upload", { vakcode: code, soort, bestandsnaam: bestand.name,
            data: await leesBestand(bestand) });
          S.vakken = (await api("GET", "/api/vakken")).vakken; toon(); melding(T("opgeslagen"));
        } catch (e) { melding(e.message); }
      });
    return [
      ...kop(T("student_titel"), T("student_uitleg")),
      tekstveld("voornaam", S.taal === "nl" ? "Voornaam" : "First name"),
      tekstveld("tussenvoegsel", S.taal === "nl" ? "Tussenvoegsel" : "Prefix (van, de)"),
      tekstveld("achternaam", S.taal === "nl" ? "Achternaam" : "Last name"),
      tekstveld("studentnummer", S.taal === "nl" ? "Studentnummer" : "Student number"),
      tekstveld("instelling", S.taal === "nl" ? "Hogeschool of universiteit" : "University"),
      tekstveld("faculteit", S.taal === "nl" ? "Faculteit of instituut" : "Faculty"),
      tekstveld("opleiding", S.taal === "nl" ? "Opleiding" : "Programme"),
      el("h2", { tekst: T("vakken") }), vakkenLijst,
      el("div", { klasse: "kader" }, veld(T("vak"), vakNaam), veld(T("code"), vakCode),
        el("button", { type: "button", klasse: "tweede", tekst: T("toevoegen"), onclick: () => {
          if (!vakNaam.value && !vakCode.value) return;
          vakken.push({ naam: vakNaam.value, code: vakCode.value.toUpperCase() }); gewijzigd(); toon();
        } })),
      el("h2", { tekst: T("vak_bestanden") }), el("p", { klasse: "uitleg", tekst: T("vak_uitleg") }),
      vakken.filter((v) => v.code).map((v) => el("div", { klasse: "veld" },
        el("span", { klasse: "label", tekst: `${v.naam || v.code} (${v.code})` }),
        el("p", { klasse: "uitleg", tekst: (bestaand[v.code] || []).join(", ") }),
        el("div", { klasse: "knoppen" }, upload(v.code, "quick-scan"), upload(v.code, "beoordelingscriteria")))),
    ];
  },

  onderhoud() {
    const bw = S.ruw.bijwerken || {};
    const opdracht = "/dutchquill:bijwerken";
    return [
      ...kop(T("onderhoud_titel")),
      el("p", { tekst: T("gidsen_stand", S.status.gidsen_gecontroleerd) }),
      el("p", { tekst: T("bijwerken_uitleg") }),
      el("div", { klasse: "knoppen" }, el("code", { klasse: "boom", tekst: opdracht }),
        el("button", { type: "button", klasse: "tweede", tekst: T("kopieer"), onclick: async () => {
          try { await navigator.clipboard.writeText(opdracht); melding(T("gekopieerd")); } catch (e) { melding(opdracht); }
        } })),
      veld(T("herinnering"), el("input", { type: "number", min: 7, max: 365, value: bw.herinnering_dagen || 30,
        onchange: (e) => { S.ruw.bijwerken = { ...bw, herinnering_dagen: Number(e.target.value) }; gewijzigd(); } })),
      el("p", { klasse: "label-klein", tekst: `${T("versie")} ${S.status.versie} | ${S.status.werkmap || ""}` }),
      el("div", { klasse: "knoppen" }, el("button", { type: "button", klasse: "eerste", tekst: T("klaar_sluiten"), onclick: klaar })),
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
function schermen() {
  return S.installatie ? ["welkom", "werkmap", "profiel", "privacy", "afronden"]
    : ["werkmap", "profiel", "controles", "toon", "uitvoer", "templates", "stem", "privacy", "student", "onderhoud"];
}
function tekenNav() {
  const lijst = schermen();
  const nav = document.getElementById("nav");
  const kopTekst = el("p", { klasse: "nav-kop", tekst: S.installatie ? T("installatie") : T("instellingen") });
  const houder = el(S.installatie ? "ol" : "ul", {}, lijst.map((s, i) => el("li", {},
    el("button", { type: "button", "aria-current": s === S.scherm ? (S.installatie ? "step" : "page") : null,
      "data-klaar": S.installatie && lijst.indexOf(S.scherm) > i ? "ja" : null,
      disabled: S.installatie && !S.status.ingesteld && i > 1 ? true : null,
      onclick: () => ga(s) },
      S.installatie ? el("span", { klasse: "nr", tekst: String(i + 1) }) : null, el("span", { tekst: T(`s_${s}`) })))));
  nav.replaceChildren(kopTekst, houder);
}
async function ga(scherm) {
  S.scherm = scherm;
  if (scherm === "stem" && !S.stem) { try { S.stem = await api("GET", "/api/stem"); } catch (e) { S.stem = null; } }
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
async function start() {
  let thema = "auto";
  try { thema = localStorage.getItem("dq-thema") || "auto"; } catch (e) { /* */ }
  zetThema(thema);
  document.querySelectorAll("#themakeuze button").forEach((b) => b.addEventListener("click", () => zetThema(b.dataset.thema)));
  document.querySelectorAll("#taalkeuze button").forEach((b) => b.addEventListener("click", () => {
    S.taal = b.dataset.taal;
    try { localStorage.setItem("dq-taal", S.taal); } catch (e) { /* */ }
    vertaalVast(); if (S.status) toon();
  }));
  document.getElementById("terugdraaien").addEventListener("click", () => { S.ruw = JSON.parse(S.origineel); toon(); });
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
