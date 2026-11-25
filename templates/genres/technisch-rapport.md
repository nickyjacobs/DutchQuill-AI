---
genre: technisch-rapport
naam: Technisch rapport
toon: zakelijk
lengte: 1500-10000 woorden
modules: taal, humaniseren
---

# Technisch rapport

Voor een pentest, een security-audit, een incidentrapport of een technische analyse. Twee lezers tegelijk: het
management leest de samenvatting en de risico's, de techneut leest de bevindingen en wil ze kunnen nadoen.

**Lezer:** opdrachtgever en management (samenvatting), beheerders en ontwikkelaars (bevindingen).

## Opbouw

1. Titel, datum, versie, classificatie, opdrachtgever en uitvoerders (frontmatter).
2. Managementsamenvatting: wat is onderzocht, het totaalbeeld in één alinea, de bevindingen per risiconiveau in
   een tabel, en de drie belangrijkste acties. Geen jargon.
3. Scope en aanpak: wat wel en niet onderzocht is, de periode, de methode of standaard (bijvoorbeeld PTES, OWASP
   WSTG, ISO 27001), de beperkingen.
4. Bevindingen, één per sectie, van hoog naar laag risico. Per bevinding vast:
   - titel en risiconiveau (met de methode: CVSS, of kans maal impact);
   - beschrijving: wat is er aan de hand;
   - bewijs: stappen om het na te doen, verzoeken, uitvoer of een schermafbeelding;
   - impact: wat kan een aanvaller ermee;
   - aanbeveling: wat te doen, zo concreet mogelijk;
   - verwijzingen (CWE, CVE, leveranciersadvies).
5. Conclusie en vervolg: wat eerst, wanneer opnieuw testen.
6. Bijlagen: gebruikte tools, tijdlijn, volledige uitvoer.

## Let op

- **Herhaling van vaste termen is hier goed.** Dezelfde naam voor hetzelfde systeem, dezelfde opbouw per
  bevinding. Varieer niet om de variatie.
- Lijdende vorm mag in het bewijs en de aanpak ("de poort werd gescand"); in de samenvatting en de aanbevelingen
  zeg je wie wat doet.
- Technische zinnen zijn langer; de leesbaarheid mag lager liggen dan bij een gewoon rapport (Flesch-Douma vanaf
  25). De managementsamenvatting houd je wel eenvoudig.
- Nooit echte wachtwoorden, sleutels of klantgegevens in voorbeelden: gebruik placeholders als `<doel-ip>` en
  `<klant>`.
- Een risicotabel of heatmap kan met `dq grafiek --type heatmap`.
