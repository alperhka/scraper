# 🔒 Ticket: DSGVO-Basics - Impressum & Datenschutzseite anlegen

## Beschreibung
Es müssen rechtlich konforme Seiten für die Event-Scraper-Plattform erstellt werden, um DSGVO-Anforderungen zu erfüllen.

---

## Anforderungen

### 1. **Impressum (§ 5 TMG & § 7 ECG)**
Folgende Informationen müssen enthalten sein:
- [ ] Name und Anschrift des Anbieters/Betreibers
- [ ] Telefonnummer und E-Mail-Adresse
- [ ] Handelsregister/Gewerbeanmeldung (falls zutreffend)
- [ ] Umsatzsteuer-ID (falls zutreffend)
- [ ] Verantwortlicher für redaktionelle Inhalte
- [ ] Hinweis auf Haftungsbeschränkung
- [ ] Hinweis auf externe Links (keine Verantwortung für fremde Inhalte)
- [ ] Beschwerdestelle für Telemediengesetz

**Template:**
```
Betreiber dieser Website:
[Name]
[Straße und Hausnummer]
[PLZ Stadt]

Kontakt:
Telefon: [Nummer]
E-Mail: [E-Mail]

Verantwortlich für redaktionelle Inhalte:
[Name]

Haftungsbeschränkung:
Die Inhalte dieser Website werden mit größtmöglicher Sorgfalt erstellt. 
Wir übernehmen jedoch keine Gewähr für die Korrektheit, Vollständigkeit oder Aktualität der Inhalte.
```

---

### 2. **Datenschutzerklärung (DSGVO Art. 13 & 14)**

Folgende Punkte **MÜSSEN** dokumentiert sein:

#### A. **Verantwortlicher**
- [ ] Name und Kontaktdaten des Verantwortlichen
- [ ] Datenschutzbeauftragter (falls vorhanden)

#### B. **Verarbeitete Daten**
- [ ] Automatisch erfasste Daten (IP-Adresse, Browser-Info, Cookies)
- [ ] Event-Daten (Titel, Ort, Datum)
- [ ] Benutzer-Daten (E-Mail, Name - falls Registrierung)
- [ ] Scraping-Quellen (welche Websites gecrawlt werden)

#### C. **Rechtsgrundlagen (DSGVO Art. 6)**
- [ ] Berechtigtes Interesse (News-Aggregation): Art. 6 Abs. 1 lit. f
- [ ] Einwilligung für Cookies: Art. 6 Abs. 1 lit. a
- [ ] Vertrag (falls Newsletter): Art. 6 Abs. 1 lit. b

#### D. **Zwecke der Verarbeitung**
- [ ] Event-Aggregation und Anzeige
- [ ] Verbesserung der Website
- [ ] Analytik (Google Analytics, falls verwendet)
- [ ] Sicherheit und Betrug-Prävention

#### E. **Speicherdauer**
- [ ] Wie lange Events gespeichert werden
- [ ] Wie lange Logs aufbewahrt werden
- [ ] Wie lange Cookies bestehen

#### F. **Empfänger der Daten**
- [ ] Supabase (Cloud-Datenbank)
- [ ] Firecrawl (Web-Scraping-Service)
- [ ] Andere Drittanbieter (falls vorhanden)

#### G. **Betroffenenrechte**
- [ ] Auskunftsrecht (Art. 15)
- [ ] Berichtigungsrecht (Art. 16)
- [ ] Löschungsrecht ("Recht auf Vergessenwerden") (Art. 17)
- [ ] Einschränkung der Verarbeitung (Art. 18)
- [ ] Datenportabilität (Art. 20)
- [ ] Widerspruchsrecht (Art. 21)
- [ ] Beschwerderecht bei Aufsichtsbehörde
  - Für Baden-Württemberg: Landesbeauftragte für Datenschutz (LfD)
  - https://www.bfdi.bund.de/DE/Infothek/Anschriften/Laender/Laender_node.html

#### H. **Cookies & Tracking**
- [ ] Cookie-Banner mit Opt-In für Analytics
- [ ] Auflistung aller verwendeten Cookies
- [ ] Drittanbieter-Cookies (Google Analytics, etc.)
- [ ] Speicherdauer von Cookies

#### I. **Externe Links**
- [ ] Hinweis auf externe Datenschutzerklärungen der gecrawlten Websites
- [ ] Hinweis, dass die Plattform nicht für externe Inhalte verantwortlich ist

---

## Technische Umsetzung

### Seiten die erstellt werden müssen:
- [ ] `/impressum` oder `/legal/impressum`
- [ ] `/datenschutz` oder `/legal/privacy`
- [ ] Footer-Links auf beiden Seiten

### Anforderungen:
- [ ] Leicht zugänglich (nicht versteckt)
- [ ] Mobile-responsive
- [ ] Barrierearm (WCAG)
- [ ] Version mit Datum versehen
- [ ] Letzte Änderung dokumentiert

---

## Besondere Hinweise für dein Scraper-Projekt

⚠️ **Wichtig:** Da du Daten von anderen Websites scrapst, musst du:

1. **robots.txt beachten** - Einige Websites erlauben kein Scraping
2. **AGB der Quellen prüfen** - z.B. SPD.de, Grüne.de (keine Anrechte-Verletzung)
3. **Transparenz** - Offenlegen, dass Daten von anderen Seiten stammen
4. **Link zur Original-Quelle** - Jedes Event sollte zur Original-URL verlinken
5. **Datenverwertung** - Klar kommunizieren, wie die Daten genutzt werden

---

## Checkliste

- [ ] Impressum geschrieben
- [ ] Datenschutzerklärung verfasst
- [ ] Mit Rechtsanwalt/in abgesprochen (empfohlen)
- [ ] Auf Website integriert
- [ ] In Footer verlinkt
- [ ] Robots.txt & Scraping-Lizenzen überprüft
- [ ] Version & Datum hinzugefügt

---

## Ressourcen

- 📖 **DSGVO**: https://gdpr-info.eu/
- 📋 **TMG/ECG**: https://www.e-recht24.de/
- 🏛️ **LfD Baden-Württemberg**: https://www.bfdi.bund.de/
- ⚖️ **E-Recht24 Generator**: https://www.e-recht24.de/muster-impressum.html (kostenpflichtig)
- 🤖 **Generative Tools**: ChatGPT, Claude können als Vorlage helfen

---

## Priorität
🔴 **HOCH** - Rechtliche Compliance erforderlich vor Go-Live

## Status
⏳ TODO
