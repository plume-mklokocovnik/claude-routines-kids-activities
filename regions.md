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
| **Praznik kakijev** | Mid November. 2025: 11-14 to 11-16 | Strunjan | 22nd edition. Salt-pan tours, persimmon workshops, largest-persimmon contest, local market. ⚠️ The "Kaki ekspres" train was not confirmed |
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

## Verified: elsewhere in Slovenia

| Fixture | When | Where | Notes |
|---|---|---|---|
| **Art kamp, Festival Lent** | Late June into early July. 2026: 06-26 to 07-05, weekends after | Mestni park, Maribor | ★★ **The biggest regional find.** A daily daytime programme in the park built around children and families: creative workshops, puppet and theatre shows, music, sport, nature activities |
| **Festival idrijske čipke** | Mid June. 2026: 06-19 to 06-21 | Idrija | 44th edition. Lace workshops, children's animation, a children's theatre show, city tours. Sunday holds the national lace competition for children and adults |
| **Jurjevanje v Beli krajini** | Late June. 2026: 06-22 to 06-28 | Črnomelj, Jurjevanjska draga | Slovenia's oldest folklore festival. **Pastirče mlado** on the Thursday at 16:00 puts ~350 young folk dancers on the main stage |
| **Kamfest and Veronikin festival** | August. Kamfest 2026: 08-07 to 08-15, children's shows at Barutana 08-08 to 08-14, 17:00–23:00 | Kamnik | Veronikin festival is described as Kamnik's largest children's festival, in Keršmančev park. ⚠️ The medieval-fair framing at Mali grad was not confirmed |

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
| Krajinski park Strunjan | `https://parkstrunjan.si/` |
| Kino Otok | `https://kinootok.org/program/` |
| Center za kulturo Izola | `https://center-izola.si/dogodki/` |
| Kobilarna Lipica | `https://www.lipica.org/` |
| Postojnska jama | `https://www.postojnska-jama.eu/sl/` |
| Visit Kras | `https://www.visitkras.info/` |
| Narodni dom Maribor, Art kamp | `https://nd-mb.si/` |
| Visit Idrija | `https://www.visit-idrija.si/sl/dogodki-in-prireditve/` |
| Festival idrijske čipke | `https://www.festivalidrijskecipke.si/` |
| Jurjevanje | `https://jurjevanje.si/` |
| Kamfest | `https://www.kamfest.org/` |
| Zgodovinska mesta (heritage town events) | `https://www.zgodovinska-mesta.si/prireditve/` |
| Planica | `https://www.planica.si/sl/program` |
