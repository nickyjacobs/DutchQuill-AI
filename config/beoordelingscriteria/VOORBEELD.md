---
vak: Vaknaam
vakcode: CODE
type: beoordelingscriteria
---

# Beoordelingscriteria — Vaknaam (CODE)

Dit bestand bevat de beoordelingscriteria (rubric) voor het vak. De agent leest alleen de items onder **## Rapportage** — items onder **## Praktijk** worden genegeerd.

## Hoe in te vullen

1. Kopieer dit bestand en hernoem naar je vakcode: `CODE.md` → bijv. `SYS.md`
2. Plak de beoordelingscriteria van je hogeschool
3. Verdeel ze in **Rapportage** en **Praktijk**
4. Groepeer rapportage-items onder subcategorieën (### Structuur, ### Taalgebruik, etc.)
5. Elk item als Markdown-checkbox: `- [ ] Beschrijving van het criterium`
6. Pas de frontmatter aan (vak, vakcode)

De vakcode moet overeenkomen met de `code` in `config/user_profile.json` → `vakken[].code`.

---

## Rapportage

### Structuur en opbouw
- [ ] Voorbeeld: Rode draad duidelijk herkenbaar in inleiding, middenstuk en conclusie
- [ ] Voorbeeld: Logische opbouw van argumentatie

### Taalgebruik
- [ ] Voorbeeld: Academische schrijfstijl
- [ ] Voorbeeld: Grammaticaal correct

### Brongebruik
- [ ] Voorbeeld: Minimaal X bronnen in literatuurlijst
- [ ] Voorbeeld: Alle claims onderbouwd met APA-citaties

### Inhoudelijke diepgang
- [ ] Voorbeeld: Methodologie beschreven en onderbouwd
- [ ] Voorbeeld: Resultaten helder gepresenteerd
- [ ] Voorbeeld: Conclusie beantwoordt de onderzoeksvraag

## Praktijk

(Items hieronder worden niet meegenomen in de review — alleen ter referentie)

- [ ] Voorbeeld: Praktijkopdracht correct uitgevoerd
