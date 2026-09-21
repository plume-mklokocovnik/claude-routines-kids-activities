# Annual Fixtures

Recurring events that come round every year. Each row carries a **recurrence rule** so the
routine can work out the date itself instead of searching for it, and a **confidence** rating so
it knows how much to trust that rule.

Researched 2026-09-21. Re-verify any row marked `low` before writing it to `db.json`.

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

`Pikin festival` (tail end) · `Dan slovenskega športa` · `Evropski teden športa` ·
`Dnevi odprtih vrat` · `ZOO svetovni dan živali` · `ZOO noč čarovnic` · `Lumpi tek` ·
`Miklavžev sprevod` · `Čarobni gozd` · `Dedek Mraz` · `Citypark` and `free museum Sunday` (monthly)

These do not: Bobri, Kurentovanje, Dan Zemlje, Igraj se z mano, Poletna muzejska noč,
Ana Desetnica, Trnovfest, outdoor cinema, Čarobni dan, Zmaj 'ma mlade, Ljubljanski festival športa.

---

## Fixed-date fixtures

The date is the same every year. Confidence is `high` by definition.

| Fixture | Date | Where | Book | Notes |
|---|---|---|---|---|
| Dan Zemlje, ZOO | 04-22, programme runs into the May Day holidays | ZOO Ljubljana | — | Included in the entrance ticket |
| Dan slovenskega športa | 09-23 | Nationwide | — | National holiday. Free sessions everywhere |
| Evropski teden športa | 09-23 to 09-30 | Nationwide | — | Clubs register free trial sessions by age band |
| Svetovni dan živali + dan oskrbnikov | The weekend nearest 10-04 | ZOO Ljubljana | — | Enrichment demos, keeper talks |
| Miklavžev sprevod | 12-05, 17:00 | Krekov trg → Prešernov trg, Ljubljana | — | St Nicholas comes down from the castle with angels and devils |

## Rule-based fixtures

The date moves, but the rule is stable. Compute it.

| Fixture | Rule | Recent years | Confidence | Book |
|---|---|---|---|---|
| **Poletna muzejska noč** | Third Saturday of June, 18:00–24:00 | 2026-06-20 | **high**, the rule has held since 2002 | — |
| **Ljubljanski festival športa** | First Saturday of September, from 09:00, Park Tivoli | 2024-09-07, 2025-09-06, 2026-09-05 | **high**, three years confirmed | — |
| **Čarobni dan** | Last Sunday of August, 10:00–18:00, Arboretum Volčji Potok | 2022-08-28, 2025-08-31, 2026-08-30 | **high** | — |
| **Pikin festival** | First full week of September, 7 days, Velenje | 2026-09-05 to 09-11 | **medium** | — |
| **Lumpi tek / NLB Ljubljanski maraton** | Third weekend of October, children's races on the Saturday | 2025-10-19, 2026-10-17/18 | **medium**, the pattern holds but no organiser confirms it as a rule | Registration opens months ahead and fills |
| **Dnevi odprtih vrat** | Through September, tied to the sports festival | Every September | **medium** | — |
| **Citypark free theatre** | First Friday of the month, plus fairy-tale Thursdays | Monthly | **medium** | — |
| **Free museum admission** | First Sunday of the month, nationwide | Monthly | **medium** | — |

## Season-window fixtures

No crisp rule, but a reliable window. Search inside it.

| Fixture | Window | Where | Confidence | Notes |
|---|---|---|---|---|
| **Festival Bobri** | Historically 01-19 to 02-08. **Moved for 2026 to 03-21 to 04-04** | Ljubljana, many venues | **low on timing, high on value** | 18th edition, ~200 events over 15 days, everything free. ⚠️ **Free digital tickets released 2026-03-07 at 10:00 on `bobri.si` and they go fast.** Check the site in February, do not assume January |
| **Igraj se z mano** | Late May, weekdays 09:00–13:00, family day on the Saturday | Kongresni trg + Park Zvezda | **medium** | 2026: 05-26 to 05-30. Everything free, 45+ workshops a day |
| **Ana Desetnica** | Late June into the first days of July | Ljubljana streets | **medium** | 100+ free street theatre events |
| **Trnovfest** | The whole of August, daily | CSK France Prešeren, Trnovo | **medium** | ~5 € daily ticket |
| **Letni Kinodvor** | Last week of August, 21:00 | Kongresni trg | **medium** | Free, but ⚠️ far too late for a toddler |
| **Kinoteka open air** | Early to mid August | Metelkova lawn | **medium** | Free, same evening problem |
| **Zmaj 'ma mlade** | Late August into early September | Postojna | **medium** | 2026: 08-25 to 09-06. All free, skews teen |
| **ZOO noč čarovnic** | October, evenings, through 10-31 | ZOO Ljubljana | **medium** | ⚠️ Evening, candlelit tours |
| **Čarobni gozd** | Roughly 12-03 to 12-22, 16:30–19:00 | Pavilion, Park Zvezda / Kongresni trg | **medium** | Free creative workshops. One of the best December fits |
| **Dedek Mraz** | Cabin in Park Zvezda 12-20 to 12-30, 10:00–18:00. Parades daily at 17:00 from 12-26 to 12-30 | Ljubljana centre | **medium** | Free |
| **Veseli december, street theatre and snow** | 12-27 to 12-29, Krekov trg | Ljubljana | **medium** | Real-snow play area |

## Moveable feasts

Tied to Easter. **Never compute these from a fixed date.** Look them up each year.

| Fixture | Rule | Where | Notes |
|---|---|---|---|
| **Kurentovanje** | The eleven days ending on Shrove Tuesday | Ptuj | 2027: 02-03 to 02-09, **children's parade 02-08 at 10:00**. The children's parade is the toddler-relevant part, not the main international one |
| **Local pust carnivals** | Shrove Sunday and Tuesday | Nationwide, most towns | Kindergartens and town squares run small parades. Very good 0-4 fit, poorly documented online. Check municipal sites in the fortnight before |

## Status unknown

| Fixture | Problem |
|---|---|
| **Otroški bazar** | `otroskibazar.si` currently shows only "OTROŠKI BAZAR SE KMALU VRNE V NOVI PREOBLEKI" with no dates. The event looks to be mid-rebrand or on hiatus. **Do not assume a September edition.** Check the site each August before promising it |

## ⛔ Retired, do not search for these

| Fixture | What happened |
|---|---|
| **Trnfest** | Last edition 2018. Succeeded by **Trnovfest**, which is a different organiser in a different part of town. Searching for Trnfest returns only archive pages |

---

## Source links for the fixtures

| Fixture | URL |
|---|---|
| Bobri | `https://bobri.si/` |
| Igraj se z mano | `https://igrajsezmano.eu/festival/ljubljana/` |
| Poletna muzejska noč | `https://sms-muzeji.si/` |
| Ana Desetnica | `https://www.anamonro.si/festivali/festivalski-program/` |
| Trnovfest | `https://www.cskfp.si/` |
| Čarobni dan | `https://www.carobnidan.si/` and `https://www.arboretum.si/dogodek/carobni-dan/` |
| Zmaj 'ma mlade | `https://www.zmaj-ma-mlade.com/` |
| Ljubljanski festival športa | `https://www.ljubljana.si/sl/ljubljana/sportna/ljubljanski-festival-sporta` |
| Pikin festival | `https://www.pikinfestival.si/` |
| Dan slovenskega športa | `https://danslovenskegasporta.si/` |
| Lumpi tek | `https://ljubljanskimaraton.si/lumpi-tek` |
| ZOO events | `https://www.zoo.si/novice` |
| Miklavžev sprevod | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/miklavzev-sprevod/` |
| December v Ljubljani | `https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani` |
| Kurentovanje | `https://kurentovanje.net/` |
| Citypark | `https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/` |
| Otroški bazar | `https://www.otroskibazar.si/` (status unknown) |
