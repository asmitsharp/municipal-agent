# Municipal Intelligence Agent System Architecture
**India-Focused Urban Research Pipeline — Version 2.0 | Pilot City: Varanasi**

---

## Core Philosophy

This system is not a generic AI summarization workflow. It is a **municipal intelligence architecture** designed to reason about Indian cities as operational systems — analyzing incentives, cash flow, land, infrastructure, governance capacity, and service delivery together.

Three principles govern all agent design:

- **PRIMARY SOURCES ONLY** — every data point must trace to a government-issued primary document (CAG audit, budget, gazette, tender). No secondary source summaries.
- **INDIA-SPECIFIC REASONING** — agents must understand crore/lakh notation, state-transfer dependence, election-cycle distortions, informal economies, and overlapping agency jurisdiction.
- **CUMULATIVE KNOWLEDGE** — every extraction feeds a permanent structured database. Research compounds over time rather than being one-off.

---

## High-Level Pipeline

| Agent | Role |
|---|---|
| Agent 1 — Discovery | Crawls ONLY primary government URLs for raw documents |
| Agent 2 — Classification | Tags documents by type, fiscal year, department, language |
| Agent 3 — OCR + Extraction | Converts scanned PDFs to structured data with unit normalization |
| Agent 4 — Ontology | Unifies naming across cities, departments, fiscal heads |
| Agent 5 — Fiscal Analysis | Computes fiscal health metrics, ratios, benchmarks |
| Agent 6 — Governance Mapping | Maps institutional fragmentation and accountability gaps |
| Agent 7 — GIS + Spatial | Connects finance data to geography, ward maps, growth patterns |
| Agent 8 — Anomaly Detection | Detects political spending spikes, stagnation, data gaps |
| Agent 9 — Visualization | Generates charts, Sankey diagrams, ward heatmaps |
| Agent 10 — Narrative Synthesis | Produces Substack drafts and X/Twitter thread structures |
| Human Researcher | Final editorial judgment, ground-truth verification |

---

## Agent 1 — Document Discovery Agent

**Purpose:** Find and download primary government documents. Accepts NO secondary sources — no news articles, no think-tank PDFs, no Wikipedia. Every document must originate from an official government domain.

> ⚠️ If a document does not originate from a `.gov.in` or `.nic.in` domain, reject it. Never use news articles, blog posts, or research papers as primary data sources.

### Accepted Source Domains (Strict Whitelist)

| Source Type | Accepted URLs / Portals |
|---|---|
| Municipal Corporation | vmc.up.gov.in (Varanasi), lmc.up.nic.in (Lucknow), official `.gov.in`/`.nic.in` domains only |
| CAG India | cag.gov.in — audit reports for UP municipal bodies |
| Ministry of Housing | mohua.gov.in — AMRUT, Smart Cities, PMAY reports |
| Finance Commission | 15thfinancecommission.in — city-level transfer data |
| RBI | rbi.org.in — State Finances report (annual), municipal bond data |
| MoSPI / Census | censusindia.gov.in, mospi.gov.in — population, ward data |
| UP Govt Portal | up.gov.in, upneda.org.in, upgis.gov.in — state budgets, GIS data |
| National Data Portal | data.gov.in — open government datasets |
| NITI Aayog | niti.gov.in — SDG Urban Index, city rankings |

### Document Types to Collect

**Budget Documents**
- Annual Budget — Revenue Account and Capital Account (separate PDFs in most cities)
- Revised Estimates vs Actuals — look for `संशोधित अनुमान` in Hindi-language versions
- Demand for Grants — department-level breakdown
- Finance Committee Meeting Minutes — contains amendment discussions

**Audit & Accountability Documents**
- CAG Performance Audit Reports — search cag.gov.in for "urban local bodies Uttar Pradesh"
- CAG Compliance Audit Reports — annual, lists financial irregularities by department
- Internal Audit Reports — sometimes published on VMC website under Transparency Portal
- Utilization Certificates for Central Grants — confirms if AMRUT/Smart City funds were actually used

**Planning & Development Documents**
- Master Plan (Development Plan) — Varanasi Master Plan 2031 from VDA (Varanasi Development Authority)
- Ward-level GIS maps — from SVAMITVA scheme portal or upgis.gov.in
- Smart Cities Mission Project Reports — smartcities.gov.in for Varanasi's SCM proposals
- AMRUT 2.0 City Water Action Plan — from mohua.gov.in

**Tax & Property Data**
- Property Tax Demand Register — if published on VMC transparency portal
- Property Tax Collection Efficiency Reports — sometimes in CAG audit annexures
- Trade License Register — commercial property tax base indicator
- Advertisement Tax Registers — from VMC finance department

### Discovery Steps

1. **Seed URLs** — Start with vmc.up.gov.in. Navigate to Finance, Budget, Reports, Transparency sections. Catalog every PDF link found.
2. **CAG Scrape** — Go to cag.gov.in → Reports → State Governments → Uttar Pradesh → Local Bodies. Download all available audit reports.
3. **MOHUA Scrape** — Go to mohua.gov.in → AMRUT → City Reports. Filter for Varanasi. Download all quarterly and annual reports.
4. **Archive Fallback** — If current website is broken, check web.archive.org for snapshots of vmc.up.gov.in from the past 3 years.
5. **Version Control** — Store each PDF with filename format: `{city}_{doc_type}_{fiscal_year}_{source}_{download_date}.pdf`

### India-Specific Failure Modes

> ⚠️ VMC website frequently returns 404 on deep links. Always capture the parent directory listing, not just individual PDF links.

> ⚠️ Budget PDFs are often uploaded without a year in the filename. Extract fiscal year from document header — look for `वित्तीय वर्ष` or "Financial Year YYYY-YY" in the first 3 pages.

> ⚠️ Some VMC documents are password-protected or image-only scans. Flag these for the OCR pipeline and do not attempt text extraction directly.

---

## Agent 2 — Document Classification Agent

**Purpose:** Classify every incoming document into a strict taxonomy before any data extraction begins. Prevents misclassification from propagating errors downstream.

### Classification Taxonomy

| Category | Document Signals to Detect |
|---|---|
| Revenue Budget | Keywords: receipts, income, revenue account, आय, राजस्व, own tax, non-tax, grants |
| Capital Budget | Keywords: capital account, expenditure, schemes, पूंजीगत, project outlay, works |
| CAG Audit Report | Header: "Report of the Comptroller and Auditor General", chapter references to para numbers |
| Smart City Report | Issued by: Smart Cities Mission; contains project names, fund utilization tables |
| AMRUT Report | Issued by: AMRUT Mission; contains water/sewerage project-level data |
| Master Plan | Contains: zoning maps, land use tables, FAR regulations, development authority seal |
| Meeting Minutes | Format: agenda items, attendance, resolutions, dated signatures of councillors |
| Property Tax Record | Contains: demand vs collection tables, ward-wise breakdowns, arrear amounts |
| Tender Document | Contains: NIT number, estimated cost, technical specifications, bid deadline |

### Priority Ranking Logic

| Priority | Criteria |
|---|---|
| P1 — Critical | CAG Audit Reports (verified financials), Annual Budget Actuals, Property Tax Collection data |
| P2 — High | Revised Estimates, AMRUT utilization reports, Smart City fund disbursement records |
| P3 — Medium | Budget Estimates (not actuals), Master Plan documents, Ward GIS data |
| P4 — Low | Meeting minutes, tender documents, press releases from govt portals |
| P5 — Archive | Duplicate documents, older than 10 years, password-protected unreadable files |

### Language Tagging

- Tag every document as: `ENGLISH`, `HINDI`, `BILINGUAL`, or `MIXED` (tables in English, narrative in Hindi)
- Hindi documents must be flagged for specialized OCR — Devanagari script requires a different OCR model than Latin text
- For BILINGUAL documents, extract English tables first, then pass Hindi narrative sections to translation layer

### Duplicate Detection

- Hash every PDF on download (SHA-256). Reject documents with identical hashes.
- Near-duplicate detection: if two budgets have same fiscal year and city, compare page count and file size. Flag for human review if within 10% of each other.

---

## Agent 3 — OCR + Structured Extraction Agent

**Purpose:** Convert raw PDFs — including scanned images — into structured machine-readable data. The most technically complex agent. Output quality here determines the reliability of all downstream analysis.

### OCR Strategy by Document Type

| Document Type | Extraction Strategy |
|---|---|
| Text-native PDF (budget) | Direct text extraction via pdfplumber or pypdf. No OCR needed. |
| Scanned budget (image PDF) | Tesseract OCR with language pack `hin+eng`. Minimum 300 DPI input. |
| Hindi-only scanned PDF | Use Google Vision API or Azure OCR for Devanagari — Tesseract alone is insufficient. |
| Tabular CAG audit PDF | Camelot or Tabula for table extraction. Cross-check row/column sums. |
| Handwritten or stamp text | Flag for manual human review. Do not attempt automated extraction. |

### What to Extract — Revenue Budget

**Revenue Account — Own Source Revenue**
- Property Tax — Demand raised (₹ crore), Amount collected (₹ crore), Collection efficiency %
- Water Charges — Connections billed, Amount billed, Amount collected
- Advertisement Tax — Number of hoardings, Revenue collected
- Trade Licenses — Number issued, Revenue collected
- Parking Fees — Number of lots, Revenue collected
- Building Plan Approval Fees — Number of plans, Revenue collected
- Sewerage Charges — Connections, Amount collected

**Revenue Account — External Transfers**
- State Finance Commission Grants — amount, conditionality (tied/untied)
- 14th/15th Finance Commission Grants — Basic and Performance grants separately
- AMRUT Mission Grants — project-specific amounts, center:state:ULB split
- Smart Cities Mission Funds — project name, sanctioned amount, released amount, utilized amount
- State Government Scheme Transfers — list each scheme separately, do not aggregate
- Octroi Compensation (if applicable) — some UP cities still receive this

**Expenditure Account**
- Salary & Wages — permanent staff count, salary bill, pension liability
- Operation & Maintenance — by sector: roads, water supply, sewerage, parks, SWM separately
- Capital Works — project name, sanctioned cost, amount spent this year, cumulative spent
- Loan Repayment — principal and interest separately, lender name (LIC, HUDCO, Bank)
- Grants to Elected Bodies — ward development funds, councillor discretionary funds
- Establishment Expenses — office running costs, travel, utilities

### Unit Normalization — Critical Rules

> ⚠️ Indian municipal budgets use crore and lakh inconsistently, sometimes within the same document. Never assume units without verifying the column header.

| Raw Value Found | Normalized Output |
|---|---|
| ₹ 45.67 crore | 45,670,000 INR |
| Rs. 234.5 lakh | 23,450,000 INR |
| 45,67,000 | 4,567,000 INR (Indian comma grouping — note position of commas) |
| USD equivalent shown | Record both USD and INR, note exchange rate used |
| "N.A." or blank cell | Store as `NULL` with flag: `MISSING_DATA` |
| Negative value in budget | Store as negative, flag as `REQUIRES_REVIEW` — may indicate correction or refund |

### Data Quality Scoring

Every extracted record must carry a confidence score:

- **HIGH (0.9+):** Machine-readable PDF, values verified by row/column sum cross-check
- **MEDIUM (0.6–0.9):** OCR output, no sum verification possible, values appear internally consistent
- **LOW (<0.6):** Heavily scanned, Devanagari-heavy, partial table extraction — requires human review

---

## Agent 4 — Municipal Ontology & Normalization Agent

**Purpose:** Create a unified semantic layer across cities and years. Without this, the same concept appears under 20 different names across different budgets, making comparison impossible.

### Canonical Expenditure Head Mapping

| Raw Name (as seen in budget) | Canonical Category |
|---|---|
| Conservancy / Safai / SWM / Solid Waste Management / Sanitation Services | `SOLID_WASTE_MANAGEMENT` |
| Roads / Sadak / Marg Nirman / Road Works / PWD contribution | `ROAD_INFRASTRUCTURE` |
| Water Supply / Jal Pradan / Nal Jal Yojana / Drinking Water | `WATER_SUPPLY` |
| Sewerage / Naali / Drainage / Sewage Treatment / SEWER | `SEWERAGE_DRAINAGE` |
| Establishment / Salary / Wages / Pay & Allowances / वेतन | `STAFF_SALARIES` |
| Pension / GPF / Leave Encashment / Retirement Benefits | `PENSION_LIABILITY` |
| Loan Repayment / Debt Servicing / Debentures / Bond Interest | `DEBT_SERVICING` |
| Smart City / SCM / Smart Infrastructure / Digital City | `SMART_CITY_PROJECTS` |
| AMRUT / Urban Renewal / Mission Funds | `AMRUT_PROJECTS` |
| Parks / Green Spaces / Udyan / Horticulture | `PUBLIC_SPACES` |
| Street Lighting / Bijli / Illumination | `STREET_LIGHTING` |
| Health / Dispensary / Public Health / Malaria Control | `PUBLIC_HEALTH` |

### Cross-City Comparability Rules

- When mapping Varanasi to Lucknow budgets, create a `MAPPING_LOG` that records every non-obvious category match made.
- Never silently merge two categories. If uncertain, keep them separate and flag for human review.
- Fiscal year normalization: Convert all years to April–March format. If a document uses Jan–Dec, note the mismatch explicitly.

---

## Agent 5 — Fiscal Analysis Engine

**Purpose:** The analytical core of the system. Computes fiscal health metrics, benchmarks against national standards, and generates the quantitative insights that power research outputs.

### Core Metrics to Compute

| Metric | Formula / Definition | Healthy Benchmark |
|---|---|---|
| Own Source Revenue Ratio | Own Revenue ÷ Total Revenue × 100 | > 40% (most Indian ULBs are below 30%) |
| Property Tax Collection Efficiency | Collected ÷ Demand Raised × 100 | > 80% |
| Property Tax per Capita | Total PT Collected ÷ City Population | Compare to peer cities |
| Salary-to-Total Expenditure Ratio | Salary Bill ÷ Total Expenditure × 100 | < 35% (alert if > 50%) |
| Capital Expenditure Ratio | Capex ÷ Total Expenditure × 100 | > 30% indicates investment-oriented |
| Grant Dependence Ratio | External Grants ÷ Total Revenue × 100 | < 50% for fiscal autonomy |
| Debt Service Coverage | Surplus before Debt ÷ Annual Debt Payment | > 1.2x |
| Revenue per Capita | Total Own Revenue ÷ Population | Trend over 5 years more important than absolute |
| O&M Spending per Sector | Sector O&M ÷ Sector Asset Base | Tracks under-maintenance |

### Property Tax Deep Analysis

Property tax is the single most important own-source revenue for Indian municipalities. Analyze it separately:

- **Demand-Collection-Balance (DCB) Analysis:** Track demand raised, collected in current year, arrears from previous years, total arrears balance
- **Coverage Analysis:** Total assessed properties vs estimated total properties from census building data. Gap = untaxed properties.
- **Assessment Method:** Determine if city uses Annual Rental Value (ARV), Capital Value (CV), or Unit Area Value (UAV) system — each has different reform levers
- **Exemption Leakage:** Quantify value lost to exemptions (religious, government, charitable). This is often 30–50% of potential tax base.
- **Digitization Status:** Is there a GIS-linked property database? If yes, what % of properties are mapped?

### Fiscal Stress Signals — Automatic Red Flags

Alert immediately if any of the following are detected:

- Salary + Pension > 60% of total revenue: city is effectively a salary-distribution machine
- Own-source revenue declining in nominal terms for 2+ consecutive years
- Property tax collection efficiency < 50%: systemic failure in enforcement
- Capital expenditure < 10% of total spending: no investment in new infrastructure
- Debt service payments > 20% of own revenue: fiscal fragility
- Any grant-funded project with 0% utilization after 2 years: implementation failure

---

## Agent 6 — Governance Mapping Agent

**Purpose:** Map the institutional fragmentation that defines Indian cities. Most urban failures are not financial — they are coordination failures between overlapping agencies.

### Agencies to Map for Varanasi

| Agency | Controls | Source for Mapping |
|---|---|---|
| Varanasi Municipal Corporation (VMC) | Property tax, SWM, water supply, street lighting, parks | vmc.up.gov.in organogram |
| Varanasi Development Authority (VDA) | Land use approvals, building plan sanction, master plan enforcement | VDA annual reports |
| Jal Nigam (UP) | Underground sewerage, water treatment plants — often overlaps with VMC | upjn.org |
| PWD (Public Works Dept) | Major roads, bridges — city arterials NOT under VMC | uppwd.gov.in |
| Traffic Police (UP Police) | Signal management, parking enforcement on major roads | Separate from VMC |
| Smart Cities SPV | Smart City projects — separate Special Purpose Vehicle, bypasses VMC | smartcities.gov.in |
| Varanasi Smart City Ltd | Digital infrastructure, surveillance, tourism projects | Company filings + Smart City reports |
| BSNL / Power Corp | Utility ducts — dig-up coordination point | Not mapped publicly |
| Ganga Pollution Control Unit | River ghats, drainage into Ganga — overlaps with VMC sewerage | NGRBA reports |

### Governance Responsibility Matrix

For each service (roads, water, SWM, sewerage, transit), produce a 5-question responsibility matrix:

1. **Who plans it?** — which agency creates the DPR
2. **Who funds it?** — central / state / municipal / PPP
3. **Who builds it?** — executing agency
4. **Who operates it?** — post-completion O&M responsibility
5. **Who regulates it?** — accountability body

> ⚠️ In most Indian cities, the answer to all 5 questions is a DIFFERENT agency. This is the structural source of the infrastructure maintenance collapse.

---

## Agent 7 — GIS & Spatial Intelligence Agent

**Purpose:** Connect financial data to geography. Reveals which parts of the city are over-taxed, under-served, growing fastest, and most fiscally stressed.

### Primary Spatial Data Sources

| Data Layer | Source | What It Reveals |
|---|---|---|
| Ward boundaries | VMC ward map + upgis.gov.in + SVAMITVA portal | Tax collection by geography |
| Built-up area growth 2011–2024 | Bhuvan (bhuvan.nrsc.gov.in) satellite imagery | Where city is actually growing vs where infra exists |
| Road network | OSM + NRSC datasets | Road coverage gaps, last-mile connectivity |
| Unauthorized colonies | VDA enforcement records, Master Plan compliance maps | Areas with no tax base but existing population |
| Infrastructure coverage | AMRUT GIS data, mohua.gov.in city maps | Water/sewerage coverage vs population density |
| Flood zones / topography | NDMA, NRSC elevation data | Infrastructure risk and maintenance cost drivers |
| Land use actual vs planned | VDA Master Plan 2031 vs Bhuvan current imagery | Zoning violations, lost development potential |

### Key Spatial Analyses

- **Property Tax Gap Map:** Overlay assessed properties with total built-up area. Dark areas = untaxed growth zones.
- **Infrastructure Deficit Map:** Water/sewerage coverage overlaid with population density. Reveals service inequality.
- **Fiscal Stress by Ward:** Tax collection per ward vs ward population. Identifies ward-level fiscal winners and losers.
- **Sprawl Cost Model:** Calculate per-km cost of extending water/sewerage to new peri-urban areas. Shows why sprawl is fiscally toxic.

---

## Agent 8 — Trend & Anomaly Detection Agent

**Purpose:** Run across multi-year datasets to detect patterns that single-year analysis misses. Identifies political distortions, reform signals, and structural deterioration.

### Anomaly Detection Rules

| Anomaly Type | Detection Rule | Likely Explanation |
|---|---|---|
| Pre-election capex spike | Capital spending > 2x 3-year average in year before election | Political patronage, road-laying before votes |
| Property tax plateau | PT revenue flat for 3+ years despite population growth > 3%/yr | Political resistance to reassessment, exemption abuse |
| Grant absorption failure | Sanctioned grants > Utilized grants by > 40% for 2+ years | Implementation failure, contractor issues, approval delays |
| Salary creep | Salary-to-revenue ratio increasing > 2% per year for 3 years | Overstaffing, wage revision without revenue growth |
| O&M collapse | O&M spending on a sector declining while asset base grows | Assets being created but not maintained — future liability |
| Sudden new revenue head | Revenue category appearing for first time > ₹5 crore | New tax, new fee, or reclassification — investigate source |
| Negative capex year | Capital expenditure < previous year in nominal terms | Fiscal squeeze, grant stoppage, or data error |

### India-Specific Patterns to Watch

- Smart City funds often create a parallel capex spike that inflates the headline capex ratio — strip these out to see true municipal capex.
- Finance Commission grants are released in two tranches. A city may show full grant received but only partial utilization — check utilization certificates separately.
- UP local body elections affect Varanasi. Cross-reference election years (2017, 2022) with spending patterns across all 5 years of data.

---

## Agent 9 — Visualization Agent

**Purpose:** Generate the visual layer of the research. Visuals must be designed for Twitter/X and Substack — not for academic journals. Clarity over completeness.

### Visualization Specifications

| Chart Type | Data Required | Tool | Use Case |
|---|---|---|---|
| Sankey Diagram | Revenue sources → departments → outcomes | D3.js / SankeyMATIC | Revenue flow visual for Substack opening |
| Stacked Bar — Revenue | Own revenue vs grants vs other, 5 years | Python matplotlib / Observable | Grant dependence trend |
| Donut Chart — Expenditure | Salary / O&M / Capex / Debt breakdown | D3.js | Twitter thread — where money goes |
| Ward Heatmap | PT collection efficiency per ward + GIS boundaries | QGIS + Mapbox / Kepler.gl | Spatial inequality visual |
| Line Chart — Fiscal Trends | OSR ratio, PT efficiency, capex ratio — 5 years | Observable / matplotlib | Reform progress or regression |
| Governance Network Map | Agency nodes + service edges + jurisdiction overlaps | D3.js force-directed graph | Fragmentation explainer |
| DCB Waterfall Chart | Opening arrears + demand + collection + closing arrears | matplotlib | Property tax leakage visual |
| Infrastructure Coverage Map | Water/sewerage coverage % overlaid on population density | QGIS / Kepler.gl | Service gap visual |

### Twitter/X Design Constraints

- Every chart must be legible at **1200×675px** (Twitter card size)
- Maximum **5 data series** per chart — more creates unreadable legends on mobile
- Always include: city name, fiscal year, and source (e.g., `Source: CAG UP Audit 2023`) in chart footer
- Use high-contrast colors — avoid red/green combinations (colorblind accessibility)

---

## Agent 10 — Narrative Synthesis Agent

**Purpose:** Convert structured analysis into public-facing research. Must sound like an expert analyst who grew up in Varanasi — not like an AI assistant summarizing data.

### Substack Article Structure

| Section | Content |
|---|---|
| Hook (150 words) | A specific, concrete fact about Varanasi that surprises readers. E.g., "VMC collected ₹X crore in property tax — enough to build Y km of sewerage. Instead, ₹Z crore went to salaries." |
| Why People Misunderstand (200 words) | Common narrative vs what data actually shows. Challenge the lazy explanation. |
| Institutional Structure (400 words) | Governance map — who controls what. Include the agency overlap diagram. |
| The Numbers (600 words) | 5 years of revenue/expenditure data with annotated charts. Sankey diagram. DCB waterfall. |
| The Structural Problems (500 words) | Incentive failures, not individual failures. Property tax political economy. Grant dependency trap. O&M collapse. |
| Comparison (300 words) | Compare to one Indian peer city that performs better on the same metrics. Explain why. |
| Reform Pathways (300 words) | Specific, politically realistic reforms. Not utopian restructuring — incremental changes that have worked elsewhere. |
| Conclusion (150 words) | Reframe the opening fact. What changes if one metric improves by 20%. |

### X/Twitter Thread Structure (20 posts)

| Post # | Content |
|---|---|
| 1 — Hook | The one number that makes the whole story. Strong claim. Visual attached. |
| 2–3 — Context | Why Varanasi matters. Scale of city. What municipal corp actually is. |
| 4–6 — Revenue Structure | Where money comes from. Sankey or pie chart. Own revenue vs grants shock. |
| 7–9 — Property Tax | DCB waterfall. The gap between demand and collection. Why it happens. |
| 10–12 — Expenditure | Where money goes. Salary dominance. Capex starvation. O&M neglect. |
| 13–14 — Governance Fragmentation | Agency overlap diagram. Who controls roads vs water vs transit. |
| 15–16 — Anomaly | The one pattern that surprised you in the data. Pre-election spike or PT plateau. |
| 17–18 — Comparison | One Indian city that does this better. What they changed. |
| 19 — Reform | One specific, achievable reform. What it would unlock financially. |
| 20 — Call to Action | Link to Substack. Ask a question to drive replies. Cite your sources. |

### Voice & Tone Guidelines

- Write as if explaining to an intelligent friend who lives in Varanasi — not a western development economist
- Use INR crore as the default unit, not USD or million
- Name the specific streets, ghats, and localities affected by data findings — ground truth matters
- Never write "the government should" — write "here is what changed when Pune/Surat/Indore did X"
- If data is uncertain, say so explicitly — never smooth over gaps with confident-sounding prose

---

## Technical Stack

| Layer | Technology |
|---|---|
| Backend API | Go — agent orchestration, document pipeline management |
| Primary Database | PostgreSQL + PostGIS — financial data, spatial data, document metadata |
| Cache / Queue | Redis — job queue for OCR tasks, rate limiting for web crawls |
| Vector Store | Qdrant — embeddings for semantic search across extracted document text |
| OCR Engine | Tesseract (eng+hin) + Google Vision API for complex Devanagari |
| Table Extraction | Camelot / Tabula-py for structured PDF tables |
| Spatial Analysis | QGIS (manual), PostGIS (automated), Kepler.gl (visualization) |
| Visualization | Python matplotlib + D3.js + Observable notebooks |
| Document Storage | S3-compatible object storage — raw PDFs with versioning |
| AI Analysis Layer | LLM (Claude / GPT-4) for ontology mapping, narrative generation |
| Orchestration | Agent pipeline in Go — each agent as a separate service |

---

## Recommended First Pilot

> ✅ **City:** Varanasi Municipal Corporation | **Topic:** Fiscal Health Assessment | **Years:** FY2019–20 to FY2023–24

### Pilot Scope

- **Download:** VMC Annual Budgets (5 years) + Latest CAG UP Audit Report + AMRUT Varanasi utilization report
- **Extract:** Revenue structure, expenditure breakdown, property tax DCB, grant receipts
- **Compute:** Own-source revenue ratio, PT collection efficiency, salary ratio, capex ratio — all 5 years
- **Map:** Agency overlap for water supply (VMC vs Jal Nigam) and roads (VMC vs PWD)
- **Visualize:** Revenue Sankey (Year 1 vs Year 5), PT DCB waterfall, Salary creep line chart
- **Output:** 1 Substack article (2000 words) + 1 Twitter thread (20 posts) + 5 charts

### Success Criteria

| Metric | Target |
|---|---|
| Data traceability | 100% of numbers in article traceable to specific page of primary source document |
| Source quality | 0 secondary sources used in final analysis |
| Metric coverage | All 8 core fiscal metrics computed for minimum 3 years |
| Visualization count | Minimum 5 publication-ready charts |
| Content output | 1 Substack article + 1 20-post Twitter thread |

---

*Municipal Intelligence System — Version 2.0*
