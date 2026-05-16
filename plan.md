# Municipal Intelligence CLI Implementation Plan

## Goal

Build a CLI-first municipal intelligence tool for Indian cities, starting with the Varanasi fiscal health pilot for FY2019-20 to FY2023-24.

The system must collect only primary government documents, extract structured fiscal data, normalize Indian municipal budget terminology, compute fiscal health metrics, generate charts, and produce draft research outputs with page-level source traceability.

## Non-Negotiable Product Rules

- Primary sources only: accept only official government domains such as `.gov.in`, `.nic.in`, `cag.gov.in`, `mohua.gov.in`, `rbi.org.in`, `data.gov.in`, and approved mission portals.
- Every extracted number must retain document ID, source URL, page number, extraction method, confidence score, and review status.
- Crore, lakh, Indian comma grouping, missing values, and negative corrections must be normalized explicitly.
- No final analysis may use unreviewed low-confidence values without a visible caveat.
- The first product surface is a CLI. Any API, dashboard, or web UI is secondary.

## CLI Product Shape

Binary name:

```bash
muni
```

Core commands:

```bash
muni init
muni sources add --city varanasi --url https://vmc.up.gov.in --type municipal
muni discover --city varanasi
muni ingest --city varanasi --path ./data/raw/varanasi
muni classify --city varanasi
muni extract --city varanasi --doc-id <id>
muni normalize --city varanasi
muni analyze --city varanasi --years 2019-20:2023-24
muni governance map --city varanasi
muni visualize --city varanasi --pack fiscal-health
muni narrative draft --city varanasi --format substack
muni narrative draft --city varanasi --format twitter
muni review queue
muni export --city varanasi --bundle pilot
```

Useful inspection commands:

```bash
muni docs list --city varanasi --priority P1
muni docs show <doc-id>
muni evidence show --metric own_source_revenue_ratio --year 2022-23
muni metrics table --city varanasi
muni anomalies list --city varanasi
muni trace <record-id>
```

## Recommended Initial Stack

Keep the first implementation local and reproducible before introducing distributed services.

| Layer | Phase 1 Choice | Later Scale-Up |
|---|---|---|
| CLI | Go + Cobra | Same |
| Database | PostgreSQL + PostGIS | Same |
| Queue | Local worker table | Redis |
| Object Storage | Local `data/raw` and `data/processed` | S3-compatible storage |
| PDF Text | `pdfplumber`, `pypdf` via Python worker | Same |
| OCR | Tesseract `eng+hin` | Google Vision / Azure OCR fallback |
| Table Extraction | Camelot / Tabula-py | Same |
| Charts | Python matplotlib | D3 / Observable for advanced outputs |
| Narrative | Markdown templates + LLM adapter | Same with review workflow |

Reason: the pilot needs auditability more than distributed architecture. Go should own orchestration, metadata, and CLI behavior. Python workers should handle PDF, OCR, table extraction, and plotting because the mature libraries are there.

## Repository Structure

```text
.
├── cmd/muni/                  # CLI entrypoint
├── internal/
│   ├── config/                # app config, domain whitelist, paths
│   ├── db/                    # migrations and database access
│   ├── discovery/             # source crawling and PDF download
│   ├── documents/             # document metadata, hashing, storage
│   ├── classification/        # taxonomy, language, priority, duplicates
│   ├── extraction/            # extraction orchestration
│   ├── ontology/              # municipal category mapping
│   ├── analysis/              # fiscal metrics and red flags
│   ├── governance/            # agency/service responsibility matrix
│   ├── spatial/               # PostGIS and ward-layer handling
│   ├── visualization/         # chart job orchestration
│   ├── narrative/             # Substack/thread generation
│   └── review/                # human review queues
├── workers/
│   ├── extract_pdf.py
│   ├── ocr_pdf.py
│   ├── extract_tables.py
│   └── render_charts.py
├── migrations/
├── configs/
│   ├── domains.yaml
│   ├── cities/varanasi.yaml
│   └── ontology.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── charts/
│   └── exports/
├── prompts/
│   ├── ontology_mapping.md
│   └── narrative_synthesis.md
└── tests/
```

## Data Model

Minimum tables for the pilot:

| Table | Purpose |
|---|---|
| `cities` | City metadata, state, population references |
| `source_domains` | Approved source whitelist and source type |
| `documents` | PDF metadata, source URL, hash, city, fiscal year, type, priority |
| `document_pages` | Extracted page text, OCR status, language, quality flags |
| `extraction_records` | Raw extracted facts with page references and confidence |
| `financial_facts` | Normalized revenue, expenditure, grant, tax, and debt records |
| `ontology_mappings` | Raw budget head to canonical category mappings |
| `metrics` | Computed fiscal indicators by city and fiscal year |
| `red_flags` | Fiscal stress alerts and anomaly findings |
| `agencies` | VMC, VDA, Jal Nigam, PWD, Smart City SPV, etc. |
| `service_responsibilities` | Who plans, funds, builds, operates, and regulates each service |
| `spatial_layers` | Ward maps and GIS metadata |
| `visualizations` | Generated chart metadata and source dependencies |
| `narrative_outputs` | Draft articles, threads, and evidence references |
| `review_items` | Low-confidence records and uncertain mappings needing human review |

## Implementation Phases

### Phase 0 - Project Bootstrap

Deliverables:

- Create Go CLI skeleton with `muni` command.
- Add config loading from `configs/*.yaml`.
- Add local data directories.
- Add PostgreSQL connection and migrations.
- Add structured logging.
- Add a `muni init` command that verifies local dependencies.

Dependency checks:

```bash
muni init
```

Should verify:

- PostgreSQL reachable
- PostGIS enabled
- Python available
- `tesseract` installed
- Hindi OCR language pack available
- `pdfinfo` or equivalent PDF utility available
- writable `data/` directories

Acceptance criteria:

- `muni --help` shows all planned command groups.
- `muni init` creates config and data directories.
- Database migrations run from a clean database.

### Phase 1 - Document Discovery and Ingestion

Deliverables:

- Domain whitelist enforcement.
- Source registry for approved portals.
- PDF link crawler for official pages.
- Download manager with SHA-256 hashing.
- Filename normalization:

```text
{city}_{doc_type}_{fiscal_year}_{source}_{download_date}.pdf
```

- Archive fallback stub for web archive lookup, initially manual-review only.

Commands:

```bash
muni sources add --city varanasi --url https://vmc.up.gov.in --type municipal
muni discover --city varanasi
muni ingest --city varanasi --path ./data/raw/varanasi
muni docs list --city varanasi
```

Acceptance criteria:

- Non-whitelisted domains are rejected before download.
- Duplicate hashes are not ingested twice.
- Each document has source URL, downloaded path, hash, and capture timestamp.
- Broken links are recorded with parent URL and HTTP status.

### Phase 2 - Document Classification

Deliverables:

- Rule-based classifier for the project taxonomy:
  - Revenue Budget
  - Capital Budget
  - CAG Audit Report
  - Smart City Report
  - AMRUT Report
  - Master Plan
  - Meeting Minutes
  - Property Tax Record
  - Tender Document
- Fiscal year detection from filename and first three pages.
- Language tagging: `ENGLISH`, `HINDI`, `BILINGUAL`, `MIXED`.
- Priority ranking from P1 to P5.
- Near-duplicate detection using city, fiscal year, file size, page count, and document type.

Commands:

```bash
muni classify --city varanasi
muni docs list --city varanasi --priority P1
muni docs show <doc-id>
```

Acceptance criteria:

- Classification result includes reason codes.
- Uncertain classification creates a `review_items` row.
- Hindi and scanned documents are routed to OCR.
- CAG, budget actuals, and property tax records are ranked P1.

### Phase 3 - OCR and Structured Extraction

Deliverables:

- PDF text extraction worker for text-native PDFs.
- OCR worker for scanned PDFs using Tesseract `eng+hin`.
- Table extraction worker using Camelot or Tabula.
- Extraction schemas for:
  - Own-source revenue
  - External transfers
  - Expenditure
  - Property tax DCB
  - Capital works
  - Debt service
- Unit normalization library for crore, lakh, Indian comma grouping, blanks, and negative values.
- Confidence scoring.

Commands:

```bash
muni extract --city varanasi --doc-id <id>
muni extract --city varanasi --priority P1
muni review queue
muni trace <record-id>
```

Acceptance criteria:

- Each extracted value has document ID, page number, raw text, normalized INR value, confidence, and extraction method.
- Row and column totals are cross-checked when table structure allows it.
- Low-confidence OCR results enter the review queue.
- No extracted number is stored without a source reference.

### Phase 4 - Ontology and Normalization

Deliverables:

- Canonical municipal category mapping from raw budget heads.
- Mapping log for every non-obvious match.
- City and fiscal year normalization.
- Review workflow for uncertain mappings.

Canonical categories must include:

- `SOLID_WASTE_MANAGEMENT`
- `ROAD_INFRASTRUCTURE`
- `WATER_SUPPLY`
- `SEWERAGE_DRAINAGE`
- `STAFF_SALARIES`
- `PENSION_LIABILITY`
- `DEBT_SERVICING`
- `SMART_CITY_PROJECTS`
- `AMRUT_PROJECTS`
- `PUBLIC_SPACES`
- `STREET_LIGHTING`
- `PUBLIC_HEALTH`

Commands:

```bash
muni normalize --city varanasi
muni ontology unmapped --city varanasi
muni ontology approve <mapping-id>
```

Acceptance criteria:

- Raw names remain preserved after mapping.
- Uncertain mappings are not silently merged.
- April-March fiscal years are normalized consistently.
- Mapping decisions are auditable.

### Phase 5 - Fiscal Analysis Engine

Deliverables:

- Metric computation engine for:
  - Own Source Revenue Ratio
  - Property Tax Collection Efficiency
  - Property Tax per Capita
  - Salary-to-Total Expenditure Ratio
  - Capital Expenditure Ratio
  - Grant Dependence Ratio
  - Debt Service Coverage
  - Revenue per Capita
  - O&M Spending per Sector
- Property tax DCB analysis.
- Fiscal stress red flags.
- Evidence trace for every metric.

Commands:

```bash
muni analyze --city varanasi --years 2019-20:2023-24
muni metrics table --city varanasi
muni evidence show --metric property_tax_collection_efficiency --year 2022-23
muni anomalies list --city varanasi
```

Acceptance criteria:

- Metrics run for at least three fiscal years in the pilot.
- Formula inputs are visible through `muni evidence show`.
- Red flags are generated for thresholds from `project.md`.
- Smart City capex can be separated from core municipal capex.

### Phase 6 - Governance Mapping

Deliverables:

- Agency registry for Varanasi:
  - VMC
  - VDA
  - Jal Nigam
  - PWD
  - Traffic Police
  - Smart Cities SPV
  - Varanasi Smart City Ltd
  - BSNL / Power Corp
  - Ganga Pollution Control Unit
- Service responsibility matrix for roads, water, SWM, sewerage, transit, street lighting, parks, and drainage.
- Source references for each agency responsibility.

Commands:

```bash
muni governance map --city varanasi
muni governance service --city varanasi --service water
```

Acceptance criteria:

- Each service records who plans, funds, builds, operates, and regulates.
- Fragmented ownership is explicitly represented.
- Unknown responsibility fields are marked `UNKNOWN`, not guessed.

### Phase 7 - GIS and Spatial Intelligence

Deliverables:

- PostGIS support for ward boundaries.
- Spatial layer ingestion metadata.
- Initial ward-level joins for property tax and population where available.
- Stubs for built-up growth, infrastructure coverage, and flood-risk layers.

Commands:

```bash
muni spatial ingest --city varanasi --layer wards --path ./data/raw/gis/wards.geojson
muni spatial layers --city varanasi
muni spatial join-tax --city varanasi
```

Acceptance criteria:

- Ward geometries load into PostGIS.
- Spatial source metadata is preserved.
- Missing ward-level tax data creates a review/data-gap item.

### Phase 8 - Trend and Anomaly Detection

Deliverables:

- Multi-year anomaly rules:
  - Pre-election capex spike
  - Property tax plateau
  - Grant absorption failure
  - Salary creep
  - O&M collapse
  - Sudden new revenue head
  - Negative capex year
- Election-year configuration for UP local bodies.

Commands:

```bash
muni anomalies run --city varanasi
muni anomalies list --city varanasi
muni anomalies explain <anomaly-id>
```

Acceptance criteria:

- Each anomaly includes rule name, years affected, metric values, threshold, and source evidence.
- Election-year rules use configured dates, not hard-coded assumptions.
- Anomalies can be dismissed or marked for narrative use.

### Phase 9 - Visualization

Deliverables:

- Chart renderer for the pilot visuals:
  - Revenue Sankey
  - Revenue stacked bar
  - Expenditure donut
  - Property tax DCB waterfall
  - Fiscal trend line chart
  - Governance network map
  - Ward heatmap if ward data exists
- Twitter/X chart size export at `1200x675`.
- Chart footer with city, fiscal year, and primary source.

Commands:

```bash
muni visualize --city varanasi --pack fiscal-health
muni visualize one --city varanasi --chart property-tax-dcb --year 2022-23
```

Acceptance criteria:

- At least five publication-ready charts are generated for the pilot.
- Each chart has source metadata in the image footer or adjacent metadata file.
- No chart uses more than five data series.
- Red/green-only palettes are avoided.

### Phase 10 - Narrative Synthesis

Deliverables:

- Markdown Substack draft generator.
- 20-post X/Twitter thread generator.
- Evidence-link insertion for claims and charts.
- Caveat insertion for uncertain data.
- Export bundle with article, thread, charts, and source table.

Commands:

```bash
muni narrative draft --city varanasi --format substack
muni narrative draft --city varanasi --format twitter
muni export --city varanasi --bundle pilot
```

Acceptance criteria:

- Draft article follows the structure in `project.md`.
- Thread contains exactly 20 posts.
- Every quantitative claim links to evidence.
- Final export includes a source bibliography with document page references.

## Pilot Workflow

Target:

- City: Varanasi Municipal Corporation
- Topic: Fiscal Health Assessment
- Years: FY2019-20 to FY2023-24

Runbook:

```bash
muni init
muni sources add --city varanasi --url https://vmc.up.gov.in --type municipal
muni sources add --city varanasi --url https://cag.gov.in --type audit
muni sources add --city varanasi --url https://mohua.gov.in --type mission
muni discover --city varanasi
muni classify --city varanasi
muni extract --city varanasi --priority P1
muni normalize --city varanasi
muni analyze --city varanasi --years 2019-20:2023-24
muni governance map --city varanasi
muni anomalies run --city varanasi
muni visualize --city varanasi --pack fiscal-health
muni narrative draft --city varanasi --format substack
muni narrative draft --city varanasi --format twitter
muni export --city varanasi --bundle pilot
```

Pilot documents:

- VMC annual budgets for five fiscal years.
- Latest CAG Uttar Pradesh local bodies audit report.
- AMRUT Varanasi utilization report.
- Smart Cities Mission Varanasi fund report.
- Property tax DCB records if available.

Pilot success criteria:

- 100% of final numbers trace to primary-source document pages.
- 0 secondary sources used in final analysis.
- All 8 core fiscal metrics computed for at least 3 years.
- Minimum 5 publication-ready charts.
- 1 Substack draft around 2,000 words.
- 1 X/Twitter thread with 20 posts.

## Review and Quality Gates

Before analysis:

- All P1 documents classified.
- Duplicate documents resolved.
- Fiscal year confirmed.
- Scanned or Hindi-heavy documents routed correctly.

Before visualization:

- Low-confidence values reviewed or excluded.
- Metric evidence traces complete.
- Outlier values checked against source pages.

Before narrative export:

- Every number has an evidence link.
- Every chart has source metadata.
- Uncertain data is caveated.
- No secondary-source claims are included as factual evidence.

## Testing Strategy

Unit tests:

- Domain whitelist validation.
- SHA-256 duplicate detection.
- Fiscal year parser.
- Language tagger.
- Unit normalization for crore, lakh, Indian comma grouping, blanks, and negatives.
- Metric formulas.
- Red flag thresholds.

Integration tests:

- Ingest a fixture PDF.
- Classify the fixture.
- Extract a known table.
- Normalize records.
- Compute metrics.
- Generate a chart with source metadata.

Golden fixtures:

- One text-native English budget PDF.
- One scanned Hindi budget PDF sample.
- One CAG report table.
- One property tax DCB table.
- One malformed document with missing year.

## Milestone Order

1. CLI skeleton, config, migrations, and local storage.
2. Document ingestion with whitelist and hashing.
3. Classification and priority ranking.
4. Text extraction and unit normalization.
5. Financial fact schema and fiscal metrics.
6. Evidence trace commands.
7. Chart generation for pilot metrics.
8. Governance matrix.
9. Narrative export.
10. GIS and advanced anomaly expansion.

## First Sprint

Build only the smallest vertical slice:

```bash
muni init
muni ingest --city varanasi --path ./data/raw/varanasi
muni classify --city varanasi
muni extract --city varanasi --doc-id <id>
muni analyze --city varanasi --years 2022-23
muni evidence show --metric own_source_revenue_ratio --year 2022-23
```

Sprint output:

- One ingested PDF.
- One classified document.
- One extracted revenue table.
- One normalized fiscal metric.
- One evidence trace proving where the number came from.

This validates the core promise before expanding into crawling, GIS, visualizations, and narrative generation.
