# Artist Watchlist — Children's Concerts

The named performers the Pass 3B sweep checks one by one, after the generic free-concert sweep
in Pass 3A has run. `routine.md` §2 defines the two sweeps. This file is the addresses and the
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
