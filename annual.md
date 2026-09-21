# Annual Fixtures

Recurring events that come round every year. Each row carries a **recurrence rule** so the
routine can work out the date itself instead of searching for it, and a **confidence** rating so
it knows how much to trust that rule.

First researched 2026-09-21, expanded the same day after a 50-event cross-check. Rows marked
`low` need re-verifying before they reach `db.json`. Rows under *Unverified* are not facts yet.

★ marks a strong 0–4 fit. ⚠️ marks a caveat that belongs in the event's `flags`.

---

## The window check

Run this before touching any fixture below. It is the whole point of the file.

```
window_start = now
window_end   = now + 3 months          # the horizon from routine.md §1
```

For each fixture, build its concrete date for the current year from the rule in the table.
If the fixture's own window has already passed this year, roll it to next year.

```
fires = (fixture_end >= window_start) AND (fixture_start <= window_end)
```

**Run the fixture's query only when `fires` is true.** Skip everything else in silence. Do not
log skipped fixtures in `diff.md`, they are noise. A fixture that sits outside the window is not
a miss, it is simply not due yet.

Two extra rules:

* **Lead time.** Where the *Book* column has a value, that is when tickets or registration open.
  When `now` is inside 7 days of that date, surface the fixture even if the event itself sits
  beyond the horizon. Bobri's free tickets disappear within hours, and Lumpi tek fills up.
  Missing the booking date makes the event itself worthless.
* **Moveable feasts.** Rows marked `moveable` are tied to Easter and shift by weeks each year.
  Never compute these from a fixed month and day. Look them up.

### Worked example, run on 2026-09-21

Window is 2026-09-21 to 2026-12-21. These fire:

`VNLG` (24–27 Sep, this week) · `Olimpijski festival` · `Dan slovenskega športa` ·
`Evropski teden športa` · `Dnevi odprtih vrat` · `Teden otroka` (5–11 Oct) ·
`ZOO svetovni dan živali` · `ZOO noč čarovnic` · `Lumpi tek` · `Ana Plamenita` ·
`Noč parkeljnov` · `Slovenski knjižni sejem` · `Prižig lučk` · `Ta veseli dan kulture` ·
`Miklavžev sprevod` · `Čarobni gozd` · `Dedek Mraz` · `Ana Mraz` · plus the monthly ones

---

## Fixed-date fixtures

| Fixture | Date | Where | Fit |
|---|---|---|---|
| Gregorčki, pozdrav pomladi | 03-11, 15:00–20:00 | Eipprova ulica, Gradaščica, Trnovo | ★ Free. Children float candlelit wooden boats downstream. Workshops and music. Moves to SEM if it rains |
| Dan Zemlje, ZOO | 04-22, running into the May Day holidays | ZOO Ljubljana | Included in the ticket |
| Mednarodni dan muzejev | 05-18 | Nationwide | Free admission and family programmes at most museums |
| Dan slovenskega športa | 09-23 | Nationwide | National holiday, free sessions |
| Evropski teden športa | 09-23 to 09-30 | Nationwide | Clubs register free trials by age band |
| Svetovni dan živali + dan oskrbnikov | Weekend nearest 10-04 | ZOO Ljubljana | Keeper talks, enrichment demos |
| Ta veseli dan kulture | 12-03 | Nationwide | ★ Prešeren's birthday. Free admission to museums, galleries and theatres, with children's shows. 25th year |
| Miklavžev sprevod | 12-05, 17:00 | Krekov trg → Prešernov trg | Free. St Nicholas comes down from the castle |
| Silvestrovanje za otroke | 12-31, 16:00–17:30 | Kongresni trg | ★ The children's New Year, hours before the adult one. Fairytale characters, music, Dedek Mraz |

## Rule-based fixtures

| Fixture | Rule | Recent years | Confidence |
|---|---|---|---|
| **Teden otroka** | Starts the first Monday of October, runs the week | 2026-10-05 to 10-11 | **high**, the rule has held since 1954. ★ Free workshops at museums, libraries and Pionirski dom |
| **Poletna muzejska noč** | Third Saturday of June, 18:00–24:00 | 2026-06-20 | **high**, rule holds since 2002 |
| **Ljubljanski festival športa** | First Saturday of September, from 09:00, Park Tivoli | 2024-09-07, 2025-09-06, 2026-09-05 | **high**, three years confirmed |
| **Čarobni dan** | Last Sunday of August, 10:00–18:00, Arboretum | 2022-08-28, 2025-08-31, 2026-08-30 | **high** |
| **Grajski dnevi** | May, marking the castle's purchase on 1905-05-16 | Annually, 15th edition | **medium**. ★ Medieval camp, knights, falconry, archery, face painting, free castle tours |
| **Otroški festival gledaliških sanj** | Late March into mid April, Pionirski dom | 2025-04-02 to 04-13, 23rd ed. 03-29 to 04-10 | **medium**. Free. Children's groups perform, so the audience skews school-age |
| **Maraton Franja** | Mid June, BTC City | 2026-06-12 to 06-14 | **medium**. ★ The *Vzajemkov otroški kolesarski izziv* is a 1,000 m loop for the youngest |
| **Pikin festival** | First full week of September, Velenje | 2026-09-05 to 09-11 | **medium** |
| **Lumpi tek / NLB Ljubljanski maraton** | Third weekend of October, children's races on the Saturday | 2025-10-19, 2026-10-17/18 | **medium**, pattern holds but no organiser states it as a rule |
| **Olimpijski festival** | Late September, Kongresni trg + Park Zvezda, from 10:00 | 2025-09-27/28 | **medium**. Free, 50+ sports, ⚠️ advertised for ages 5–17 |
| **Ana Plamenita** | Early to mid November, 18:00–21:00, Park Gradaščica | 2023-11-11, 2024-11-15, 2025-11-07 | **medium**. Fire installations. ⚠️ Dark, but an 18:00 start is workable |
| **Noč parkeljnov, Goričane** | Friday and Saturday in the second half of November, Medvode | 2024-11-22/23, 2025-11-21/22 | **medium**. ⚠️⚠️ **Not for toddlers.** 700+ Krampus figures, chains, torches, engines. Genuinely frightening |
| **Prižig prazničnih lučk** | Late November, 17:00, Prešernov trg | 2026-11-28 | **medium**. Free, children's choir, countdown |
| **Slovenski knjižni sejem** | Late November | 2026-11-23 to 11-29 | **medium**. ⚠️ Moved to Gospodarsko razstavišče for 2026, no longer Cankarjev dom |
| **Dnevi odprtih vrat** | Through September | Annually | **medium** |
| **Citypark free theatre** | First Friday monthly, plus fairy-tale Thursdays | Monthly | **medium** |
| **Free museum admission** | First Sunday monthly, nationwide | Monthly | **medium** |

## Season-window fixtures

| Fixture | Window | Where | Notes |
|---|---|---|---|
| **LUV fest** | 02-08 to 03-12 | Ljubljana, 100+ partners | 4th edition carried 220+ events. Workshops, fairytale walks, family trails |
| **Festival Bobri** | Historically 01-19 to 02-08. **Moved for 2026 to 03-21 to 04-04** | Ljubljana, many venues | ★ ~200 events over 15 days, all free. ⚠️ **Free digital tickets released 2026-03-07 at 10:00 on `bobri.si` and they go within hours.** Check in February, not January |
| **Zmaj kamišibaj** | Spring, 13th edition in 2026 | Hiša otrok in umetnosti | ★ Japanese paper theatre, small scale, very good for the youngest. ⚠️ Month unconfirmed, verify |
| **Igraj se z mano** | Late May, weekdays 09:00–13:00, family day Saturday | Kongresni trg + Park Zvezda | ★ 2026: 05-26 to 05-30. All free, 45+ workshops a day |
| **Svetlobna gverila** | 05-26 to 06-20, daily 21:30–23:30 | Ljubljana public space | Free, 20th edition. ⚠️⚠️ 21:30 start makes it unusable for this age band |
| **Knjižnica pod krošnjami** | 05-30 to 08-31 | 7 Ljubljana spots: Tivoli, Park Zvezda, the castle, park by the Roman wall, Trnovski pristan, Tobačna 001, Mala ulica | Free. ⚠️ The reading islands themselves are an always-on facility and fall under exclusion rule 2. Only the **scheduled storyteller sessions** are events |
| **Otroški knjižni festival** | June, before the summer holidays | Cankarjev dom park | Performances, concerts, workshops. Distinct from the November book fair |
| **Mini poletje** | Late June through August | Mini teater, Križevniška + Ljubljanski grad | International children's and puppet festival. Creative workshops on Sundays |
| **Ana Desetnica** | Late June into early July | Ljubljana streets | ★ 100+ free street theatre events |
| **Rimljani v Ljubljani** | One day, usually September | 8 locations, Arheopark Emona + MGML | Free, 4+. Legionaries, Roman crafts, stamp trail. ⚠️ Month varies, verify |
| **FeKK / FeKKids** | Mid to late August | Kinodvor and partner venues | 2026: 08-17 to 08-22. ⚠️ FeKKids is curated 5+ |
| **Trnovfest** | The whole of August, daily | CSK France Prešeren, Trnovo | ~5 € a day |
| **Emonska promenada** | 08-22 to 08-24 | Novi trg | ★ Run by Hiša otrok in umetnosti, 19th edition, everything free. Street games, bubbles, outdoor puppetry |
| **Letni Kinodvor** | Last week of August, 21:00 | Kongresni trg | Free. ⚠️ Far too late |
| **Kinoteka open air** | Early to mid August | Metelkova lawn | Free. ⚠️ Same evening problem |
| **Zmaj 'ma mlade** | Late August into early September | Postojna | 2026: 08-25 to 09-06. All free, skews teen |
| **VNLG, vikend neodvisnega lutkovnega gledališča** | Late September | Hiša otrok in umetnosti | ★ 2026: 09-24 to 09-27. All performances free, reservation required |
| **ZOO noč čarovnic** | October, evenings, through 10-31 | ZOO Ljubljana | ⚠️ Candlelit evening tours |
| **Čarobni gozd** | Roughly 12-03 to 12-22, 16:30–19:00 | Pavilion, Park Zvezda | ★ Free daily craft workshops. One of the best December fits |
| **Dedek Mraz** | Cabin in Park Zvezda 12-20 to 12-30, 10:00–18:00. Parades daily 17:00 from 12-26 to 12-30 | Ljubljana centre | ★ Free |
| **Ana Mraz** | 12-21 to 12-30 | Gornji trg, Krekov trg, Špica | Street theatre and circus. Real-snow play area on Krekov trg 12-27 to 12-29 |

## Moveable feasts

Tied to Easter. **Never compute these from a fixed date.** Look them up each year.

| Fixture | Rule | Where | Notes |
|---|---|---|---|
| **Zmajev karneval** | Carnival Saturday, parade from 11:00 | Novi trg → Čevljarski most → Prešernov trg → Kongresni trg | ★★ **The best carnival fit.** Led by Ljubljana's green dragon, with ten-plus groups from city kindergartens. Daytime, outdoor, free. 2026: 02-14 |
| **Pustno rajanje, Pionirski dom** | Carnival Saturday, 16:00–20:00 | Pionirski dom festival hall | Costumes, art workshops, face painting, balloon release |
| **Kurentovanje** | The eleven days ending on Shrove Tuesday | Ptuj | 2027: 02-03 to 02-09, **children's parade 02-08 at 10:00**. The children's parade is the relevant part, not the main international one |
| **Local pust carnivals** | Shrove Sunday and Tuesday | Nationwide | Kindergartens and town squares run small parades. Good 0–4 fit, poorly documented. Check municipal sites in the fortnight before |

## Unverified

Reported but not confirmed by this research. **Do not present these as real** until checked.
The venue may exist while the specific annual event does not.

| Claim | What is actually confirmed |
|---|---|
| Praznik pomladi v Botaničnem vrtu | The garden is real and publishes a monthly `napovednik dogodkov` with family workshops. A distinct annual spring festival was not found |
| Pust v Živalskem vrtu | The zoo runs holiday events, but a Shrovetide edition was not confirmed |
| Promenadni koncerti pihalnih orkestrov | Not confirmed |
| Junij v Ljubljani | Not confirmed as a named festival |
| PikniKoncert, Tivoli and the castle | Not confirmed |
| ARTish Family Fair Days | ARTish exists as a Ljubljana art market. A family-fair strand was not confirmed |
| Nočni sprehod v Živalskem vrtu | Night tours happen inside other events, not as a standing series |
| Ljubljana Beachvolley & Urban Sports Days | Not confirmed |
| Poljanska Fest | Not confirmed |
| Praznik kostanja na Špici | Not confirmed |
| Dobrodelni praznični sejem, Cankarjevo nabrežje | Not confirmed as an annual fixture |
| Pravljice pod zvonikom | Not confirmed under this name |

## Out of scope under the existing rules

Real, but excluded by `routine.md` §1. Listed so nobody re-adds them.

| Item | Rule it breaks |
|---|---|
| Zimske počitniške delavnice, Pionirski dom | Rule 3, multi-day paid holiday camps |
| WOOP! winter challenge | Rule 2, permanent commercial venue |
| Koruzni labirint Stanežiče (July to October) | Rule 2, a seasonal attraction with opening hours, not a scheduled event |
| Odprta kuhna, Fridays at Pogačarjev trg | Rule 2, a weekly recurring market |
| Knjižnica pod krošnjami reading islands | Rule 2 for the islands. Its scheduled storyteller sessions stay in scope |

## ⛔ Retired or misidentified

| Item | What is actually true |
|---|---|
| **Trnfest** | Last edition 2018. Succeeded by **Trnovfest**, different organiser, different part of town |
| **Zmajev festival at Ljubljanski grad** | This is a **music festival** (Hladno pivo, Elvis Jackson and similar), not a children's dragon event. The castle's actual dragon content for children is **Zmajski dan**, **Zmajelovščina** and the puppet play **Friderik in zmaj** (3+) |

---

## Source links

| Fixture or venue | URL |
|---|---|
| Gregorčki | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/pozdrav-pomladi-z-gregorcki` |
| LUV fest | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/luv-fest` |
| Bobri | `https://bobri.si/` |
| **Hiša otrok in umetnosti** (Zmaj kamišibaj, VNLG, Emonska promenada) | `https://www.hisaotrok.si/koledar_prireditev/list/` |
| **Pionirski dom** | `https://pionirski-dom.si/` |
| **Mini teater** | `https://www.mini-teater.si/si` |
| **Botanični vrt** | `http://www.botanicni-vrt.si/napovednik-dogodkov` |
| Grajski dnevi | `https://www.ljubljanskigrad.si/sl/dogodki/grajski-dnevi/` |
| Igraj se z mano | `https://igrajsezmano.eu/festival/ljubljana/` |
| Svetlobna gverila | `https://www.svetlobnagverila.net/` |
| Knjižnica pod krošnjami | `https://www.knjiznicapodkrosnjami.si/` |
| Poletna muzejska noč | `https://sms-muzeji.si/` |
| Maraton Franja | `https://franja.org/` |
| Ana Desetnica, Ana Plamenita, Ana Mraz | `https://www.anamonro.si/festivali/festivalski-program/` |
| Trnovfest | `https://www.cskfp.si/` |
| Čarobni dan | `https://www.carobnidan.si/` |
| Zmaj 'ma mlade | `https://www.zmaj-ma-mlade.com/` |
| Rimljani v Ljubljani | `https://rimljanivljubljani.si/` |
| Ljubljanski festival športa | `https://www.ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` |
| Olimpijski festival, European Week of Sport | `https://olympic.si/` and `https://ewos.olympic.si/` |
| Teden otroka | `https://www.zpms.si/programi/teden-otroka/` |
| Pikin festival | `https://www.pikinfestival.si/` |
| Dan slovenskega športa | `https://danslovenskegasporta.si/` |
| Lumpi tek | `https://ljubljanskimaraton.si/lumpi-tek` |
| Slovenski knjižni sejem | `https://knjizni-sejem.si/` |
| Otroški knjižni festival | `https://www.cd-cc.si/kultura/za-mlade-in-sole/otroski-knjizni-festival` |
| ZOO events | `https://www.zoo.si/novice` |
| Miklavžev sprevod | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/miklavzev-sprevod/` |
| December v Ljubljani, Silvestrovanje za otroke | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani` |
| Kurentovanje | `https://kurentovanje.net/` |
| Citypark | `https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/` |
| Otroški bazar | `https://www.otroskibazar.si/` (status unknown, holding page) |
