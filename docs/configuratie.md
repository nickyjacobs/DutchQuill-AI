# Configuratie

## Gebruikersprofiel

In `config/user_profile.json` staan je persoonlijke gegevens. Die worden automatisch ingevuld bij het aanmaken van APA-titelpagina's en document-metadata. Het profiel is niet verplicht, maar scheelt je tijd.

### Instellen

```bash
cp config/user_profile.example.json config/user_profile.json
```

Open `config/user_profile.json` en vul je gegevens in.

### Velden

| Veld | Type | Voorbeeld | Gebruik |
|------|------|-----------|---------|
| `voornaam` | string | `"Jan"` | Titelpagina, auteursnaam |
| `tussenvoegsel` | string | `"van"` | Titelpagina (optioneel) |
| `achternaam` | string | `"Dijk"` | Titelpagina, auteursnaam |
| `studentnummer` | string | `"900123456"` | Titelpagina |
| `instelling` | string | `"Hogeschool Amsterdam"` | Titelpagina |
| `faculteit` | string | `"Faculteit Techniek"` | Titelpagina |
| `opleiding` | string | `"Software Engineering"` | Titelpagina |
| `docenten` | array | Zie onder | Titelpagina (begeleider) |
| `vakken` | array | Zie onder | Titelpagina (vaknaam + code) |

### Docenten

```json
"docenten": [
  {
    "naam": "Dr. P. de Vries",
    "rol": "begeleider",
    "vak": "Afstuderen"
  },
  {
    "naam": "Dhr. A. Jansen",
    "rol": "tweede lezer",
    "vak": "Onderzoeksmethoden"
  }
]
```

### Vakken

```json
"vakken": [
  {
    "naam": "Onderzoeksmethoden",
    "code": "OZM301"
  },
  {
    "naam": "Afstuderen",
    "code": "AFS401"
  }
]
```

### Hoe het werkt

De skills `/schrijven`, `/herschrijven` en `/reviewen` kijken bij het opstarten of `config/user_profile.json` bestaat:

- **Bestand gevonden:** je gegevens worden als standaardwaarden ingevuld. Claude vraagt om bevestiging: "Klopt deze info voor dit rapport?"
- **Bestand niet gevonden:** Claude vraagt de gegevens direct aan jou. De skills werken prima zonder profiel.
- **Specifieke context:** als je een vak of docent noemt in je instructie, wordt die informatie gebruikt in plaats van wat in het profiel staat.

---

## Quick Scans en Beoordelingscriteria

Naast het gebruikersprofiel kun je per vak twee soorten eisen opslaan:

| Map | Wat | Doel |
|-----|-----|------|
| `config/quick_scans/` | Inlevereisen (quick scan) | Checken of je opdracht mag worden ingeleverd |
| `config/beoordelingscriteria/` | Beoordelingsrubric | Checken waarop je rapport wordt beoordeeld |

### Instellen

1. Kopieer het voorbeeldbestand en hernoem naar je vakcode:
```bash
cp config/quick_scans/VOORBEELD.md config/quick_scans/SYS.md
cp config/beoordelingscriteria/VOORBEELD.md config/beoordelingscriteria/SYS.md
```

2. Vul de bestanden in op basis van de documenten van je hogeschool
3. Zorg dat de bestandsnaam overeenkomt met de `code` in `user_profile.json` → `vakken[].code`

### Formaat

Elk bestand heeft twee secties:
- **`## Rapportage`** — items die relevant zijn voor rapportages (worden gebruikt door DutchQuill AI)
- **`## Praktijk`** — items voor praktijkopdrachten (worden genegeerd)

Dit laat je het volledige document van je hogeschool plakken en eenmalig organiseren in de juiste secties.

### Hoe het werkt

Bij `/reviewen` kijkt de workflow in Stap 0:
1. Leest de vakcode uit `user_profile.json`
2. Zoekt matching bestanden in `config/quick_scans/` en `config/beoordelingscriteria/`
3. Laadt alleen de `## Rapportage` items
4. Voert **Domein 5: Inlevereisen & Beoordelingscriteria** uit als extra reviewstap

Als geen bestanden gevonden: standaard review met 4 domeinen (huidige gedrag). De criteria zijn volledig optioneel.

### Nieuw vak toevoegen

1. Voeg het vak toe aan `user_profile.json` → `vakken[]`
2. Maak `config/quick_scans/<VAKCODE>.md` aan
3. Maak `config/beoordelingscriteria/<VAKCODE>.md` aan
4. Vul de `## Rapportage` secties in

---

### Privacy

`config/user_profile.json` staat in `.gitignore` en wordt nooit meegecommit. Alleen het voorbeeldbestand (`config/user_profile.example.json`) zit in de repository.

## Claude Code Settings

De project-instellingen staan in `.claude/settings.json`:

- **Permissions:** alle tools zijn vooraf goedgekeurd voor automatische uitvoering
- **Hooks:** de stop-hook `check_verboden_woorden.py` draait na elke Claude-response

Persoonlijke aanpassingen maak je in `.claude/settings.local.json` (ook gitignored).
