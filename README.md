
# KeyGenPy – Professioneller Passwort-Generator

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt-6.6+-green.svg)

**KeyGenPy** ist ein leistungsstarker Passwort-Generator mit einer übersichtlichen Dark-Mode-GUI. Er erzeugt hochsichere Passwörter mit einstellbarer Länge, Zeichenzusammensetzung und Sonderzeichen-Häufigkeit. Zusätzlich bietet er einen Verlauf, Export-Funktionen und macOS-iCloud-Integration.

<img width="910" height="759" alt="screenshot" src="https://github.com/user-attachments/assets/f4c52b64-4e3d-4d64-a72e-a067469ac0f4" />

---

## ✨ Features

- **Individuelle Passwort-Einstellungen**  
  - Länge von 4 bis 2048 Zeichen  
  - Groß-/Kleinbuchstaben, Ziffern, Sonderzeichen  
  - Ausschluss bestimmter Zeichen (z. B. `0O1lI`)  
  - Gruppierung mit Trennzeichen (z. B. `ABCD-1234-EFGH`)  

- **Sonderzeichen-Steuerung**  
  Wählen Sie die Häufigkeit der Sonderzeichen:  
  - `viele (Standard)` – gleichmäßige Verteilung  
  - `wenige` – ca. 10 % Sonderzeichen  
  - `einzelne` – ca. 5 % Sonderzeichen  
  - `eins pro Gruppe` – genau ein Sonderzeichen pro Gruppe (bei Gruppierung > 0)  
  - `nur eins` – genau ein Sonderzeichen im gesamten Passwort  

- **Entropie- und Stärke-Anzeige**  
  Echtzeit-Berechnung der Entropie (in Bit) und farbige Stärke-Balken.

- **Verlauf**  
  Alle generierten Passwörter werden mit Zeitstempel angezeigt – Export als JSON, TXT oder CSV möglich

- **Automatisches Kopieren**  
  Optional: Passwort direkt nach der Generierung in die Zwischenablage kopieren und in den Verlauf übernehmen.

- **macOS iCloud-Schlüsselbund-Export**  
  Erzeugt eine Apple-kompatible CSV-Datei für den Import in die macOS-Passwörter-App (für Websites und Apps).

- **Dark Theme & Tastaturkürzel**  
  Modernes, augenschonendes Design, `Ctrl+G` für Neu-Generierung, `Ctrl+Shift+C` für Kopieren.

---

<details>
<summary>📞 Kontakt</summary>


Bei Fragen oder Anregungen können Sie ein Issue auf GitHub eröffnen.
</details>

---

## Viel Spaß mit KeyGenPy – sichere Passwörter leicht gemacht! 🔐


---

<details>
<summary>🛡️ Lizenzen / Licenses</summary>

MIT-Lizenz

Copyright (c) 2026 BinhDiez64

Hiermit wird jeder Person, die eine Kopie dieser Software und der zugehörigen
Dokumentationsdateien (die "Software") erhält, unentgeltlich die Erlaubnis erteilt,
die Software ohne Einschränkung zu nutzen, einschließlich und ohne Einschränkung
der Rechte zur Nutzung, Kopie, Änderung, Zusammenführung, Veröffentlichung,
Verteilung, Unterlizenzierung und/oder zum Verkauf von Kopien der Software, und Personen, denen
die Software zur Verfügung gestellt wird, dies unter den folgenden Bedingungen zu gestatten:
Der obige Urheberrechtshinweis und dieser Erlaubnishinweis müssen in allen Kopien oder
wesentlichen Teilen der Software enthalten sein.

DIE SOFTWARE WIRD OHNE JEGLICHE AUSDRÜCKLICHE ODER STILLSCHWEIGENDE GARANTIE BEREITGESTELLT,
EINSCHLIESSLICH, ABER NICHT BESCHRÄNKT AUF DIE GARANTIEN DER MARKTGÄNGIGKEIT, DER EIGNUNG
FÜR EINEN BESTIMMTEN ZWECK UND DER NICHTVERLETZUNG VON RECHTEN. IN KEINEM FALL
SIND DIE AUTOREN ODER RECHTSINHABER FÜR JEGLICHE ANSPRÜCHE, SCHÄDEN ODER
ANDEREN HAFTUNGEN VERANTWORTLICH, OB IN EINER VERTRAGS- ODER DELIKTSHAFTUNG ODER ANDERWEITIG,
DIE AUS DER ODER IN VERBINDUNG MIT DER SOFTWARE ODER DER NUTZUNG ODER ANDEREN HANDLUNGEN 
DER SOFTWARE ENTSTEHEN.

    ---

Diese Software verwendet PyQt6, das urheberrechtlich (c) Riverbank Computing Limited
geschützt ist.
PyQt6 ist freie Software: Sie können es unter den Bedingungen der GNU General Public License,
wie von der Free Software Foundation veröffentlicht, entweder Version 3 der Lizenz
oder (nach Ihrer Wahl) jeder späteren Version, weiterverteilen und/oder modifizieren.
PyQt6 wird in der Hoffnung verteilt, dass es nützlich sein wird, aber OHNE JEGLICHE GARANTIE;
sogar ohne die stillschweigende Garantie der MARKTGÄNGIGKEIT oder der EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
Weitere Einzelheiten finden Sie in der GNU General Public License.
Sie sollten eine Kopie der GNU General Public License zusammen mit PyQt6 erhalten haben.
Falls nicht, siehe <http://www.gnu.org/licenses/>.

=== English Version ===

MIT License

Copyright (c) 2026 BinhDiez64

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

This software uses PyQt6, which is Copyright (c) Riverbank Computing Limited.

PyQt5 is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

PyQt6 is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
PyQt5. If not, see <http://www.gnu.org/licenses/>.

</details>

---

<details>
<summary>🔒 macOS Gatekeeper_Info</summary>

KeyGenPy ist derzeit nicht mit einem Apple-Developer-Zertifikat signiert.

Beim ersten Start kann macOS Gatekeeper die Ausführung blockieren.

1. App einmal öffnen.
2. Warnung schließen.
3. **Systemeinstellungen → Datenschutz & Sicherheit**
4. Dort ganz nach unten bis zur Warnung "KeyGenPy wurde blockiert..." scrollen.
5. **„Dennoch öffnen“** auswählen
6. Wenn noch einmal gewarnt wird: erneut **„Dennoch öffnen“** auswählen und mit Passwort bestätigen.

### Alternativ:

Seit neueren macOS-Versionen kann die Meldung manchmal strenger sein oder es Wenn es keinen Button „Dennoch öffnen“ gibt

Dann kannst du das Quarantäne-Attribut im Terminal entfernen:

🍎 macOS Terminal

xattr -d com.apple.quarantine /Pfad/zu/KeyGenPy.app

Oder, wenn die App z. B. im Programme-Ordner liegt:

xattr -d com.apple.quarantine "/Applications/KeyGenPy.app"

Falls die App in deinem Downloads-Ordner liegt:

xattr -d com.apple.quarantine "$HOME/Downloads/KeyGenPy.app"

> Den Pfad zur Datei ggf. anpassen.

Anschließend die App erneut starten.

</details>

---

<details>
<summary>🖥️ Download-Info</summary>

### Download-Versione

| Suffix | Betriebssystem |
|--------|-----------------|
| `_macOS_as` | Apple Silicon (M1–M4) |
| `_macOS_intel` | Intel Macs |
| `_win` | Windows x64 |

> Windows on ARM wird derzeit nicht unterstützt / not supported

### Extract 7z-Archive

| Betriebssystem | Empfohlene App |
|---------------|----------------|
| 🍎 macOS | **Keka** – <https://www.keka.io/> |
| 🪟 Windows | **7-Zip** – <https://www.7-zip.org/> |

</details>


<details>
<summary>🔑 7z Passwort</summary>

**BinhDiez**

</details>



