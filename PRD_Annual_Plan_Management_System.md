# Product Requirements Document (PRD)
# Annual Plan Management System (نظام إدارة الخطة السنوية)

**Version:** 1.0  
**Date:** May 19, 2026  
**Status:** Draft  
**Author:** Senior Software Engineer  
**Reviewed By:** TBD  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Objectives & Goals](#3-objectives--goals)
4. [Scope](#4-scope)
5. [Stakeholders & User Roles](#5-stakeholders--user-roles)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Architecture](#8-system-architecture)
9. [Database Design (MySQL)](#9-database-design-mysql)
10. [API Specification](#10-api-specification)
11. [UI/UX Requirements](#11-uiux-requirements)
12. [Technology Stack](#12-technology-stack)
13. [Project Structure (Django)](#13-project-structure-django)
14. [Security Requirements](#14-security-requirements)
15. [Deployment & DevOps](#15-deployment--devops)
16. [Testing Strategy](#16-testing-strategy)
17. [Glossary](#17-glossary)

---

## 1. Executive Summary

The **Annual Plan Management System** is a web-based platform built with **Django** (backend + frontend via templates) and **MySQL** as the data store. It digitizes and centralizes the annual planning lifecycle for organizations — from SWOT analysis through goal definition, execution tracking, timeline visualization, risk management, and final recommendations. The system replaces manual Excel/Word workflows with a structured, role-aware, auditable digital process aligned with the **SMART** goal framework and **KPI**-driven performance management.

---

## 2. Problem Statement

Organizations currently manage annual plans through disconnected Excel workbooks and Word templates (as evidenced in the source files: `برنامج الخطة السنوية.xlsx` and `نموذج خطة سنوية.docx`). This approach creates:

| Problem | Impact |
|---|---|
| No centralized data store | Duplicate, conflicting plan versions |
| Manual completion tracking | Inaccurate progress percentages |
| No role-based access | Unauthorized edits to submitted plans |
| No automated timeline Gantt | Manual color-coding per month |
| No risk escalation workflow | Risks never formally tracked |
| No submission/approval audit trail | No accountability chain |
| No cross-formation reporting | Cannot compare performance across units |

---

## 3. Objectives & Goals

### Primary Objectives
1. Provide a **single source of truth** for annual plans across all formations (هيأة / قسم / شعبة / وحدة).
2. Enforce the **SMART** goal methodology for every created objective.
3. Automate **KPI calculations** and completion percentages.
4. Generate a **visual annual Gantt timeline** per plan (Q1–Q4).
5. Implement a formal **submission → review → approval** workflow.
6. Enable **risk logging** with probability/impact classification.
7. Support **Arabic RTL** interface.

### SMART Alignment
- **Specific:** Each goal has a code, title, type, and KPI.
- **Measurable:** KPI types are pre-defined from a controlled dropdown.
- **Achievable:** Resource allocation tracked per activity.
- **Relevant:** Goal types mapped to organizational domains.
- **Time-bound:** Start/End dates with auto-calculated duration.

---

## 4. Scope

### In Scope
- User authentication and role management
- Formation/Unit hierarchy management
- Annual plan CRUD with all 7 sections
- Automated calculation engine (completion %, duration, goal status)
- Gantt timeline rendering
- Plan submission, review, and approval workflow
- Dashboard with cross-formation analytics
- Export to PDF
- Arabic RTL support
- Audit log

### Out of Scope (v1.0)
- Mobile native applications (iOS/Android)
- Integration with ERP/HR systems
- Multi-year plan comparison
- AI-based plan suggestions
- Email/SMS notification engine (deferred to v1.1)

---

## 5. Stakeholders & User Roles

### 5.1 Stakeholder Map

| Stakeholder | Interest |
|---|---|
| Formation Manager (مدير التشكيل) | Creates, submits, monitors plans |
| Plan Organizer (منظم الاستمارة) | Drafts and edits plan details |
| Section Head (رئيس القسم) | Reviews plans of sub-units |
| System Administrator | Manages users, lookups, formations |
| Executive Management | Views company-wide performance dashboards |

### 5.2 User Roles & Permissions

| Role | Create Plan | Edit Plan | Submit Plan | Review/Approve | Manage Users | View Dashboard |
|---|---|---|---|---|---|---|
| `ADMIN` | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| `MANAGER` | ✔ | ✔ (own) | ✔ | ✔ (subordinate) | ✘ | ✔ (own unit) |
| `ORGANIZER` | ✔ (assigned) | ✔ (assigned) | ✘ | ✘ | ✘ | ✔ (own unit) |
| `REVIEWER` | ✘ | ✘ | ✘ | ✔ | ✘ | ✔ |
| `VIEWER` | ✘ | ✘ | ✘ | ✘ | ✘ | ✔ |

---

## 6. Functional Requirements

### 6.1 Authentication Module (FR-AUTH)

| ID | Requirement |
|---|---|
| FR-AUTH-01 | System shall provide login with username/password |
| FR-AUTH-02 | Passwords shall be hashed using PBKDF2/bcrypt |
| FR-AUTH-03 | Session shall expire after 30 minutes of inactivity |
| FR-AUTH-04 | Admin can create, deactivate, reset password for users |
| FR-AUTH-05 | System shall log all login/logout events with timestamp and IP |

---

### 6.2 Formation Management Module (FR-FORM)

| ID | Requirement |
|---|---|
| FR-FORM-01 | Admin shall manage a hierarchical tree of formations (Company → Board → Division → Section → Unit) |
| FR-FORM-02 | Each formation has a unique code and name (Arabic) |
| FR-FORM-03 | A formation can be active or archived |
| FR-FORM-04 | A user is assigned to exactly one formation but can view sub-formation plans |

---

### 6.3 Annual Plan Module (FR-PLAN)

#### 6.3.1 Plan Header

| ID | Requirement |
|---|---|
| FR-PLAN-01 | Plan is created per formation per year |
| FR-PLAN-02 | Only one active plan per formation per year is allowed |
| FR-PLAN-03 | Plan header captures: Formation (dropdown), Manager Name, Organizer Name, Endorsement text, Date |
| FR-PLAN-04 | Plan has statuses: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED` |
| FR-PLAN-05 | Plan year defaults to current year but can be set for future year |

#### 6.3.2 Section 1: SWOT Analysis (FR-SWOT)

| ID | Requirement |
|---|---|
| FR-SWOT-01 | Plan shall have exactly one SWOT record |
| FR-SWOT-02 | Each quadrant (Strengths, Weaknesses, Opportunities, Threats) accepts rich text/multi-line input |
| FR-SWOT-03 | SWOT is editable while plan is in `DRAFT` status |

#### 6.3.3 Section 2: Annual Goals — SMART (FR-GOAL)

| ID | Requirement |
|---|---|
| FR-GOAL-01 | A plan can have 1 to N main goals |
| FR-GOAL-02 | Each goal has: Code (auto-generated), Title, KPI Type (dropdown), Goal Type (dropdown) |
| FR-GOAL-03 | Goal code auto-increments as (1), (2), (3)… within the plan |
| FR-GOAL-04 | KPI Type dropdown values: ب/ي, مقمق/ي, نسبة الإنجاز, نسبة تنفيذ الخطة, عدد المشاريع المنجزة, عدد الأنشطة المنفذة, نسبة الالتزام بالجدول الزمني, نسبة التحول الرقمي, نسبة جودة الأداء, عدد المبادرات, مستوى رضا المستفيدين, نسبة تنفيذ الخطة الاستثمارية, عدد الأنظمة الإلكترونية, نسبة تحسين الأداء, أخرى |
| FR-GOAL-05 | Goal Type dropdown values: استراتيجي, استثماري, تشغيلي, مختبرية, صيانة, سلامة, مشروع, جودة, تحول رقمي, مالي, تطويري, زيادة انتاج, رقابي, قانوني, أخرى |

#### 6.3.4 Section 3: Execution Plan — Activities (FR-ACT)

| ID | Requirement |
|---|---|
| FR-ACT-01 | Each main goal has one or more activities (tasks) |
| FR-ACT-02 | Activity code format: `{goal_code} ─ {sequence}` e.g. `1 ─ 1`, `1 ─ 2` |
| FR-ACT-03 | Activity fields: Code (auto), Name, Responsible Formation (dropdown — all formations), Required Resources, Start Date, End Date, Planned Completion %, Actual Completion % |
| FR-ACT-04 | Duration in days = End Date - Start Date (calculated automatically) |
| FR-ACT-05 | Planned Completion % and Actual Completion % accept integer values 0–100 |
| FR-ACT-06 | Actual Completion % is editable after plan approval (progress updates) |

#### 6.3.5 Section 4: Goals Status Summary (FR-SUMM)

| ID | Requirement |
|---|---|
| FR-SUMM-01 | Summary is auto-calculated; no manual entry |
| FR-SUMM-02 | For each goal: Total Activities, Completed, In-Progress, Rolled-Over, Not-Completed are computed from activity statuses |
| FR-SUMM-03 | Goal Completion % = (Completed Activities / Total Activities) × 100 |
| FR-SUMM-04 | Goal Status is derived: 100% → مكتمل; 1–99% → قيد الإنجاز; 0% not started → لم يبدأ; past end date with <100% → متأخر |
| FR-SUMM-05 | Summary refreshes on every activity update |

#### 6.3.6 Section 5: Annual Gantt Timeline (FR-GANTT)

| ID | Requirement |
|---|---|
| FR-GANTT-01 | System renders a 12-month Gantt chart (ك2, شباط, آذار … ك1) grouped by quarter |
| FR-GANTT-02 | Each activity row is colored based on its date range |
| FR-GANTT-03 | Color coding: Planned (blue), In Progress (yellow), Completed (green), Delayed (red) |
| FR-GANTT-04 | Gantt is read-only and updates automatically when activity dates change |

#### 6.3.7 Section 6: Risk Management (FR-RISK)

| ID | Requirement |
|---|---|
| FR-RISK-01 | Plan can have multiple risk records |
| FR-RISK-02 | Risk fields: Potential Risk description, Probability (منخفض / متوسط / عالي), Impact description, Alternative Treatment Plan |
| FR-RISK-03 | Risk matrix visualization is displayed (probability vs. impact 3×3 grid) |

#### 6.3.8 Section 7: Final Recommendations (FR-REC)

| ID | Requirement |
|---|---|
| FR-REC-01 | Plan has one free-text Recommendations field |
| FR-REC-02 | Recommendations are editable only while plan is in DRAFT or UNDER_REVIEW |

---

### 6.4 Workflow & Submission (FR-WF)

| ID | Requirement |
|---|---|
| FR-WF-01 | Submit Plan button is available only when plan status = `DRAFT` |
| FR-WF-02 | On submission, status changes to `SUBMITTED` and a timestamp is recorded |
| FR-WF-03 | Reviewer can approve (→ `APPROVED`) or reject (→ `REJECTED`) with mandatory comment |
| FR-WF-04 | Rejected plan returns to `DRAFT` for the organizer to correct |
| FR-WF-05 | Approved plans are locked; only Actual Completion % of activities is editable |
| FR-WF-06 | Every status transition is logged in the audit table |

---

### 6.5 Dashboard & Reporting (FR-DASH)

| ID | Requirement |
|---|---|
| FR-DASH-01 | Manager dashboard shows: active plan status, goal completion %, overdue activities count |
| FR-DASH-02 | Admin dashboard shows: all formations' plan submission status, average completion % |
| FR-DASH-03 | Risk matrix heatmap across all plans |
| FR-DASH-04 | PDF export of full plan |
| FR-DASH-05 | Filters: Year, Formation, Goal Type, Status |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| ID | Requirement |
|---|---|
| NFR-PERF-01 | Page load time < 2 seconds for plan view under 50 concurrent users |
| NFR-PERF-02 | Dashboard aggregation queries must complete in < 3 seconds |
| NFR-PERF-03 | PDF export must complete within 10 seconds |

### 7.2 Scalability

| ID | Requirement |
|---|---|
| NFR-SCALE-01 | System shall support up to 500 formations |
| NFR-SCALE-02 | System shall support up to 1,000 registered users |
| NFR-SCALE-03 | Each plan can have up to 50 goals and 200 activities |

### 7.3 Availability

| ID | Requirement |
|---|---|
| NFR-AVAIL-01 | System uptime ≥ 99.5% during business hours (8AM–6PM) |
| NFR-AVAIL-02 | Scheduled maintenance window: Fridays 12AM–4AM |

### 7.4 Security

| ID | Requirement |
|---|---|
| NFR-SEC-01 | All data transmitted over HTTPS (TLS 1.2+) |
| NFR-SEC-02 | CSRF protection on all POST/PUT/DELETE endpoints |
| NFR-SEC-03 | SQL injection prevention via Django ORM parameterized queries |
| NFR-SEC-04 | XSS prevention via Django template auto-escaping |
| NFR-SEC-05 | Role-based access enforced at view and model level |
| NFR-SEC-06 | Sensitive data (passwords) never stored in plain text |
| NFR-SEC-07 | Audit trail of all data mutations |

### 7.5 Usability

| ID | Requirement |
|---|---|
| NFR-USE-01 | Full Arabic (RTL) UI support |
| NFR-USE-02 | Responsive design — works on desktop and tablet |
| NFR-USE-03 | Browser support: Chrome 110+, Edge 110+, Firefox 115+ |

### 7.6 Maintainability

| ID | Requirement |
|---|---|
| NFR-MAINT-01 | Code coverage ≥ 80% for business logic |
| NFR-MAINT-02 | All Django models have verbose Arabic labels for admin interface |
| NFR-MAINT-03 | Configuration via environment variables (.env), no hardcoded secrets |

---

## 8. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│              (Django Templates + Bootstrap 5 RTL)               │
│              (AJAX calls via Fetch API / HTMX)                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────────────────────────┐
│                        NGINX (Reverse Proxy)                     │
│                    Static files served here                      │
└────────────┬─────────────────────────────────────┬──────────────┘
             │ WSGI / Gunicorn                      │ Static/Media
┌────────────▼────────────────────┐    ┌────────────▼─────────────┐
│         DJANGO APPLICATION       │    │      Static File Storage  │
│  ┌──────────────────────────┐   │    │   (WhiteNoise / S3 CDN)   │
│  │  accounts app            │   │    └──────────────────────────┘
│  │  formations app          │   │
│  │  plans app               │   │
│  │    ├─ swot               │   │
│  │    ├─ goals              │   │
│  │    ├─ activities         │   │
│  │    ├─ summary            │   │
│  │    ├─ gantt              │   │
│  │    ├─ risks              │   │
│  │    └─ recommendations    │   │
│  │  workflow app            │   │
│  │  dashboard app           │   │
│  │  reports app             │   │
│  └──────────────────────────┘   │
│         Django ORM               │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│         MySQL 8.x DATABASE       │
│   (annual_plan_db schema)        │
└─────────────────────────────────┘
```

### Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend rendering | Django Templates + HTMX | Avoids SPA complexity; Arabic RTL easier with server-side HTML |
| CSS Framework | Bootstrap 5 with RTL | Built-in RTL support, widely known |
| Gantt rendering | Chart.js or custom HTML/CSS grid | Lightweight, no heavy BI library needed |
| PDF generation | WeasyPrint | Best Arabic text support in Python |
| Authentication | Django built-in auth + session | Proven, simple, sufficient for requirements |
| Task queue | Celery + Redis (v1.1) | Deferred; needed for PDF email delivery in future |

---

## 9. Database Design (MySQL)

### 9.1 Entity Relationship Overview

```
users ─────────────────── formations
  │                           │
  │                      annual_plans
  │                           │
  │              ┌────────────┼──────────────┐
  │              │            │              │
  │           swot_analyses  goals          risks
  │                           │
  │                       activities
  │                           │
  │                    plan_workflow_logs
  └──────────────────────── audit_logs
```

### 9.2 Table Definitions

#### `formations`
```sql
CREATE TABLE formations (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code            VARCHAR(20)  NOT NULL UNIQUE COMMENT 'Formation unique code',
    name_ar         VARCHAR(200) NOT NULL COMMENT 'Arabic name',
    parent_id       INT UNSIGNED NULL REFERENCES formations(id),
    level           ENUM('COMPANY','BOARD','DIVISION','SECTION','UNIT') NOT NULL,
    is_active       TINYINT(1) NOT NULL DEFAULT 1,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent (parent_id),
    INDEX idx_level  (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `users` (extends Django auth_user)
```sql
CREATE TABLE user_profiles (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    formation_id    INT UNSIGNED NOT NULL REFERENCES formations(id),
    role            ENUM('ADMIN','MANAGER','ORGANIZER','REVIEWER','VIEWER') NOT NULL DEFAULT 'ORGANIZER',
    full_name_ar    VARCHAR(200) NOT NULL COMMENT 'Arabic full name',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_formation (formation_id),
    INDEX idx_role      (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `annual_plans`
```sql
CREATE TABLE annual_plans (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    formation_id        INT UNSIGNED NOT NULL REFERENCES formations(id),
    plan_year           YEAR NOT NULL,
    manager_name        VARCHAR(200) NOT NULL COMMENT 'اسم مدير التشكيل',
    organizer_name      VARCHAR(200) NOT NULL COMMENT 'اسم منظم الاستمارة',
    endorsement_text    TEXT NULL COMMENT 'نص المصادقة',
    endorsement_date    DATE NULL,
    endorsement_ref_no  VARCHAR(50) NULL COMMENT 'رقم الإشارة',
    status              ENUM('DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED','ARCHIVED')
                        NOT NULL DEFAULT 'DRAFT',
    recommendations     TEXT NULL COMMENT 'سابعاً - التوصيات النهائية',
    created_by_id       INT NOT NULL REFERENCES auth_user(id),
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    submitted_at        DATETIME NULL,
    approved_at         DATETIME NULL,
    UNIQUE KEY uq_formation_year (formation_id, plan_year),
    INDEX idx_status (status),
    INDEX idx_year   (plan_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `swot_analyses`
```sql
CREATE TABLE swot_analyses (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plan_id     INT UNSIGNED NOT NULL UNIQUE REFERENCES annual_plans(id) ON DELETE CASCADE,
    strengths   TEXT NULL COMMENT 'نقاط القوة',
    weaknesses  TEXT NULL COMMENT 'نقاط الضعف',
    opportunities TEXT NULL COMMENT 'الفرص',
    threats     TEXT NULL COMMENT 'التهديدات',
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `goals`
```sql
CREATE TABLE goals (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plan_id         INT UNSIGNED NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    sequence        TINYINT UNSIGNED NOT NULL COMMENT 'Order: 1,2,3... used in code',
    code            VARCHAR(20) NOT NULL COMMENT 'Auto e.g. (1), (2)',
    title           TEXT NOT NULL COMMENT 'الهدف الرئيسي',
    kpi_type        VARCHAR(100) NOT NULL COMMENT 'مؤشر الأداء KPI',
    goal_type       VARCHAR(50)  NOT NULL COMMENT 'نوع الهدف',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_plan_seq (plan_id, sequence),
    INDEX idx_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `activities`
```sql
CREATE TABLE activities (
    id                      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    goal_id                 INT UNSIGNED NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    sequence                TINYINT UNSIGNED NOT NULL COMMENT 'Order within goal: 1,2,3…',
    code                    VARCHAR(20) NOT NULL COMMENT 'e.g. 1-1, 1-2',
    title                   TEXT NOT NULL COMMENT 'المهمة / النشاط',
    responsible_formation_id INT UNSIGNED NULL REFERENCES formations(id),
    required_resources      TEXT NULL COMMENT 'الموارد المطلوبة',
    start_date              DATE NOT NULL,
    end_date                DATE NOT NULL,
    duration_days           SMALLINT UNSIGNED GENERATED ALWAYS AS
                            (DATEDIFF(end_date, start_date)) VIRTUAL,
    planned_completion_pct  TINYINT UNSIGNED NOT NULL DEFAULT 0
                            COMMENT 'نسبة الانجاز المخطط (%)',
    actual_completion_pct   TINYINT UNSIGNED NOT NULL DEFAULT 0
                            COMMENT 'نسبة الانجاز المتحقق (%)',
    activity_status         ENUM('NOT_STARTED','IN_PROGRESS','COMPLETED','DELAYED','ROLLED_OVER','STOPPED')
                            NOT NULL DEFAULT 'NOT_STARTED',
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_goal_seq (goal_id, sequence),
    INDEX idx_goal      (goal_id),
    INDEX idx_status    (activity_status),
    INDEX idx_dates     (start_date, end_date),
    CONSTRAINT chk_dates CHECK (end_date >= start_date),
    CONSTRAINT chk_planned_pct CHECK (planned_completion_pct BETWEEN 0 AND 100),
    CONSTRAINT chk_actual_pct  CHECK (actual_completion_pct  BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `risks`
```sql
CREATE TABLE risks (
    id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plan_id             INT UNSIGNED NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    risk_description    TEXT NOT NULL COMMENT 'الخطر المحتمل',
    probability         ENUM('LOW','MEDIUM','HIGH') NOT NULL COMMENT 'احتمالية الحدوث',
    impact_description  TEXT NOT NULL COMMENT 'التأثير',
    treatment_plan      TEXT NOT NULL COMMENT 'خطة المعالجة البديلة',
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plan (plan_id),
    INDEX idx_prob (probability)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `plan_workflow_logs`
```sql
CREATE TABLE plan_workflow_logs (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    plan_id         INT UNSIGNED NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    from_status     ENUM('DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED','ARCHIVED') NULL,
    to_status       ENUM('DRAFT','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED','ARCHIVED') NOT NULL,
    performed_by_id INT NOT NULL REFERENCES auth_user(id),
    comment         TEXT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `audit_logs`
```sql
CREATE TABLE audit_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES auth_user(id),
    action          VARCHAR(50) NOT NULL COMMENT 'CREATE|UPDATE|DELETE|LOGIN|LOGOUT|EXPORT',
    model_name      VARCHAR(100) NOT NULL,
    object_id       INT UNSIGNED NULL,
    object_repr     VARCHAR(500) NULL,
    changes_json    JSON NULL COMMENT 'Before/after values',
    ip_address      VARCHAR(45) NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user      (user_id),
    INDEX idx_model     (model_name, object_id),
    INDEX idx_created   (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### `lookup_values` (Controlled Dropdown Lists)
```sql
CREATE TABLE lookup_values (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category    VARCHAR(50) NOT NULL COMMENT 'KPI_TYPE | GOAL_TYPE | PROBABILITY',
    code        VARCHAR(50) NOT NULL,
    label_ar    VARCHAR(200) NOT NULL,
    sort_order  TINYINT UNSIGNED NOT NULL DEFAULT 0,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    UNIQUE KEY uq_cat_code (category, code),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 10. API Specification

> The system uses Django's URL routing with HTML views for main pages and JSON endpoints for AJAX/HTMX interactions.

### 10.1 URL Patterns Summary

```
/                           → redirect to dashboard
/auth/login/                → Login page
/auth/logout/               → Logout
/auth/password-change/      → Password change

/formations/                → Formation list (ADMIN)
/formations/create/         → Create formation
/formations/<id>/edit/      → Edit formation

/plans/                     → My formation's plans list
/plans/create/              → Create new plan
/plans/<id>/                → Plan detail (all sections tabbed)
/plans/<id>/edit/           → Edit plan header
/plans/<id>/submit/         → Submit plan [POST]
/plans/<id>/approve/        → Approve plan [POST] (REVIEWER/MANAGER)
/plans/<id>/reject/         → Reject plan [POST] (REVIEWER/MANAGER)

/plans/<id>/swot/edit/      → Edit SWOT section
/plans/<id>/goals/          → Goals list for plan
/plans/<id>/goals/create/   → Create goal [POST]
/plans/<id>/goals/<gid>/edit/    → Edit goal
/plans/<id>/goals/<gid>/delete/  → Delete goal

/plans/<id>/goals/<gid>/activities/create/      → Create activity [POST]
/plans/<id>/goals/<gid>/activities/<aid>/edit/  → Edit activity
/plans/<id>/goals/<gid>/activities/<aid>/update-progress/ → Update actual % [PATCH]

/plans/<id>/risks/create/   → Add risk
/plans/<id>/risks/<rid>/edit/    → Edit risk
/plans/<id>/risks/<rid>/delete/  → Delete risk

/plans/<id>/gantt/          → Gantt timeline view (read-only)
/plans/<id>/summary/        → Goals status summary (auto-computed)
/plans/<id>/export/pdf/     → Export plan to PDF

/dashboard/                 → Role-aware dashboard
/dashboard/admin/           → Admin overview
/reports/formations/        → Cross-formation report
```

### 10.2 Key AJAX Endpoints (JSON)

| Method | URL | Description |
|---|---|---|
| GET | `/api/plans/<id>/summary/` | Returns JSON summary of goals + completion stats |
| PATCH | `/api/activities/<id>/progress/` | Updates `actual_completion_pct` |
| GET | `/api/plans/<id>/gantt-data/` | Returns JSON data for Gantt chart |
| GET | `/api/formations/tree/` | Returns formation hierarchy as JSON tree |

---

## 11. UI/UX Requirements

### 11.1 General Layout

- **Direction:** RTL (right-to-left) throughout
- **Language:** Arabic primary; system messages in Arabic
- **Navigation:** Sidebar with collapsible sections
- **Branding:** Configurable logo and system title in settings

### 11.2 Plan Form — Tab Structure

```
┌──────────────────────────────────────────────────────────────┐
│  [رأس الخطة]  [SWOT]  [الأهداف]  [الأنشطة]  [الملخص]  [Gantt]  [المخاطر]  [التوصيات]  │
└──────────────────────────────────────────────────────────────┘
```

Each section is a separate tab. Changes auto-save on blur (HTMX PATCH requests).

### 11.3 Gantt Chart Columns

| Month (Arabic) | Month (Gregorian) | Quarter |
|---|---|---|
| كانون الثاني (ك2) | January | Q1 |
| شباط | February | Q1 |
| آذار | March | Q1 |
| نيسان | April | Q2 |
| أيار | May | Q2 |
| حزيران | June | Q2 |
| تموز | July | Q3 |
| آب | August | Q3 |
| أيلول | September | Q3 |
| تشرين الأول (ت1) | October | Q4 |
| تشرين الثاني (ت2) | November | Q4 |
| كانون الأول (ك1) | December | Q4 |

### 11.4 Goal Status Color Coding

| Status | Arabic | Color |
|---|---|---|
| `COMPLETED` | مكتمل (100%) | Green `#28a745` |
| `IN_PROGRESS` | قيد الإنجاز | Yellow `#ffc107` |
| `DELAYED` | متأخر | Red `#dc3545` |
| `STOPPED` | متوقف | Grey `#6c757d` |
| `NOT_STARTED` | لم يبدأ | Light grey `#e9ecef` |
| `ROLLED_OVER` | تم ترحيله | Orange `#fd7e14` |

---

## 12. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Backend framework | Django | 5.x | MVC web framework |
| Database | MySQL | 8.x | Relational data store |
| ORM | Django ORM | built-in | Database abstraction |
| Frontend templates | Django Templates + Jinja2 | built-in | Server-side HTML rendering |
| CSS framework | Bootstrap 5 RTL | 5.3.x | Responsive RTL styling |
| AJAX/Interactivity | HTMX | 1.9.x | Partial page updates without full SPA |
| Charts/Gantt | Chart.js | 4.x | Goal completion charts |
| PDF Export | WeasyPrint | 60.x | Arabic-aware PDF generation |
| Web server | Gunicorn + Nginx | latest | WSGI server + reverse proxy |
| DB driver | mysqlclient | 2.x | MySQL Python connector |
| Environment config | python-decouple | 3.x | `.env` variable management |
| Form validation | Django Forms + crispy-forms | built-in / 2.x | Form rendering and validation |
| Testing | pytest-django | 4.x | Test runner |
| Code quality | flake8, black | latest | Linting and formatting |

---

## 13. Project Structure (Django)

```
annual_plan_system/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                         # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py                 # Common settings
│   │   ├── development.py          # Dev overrides
│   │   └── production.py           # Prod overrides
│   ├── urls.py                     # Root URL config
│   └── wsgi.py
│
├── apps/
│   ├── accounts/                   # User auth & profiles
│   │   ├── models.py               # UserProfile
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/accounts/
│   │
│   ├── formations/                 # Formation hierarchy
│   │   ├── models.py               # Formation
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── templates/formations/
│   │
│   ├── plans/                      # Core plan application
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── plan.py             # AnnualPlan
│   │   │   ├── swot.py             # SwotAnalysis
│   │   │   ├── goal.py             # Goal
│   │   │   ├── activity.py         # Activity
│   │   │   ├── risk.py             # Risk
│   │   │   └── workflow.py         # PlanWorkflowLog
│   │   ├── views/
│   │   │   ├── plan_views.py
│   │   │   ├── goal_views.py
│   │   │   ├── activity_views.py
│   │   │   ├── risk_views.py
│   │   │   ├── gantt_views.py
│   │   │   └── summary_views.py
│   │   ├── services/
│   │   │   ├── completion_service.py  # Calc goal/plan completion
│   │   │   ├── gantt_service.py       # Build gantt JSON
│   │   │   └── pdf_service.py         # PDF export logic
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templates/plans/
│   │       ├── plan_detail.html
│   │       ├── plan_form.html
│   │       ├── sections/
│   │       │   ├── swot.html
│   │       │   ├── goals.html
│   │       │   ├── activities.html
│   │       │   ├── summary.html
│   │       │   ├── gantt.html
│   │       │   ├── risks.html
│   │       │   └── recommendations.html
│   │       └── pdf/
│   │           └── plan_pdf.html
│   │
│   ├── dashboard/                  # Analytics & reporting
│   │   ├── views.py
│   │   └── templates/dashboard/
│   │
│   └── core/                       # Shared utilities
│       ├── models.py               # AuditLog, LookupValue
│       ├── mixins.py               # RoleRequiredMixin
│       ├── middleware.py           # Audit logging middleware
│       └── templatetags/
│           └── rtl_extras.py       # Arabic helper template tags
│
├── static/
│   ├── css/
│   │   └── custom-rtl.css
│   ├── js/
│   │   ├── gantt.js
│   │   └── plan-form.js
│   └── img/
│
└── templates/
    ├── base.html                   # Base template with Bootstrap RTL
    ├── navbar.html
    └── sidebar.html
```

---

## 14. Security Requirements

### 14.1 Authentication & Session
- Django's built-in PBKDF2-SHA256 password hashing
- `SESSION_COOKIE_SECURE = True` in production
- `SESSION_COOKIE_HTTPONLY = True`
- `CSRF_COOKIE_SECURE = True`
- Session timeout: 1800 seconds (30 minutes)

### 14.2 Authorization
- Every view decorated with `@login_required` + `RoleRequiredMixin`
- Object-level permission: users can only access plans of their formation (or sub-formations for Managers)
- Django admin restricted to `ADMIN` role only

### 14.3 Input Validation
- All form inputs validated via Django Forms (whitelist approach)
- Date fields validated: `end_date >= start_date`
- Numeric fields: percentage values constrained to 0–100
- No direct SQL queries — all database access via Django ORM

### 14.4 OWASP Top 10 Mitigations

| OWASP Risk | Mitigation |
|---|---|
| A01 Broken Access Control | `RoleRequiredMixin` + queryset filtering per user |
| A02 Cryptographic Failures | HTTPS enforced, passwords hashed, no secrets in code |
| A03 Injection | Django ORM parameterized queries, no raw SQL |
| A04 Insecure Design | SWOT/risk/goal access blocked post-approval |
| A05 Security Misconfiguration | `DEBUG=False` in prod, `ALLOWED_HOSTS` set |
| A06 Vulnerable Components | `pip-audit` in CI pipeline |
| A07 Auth Failures | Rate limiting on login (django-axes), session timeout |
| A08 Data Integrity Failures | CSRF tokens on all state-changing forms |
| A09 Logging/Monitoring | Audit log table + Django logging to file |
| A10 SSRF | No user-supplied URLs fetched by server |

---

## 15. Deployment & DevOps

### 15.1 Environment Variables (.env)

```env
# Django
SECRET_KEY=<generated-secret>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=annual_plan_db
DB_USER=annual_plan_user
DB_PASSWORD=<strong-password>
DB_HOST=127.0.0.1
DB_PORT=3306

# Security
SESSION_COOKIE_AGE=1800
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### 15.2 MySQL Database Setup

```sql
CREATE DATABASE annual_plan_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER 'annual_plan_user'@'localhost'
    IDENTIFIED BY '<strong-password>';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
    ON annual_plan_db.*
    TO 'annual_plan_user'@'localhost';

FLUSH PRIVILEGES;
```

### 15.3 Django Settings (Database Config)

```python
# config/settings/base.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 15.4 Production Stack

```
[Client] ──HTTPS──► [Nginx :443]
                         │
                    [Gunicorn :8000]
                         │
                  [Django Application]
                         │
                    [MySQL :3306]
```

### 15.5 Initial Deployment Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd annual_plan_system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with actual values

# 5. Database migrations
python manage.py migrate

# 6. Load initial lookup data
python manage.py loaddata fixtures/lookups.json
python manage.py loaddata fixtures/formations.json

# 7. Create superuser
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --no-input

# 9. Run (development)
python manage.py runserver

# 10. Run (production)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 16. Testing Strategy

### 16.1 Test Categories

| Type | Tool | Coverage Target |
|---|---|---|
| Unit tests | pytest-django | Models, services, forms ≥ 80% |
| Integration tests | pytest-django | Views + DB queries |
| Workflow tests | pytest-django | Status transitions: DRAFT→APPROVED |
| Security tests | Manual / OWASP ZAP | Auth bypass, XSS, CSRF |
| Performance tests | Locust | 50 concurrent users |

### 16.2 Key Test Cases

| ID | Description |
|---|---|
| TC-01 | Create plan with all 7 sections and submit — verify status = SUBMITTED |
| TC-02 | Only formation's ORGANIZER can edit plan in DRAFT |
| TC-03 | Activity `actual_completion_pct` updates goal summary automatically |
| TC-04 | Duplicate plan (same formation + year) is rejected |
| TC-05 | Gantt data returns correct month coverage for activity date range |
| TC-06 | PDF export renders Arabic text correctly |
| TC-07 | Rejected plan reverts to DRAFT with reviewer comment visible |
| TC-08 | VIEWER role cannot access any edit URL (403 returned) |
| TC-09 | CSRF token missing on form POST returns 403 |
| TC-10 | end_date < start_date is rejected with validation error |

---

## 17. Glossary

| Term | Arabic | Definition |
|---|---|---|
| Annual Plan | الخطة السنوية | Organizational plan for one fiscal year |
| Formation | التشكيل | Organizational unit (board, division, section, unit) |
| SWOT | تحليل الوضع الحالي | Strengths, Weaknesses, Opportunities, Threats analysis |
| SMART Goal | هدف ذكي | Specific, Measurable, Achievable, Relevant, Time-bound |
| KPI | مؤشر الأداء الرئيسي | Key Performance Indicator |
| Goal | الهدف الرئيسي | Main annual objective |
| Activity | النشاط / المهمة | Sub-task under a main goal |
| Gantt Chart | الجدول الزمني السنوي | Visual timeline of activities across months |
| Endorsement | المصادقة | Official approval signature with reference number |
| Rolled Over | تم ترحيله | Activity/goal moved to next planning cycle |
| Completion % | نسبة الإنجاز | Ratio of completed activities to total |

---

*Document End — PRD v1.0*  
*This document is the single source of truth for development of the Annual Plan Management System.*  
*All changes must be version-controlled and reviewed before implementation.*
