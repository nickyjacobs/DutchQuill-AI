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

### Privacy

`config/user_profile.json` staat in `.gitignore` en wordt nooit meegecommit. Alleen het voorbeeldbestand (`config/user_profile.example.json`) zit in de repository.

## Claude Code Settings

De project-instellingen staan in `.claude/settings.json`:

- **Permissions:** alle tools zijn vooraf goedgekeurd voor automatische uitvoering
- **Hooks:** de stop-hook `check_verboden_woorden.py` draait na elke Claude-response

Persoonlijke aanpassingen maak je in `.claude/settings.local.json` (ook gitignored).
