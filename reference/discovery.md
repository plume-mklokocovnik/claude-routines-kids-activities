# Discovery Policy and Queries

Use this reference for semantic filtering and source selection. Follow
[routine.md](../routine.md) for execution and [the data contract](../docs/data-contract.md)
for persistence. In this file, `now` means the staged run's captured clock.
Existing records are never deleted, even when they no longer qualify as active.

Every candidate needs a fetched confirming URL, a confirmed date and a venue.
Keep missing-date or missing-venue items as leads. Never invent missing fields.
Search examples with a month/year are templates. Substitute every month and year
intersecting the actual three-month horizon, including January after a year roll.
Historical prices and calendar dates below are examples, not current evidence.

## 1. Sweep Criteria & Filters

### ✅ Target Activity Criteria
* **Geography (two passes, plus a category pass):**
  1. **Pass 1 — Ljubljana** and its immediate surrounding neighborhoods. Always run this pass.
  2. **Pass 2 — rest of Slovenia.** Judge by destination value, not by category. **Take** anything worth the trip on its own: a full-day or multi-day festival, a free family day at a castle or estate, a signature local celebration with a children's programme, a race, an open-door day. **Leave** a standalone single performance that simply happens to be in another town, since a 30-minute puppet show does not repay two hours in the car. The same show inside a day-long festival does. Set `city` and the `outside_ljubljana` flag on everything from this pass. Fixtures, leads and regional sources live in [`regions.md`](regions.md).
  3. **Pass 3 — children's concerts.** A category sweep that runs on top of both, with its own geography carve-out for the named artists. Defined in [§2](#pass-3--childrens-concerts).
* **Target audience: include by default.** The reader decides what is worth going to. The routine decides only what a child could plausibly attend, and it decides that generously. Record `age_min` when the source publishes one and **never use it to drop an event**. An advertised `6+` or `8+` is saved with `age_stretch`. A listing with no age at all is saved as it stands, not skipped. Slovenian listings routinely under-serve the 0–3 band, so absence of an age says nothing.

  Only two things take an event out on audience grounds:
  1. **It says it is not for children.** `18+`, *za odrasle*, *samo za odrasle*, *ni primerno za otroke*, explicit content, licensed-premises nightlife. An explicit statement, not an inference from the topic.
  2. **Nobody would bring a child to it**, whatever age it states or omits. A council session, a professional conference, a job fair, a support group, an adult lecture series, a public consultation. The MOL calendar in particular carries all of these interleaved with real events.

  Everything else goes in, flagged where the fit is doubtful. A longer list the reader skims beats a short one that already made the decision for them.
* **Format:** One-off, scheduled, date-and-time specific events.
* **Time of day:** irrelevant. Never filter, flag or downgrade an event because of when it starts. Record `start_time` and let the reader judge.
* **Time window:** `now` to `now + 3 months`, and no further. This is a hard ceiling on both the searches and what gets written to `db.json`. Listings that publish a whole season at once (theatre repertoires, festival programmes, race calendars) routinely reach six or twelve months out. Take only the part that falls inside the window.

### 🎯 Target Categories
Record the matching value in the event's `category` field.

| `category` | What it covers |
|---|---|
| `lutke` | Puppet and theatre shows for young audiences (Ljubljana only) |
| `pravljice` | Storytelling hours, *ure pravljic*, *kamišibaj* (Ljubljana only) |
| `kino` | Children's screenings, plus free open-air cinema |
| `delavnica` | Museum, gallery and library workshops (Ljubljana only) |
| `sport` | Sports events, movement sessions, sport festivals |
| `tek` | Children's and family runs, *otroški tek*, *družinski tek* |
| `kolo` | Balance-bike races, KoloPark, pumptrack events |
| `ples` | Dance performances and one-off dance workshops |
| `koncert` | Children's concerts and family music events, whether found generically or through the watchlist in [`artists.md`](artists.md) |
| `odprta_vrata` | Open-door days, free trials of otherwise-paid activities |
| `zoo` | Zoo and nature-conservation events |
| `festival` | Family and children's festivals, seasonal city programs, and free-entry days/weeks at museums, galleries and memorial houses |
| `pop_up` | Shopping-centre stages, street pop-ups, market events |
| `avto_moto` | Veteran and youngtimer car/motorbike meetups, Tomos moped gatherings, car and moto shows |

### ❌ Strict Exclusion Rules (Do Not Scrape/Save)
1. **Recurring Courses & Subscriptions:** Any multi-week course, semester enrollment, or subscription program.
   * *Keywords to exclude:* `tečaj`, `vpisi`, `vpis`, `celoletno`, `semestralno`, `abonma`, `semeštrij`.
   * **Single-ticket carve-out.** Keep a dated show that belongs to a subscription series when its ticket is also sold on its own. Kino Bežigrad is the worked example: every show is filed under *Gledališki abonma* and the page says *predstava je del abonmaja*, yet each one is a dated one-off with a single ticket at 8,10 €. Sell-the-series is the venue's framing, not the thing on offer. Save the show, drop the `ABONMA 2026/2027` enrollment page. The test is the same one as rule 2: is there a dated thing you can buy one seat for, or only a season you have to join?
   * **Open-door carve-out.** Keep an item despite these keywords when it has a concrete date **and** a start time **and** a free-trial marker: `dan odprtih vrat`, `dnevi odprtih vrat`, `brezplačna vadba`, `predstavitvena vadba`, `brezplačno preizkusite`, `preizkusi šport`. Clubs advertise their free sessions on the same page that pushes enrollment, so a naive keyword match would throw away the entire `odprta_vrata` category. Save the session, drop the enrollment.
2. **Normal opening hours, not the venue:** Exclude the *visit*, never the *venue*. What disqualifies an item is that it is the place simply being open, with nothing scheduled: general play cafe hours, a standard indoor playground session, regular zoo hours, a permanent museum exhibition.
   * **Any venue qualifies when it hosts a real event.** A play cafe, trampoline park, shopping centre, indoor playground or commercial attraction is in scope the moment it runs something dated and distinct from its ordinary operation. A puppet show at a play cafe, a themed night at a trampoline park, a Saturday workshop at a climbing gym. Commercial ownership is not a reason to skip it.
   * **The test:** would this still be happening if nobody had scheduled it? If yes, it is opening hours. If no, it is an event.
   * A scheduled event counts even when it costs nothing beyond the normal entrance ticket, which is how most zoo and museum events work.
   * **The attendance test, a second filter that only applies to childcare and school sources.** The reader has to be able to come along. A kindergarten's swimming course, field trip or farm stay is scheduled, dated and distinct from ordinary operation, so the first test passes it, and it is still useless here: the child goes as part of the day and the parent stays home. Save an item from a kindergarten or school only when a parent and child attend **together**, and normally outside regular hours. Open days, family evenings, weekend fairs and public performances qualify. The daytime programme does not, however well it is described.
3. **Multi-day paid camps:** Holiday care, *počitniško varstvo*, and week-long camps. These are the subscription pattern in a different wrapper.
4. **Past Events:** Reject past candidates relative to the captured run clock. For `time_unknown`, compare the local date, retaining today's events through the day. Existing expired records are retained with `status: expired`, never deleted.
5. **Beyond the horizon:** Any event whose `start_time` is later than `now + 3 months`. Do not save it, do not list it. Annual fixtures further out belong in [`annual.md`](annual.md), not in `db.json`. They get picked up on a later run once they enter the window.

### ⚠️ Flags (save, but annotate)
Set `flags` on the event rather than dropping it:
* `age_stretch` — advertised `age_min` is 5 or above but the format is plausibly drop-in.
* `outside_ljubljana` — found in Pass 2.
* `travel` — more than roughly 45 minutes from the city centre.
* `not_toddler_appropriate`: billed for children, but plainly not for the 0-4 band because it is loud, frightening or physically demanding. Save it flagged. Time of day alone never triggers this flag.
* `time_unknown`: the date is confirmed but the source publishes no start time. Store local midnight with the correct offset and this flag. The calendar shows `?`, not a fictional midnight. Never invent a plausible time. Some venues keep the time inside a booking widget the sweep cannot read.


---

## 2. Search Queries & Target Sources

**URLs live in [`links.md`](links.md)**, a flat status-checked index with a do-not-retry block.
**Context lives in [`sources.md`](sources.md)**: cadence, age fit, scraping notes and a
month-by-month table of annual fixtures. Read `links.md` on every run and reach for a search
engine only when neither file covers what you need. The queries below are the minimum sweep.

### Language and locale

Applies to every pass, not just Pass 3. These are local events organised by Slovenian
institutions for a Slovenian audience, and the English-language web barely knows they exist.

* **Query in Slovenian. Always.** Never translate a query into English, and never run an English
  query as a fallback when a Slovenian one comes back thin. `kids events Ljubljana` returns
  tourist copy and listicles. `dogodki za otroke Ljubljana ta vikend` returns dated listings. An
  English query for a Slovenian local event is close to a wasted request.
* **Use Slovenian month and time words** in dated queries: `oktober`, `november`, `ta vikend`,
  `ta konec tedna`, `prireditve`. Not `October`, not `this weekend`.
* **Anchor the locale when results drift international.** Add `site:.si`, or a town name, to a
  query that comes back with foreign results. The search tool is US-region and will happily
  return an American event for a Slovenian-looking query.
* **Prefer the Slovenian version of a bilingual site.** `/sl/` over `/en/`, `.si` over `.com`
  where both exist. The Slovenian page carries the full programme. The English page is usually a
  reduced tourist subset, and sometimes a stale copy that was never updated.
  * One known exception is already recorded in `links.md`: `postojnska-jama.eu` 404s on the
    Slovenian path for the nativity scenes and answers on the English one. When the Slovenian
    page is genuinely dead, take the English one and note it. The rule is a preference, not a
    prohibition.
* **Diacritics.** Keep `č`, `š` and `ž` in the query. If it returns nothing, retry once without
  them, because Slovenian sites are inconsistent about stripping them from slugs and titles.
* **Save what was published.** Titles, venue names and price text go into `db.json` in Slovenian,
  exactly as the source wrote them. Never translate a title on the way in. This rule is about
  queries and sources. [Output structure](../docs/output-format.md) is owned by scripts.

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

### Pass 2: rest of Slovenia (destination value)
```
otroški tek Slovenija koledar prireditev
družinski tek Slovenija
pumptrack tekma otroci Slovenija
dan odprtih vrat športni klub otroci Slovenija
brezplačna vadba za otroke Slovenija
plesna prireditev za otroke Slovenija
brezplačen letni kino Slovenija
družinski festival Slovenija brezplačno
živalski vrt prireditev za otroke Slovenija
```

### Pass 3 — children's concerts

Two sweeps, in this order. 3A finds the concerts the routine would otherwise miss entirely, 3B
looks for nine named performers the household actually wants to see. Run 3A first and run it
every time, because the generic sweep is what keeps the category honest in the many weeks when
none of the nine has a date. Everything found in either sweep gets `category: koncert`.

**Geography carve-out.** Pass 2's destination-value test does not apply to 3B. A watchlist artist
is worth the trip on their own, anywhere in Slovenia, which is the entire point of naming them.
Still set `city` and `outside_ljubljana`, and still set `travel` past roughly 45 minutes, so the
reader can see what the trip costs. 3A keeps the normal Pass 1 and Pass 2 rules.

#### 3A — generic free concerts for children

Free first, paid second. A children's concert is far more often a free stage at a town
celebration, a shopping centre or a library than a ticketed hall, and the free ones never reach a
ticket seller.

```
brezplačen koncert za otroke Ljubljana
otroški koncert Ljubljana
glasbena predstava za otroke Ljubljana
koncert za najmlajše prost vstop
otroške pesmi koncert Slovenija brezplačno
družinski koncert prost vstop
pravljični koncert za otroke
glasbena urica za malčke Ljubljana
```

Run each of those undated, then re-run the top four with a month anchor appended for every month
in the horizon (`<mesec> <leto>`). Undated queries skew hard
towards evergreen pages, listicles and last year's edition.

Then sweep `napovednik.com/glasba` with its `narodnozabavna`, `sansoni-kantavtorstvo` and
`klasicna` sub-categories, and re-read the Pass 1 aggregators for anything musical. The addresses
are in [`artists.md`](artists.md) under *Where a date is likely to be confirmable*.

#### 3B — the named artists

**Search first, pages second.** This inverts Passes 1 and 2, and it is deliberate. A puppet
theatre has a calendar. A Čuki booking is a town square in Grosuplje, a shopping-centre stage or
a firefighters' fundraiser, and no venue list will ever hold it, because the organiser is a
municipality or a local society rather than a venue. For this pass the query is the discovery
mechanism and the pages below are how you confirm what a query turns up.

Run a **dated** query per artist per month across the horizon rather than one undated query per
artist. Slovenian month names, because the listings are Slovenian:

```
<ime> koncert <mesec> <leto>
<ime> nastop <mesec> <leto>
```

Then open the pages below, but only for the names a query actually put on the board, to pin down
the venue, the start time and the price. Read [`artists.md`](artists.md) first: it holds the
verified links and the confirmation rule.

| Artist | Confirm at |
|---|---|
| Čuki | Instagram and Facebook. The website is dead, do not retry it |
| Otroški pevski zbor RTV Slovenija | The RTV choir page |
| Romana Krajnčan | Own site and two Facebook pages |
| Neca Falk | Facebook |
| Alenka Kolman | Own site |
| Adi Smolar | Facebook and Instagram |
| Ribič Pepe | Own site and Facebook |
| Dejan Dogaja | The organiser's event page. His own site lists no dates, Facebook and Instagram are leads only |
| Vila Eksena | The organiser's event page. Her own site is a booking brochure with no calendar, Facebook is a lead only |

**Price never gates a 3B save.** For all nine artists, save every confirmed appearance, free
and paid alike, ticketed halls included. The reader decides whether to go, so record the price
text exactly as the source states it and set `is_free` only when entry is free for everyone.
Free is a label on the event, not a condition for saving it.

**Dejan Dogaja and Vila Eksena.** Both are hired by municipalities, libraries and festivals, so
their appearances are listed by the organiser and never on their own sites. The free ones are
municipal stages and library summer programmes, the paid ones are ticketed festivals and
children's carnivals. Query each name every month with `<ime> vstop prost <mesec> <leto>` as
well as the two templates above, so the free stages are not buried under ticket sellers, then
confirm on the organiser's own page. An entry that is free only for small children (the *Poli
žur* pattern, under 4 free and capped at three children) is a paid event, so keep `is_free`
false and put the rule in `price_text`. Dejan Dogaja's band also plays adult functions
(weddings, *gasilske veselice*, late-night parties). Save only a listing that names a
children's or family programme, and skip the rest under §1.

**What the search tool actually returns.** It is US-region and Slovenian local results come back
thin and noisy. Measured on the 2026-09-22 research pass: the top "official" hit for Čuki was
`cuki.si`, a domain with no DNS record at all. A plain *Alenka Kolman* search returned mostly
pages about Alenka Godec, a different singer. Budget for that rate. Apply the *Language and
locale* rules above, prefer a result carrying a date and an address over one carrying a
biography, and never promote a search snippet to an event without opening the page behind it.

**The confirmation rule.** A social post is a lead, not an event. Confirm the date against a
non-social source before saving, put the confirming URL in `url` rather than the social one, and
when nothing confirms it, list it under *Unconfirmed leads* in `diff.md` instead of saving it.
This applies the evidence requirement to sources that often omit the year or venue.

**Facebook and Instagram do not answer a plain fetch.** Facebook returns 400 on most page paths
and Instagram returns an empty 200 behind a login wall. Neither status code means the page is
dead, and neither ever justifies a *Do not retry* row. Reach the content through
`site:facebook.com` and `site:instagram.com` searches instead. Never sign in, never request to
join a group, never post.

### Pass 4 — free entry to museums, galleries and memorial houses

A permanent exhibition is normally excluded under §1 rule 2 as ordinary opening hours. A
**free-entry day or week to that same exhibition is the exception**: it is dated, it is
distinct from the venue's normal (paid) operation, and it disappears again when the promotion
ends, so it passes the rule 2 test the same way an open-door club session does. Save it, tagged
`festival`, with `is_free: true` and the promotion's date range folded into `price_text` since
the schema has no separate end-date field (see `ng_20261006_0000` for the worked example: a
week-long free viewing of the Narodna galerija permanent collection).

This covers museums, galleries, castles, and the memorial or birth houses of notable Slovenians
(*rojstna hiša*, *spominska hiša*, *domačija*) — Prešernova hiša, Cankarjeva rojstna hiša and
similar are typically outside Ljubljana, so apply Pass 2's geography rules: set `city`,
`outside_ljubljana`, and `travel` when the visit is worth more than roughly 45 minutes.

```
brezplačen vstop muzej
brezplačen vstop galerija
ogledate brezplačno
brez vstopnine muzej
zastonj vstop muzej
teden brezplačnega vstopa muzeji
dan odprtih vrat muzej brezplačno
rojstna hiša brezplačen vstop
spominska hiša brezplačen vstop
```

Run each undated first, then re-run the top three with a month anchor for every month in the
horizon, the same pattern as 3A. A one-day promotion tied to a fixed nationwide date (*Ta veseli
dan kulture*, 12-03) is already a fixture in [`annual.md`](annual.md) and does not need a query
once its window opens. Only search for it to confirm the current year's programme. A multi-day
or venue-specific promotion, the Narodna galerija week among them, is what this pass exists to
catch, because nothing else in this file looks for it.

#### Named campaigns checked every run

Three nationwide campaigns are checked by name on every run while their window is inside the
horizon, because each one turns dozens of museums free at once. The fixture rows are in
[`annual.md`](annual.md). This table is the check.

| Campaign | Window | Where it is announced | What to save |
|---|---|---|---|
| **Za družine brezplačno** (Teden družin) | 05-15 to 05-22 every year. Run by Zveza prijateljev mladine Slovenije (ZPMS), 27th year in 2026 | `zpms.si` news post plus a PDF list of 46 to 47 museums and galleries, with each one's free day or week | One event per institution, with its free days folded into `price_text` |
| **Mednarodni dan muzejev** | 05-18, which always falls inside Teden družin | The participating museums' own sites, `sms-muzeji.si` | Only a museum that is not already saved for Teden družin, otherwise extend that event's `price_text` |
| **Poletna muzejska noč** | Third Saturday of June, 18:00 to 24:00. 24th edition 2026-06-20 | `sms-muzeji.si`, then each museum's own page | One event per museum or programme the household could attend |

* **Noč muzejev is this campaign.** In Slovenia the nationwide museum night is *Poletna muzejska
  noč*, and press sometimes calls it *Muzejska noč*. A search for *Noč muzejev* returns the French
  *Nuit des musées* (23 May 2026) first, so add `Slovenija` or `Skupnost muzejev Slovenije` to the
  query and ignore Île-de-France results. Checked 2026-10-05, no separate nationwide Slovenian
  event under that exact name was found. A single museum that advertises its own *Noč muzejev* is
  an ordinary Pass 4 candidate.
* **Not published yet is not a miss.** The 2026 Teden družin list appeared on 2026-05-12, three
  days before it started. While the window is inside the horizon but the list is missing, record
  a lead (title, `zpms.si`, "list of institutions not yet published") and check again next run.
  Never build event rows from last year's list. Institutions change every year.
* **Free means free for the family.** Teden družin and the museum night open admission to
  everyone, so `is_free: true`. An institution that discounts or only offers a free guided hour
  is not free entry, so keep the exact wording in `price_text`.
* **Queries.** `Za družine brezplačno <leto>`, `Teden družin <leto> brezplačen vstop muzej`,
  `Mednarodni dan muzejev <leto> brezplačen vstop`, `Poletna muzejska noč <leto> program`.
  Add the city or region for a Ljubljana or regional sweep. Ljubljana's MGML locations
  (Mestni muzej, Arheopark Emona, Plečnikova hiša) join both campaigns every year.

Apply the same confirmation rule as 3B: a free-entry promotion is often announced first on a
venue's Facebook page, so confirm the dates against the venue's own site before saving, and put
that URL in `url`.

### Pass 5 - veteran car and motorbike meetups (avto-moto)

Added at the reader's request, their child is excited by cars and motorbikes. Runs Slovenia-wide
with no destination-value filter. Pass 2's "worth the trip on its own" test does not apply here,
the category exists specifically so a small child can go and look at old cars and motorbikes up
close, which is the whole point regardless of distance. Still set `city`, `outside_ljubljana` and
`travel` as usual so the reader can see what the trip costs.

These are owners'-club meetings, attended here as a **visitor**, not as a participant bringing a
vehicle. The household checks the price itself, so do not gate a save on confirming `is_free`.
Save the event, record whatever price text the source publishes (it is usually the participant's
rally fee, not a spectator charge), and let the reader judge.

```
srečanje starodobnikov <mesec> <leto>
starodobna vozila srečanje Slovenija
motoristično srečanje starodobniki Slovenija
Tomos srečanje mopedi
youngtimer srečanje Slovenija
oldtimer rally Slovenija <mesec> <leto>
```

Read the SVAMZ full-year calendar before searching, it is the single best-structured source and it
already spans the whole year: `https://svamz.com/koledar-dogodkov/`. Fetch recipe in
[`links.md`](links.md), the parsed 2026 calendar and the closest-in fixtures in
[`regions.md`](regions.md) under *Avto-moto*, including the town-anchored queries for Ljubljana,
Portorož, Koper, Izola, Bled and Kranjska Gora.

### Priority sources
* **Aggregators:** `napovednik.com/za-otroke`, Visit Ljubljana events (filter *Prost vstop* + *Za družine*), `dogodki.kulturnik.si/?what=otroci`
* **MOL calendar, every run, fetched with curl:** `curl -sL 'https://www.ljubljana.si/sl/aktualno/dogodki?nrOfItems=100'`. Never the default view, which returns 20 of 54 and paginates. Never the `cat=124` Otroci filter, which returns zero. Sweep the whole list and apply the target-audience rule in §1. Full recipe in [`links.md`](links.md).
* **Ljubljana venues:** LGL, MKL, Kinodvor Kinobalon, Kino Bežigrad (*Predstave in delavnice*), Mala ulica, MGML, Narodna galerija, SEM, MAO, Cankarjev dom, Ljubljanski grad, ZOO Ljubljana
* **Free entry (Pass 4):** the venues above plus `sms-muzeji.si` (Museums of Slovenia, the nationwide aggregator behind *Poletna muzejska noč*), `zpms.si` (the *Za družine brezplačno* list) and any *rojstna hiša* / *spominska hiša* a query turns up
* **Sport and movement:** Argeta Junior KoloPark Pokal, Pumpaj Slovenija, Ljubljanski festival športa, MOL *Gremo na brezplačne vadbe*, Šport Ljubljana, Dan slovenskega športa
* **Runs:** `tekaskeprireditve.si` (Otroški tek and Družinski tek categories), `tekaski-koledar.si`, Lumpi tek
* **Pop-ups:** Citypark, ALEJA, Supernova, BTC. Published as news posts a week ahead at most, so sweep weekly
* **Avto-moto:** SVAMZ full-year calendar (`svamz.com/koledar-dogodkov`), Zveza SVS news (`zveza-svs.si/obvestila`). Fixtures and the recurrence pattern in [`regions.md`](regions.md)

### Seasonal checks
Run the matching query when the month comes round. The full table is in `sources.md`:
Bobri (Jan–Apr) · Za družine brezplačno and Mednarodni dan muzejev (15 to 22 May) · Igraj se z mano (May) · Poletna muzejska noč (June) · Ana Desetnica (late June) ·
Trnfest and free open-air cinema (Aug) · Čarobni dan (late Aug) · Ljubljanski festival športa,
Otroški bazar, Pikin festival, Dan slovenskega športa (Sep) · Lumpi tek and ZOO Noč čarovnic (Oct) ·
Veseli december (Dec)


---
