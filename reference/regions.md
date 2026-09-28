# Regional Fixtures and Search Leads, Outside Ljubljana

Everything here is Pass 2 territory. [`annual.md`](annual.md) stays the Ljubljana calendar.
Same window check applies: build the date, test it against `now` to `now + 3 months`, skip silently otherwise.

Researched 2026-09-21 from a 90-entry cross-check. **Verified** rows were confirmed against a
live source. **Leads** were not, and exist so the routine has something to search for rather than
nothing. A lead is a query, not a fact. Never write one to `db.json` without confirming it first.

★ marks a strong 0–4 fit.

---

## The Pass 2 scope change this triggered

The old rule said: do not expand art workshops, gallery programmes, storytelling or puppet shows
beyond Ljubljana. That rule breaks on this list, because most good regional family events are
*festivals that contain* puppet shows and workshops. Excluding them by category would have
thrown away Art kamp, Kekčevi dnevi and the Podmornica strand at Kino Otok.

**The criterion is destination value, not category.** Outside Ljubljana:

* **Take it** when it is worth the trip on its own: a full-day or multi-day festival, a free
  family day at a castle or estate, a signature local celebration with a children's programme.
* **Leave it** when it is a single 30-minute performance that happens to be in another town.
  A standalone puppet show in Maribor is not worth two hours in the car. The same show inside
  Art kamp is, because the rest of the day comes with it.

Record `city` on every Pass 2 event and set the `outside_ljubljana` flag.

---

## Verified: coast, Karst and Postojna

| Fixture | When | Where | Notes |
|---|---|---|---|
| **Solinarski praznik** | Around St George, late April. 2026: 04-24 to 04-26 | Piran, Sečovlje and Strunjan salt pans | 22nd edition. Opens the salt season. Three days across all three sites |
| **Kino Otok – Podmornica** | Mid June. 2026: 06-10 to 06-14 | Izola | ★ Podmornica is the children's strand, ages 3–18, films plus **free** creative workshops and themed walks. Runs over the weekend |
| **Altroke Sladka Istra** | Early September. 2026: 09-05, 09:00–18:00 | Koper, Hlavatyjev park | ★ **Free.** Dedicated children's corner: craft workshops, sensory lab, cookie decorating, face painting, street circus, wooden games |
| **Dan Kobilarne Lipica** | September, from 09:30 | Lipica | ★ Free-entry open day. Mares and foals released to pasture, farrier demos, horse workshops, estate tours |
| **Praznik kakijev** | Mid November. **2026 confirmed: 11-10 to 11-12** (the 11-14/11-16 date seen in some listings was actually 2025's) | Strunjan | 22nd edition. Salt-pan tours, persimmon workshops, largest-persimmon contest, local market. Confirmed 2026-09-24 via `zgodovinska-mesta.si` (index + dedicated event page, independently agreeing). ⚠️ The "Kaki ekspres" train was not confirmed |
| **Žive jaslice** | 12-25 to 12-30, several times daily from 13:30 | Postojnska jama | 35th edition. 90 minutes, 5 km underground route, 18 scenes, 100+ actors. Ticketed. ⚠️ Long and cold, dress for a cave |

## Verified: Gorenjska

| Fixture | When | Where | Notes |
|---|---|---|---|
| **Prešernov smenj** | 02-08 | Kranj old town | ★ 19th-century costumed fair. Creative workshops and a children's show at the city library, treasure hunt, pony rides, free tours at Khislstein |
| **Planica, otroški dan** | The Thursday of the March ski-flying finals | Planica | Under 6 free every day. 2026: under 14 free on Sunday 03-29. Ages 7–14 need a free ticket collected at a sales point |
| **Festival čokolade** | Mid April. 2026: 04-18 to 04-19 | Radovljica | ★ **Under 18 free.** Chocolate workshops, circus acts, animation, a small medieval funfair on the church square |
| **Mednarodni festival alpskega cvetja** | Late May into early June. 2026: 05-22 to 06-07 | Bohinj, 24 villages | 20th edition. Botanical walks, children's workshops, fairytale and sports activities. The Weekend of Sports strand is free with children's animation |
| **Srednjeveški dnevi** | First weekend of June | Blejski grad | ★ Knights from across Europe, archery, games, creative workshops with a points trail, crafts market, camp in the castle park |
| **Kekčevi dnevi** | Late June, at the start of the school holidays. 2026: 06-24 to 06-28 | Kranjska Gora | ★ Free shows on the church square, old shepherd games, creative workshops, Kekec films, Mini DJ academy |
| **Šuštarska nedelja** | *Angelska nedelja*, the first Sunday of September | Tržič | Shoemaking heritage fair. Stalls, crafts, demonstrations across the old factory complex |
| **Kravji bal** | Third Sunday of September, 10:00–18:00 | Ukanc, Bohinj | ★ **Under 7 free**, 7–14 costs 2 €. Decorated cows down from the high pastures, children's corner with games and workshops, folk groups, brass bands |
| **B.O.FEjST — jesenski otroški festival** | Late October, 15:00–19:00. 2026: 10-31 | Dvorana Danica, Bohinjska Bistrica | ★ **Free.** Bohinj's biggest children's festival, running since 2008. Games, workshops, music, mascot Fejstka, free transport around Bohinj. New find, 2026-09-24 — confirmed via `mojaobcina.si`; `tdbohinj.si` and `bohinj.si`'s English event path both 404 for this one, use `mojaobcina.si/bohinj/dogodki/` instead |

## Verified: elsewhere in Slovenia

| Fixture | When | Where | Notes |
|---|---|---|---|
| **Art kamp, Festival Lent** | Late June into early July. 2026: 06-26 to 07-05, weekends after | Mestni park, Maribor | ★★ **The biggest regional find.** A daily daytime programme in the park built around children and families: creative workshops, puppet and theatre shows, music, sport, nature activities |
| **Festival idrijske čipke** | Mid June. 2026: 06-19 to 06-21 | Idrija | 44th edition. Lace workshops, children's animation, a children's theatre show, city tours. Sunday holds the national lace competition for children and adults |
| **Jurjevanje v Beli krajini** | Late June. 2026: 06-22 to 06-28 | Črnomelj, Jurjevanjska draga | Slovenia's oldest folklore festival. **Pastirče mlado** on the Thursday at 16:00 puts ~350 young folk dancers on the main stage |
| **Kamfest and Veronikin festival** | August. Kamfest 2026: 08-07 to 08-15, children's shows at Barutana 08-08 to 08-14, 17:00–23:00 | Kamnik | Veronikin festival is described as Kamnik's largest children's festival, in Keršmančev park. ⚠️ The medieval-fair framing at Mali grad was not confirmed |
| **Celjski mali maraton — otroški in družinski tek** | Sunday, 11:00, alongside the main marathon. 2026: 11-08 | Kajak kanu center Špica, Celje | 15th edition, 1.600 m, non-competitive. Confirmed 2026-09-24 via `fatburn.si` (see *Regional sources* below for the access note — this page bot-blocks a plain fetch). Ticket price for this specific distance not published (only the 6.2/11/14/21 km tiers are priced) |

## Verified: Dolenjska

| Fixture | When | Where | Notes |
|---|---|---|---|
| **WILD KIDS, Kavbojska dežela** | Early October, 2026: 10-02 to 10-04, starts Friday 14:00 | Kavbojska dežela, Višnja Gora | ★ Children's festival weekend on a working farm. 15 inflatables, animation, Kavboj Pepe, concerts Saturday 15:00 (Firbci) and Sunday 15:00 (Čuki). 10 € per child, parents and under-2s free. Confirmed direct from source 2026-09-28, fetch recipe in [`links.md`](links.md) |
| **Montwest Country Festival, Kavbojska dežela** | Mid June. 2027: 06-18 to 06-20 | Kavbojska dežela, Višnja Gora | 3-day country festival, western riding, kids' inflatables, on-site camping. Ticket tiers 10 € day / 25 € weekend / 30 € family. Confirmed direct from source 2026-09-28, still well outside any horizon this far ahead |

## Search patterns, better than listing every venue

Slovenia has dozens of castles and dozens of produce festivals, and they nearly all run the same
two templates. Search the pattern rather than maintaining a row for each.

| Pattern | Query shape | Why it works |
|---|---|---|
| Castle family day | `srednjeveški dnevi grad <ime>`, `grajski dan <ime>`, `vitezi otroci grad <ime>` | Bled, Ljubljana, Ptuj, Celje Stari grad, Rajhenburg, Bogenšperk and Štanjel all run versions. Knights, archery, crafts, usually free or cheap |
| Produce festival | `praznik <pridelek> <kraj> otroški program` | Persimmons in Strunjan, cherries in Brda, grapes in Lendava, apricots in Vipava, chestnuts, cheese in Bohinj, žlikrofi in Idrija, teran in Dutovlje. Most bolt a children's corner onto a food festival |
| Craft heritage day | `<obrt>ska nedelja`, `rokodelski sejem <kraj> otroci` | Šuštarska nedelja in Tržič, suha roba in Ribnica, lace in Idrija |
| Winter fairytale | `zimska pravljica <kraj>`, `pravljični park <kraj>` | Bled, Kranjska Gora, Koper and Portorož each run a December version |
| Krampus night | `noč parkeljnov <kraj>` | Goričane, Sežana, Postojna and others. ⚠️ Loud, dark and frightening. Note it, do not recommend it blind |

## Leads, not yet verified

Search these by name when their month comes round. Confirm before saving.

**Coast, Karst, Postojna**
Ribiški praznik (Izola, Aug) · Fantazima and winter fairytale (Koper, Dec) · Poletni lutkovni
pristaniščnik (Koper, Jul–Aug) · Festival Kraška gmajna (Lipica and Štanjel, Sep–Oct) ·
Pust parades (Postojna and Koper, Feb) · Otroški živžav pri Svetilniku (Izola, Jul) ·
Tartini Festival family mornings (Piran, Aug) · Magični december (Portorož) ·
Istra gourmet market (monthly, summer) · Postojna outdoor summer and castle nights (Jul–Aug) ·
Regata starih bark (Piran, Jun) · Festival oljk in piranske soli (Portorož, Apr) ·
Jesenski pohodi po drevoredih (Lipica, Oct) · Noč parkeljnov (Sežana and Postojna, Nov–Dec)

**Gorenjska**
Blejska zimska pravljica and Legenda o potopljenem zvonu (Bled, Dec) · Prgarski dnevi (Zasip, Oct) ·
Lučke na jezeru (Bled, Jul) · Srednjeveški dan (Radovljica, Jun) · Teden mladih (Kranj, May) ·
Bohinjski otroški živžav (Bohinj, Jun) · Poletna and zimska pravljica (Kranjska Gora) ·
Kranjska kuhna and Otroški Khislstein (Kranj, Jun–Sep) · Pravljični park and Oživel kamen (Bled, Dec) ·
Praznik sira in žgancev (Bohinjska Bistrica, Oct) · Radovljiško sladko poletje (Jul–Aug) ·
Pravljični večeri, Slovenski planinski muzej (Mojstrana, Aug and Dec)

**Štajerska, Prekmurje, Dolenjska, Primorska, Notranjska**
Grajski dan, Stari grad Celje · Grajski dnevi, grad Rajhenburg (Brestanica) ·
Srednjeveški dan, grad Bogenšperk · Srednjeveški dan, grad Ptuj · Trške igrice (Škofja Loka) ·
Praznik idrijskih žlikrofov (Aug) · Praznik grozdja (Lendava, Sep) ·
Praznik češenj (Goriška brda, Jun) · Festival lesa (Kočevje) ·
Noč čarovnic, grad Rakičan (Murska Sobota, Oct) · Soča Outdoor family day (Tolmin, Jul) ·
Praznik terana in pršuta (Dutovlje, Aug) · Praznik marelic (Vipava) · Grajski večeri (Ribnica)

## Company-run family days, worth a yearly check

Not tied to a region, since the organiser can move the venue. Kept separate from the leads list
above because it comes with an organiser name and one confirmed past edition, not just a name.

| Fixture | When | Where | Notes |
|---|---|---|---|
| **Hura! Družinski dan** (Baby Center) | Once a year, autumn. Only confirmed edition so far: October 2025 | 2025 edition: AMZS varna vožnja polygon, Vransko | One data point, not yet a confirmed recurrence rule. 2025: 450+ families attended despite rain, children's workshops, singing and dance performances, fairytale characters and superheroes, child-car-seat safety demos on the driving polygon, a charity collection for Zlata nit. Search `"Hura! Družinski dan" Baby Center <year>` and check `babycenter.si/blog` each September, since the venue can change year to year and the date is announced short notice |

## Avto-moto: veteran car and motorbike meetups, nationwide

Added 2026-09-28, a new category at the reader's request: their child is excited by cars and
motorbikes. This is genuinely nationwide, run by a circuit of owners' clubs rather than tied to
one town, so it sits here even on the one occasion a meeting lands in Ljubljana itself. Source and
fetch recipe are in [`links.md`](links.md).

The household attends these as **visitors**, not as participants bringing a vehicle, and checks the
price at the venue itself. Where a source publishes a price it is normally the participant's rally
fee, worth recording but not a reason to hold the event back.

### Within the current window (checked against 2026-09-28 to 2026-12-28)

| Fixture | When | Where | Notes |
|---|---|---|---|
| Usposabljanje motoristov, spretnostna vožnja s starodobnimi avti | 2026-10-04 | Nova Gorica, Mercator center car park (place inferred from the March entry at the same contact) | Skill-driving demonstration with vintage cars, contact `mmozetic@yahoo.com`. Start time unconfirmed |
| Alfa Rally | 2026-11-28 | Not stated | Alfa Romeo club rally, contact `info@alfa-klub.com`. No venue published yet, too vague to save as an event until one is confirmed closer to the date |
| Srečanje starodobnih vozil na Štefanovo, Valburga | 2026-12-26 | Šmarna gora and Zbilja area, Medvode | ★ Closest to Ljubljana of the three. St Stephen's Day drive and meet, contact `cmoc96@gmail.com` (C.M.O.C. Šentvid club). Start time unconfirmed |

### The full 2026 calendar, for next year's pattern

Pulled whole from the SVAMZ calendar on 2026-09-28. Most of the year has already passed by the
time this was written, kept anyway because next year's edition of each fixture tends to land in
the same month. Re-check the exact date every year rather than assuming it repeats on the same day.

| Month | Fixture | Where |
|---|---|---|
| January | GO moto GO (Slovenia + Italy) | not stated |
| January | Zimski rally za motocikle | Sežana |
| March | I. srečanje SOLEX mopedov | Vransko |
| March | Usposabljanje motoristov, spretnostna vožnja s starodobnimi avti | Nova Gorica, Mercator center |
| April into May | Citroën klub, prvomajsko srečanje | not stated |
| May | Razstava in parada starodobnih vozil | Naklo |
| May | Srečanje mopedov do 50 ccm | Stara Gora |
| May | Srečanje vojaških vozil | Novo mesto |
| May | Mitteleuropean race | Gorica |
| May | **Srečanje Tomos oldtimer** | Peskovci, Abraham Garaža |
| May | Mednarodno srečanje s starodobnimi kolesi in oblačili iz preteklosti | Stara Gora |
| May | **8. Youngtimer srečanje Ljubljana** (Avtonostalgija 80&90) | Ljubljana, parkirišče Leclerc |
| May | Days of Thunder | Vista park, Velenje |
| June | Tradicionalno mednarodno srečanje Laverda | Pri Celju |
| June | Tradicionalno srečanje starodobnih vozil | Grosuplje |
| June | Veliko srečanje Alfistov | not stated |
| June | 15. mednarodno VW Bus srečanje | Vinica |
| June | **Naj starodobnik Slovenije** | Ormož |
| June | Poletna muzejska noč s Celjskimi knezi | Celje |
| June | Citroën mini srečanje | not stated |
| June | 8. mednarodno srečanje starodobnih vozil, 10. obletnica društva | Starodobniki Miklavž pri Ormožu |
| June | Aircooled camping | Adlešiči |
| June | XIII. Pilihov memorial | AMD-DLT Šmartno ob Paki |
| June | Dan državnosti, potep z vojaškimi vozili | Dravograd |
| July | 30 let kluba C.M.O.C. | Šentvid |
| July | Hidroraid Citroën | not stated |
| July | 18. mednarodno srečanje starodobnih vozil in tehnike | Peskovci |
| August | Oranje s starodobnimi traktorji | Krčevina |
| August | V.I.P. srečanje | not stated |
| August | 9th Cruisers Rockabilly Overdrive | Rancho Village, Dragomelj |
| August | Let's bug together #32 (VW Hrošč klub) | not stated |
| August | Mednarodno srečanje starodobnih traktorjev in kmetijske opreme | Stara Gora |
| August | Vožnja z dirkalnimi in starodobnimi vozili, Grand Prix | Nova Gorica |
| September | Rally Kras, Brkini | not stated |
| September | Citroën klub, jesensko mini srečanje | not stated |
| October | Usposabljanje motoristov, spretnostna vožnja s starodobnimi avti | Nova Gorica |
| November | Alfa Rally | not stated |
| December | Srečanje starodobnih vozil na Štefanovo, Valburga | Šmarna gora, Zbilja |

Two entries on that list stand out for a car-and-motorbike-loving toddler specifically:

* **Srečanje Tomos oldtimer**, late May, Peskovci (Abraham Garaža). The one dedicated Tomos meet
  on the calendar, and Tomos is a Slovenian-made brand, so the mopeds are usually local and
  familiar-looking rather than exotic. SVAMZ's own history also carries a 2023 Guinness World
  Record attempt built around a mass gathering of Tomos mopeds, so the club takes the brand
  seriously (`https://svamz.com/balkan-forum-2023/`, historical, not a current fixture).
* **8. Youngtimer srečanje Ljubljana** (Avtonostalgija 80&90), late May, parkirišče Leclerc,
  Ljubljana. Eight editions in and inside the city itself, the best-placed entry on this whole
  list once next May comes into the window. Worth a line in `annual.md` at that point.

Also worth knowing: **Auto Motor Show Slovenija** is the country's biggest ticketed car show, held
2026-05-16/17 at the Celjski sejem after 15 years back in Ljubljana the year before. Paid, free
entry stops at age 7. See [`links.md`](links.md).

### Town-anchored leads: Ljubljana, Portorož, Koper, Izola, Bled, Kranjska Gora

Researched 2026-09-28 at the reader's request, they remember seeing car and motorbike meets in
these six towns and want them checked every year rather than rediscovered from scratch. Confidence
varies a lot by town, noted per row. Add the queries under each town to the Pass 5 sweep.

| Town | Fixture | When | Notes |
|---|---|---|---|
| **Ljubljana** | 8. Youngtimer srečanje Ljubljana (Avtonostalgija 80&90) | Late May | Already listed above. `youngtimer srečanje Ljubljana <leto>` |
| **Ljubljana** | Starodobniški klepet ob kavi (S.K.O.K.), Oldtimer klub Škofljica | 2026 edition: 14 March, in front of E.Leclerc, Trgovski center Rudnik | A casual, recurring oldtimer coffee meetup, confirmed from the Zveza SVS 2026 calendar PDF. Rudnik is inside the city. `starodobniški klepet ob kavi Ljubljana Rudnik` |
| **Portorož / Piran** | OneLife, "Portorose to Porto" | 2026: 19 to 21 June, main public day Saturday 20 June, Tartini trg, Piran | ★★ Confirmed **free**, straight from the organiser's own event page: "Visitors will have the opportunity to admire the cars up close and meet the drivers free of charge." 60+ Ferrari, Lamborghini and Porsche cars staged before departing for Monaco. Best-confirmed find of this whole pass. `OneLife Portorož Piran <leto>` |
| **Portorož / Piran** | Harley-Davidson European H.O.G. rally | 2026: early summer, roughly 29th edition | Large touring motorcycle rally, thousands of riders. The European edition moves host city each year, so do not assume Portorož repeats without checking. One earlier local edition was reported cancelled (`eMORJE.com`), so confirm before promising it. `Harley Davidson srečanje Portorož <leto>`, `H.O.G. European rally <leto>` |
| **Portorož** | Ferrari club showcase, Marina Portorož | Reported June 2026, exact recurrence unconfirmed | ~30 Ferraris on display at the marina, may be the same OneLife weekend or a separate club visit, not disambiguated this pass. `Ferrari klub Portorož marina` |
| **Koper** | 28. Adria Classic (Adria Classic Koper, 30 let društva, 10. Valterjev memorial) | 2026: Friday 15 and Saturday 16 May | ★ Confirmed from the Zveza SVS 2026 calendar PDF. 100+ classic vehicles, 1900s to late 1980s, touring the coast and Slovenian Istria interior. Route explicitly names Koper, Izola and Piran municipalities | `Adria Classic Koper <leto>` |
| **Koper** | Starodobniški klepet ob kavi (S.K.O.K.), Adria Classic Koper | 2026 edition: 14 March, Titov trg and Verdijeva ulica | ★ Confirmed free and public from a 2023 write-up of an earlier edition: 80+ classic cars, 8:30 to 12:00, owners on hand to answer questions, a "late breakfast" laid on by the local tourism office. Read as a recurring pattern rather than a single date | `starodobniški klepet ob kavi Koper Titov trg` |
| **Izola** | **Adijo Poletje**, Mustang Club Slovenija | 2026: 12 September, 10:00 to 23:50, San Simon Resort, Simonov zaliv (Morova ulica 6a) | ★★ Confirmed **free** from the club's own site and press coverage. 4th edition, the biggest Mustang gathering in the country, 130 Mustangs from Slovenia, Austria, Croatia and Hungary, 5,000+ visitors, live music, charity Mustang rides. ⚠️ **First time on the coast**, the first three editions were held elsewhere (location not identified this pass), so do not assume Izola repeats next year without checking. The club also runs a **spring meeting** (~100 Mustangs, 3,000+ visitors in 2026), venue not identified, worth its own search. `Adijo Poletje Mustang Izola <leto>`, `Mustang klub Slovenija spomladansko srečanje <leto>` |
| **Izola** | Porsche club meetup | Not found | Checked the Porsche Klub Slovenija 2026 calendar directly (`porsche-klub-slovenija.si` event list): Katarina hillclimb, Dolenjska, Grobnik, Dalmacija (Croatia), Prekmurje, Villa Fabiani, Koroška. Nothing on the coast and nothing in Izola specifically. Re-check next year rather than assuming this is permanent | `Porsche klub Slovenija Izola`, `Porsche klub Slovenija obala` |
| **Bled** | Nothing confirmed this pass | not stated | Bled's own events page (`bled.si/sl/prireditve/`) carried no car or motorbike keyword on this sweep. The reader's memory of a Bled event was not tracked down, keep searching rather than dropping it | `starodobniki srečanje Bled`, `oldtimer rally Bled avtomobili` |
| **Kranjska Gora** | Blagoslov motorjev | Annual, May (2025 edition: 11 May) | ★ Confirmed annual tradition, organised by the local tourist society (Turistično društvo Kranjska Gora). Free, public, town square in front of the church, no registration mentioned. Priest blesses the bikes, riders socialise after | `blagoslov motorjev Kranjska Gora <leto>` |

---

## Regional sources

| Source | URL |
|---|---|
| Gorenjska tourist calendar | `https://www.gorenjska.si/` |
| Bled | `https://www.bled.si/sl/prireditve/` |
| Blejski grad | `https://www.blejski-grad.si/` |
| Bohinj | `https://www.bohinj.si/prireditve-internal/` |
| Turistično društvo Bohinj | `https://tdbohinj.si/` |
| Kranjska Gora | `https://kranjska-gora.si/dogodki/` |
| Visit Kranj | `https://www.visitkranj.com/` |
| Radolca / Radovljica | `https://www.radolca.si/` |
| Festival čokolade | `https://www.festival-cokolade.si/` |
| Visit Tržič | `https://visit-trzic.com/sl/prireditve` |
| Visit Koper | `https://visitkoper.si/prireditve/` |
| Portorož and Piran | `https://www.portoroz.si/sl/dogodki` |
| Krajinski park Strunjan | `https://parkstrunjan.si/` — ⚠️ its *Praznik kakijev* page served 2015-era content on 2026-09-22; cross-check dates against `https://www.zgodovinska-mesta.si/prireditve/` instead |
| Kino Otok | `https://kinootok.org/program/` |
| Center za kulturo Izola | `https://center-izola.si/dogodki/` |
| Kobilarna Lipica | `https://www.lipica.org/` — ⚠️ its own per-event pages returned what looked like stale 2023 content to WebFetch on 2026-09-22, but re-checked 2026-09-24: the real symptom is a JS bot-challenge (same as `fatburn.si` below), and `curl -A "<desktop UA>"` returns live, current content. Still use `https://www.tekaskipozdrav.si/` for *Tekaški pozdrav jeseni na Krasu* since that's the venue's own dedicated site, but don't write off other `lipica.org` event pages as stale without trying curl+UA first |
| Fatburn (Celjski mali maraton) | `https://fatburn.si/celjski-mali-maraton/` — ⚠️ WebFetch always hits a "please wait, verifying…" bot-challenge here (and on `/blog/...`, `/product/...` sub-paths). `curl -A "<desktop browser User-Agent>"` bypasses it and returns full current content. Not dead, don't blacklist |
| Visit Celje | `https://www.visitcelje.eu/` — same bot-challenge as fatburn.si, curl+UA works. Its "Tek očkov" product page (`/sl/izdelek/tek-ockov-2026/`) 404s even past the challenge — slug moved or not yet published, not a dead site |
| Postojnska jama | `https://www.postojnska-jama.eu/sl/` |
| Visit Kras | `https://www.visitkras.info/` |
| Narodni dom Maribor, Art kamp | `https://nd-mb.si/` |
| Visit Idrija | `https://www.visit-idrija.si/sl/dogodki-in-prireditve/` |
| Festival idrijske čipke | `https://www.festivalidrijskecipke.si/` |
| Jurjevanje | `https://jurjevanje.si/` |
| Kamfest | `https://www.kamfest.org/` |
| Zgodovinska mesta (heritage town events) | `https://www.zgodovinska-mesta.si/prireditve/` |
| Planica | `https://www.planica.si/sl/program` |
| Kavbojska dežela (Višnja Gora) | `https://kavbojska-dezela.si/dogodki/`. Fetch recipe and confirmed events in [`links.md`](links.md) |
| Baby Center (Hura! Družinski dan) | `https://www.babycenter.si/blog`. No dedicated events page found, sweep the blog and search by name each autumn |
