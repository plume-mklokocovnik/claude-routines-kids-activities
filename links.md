# Link Index

Flat lookup table of every URL checked during the source research. Read this instead of
re-discovering sources through search. `sources.md` has the reasoning, cadence and age-fit notes. `annual.md` has Ljubljana's yearly fixtures
and their recurrence rules, `regions.md` has the rest of Slovenia plus its own source list.
This file is just the addresses.

**Verified:** 2026-09-21, every row status-checked with a real HTTP request.

Status values:
* `ok` — returned 200, use it
* `low` — resolves, but poor yield for this routine
* **`avoid`** — do not retry, see the block below for why

---

## ⛔ Do not retry

Confirmed dead ends. Each was checked at least twice, by two different methods where possible.
Retrying these wastes a request and returns nothing. Use the replacement instead.

| Dead URL | Failure | Certainty | Use instead |
|---|---|---|---|
| `ljubljanajesport.si` (whole domain) | NXDOMAIN, no DNS record at all. Two curl attempts plus a direct DNS lookup | **Certain.** A domain with no DNS record cannot come back without someone re-registering it | `https://www.ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` |
| `ljubljanskifestivalsporta.ljubljana.si` | NXDOMAIN, same as above | **Certain** | Same as above |
| `https://casoris.si/kam-z-otroki-vsak-dan/` | Resolves and returns 200, but the editors posted that they can no longer track children's events. The listings are frozen | **Certain.** The page is alive and the content is abandoned. Fetching it costs tokens and returns stale events | `napovednik.com/za-otroke` |
| `https://www.napovednikdogodkov.si/` (as a kids source) | Alive, but its WordPress category feed contains only `glasbene-novice` and `uncategorized`. It is a music news site. The `/za-otroke/` path a search engine surfaced is a 404 | **Certain.** There is no children's category to sweep | `napovednik.com/za-otroke` (different site, similar name) |
| `https://www.zoo.si/ponudba/noc-carovnic` | 404. Seasonal page, taken down out of season | *Likely seasonal.* Worth one check in October, not before | `https://www.zoo.si/novice` |
| `festival.olympic.si` | NXDOMAIN. The 2025 Olympic Festival had its own subdomain and it has since been taken down | **Certain**, no DNS record | `https://olympic.si/` and `https://ewos.olympic.si/` |

### Wrong guesses, not dead sites

These 404s were bad path guesses on healthy sites. The site is fine. Use the corrected path.

| Guessed | Correct |
|---|---|
| `napovednik.com/prireditve/za_otroke` | `napovednik.com/za-otroke` |
| `lgl.si/si/predstave`, `/si/program`, `/si/repertoar` | `lgl.si/spored-predstav` |
| `mklj.si/napovednik-dogodkov/` | `mklj.si/dogodki/` |
| `ljubljana.si/.../ljubljana-je-sport/ljubljanski-festival-sporta/` | `ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` |

---

## Aggregators

| Source | URL | Use | Status |
|---|---|---|---|
| Napovednik | `https://napovednik.com/za-otroke` | Primary feed, start here | ok |
| Napovednik shows | `https://napovednik.com/za-otroke/predstave-za-otroke` | Performances | ok |
| Napovednik events | `https://napovednik.com/za-otroke/prireditve-za-otroke` | General events | ok |
| Napovednik sport | `https://napovednik.com/za-otroke/sport-za-otroke` | Kids sport | ok |
| Napovednik activities | `https://napovednik.com/za-otroke/aktivnosti-za-otroke` | Activities | ok |
| Napovednik holiday care | `https://napovednik.com/za-otroke/pocitnisko-varstvo` | Camps, mostly excluded by rules | low |
| Napovednik dance | `https://napovednik.com/prireditve/plesna-prireditev` | Dance category | ok |
| Napovednik sport events | `https://napovednik.com/prireditve/sportna-prireditev` | Sport category | ok |
| Visit Ljubljana | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/` | Filters: Prost vstop + Za družine + date + Izven Ljubljane | ok |
| MOL calendar | `https://www.ljubljana.si/sl/aktualno/dogodki/` | KoloPark, festivals, December | ok |
| Kulturnik | `https://dogodki.kulturnik.si/?what=otroci` | Culture tagged otroci, `&where=` filters venue | ok |
| MojaObčina LJ | `https://www.mojaobcina.si/ljubljana/dogodki/` | Zoo and neighbourhood pickup | ok |
| Kam z mulcem | `https://kamzmulcem.si/` | Editorial round-ups, lead generation only | low |
| Otroško veselje | `https://otroskoveselje.si/dogaja-se-ljubljana/` | Thin metadata, no date filter | low |

## Ljubljana venues: stage, screen, story

| Source | URL | Status |
|---|---|---|
| LGL schedule | `https://www.lgl.si/spored-predstav` | ok |
| LGL kids shows | `https://www.lgl.si/predstave-za-otroke` | ok |
| LGL puppet museum | `https://www.lgl.si/lutkovni-muzej/muzejski-dogodki` | ok |
| MKL events | `https://www.mklj.si/dogodki/` | ok |
| MKL kids section | `https://www.mklj.si/otroci/` | ok |
| Kinodvor Kinobalon | `https://www.kinodvor.org/kinobalon/` | ok |
| Kinodvor outdoor summer | `https://www.kinodvor.org/kinodvorovo-poletje-s-filmi-na-prostem/` | ok |
| Mala ulica | `https://www.malaulica.si/sl/aktivnosti` | ok |
| Cankarjev dom | `https://www.cd-cc.si/` | ok |
| SiTi Teater Saturdays | `https://www.sititeater.si/sobotni-dopoldnevi/` | ok |
| Plesni Teater Ljubljana | `http://ptl.si/` | ok |
| Katja Dance Company | `https://www.katjadancecompany.com/` | ok |

**MKL filter params:** `tribe_filterbar_dogodki_ciljna_skupina[]`, `_prizorisce[]`, `_vrsta[]`, `_serija[]`.
Event permalinks: `/dogodek/<slug>/<YYYY-MM-DD>/`.

## Ljubljana venues: museums, galleries, zoo

| Source | URL | Status |
|---|---|---|
| MGML events | `https://mgml.si/sl/dogodki/` | ok |
| MGML family programmes | `https://mgml.si/sl/programi/programi-druzine/` | ok |
| Narodna galerija | `https://www.ng-slo.si/si/` | ok |
| SEM | `https://www.etno-muzej.si/sl/dogodki` | ok |
| MAO | `https://mao.si/` | ok |
| Hiša eksperimentov | `https://he.si/` | ok |
| Tehniški muzej Bistra | `https://www.tms.si/` | ok |
| Ljubljanski grad | `https://www.ljubljanskigrad.si/` | ok |
| ZOO news | `https://www.zoo.si/novice` | ok |
| ZOO programmes | `https://www.zoo.si/ponudba` | ok |
| Museums of Slovenia | `https://sms-muzeji.si/` | ok, Poletna muzejska noč host |

## Sport, runs, wheels

| Source | URL | Status |
|---|---|---|
| Argeta Junior KoloPark | `https://www.kd-rajd.si/en/argeta-junior-kolopark-pokal/` | ok, best 0-4 fit |
| Pumpaj Slovenija | `https://pumptrack.si/pumpaj-slovenija/` | ok |
| Pumpaj 2026 calendar | `https://pumptrack.si/pumpaj-slovenija/koledar-2026/` | ok |
| Ljubljanski festival športa | `https://www.ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` | ok |
| MOL free sessions | `https://www.ljubljana.si/sl/ljubljana/sportna/gremo-na-brezplacne-vadbe` | ok |
| Šport Ljubljana | `https://www.sport-ljubljana.si/` | ok |
| Športna zveza Ljubljane | `https://szlj.si/` | ok, skews school-age |
| Dan slovenskega športa | `https://danslovenskegasporta.si/` | ok |
| Olympic Committee | `https://olympic.si/` | ok, European Week of Sport registry |
| Running events calendar | `https://tekaskeprireditve.si/koledar-tekaskih-prireditev/` | ok, has Otroški tek and Družinski tek categories |
| Slovenian running calendar | `https://tekaski-koledar.si/` | ok |
| Lumpi tek | `https://ljubljanskimaraton.si/lumpi-tek` | ok |
| Plesna zveza Slovenije | `https://www.plesna-zveza.si/` | ok, skews school-age |
| Parada plesa | `https://www.paradaplesa.si/` | ok, news portal not a calendar |

## Festivals and seasonal

| Event | URL | Month | Status |
|---|---|---|---|
| Bobri | `https://bobri.si/` | Jan–Apr | ok |
| Igraj se z mano | `https://igrajsezmano.eu/festival/ljubljana/` | May | ok |
| Ana Desetnica | `https://www.anamonro.si/festivali/festivalski-program/` | Jun–Jul | ok |
| Čarobni dan | `https://www.arboretum.si/dogodek/carobni-dan/` | Late Aug | ok |
| Arboretum calendar | `https://www.arboretum.si/dogajanje/prireditvenik/` | All year | ok |
| Zmaj 'ma mlade (Postojna) | `https://www.zmaj-ma-mlade.com/` | Aug–Sep | ok |
| Otroški bazar | `https://www.otroskibazar.si/` | Sep | ok |
| Pikin festival (Velenje) | `https://www.pikinfestival.si/` | Sep | ok |
| Slovenska kinoteka | `https://www.kinoteka.si/` | Aug outdoor | ok |
| Čarobni dan (own site) | `https://www.carobnidan.si/` | Late Aug | ok |
| Trnovfest (CSK F. Prešeren) | `https://www.cskfp.si/` | Aug | ok, replaces the retired Trnfest |
| Miklavžev sprevod | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/miklavzev-sprevod/` | 5 Dec | ok |
| December v Ljubljani | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani` | Dec | ok |
| Kurentovanje (Ptuj) | `https://kurentovanje.net/` | Moveable, tied to Easter | ok |
| Otroški bazar | `https://www.otroskibazar.si/` | Sep | ⚠️ resolves, but shows a holding page with no dates. Status unknown |

## Children's arts venues found in the 50-event cross-check

These were missing from the first pass. Hiša otrok in umetnosti alone runs three annual
festivals, so it is the biggest single gap the cross-check closed.

| Source | URL | Why it matters | Status |
|---|---|---|---|
| **Hiša otrok in umetnosti** | `https://www.hisaotrok.si/koledar_prireditev/list/` | Runs Zmaj kamišibaj, VNLG and Emonska promenada, plus a regular children's programme. Kamišibaj here is the best small-scale format for the youngest | ok |
| **Pionirski dom** | `https://pionirski-dom.si/` | Otroški festival gledaliških sanj, Teden otroka open doors, carnival party | ok |
| **Mini teater** | `https://www.mini-teater.si/si` | Mini poletje, year-round puppet programme on Križevniška and at the castle | ok |
| **Botanični vrt** | `http://www.botanicni-vrt.si/napovednik-dogodkov` | Monthly event listing, family workshops, Mali raziskovalci | ok |
| **Knjižnica pod krošnjami** | `https://www.knjiznicapodkrosnjami.si/` | Summer outdoor reading islands with scheduled storytellers | ok |
| Rimljani v Ljubljani | `https://rimljanivljubljani.si/` | MGML Roman family festival, free, 4+ | ok |
| Svetlobna gverila | `https://www.svetlobnagverila.net/` | Light festival, installations across the city | ok |
| Maraton Franja | `https://franja.org/` | Kids 1,000 m cycling challenge at BTC | ok |
| Teden otroka (ZPMS) | `https://www.zpms.si/programi/teden-otroka/` | The national organiser, first week of October | ok |
| Slovenski knjižni sejem | `https://knjizni-sejem.si/` | Late November, moved to Gospodarsko razstavišče | ok |
| Otroški knjižni festival | `https://www.cd-cc.si/kultura/za-mlade-in-sole/otroski-knjizni-festival` | Cankarjev dom, June | ok |
| Grajski dnevi | `https://www.ljubljanskigrad.si/sl/dogodki/grajski-dnevi/` | May medieval camp at the castle | ok |
| Gregorčki | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/pozdrav-pomladi-z-gregorcki` | 11 March, candlelit boats on the Gradaščica | ok |
| LUV fest | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/luv-fest` | 8 Feb to 12 Mar, 220+ events | ok |
| EWoS | `https://ewos.olympic.si/` | European Week of Sport free-session registry | ok |

## Shopping centres and commercial play venues

Published as news posts and social posts roughly a week ahead, not as calendars. Sweep weekly or
miss them. Since exclusion rule 2 now turns on whether something is scheduled rather than who
owns the venue, play cafes, trampoline parks and indoor playgrounds belong here too: skip their
opening hours, take their dated events.

| Source | URL | Status |
|---|---|---|
| Citypark kids | `https://www.citypark.si/si/otroci/` | ok |
| Citypark shows | `https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/` | ok, free theatre first Friday monthly |

---

## Maintenance

When a sweep hits a failure, classify it before editing this file.

* **NXDOMAIN or connection refused, twice** — move the row to *Do not retry* with a replacement.
* **404 on a path while the site root answers** — the path moved. Find the new one, correct the row, do not blacklist the site.
* **404 on a page that only exists in season** — leave it, note the month.
* **Alive but the content is stale or off-topic** — move to *Do not retry* and say so. A live URL that never yields a usable event is more expensive than a dead one, because nothing signals to stop fetching it.
* **An annual event whose site shows a holding page** — leave the row, mark the status unknown, and record the doubt in [`annual.md`](annual.md). Do not quietly keep promising the event.
