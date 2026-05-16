# Municipal Intelligence CLI Implementation Plan

## Goal

Build a CLI-first municipal intelligence tool for Indian cities. The system should work for any city where primary government documents can be found, with Varanasi used only as an example starter city.

The tool will collect official documents, classify them, extract fiscal and governance data, normalize Indian municipal terminology, compute fiscal health metrics, generate charts, and produce evidence-backed research drafts.

## Core Product Rules

- Primary sources only: accept official government domains such as `.gov.in`, `.nic.in`, `cag.gov.in`, `mohua.gov.in`, `rbi.org.in`, `data.gov.in`, state portals, municipal portals, and approved mission portals.
- Every number must trace back to a document, source URL, page number, extraction method, confidence score, and review status.
- Crore, lakh, Indian comma grouping, missing values, and negative corrections must be normalized explicitly.
- Low-confidence data must go to human review before it is used in final analysis.
- The first product is a CLI. The CLI should be useful before any dashboard, API, or web app exists.

## City-Agnostic Design

The system must not hard-code Varanasi, Uttar Pradesh, or any one municipal corporation.

Each city is represented by a city profile:

```yaml
slug: lucknow
name: Lucknow
state: Uttar Pradesh
country: India
population:
  value: 2817105
  year: 2011
  source: censusindia.gov.in
fiscal_year_format: april_march
primary_language: hindi
secondary_language: english
official_sources:
  - url: https://lmc.up.nic.in
    type: municipal
  - url: https://cag.gov.in
    type: audit
  - url: https://mohua.gov.in
    type: mission
known_agencies:
  - Lucknow Municipal Corporation
  - Lucknow Development Authority
  - Jal Nigam
  - PWD
```

The CLI should support:

- Adding a new city.
- Registering official source URLs for that city.
- Running the same discovery, extraction, analysis, visualization, and narrative pipeline against that city.
- Keeping city-specific agency names, source portals, languages, ward layers, and election years in config instead of code.

## How The CLI Works

The CLI is a pipeline runner plus an inspection tool.

A user should be able to run one command at a time while building confidence:

```bash
muni city add --slug lucknow --name "Lucknow" --state "Uttar Pradesh"
muni sources add --city lucknow --url https://lmc.up.nic.in --type municipal
muni discover --city lucknow
muni classify --city lucknow
muni extract --city lucknow --priority P1
muni normalize --city lucknow
muni analyze --city lucknow --years 2019-20:2023-24
muni visualize --city lucknow --pack fiscal-health
muni narrative draft --city lucknow --format substack
```

The same flow should also run as a bundled workflow:

```bash
muni run fiscal-health --city lucknow --years 2019-20:2023-24
```

For normal use, there should be one command that runs the complete workflow:

```bash
muni run all --city lucknow --years 2019-20:2023-24
```

The CLI does four things for every command:

1. Reads city config, source config, and pipeline settings.
2. Runs the requested stage.
3. Writes structured records to the database and artifacts to `data/`.
4. Prints a concise terminal report showing what succeeded, what failed, and what needs review.

Example output style:

```text
City: Lucknow
Stage: classify

Documents scanned: 42
Classified: 36
Needs review: 6
Duplicates skipped: 4

Next:
  muni review queue --city lucknow
  muni extract --city lucknow --priority P1
```

The CLI should never hide uncertainty. If a document has no fiscal year, a table fails extraction, or a source is not whitelisted, the command should record the issue and show the next action.

## CLI Commands

Binary name:

```bash
muni
```

Setup and configuration:

```bash
muni init
muni doctor
muni city add --slug <city_slug> --name "<City Name>" --state "<State>"
muni city list
muni city show --city <city_slug>
muni sources add --city <city_slug> --url <official_url> --type <source_type>
muni sources list --city <city_slug>
```

Pipeline commands:

```bash
muni discover --city <city_slug>
muni ingest --city <city_slug> --path ./data/raw/<city_slug>
muni classify --city <city_slug>
muni extract --city <city_slug> --doc-id <doc_id>
muni extract --city <city_slug> --priority P1
muni normalize --city <city_slug>
muni analyze --city <city_slug> --years 2019-20:2023-24
muni governance map --city <city_slug>
muni spatial ingest --city <city_slug> --layer wards --path ./wards.geojson
muni anomalies run --city <city_slug>
muni visualize --city <city_slug> --pack fiscal-health
muni narrative draft --city <city_slug> --format substack
muni narrative draft --city <city_slug> --format twitter
muni export --city <city_slug> --bundle fiscal-health
```

Inspection and review commands:

```bash
muni docs list --city <city_slug> --priority P1
muni docs show <doc_id>
muni review queue --city <city_slug>
muni review approve <review_id>
muni ontology unmapped --city <city_slug>
muni ontology approve <mapping_id>
muni metrics table --city <city_slug>
muni anomalies list --city <city_slug>
muni evidence show --metric own_source_revenue_ratio --city <city_slug> --year 2022-23
muni trace <record_id>
```

Bundled workflows:

```bash
muni run all --city <city_slug> --years 2019-20:2023-24
muni run fiscal-health --city <city_slug> --years 2019-20:2023-24
muni run discovery-only --city <city_slug>
muni run charts-only --city <city_slug>
```

One-command first-time run:

```bash
muni run all \
  --city <city_slug> \
  --name "<City Name>" \
  --state "<State>" \
  --municipal-url <official_municipal_url> \
  --years 2019-20:2023-24
```

If the city already exists, `--name`, `--state`, and `--municipal-url` are optional. If the city does not exist, the command should create the city profile, register the municipal source, add default national sources such as CAG and MOHUA, and then run the full pipeline.

`muni run all` should execute these stages in order:

1. `doctor` dependency checks.
2. City profile validation or creation.
3. Official source validation.
4. Document discovery.
5. Document classification.
6. P1 extraction.
7. Ontology normalization.
8. Fiscal analysis.
9. Governance mapping.
10. Anomaly detection.
11. Visualization pack generation.
12. Substack draft generation.
13. Twitter thread generation.
14. Export bundle creation.

Default behavior should stop before narrative export if there are unresolved critical review items. The user can override this with:

```bash
muni run all --city <city_slug> --years 2019-20:2023-24 --allow-review-gaps
```

## Python Tech Stack

Use Python across the project for speed of implementation, easier PDF processing, and simpler data science workflows.

| Layer | Recommended Tooling |
|---|---|
| CLI | Typer + Rich |
| Config | Pydantic Settings + YAML |
| Database ORM | SQLAlchemy |
| Migrations | Alembic |
| Primary Database | PostgreSQL + PostGIS |
| Local Development Database | SQLite allowed only for lightweight tests |
| HTTP Fetching | httpx |
| HTML Parsing | BeautifulSoup / selectolax |
| Crawling | Custom crawler first, Scrapy later if needed |
| PDF Text | pdfplumber + pypdf |
| OCR | pytesseract + Tesseract `eng+hin` |
| OCR Fallback | Google Vision or Azure OCR for difficult Devanagari scans |
| Table Extraction | Camelot + Tabula-py |
| Data Analysis | pandas + numpy |
| Spatial | GeoPandas + Shapely + PostGIS |
| Charts | matplotlib + seaborn + plotly where useful |
| Templates | Jinja2 |
| LLM Adapter | Provider-neutral interface |
| Testing | pytest |
| Formatting | ruff |
| Type Checking | mypy or pyright |
| Packaging | uv or Poetry |

Future scale-up options:

- Redis for background job queues.
- S3-compatible storage for raw PDFs and generated artifacts.
- Qdrant for semantic search across extracted text.
- FastAPI if a web API is needed later.

## Repository Structure

```text
.
├── muni/
│   ├── __init__.py
│   ├── cli.py                     # Typer app entrypoint
│   ├── config.py                  # settings and config loading
│   ├── db/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── cities/
│   │   ├── service.py             # city profile operations
│   │   └── schemas.py
│   ├── sources/
│   │   ├── whitelist.py
│   │   └── crawler.py
│   ├── documents/
│   │   ├── ingest.py
│   │   ├── hashing.py
│   │   └── classify.py
│   ├── extraction/
│   │   ├── pdf_text.py
│   │   ├── ocr.py
│   │   ├── tables.py
│   │   ├── units.py
│   │   └── records.py
│   ├── ontology/
│   │   ├── mapping.py
│   │   └── categories.py
│   ├── analysis/
│   │   ├── metrics.py
│   │   ├── property_tax.py
│   │   └── anomalies.py
│   ├── governance/
│   │   └── matrix.py
│   ├── spatial/
│   │   └── layers.py
│   ├── visualization/
│   │   └── charts.py
│   ├── narrative/
│   │   ├── drafts.py
│   │   └── templates/
│   ├── review/
│   │   └── queue.py
│   └── workflows/
│       └── fiscal_health.py
├── configs/
│   ├── domains.yaml
│   ├── ontology.yaml
│   └── cities/
│       ├── varanasi.yaml
│       └── lucknow.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── charts/
│   └── exports/
├── tests/
│   ├── fixtures/
│   └── test_units.py
├── pyproject.toml
├── README.md
└── plan.md
```

## Data Model

Minimum tables:

| Table | Purpose |
|---|---|
| `cities` | City metadata, state, population references, fiscal-year rules |
| `source_domains` | Approved source whitelist and source type |
| `city_sources` | Official URLs registered for each city |
| `documents` | PDF metadata, source URL, hash, city, fiscal year, type, priority |
| `document_pages` | Extracted page text, OCR status, language, quality flags |
| `extraction_records` | Raw extracted facts with page references and confidence |
| `financial_facts` | Normalized revenue, expenditure, grant, tax, debt, and capex records |
| `ontology_mappings` | Raw budget head to canonical category mappings |
| `metrics` | Computed fiscal indicators by city and fiscal year |
| `red_flags` | Fiscal stress alerts and anomaly findings |
| `agencies` | City-specific agencies and source evidence |
| `service_responsibilities` | Who plans, funds, builds, operates, and regulates each service |
| `spatial_layers` | Ward maps and GIS metadata |
| `visualizations` | Generated chart metadata and source dependencies |
| `narrative_outputs` | Draft articles, threads, and evidence references |
| `review_items` | Low-confidence records and uncertain mappings needing human review |

## Implementation Phases

### Phase 0 - Python Project Bootstrap

Deliverables:

- Create Python package and Typer CLI.
- Add `muni init`, `muni doctor`, and `muni --help`.
- Add config loading from `configs/*.yaml`.
- Add local data directories.
- Add SQLAlchemy models and Alembic migrations.
- Add Rich terminal output.
- Add pytest and ruff.

`muni doctor` should verify:

- Python version.
- PostgreSQL connection.
- PostGIS availability.
- Tesseract installed.
- Hindi OCR language pack available.
- Java available if Tabula is enabled.
- writable `data/` directories.

Acceptance criteria:

- `muni --help` shows command groups.
- `muni init` creates required config and data directories.
- `muni doctor` reports dependency status clearly.
- Migrations run from a clean database.

### Phase 1 - City Profiles and Source Registry

Deliverables:

- Add city profile schema.
- Add city create/list/show commands.
- Add source URL registration.
- Add strict domain whitelist validation.
- Add city-specific config files under `configs/cities/`.

Commands:

```bash
muni city add --slug lucknow --name "Lucknow" --state "Uttar Pradesh"
muni sources add --city lucknow --url https://lmc.up.nic.in --type municipal
muni sources list --city lucknow
```

Acceptance criteria:

- New cities can be added without code changes.
- Non-whitelisted domains are rejected.
- Official sources are linked to the correct city.
- City profile data is available to later pipeline stages.

### Phase 2 - Document Discovery and Ingestion

Deliverables:

- PDF link crawler for registered official sources.
- Download manager with SHA-256 hashing.
- Manual local file ingestion.
- Broken-link logging.
- Filename normalization:

```text
{city}_{doc_type}_{fiscal_year}_{source}_{download_date}.pdf
```

Commands:

```bash
muni discover --city lucknow
muni ingest --city lucknow --path ./data/raw/lucknow
muni docs list --city lucknow
```

Acceptance criteria:

- Duplicate hashes are not ingested twice.
- Each document has source URL, local path, hash, and capture timestamp.
- Broken links are recorded with parent URL and HTTP status.
- Documents from unknown domains are rejected before download.

### Phase 3 - Document Classification

Deliverables:

- Rule-based classifier for:
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
muni classify --city lucknow
muni docs list --city lucknow --priority P1
muni docs show <doc_id>
```

Acceptance criteria:

- Classification result includes reason codes.
- Uncertain classifications create review items.
- Hindi and scanned documents are routed to OCR.
- CAG reports, budget actuals, and property tax records are ranked P1.

### Phase 4 - OCR and Structured Extraction

Deliverables:

- Text extraction for text-native PDFs.
- OCR for scanned PDFs using Tesseract `eng+hin`.
- Table extraction using Camelot or Tabula.
- Extraction schemas for:
  - Own-source revenue
  - External transfers
  - Expenditure
  - Property tax DCB
  - Capital works
  - Debt service
- Unit normalization for crore, lakh, Indian comma grouping, blanks, and negative values.
- Confidence scoring.

Commands:

```bash
muni extract --city lucknow --doc-id <doc_id>
muni extract --city lucknow --priority P1
muni review queue --city lucknow
muni trace <record_id>
```

Acceptance criteria:

- Each extracted value has document ID, page number, raw text, normalized INR value, confidence, and extraction method.
- Row and column totals are cross-checked when possible.
- Low-confidence OCR results enter the review queue.
- No extracted number is stored without a source reference.

### Phase 5 - Ontology and Normalization

Deliverables:

- Canonical municipal category mapping from raw budget heads.
- Mapping log for every non-obvious match.
- Fiscal year normalization to April-March unless city config says otherwise.
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
muni normalize --city lucknow
muni ontology unmapped --city lucknow
muni ontology approve <mapping_id>
```

Acceptance criteria:

- Raw names remain preserved after mapping.
- Uncertain mappings are not silently merged.
- Mapping decisions are auditable.
- The same ontology works across multiple cities.

### Phase 6 - Fiscal Analysis Engine

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
muni analyze --city lucknow --years 2019-20:2023-24
muni metrics table --city lucknow
muni evidence show --metric property_tax_collection_efficiency --city lucknow --year 2022-23
```

Acceptance criteria:

- Metrics run for at least three fiscal years when data exists.
- Formula inputs are visible through `muni evidence show`.
- Red flags are generated from configured thresholds.
- Smart City capex can be separated from core municipal capex.

### Phase 7 - Governance Mapping

Deliverables:

- City-specific agency registry.
- Service responsibility matrix for roads, water, SWM, sewerage, transit, street lighting, parks, and drainage.
- Source references for each agency responsibility.

Commands:

```bash
muni governance map --city lucknow
muni governance service --city lucknow --service water
```

Acceptance criteria:

- Each service records who plans, funds, builds, operates, and regulates.
- Fragmented ownership is explicitly represented.
- Unknown responsibility fields are marked `UNKNOWN`, not guessed.
- Agency names come from city config and discovered documents.

### Phase 8 - GIS and Spatial Intelligence

Deliverables:

- PostGIS support for ward boundaries.
- Spatial layer ingestion metadata.
- Ward-level joins for property tax and population where available.
- Stubs for built-up growth, infrastructure coverage, and flood-risk layers.

Commands:

```bash
muni spatial ingest --city lucknow --layer wards --path ./data/raw/gis/lucknow_wards.geojson
muni spatial layers --city lucknow
muni spatial join-tax --city lucknow
```

Acceptance criteria:

- Ward geometries load into PostGIS.
- Spatial source metadata is preserved.
- Missing ward-level tax data creates a review/data-gap item.

### Phase 9 - Trend and Anomaly Detection

Deliverables:

- Multi-year anomaly rules:
  - Pre-election capex spike
  - Property tax plateau
  - Grant absorption failure
  - Salary creep
  - O&M collapse
  - Sudden new revenue head
  - Negative capex year
- Election-year configuration by state and city.

Commands:

```bash
muni anomalies run --city lucknow
muni anomalies list --city lucknow
muni anomalies explain <anomaly_id>
```

Acceptance criteria:

- Each anomaly includes rule name, years affected, metric values, threshold, and source evidence.
- Election-year rules use configured dates.
- Anomalies can be dismissed or marked for narrative use.

### Phase 10 - Visualization

Deliverables:

- Chart renderer for:
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
muni visualize --city lucknow --pack fiscal-health
muni visualize one --city lucknow --chart property-tax-dcb --year 2022-23
```

Acceptance criteria:

- At least five publication-ready charts are generated when data exists.
- Each chart has source metadata in the image footer or adjacent metadata file.
- No chart uses more than five data series.
- Red/green-only palettes are avoided.

### Phase 11 - Narrative Synthesis

Deliverables:

- Markdown Substack draft generator.
- 20-post X/Twitter thread generator.
- Evidence-link insertion for claims and charts.
- Caveat insertion for uncertain data.
- Export bundle with article, thread, charts, and source table.

Commands:

```bash
muni narrative draft --city lucknow --format substack
muni narrative draft --city lucknow --format twitter
muni export --city lucknow --bundle fiscal-health
```

Acceptance criteria:

- Draft article follows the research structure from `project.md`.
- Thread contains exactly 20 posts.
- Every quantitative claim links to evidence.
- Final export includes a source bibliography with document page references.

## Example End-to-End Workflow

For any city:

```bash
muni run all \
  --city <city_slug> \
  --name "<City Name>" \
  --state "<State>" \
  --municipal-url <municipal_url> \
  --years 2019-20:2023-24
```

For Varanasi as a starter example:

```bash
muni run all \
  --city varanasi \
  --name "Varanasi" \
  --state "Uttar Pradesh" \
  --municipal-url https://vmc.up.gov.in \
  --years 2019-20:2023-24
```

The step-by-step commands should still exist for debugging, partial reruns, and human review, but `muni run all` is the default user-facing path.

## Fiscal Health Workflow Inputs

Minimum target documents for a strong city analysis:

- Annual municipal budgets for at least three fiscal years.
- Latest relevant CAG local bodies audit report.
- Property tax DCB or demand-collection records.
- AMRUT or Smart City utilization reports if applicable.
- Master plan or development authority documents for governance context.
- Ward maps if spatial analysis is required.

Success criteria:

- 100% of final numbers trace to primary-source document pages.
- 0 secondary sources used as factual evidence.
- All core fiscal metrics computed for at least 3 years where source data exists.
- Minimum 5 publication-ready charts when the data supports them.
- 1 Substack-style draft.
- 1 X/Twitter thread with 20 posts.

## Review and Quality Gates

Before analysis:

- P1 documents classified.
- Duplicate documents resolved.
- Fiscal years confirmed.
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
- City profile parsing.
- SHA-256 duplicate detection.
- Fiscal year parser.
- Language tagger.
- Unit normalization for crore, lakh, Indian comma grouping, blanks, and negatives.
- Metric formulas.
- Red flag thresholds.

Integration tests:

- Add a city profile.
- Register an official source.
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

1. Python CLI skeleton, config, migrations, and local storage.
2. City profiles and official source registry.
3. Document ingestion with whitelist and hashing.
4. Classification and priority ranking.
5. Text extraction and unit normalization.
6. Financial fact schema and fiscal metrics.
7. Evidence trace commands.
8. Chart generation for fiscal metrics.
9. Governance matrix.
10. Narrative export.
11. GIS and advanced anomaly expansion.

## First Sprint

Build the smallest vertical slice:

```bash
muni init
muni city add --slug varanasi --name "Varanasi" --state "Uttar Pradesh"
muni ingest --city varanasi --path ./data/raw/varanasi
muni classify --city varanasi
muni extract --city varanasi --doc-id <doc_id>
muni analyze --city varanasi --years 2022-23
muni evidence show --metric own_source_revenue_ratio --city varanasi --year 2022-23
```

Sprint output:

- One city profile.
- One ingested PDF.
- One classified document.
- One extracted revenue table.
- One normalized fiscal metric.
- One evidence trace proving where the number came from.

This validates the core promise before expanding into crawling, GIS, visualizations, and narrative generation.
