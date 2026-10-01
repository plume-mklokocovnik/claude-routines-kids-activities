# Routine Run: 2026-10-01T09:05:53+02:00

Run: `20261001T070553Z_56e70032`

| New | Updated | Expired | Hidden | Filtered | Deferred | Unchanged |
|---|---|---|---|---|---|---|
| 48 | 5 | 5 | 0 | 17 | 0 | 0 |

## Discovery Coverage

| Pass | Status | Notes |
|---|---|---|
| avto\_moto | ok | SVAMZ and Zveza SVS PDF calendars re-fetched and cross-checked; all previously-recorded Oct-Dec fixtures re-verified. Confirmed the Škofljica fair's actual visitor start time (08:00) from the club's own site, correcting the stored time\_unknown. Alfa Rally and a new 'Od Štorkle do Torklje' rally lead remain unconfirmed (no venue/fixed date). |
| concerts\_generic | ok | All 3A undated + month-anchored queries run, napovednik.com/glasba sub-categories swept, Pass 1 venues re-checked for music. Found the Lisztov inštitut bilingual musical hours, Cellofest's closing concert, and a second SiTi Teater concert series (nedeljski popoldnevi) not previously tracked. |
| concerts\_watchlist | ok | All 7 watchlist artists searched across Oct/Nov/Dec 2026 via dated queries. Only Alenka Kolman (via her label's own page) and the already-known Romana Krajnčan Kino Bežigrad date returned confirmable results. Resolved last run's 'unresolved conflict' at Kino Bežigrad: raw-HTML grep shows Pika Nogavička and the Krajnčan musical are on different dates, not double-booked; last run's stored 17:00 start time for the Krajnčan show appears to have been a hallucinated WebFetch summary and is corrected back to time\_unknown this run. |
| free\_entry | ok | All undated and month-anchored Pass 4 queries run. Found Narodni muzej Slovenije's own Teden otroka free week (previously undiscovered source nms.si) and a joint Metelkova tri-museum free afternoon. Corrected the existing Narodna galerija record's url to the venue's own dedicated free-entry page. |
| ljubljana | ok | MOL calendar (37 events, down from 54 on 9/25) fetched fresh via curl; all mandatory venues/aggregators checked. Kino Bežigrad Pika Nogavička title correction applied. Hiša otrok in umetnosti regression from last run is resolved (live content again). 26 new MKL library events found net of 9 that match existing hidden\_events rows. |
| slovenia | ok | Regional sweep against regions.md fixtures plus Pass 2 query block. Praznik kakijev date corrected (13-15 Nov, not 10-12). Novomeški polmaraton's previously-conflicting dates resolved via a non-social aggregator. New Hura! Družinski dan 2026 edition confirmed. kavbojska-dezela.si developed a new bot-block (sgcaptcha) since 9/28, noted for links.md. |

## New

| When | Event / ID | Place | Age / price / notes |
|---|---|---|---|
| 01.10.2026 17:00 | [Sončnice (delavnica)](https://www.mklj.si/dogodek/soncnice-2/)<br>`delavnica`<br>`event_20261001_1700_b402f73a56d0` | [Knjižnica Horjul (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Horjul%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 02.10.2026 17:00 | [Beremo z nasmehom s psičko Luno](https://www.mklj.si/dogodek/beremo-z-nasmehom-s-psicko-luno-6/)<br>`delavnica`<br>`event_20261002_1700_476cbd334f02` | [Knjižnica Jožeta Mazovca (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Jo%C5%BEeta%20Mazovca%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 02.10.2026 17:00 | [Madžarsko-slovenska glasbena ura za otroke](https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6261)<br>`koncert`<br>`event_20261002_1700_69f9e50597f9` | [Lisztov inštitut Ljubljana, Barvarska steza 8](https://maps.google.com/?q=Lisztov%20in%C5%A1titut%20Ljubljana%2C%20Barvarska%20steza%208%20Ljubljana) | `3+` / 🆓 Brezplačen dogodek<br> |
| 03.10.2026 ? | [Hura! Družinski dan (Baby Center)](https://www.babycenter.si/blog/vabljeni-na-hura-druzinski-dan)<br>`festival`<br>`event_20261003_0000_7a92e795ce3b` | [AMZS Center varne vožnje, Vransko, Vransko](https://maps.google.com/?q=AMZS%20Center%20varne%20vo%C5%BEnje%2C%20Vransko%20Vransko) | `?` / `?`<br><br>daljša pot, ura ni znana |
| 05.10.2026 ? | [Z igro do dediščine 2026: brezplačen vstop v Narodni muzej Slovenije](https://www.nms.si/si/dogodki/2026/10/12404-Z-igro-do-dediscine)<br>`festival`<br>`event_20261005_0000_f05d766f3b85` | [Narodni muzej Slovenije – Muzejska ulica 1 in Metelkova 20](https://maps.google.com/?q=Narodni%20muzej%20Slovenije%20%E2%80%93%20Muzejska%20ulica%201%20in%20Metelkova%2020%20Ljubljana) | `?` / 🆓 Brezplačen ogled stalnih zbirk in razstav za otroke in družine (Muzejska: 5.–11. 10. 2026; Metelkova: 6.–11. 10. 2026). Sicer: odrasli 8 €/10 € (ena/obe lokaciji), upokojenci in učenci/dijaki/študentje 4 €/6 €, družine 16 €/17 €.<br><br>ura ni znana |
| 05.10.2026 17:30 | [Primer št. 4 cm – Lutke Pika Poka](https://www.mklj.si/dogodek/tetka-jesen-lutke-pika-poka-2/)<br>`lutke`<br>`event_20261005_1730_41ed01f662df` | [Knjižnica Jurij Vega (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Jurij%20Vega%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:00 | [Dežela zmajev](https://www.mklj.si/dogodek/dezela-zmajev-4/)<br>`pravljice`<br>`event_20261006_1700_4a59b5a902dc` | [Knjižnica Grba (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Grba%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:00 | [Štirje muzikanti](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261006_1700_78b1394a39c0` | [Veliki oder, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Veliki%20oder%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / 8 EUR<br> |
| 06.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-280/2026-10-06/)<br>`pravljice`<br>`event_20261006_1700_8b326ba6a252` | [Knjižnica Savsko naselje (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Savsko%20naselje%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-286/2026-10-06/)<br>`pravljice`<br>`event_20261006_1700_bdcb08d7fa2a` | [Knjižnica Jarše (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Jar%C5%A1e%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-282/2026-10-06/)<br>`pravljice`<br>`event_20261006_1700_f5c25b7c7bcc` | [Knjižnica Fužine (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Fu%C5%BEine%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:30 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-270/2026-10-06/)<br>`pravljice`<br>`event_20261006_1730_3c2bc2c9f3a5` | [Knjižnica Dobrova (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Dobrova%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 17:30 | [Ura pravljic v angleškem jeziku](https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-15/2026-10-06/)<br>`pravljice`<br>`event_20261006_1730_e8b322d8e908` | [Knjižnica Škofljica (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20%C5%A0kofljica%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 18:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-249/2026-10-06/)<br>`pravljice`<br>`event_20261006_1800_86f5a6b1deab` | [Knjižnica Gameljne (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Gameljne%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 06.10.2026 18:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-258/2026-10-06/)<br>`pravljice`<br>`event_20261006_1800_eaf8408533f4` | [Knjižnica Horjul (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Horjul%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 07.10.2026 16:00 | [Ura pravljic v nemškem jeziku](https://www.mklj.si/dogodek/ura-pravljic-v-nemskem-jeziku-5/2026-10-07/)<br>`pravljice`<br>`event_20261007_1600_4fcdbf1dfc0f` | [Knjižnica Polje (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Polje%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 07.10.2026 17:00 | [Ura pravljic: Čevljar – mojster, ki je obul svet](https://www.mklj.si/dogodek/ura-pravljic-cevljar-mojster-ki-je-obul-svet-petra-kozjan/)<br>`pravljice`<br>`event_20261007_1700_d5017a4f15a5` | [Knjižnica Bežigrad, podpritličje (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Be%C5%BEigrad%2C%20podpritli%C4%8Dje%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 08.10.2026 17:00 | [Medgeneracijsko srečališče: delavnica izdelovanja značk](https://mao.si/dogodek/medgeneracijsko-srecalisce-delavnica-izdelovanja-znack/)<br>`delavnica`<br>`event_20261008_1700_261236e76ec0` | [MAO, Rusjanov trg 7](https://maps.google.com/?q=MAO%2C%20Rusjanov%20trg%207%20Ljubljana) | `?` / 🆓 Dogodek je brezplačen<br> |
| 08.10.2026 17:00 | [Štirje muzikanti](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261008_1700_9085bff91540` | [Veliki oder, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Veliki%20oder%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / 8 EUR<br> |
| 10.10.2026 11:00 | [Z odra v muzej – Štirje muzikanti (predstava in vodeni ogled)](https://www.ljubljanskigrad.si/)<br>`lutke`<br>`event_20261010_1100_b8ad33f756ac` | [Lutkovni muzej, Ljubljanski grad](https://maps.google.com/?q=Lutkovni%20muzej%2C%20Ljubljanski%20grad%20Ljubljana) | `?` / `?`<br> |
| 10.10.2026 15:00 | [En dan. Trije muzeji. Ena ploščad. – jesensko muzejsko popoldne (prost vstop)](https://www.nms.si/si/dogodki/2026/10/12403-En-dan-Trije-muzeji-Ena-ploscad)<br>`festival`<br>`event_20261010_1500_4352040c3e5a` | [Muzejska ploščad Metelkova (NMS, SEM, MSUM)](https://maps.google.com/?q=Muzejska%20plo%C5%A1%C4%8Dad%20Metelkova%20%28NMS%2C%20SEM%2C%20MSUM%29%20Ljubljana) | `0+` / 🆓 Prost vstop na razstave vseh treh muzejev na Metelkovi od 15.00 dalje, plus delavnice, vodeni ogledi, art sejem in koncert. Sicer: NMS-Metelkova 8 €/4 €, 16 € družina; SEM 8 €/5 €, 16 € družina.<br> |
| 10.10.2026 16:00 | [Z igro do dediščine 2026: brezplačno vodstvo za družine po Plečnikovi hiši](https://mgml.si/sl/plecnikova-hisa/dogodki/2534/2026-10-10/16-00/z-igro-do-dediscine-2026-brezplacno-vodstvo-za-druzine-po-plecnikovi-hisi/)<br>`festival`<br>`event_20261010_1600_9c1e44b08598` | [Plečnikova hiša, Karunova ulica 4](https://maps.google.com/?q=Ple%C4%8Dnikova%20hi%C5%A1a%2C%20Karunova%20ulica%204%20Ljubljana) | `?` / 🆓 Brezplačno vodstvo za družine (16.00–17.15), rezervacija na prijava@mgml.si. Sicer: odrasli 12 €, dijaki in otroci 9 €, otroci do 6. leta brezplačno, nad 60 let 9 €, družine 25 €.<br><br>prijava |
| 10.10.2026 17:00 | [Štirje muzikanti](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261010_1700_f5f518db768b` | [Veliki oder, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Veliki%20oder%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / 8 EUR (dopoldanska 11:00 uprizoritev razprodana)<br> |
| 11.10.2026 11:00 | [SiTi Teater nedeljski popoldnevi: Repki 1](https://www.sititeater.si/nedeljski-popoldnevi/repki-1/)<br>`koncert`<br>`event_20261011_1100_3db2b6fe1c75` | [SiTi Teater BTC, Ameriška ulica 3](https://maps.google.com/?q=SiTi%20Teater%20BTC%2C%20Ameri%C5%A1ka%20ulica%203%20Ljubljana) | `4+` / `?`<br> |
| 11.10.2026 17:00 | [SiTi Teater nedeljski popoldnevi: Repki 2](https://www.sititeater.si/nedeljski-popoldnevi/repki-2/)<br>`koncert`<br>`event_20261011_1700_357e4e92e629` | [SiTi Teater BTC, Ameriška ulica 3](https://maps.google.com/?q=SiTi%20Teater%20BTC%2C%20Ameri%C5%A1ka%20ulica%203%20Ljubljana) | `4+` / `?`<br> |
| 13.10.2026 09:30 | [Ura pravljic z igranjem 2+](https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-13/)<br>`pravljice`<br>`event_20261013_0930_8dc460030f49` | [Knjižnica Bežigrad (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Be%C5%BEigrad%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 14.10.2026 09:30 | [Otroški knjižni klub (za otroke, ki ne obiskujejo vrtca)](https://www.mklj.si/dogodek/otroski-knjizni-klub-pravljicna-urica-za-otroke-ki-ne-obiskujejo-vrtca/)<br>`pravljice`<br>`event_20261014_0930_93797fb32172` | [Knjižnica Šiška (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20%C5%A0i%C5%A1ka%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 14.10.2026 17:00 | [Zverjasec](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261014_1700_654129318ed4` | [Veliki oder, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Veliki%20oder%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / Razprodano<br><br>razprodano |
| 15.10.2026 17:00 | [Zverjasec](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261015_1700_9b962251c05a` | [Veliki oder, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Veliki%20oder%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / Razprodano<br><br>razprodano |
| 15.10.2026 18:00 | [Bikec Ferdinand (premiera)](https://lgl.mojekarte.si/en/all.html)<br>`lutke`<br>`event_20261015_1800_cb1cb57d569e` | [Oder pod zvezdami, Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Oder%20pod%20zvezdami%2C%20Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `?` / 8 EUR<br> |
| 16.10.2026 17:00 | [Madžarsko-slovenska glasbena ura za otroke](https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6262)<br>`koncert`<br>`event_20261016_1700_2244a3b3ba70` | [Lisztov inštitut Ljubljana, Barvarska steza 8](https://maps.google.com/?q=Lisztov%20in%C5%A1titut%20Ljubljana%2C%20Barvarska%20steza%208%20Ljubljana) | `3+` / 🆓 Brezplačen dogodek<br> |
| 16.10.2026 17:00 | [Festival Hokus Pokus s Klemnom Janežičem](https://pionirski-dom.si/aktualno/festival-hokus-pokus-s-klemnom-janezicem/)<br>`festival`<br>`event_20261016_1700_e18279d14954` | [Pionirski dom](https://maps.google.com/?q=Pionirski%20dom%20Ljubljana) | `?` / 🆓<br> |
| 18.10.2026 11:00 | [Zaključni koncert tridnevne delavnice za 100 najmlajših violončelistov iz vse Slovenije (Cellofest)](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/zakljucni-koncert-tridnevne-delavnice-za-100-najmlajsih-violoncelistov-iz-vse-slovenije)<br>`koncert`<br>`event_20261018_1100_2581648f27d5` | [Konservatorij za glasbo in balet Ljubljana (Dvorana L. M. Škerjanca), Ižanska cesta 12](https://maps.google.com/?q=Konservatorij%20za%20glasbo%20in%20balet%20Ljubljana%20%28Dvorana%20L.%20M.%20%C5%A0kerjanca%29%2C%20I%C5%BEanska%20cesta%2012%20Ljubljana) | `?` / 🆓 Vstopnine ni<br> |
| 21.10.2026 16:00 | [Ura pravljic v angleškem jeziku](https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-14/2026-10-21/)<br>`pravljice`<br>`event_20261021_1600_1025c93fee2a` | [Knjižnica Polje (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Polje%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 21.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-250/2026-10-21/)<br>`pravljice`<br>`event_20261021_1700_34260efed061` | [Knjižnica Šiška (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20%C5%A0i%C5%A1ka%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 22.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-273/2026-10-22/)<br>`pravljice`<br>`event_20261022_1700_56334331b4ad` | [Knjižnica Prežihov Voranc (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Pre%C5%BEihov%20Voranc%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 22.10.2026 17:00 | [Ura pravljic](https://www.mklj.si/dogodek/ura-pravljic-278/2026-10-22/)<br>`pravljice`<br>`event_20261022_1700_c87d90965055` | [Knjižnica Glinškova ploščad (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Glin%C5%A1kova%20plo%C5%A1%C4%8Dad%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 23.10.2026 16:00 | [Alenka Kolman – nastop za otroke](https://glasbenadezela.si/nastopi/)<br>`koncert`<br>`event_20261023_1600_0fad17a23b00` | [Novo mesto (natančno prizorišče ni objavljeno), Novo mesto](https://maps.google.com/?q=Novo%20mesto%20%28natan%C4%8Dno%20prizori%C5%A1%C4%8De%20ni%20objavljeno%29%20Novo%20mesto) | `?` / `?`<br><br>daljša pot |
| 26.10.2026 09:00 | [MINT: Misija Računalnik od abakusa do računalnika](https://www.mklj.si/dogodek/mint-misija-racunalnik-od-abakusa-do-racunalnika-rudi-majerle/)<br>`delavnica`<br>`event_20261026_0900_370c07817cba` | [Knjižnica Šiška (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20%C5%A0i%C5%A1ka%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 27.10.2026 08:30 | [Ura pravljic z igranjem 2+](https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-27/)<br>`pravljice`<br>`event_20261027_0830_5b48f3e04255` | [Knjižnica Bežigrad (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Be%C5%BEigrad%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |
| 27.10.2026 09:00 | [MINT: Camera obscura](https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster-2/)<br>`delavnica`<br>`event_20261027_0900_94b214fc7950` | [Knjižnica Polje (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Polje%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 28.10.2026 09:00 | [MINT: Camera obscura](https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster/)<br>`delavnica`<br>`event_20261028_0900_7ff16e37a744` | [Knjižnica Prežihov Voranc (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Pre%C5%BEihov%20Voranc%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 28.10.2026 09:00 | [MINT: Kako je bilo, ko še ni bilo šivalnih strojev](https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev/)<br>`delavnica`<br>`event_20261028_0900_e08a35103c91` | [Knjižnica Rudnik (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Rudnik%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 29.10.2026 09:00 | [MINT: Kako je bilo, ko še ni bilo šivalnih strojev](https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev-nina-ambroz-2/)<br>`delavnica`<br>`event_20261029_0900_5eb6b1f7685c` | [Knjižnica Jožeta Mazovca (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Jo%C5%BEeta%20Mazovca%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 29.10.2026 09:00 | [MINT: Misija Se slišimo? Radioamaterstvo in komunikacija nekoč](https://www.mklj.si/dogodek/mint-misija-se-slisimo-radioamaterstvo-in-komunikacija-nekoc/)<br>`delavnica`<br>`event_20261029_0900_98d0c218647a` | [Knjižnica Prežihov Voranc (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20Pre%C5%BEihov%20Voranc%20%28MKL%29%20Ljubljana) | `6+` / 🆓<br><br>starost? |
| 14.11.2026 14:40 | [Novomeški polmaraton – otroški tek (predšolski in šolski)](https://www.finishers.com/pl/e/polmaraton-w-novo-mesto)<br>`tek`<br>`event_20261114_1440_35c838879cf0` | [Seidlova cesta 1, Novo mesto, Novo Mesto](https://maps.google.com/?q=Seidlova%20cesta%201%2C%20Novo%20mesto%20Novo%20Mesto) | `?` / `?`<br><br>daljša pot, starost? |
| 13.12.2026 18:00 | [Katalena: Enci benci Katalenci](https://www.cd-cc.si/kultura/za-mlade-in-sole/katalena-enci-benci-katalenci-0)<br>`koncert`<br>`event_20261213_1800_336663f50811` | [Linhartova dvorana, Cankarjev dom](https://maps.google.com/?q=Linhartova%20dvorana%2C%20Cankarjev%20dom%20Ljubljana) | `11+` / 12,00 EUR<br><br>starost? |
| 26.12.2026 11:00 | [SiTi Teater sobotni dopoldnevi: Škratovske priprave na praznike z obiskom Dedka Mraza](https://www.sititeater.si/sobotni-dopoldnevi/)<br>`lutke`<br>`event_20261226_1100_2df3ca6c0137` | [SiTi Teater BTC, Ameriška ulica 3](https://maps.google.com/?q=SiTi%20Teater%20BTC%2C%20Ameri%C5%A1ka%20ulica%203%20Ljubljana) | `?` / `?`<br> |

## Updated

| When | Event / ID | Place | Age / price / notes |
|---|---|---|---|
| 06.10.2026 ? | [Teden akcije Z igro do dediščine: brezplačen ogled stalne zbirke](https://www.ng-slo.si/si/dogodki/prost-vstop-na-stalno-zbirko-za-druzine-z-otroki?id=6709)<br>`festival`<br>`ng_20261006_0000` | [Narodna galerija, Puharjeva 9](https://maps.google.com/?q=Narodna%20galerija%2C%20Puharjeva%209%20Ljubljana) | `0+` / 🆓 Brezplačno za družine z otroki do 18. leta, 6.–11. 10. 2026<br>price\_text, url<br>ura ni znana |
| 10.10.2026 ? | [Pika Nogavička in časovna pustolovščina v Vili Čira Čara](https://www.kino-bezigrad.si/predstava/gledaliska-predstava-pika-nogavicka-in-potovanje-skozi-cas/)<br>`lutke`<br>`kinobezigrad_20261010_0000` | [Kino Bežigrad](https://maps.google.com/?q=Kino%20Be%C5%BEigrad%20Ljubljana) | `3+` / 9,90 EUR (samostojna vstopnica, tudi del abonmaja)<br>title<br>ura ni znana |
| 11.10.2026 08:00 | [Sejem starodobnih vozil in opreme](https://www.oldtimer-skofljica.com/)<br>`avto_moto`<br>`event_20261011_0000_6f17d5aff49d` | [Pri AC Žgajnar, Škofljica, Škofljica](https://maps.google.com/?q=Pri%20AC%20%C5%BDgajnar%2C%20%C5%A0kofljica%20%C5%A0kofljica) | `?` / `?`<br>flags, start\_time, url |
| 09.11.2026 ? | [Nov muzikal Romane Krajnčan: Kako je mravljica postala huda](https://www.kino-bezigrad.si/predstava/nov-muzikal-romane-krajncan-kako-je-mravljica-postala-huda/)<br>`lutke`<br>`kinobezigrad_20261109_0000` | [Kino Bežigrad](https://maps.google.com/?q=Kino%20Be%C5%BEigrad%20Ljubljana) | `3+` / Cena ni navedena<br>flags, start\_time<br>ura ni znana |
| 13.11.2026 ? | [Praznik kakijev v Strunjanu](https://www.zgodovinska-mesta.si/prireditve/praznik-kakijev-v-strunjanu/)<br>`festival`<br>`strunjan_20261110_1100` | [Strunjanske soline (TD Solinar Strunjan), Strunjan (Piran)](https://maps.google.com/?q=Strunjanske%20soline%20%28TD%20Solinar%20Strunjan%29%20Strunjan%20%28Piran%29) | `0+` / 23. izvedba, 13.–15. 11. 2026. Program (sejem, delavnice, tekmovanje za največji kaki) bo objavljen naknadno.<br>flags, is\_free, price\_text, start\_time<br>daljša pot, ura ni znana |

## Expired

| When | Event / ID | Place | Age / price / notes |
|---|---|---|---|
| 28.09.2026 17:00 | [Mavgli / Mowgli](https://www.lgl.si/mavgli-mowgli)<br>`lutke`<br>`event_20260928_1700_4d79d389347a` | [Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `3+` / `?`<br> |
| 28.09.2026 18:00 | [Kumulunimbu](https://www.lgl.si/kumulunimbu)<br>`lutke`<br>`event_20260928_1800_9fba40649ae8` | [Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `6+` / `?`<br><br>starost? |
| 28.09.2026 20:00 | [sorodne duše / soul mates](https://www.lgl.si/sorodne-duse-soul-mates)<br>`lutke`<br>`event_20260928_2000_4c3eb5b6c9ed` | [Lutkovno gledališče Ljubljana (LGL)](https://maps.google.com/?q=Lutkovno%20gledali%C5%A1%C4%8De%20Ljubljana%20%28LGL%29%20Ljubljana) | `5+` / `?`<br><br>starost? |
| 30.09.2026 17:00 | [Izdelava kokedam](http://www.botanicni-vrt.si/napovednik-dogodkov/september-2026-v-botanicnem-vrtu)<br>`delavnica`<br>`event_20260930_1700_97e81ddad9be` | [Botanični vrt, Ižanska cesta 15](https://maps.google.com/?q=Botani%C4%8Dni%20vrt%2C%20I%C5%BEanska%20cesta%2015%20Ljubljana) | `?` / 10 €<br> |
| 30.09.2026 17:00 | [Branje za otroke: Lokomotiva](https://www.mklj.si/dogodek/branje-za-otroke-narisi-mi-obliko-2/)<br>`pravljice`<br>`event_20260930_1700_e8f1be44cd1a` | [Knjižnica Šiška (MKL)](https://maps.google.com/?q=Knji%C5%BEnica%20%C5%A0i%C5%A1ka%20%28MKL%29%20Ljubljana) | `?` / 🆓<br> |

## Hidden

_None._

## Filtered

| When | Event / ID | Place | Age / price / notes |
|---|---|---|---|
| ? | [2. Dnevi ozimnice v Ljubljani (dopoldanski del, 09:00)](https://www.ljubljana.si/sl/aktualno/dogodki/2-dnevi-ozimnice-v-ljubljani-6aa1089611378) | ? | Dopoldanski del (09:00) je namenjen izključno vrtčevskim/šolskim skupinam, ne javnosti — ne prestane attendance testa iz discovery.md. Popoldanski javni del (16:00) je že v bazi. |
| ? | [Alfa Rally (28.11.2026)](https://svamz.com/koledar-dogodkov/) | ? | Datum potrjen, a prizorišče še ni objavljeno nikjer (preverjeno tudi na kluba lastni strani) — premalo za potrditev dogodka. |
| ? | [Celjski mali maraton – otroški in družinski tek (8.11. 11:00)](https://fatburn.si/celjski-mali-maraton/) | ? | Ujema se z obstoječim hidden\_events zapisom celje\_20261108\_1100 ('not interested'). Ni ponovno oddano. |
| ? | [Dan Kobilarne Lipica, septembrska izvedba](https://www.lipica.org/en/events/) | ? | Uradni koledar za jesen 2026 kaže le dogodek 12. septembra (Dan vrnitve Primorske), ki je zunaj okna, ne pravi 'Dan Kobilarne' odprtih vrat. Brez potrjenega jesenskega termina. |
| ? | [Filharmonija Mladih ušes (Young Ears), 3.10. in 5.12.2026](https://filharmonija.si/en/concerts/program/) | ? | Potrjeno razprodano, brez možnosti nakupa posamezne vstopnice — abonma-only, ne prestane single-ticket carve-outa. |
| ? | [Friderik in zmaj (3.10. 17:00, Ljubljanski grad)](https://www.ljubljanskigrad.si/sl/dogodki/friderik-in-zmaj/) | ? | Ujema se z obstoječim hidden\_events zapisom grad\_20261003\_1700 ('not interested'). Ni ponovno oddano. |
| ? | [Interaktivno družinsko vodenje v Vili Zlatica (3.10. 11:00)](https://mgml.si/sl/dogodki/) | ? | Ujema se z obstoječim hidden\_events zapisom vilazlatica\_20261003\_1100 ('not interested'). Ni ponovno oddano. |
| ? | [Jesenske počitnice (Ljubljanski grad, 26.–30.10.)](https://www.ljubljanskigrad.si/) | ? | Celodnevni varstveni program brez spremstva odraslih, starost 6–9 let — mnogodnevni tabor po discovery.md §1 pravilo 3 / attendance test. |
| ? | [Kinobalon 'Prvič v kino': Miška gre na goro (10.10. 10:00)](https://www.kinodvor.org/film/miska-gre-na-goro/) | ? | Ujema se z user\_rules exclude\_keywords ('Kinobalon \\'Prvič v kino\\': Miška gre na goro') in hidden\_events kinodvor\_20261010\_1000. Poznejše oktobrske/novembrske projekcije istega filma so druge priložnosti in ostajajo v bazi. Ni ponovno oddano. |
| ? | [Kinobalon 'Prvič v kino': Samo in Julija (3.10. 10:00)](https://www.kinodvor.org/film/samo-in-julija/) | ? | Ujema se z obstoječim hidden\_events zapisom kinodvor\_20261003\_1000 ('not interested'). Ni ponovno oddano. |
| ? | [Mednarodni Classic Rally – Od Štorkle do Torklje](https://www.zveza-svs.si/wp-content/uploads/2026/01/KOLEDAR-Zveze-SVS-2026.pdf) | ? | Organizator datuma še ni določil (zapisano kot '10.10. ali 17.10.2026'), prizorišče ni objavljeno — premalo za potrditev. |
| ? | [Mednarodni orgelski cikel Ljubljana Polje 2026 (4. koncert)](https://www.ljubljana.si/sl/aktualno/dogodki/mednarodni-orgelski-cikel-ljubljana-polje-2026-4-koncert-6ab2783c6a363) | ? | Večerni (20:00) orgelski recital za odraslo publiko, brez družinskega konteksta. |
| ? | [Plesna pravljica: Mišja šola (2.10. 18:00, Citypark)](https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/) | ? | Ujema se z obstoječim hidden\_events zapisom citypark\_20261002\_1800 ('not interested'). Ni ponovno oddano. |
| ? | [Praznik sira in vina (24.10., Bohinjska Bistrica)](https://www.mojaobcina.si/bohinj/dogodki/praznik-sira-in-vina-5.html) | ? | Degustacijski dogodek za odrasle (vino, sir, glasba za vzdušje), brez otroškega programa — pass 2's destination-value/attendance test ne prestane. |
| ? | [Ura pravljic (več knjižnic, 1.–6. 10.)](https://www.mklj.si/otroci/) | ? | Ujema se z obstoječimi hidden\_events zapisi (not interested): Šentvid, Prežihov Voranc, Škerl, Glinškova ploščad, Mazovec, Polje (vsi 1.10. 17:00), Levstik (5.10. 18:00), Podpeč in Otona Župančiča (6.10. 17:00). Ni ponovno oddano. |
| ? | [Ustvarjalna delavnica: Mucka, Putka, Slon (4.10. 11:00, MAO)](https://mao.si/dogodek/ustvarjalna-delavnica-mucka-putka-slon/) | ? | Ujema se z obstoječim hidden\_events zapisom mao\_20261004\_1100 ('not interested'). Ni ponovno oddano. |
| ? | [Zgodba o Šimnu Sirotniku (1.10. in 3.10.)](https://www.lgl.si/zgodba-o-simnu-sirotniku) | ? | LGL-jeva lastna objava označuje predstavo kot 'odraslo', 15+ — explicit 'not for children' po discovery.md §1. |

## Deferred

_None._

## Unchanged

_None._

## Unconfirmed Leads

| Lead | Source | Missing |
|---|---|---|
| Ana Plamenita 2026 | [source](https://www.anamonro.si/festivali/festivalski-program/) | Noben 2026 datum ni bil najden; samo 2025-11-08 je potrjen zgodovinsko. |
| Prižig prazničnih lučk 2026 | [source](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani) | 2026 datum še ni objavljen; podstran dogodka je JS-rendered in ne vrne vsebine; zadnji potrjeni vzorec je 28.11.2025 17:00. |
| Koča dedka Mraza / Sprevodi dedka Mraza / Ana Mraz / Čarobni gozd 2026 datumi | [source](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani) | Sezona (27.11.2026–15.1.2027) je potrjena, a posamezne podstrani dogodkov so JS-rendered prazne lupine brez konkretnih datumov/ur za letošnjo sezono. |
| Silvestrovanje za otroke 2026-12-31 | [source](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/silvestrovanje-za-otroke) | 2026 stran je prazna lupina brez datuma/ure; lanski vzorec (16:00–17:30, Kongresni trg) ni potrjen za letos. |
| Miklavžev sprevod 2026-12-05 | [source](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/miklavzev-sprevod) | Enak JS-rendering problem; letošnja ura/pot nista neodvisno potrjena. |
| ZOO Ljubljana – Noč čarovnic 2026 | [source](https://www.zoo.si/novice) | Stran je client-rendered Next.js app; curl z UA vrne JSON novic arhiv, a brez vsebine za oktober 2026 do zdaj. |
| Citypark brezplačno gledališče – novembrska in decembrska izvedba | [source](https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/) | Samo 2.10. predstava je objavljena; naslednje mesečne izvedbe se objavijo šele teden vnaprej. |
| Ta veseli dan kulture 2026 – imena sodelujočih ljubljanskih ustanov | [source](https://www.gov.si/taveselidan) | Uradna stran še vedno kaže program za 2025; nobena ljubljanska ustanova (MGML, NG, SEM, MAO) še ni objavila 2026 programa za 3.12. |
| Martinovo v Šmartnem (Brda), otroški kotiček | [source](https://www.brda.si/en/events/2026061312313870/) | Datum (7.–8. 11.) potrjen, a stran ne navaja konkretnega otroškega programa, ure ali cene za letošnjo izvedbo. |
| Magični grad noči čarovnic (grad Žužemberk) | [source](https://www.zgodovinska-mesta.si/prireditve/) | Najden je le opis preteklih izvedb; 2026 datum ni objavljen. |

## Sources

| Source | Pass | Status | Checked | Notes |
|---|---|---|---|---|
| [http://www.motoclub-mak.si/](http://www.motoclub-mak.si/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [http://www.oldtimerstajerska.com/](http://www.oldtimerstajerska.com/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://svamz.com/koledar-dogodkov/](https://svamz.com/koledar-dogodkov/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.adria-classic.si/](https://www.adria-classic.si/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.alfa-klub.com/](https://www.alfa-klub.com/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.bled.si/sl/prireditve/](https://www.bled.si/sl/prireditve/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.motoklub-veterani.si/](https://www.motoklub-veterani.si/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.oldtimer-skofljica.com/](https://www.oldtimer-skofljica.com/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.portoroz.si/en/events/](https://www.portoroz.si/en/events/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zveza-svs.si/obvestila/](https://www.zveza-svs.si/obvestila/) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zveza-svs.si/wp-content/uploads/2026/01/KOLEDAR-Zveze-SVS-2026.pdf](https://www.zveza-svs.si/wp-content/uploads/2026/01/KOLEDAR-Zveze-SVS-2026.pdf) | avto\_moto | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://filharmonija.si/en/concerts/program/](https://filharmonija.si/en/concerts/program/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://napovednik.com/glasba](https://napovednik.com/glasba) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://napovednik.com/glasba/klasicna](https://napovednik.com/glasba/klasicna) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://napovednik.com/glasba/narodnozabavna](https://napovednik.com/glasba/narodnozabavna) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6261](https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6261) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6262](https://napovednik.com/za-otroke/aktivnosti-za-otroke/madzarsko-slovenska-glasbena-ura-za-otroke-6262) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.cd-cc.si/kultura/za-mlade-in-sole/katalena-enci-benci-katalenci-0](https://www.cd-cc.si/kultura/za-mlade-in-sole/katalena-enci-benci-katalenci-0) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kino-bezigrad.si/predstava/koncert-repki-2/](https://www.kino-bezigrad.si/predstava/koncert-repki-2/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kino-bezigrad.si/predstava/koncert-z-obiskom-bozicka-bozicni-repki/](https://www.kino-bezigrad.si/predstava/koncert-z-obiskom-bozicka-bozicni-repki/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/nedeljski-popoldnevi/repki-1/](https://www.sititeater.si/nedeljski-popoldnevi/repki-1/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/nedeljski-popoldnevi/repki-2/](https://www.sititeater.si/nedeljski-popoldnevi/repki-2/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/sobotni-dopoldnevi/cudezni-kljuc-premiera/](https://www.sititeater.si/sobotni-dopoldnevi/cudezni-kljuc-premiera/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/sobotni-dopoldnevi/glasbocasnice/](https://www.sititeater.si/sobotni-dopoldnevi/glasbocasnice/) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/zakljucni-koncert-tridnevne-delavnice-za-100-najmlajsih-violoncelistov-iz-vse-slovenije](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/zakljucni-koncert-tridnevne-delavnice-za-100-najmlajsih-violoncelistov-iz-vse-slovenije) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zurnal24.si/popotnik/vau-to-so-v-ljubljani-pripravili-za-najmlajse-397876](https://www.zurnal24.si/popotnik/vau-to-so-v-ljubljani-pripravili-za-najmlajse-397876) | concerts\_generic | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://365.rtvslo.si/oddaja/ribic-pepe/21235734](https://365.rtvslo.si/oddaja/ribic-pepe/21235734) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://glasbenadezela.si/nastopi/](https://glasbenadezela.si/nastopi/) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://ribicpepe.si](https://ribicpepe.si) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.alenkakolman.si](https://www.alenkakolman.si) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.drama.si/en/repertoire](https://www.drama.si/en/repertoire) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.eventim.si/artist/neca-falk/](https://www.eventim.si/artist/neca-falk/) | concerts\_watchlist | failed | 2026-10-01T12:00:00+02:00 | 503/connection failure, Akamai |
| [https://www.kino-bezigrad.si/predstave-in-delavnice/](https://www.kino-bezigrad.si/predstave-in-delavnice/) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mojekarte.si/si/iskanje.html](https://www.mojekarte.si/si/iskanje.html) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.romanakr.com](https://www.romanakr.com) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.rtvslo.si/opz-in-mpz/](https://www.rtvslo.si/opz-in-mpz/) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.rtvslo.si/orkestra-in-zbora/koncertni-koledar](https://www.rtvslo.si/orkestra-in-zbora/koncertni-koledar) | concerts\_watchlist | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://mgml.si/sl/mestna-galerija/dogodki/2529/2026-10-10/15-00/brezplacno-vodstvo-po-razstavi-za-otroke-in-druzine/](https://mgml.si/sl/mestna-galerija/dogodki/2529/2026-10-10/15-00/brezplacno-vodstvo-po-razstavi-za-otroke-in-druzine/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://mgml.si/sl/plecnikova-hisa/dogodki/2534/2026-10-10/16-00/z-igro-do-dediscine-2026-brezplacno-vodstvo-za-druzine-po-plecnikovi-hisi/](https://mgml.si/sl/plecnikova-hisa/dogodki/2534/2026-10-10/16-00/z-igro-do-dediscine-2026-brezplacno-vodstvo-za-druzine-po-plecnikovi-hisi/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://sms-muzeji.si/z-igro-do-dediscine-2/](https://sms-muzeji.si/z-igro-do-dediscine-2/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://visitzirovnica.si/en/france-preseren-birthhouse-vrba/](https://visitzirovnica.si/en/france-preseren-birthhouse-vrba/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.belakrajina.si/sl/obiscite/odprta-vrata/spominska-hisa-otona-zupancica-vinica/](https://www.belakrajina.si/sl/obiscite/odprta-vrata/spominska-hisa-otona-zupancica-vinica/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.etno-muzej.si/sl/novice/z-igro-do-dediscine-v-sem-brezplacni-programi-za-otroke-in-druzine](https://www.etno-muzej.si/sl/novice/z-igro-do-dediscine-v-sem-brezplacni-programi-za-otroke-in-druzine) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.gov.si/taveselidan](https://www.gov.si/taveselidan) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljanskigrad.si/sl/dogodki/](https://www.ljubljanskigrad.si/sl/dogodki/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mg-lj.si/si/dogodki/4446/program-javnih-vodstev-s-kustatorjem-razstave/](https://www.mg-lj.si/si/dogodki/4446/program-javnih-vodstev-s-kustatorjem-razstave/) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ng-slo.si/si/dogodki](https://www.ng-slo.si/si/dogodki) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ng-slo.si/si/dogodki/prost-vstop-na-stalno-zbirko-za-druzine-z-otroki?id=6709](https://www.ng-slo.si/si/dogodki/prost-vstop-na-stalno-zbirko-za-druzine-z-otroki?id=6709) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.nms.si/si/dogodki](https://www.nms.si/si/dogodki) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.nms.si/si/dogodki/2026/10/12403-En-dan-Trije-muzeji-Ena-ploscad](https://www.nms.si/si/dogodki/2026/10/12403-En-dan-Trije-muzeji-Ena-ploscad) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.nms.si/si/dogodki/2026/10/12404-Z-igro-do-dediscine](https://www.nms.si/si/dogodki/2026/10/12404-Z-igro-do-dediscine) | free\_entry | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://he.si/](https://he.si/) | ljubljana | failed | 2026-10-01T12:00:00+02:00 | connection failed outright, worse than prior 503 |
| [https://knjizni-sejem.si/](https://knjizni-sejem.si/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://knjizni-sejem.si/obisk/](https://knjizni-sejem.si/obisk/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://lgl.mojekarte.si/en/all.html](https://lgl.mojekarte.si/en/all.html) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://ljubljanskimaraton.si/lumpi-tek](https://ljubljanskimaraton.si/lumpi-tek) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://mao.si/dogodek/medgeneracijsko-srecalisce-delavnica-izdelovanja-znack/](https://mao.si/dogodek/medgeneracijsko-srecalisce-delavnica-izdelovanja-znack/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://mgml.si/sl/dogodki/](https://mgml.si/sl/dogodki/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://pionirski-dom.si/aktualno/festival-hokus-pokus-s-klemnom-janezicem/](https://pionirski-dom.si/aktualno/festival-hokus-pokus-s-klemnom-janezicem/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://pionirski-dom.si/aktualno/teden-odprtih-vrat-pionirskega-doma-2026/](https://pionirski-dom.si/aktualno/teden-odprtih-vrat-pionirskega-doma-2026/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.anamonro.si/festivali/festivalski-program/](https://www.anamonro.si/festivali/festivalski-program/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.cd-cc.si/kultura/za-mlade-in-sole](https://www.cd-cc.si/kultura/za-mlade-in-sole) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.cd-cc.si/kultura/za-mlade-in-sole/katalena-enci-benci-katalenci-0](https://www.cd-cc.si/kultura/za-mlade-in-sole/katalena-enci-benci-katalenci-0) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/](https://www.citypark.si/si/otroci/gledaliske-predstave-za-otroke/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.etno-muzej.si/sl/dogodki](https://www.etno-muzej.si/sl/dogodki) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.hisaotrok.si/koledar\_prireditev/list/](https://www.hisaotrok.si/koledar_prireditev/list/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kino-bezigrad.si/predstava/gledaliska-predstava-pika-nogavicka-in-potovanje-skozi-cas/](https://www.kino-bezigrad.si/predstava/gledaliska-predstava-pika-nogavicka-in-potovanje-skozi-cas/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kino-bezigrad.si/predstava/nov-muzikal-romane-krajncan-kako-je-mravljica-postala-huda/](https://www.kino-bezigrad.si/predstava/nov-muzikal-romane-krajncan-kako-je-mravljica-postala-huda/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kino-bezigrad.si/predstave-in-delavnice/](https://www.kino-bezigrad.si/predstave-in-delavnice/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.kinodvor.org/kinobalon/](https://www.kinodvor.org/kinobalon/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.lgl.si/spored-predstav](https://www.lgl.si/spored-predstav) | ljubljana | failed | 2026-10-01T12:00:00+02:00 | 503 again this run |
| [https://www.ljubljana.si/sl/aktualno/dogodki/11-medeni-dan-6aa113901ec1a](https://www.ljubljana.si/sl/aktualno/dogodki/11-medeni-dan-6aa113901ec1a) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki/2-dnevi-ozimnice-v-ljubljani-6aa1089611378](https://www.ljubljana.si/sl/aktualno/dogodki/2-dnevi-ozimnice-v-ljubljani-6aa1089611378) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki/dan-odprtih-vrat-pgd-zgornji-kaselj-6aaa94dc4b0ec](https://www.ljubljana.si/sl/aktualno/dogodki/dan-odprtih-vrat-pgd-zgornji-kaselj-6aaa94dc4b0ec) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki/delavnica-peke-in-krasenja-medenjakov-6aa1180dc570c](https://www.ljubljana.si/sl/aktualno/dogodki/delavnica-peke-in-krasenja-medenjakov-6aa1180dc570c) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki/mednarodni-orgelski-cikel-ljubljana-polje-2026-4-koncert-6ab2783c6a363](https://www.ljubljana.si/sl/aktualno/dogodki/mednarodni-orgelski-cikel-ljubljana-polje-2026-4-koncert-6ab2783c6a363) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki/teater-za-telebana-6ab1f7dfde1b6](https://www.ljubljana.si/sl/aktualno/dogodki/teater-za-telebana-6ab1f7dfde1b6) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljana.si/sl/aktualno/dogodki?nrOfItems=100](https://www.ljubljana.si/sl/aktualno/dogodki?nrOfItems=100) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljanskigrad.si/](https://www.ljubljanskigrad.si/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljanskigrad.si/sl/dogodki/](https://www.ljubljanskigrad.si/sl/dogodki/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ljubljanskigrad.si/sl/dogodki/friderik-in-zmaj/](https://www.ljubljanskigrad.si/sl/dogodki/friderik-in-zmaj/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.malaulica.si/sl/aktivnosti](https://www.malaulica.si/sl/aktivnosti) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/beremo-z-nasmehom-s-psicko-luno-6/](https://www.mklj.si/dogodek/beremo-z-nasmehom-s-psicko-luno-6/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/dezela-zmajev-4/](https://www.mklj.si/dogodek/dezela-zmajev-4/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster-2/](https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster-2/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster/](https://www.mklj.si/dogodek/mint-camera-obscura-matevz-paternoster/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev-nina-ambroz-2/](https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev-nina-ambroz-2/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev/](https://www.mklj.si/dogodek/mint-kako-je-bilo-ko-se-ni-bilo-sivalnih-strojev/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-misija-racunalnik-od-abakusa-do-racunalnika-rudi-majerle/](https://www.mklj.si/dogodek/mint-misija-racunalnik-od-abakusa-do-racunalnika-rudi-majerle/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/mint-misija-se-slisimo-radioamaterstvo-in-komunikacija-nekoc/](https://www.mklj.si/dogodek/mint-misija-se-slisimo-radioamaterstvo-in-komunikacija-nekoc/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/otroski-knjizni-klub-pravljicna-urica-za-otroke-ki-ne-obiskujejo-vrtca/](https://www.mklj.si/dogodek/otroski-knjizni-klub-pravljicna-urica-za-otroke-ki-ne-obiskujejo-vrtca/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/soncnice-2/](https://www.mklj.si/dogodek/soncnice-2/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/tetka-jesen-lutke-pika-poka-2/](https://www.mklj.si/dogodek/tetka-jesen-lutke-pika-poka-2/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-249/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-249/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-250/2026-10-21/](https://www.mklj.si/dogodek/ura-pravljic-250/2026-10-21/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-258/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-258/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-270/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-270/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-273/2026-10-22/](https://www.mklj.si/dogodek/ura-pravljic-273/2026-10-22/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-278/2026-10-22/](https://www.mklj.si/dogodek/ura-pravljic-278/2026-10-22/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-280/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-280/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-282/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-282/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-286/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-286/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-cevljar-mojster-ki-je-obul-svet-petra-kozjan/](https://www.mklj.si/dogodek/ura-pravljic-cevljar-mojster-ki-je-obul-svet-petra-kozjan/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-14/2026-10-21/](https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-14/2026-10-21/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-15/2026-10-06/](https://www.mklj.si/dogodek/ura-pravljic-v-angleskem-jeziku-15/2026-10-06/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-v-nemskem-jeziku-5/2026-10-07/](https://www.mklj.si/dogodek/ura-pravljic-v-nemskem-jeziku-5/2026-10-07/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-13/](https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-13/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-27/](https://www.mklj.si/dogodek/ura-pravljic-z-igranjem-2-6/2026-10-27/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mklj.si/dogodki/](https://www.mklj.si/dogodki/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.ng-slo.si/si/dogodki/prost-vstop-na-stalno-zbirko-za-druzine-z-otroki?id=6709](https://www.ng-slo.si/si/dogodki/prost-vstop-na-stalno-zbirko-za-druzine-z-otroki?id=6709) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/cene-vstopnic/](https://www.sititeater.si/cene-vstopnic/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.sititeater.si/sobotni-dopoldnevi/](https://www.sititeater.si/sobotni-dopoldnevi/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani](https://www.visitljubljana.com/sl/obiskovalci/prireditve/prireditve-v-ljubljani/december-v-ljubljani) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zoo.si/novice](https://www.zoo.si/novice) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zoo.si/ponudba](https://www.zoo.si/ponudba) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zpms.si/programi/teden-otroka/](https://www.zpms.si/programi/teden-otroka/) | ljubljana | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://fatburn.si/celjski-mali-maraton/](https://fatburn.si/celjski-mali-maraton/) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://kavbojska-dezela.si/dogodki/](https://kavbojska-dezela.si/dogodki/) | slovenia | failed | 2026-10-01T12:00:00+02:00 | new sgcaptcha bot-block, was ok 9/28 |
| [https://novomesto21.si/](https://novomesto21.si/) | slovenia | failed | 2026-10-01T12:00:00+02:00 | JS SPA, empty to curl/WebFetch |
| [https://www.babycenter.si/blog/vabljeni-na-hura-druzinski-dan](https://www.babycenter.si/blog/vabljeni-na-hura-druzinski-dan) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.brda.si/en/events/2026061312313870/](https://www.brda.si/en/events/2026061312313870/) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.finishers.com/pl/e/polmaraton-w-novo-mesto](https://www.finishers.com/pl/e/polmaraton-w-novo-mesto) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.lipica.org/en/events/](https://www.lipica.org/en/events/) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mojaobcina.si/bohinj/dogodki/bofejst---jesenski-otroski-festival.html](https://www.mojaobcina.si/bohinj/dogodki/bofejst---jesenski-otroski-festival.html) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.mojaobcina.si/bohinj/dogodki/praznik-sira-in-vina-5.html](https://www.mojaobcina.si/bohinj/dogodki/praznik-sira-in-vina-5.html) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.postojnska-jama.eu/en/tickets/living-nativity-scenes/](https://www.postojnska-jama.eu/en/tickets/living-nativity-scenes/) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |
| [https://www.zgodovinska-mesta.si/prireditve/praznik-kakijev-v-strunjanu/](https://www.zgodovinska-mesta.si/prireditve/praznik-kakijev-v-strunjanu/) | slovenia | ok | 2026-10-01T12:00:00+02:00 |  |

## Runtime Notes

- \[coordinator\] Six research passes were dispatched as parallel background agents, each reading routine.md/discovery.md/links.md plus its pass-specific reference file and doing live WebSearch/WebFetch/curl research; this session merged, cross-checked and applied their reports. No agent touched db.json or ran scripts directly.
- \[coordinator\] Heavy overlap with the 2026-09-28 run was expected (only 3 days prior) and confirmed: most near-term Ljubljana-area finds already existed in db.json under matching title/time/venue and were not resubmitted as new, to keep the new/unchanged counts meaningful.
- \[coordinator\] Cross-checked every candidate against db.json's hidden\_events table and user\_rules.exclude\_keywords before staging. Found that this run's agents independently rediscovered 9 MKL 'Ura pravljic' occurrences, the MAO/Vila Zlatica/Citypark/Kinodvor/Ljubljanski grad ('Friderik in zmaj') items, and the Celjski mali maraton race that are explicitly hidden by the user — none were resubmitted (see filtered). One hidden match (Kinodvor 'Miška gre na goro' 10.10. 10:00) is hidden via a keyword rule anchored to its OLD title ('Kinobalon \\'Prvič v kino\\': ...'); this run's sources now publish it under a shortened title that the keyword rule would NOT automatically catch, so it was manually excluded here as a safety net. Flagging for links.md/AGENTS.md maintenance: title drift on a hidden show's own page can silently defeat a keyword-based hide.
- \[coordinator\] kino-bezigrad.si's Romana Krajnčan musical page: three independent fresh fetches this run (by the ljubljana, concerts\_generic and concerts\_watchlist passes) agree the page publishes no start time, contradicting the 17:00 stored on this record since the 2026-09-28 run. The concerts\_watchlist pass did a raw-HTML grep for time/price patterns and found none, concluding the prior run's 17:00 was most likely fabricated by a summarizing WebFetch rather than read from the page. Corrected back to time\_unknown this run. Recommend treating any time/price read from this venue's detail pages as unverified unless confirmed against raw HTML.
- \[coordinator\] Narodna galerija's existing record (ng\_20261006\_0000) had its url corrected from a puppet-show page to the venue's own dedicated free-entry announcement page per free\_entry pass's finding; price\_text's date range (6-11 Oct, one day later than the nationwide 5-11 Oct) was already correct and is unchanged.
- \[coordinator\] Praznik kakijev v Strunjanu's date is corrected from '10-12 Nov' (recorded 2026-09-24) to '13-15 Nov' (23rd edition) per a fresh, independently-agreeing live check of the same source family; programme is not yet published for this edition.
- \[ljubljana\] MOL calendar yield dropped to 37 events this run vs 54 on 2026-09-25 — confirmed complete (37 date-from spans counted directly), not a fetch/pagination artifact.
- \[ljubljana\] Hiša eksperimentov (he.si) got worse: outright connection failure (status 000) on both plain and full-browser-header curl attempts this run, vs 503 previously. Possibly down rather than merely bot-blocking.
- \[ljubljana\] Visit Ljubljana's per-event December sub-pages (Silvestrovanje, Čarobni gozd, Miklavžev sprevod, Dedek Mraz, Ana Mraz, Prižig prazničnih lučk) are JS-rendered and return the generic landing-page shell with zero event-specific text to curl or WebFetch; only the overview page (december-v-ljubljani) carries real text, at the 'these fixtures exist in this season' level, not per-event dates. Re-check closer to late November.
- \[slovenia\] kavbojska-dezela.si returned a new sgcaptcha bot-challenge (HTTP 202) to every attempt this run (2 UAs + cookie jar), unlike the clean 200 it gave on 2026-09-28. Not classified dead — the existing WILD KIDS record (already in db.json, confirmed 3 days ago with full detail) is retained as-is pending a working fetch method.
- \[concerts\_watchlist\] mojekarte.si's search endpoint is JS/AJAX-rendered; a static fetch returns only the category-taxonomy shell plus an always-present 'Ni zadetkov za' JS template string that is NOT a real no-results signal. Needs a JS-capable fetch to be useful at all.
- \[avto\_moto\] Timezone note: Oct 4/11/18 fixtures use +02:00 (before the 25 Oct DST change), Nov 1 / Dec 6 / Dec 26 fixtures use +01:00.
- \[avto\_moto\] New recurring pattern found, not yet in regions.md: Oldtimer klub Škofljica also runs an annual 'jesensko klubsko srečanje' in late September (out of this run's window), distinct from their October parts fair.
