# Design systems, component libraries and reference collections for a dark SimHub telemetry dashboard (as of Oct 2026)

Method note: ~35 tool calls (over the nominal budget because of breadth). Pinterest, Figma Community and Dribbble/Behance could NOT be fetched or surfaced (Pinterest returned an empty shell; `site:pinterest.com` search returned no Pinterest pages; Figma Community returned 403). Those parts are marked as gaps rather than filled from memory.

## 1. Which design systems have strong dark, data-dense, real-time patterns, and what transfers?

### Takeaway
The best transferable material is (a) Carbon's 8px "mini unit" scale and status/categorical colour rules, (b) Grafana's "Retro LCD" bar-gauge mode, which is almost exactly the project's comb-style segmented bar, (c) Android Automotive's "black base, one accent, opacity for hierarchy, 4.5:1 contrast" rules, and (d) aviation's reserved-colour doctrine. Web component code (Carbon, Blueprint, EUI, Tremor, Porsche) cannot run in SimHub and is only useful as token and anatomy reference. Apple's gauge guidance supports the current watchOS direction. Porsche and EUI licences are unverified or restrictive and need checking before copying any assets.

### Cited Findings

**IBM Carbon (strongest data-viz reference)**
- Carbon is Apache-2.0, ~9.6k stars; `@carbon/type` is "type tokens designed to pair with IBM Plex", `@carbon/layout` holds "layout units and spacing scale tokens" — [GitHub carbon-design-system/carbon](https://github.com/carbon-design-system/carbon)
- Carbon's base unit is an 8px square "mini unit". Fixed sizing scale (icons, tiles, vertical spacing) is 8, 16, 24, 32, 48, 64, 80 px (1x,2x,3x,4x,6x,8x,10x). Padding is fixed at 16px, and type aligns to the padding edge. Boxes are constrained to aspect ratios 1:1, 2:1, 2:3, 3:2, 4:3, 16:9 where possible — [Carbon 2x Grid](https://carbondesignsystem.com/elements/2x-grid/overview/)
- Carbon categorical data palette, to be applied in strict order "to maximize contrast between neighboring colors": Purple 70 #6929c4, Cyan 50 #1192e8, Teal 70 #005d5d, Magenta 70 #9f1853, Red 50 #fa4d56, Red 90 #570408, Green 60 #198038, Blue 80 #002d9c, Magenta 50 #ee538b, Yellow 50 #b28600, Teal 50 #009d9a, Cyan 90 #012749, Orange 70 #8a3800, Purple 50 #a56eff — [Carbon color palettes](https://carbondesignsystem.com/data-visualization/color-palettes/)
- Carbon status colours: danger Red 60 #da1e28, serious warning Orange 40 #ff832b, regular warning Yellow 30 #f1c21b, normal/success Green 60 #198038. The page states four-level status semantics (red / orange / yellow / green) — [Carbon color palettes](https://carbondesignsystem.com/data-visualization/color-palettes/)
- Dark-theme rule for sequential palettes: "In dark themes, the lightest color denotes the largest values" (opposite of light themes). Gradients should never replace a sequential palette. Diverging palettes: red-cyan for hot/cold, purple-teal for neutral — [Carbon color palettes](https://carbondesignsystem.com/data-visualization/color-palettes/)
- In Carbon's dark theme the first six categorical colours are reported (via a third-party wrapper doc, secondhand) as purple 60, cyan 40, teal 60, magenta 40, red 50, red 10 — [Socket.dev @polyxd/ds-carbon](https://socket.dev/npm/package/@polyxd/ds-carbon)
- Carbon Charts has a Gauge chart with `pairing`, `gradient` and `scale` colour options — [Carbon Charts gauge options](https://charts.carbondesignsystem.com/api/interfaces/gaugechartoptions)
- Figma: the free v11 library is in Figma Community, bundles four themes (White, Gray 10, Gray 90, Gray 100), plus IBM Color, Type Sets, Icon and Pictogram libraries; using it requires a Figma licence. Sketch/XD/Axure kits are no longer maintained — [Carbon Figma kit](https://carbondesignsystem.com/designing/kits/figma/) and [search summary](https://carbondesignsystem.com/designing/design-resources/)

**Grafana (closest anatomy to the project's segmented bars)**
- Grafana bar gauge has three display modes: Gradient, Retro LCD ("split into small cells that are lit or unlit") and Basic (single colour from the matching threshold). "Show unfilled area" (dark grey for the unfilled region) does not apply to Retro LCD. Thresholds set bar and value colours — [Grafana bar gauge docs (v9.5 archive)](https://archive.grafana.com/docs/grafana/v9.5/panels-visualizations/visualizations/bar-gauge/), [Amazon Managed Grafana](https://docs.aws.amazon.com/grafana/latest/userguide/v9-panels-bar-gauge.html)
- A third-party guide recommends Retro LCD for an "industrial control panel aesthetic" (informal) — [ENLYZE docs](https://docs.enlyze.com/en/integrations/grafana/visualisation-types/02-single-values)
- The "Saga" design-system URL I tried (grafana.github.io/grafana-ui-saga) returned 404, so I could not verify Saga's existence, scope or licence — see Gaps.

**Palantir Blueprint**
- Apache-2.0, ~22.2k stars, actively maintained (4,324 commits, 2026 copyright, v6.x), demo app shows light and dark themes — [GitHub palantir/blueprint](https://github.com/palantir/blueprint). Grid unit not confirmed from the page.

**Elastic EUI**
- Dual-licensed under Elastic License v2 and SSPL v1 (not OSI-approved permissive); ~6.4k stars — [GitHub elastic/eui](https://github.com/elastic/eui). Treat as reference-only; do not copy assets.

**Tremor**
- Apache-2.0 React/Tailwind/Radix library with "35+" components — [GitHub tremorlabs/tremor](https://github.com/tremorlabs/tremor). Tremor Labs was acquired by Vercel (Jan 2025; site banner says Tremor is joining Vercel) — [Wikipedia: Vercel](https://en.wikipedia.org/wiki/Vercel), [Walder Wyss](https://www.walderwyss.com/fr/news/2025-01-22_walder-wyss-advises-on-exit-of-y-combinator-startup-tremor-labs-inc-to-vercel-inc). Its docs list CategoryBar (progress/performance/status), BarList, Tracker (status strips) and spark charts (named SparkLine/Area/BarChart in the npm package) — [Tremor on tessl registry](https://tessl.io/registry/tessl/npm-tremor--react), [tremor.so](https://tremor.so/). Useful anatomy: Tracker = row of small coloured blocks (maps to a lap-by-lap or tyre-wear strip); CategoryBar = one bar split into coloured zones with a marker.

**Porsche Design System**
- Open on GitHub (~672 stars), "design tokens, robust web components and comprehensive guidelines". Licence is linked as LICENSE.md but the terms were not readable; no mention of font/brand restrictions — [GitHub porsche-design-system](https://github.com/porsche-design-system/porsche-design-system). v4 tokens use CSS `light-dark()` with `.scheme-dark` classes; token objects available in JS — [Porsche DS v4 tokens](https://designsystem.porsche.com/v4/tokens/introduction/), [theme](https://designsystem.porsche.com/v4/must-know/theme/). Do not reuse Porsche branding/fonts (Porsche Next) — not verified, treat as restricted.

**Apple HIG (watchOS / gauges)**
- Gauges: standard and capacity styles, circular and linear; accessory variants resemble watchOS complications. Labels should be succinct and describe the current value and both range endpoints; Apple suggests filling the path with a gradient to communicate purpose (e.g. red-to-blue for hot/cold) — [Apple HIG Gauges](https://developer.apple.com/design/human-interface-guidelines/gauges.md)
- Legacy ClockKit gauge styles: `.fill` (grows with the fraction) vs `.ring` (indicator at position on a full gauge) — [Apple tech talk 208](https://developer.apple.com/jp/videos/play/tech-talks/208/?time=661)
- Third-party summaries (unverified against Apple): complications should be understandable without context ("72F" not "72") and ship tinted and full-colour variants — [skills.cat watchOS guidelines](https://skills.cat/skills/project-kiri/kiri-friends/watchos-design-guidelines)

**Android Automotive OS (Material for cars)**
- Built from black so day and night themes stay consistent; grayscale palette with mid-greys because Material Grey 900 and up "approach brighter colors too quickly" and Grey 700 is "too bright for the auto context"; one official accent ("car accent", a more saturated blue); use colour minimally; elevation via grayscale tones; text/icon contrast at least 4.5:1; white opacity levels 88/72/56 for hierarchy; use 96% white at night; same colour for same item across views; don't use different colours to arbitrarily distinguish repeated components; don't overuse full opacity — [AAOS colour](https://developers.google.com/cars/design/automotive-os/design-system/color)
- Touch targets min 76x76dp and 24dp spacing (irrelevant for non-touch dash) — [AAOS media guidelines](https://developers.google.cn/cars/design/automotive-os/apps/media/guidelines-custom-screens?hl=en)

**Aviation / glass cockpit**
- Certified aviation reserves colours: red = warning requiring immediate awareness, amber/yellow = caution — [Kitplanes](https://www.kitplanes.com/buzzwords-human-factors/)
- G1000 PFD uses the "T" layout (attitude centre, airspeed left tape, altitude right, heading bottom); airspeed tape arcs: green = normal, yellow = caution, red = never-exceed — [Rotate Pilot](https://www.rotatepilot.com/guides/garmin-g1000-guide), [AOPA](https://www.aopa.org/news-and-media/all-news/2020/august/flight-training-magazine/ol-how-it-works-pfd)
- Screen clutter is linked to missed alerts — [Just Helicopters](https://justhelicopters.com/Articles-and-News/Community-Articles/Article/176028/What-Makes-a-Glass-Display-Really-Good)

**Motorsport hardware dashes**
- AiM MXG: default view RPM, gear, speed; up to four extra fields per page; ten multicolour RGB shift lights with per-gear thresholds; alarm LEDs solid/flashing with text message; layout built in Race Studio 3 — [GPR Direct MXG 1.3 Strada](https://www.gprdirect.com/aim-mxg-1-3-strada-7-tft-dash-display-with-road-icons/)
- Ferrari/Ansys HUD study: too much data can overload the driver, so placement matters — [Ansys HUD design](https://www.ansys.com/blog/hud-design)
- Car-dash design workshop uses 1920x720 frames as reference automotive size — [Univ. of Windsor](https://www.uwindsor.ca/science/computerscience/news/node/435286)

### Inferences
- Grafana "Retro LCD" is the direct vocabulary for the project's comb bars: lit cells use the threshold colour, unlit cells a dark-grey "off" tone. The existing `segmented_bar` already matches; the evolution is in how thresholds colour cells (per-cell vs whole-bar) and whether off cells are visible.
- Carbon's 8px mini-unit + {8,16,24,32,48,64,80} scale fits 1280x517 (517 is not a multiple of 8; 512 + 5 px or 64 rows of 8 with a 5 px slack). A 4px half-step is likely needed for dense tiles; Carbon scale is a good source for gutters and padding tokens in `theme.py`.
- Carbon's red/orange/yellow/green status ladder suggests a 4-level state scheme (ok / notice / warn / critical) per metric; AAOS and aviation both argue for keeping a single accent for identity and reserving red/amber strictly for state.
- AAOS opacity levels (88/72/56% white) translate to three fixed grey text tokens (primary/secondary/tertiary) which is how Grafite already works; the useful change is to formalise them as named tokens.
- Apple gauge guidance ("label both endpoints", gradient to communicate purpose) supports the watchOS evolution path but is low-fidelity for WPF: SimHub gradients are available on Rectangle fills but are heavier; use discrete stepped colours instead.
- Rejected as direct sources: Blueprint, EUI, Tremor code (not runnable; EUI licence restrictive). Use only Tremor's Tracker/CategoryBar anatomy and Blueprint's dark-density conventions.

### Gaps
- Grafana Saga: URL returned 404, existence/scope/licence unverified.
- shadcn/ui charts, Ant Design Charts: not researched (not fetched). From general knowledge shadcn charts are MIT wrappers around Recharts with CSS-variable colour tokens (`--chart-1..5`), unverified here.
- Carbon exact dark-theme (g100) hex background/layer values and type scale not extracted.
- Bloomberg Terminal design notes, Mercedes MBUX, Rivian/Tesla UI, CarPlay and Live Activities HIG pages, Garmin G1000 cyan/magenta conventions: not found in sources; no citations.
- Porsche Design System exact licence text and Figma kit availability not verified.
- Blueprint's grid unit (commonly cited as 4px) not confirmed from sources.

## 2. Open-source SimHub / sim-racing dashboards on GitHub

### Takeaway
Only one relevant repo is permissively licensed (mkstrike-overlays, MIT, but it is overlays, not a driver dash). TWF-Dash is CC BY-NC-SA 4.0 (reuse OK non-commercially with attribution and share-alike); Lovely Dashboard forbids commercial/marketing use and its UI design is under a custom licence; AIO-DASHBOARD has no stated licence (all rights reserved by default). Treat all as visual reference, not as asset sources.

### Cited Findings
- Lovely Sim Racing `lovely-dashboard`: multi-sim (ACC, iRacing, AC, AMS2, rF2, F1) DDU plus stream overlay; "True Dark Mode" theming with a blue variant; layouts from 800x286 to 1920x480 including round and square; ~751 stars, 553 commits, Plugin v3.6.0.2 / Dashboards v4.6.1; © 2026 Lovely Sim Racing LP. Licence is a separate "Software License" (lsr.gg/license); free to use but UI design is under that licence and commercial/marketing use is forbidden without consent — [GitHub lovely-dashboard](https://github.com/Lovely-Sim-Racing/lovely-dashboard). I was redirected to store.lsr.gg/pages/license and did not read the full text.
- `hakanuzunoglu/TWF-Dash`: 8-10 non-replica dashboards (main, WIDE, ULTRAWIDE, LITE, PURE RACE, RADAR, LAPTIMER, VERTICAL), supports iRacing, uses Rajdhani font (Google Fonts), shared `TWF_DASH_HELPER.js` and `TWF_DASH_CONFIG.json`, needs SimHub 8.3.7 and Romain Rob's plugins. Licence CC BY-NC-SA 4.0; third-party logos, fonts and plugins have their own terms — [GitHub TWF-Dash](https://github.com/hakanuzunoglu/TWF-Dash)
- `thekingm249/AIO-DASHBOARD`: ~18 sims incl. iRacing; 3 screens, 13 widgets triggered by action buttons, quick views for fuel/pit/energy/pace/damage/radar, variants with/without RPM LED strip; no licence stated; releases distributed separately — [GitHub AIO-DASHBOARD](https://github.com/thekingm249/AIO-DASHBOARD)
- `neonka/mkstrike-overlays`: free iRacing SimHub overlays (pit, radar, relative, standings), MIT licence, beta, Roboto font, 13 commits — [GitHub mkstrike-overlays](https://github.com/neonka/mkstrike-overlays)
- Other iRacing-only community dashes exist on RaceDepartment/SimHubDash (BKN dashboard requires the iRacing Extra Properties plugin; others of unclear licence) — [BKN dashboard](https://racedepartment.com/downloads/bkn-dashboard.68281/), [SimHubDash community](https://www.simhubdash.com/community-2/dashboard-templates/meekstaaas-iracing-dashboard-wonderset/)
- GitHub topic `simhub` lists these projects — [GitHub topic simhub](https://www.github.com/topics/simhub)
- SimHub official wiki covers DashStudio bindings, performance and template creation — [SHWotever/SimHub wiki](https://github.com/SHWotever/SimHub/wiki)

### Inferences
- Lovely's strengths per its own description: consistent information architecture across screen sizes and a "true dark" theme variant system; the evolutionary lesson is to expose theme variants (graphite / blue) from `theme.py` as one dict swap.
- Because TWF-Dash is non-commercial share-alike and the SF23 project is a personal, presumably non-commercial one, studying its structure is safe; copying code or art would pull in CC BY-NC-SA obligations. Recommended practice: borrow ideas (layout conventions, font choice like Rajdhani), not files.
- Most community dashes ship as `.djson`/zip releases rather than source in the repo, so inspecting them requires downloading releases (not done).

### Gaps
- Full text of Lovely licence not read; last-commit dates for all repos not visible.
- No visual inspection of screenshots was possible (text-only fetch), so design-language descriptions of these dashes beyond README text are not available.
- RaceDepartment/Overtake download pages were not fetched individually.

## 3. Figma Community files for racing dashboards / car HMI

### Takeaway
No Figma Community file could be verified: Figma Community pages returned 403 and web search surfaced mainly marketplace and portfolio items. Verified options are a paid $10 Gumroad racing dashboard (Figma/Sketch/XD) and Carbon's free Figma kit for token reference.

### Cited Findings
- "Racing Car Dashboard UI Concept": Gumroad, ~$10, one dashboard screen in Figma/Sketch/XD; fonts not included, image licence not included — [Gumroad arshakir](https://arshakir.gumroad.com/l/qCCGC)
- Automotive HMI Dashboards UI Pack is a Unity Asset Store package (not a Figma kit); source files on request — [Unity Asset Store](https://assetstore.unity.com/packages/2d/gui/automotive-hmi-dashboards-ui-pack-241087)
- Dribbble HMI collections and projects (some tagged Figma) show car HMI concepts but are not downloadable kits — [Dribbble LenYun HMI collection](https://dribbble.com/LenYun/collections/5646256-HMI), [Dribbble yanwr_](https://dribbble.com/yanwr_)
- Commercial sim dashes (MOZA CM2 5-inch, Simagic MagicDash 4, P1Sim Arnage portrait wheel display, Heusinkveld DisplayDash) show current commercial styling — [Traxion DisplayDash](https://traxion.gg/heusinkvelds-displaydash-is-a-sim-button-box-and-display-hybrid/), [Traxion Arnage](https://traxion.gg/the-p1sim-arnage-steering-wheel-has-a-portrait-screen-like-your-smartphone/), [MOZA CM2 retailer](https://www.jbhifi.co.nz/products/moza-cm2-hd-racing-dash)
- Carbon Figma kit (free, Community, Apache-2.0 system, needs Figma licence) — [Carbon Figma kits](https://carbondesignsystem.com/designing/kits/figma/)

### Inferences
- The project's Figma connection (mcp__Figma__*) could be used to search a specific named file once the user supplies a link; a blind Community crawl is not possible through WebFetch.
- Commercial Figma "dashboard concept" files rarely allow reuse of imagery; use them only for composition ideas.

### Gaps
- No verified Figma Community file URLs for racing HUD / steering wheel display; the Figma MCP in this session lists as requiring authentication (plugin:design:figma), so it was not used.
- Dribbble/Behance individual shots for "sim racing dashboard" not found by search.

## 4. Pinterest boards and recurring visual directions

### Takeaway
Pinterest could not be retrieved (fetch returned an empty page; `site:pinterest.com` search returned no Pinterest results), and the Dribbble/Behance fallback produced only a few usable links. Recurring directions below are therefore drawn from the verified product/portfolio sources and flagged as a thin evidence base.

### Cited Findings
- Pinterest search URL for "sim racing dashboard ui" returned only the word "Pinterest" (JS-rendered, blocked) — attempted fetch of pinterest.com/search/pins.
- Web search results for sim-racing dash UI are dominated by shops and reviews: fixed DDU-style dashes with configurable pages (lap delta, gear, fuel, tyres), wheel-mounted portrait screens putting key info at the top, MOZA's customizable UI system with community sharing, and an Android "SIM Dashboard" app with 200+ widgets shared by QR code — [gperformance.eu dashboards](https://gperformance.eu/collections/dashboards), [SimRacingCockpit guide](https://simracingcockpit.com/sim-racing-dashboard/), [BSimRacing SIM Dashboard](https://bsimracing.com/?p=77013), [MOZA RS072 CM2](https://www.gigaparts.com/moza-racing-game-rs072-cm2-racing-dash-touchscreen-display.html)
- DashForge (iOS/macOS) offers Drift Tyre HUD and Live Telemetry Graph widgets — [App Store DashForge](https://apps.apple.com/id/app/dashforge/id6772732368)
- Dribbble tags such as "HMI", "car dashboard", "figma", "after effects" collect car HMI concepts — [Dribbble HMI collection](https://dribbble.com/LenYun/collections/5646256-HMI), [Dribbble Devil](https://dribbble.com/Devil)

### Inferences
Directions that the verified sources collectively point to (not a statistical survey):
1. Dark "black-base, one accent" automotive minimalism (AAOS, Porsche-style) — matches the current Grafite; evolution = more disciplined opacity-based hierarchy and fewer colours.
2. Segmented/LCD "instrument" look (Grafana Retro LCD, AiM RPM LEDs) — a native fit for comb bars and shift lights.
3. Aviation PFD / tape-and-arc look (G1000) — semantic arcs (green/amber/red) and rigid grid, good for tyre temp, fuel, brake bias.
4. Watch-style rings and capacity gauges (Apple HIG) — current inspiration; WPF Gauge primitive supports it but circular space is expensive on a 517 px height.
5. Neon/HUD cyberpunk and glassmorphism are common in Dribbble concepts but I have no cited example; these are risky for WPF (blur/glow are not primitives) and for glance legibility, so treat them as lower priority.

### Gaps
- No Pinterest pins or boards could be retrieved or cited; no concrete example links for glassmorphism, neon, Swiss minimalism or retro-LCD styles. Suggest the user open the Pinterest searches manually (or provide pin links) and drop screenshots into `referencia-design/`.
- Behance case studies not retrieved.

## 5. Typography and spacing systems for a fixed 1280x517 canvas

### Takeaway
Carbon's 8px mini unit with a 16px padding rule and sizing scale 8-80 is the best documented, openly licensed spacing system; AAOS gives the contrast/opacity rules. Neither supplies a specific mono-numeric type scale suited to a 517 px height — that remains the project's own decision.

### Cited Findings
- Carbon 8px mini unit; sizing scale 8/16/24/32/48/64/80; fixed 16px padding; margins 0/16/24; gutters 32 total; type aligns to padding edge not on it; allowed aspect ratios 1:1, 2:1, 2:3, 3:2, 4:3, 16:9 — [Carbon 2x Grid](https://carbondesignsystem.com/elements/2x-grid/overview/)
- Carbon type is IBM Plex-paired (`@carbon/type`) — [GitHub carbon](https://github.com/carbon-design-system/carbon)
- AAOS: contrast at least 4.5:1, white-on-black hierarchy at 88/72/56% opacity — [AAOS colour](https://developers.google.com/cars/design/automotive-os/design-system/color)
- TWF-Dash uses Rajdhani; mkstrike uses Roboto — [TWF-Dash](https://github.com/hakanuzunoglu/TWF-Dash), [mkstrike](https://github.com/neonka/mkstrike-overlays)

### Inferences
- A 4px base with an 8px rhythm (Carbon's scale subdivided) fits tile paddings; 517 px height gives about 64 rows of 8 px; a 517 = 8x64 + 5 slack, so keep a 5 px offset or use 4px steps for vertical alignment. This arithmetic is mine.
- Type tiers worth formalising in `theme.py` (suggested, not cited): hero number, secondary number, label (uppercase small), unit (small grey), with unit-to-value ratio fixed (e.g. unit about 35-40% of value size) as in `value_unit`.
- Mono numerals (Arame Mono already) align with Carbon's use of IBM Plex Mono for data; no need to change font.

### Gaps
- No source provides type sizes for a 517 px-tall display; Carbon type token values (productive/expressive scale) were not extracted. AAOS type scale not found.
- IBM Plex Mono licence (SIL OFL) not verified here.

## Suggested three evolution paths (synthesis of the above; the proposals are my inference)

1. "Carbon data-viz and token anatomy": formalise `theme.py` as named tokens (surface/layer, text 88/72/56, spacing 4/8/16/24/32/48, 4-level status ladder from Carbon status colours), keep Grafite layout. Sources: Carbon, AAOS. Lowest risk, fully re-implementable.
2. "Motorsport / aviation HMI": reserved-colour doctrine (red/amber only for state), Grafana Retro LCD semantics for all bars (per-cell threshold colours, visible off-cells), tape/arc zones à la G1000, shift-light logic à la AiM. Sources: Grafana, aviation, AiM.
3. "Apple watchOS / capacity-gauge direction": capacity gauge fills, endpoint labels, tinted single-hue tiles; sourcing from Apple HIG gauges. Needs rounder corners/rings which fight the chamfered identity, so use sparingly.
