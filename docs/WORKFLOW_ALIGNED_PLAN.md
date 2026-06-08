# Workflow-Aligned Implementation Plan

This document supersedes the earlier 4-role plan. It aligns the implementation with `FPA_PRD_WORKFLOW.md` which defines **only two roles: Admin and Staff**.

---

## 1. Role Model Change Summary

| Previous Plan (4 roles) | Workflow Doc (2 roles) | Resolution |
|---|---|---|
| Super Admin | Admin | Merged into `Admin` |
| Operator | Staff | Renamed to `Staff` |
| Consultant | Admin (review) | Folded into Admin (review = Admin only) |
| Client/Parent | (not in app) | Removed from app role enum — clients are *participants*, not users |

**Final role enum (MVP):**
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
```

**Participant ≠ User.** Participants are stored in `scan_sessions` directly (`participant_name`, `participant_age`, `participant_gender`, `notes`). No separate `clients` table needed for MVP.

---

## 2. Session Status Lifecycle (from workflow §6)

```
DRAFT → REGISTERED → SCANNING → SCAN_COMPLETED → WAITING_FOR_REVIEW
  → APPROVED → GENERATING_REPORT → REPORT_GENERATED
  → (alt) REJECTED
  → (alt) NEED_RESCAN → SCANNING → ...
```

**Updated enum:**
```python
class SessionStatus(str, Enum):
    DRAFT = "draft"
    REGISTERED = "registered"
    SCANNING = "scanning"
    SCAN_COMPLETED = "scan_completed"
    WAITING_FOR_REVIEW = "waiting_for_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEED_RESCAN = "need_rescan"
    GENERATING_REPORT = "generating_report"
    REPORT_GENERATED = "report_generated"
```

Replaces the current 3-value enum (`IN_PROGRESS`, `COMPLETED`, `FAILED`).

---

## 3. Permissions Matrix (from workflow §10)

| Feature | Admin | Staff |
|---|:--:|:--:|
| Login | ✓ | ✓ |
| Register users | ✓ | ✗ |
| Register session | ✓ | ✓ |
| Scan fingers | ✓ | ✓ |
| Preview scan | ✓ | ✓ |
| Submit scan | ✓ | ✓ |
| Review scan | ✓ | ✗ |
| Approve / Reject / Rescan | ✓ | ✗ |
| Generate report | ✓ | ✗ |
| View report history | ✓ | ✓ |
| Download PDF | ✓ | Optional |
| Account profile | ✓ | ✓ |

---

## 4. Updated Sprint Roadmap (7 sprints, ~8 weeks)

### Sprint 0 — Foundation Alignment (3 days) — **NEW, starts now**
- [ ] Update `User.role` (replace `is_admin` bool with `UserRole` enum)
- [ ] Update `SessionStatus` enum to 10-value lifecycle
- [ ] Add `participant_name`, `participant_age`, `participant_gender`, `notes` to `ScanSession`
- [ ] Add `reviewed_by_id`, `reviewed_at`, `rejection_reason` to `ScanSession`
- [ ] Alembic migration 002
- [ ] RBAC dependency `require_role(...)` in `app/middleware/auth.py`
- [ ] Apply role guards to all routers

### Sprint 1 — Image Processing Pipeline (1.5 weeks)
Implements PRD FR-07 fully. See `SPRINT_1_IMPLEMENTATION.md` for code.
- preprocessing.py (CLAHE, bilateral, Sauvola)
- segmentation.py (variance-based mask)
- ridge_enhancement.py (orientation, Gabor)
- skeletonization.py (Zhang-Suen)
- feature_extractor.py (pattern, ridge count, core/delta, minutiae, density, orientation stability)
- `fingerprint_features` table + migration 003

### Sprint 2 — Rule-Based Scoring (2 weeks)
- scoring_config.py (weights per category)
- categories: multiple_intelligence, disc_personality, brain_dominance, learning_style, quotients, love_language
- recommendation_engine.py
- indonesian_content.py (text templates)
- `report_scores` + `recommendations` tables + migration 004

### Sprint 3 — Indonesian PDF (1 week)
- IndonesianPDFGenerator (Jinja2 + WeasyPrint or ReportLab)
- visualizations.py (radar/bar charts via matplotlib)
- All 11 report sections, disclaimer

### Sprint 4 — Camera UX (1 week, mobile)
- quality_analyzer.dart (on-device pre-check)
- QualityRingOverlay, ZoomControl, FocusIndicator, LightingFeedback
- Auto-capture when quality ≥ threshold for N frames

### Sprint 5 — Review & Approval Workflow (1 week)
- `/sessions/{id}/submit`, `/sessions/{id}/approve`, `/sessions/{id}/reject`, `/sessions/{id}/request-rescan`
- Mobile: Review menu (Admin only), Review Detail screen, decision UI
- Status transitions enforced by service layer

### Sprint 6 — Dashboard & Report History (0.5 week)
- Backend `/dashboard/stats` (counts per status)
- Mobile Dashboard screen with KPI tiles
- Report History list + detail + download

> Admin Dashboard (Next.js) is **deferred** — not in workflow MVP. Mobile-first only.

---

## 5. Critical Schema Changes Needed

### `users` table
```sql
ALTER TABLE users DROP COLUMN is_admin;
ALTER TABLE users ADD COLUMN role VARCHAR(16) NOT NULL DEFAULT 'staff';
-- back-fill: UPDATE users SET role = 'admin' WHERE is_admin = TRUE;
```

### `scan_sessions` table
```sql
ALTER TABLE scan_sessions
  ADD COLUMN participant_name VARCHAR(120) NOT NULL,
  ADD COLUMN participant_age  INTEGER       NOT NULL,
  ADD COLUMN participant_gender VARCHAR(16),
  ADD COLUMN notes TEXT,
  ADD COLUMN reviewed_by_id INTEGER REFERENCES users(id),
  ADD COLUMN reviewed_at TIMESTAMP,
  ADD COLUMN rejection_reason TEXT,
  ADD COLUMN submitted_at TIMESTAMP,
  ADD COLUMN approved_at TIMESTAMP;
-- change status enum (drop + recreate or use VARCHAR with check)
```

### New table: `fingerprint_features` (Sprint 1)
See migration 003.

### New tables: `report_scores`, `recommendations` (Sprint 2)
See migration 004.

---

## 6. Order of Execution (build mode)

1. **NOW:** Sprint 0 — schema + RBAC (this PR)
2. Sprint 1 — image processing
3. Sprint 2 — scoring
4. Sprint 3 — PDF
5. Sprint 5 — workflow endpoints (camera UX can run in parallel)
6. Sprint 4 — mobile camera
7. Sprint 6 — dashboard polish

---

## 7. Acceptance Criteria (from workflow §11)

### Admin
- [ ] Login as admin works
- [ ] Can register staff users
- [ ] Can create participant session with auto timestamp
- [ ] Can scan 10 fingers
- [ ] Can preview, approve/reject/rescan
- [ ] Can generate report after approval
- [ ] Can view + download PDF

### Staff
- [ ] Login as staff works
- [ ] Cannot see Review menu / cannot approve
- [ ] Can create session, scan, submit
- [ ] Can view generated report history

---

## 8. Files Reference

- `FR_PROGRESS_ASSESSMENT.md` — gap analysis (still valid)
- `DEVELOPMENT_CONTINUATION_PLAN.md` — old 9-week plan (superseded by this doc for role/workflow scope; sprint code content still valid)
- `SPRINT_1_IMPLEMENTATION.md` — concrete code for image pipeline (unchanged)
- `NEXT_STEPS.md` — quick-start guide (rewritten below)
- `FPA_PRD_WORKFLOW.md` — source of truth for roles + lifecycle

---

**Next action:** Execute Sprint 0 — implement schema + RBAC changes now.
