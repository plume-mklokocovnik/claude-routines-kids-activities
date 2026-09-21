# Source Registry: Toddler Activities, Ljubljana → Slovenia

Research pass: 2026-09-21. Every URL below was reachability-checked (HTTP 200) on that date.
This file is the lookup table for `routine.md` §2. Update it when a source dies or a new one appears.
For a flat, token-cheap list of every URL with its status, see [`links.md`](links.md). Read that
first on a normal run. Come here when you need the reasoning, cadence or age-fit behind a source.

**Age note.** Most Slovenian listings advertise `3+`, `4+` or `od 4. leta`. Genuine 0–4 content is
a minority of what these sources carry, so the routine still has to age-filter. Where a source
skews older than the target band, it is marked ⚠️ below.

---

## Tier 0 — Aggregators (sweep these first, they cover the long tail)

| Source | URL | What it gives | Notes |
|---|---|---|---|
| Napovednik.com | `https://napovednik.com/za-otroke` | The single best structured feed. Sub-paths: `/za-otroke/prireditve-za-otroke`, `/za-otroke/predstave-za-otroke`, `/za-otroke/sport-za-otroke`, `/za-otroke/aktivnosti-za-otroke`, `/za-otroke/pocitnisko-varstvo` | Also `/prireditve/plesna-prireditev` and `/prireditve/sportna-prireditev` for the new dance/sport categories. Slug pattern `/<kategorija>/<slug>-<id>` |
| Visit Ljubljana | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/` | Official city calendar. Filters: **Prost vstop**, **Za družine**, **Šport in rekreacija**, **Prireditve na prostem**, plus **Ljubljana / Izven Ljubljane** and a from–to date range | The "Prost vstop" + "Za družine" combination is the highest-yield query on the whole list |
| MOL event calendar | `https://www.ljubljana.si/sl/aktualno/dogodki/` | Municipal calendar. Carries the KoloPark races, festival športa, Veseli december | |
| Kulturnik | `https://dogodki.kulturnik.si/?what=otroci` | Cultural events tagged `otroci`, queryable by venue via `&where=` | |
| MojaObčina Ljubljana | `https://www.mojaobcina.si/ljubljana/dogodki/` | Picks up ZOO and neighbourhood events the bigger portals miss | |
| Kam z mulcem | `https://kamzmulcem.si/` | Editorial, not a calendar. Strong on round-up posts (free December events, pumptrack lists) | Blog format, no date-structured feed |
| Otroško veselje | `https://otroskoveselje.si/dogaja-se-ljubljana/` | Ljubljana kids events, shows price per card | Thin metadata, no date filter |
| Napovednik dogodkov | `https://www.napovednikdogodkov.si/` | ⛔ **Do not sweep.** Its category feed holds only `glasbene-novice`. It is a music news site whose name misleads | Not to be confused with `napovednik.com`, which is the real source |
| Časoris "Kam z otroki" | `https://casoris.si/kam-z-otroki-vsak-dan/` | ⛔ **Dead.** Editors posted that they can no longer keep it current | Do not sweep. Listed so nobody re-adds it |

---

## Tier 1 — Ljubljana core venues

### Theatre, puppets, storytelling, cinema (Ljubljana only, never expanded nationwide)

| Venue | URL | Cadence | Age fit |
|---|---|---|---|
| Lutkovno gledališče Ljubljana | `https://www.lgl.si/spored-predstav` and `https://www.lgl.si/predstave-za-otroke` | Weekend mornings, most weeks | 2+ / 3+, good |
| LGL Lutkovni muzej | `https://www.lgl.si/lutkovni-muzej/muzejski-dogodki` | Occasional | 3+ |
| MKL (city libraries) | `https://www.mklj.si/dogodki/` | *Ure pravljic* most weekday afternoons across ~20 branches | 3+ mostly, some 2+ |
| Kinodvor / Kinobalon | `https://www.kinodvor.org/kinobalon/` | Weekend mornings, *Prvikrat v kino* is the toddler strand | 3+ at the earliest |
| Mala ulica | `https://www.malaulica.si/sl/aktivnosti` | Daily afternoon fairy tales, workshops, *Mala ulica na ulici* pop-ups | **0–4, the single best fit** |
| Cankarjev dom | `https://www.cd-cc.si/` | Weekend family programme | 3+ |
| SiTi Teater BTC | `https://www.sititeater.si/sobotni-dopoldnevi/` | *Sobotni dopoldnevi*, Saturday mornings, Oct–Apr season | 3+ |

**MKL scraping detail.** The site runs The Events Calendar with a filter bar. Useful query params:
`tribe_filterbar_dogodki_ciljna_skupina[]` (target audience), `_prizorisce[]` (branch),
`_vrsta[]` (event type), `_serija[]` (series). Individual events resolve to
`/dogodek/<slug>/<YYYY-MM-DD>/`, which makes deterministic IDs easy. Filtering on
`ciljna_skupina` is far cheaper than scraping the whole calendar.

### Museums and galleries

| Venue | URL | Cadence | Age fit |
|---|---|---|---|
| MGML (city museums) | `https://mgml.si/sl/dogodki/` and `/sl/programi/programi-druzine/` | Saturday-afternoon family workshops | 4+ ⚠️ |
| Narodna galerija | `https://www.ng-slo.si/si/` | *Galove urice* | 4+ ⚠️ |
| SEM | `https://www.etno-muzej.si/sl/dogodki` | Weekend family workshops | 4+ ⚠️ |
| MAO | `https://mao.si/` | *MiniMAO* | 4+ ⚠️ |
| Hiša eksperimentov | `https://he.si/` | Science demos, age-banded workshops | 4+ ⚠️ |
| Tehniški muzej Bistra | `https://www.tms.si/` | Thematic weekends with workshops and demos | 4+ ⚠️, outside city |
| Ljubljanski grad | `https://www.ljubljanskigrad.si/` | Family programmes, Bobri host venue | 4+ |

**Nationwide museum hook:** first Sunday of the month is free admission at most Slovenian
museums, and many add a children's workshop on that day. Worth a standing monthly check.

### ZOO Ljubljana

`https://www.zoo.si/novice` and `https://www.zoo.si/ponudba`

The zoo runs free conservation events and animal encounters on weekends and public holidays
year-round. These cost nothing beyond the normal entrance ticket, so they qualify as scheduled
one-off events rather than "always on" opening hours. Recurring annual fixtures:

* **Dan Zemlje** — late April into the May Day holidays, conservation programme across several days
* **Svetovni dan živali + dan oskrbnikov** — the weekend around 4 October, enrichment demos, "how to become a conservationist", night tours
* **Noč čarovnic** — through October to the 31st, candlelit themed evening tours ⚠️ *evening timing, poor toddler fit*
* **Poletne počitnice** and **zimske počitnice** — ⛔ **exclude**, these are paid multi-day camps for ages 5+, exactly the subscription pattern the rules forbid

---

## Tier 2 — New activity categories

### 🏃 Runs and family races

| Source | URL | Notes |
|---|---|---|
| Slovenski tekaški koledar | `https://tekaski-koledar.si/` | 200+ events, has an explicit family-friendly flag |
| Tekaške prireditve | `https://tekaskeprireditve.si/koledar-tekaskih-prireditev/` | Categorises by **Otroški tek** and **Družinski tek** — sweep these two categories directly |
| NLB Ljubljanski maraton — Lumpi tek | `https://ljubljanskimaraton.si/lumpi-tek` | The preschool race. Non-competitive, no timing, medal and small gift for every child |

**Lumpi tek 2026.** The marathon weekend is 17–18 October 2026, with children's, school and
promotional races on the Saturday. Course runs along Rimska cesta and finishes at Kongresni trg.
Start packets at Sejem Tečem in Arena Stožice, or at Trg republike on race day.
⚠️ Source pages gave inconsistent day/date pairings, so re-verify the exact Lumpi start time
against `ljubljanskimaraton.si` before writing it into `db.json`.

### 🚲 Balance bikes and pumptracks — the best-fitting sport category for 0–4

| Source | URL | Notes |
|---|---|---|
| Argeta Junior KoloPark Pokal | `https://www.kd-rajd.si/en/argeta-junior-kolopark-pokal/` + MOL calendar | Series across Ljubljana's koloparks: Bežigrad, Aleja, Vič, Polje, Nove Fužine, Štepanjsko naselje. Spring to autumn, Saturday mornings around 9:30 |
| Pumpaj Slovenija | `https://pumptrack.si/pumpaj-slovenija/` | National series, per-venue calendar pages under `/koledar-2026/` |

The KoloPark series explicitly welcomes the youngest riders **on balance bikes with a parent
helping**, and hands a prize to every registered starter. Free, recreational, no published
results. This is the strongest toddler-sport find of the whole sweep. Pumpaj's companion
programme **Grbine so fine** is free animation for ages 4–12 with licensed instructors.

### 🤸 Open-door days and free trials of otherwise-paid activities

| Source | URL | Notes |
|---|---|---|
| Ljubljanski festival športa | `https://www.ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` | See annual fixtures below |
| Gremo na brezplačne vadbe (MOL) | `https://www.ljubljana.si/sl/ljubljana/sportna/gremo-na-brezplacne-vadbe` | Year-round free sessions. *Mali sonček* strand targets preschoolers |
| Javni zavod Šport Ljubljana | `https://www.sport-ljubljana.si/` | Free pool and fitness sessions, guided training |
| Športna zveza Ljubljane | `https://szlj.si/` | Runs the free summer sports holidays ⚠️ *school-age* |
| Dan slovenskega športa | `https://danslovenskegasporta.si/` | 23 September, national holiday. Free sessions nationwide |
| Olimpijski komite | `https://olympic.si/` | European Week of Sport registry, clubs register free trial sessions by age band |

⚠️ **Rules conflict, needs a decision.** Open-door days are the exact thing the user asked to
capture, but clubs advertise them on pages that also push enrollment, so the words `vpis`,
`vpisi` and `tečaj` sit right next to the free session. A naive keyword exclusion throws away
the whole category. The fix, now written into `routine.md` §1, is a carve-out: keep an item when
it has a concrete date **and** start time **and** a free-trial marker
(`dan odprtih vrat`, `brezplačna vadba`, `predstavitvena vadba`, `preizkusi`, `brezplačno preizkusite`),
even when enrollment language appears elsewhere on the page. Exclude the enrollment itself.

### 💃 Dance

| Source | URL | Notes |
|---|---|---|
| Napovednik dance category | `https://napovednik.com/prireditve/plesna-prireditev` | Best structured source for one-off dance events |
| Parada plesa | `https://www.paradaplesa.si/` | Dance news portal. Announces festivals, championships, public performances |
| Plesna zveza Slovenije | `https://www.plesna-zveza.si/` | Šolski plesni festival, *Slovenija pleše* ⚠️ *school-age* |
| Plesni Teater Ljubljana | `http://ptl.si/` | Occasional dance pieces for young audiences |
| Katja Dance Company | `https://www.katjadancecompany.com/` | Danced fairy tales for children, e.g. *Objemi drevo!* |

Honest assessment: dance for the 0–4 band in Slovenia is overwhelmingly **courses**, not events.
The few genuine one-off items are danced fairy-tale performances and the open free trials at
studios such as Plesni Studio Intakt. Expect low yield and expect the exclusion rules to fire
often here.

### 🎬 Free open-air cinema

| Event | Where | When | Free? |
|---|---|---|---|
| Letni Kinodvor | Kongresni trg, Ljubljana | ~26–29 August, 21:00 | ✅ Free |
| Slovenska kinoteka open-air | Muzejska ploščad Metelkova | ~6–22 August | ✅ Free |
| Kinodvorišče | Kinodvor atrium | June to early July, 21:30 | ❌ Paid |
| Film pod zvezdami | Ljubljanski grad courtyard | ~9 July – 1 August, 21:30 | ❌ Paid |
| Letni kino Minoriti | Maribor | July–August | Mixed |
| Skatepark Maribor | Maribor | Occasional, Slovenian films | ✅ Free |
| Arboretum open-air | Volčji Potok | Summer evenings, children's films | With park ticket |

⚠️ **Timing caveat worth acting on.** Every free outdoor screening starts at 21:00 or later,
which is past bedtime for the target band. Only Arboretum programmes films actually aimed at
children. The routine should still capture these, but flag them rather than presenting them as
toddler-suitable.

---

## Tier 3 — Annual fixtures

Moved to **[`annual.md`](annual.md)**, which now holds the recurrence rule, typical window,
confidence rating and booking lead time for every yearly event, plus the window-overlap check the
routine runs against the 3-month horizon. Keeping one copy avoids the two drifting apart.

Corrections that came out of that research and matter here:

* **Bobri moved.** It used to run mid-January to early February. The 2026 edition ran 21 March to
  4 April. Do not search for it in January. Its free tickets are released about two weeks ahead
  and go within hours.
* **Trnfest is retired.** Last edition 2018. The successor is **Trnovfest**, a different
  organiser in Trnovo (`https://www.cskfp.si/`), running daily through August at roughly 5 € a day.
* **Otroški bazar status is unknown.** The site shows only a "returning in a new form" holding
  message with no dates. Do not promise a September edition without checking first.
* **Three recurrence rules are solid enough to compute instead of search:** Poletna muzejska noč
  is the third Saturday of June, Ljubljanski festival športa is the first Saturday of September,
  and Čarobni dan is the last Sunday of August.

---

## Search queries

### Pass 1 — Ljubljana

```
dogodki za otroke Ljubljana ta vikend
brezplačne prireditve za otroke Ljubljana
ure pravljic Ljubljana MKL
lutkovna predstava Ljubljana za malčke
Kinobalon Kinodvor spored
delavnice za otroke Ljubljana
dan odprtih vrat brezplačna vadba otroci Ljubljana
brezplačno preizkusi šport otroci Ljubljana
plesna predstava za otroke Ljubljana
otroški tek Ljubljana družinski tek
kolopark pokal Ljubljana poganjalčki
kino na prostem Ljubljana brezplačno
ZOO Ljubljana prireditev vikend
prireditve za družine Ljubljana prost vstop
```

### Pass 2 — Slovenia-wide

Run these only for sport, dance, runs, open-door days, zoo and outdoor cinema.
**Do not expand art workshops, gallery programmes, storytelling or puppet shows beyond
Ljubljana** — travelling an hour each way with a toddler for a 30-minute puppet show does not pay
off, and the volume would drown the list.

```
otroški tek Slovenija koledar prireditev
družinski tek Slovenija
pumptrack tekma otroci Slovenija
dan odprtih vrat športni klub otroci Slovenija
brezplačna vadba za otroke Slovenija september
plesna prireditev za otroke Slovenija
brezplačen letni kino Slovenija
družinski festival Slovenija brezplačno
živalski vrt prireditev za otroke Slovenija
```

### Seasonal, run in the matching month

```
Festival Bobri program            # Jan–Apr
Igraj se z mano festival program  # May
Poletna muzejska noč program      # June
Ana Desetnica program             # late June
Čarobni dan Arboretum             # late Aug
Ljubljanski festival športa Tivoli  # early Sep
Otroški bazar program             # Sep
Pikin festival program            # Sep
Dan slovenskega športa brezplačne aktivnosti  # 23 Sep
Lumpi tek prijave                 # Oct
Noč čarovnic ZOO Ljubljana        # Oct
Veseli december Ljubljana dedek mraz program  # Dec
```

---

## Scraping notes

* **Napovednik.com** is the only source with a clean, consistent, category-scoped URL structure.
  Start every sweep there.
* **MKL** exposes filter-bar query params, so filter server-side on `ciljna_skupina` instead of
  pulling the full calendar.
* **Visit Ljubljana** has the single most useful filter combination in the whole registry:
  *Prost vstop* + *Za družine* + a date range, with an Izven Ljubljane toggle that directly
  implements the two-pass geography.
* **kamzmulcem** and **otroskoveselje** are editorial. Treat them as lead generators for venues
  worth checking, not as parseable calendars.
* Shopping-centre programmes (Citypark, Aleja, Supernova, BTC) are published as news posts rather
  than calendars and tend to appear only a week ahead. Sweep them weekly or you will miss them.
* Several sites have moved or died since the original spec was written. `ljubljanajesport.si`
  no longer resolves, `casoris.si` stopped updating, and `lgl.si` reorganised its paths. Re-check
  reachability periodically and prune this file rather than letting the routine fail quietly.
