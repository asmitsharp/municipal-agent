# Municipal Intelligence Agent System Implementation Plan

## Goal

Build a city-agnostic municipal intelligence agent system for Indian cities.

This is not a generic document summarizer and not just a CLI data pipeline. The product is an agent-based research system that collects primary government documents, converts them into cumulative structured evidence, analyzes Indian municipal finance and governance, connects the findings to space and institutions, and produces source-backed research outputs for a human researcher to review.

The CLI is the control surface. The agents are the architecture.

```text
muni run all --city <city_slug>
  -> AgentOrchestrator
    -> DocumentDiscoveryAgent
    -> DocumentClassificationAgent
    -> OCRExtractionAgent
    -> OntologyNormalizationAgent
    -> FiscalAnalysisAgent
    -> GovernanceMappingAgent
    -> SpatialIntelligenceAgent
    -> AnomalyDetectionAgent
    -> VisualizationAgent
    -> NarrativeSynthesisAgent
      -> human researcher review
```

## Core Philosophy

Three rules govern the system:

1. Primary sources only.
   Every data point must trace to a government-issued primary source such as a municipal budget, CAG audit, gazette, tender, grant report, official GIS layer, or government portal.

2. India-specific reasoning.
   The system must understand crore/lakh notation, Hindi and bilingual documents, April-March fiscal years, state-transfer dependence, overlapping agency jurisdiction, election-cycle spending distortions, and informal urban growth.

3. Cumulative knowledge.
   Each run must add to a durable evidence database. Research should compound across cities, years, documents, agencies, fiscal heads, spatial layers, and extracted facts.

## What The System Must Produce

For any supported city, the system should eventually produce:

- A document evidence base of official primary sources.
- Classified and prioritized municipal documents.
- Extracted fiscal records with page-level traceability.
- Normalized municipal budget categories.
- Fiscal health metrics over multiple years.
- Property tax demand-collection-balance analysis.
- Governance responsibility maps.
- Spatial intelligence where GIS data exists.
- Trend and anomaly findings.
- Publication-ready charts.
- A Substack-style article draft.
- A 20-post X/Twitter thread draft.
- A review queue for uncertain documents, facts, mappings, and claims.

## Product Layers

The system has four layers:

| Layer | Responsibility |
|---|---|
| CLI | User control surface: setup, run agents, inspect evidence, review outputs |
| Agent Runtime | Common agent interface, orchestration, logging, status, retries, review gates |
| Domain Services | Crawling, PDF parsing, OCR, table extraction, normalization, metrics, charts |
| Evidence Store | Documents, pages, extracted records, facts, metrics, review items, artifacts |

The CLI should never contain the business logic. CLI commands call workflows or individual agents.

## Current Implementation State

Already implemented:

- Python package skeleton.
- Typer CLI and Rich output.
- `muni init`.
- `muni doctor`.
- City profiles under `configs/cities/`.
- Source registration.
- Domain whitelist validation.
- SQLAlchemy and Alembic bootstrap.
- pytest and ruff setup.

Important correction:

- The next phase should not jump directly into ingestion as loose functions.
- The next phase should add the agent runtime and make future pipeline stages first-class agents.

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
election_years:
  local_body:
    - 2017
    - 2022
```

City profiles provide agent context. They tell agents where to search, which languages to expect, which fiscal-year convention to use, which agencies are known, and which election years matter for anomaly detection.

## Agent Runtime Design

All agents should implement the same basic contract.

```python
class BaseAgent:
    name: str
    description: str

    def run(self, context: AgentContext) -> AgentResult:
        ...
```

Shared context:

```python
@dataclass
class AgentContext:
    city_slug: str
    years: Optional[YearRange]
    run_id: str
    settings: Settings
    city_profile: CityProfile
    database_url: str
    artifact_dir: Path
    allow_review_gaps: bool = False
```

Shared result:

```python
@dataclass
class AgentResult:
    agent_name: str
    status: Literal["success", "partial", "failed", "blocked"]
    records_created: int = 0
    records_updated: int = 0
    review_items_created: int = 0
    artifacts_created: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
```

Why this matters:

- `muni run all` can report stage-by-stage status.
- Failed runs can resume from a named agent.
- Review gates can stop unsafe narrative generation.
- Each agent can be tested independently.
- LLM-backed steps can be added later without changing CLI behavior.

## Agents To Implement

### Agent 1 - DocumentDiscoveryAgent

Purpose: find and download only primary government documents.

Responsibilities:

- Read official sources from the city profile.
- Crawl approved domains only.
- Reject news, blogs, think-tank PDFs, Wikipedia, and unapproved domains.
- Discover municipal budgets, CAG reports, grant reports, master plans, GIS documents, tenders, meeting minutes, and property tax records.
- Record broken links and parent pages.
- Support archive fallback later.
- Store downloaded PDFs with stable metadata and hash.

Inputs:

- City profile.
- Domain whitelist.
- Source registry.

Outputs:

- Document records.
- Raw PDFs in local or object storage.
- Broken-link records.
- Review items for suspicious or unsupported sources.

CLI:

```bash
muni discover --city <city_slug>
```

### Agent 2 - DocumentClassificationAgent

Purpose: classify incoming documents before extraction.

Responsibilities:

- Classify document type:
  - Revenue Budget
  - Capital Budget
  - CAG Audit Report
  - Smart City Report
  - AMRUT Report
  - Master Plan
  - Meeting Minutes
  - Property Tax Record
  - Tender Document
- Detect fiscal year from filename and first pages.
- Tag language: `ENGLISH`, `HINDI`, `BILINGUAL`, `MIXED`.
- Rank priority P1-P5.
- Detect exact duplicates by SHA-256.
- Detect near duplicates by city, year, type, file size, and page count.

Outputs:

- Classified document metadata.
- Priority queues.
- Review items for uncertain classification.

CLI:

```bash
muni classify --city <city_slug>
```

### Agent 3 - OCRExtractionAgent

Purpose: convert PDFs and scanned documents into structured evidence.

Responsibilities:

- Extract text from text-native PDFs.
- OCR scanned PDFs using Tesseract `eng+hin`.
- Route difficult Devanagari scans to Google Vision or Azure OCR later.
- Extract tables using Camelot or Tabula.
- Extract own-source revenue, external transfers, expenditure, property tax DCB, capital works, and debt service.
- Normalize crore, lakh, Indian comma grouping, blanks, and negative values.
- Assign confidence scores.
- Preserve raw text, page number, extraction method, and source reference.

Outputs:

- Page text.
- Raw extraction records.
- Normalized financial facts.
- Confidence scores.
- Review items for low-confidence extraction.

CLI:

```bash
muni extract --city <city_slug> --priority P1
muni extract --city <city_slug> --doc-id <doc_id>
```

### Agent 4 - OntologyNormalizationAgent

Purpose: create a semantic layer across cities and years.

Responsibilities:

- Map raw budget heads to canonical municipal categories.
- Preserve raw labels.
- Record every non-obvious mapping in a mapping log.
- Never silently merge uncertain categories.
- Normalize fiscal years to April-March unless city config says otherwise.

Canonical categories include:

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

CLI:

```bash
muni normalize --city <city_slug>
muni ontology unmapped --city <city_slug>
muni ontology approve <mapping_id>
```

### Agent 5 - FiscalAnalysisAgent

Purpose: compute municipal fiscal health metrics and red flags.

Responsibilities:

- Compute:
  - Own Source Revenue Ratio
  - Property Tax Collection Efficiency
  - Property Tax per Capita
  - Salary-to-Total Expenditure Ratio
  - Capital Expenditure Ratio
  - Grant Dependence Ratio
  - Debt Service Coverage
  - Revenue per Capita
  - O&M Spending per Sector
- Run property tax demand-collection-balance analysis.
- Separate Smart City capex from core municipal capex where possible.
- Generate red flags for fiscal stress.
- Store evidence traces for each formula input.

CLI:

```bash
muni analyze --city <city_slug> --years 2019-20:2023-24
muni metrics table --city <city_slug>
muni evidence show --metric own_source_revenue_ratio --city <city_slug> --year 2022-23
```

### Agent 6 - GovernanceMappingAgent

Purpose: map institutional fragmentation and accountability gaps.

Responsibilities:

- Build a city-specific agency registry.
- For roads, water, SWM, sewerage, transit, street lighting, parks, and drainage, answer:
  - Who plans it?
  - Who funds it?
  - Who builds it?
  - Who operates it?
  - Who regulates it?
- Mark unknown fields as `UNKNOWN`, not guessed.
- Attach source evidence to each responsibility claim.

CLI:

```bash
muni governance map --city <city_slug>
muni governance service --city <city_slug> --service water
```

### Agent 7 - SpatialIntelligenceAgent

Purpose: connect finance and governance data to geography.

Responsibilities:

- Ingest ward boundaries into PostGIS.
- Store spatial source metadata.
- Join ward-level property tax and population data where available.
- Support future layers for built-up growth, road networks, infrastructure coverage, unauthorized colonies, flood zones, and land-use mismatch.
- Generate data gaps when spatial data is unavailable.

CLI:

```bash
muni spatial ingest --city <city_slug> --layer wards --path ./wards.geojson
muni spatial layers --city <city_slug>
muni spatial join-tax --city <city_slug>
```

### Agent 8 - AnomalyDetectionAgent

Purpose: detect multi-year patterns that single-year analysis misses.

Responsibilities:

- Detect pre-election capex spikes.
- Detect property tax plateau.
- Detect grant absorption failure.
- Detect salary creep.
- Detect O&M collapse.
- Detect sudden new revenue heads.
- Detect negative capex years.
- Use election-year config from city/state profile.

CLI:

```bash
muni anomalies run --city <city_slug>
muni anomalies list --city <city_slug>
muni anomalies explain <anomaly_id>
```

### Agent 9 - VisualizationAgent

Purpose: produce publication-ready visuals for research outputs.

Responsibilities:

- Generate:
  - Revenue Sankey
  - Revenue stacked bar
  - Expenditure donut
  - Property tax DCB waterfall
  - Fiscal trend line chart
  - Governance network map
  - Ward heatmap where data exists
- Export Twitter/X-ready `1200x675` images.
- Include city, fiscal year, and source footer or metadata.
- Avoid more than five data series per chart.
- Avoid red/green-only palettes.

CLI:

```bash
muni visualize --city <city_slug> --pack fiscal-health
muni visualize one --city <city_slug> --chart property-tax-dcb --year 2022-23
```

### Agent 10 - NarrativeSynthesisAgent

Purpose: convert structured analysis into public-facing research drafts.

Responsibilities:

- Produce a Substack-style draft.
- Produce a 20-post X/Twitter thread.
- Use INR crore as the default public unit.
- Insert evidence links for quantitative claims.
- Insert caveats for uncertain data.
- Avoid unsupported claims.
- Stop if critical review items remain unless explicitly overridden.

CLI:

```bash
muni narrative draft --city <city_slug> --format substack
muni narrative draft --city <city_slug> --format twitter
muni export --city <city_slug> --bundle fiscal-health
```

## CLI Behavior

The CLI should support both individual agents and full workflows.

Setup:

```bash
muni init
muni doctor
muni city add --slug <city_slug> --name "<City Name>" --state "<State>"
muni sources add --city <city_slug> --url <official_url> --type <source_type>
muni sources list --city <city_slug>
```

Run one agent:

```bash
muni discover --city <city_slug>
muni classify --city <city_slug>
muni extract --city <city_slug> --priority P1
muni normalize --city <city_slug>
muni analyze --city <city_slug> --years 2019-20:2023-24
```

Run the full workflow:

```bash
muni run all \
  --city <city_slug> \
  --name "<City Name>" \
  --state "<State>" \
  --municipal-url <official_municipal_url> \
  --years 2019-20:2023-24
```

`muni run all` must run:

1. `doctor` checks.
2. City profile validation or creation.
3. Source validation.
4. DocumentDiscoveryAgent.
5. DocumentClassificationAgent.
6. OCRExtractionAgent.
7. OntologyNormalizationAgent.
8. FiscalAnalysisAgent.
9. GovernanceMappingAgent.
10. SpatialIntelligenceAgent where spatial inputs exist.
11. AnomalyDetectionAgent.
12. VisualizationAgent.
13. NarrativeSynthesisAgent.
14. Export bundle.

Default behavior: stop before narrative generation if critical review items remain.

Override:

```bash
muni run all --city <city_slug> --years 2019-20:2023-24 --allow-review-gaps
```

Inspection commands:

```bash
muni docs list --city <city_slug> --priority P1
muni docs show <doc_id>
muni review queue --city <city_slug>
muni review approve <review_id>
muni metrics table --city <city_slug>
muni anomalies list --city <city_slug>
muni evidence show --metric own_source_revenue_ratio --city <city_slug> --year 2022-23
muni trace <record_id>
```

## Evidence And Data Model

The database must support cumulative research, not one-off outputs.

Minimum entities:

| Entity | Purpose |
|---|---|
| `cities` | City metadata, languages, fiscal rules, population references |
| `city_sources` | Official source URLs per city |
| `agent_runs` | Per-agent run status, timestamps, warnings, errors |
| `documents` | Source URL, file path, hash, document type, city, year, priority |
| `document_pages` | Extracted text, OCR status, page language, page quality |
| `extraction_records` | Raw extracted values with page references and confidence |
| `financial_facts` | Normalized fiscal facts in INR and canonical units |
| `ontology_mappings` | Raw labels mapped to canonical categories |
| `metrics` | Computed indicators by city and fiscal year |
| `metric_inputs` | Formula inputs for traceability |
| `red_flags` | Fiscal stress and anomaly findings |
| `agencies` | City-specific agencies |
| `service_responsibilities` | Who plans, funds, builds, operates, regulates |
| `spatial_layers` | GIS layer metadata and source references |
| `visualizations` | Chart artifacts and source dependencies |
| `narrative_outputs` | Drafts, threads, and claim references |
| `review_items` | Human review queue for uncertainty and low confidence |

Every important record should connect back to evidence.

```text
claim -> metric -> metric_inputs -> financial_facts -> extraction_records -> document_page -> document -> source_url
```

## Review Gates

Agents should create review items instead of guessing.

Review item types:

- `UNAPPROVED_SOURCE`
- `UNKNOWN_DOCUMENT_TYPE`
- `MISSING_FISCAL_YEAR`
- `LOW_CONFIDENCE_OCR`
- `TABLE_EXTRACTION_FAILED`
- `UNIT_AMBIGUITY`
- `NEGATIVE_VALUE_REVIEW`
- `UNCERTAIN_ONTOLOGY_MAPPING`
- `MISSING_GOVERNANCE_SOURCE`
- `SPATIAL_DATA_GAP`
- `UNSUPPORTED_NARRATIVE_CLAIM`

Hard gates:

- No unapproved source can enter final analysis.
- No number without page-level evidence can enter final narrative.
- Critical low-confidence facts must be reviewed before narrative export.
- Narrative generation must stop if evidence links are missing, unless the user explicitly allows review gaps.

## Python Tech Stack

Use Python for implementation speed and strong PDF/data tooling.

| Layer | Tooling |
|---|---|
| CLI | Typer + Rich |
| Agent Runtime | Python classes with shared context/result models |
| Config | YAML, later Pydantic validation |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Primary Database | PostgreSQL + PostGIS |
| Local Early Development | SQLite allowed for bootstrap/tests only |
| HTTP | httpx |
| HTML Parsing | BeautifulSoup or selectolax |
| PDF Text | pdfplumber + pypdf |
| OCR | pytesseract + Tesseract `eng+hin` |
| OCR Fallback | Google Vision or Azure OCR |
| Tables | Camelot + Tabula-py |
| Data Analysis | pandas + numpy |
| Spatial | GeoPandas + Shapely + PostGIS |
| Charts | matplotlib, seaborn, plotly, later D3/Observable where needed |
| Templates | Jinja2 |
| LLM Adapter | Provider-neutral interface for ontology/narrative only when useful |
| Testing | pytest |
| Formatting | ruff |

Future scale-up:

- Redis for queues and crawl rate limiting.
- S3-compatible object storage for PDFs and artifacts.
- Qdrant for semantic search over extracted document text.
- FastAPI for a future API surface.

## Repository Structure

Target structure:

```text
.
├── muni/
│   ├── cli.py
│   ├── config.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── context.py
│   │   ├── result.py
│   │   ├── orchestrator.py
│   │   ├── discovery.py
│   │   ├── classification.py
│   │   ├── extraction.py
│   │   ├── ontology.py
│   │   ├── fiscal_analysis.py
│   │   ├── governance.py
│   │   ├── spatial.py
│   │   ├── anomaly.py
│   │   ├── visualization.py
│   │   └── narrative.py
│   ├── cities/
│   ├── sources/
│   ├── documents/
│   ├── extraction/
│   ├── ontology/
│   ├── analysis/
│   ├── governance/
│   ├── spatial/
│   ├── visualization/
│   ├── narrative/
│   ├── review/
│   └── db/
├── configs/
│   ├── domains.yaml
│   ├── ontology.yaml
│   └── cities/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── charts/
│   └── exports/
├── tests/
├── project.md
├── plan.md
└── tracker.md
```

Agent classes should orchestrate domain services. Domain services should hold reusable deterministic logic.

Example:

```text
DocumentClassificationAgent
  -> documents/classifier.py
  -> documents/fiscal_year.py
  -> documents/language.py
  -> review/queue.py
```

## Implementation Phases

### Phase 0 - Bootstrap - Complete

Implemented:

- Python package skeleton.
- Typer CLI.
- `muni init`.
- `muni doctor`.
- SQLAlchemy/Alembic bootstrap.
- pytest and ruff.

### Phase 1 - City Profiles and Source Registry - Complete

Implemented:

- City profiles.
- `muni city add/list/show`.
- Source registration.
- Domain whitelist validation.
- `muni sources add/list`.

### Phase 2 - Agent Runtime Foundation

Deliverables:

- `muni/agents/base.py`.
- `muni/agents/context.py`.
- `muni/agents/result.py`.
- `muni/agents/orchestrator.py`.
- Agent run logging model or file-backed run log.
- Agent registry mapping CLI commands to agent classes.
- No-op or minimal implementations for all 10 agents.
- `muni run all` should invoke the orchestrator and show per-agent status, even if most agents are placeholders.

Acceptance criteria:

- All 10 agent classes exist.
- Every agent returns an `AgentResult`.
- `muni run all` executes agents in order.
- Failed/blocked agents are reported clearly.
- Tests cover the orchestrator order and result handling.

### Phase 3 - Document Evidence Store and Local Ingestion

Deliverables:

- Document metadata model.
- Local PDF ingestion.
- SHA-256 hashing.
- Exact duplicate detection.
- `muni ingest` implemented through DocumentDiscoveryAgent or ingestion service.
- `muni docs list`.
- `muni docs show`.

Acceptance criteria:

- Documents are associated with city profiles.
- Duplicate hashes are skipped.
- Every document has source/path/hash/capture metadata.

### Phase 4 - DocumentDiscoveryAgent Web Discovery

Deliverables:

- Official source crawler.
- PDF link discovery.
- Domain whitelist enforcement during crawl.
- Broken-link logging.
- Parent page capture.
- Basic download manager.

Acceptance criteria:

- Non-whitelisted URLs are rejected.
- Discovered PDFs are stored as document records.
- Broken links and skipped sources are visible in agent results.

### Phase 5 - DocumentClassificationAgent

Deliverables:

- Rule-based taxonomy classifier.
- Fiscal-year parser.
- Language tagger.
- Priority ranking.
- Near-duplicate detection.
- Review queue integration.

Acceptance criteria:

- P1 documents can be listed.
- Uncertain documents create review items.
- Classification reason codes are stored.

### Phase 6 - OCRExtractionAgent

Deliverables:

- PDF text extraction.
- OCR routing.
- Table extraction.
- Revenue/expenditure/property-tax extraction schemas.
- Unit normalization.
- Confidence scoring.

Acceptance criteria:

- Extracted facts include page-level evidence.
- Low-confidence records create review items.
- Normalized values preserve raw text.

### Phase 7 - OntologyNormalizationAgent

Deliverables:

- Canonical category mapping.
- Mapping log.
- Fiscal-year normalization.
- Review workflow for uncertain mappings.

Acceptance criteria:

- Raw labels are preserved.
- Uncertain mappings are not silently merged.
- Mappings work across more than one city.

### Phase 8 - FiscalAnalysisAgent

Deliverables:

- Core fiscal metrics.
- Property tax DCB analysis.
- Fiscal stress red flags.
- Evidence traces for formulas.

Acceptance criteria:

- Metrics can be traced to source pages.
- Red flags include rule, threshold, values, and evidence.

### Phase 9 - GovernanceMappingAgent

Deliverables:

- Agency registry.
- Service responsibility matrix.
- Source-backed responsibility claims.

Acceptance criteria:

- Unknown fields are marked `UNKNOWN`.
- Agency claims cite evidence.

### Phase 10 - SpatialIntelligenceAgent

Deliverables:

- Spatial layer metadata.
- Ward boundary ingestion.
- Ward tax/population joins where available.
- Spatial data-gap review items.

Acceptance criteria:

- Ward geometries load into PostGIS when configured.
- Missing spatial data does not block non-spatial analysis.

### Phase 11 - AnomalyDetectionAgent

Deliverables:

- Multi-year anomaly rules.
- Election-year config usage.
- Anomaly explanation command.

Acceptance criteria:

- Anomalies include rule, threshold, years, values, and evidence.

### Phase 12 - VisualizationAgent

Deliverables:

- Fiscal-health chart pack.
- Chart metadata.
- `1200x675` export.
- Source footers.

Acceptance criteria:

- At least five charts generated when data exists.
- Charts are evidence-linked.

### Phase 13 - NarrativeSynthesisAgent

Deliverables:

- Substack draft.
- 20-post X/Twitter thread.
- Evidence-linked claims.
- Export bundle.

Acceptance criteria:

- Every quantitative claim has evidence.
- Critical review gaps stop final export by default.

## Recommended First Real Workflow

Use Varanasi only as the first validation city, not as a product limitation.

```bash
muni run all \
  --city varanasi \
  --name "Varanasi" \
  --state "Uttar Pradesh" \
  --municipal-url https://vmc.up.gov.in \
  --years 2019-20:2023-24
```

Initial target documents:

- VMC annual budgets for at least three years.
- Latest CAG Uttar Pradesh local bodies audit report.
- AMRUT or Smart City utilization report.
- Property tax DCB record if available.
- Master plan or development authority document for governance context.

Pilot success criteria:

- 100 percent of final numbers trace to primary-source document pages.
- 0 secondary sources used as factual evidence.
- All core fiscal metrics computed for at least 3 years where data exists.
- Minimum 5 charts when data supports them.
- 1 Substack-style draft.
- 1 X/Twitter thread with exactly 20 posts.

## Next Step

Before continuing document ingestion, implement Phase 2: the agent runtime foundation.

This keeps the code aligned with `project.md`: a municipal intelligence agent system controlled by a CLI, not a CLI pipeline that later tries to retrofit agents.
