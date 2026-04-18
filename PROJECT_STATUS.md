# SmartISMS — Project Status

> Last updated: 2026-04-18

---

## 1. Completed Backend Modules

### `backend/isms_core/` — Core Engine
| Module | Purpose |
|--------|---------|
| `rule_engine.py` | Generic control evaluator (load controls + evaluate) |
| `compliance_calculator.py` | Compliance percentage calculator |
| `report_history_manager.py` | JSON-file-based report persistence (save/get/get_latest) |
| `assessment_service.py` | Run + save assessment (single standard) |
| `company_report_summary.py` | Company-level report summary |
| `standard_profiles_loader.py` | Load standard profiles JSON |
| `standard_recommender.py` | Recommend standards by organization type |
| `assessment_session_initializer.py` | Session bootstrap utility |

### `backend/assessment/` — Assessment Pipeline
| Module | Purpose |
|--------|---------|
| `input_mapper.py` | Normalize raw input to check_key mapping |
| `assessment_runner.py` | Single-standard assessment runner |
| `full_assessment_runner.py` | Full pipeline: map, evaluate, risks, heatmap, treatment |
| `result_formatter.py` | Format evaluation results |
| `risk_engine.py` | Generate risks from failed controls |
| `risk_register_formatter.py` | Format risk register with summary |
| `heatmap_generator.py` | Generate risk heatmap grid |
| `treatment_plan_generator.py` | Generate treatment actions for risks |
| `assessment_output_builder.py` | Assemble final assessment output |
| `multi_standard_assessment_runner.py` | Optional utility only (disconnected from main flow) |

### `backend/config_analysis/` — Configuration Analysis
| Module | Purpose |
|--------|---------|
| `config_input_mapper.py` | Normalize raw config to boolean schema |
| `config_analysis_runner.py` | Map + evaluate config against baseline |
| `technical_findings_formatter.py` | Format findings summary + details |
| `technical_risk_engine.py` | Generate technical risks from failed checks |

### `backend/integration/` — Combined Pipeline
| Module | Purpose |
|--------|---------|
| `combined_output_builder.py` | Merge assessment + technical analysis |
| `full_combined_runner.py` | Orchestrate both pipelines into unified output |

### `backend/reporting/` — Report Generation
| Module | Purpose |
|--------|---------|
| `executive_report_formatter.py` | Format assessment-only executive report |
| `pdf_report_generator.py` | Generate assessment-only PDF |
| `report_export_service.py` | Export assessment-only PDF by company |
| `combined_report_formatter.py` | Format combined report (assessment + technical) |
| `combined_pdf_report_generator.py` | Generate combined PDF with 7 sections |
| `combined_report_export_service.py` | Export combined PDF by company |

### `backend/standards/` — Standard Files
| File | Controls |
|------|----------|
| `iso27001.json` | 5 |
| `pci_dss.json` | 5 |
| `hipaa.json` | 5 |
| `nist.json` | 5 |
| `cis.json` | 5 |
| `sama.json` | 5 |
| `config_baseline.json` | 5 |
| `standard_profiles.json` | 6 profiles with applicability rules |

---

## 2. Completed Frontend Pages

| Route | Page | Status |
|-------|------|--------|
| `/` | Home — title, subtitle, 3 navigation cards | Static |
| `/assessment` | Assessment — form inputs + results display | Integrated with backend |
| `/config-analysis` | Config Analysis — placeholder only | Not integrated |
| `/reports` | Reports — report list + export PDF | Integrated with backend |

### Shared Components
- `Navbar.js` — navigation links + theme toggle
- `PageContainer.js` — centered page layout wrapper
- `PlaceholderSection.js` — dashed placeholder for upcoming features
- `lib/api.js` — configurable API base URL

---

## 3. Active API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check |
| `POST` | `/run-full-analysis` | Run combined analysis (no save) |
| `POST` | `/run-and-save-assessment` | Run combined analysis + save report |
| `GET` | `/reports/{company_id}` | Get all saved reports for a company |
| `POST` | `/export-latest-report` | Export latest assessment-only PDF |

---

## 4. Working End-to-End Flows

1. **Assessment → Save → Reports**
   - User fills form on `/assessment` → clicks Run → backend runs combined analysis → saves report → results displayed → report appears on `/reports`

2. **Reports Listing**
   - `/reports` fetches saved reports for company `C001` → displays in table with compliance %, standard, timestamp

3. **PDF Export (assessment-only)**
   - `/export-latest-report` generates a PDF from the latest saved assessment

4. **Combined PDF Generation (standalone)**
   - `combined_pdf_report_generator.py` generates a 7-section PDF from combined output

---

## 5. Known Gaps / Not Yet Implemented

- [ ] Config Analysis page not integrated with backend
- [ ] Combined PDF export not wired to an API endpoint
- [ ] No authentication or user management
- [ ] No file upload for security inputs
- [ ] No dynamic company ID — hardcoded to `C001`
- [ ] No charts or visual analytics on frontend
- [ ] No severity-based risk scoring (all risks use fixed likelihood=3, impact=3)
- [ ] Recommendation engine exists in older codebase but not integrated here
- [ ] No database — reports stored as JSON files
- [ ] Standard files have 5 controls each — production would need more

---

## 6. Suggested Next 5 Tasks

1. **Integrate the Config Analysis page** — wire `/config-analysis` to a dedicated backend endpoint
2. **Add combined PDF export endpoint** — expose `POST /export-combined-report` using the existing combined PDF generator
3. **Add dynamic company ID support** — allow multiple companies from the frontend
4. **Add compliance charts** — render compliance percentage and risk breakdown visually
5. **Add severity-aware risk scoring** — use control `severity` field to compute variable likelihood/impact
