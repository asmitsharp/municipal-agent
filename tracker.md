# Municipal Intelligence CLI Tracker

## Purpose

Use this file as the agent handoff and execution tracker. When switching agents, read this file first, then `plan.md`, then inspect the git diff/status.

This tracker should be updated whenever meaningful work is completed, blocked, or deliberately deferred.

## Current State

- Project status: Phase 3 local ingestion complete; web discovery crawler pending.
- Primary implementation plan: `plan.md`.
- Architecture source document: `project.md`.
- Current product direction: city-agnostic municipal intelligence agent system with a Python CLI control surface.
- Default user-facing command: `muni run all`.
- Starter example city: Varanasi only as an example, not a product limitation.
- Git status at tracker creation: clean after commit `adf3e93`.
- Current implementation includes Python package skeleton, Typer CLI, config initialization, doctor checks, SQLAlchemy/Alembic bootstrap, pytest, and ruff.
- City profiles and source registration are file-based under `configs/cities/`.

## Key Decisions

- Use Python for the implementation instead of Go.
- Use `Typer` for the CLI and `Rich` for terminal output.
- Use city profiles so the system can support any Indian city.
- Keep city-specific source URLs, agencies, fiscal-year rules, languages, ward layers, and election years in config.
- Use PostgreSQL + PostGIS as the primary database.
- Allow SQLite only for lightweight local tests.
- Require primary-source traceability for every numeric fact.
- Treat low-confidence extraction as a human-review item before final narrative export.
- Provide both step-by-step commands and one full workflow command.
- Agents are now first-class architecture objects. The CLI should call agents or workflows; it should not become the core business-logic layer.

## CLI Direction

Main command:

```bash
muni run all \
  --city <city_slug> \
  --name "<City Name>" \
  --state "<State>" \
  --municipal-url <official_municipal_url> \
  --years 2019-20:2023-24
```

Expected `muni run all` stages:

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

Default behavior: stop before narrative export if critical review items remain.

Override:

```bash
muni run all --city <city_slug> --years 2019-20:2023-24 --allow-review-gaps
```

## Phase Tracker

Status legend:

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- `[!]` Blocked
- `[-]` Deferred

### Phase 0 - Python Project Bootstrap

- [x] Create Python package structure under `muni/`.
- [x] Add `pyproject.toml`.
- [x] Add Typer CLI entrypoint.
- [x] Add `muni init`.
- [x] Add `muni doctor`.
- [x] Add Rich terminal output helpers.
- [x] Add config loading from YAML.
- [x] Add local `data/` directory creation.
- [x] Add SQLAlchemy session setup.
- [x] Add Alembic migration setup.
- [x] Add pytest.
- [x] Add ruff.
- [x] Verify `muni --help`.

Acceptance checkpoint:

- [x] `muni --help` shows command groups.
- [x] `muni init` creates required local directories.
- [x] `muni doctor` reports dependency status.
- [x] Empty database migrations run cleanly.

### Phase 1 - City Profiles and Source Registry

- [x] Add city profile schema.
- [x] Add `muni city add`.
- [x] Add `muni city list`.
- [x] Add `muni city show`.
- [x] Add `muni sources add`.
- [x] Add `muni sources list`.
- [x] Add domain whitelist config.
- [x] Enforce official domain validation.
- [x] Store city profiles under `configs/cities/`.

Acceptance checkpoint:

- [x] New city can be added without code changes.
- [x] Non-whitelisted source domains are rejected.
- [x] Official sources are linked to city profiles.

### Phase 2 - Agent Runtime Foundation

- [x] Add `muni/agents/base.py`.
- [x] Add `muni/agents/context.py`.
- [x] Add `muni/agents/result.py`.
- [x] Add `muni/agents/orchestrator.py`.
- [x] Add all 10 planned agent classes as concrete or placeholder classes.
- [x] Add shared `AgentContext`.
- [x] Add shared `AgentResult`.
- [x] Add agent registry.
- [x] Wire `muni run all` through the orchestrator.
- [x] Add per-agent status output.
- [x] Add tests for orchestrator order and result handling.

Acceptance checkpoint:

- [x] All 10 agent classes exist.
- [x] Every agent returns an `AgentResult`.
- [x] `muni run all` executes agents in documented order.
- [x] Failed or blocked agents are reported clearly.

### Phase 3 - Document Evidence Store and Local Ingestion

- [ ] Add PDF link crawler for registered official sources.
- [x] Add manual local ingestion.
- [x] Add SHA-256 hashing.
- [x] Add duplicate detection by hash.
- [ ] Add broken-link logging.
- [ ] Add normalized filename generation.
- [ ] Add `muni discover`.
- [x] Add `muni ingest`.
- [x] Add `muni docs list`.
- [x] Add `muni docs show`.

Acceptance checkpoint:

- [ ] Unknown domains rejected before download.
- [x] Duplicate documents skipped.
- [x] Every document stores source URL, local path, hash, and capture timestamp.

### Phase 4 - Document Classification

- [ ] Add document taxonomy.
- [ ] Add rule-based classifier.
- [ ] Add fiscal year detection from filename.
- [ ] Add fiscal year detection from first pages.
- [ ] Add language tagging: `ENGLISH`, `HINDI`, `BILINGUAL`, `MIXED`.
- [ ] Add priority ranking P1-P5.
- [ ] Add near-duplicate detection.
- [ ] Add review item creation for uncertain classification.
- [ ] Add `muni classify`.

Acceptance checkpoint:

- [ ] Classification includes reason codes.
- [ ] Uncertain classifications enter review queue.
- [ ] Hindi/scanned documents are routed to OCR.

### Phase 5 - OCR and Structured Extraction

- [ ] Add text-native PDF extraction with `pdfplumber` / `pypdf`.
- [ ] Add scanned PDF OCR with Tesseract `eng+hin`.
- [ ] Add table extraction with Camelot or Tabula.
- [ ] Add extraction schemas for own-source revenue.
- [ ] Add extraction schemas for external transfers.
- [ ] Add extraction schemas for expenditure.
- [ ] Add extraction schemas for property tax DCB.
- [ ] Add extraction schemas for capital works.
- [ ] Add extraction schemas for debt service.
- [ ] Add unit normalization for crore/lakh.
- [ ] Add Indian comma grouping parser.
- [ ] Add missing value and negative value handling.
- [ ] Add confidence scoring.
- [ ] Add `muni extract`.
- [ ] Add `muni trace`.

Acceptance checkpoint:

- [ ] Every extracted value has document ID, page number, raw text, normalized value, confidence, and method.
- [ ] Low-confidence OCR results enter review queue.
- [ ] No extracted number is stored without source reference.

### Phase 6 - Ontology and Normalization

- [ ] Add canonical municipal categories.
- [ ] Add raw budget head mapping.
- [ ] Add mapping log.
- [ ] Add uncertain mapping review workflow.
- [ ] Add fiscal year normalization.
- [ ] Add `muni normalize`.
- [ ] Add `muni ontology unmapped`.
- [ ] Add `muni ontology approve`.

Acceptance checkpoint:

- [ ] Raw names remain preserved.
- [ ] Uncertain mappings are not silently merged.
- [ ] Same ontology works across multiple cities.

### Phase 7 - Fiscal Analysis Engine

- [ ] Add Own Source Revenue Ratio.
- [ ] Add Property Tax Collection Efficiency.
- [ ] Add Property Tax per Capita.
- [ ] Add Salary-to-Total Expenditure Ratio.
- [ ] Add Capital Expenditure Ratio.
- [ ] Add Grant Dependence Ratio.
- [ ] Add Debt Service Coverage.
- [ ] Add Revenue per Capita.
- [ ] Add O&M Spending per Sector.
- [ ] Add property tax DCB analysis.
- [ ] Add fiscal stress red flags.
- [ ] Add metric evidence traces.
- [ ] Add `muni analyze`.
- [ ] Add `muni metrics table`.
- [ ] Add `muni evidence show`.

Acceptance checkpoint:

- [ ] Metrics run for at least three fiscal years when data exists.
- [ ] Formula inputs are visible through evidence commands.
- [ ] Red flags are generated from configured thresholds.

### Phase 8 - Governance Mapping

- [ ] Add city-specific agency registry.
- [ ] Add service responsibility matrix.
- [ ] Add source references for agency responsibility claims.
- [ ] Add `muni governance map`.
- [ ] Add `muni governance service`.

Acceptance checkpoint:

- [ ] Each service records who plans, funds, builds, operates, and regulates.
- [ ] Unknown responsibility fields are marked `UNKNOWN`, not guessed.
- [ ] Agency names come from city config and discovered documents.

### Phase 9 - GIS and Spatial Intelligence

- [ ] Add PostGIS spatial layer model.
- [ ] Add ward boundary ingestion.
- [ ] Add spatial source metadata.
- [ ] Add ward-level tax join support.
- [ ] Add ward-level population join support.
- [ ] Add `muni spatial ingest`.
- [ ] Add `muni spatial layers`.
- [ ] Add `muni spatial join-tax`.

Acceptance checkpoint:

- [ ] Ward geometries load into PostGIS.
- [ ] Spatial source metadata is preserved.
- [ ] Missing ward-level tax data creates a review/data-gap item.

### Phase 10 - Trend and Anomaly Detection

- [ ] Add pre-election capex spike rule.
- [ ] Add property tax plateau rule.
- [ ] Add grant absorption failure rule.
- [ ] Add salary creep rule.
- [ ] Add O&M collapse rule.
- [ ] Add sudden new revenue head rule.
- [ ] Add negative capex year rule.
- [ ] Add state/city election-year config.
- [ ] Add `muni anomalies run`.
- [ ] Add `muni anomalies list`.
- [ ] Add `muni anomalies explain`.

Acceptance checkpoint:

- [ ] Each anomaly includes rule, years, metric values, threshold, and evidence.
- [ ] Election rules use config, not hard-coded dates.

### Phase 11 - Visualization

- [ ] Add revenue Sankey chart.
- [ ] Add revenue stacked bar chart.
- [ ] Add expenditure donut chart.
- [ ] Add property tax DCB waterfall chart.
- [ ] Add fiscal trend line chart.
- [ ] Add governance network map.
- [ ] Add ward heatmap when spatial data exists.
- [ ] Add chart metadata output.
- [ ] Add `1200x675` export size.
- [ ] Add `muni visualize`.
- [ ] Add `muni visualize one`.

Acceptance checkpoint:

- [ ] At least five charts generated when data exists.
- [ ] Each chart has source metadata.
- [ ] No chart uses more than five data series.
- [ ] Red/green-only palettes are avoided.

### Phase 12 - Narrative Synthesis

- [ ] Add Substack markdown draft generator.
- [ ] Add 20-post Twitter thread generator.
- [ ] Add evidence links for quantitative claims.
- [ ] Add caveats for uncertain data.
- [ ] Add export bundle.
- [ ] Add `muni narrative draft`.
- [ ] Add `muni export`.

Acceptance checkpoint:

- [ ] Article follows `project.md` research structure.
- [ ] Thread contains exactly 20 posts.
- [ ] Every quantitative claim links to evidence.
- [ ] Export includes source bibliography with document page references.

## One-Command Workflow Tracker

- [ ] Add `muni run all`.
- [ ] Support first-time flags: `--name`, `--state`, `--municipal-url`.
- [ ] Create city profile if missing.
- [ ] Register default national sources if missing.
- [x] Run stages in documented order.
- [ ] Stop before narrative export if critical review items remain.
- [ ] Add `--allow-review-gaps`.
- [x] Print stage-by-stage summary.
- [ ] Persist failed stage details for resume.
- [ ] Add rerun/resume behavior.

## Testing Tracker

- [x] Domain whitelist validation tests.
- [x] City profile parsing tests.
- [ ] SHA-256 duplicate detection tests.
- [ ] Fiscal year parser tests.
- [ ] Language tagger tests.
- [ ] Unit normalization tests.
- [ ] Metric formula tests.
- [ ] Red flag threshold tests.
- [x] Add-city integration test.
- [x] Register-source integration test.
- [x] Agent result validation test.
- [x] Orchestrator order and blocked-result test.
- [x] `muni run all` orchestrator integration test.
- [ ] Fixture PDF ingestion test.
- [ ] Fixture classification test.
- [ ] Fixture table extraction test.
- [ ] Chart metadata generation test.

## Golden Fixtures Needed

- [ ] Text-native English budget PDF.
- [ ] Scanned Hindi budget PDF sample.
- [ ] CAG report table.
- [ ] Property tax DCB table.
- [ ] Malformed document with missing fiscal year.

## Open Questions

- Which package manager should be used long-term: `uv` or Poetry? Current bootstrap uses setuptools with editable `pip install -e ".[dev]"`.
- Should local development require PostgreSQL after Phase 0, or continue allowing SQLite through early phases? Current bootstrap defaults to SQLite for local CLI checks.
- Which LLM provider should the narrative and ontology adapter target first?
- Should OCR fallback use Google Vision or Azure OCR first?
- What should be the first real city dataset for implementation testing?

## Blockers

- No implementation blockers yet.
- Real source PDFs are not yet collected.
- OCR dependencies are not yet verified on the machine.
- Database choice for first runnable version needs confirmation.

## Completed Work Log

### 2026-05-16

- Created `plan.md` from `project.md`.
- Revised `plan.md` to make the system city-agnostic.
- Changed implementation direction from Go to Python.
- Added CLI behavior explanation.
- Added one-command workflow: `muni run all`.
- Committed the plan updates in commit `adf3e93` with message `Refine municipal CLI implementation plan`.
- Created this `tracker.md`.
- Implemented Phase 0 bootstrap:
  - Added `pyproject.toml`, `README.md`, `.gitignore`, and package skeleton under `muni/`.
  - Added Typer CLI entrypoint with planned command groups and Phase 0 placeholders.
  - Added `muni init` to create config files and local data directories.
  - Added `muni doctor` with Python, workspace, database, PostGIS, Tesseract, Java, and domain-config checks.
  - Added YAML config helpers with default `domains.yaml` and `ontology.yaml`.
  - Added SQLAlchemy engine/session helpers and Alembic migration bootstrap.
  - Added pytest CLI tests and ruff configuration.
- Verification passed:
  - `python3 -m pip install -e ".[dev]"`
  - `muni --help`
  - `muni init`
  - `muni doctor`
  - `alembic upgrade head`
  - `python3 -m pytest`
  - `python3 -m ruff check .`
- Implemented Phase 1 city profile and source registry:
  - Added `muni/cities/schemas.py` and `muni/cities/service.py`.
  - Added `muni/sources/whitelist.py`.
  - Implemented `muni city add`, `muni city list`, and `muni city show`.
  - Implemented `muni sources add` and `muni sources list`.
  - Enforced official source domain validation using `configs/domains.yaml`.
  - Added tests for city creation/list/show, source registration, and source rejection.
- Phase 1 verification passed:
  - `python3 -m pytest`
  - `python3 -m ruff check .`
  - `muni city add --help`
  - `muni sources add --help`
- Rewrote `plan.md` to correct the architecture:
  - Agents are now the core system design.
  - The CLI is explicitly the control surface, not the architecture.
  - Phase 2 is now Agent Runtime Foundation.
  - Document ingestion moved after the agent runtime.
  - Added the 10 named agents, shared `AgentContext`, shared `AgentResult`, orchestration model, evidence chain, and review gates.
- Implemented Phase 2 agent runtime foundation:
  - Added `muni/agents/base.py`, `context.py`, `result.py`, and `orchestrator.py`.
  - Added all 10 named agent classes as first-class placeholder agents.
  - Added `DEFAULT_AGENT_CLASSES` registry.
  - Wired `muni run all` through `AgentOrchestrator`.
  - Added first-time city setup and source registration to `muni run all`.
  - Added per-agent status table output.
  - Added tests for invalid agent status, orchestrator order, blocked results, and CLI orchestration.
- Phase 2 verification passed:
  - `python3 -m pytest`
  - `python3 -m ruff check .`
  - Direct smoke test of `muni run all` through Typer runner.

### 2026-05-17

- Implemented Phase 3 document ingestion foundation:
  - Added `Document` database model using SQLAlchemy.
  - Generated and ran Alembic migration for `documents` table.
  - Implemented `muni.documents.service` with SHA-256 hashing and local duplicate detection.
  - Updated `muni ingest` CLI to support file and directory imports.
  - Updated `muni docs list` and `muni docs show` CLI to display document metadata.
  - Manually verified ingestion logic with dummy file test.

## Next Recommended Task

Start Phase 3 Crawler:

1. Add PDF link crawler for registered official sources.
2. Implement `muni discover`.
3. Integrate broken-link logging.
4. Integrate normalized filename generation.
5. Add fixture-file tests before implementing web crawling.

Keep ingestion behind the agent architecture: CLI commands should call an agent or agent-owned service, not isolated one-off functions.
