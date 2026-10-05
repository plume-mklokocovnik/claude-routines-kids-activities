# Artist Watchlist — Children's Concerts

The named performers the Pass 3B sweep checks one by one, after the generic free-concert sweep
in Pass 3A has run. [discovery.md](discovery.md) §2 defines the two sweeps. This file is the addresses and the
failure modes.

**Verified:** 2026-09-22. Every non-social URL below was status-checked with a real HTTP request.
Facebook and Instagram rows were **not** status-checked, for the reason in *Social media reality*
below.

---

## The list

| # | Artist | Official | Facebook | Instagram | Genre / fit |
|---|---|---|---|---|---|
| 1 | **Čuki** | ⛔ `cuki.si` is dead, see below | `facebook.com/profile.php?id=100044442189383` | `instagram.com/skupina_cuki` | Narodnozabavna pop. Huge kids following, plays town festivals and shopping centres |
| 2 | **Otroški pevski zbor RTV Slovenija** | `https://www.rtvslo.si/opz-in-mpz/` | none found | none found | Children's choir, conductor Anka Jazbec. Concerts via RTV and Cankarjev dom |
| 3 | **Romana Krajnčan** | `https://www.romanakr.com/` | `facebook.com/romana.najlepse.pesmi.za.otroke`, `facebook.com/romana.krajncan` | none found | The reference name in Slovenian children's song. Musicals and sung fairy tales |
| 4 | **Neca Falk** | none found. ⛔ `muri-maca.com` (the "Maček Muri in Muca Maca" project's own site) is dead, NXDOMAIN — see below | `facebook.com/singerNecaFalk` | none found | Chanson and children's classics. Occasional album-promo concerts |
| 5 | **Alenka Kolman** | `https://www.alenkakolman.si/` | not confirmed | not confirmed | 80+ recorded children's songs, also organises children's events |
| 6 | **Adi Smolar** | none found | `facebook.com/AdiSmolar` | `instagram.com/adi_smolar_uradna_stran` | Singer-songwriter. Mostly adult venues, some family matinees. Booking `info@studio-gong.si` |
| 7 | **Ribič Pepe** | `https://ribicpepe.si/` | `facebook.com/ribicPepe` | none found | Igor Ribič's TV character, RTV SLO 1 Saturdays. Live shows all year, heaviest in December |
| 8 | **Dejan Dogaja** (Dogaja Band) | `https://dejandogaja.si/`, booking only, no event list | `facebook.com/dejan.krajnc` | `instagram.com/dejan_krajnc` | Dejan Krajnc, ex-frontman of Poskočni muzikanti. A party band with a children's animation programme. Plays pust, summer town festivals and New Year's farewells for children. Also plays adult functions that do not qualify. Booking `info@dejandogaja.si` |
| 9 | **Vila Eksena** | `https://vila-eksena.si/`, booking brochure, no event list | `facebook.com/VilaEksena` (from a search result, not opened) | none found | Singing fairy with superhero characters, songs and dancing, billed for children of all ages. Booked by libraries, municipalities and festivals. Booking `info@vila-eksena.si` |

## Dejan Dogaja and Vila Eksena: where their appearances turn up

**Price never gates a save, for any artist on the list.** Free and paid appearances are both
recorded and the reader decides. Free is only a label (`is_free`).

**Verified:** 2026-10-05, with web searches and fetches of both official sites. Neither site
publishes a calendar, so every date comes from the organiser who booked them. The rows below
are evidence of where their appearances turn up, free and paid, not dates to reuse.

| Appearance seen | Organiser's page | Entry | Pattern to search for |
|---|---|---|---|
| Vila Eksena, *zaključni pravljični koncert*, Park Sonce, Lucija, 2026-08-26 20:00 | `piran.si/dogodek/` and `pir.sik.si/napovednik/` (Mestna knjižnica Piran, project *Lučke v parku Sonce*) | **Free** (*Vstop prost*) | Library and municipal summer programmes, July and August |
| Dejan Dogaja, *Goriško poletje*, Ploščad Silvana Furlana, Nova Gorica, 2026-08-05 19:00 | `dogodki.turizem-novagorica-vipavskadolina.si` | **Free** (*Vstop prost*), cancelled in rain | Municipal summer festivals |
| Dejan Dogaja, *Otroško slovo od starega leta*, Laško courtyard, 2024-12-28 17:00 | `lasko.info/dogodek/` | Price not stated on the page | Late December children's farewells to the year |
| Dejan Dogaja and Vila Eksena, *Poli žur*, Arena Campus Sava Ptuj, 2026-02-12 17:00 | `ptujinfo.com`, `vstopnice.campus.si` | **Paid**, 12 €. Children under 4 free, three per ticket | Pust, early February |
| Both and Čuki, *Veveričkin otroški festival*, ŠRC Polena, Lenart, 2026-06-12 to 06-14 | `ovtar24.si` | **Paid**. Children 1 to 13 need a ticket, accompanying adults enter free | June |
| Dejan Dogaja, *Odisejino otroško pustovanje* (venue and year not recorded) | `ljubljanainfo.com/dogodek/` | **Paid**, 15 € per child. Under 2 free | Pust, February |

* **Where to look.** Municipal and library calendars, regional tourist boards (`piran.si`,
  `obalaplus.si`, `turizem-novagorica-vipavskadolina.si`, `ptujinfo.com`, `lasko.info`,
  `  ljubljanainfo.com`) and the Pass 1 and Pass 2 aggregators. A dated query with `vstop prost`
  surfaces the free ones, the plain name queries surface the ticketed ones. Facebook event
  pages are leads only.
* **Free test.** Entry free for everyone sets `is_free: true`. Free for small children only, or a
  free adult with a paid child, is a paid event. Put the rule in `price_text`.
* **Children's programme only.** Dejan Dogaja's band mostly plays adult functions. Save a listing
  only when it names a children's or family programme.
* **Both are 3B names.** The geography carve-out in [discovery.md](discovery.md) §2 applies. Set
  `city`, `outside_ljubljana` and `travel` so the reader sees the cost of the trip.

## Do not retry

| Dead URL | Failure | Certainty | Use instead |
|---|---|---|---|
| `cuki.si` / `www.cuki.si` | NXDOMAIN, no DNS record. Two curl attempts plus a direct lookup | **Certain.** A domain with no DNS record cannot answer until someone re-registers it | The Instagram and Facebook rows above, plus `napovednik.com/glasba/narodnozabavna` |
| `muri-maca.com` | NXDOMAIN, no DNS record. Checked 2026-09-24 while trying to confirm the Neca Falk "Maček Muri in Muca Maca" lead below | **Certain** | The `eventim.si` listing (Akamai-blocked, unverified) or `drama.si` directly (checked, no date published) — both still unconfirmed as of 2026-09-24 |

## Where a date is likely to be confirmable

Social posts announce. These sources confirm. Sweep them for the artist names before going near
Facebook.

| Source | URL | Status | Why |
|---|---|---|---|
| Napovednik music | `https://napovednik.com/glasba` | ok | Dated national concert calendar |
| → narodnozabavna | `https://napovednik.com/glasba/narodnozabavna` | ok | Čuki and the town-festival circuit |
| → šansoni, kantavtorstvo | `https://napovednik.com/glasba/sansoni-kantavtorstvo` | ok | Adi Smolar, Neca Falk |
| → klasična | `https://napovednik.com/glasba/klasicna` | ok | Choirs, including the RTV ones |
| Napovednik kids events | `https://napovednik.com/za-otroke/prireditve-za-otroke` | ok | Already in the Pass 1 sweep, carries children's concerts |
| Mojekarte | `https://www.mojekarte.si/` | ok | Ticketed dates, searchable by performer |
| Eventim SI | `https://www.eventim.si/artist/<slug>/` | unverified | Has per-artist pages (`/artist/adi-smolar/`), but the site sits behind Akamai and refused both curl and a fetch on this check. Browser only |
| Ribič Pepe on RTV | `https://365.rtvslo.si/oddaja/ribic-pepe/21235734` | ok | Broadcast schedule, sometimes flags live appearances |
| ⚠️ Ribič Pepe own site | `https://ribicpepe.si/` | **stale as of 2026-09-22** | Root now serves only 2017–2018 archived content, `/dogodki/` 404s. Use Facebook (`facebook.com/ribicPepe`) or the RTV broadcast page above instead |
| YouTube — Romana Krajnčan | `https://www.youtube.com/channel/UCPOQn2OBmYMoGV8_wlyRE9A` | ok | Announcements when the site is quiet |
| YouTube — Ribič Pepe | `https://www.youtube.com/@ribicpepe585` | ok | Same |
| YouTube — Alenka Kolman | `https://www.youtube.com/@AlenkaKolman-glasba` | ok | Same |

---

## Social media reality

This matters more than the link list, because the naive approach silently produces nothing.

* **Facebook pages are not fetchable.** A plain request returns HTTP 400 on most page paths and
  an inconsistent 200 on others, with no post content either way. A 400 here means *bot-blocked*,
  not *dead*. Never move a Facebook row to *Do not retry* on the strength of a status code.
* **Instagram returns 200 and no content.** The profile is a JavaScript shell behind a login
  wall. The status code is meaningless.
* **Fan groups are worse.** `facebook.com/groups/<id>` is usually closed. Read what a search
  engine surfaces. Never request to join a group, never sign in, never post.
* **What does work:** a search engine scoped to the domain. `site:facebook.com Čuki koncert
  oktober 2026`, `site:instagram.com skupina_cuki koncert`. Public post text is indexed even
  when the page itself refuses a direct fetch.
* **Public event pages** of the shape `facebook.com/events/<id>` occasionally render enough in a
  fetch to read a date and a venue. Worth one attempt when a search surfaces one.

## The confirmation rule

A social post is a **lead, never an event**. It carries a date and a town and nothing else
reliable, and it is frequently a repost of something from three years ago.

1. Found on Facebook or Instagram → write down the claimed date, town and venue.
2. Confirm it against a non-social source: the venue's own site, the municipal calendar,
   Visit Ljubljana, Napovednik, a ticket seller.
3. **Confirmed** → save it to `db.json` like any other event, with the confirming URL in `url`,
   not the social one.
4. **Not confirmed** → do not save it. List it under *Unconfirmed leads* in `diff.md` with the
   social URL, so the next run knows to look again.

This is `routine.md` §0 *Never invent an event* applied to a source that invites invention. A
Čuki post saying "vidimo se v soboto" is not an event until something with an address says so.
