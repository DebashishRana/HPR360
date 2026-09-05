<div align="center">

<img src="docs/assets/peoplepay360-logo.svg" alt="PeoplePay360 Logo" width="180"/>

# PeoplePay360

### HR & Payroll Operations Platform

**Connecting employee lifecycle, contracts, attendance, time off, payroll processing, payslips and operational analytics.**

<p>
  <img src="https://img.shields.io/badge/Status-Hackathon%20Build-blue?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/Platform-Frappe%20%2F%20ERPNext-red?style=for-the-badge" alt="Platform"/>
  <img src="https://img.shields.io/badge/Frontend-Vue-42b883?style=for-the-badge" alt="Vue"/>
  <img src="https://img.shields.io/badge/Database-PostgreSQL%2017-blue?style=for-the-badge" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Cache-Redis-red?style=for-the-badge" alt="Redis"/>
  <img src="https://img.shields.io/badge/Security-RBAC-orange?style=for-the-badge" alt="Security"/>
</p>

<p>
  <a href="#-overview">Overview</a> •
  <a href="#-problem">Problem</a> •
  <a href="#-solution">Solution</a> •
  <a href="#-implemented-features">Implemented</a> •
  <a href="#-planned-features">Planned</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-security">Security</a> •
  <a href="#-demo-flow">Demo</a>
</p>

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Problem](#-problem)
- [Solution](#-solution)
- [Implementation Status](#-implementation-status)
- [Implemented Features](#-implemented-features)
- [Planned Features](#-planned-features)
- [Core Workflow](#-core-workflow)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Data Model](#-data-model)
- [Security](#-security)
- [Performance & Scalability](#-performance--scalability)
- [Database Foundation](#-database-foundation)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Hackathon Demo Flow](#-hackathon-demo-flow)
- [Engineering Highlights](#-engineering-highlights)
- [Why This Architecture](#-why-this-architecture)
- [Roadmap](#-roadmap)
- [Team](#-team)
- [License](#-license)

---

# 📌 Overview

**PeoplePay360** is an integrated HR and Payroll operations platform designed to connect the employee lifecycle from HR master data through payroll processing and payslip delivery.

The system brings together:

```text
Employee
   ↓
Contract + Working Schedule
   ↓
Attendance + Time Off
   ↓
Salary Structure + Salary Rules
   ↓
Payrun
   ↓
Payslips
   ↓
Validation → Payment → PDF → Email
   ↓
Payroll Dashboard
```

The project is built on the **Frappe / ERPNext / Frappe HR ecosystem** and adds PeoplePay360-specific workflow and payroll experience on top of the existing platform.

The repository also contains an independent **PostgreSQL-based PeoplePay360 database foundation** for domain modeling, constraints, payroll integrity and future service-oriented integration.

---

# 🎯 Problem

HR and payroll data is operationally connected, but many systems expose these areas as disconnected modules.

This can create problems such as:

- Incorrect contract selection for a payroll period.
- Unresolved attendance exceptions.
- Difficult-to-audit leave balances.
- Non-transparent salary calculations.
- Accidental inclusion of employees in payroll.
- Missing payroll information discovered too late.
- Duplicate payslip generation.
- Historical payroll data being modified incorrectly.
- Unauthorized access to sensitive payroll information.

PeoplePay360 addresses these problems by connecting HR records and payroll decisions into a single workflow.

---

# 💡 Solution

PeoplePay360 focuses on **business continuity across HR and payroll**.

Instead of:

```text
Employee
Attendance
Leave
Contract
Salary
Payroll
```

being treated as unrelated modules, the platform connects them:

```text
Employee
   ├── Contract
   ├── Working Schedule
   ├── Attendance
   ├── Time Off
   └── Salary Assignment
          ↓
    Salary Structure
          ↓
       Payrun
          ↓
      Payslips
          ↓
   Payment / PDF / Email
          ↓
       Analytics
```

The primary product focus is:

- Payroll correctness.
- Period-aware employment context.
- Explicit employee selection.
- Payroll warnings.
- Salary calculation visibility.
- Role-based access.
- Historical integrity.
- Operational reporting.

---

# 🚦 Implementation Status

To keep this repository technically honest, features are divided into three categories.

| Status | Meaning |
|---|---|
| ✅ **Implemented** | Functionality currently present in this repository |
| 🟡 **Platform Foundation** | Functionality provided by Frappe/ERPNext and reused by PeoplePay360 |
| 🚧 **Planned** | Intended enhancement that should not be considered completed |

> **Important:** Planned features are deliberately separated from implemented functionality. The README should only describe a feature as implemented when it can be demonstrated or verified from the current codebase.

---

# ✅ Implemented Features

## 1. PeoplePay360 Application Branding

- PeoplePay360 application identity.
- PeoplePay360 navigation entry.
- PeoplePay360 payroll dashboard branding.
- Dedicated PeoplePay360 project documentation.

---

## 2. Two-Step Payrun Creation

A custom Payrun workflow is implemented on top of the Frappe Payroll Entry model.

### Step 1 — Scope & Period

The wizard supports:

- Company.
- Salary Structure.
- Posting Date.
- Payroll Frequency.
- Period Start.
- Period End.
- Department.
- Designation.
- Branch.
- Currency.
- Payroll Payable Account.
- Timesheet-based payroll option.

### Step 2 — Employee Selection

The system:

- Fetches eligible employees.
- Displays employee information.
- Displays applicable employment contract.
- Displays salary-withholding information.
- Supports Select All.
- Supports Deselect All.
- Displays selected/total employee count.
- Requires at least one employee before Payrun creation.

The Payrun is created only after employee selection.

---

## 3. Period-Aware Employee Eligibility

The Payrun employee selection logic checks the applicable employment contract for the selected payroll period.

The system can identify:

- Applicable employment contract.
- Salary structure eligibility.
- Employees without an applicable contract.
- Salary Structure Assignment fallback where contracts are not yet configured.

This reduces the risk of blindly processing every employee.

---

## 4. Payrun Processing Screen

A dedicated Payrun Processing page is implemented.

It provides:

- Payrun status.
- Employee count.
- Payslip count.
- Submitted payslip count.
- Bank-entry information.
- Missing bank-detail warnings.
- Duplicate payslip detection.
- Processing actions.
- Payslip delivery action.

The processing screen is directly accessible from Payroll.

---

## 5. Payroll Warning Detection

The current payroll implementation includes warning detection for areas such as:

- Missing bank details.
- Duplicate payslips.
- Unmarked attendance.
- Contract attention.
- Queued Payruns.
- Failed Payruns.

Warnings are surfaced through the Payrun Processing experience and Payroll Dashboard.

---

## 6. Payroll Dashboard

A PeoplePay360-branded payroll dashboard is implemented.

### Filters

- Company.
- Department.
- Employee Type.
- From Date.
- To Date.

### KPIs

- Total Net Salary.
- Payslips Generated.
- Average Salary.
- Approved Time Off.
- Pending Time Off.
- Active Employees.
- Attendance Health.

### Analytics

- Monthly Net Salary Trends.
- Salary Cost by Department.
- Department headcount.
- Attendance Overview.
- Time Off Overview.

### Operational Alerts

- Queued Payruns.
- Failed Payruns.
- Missing Bank Details.
- Duplicate Payslips.
- Contract Attention.
- Unmarked Attendance.

Dashboard values are retrieved from live Frappe HR/Payroll records through server-side queries.

---

## 7. Attendance Warning Infrastructure

The existing HRMS implementation provides attendance warning and exception functionality.

The repository includes support for identifying cases such as:

- Holiday conflicts.
- Leave conflicts.
- Attendance corrections.
- Missing/exception situations.

The payroll dashboard also surfaces attendance-related operational information.

---

## 8. Employment Contract Validation

The repository contains Employment Contract logic enforcing the rule:

> Only one active contract is allowed for a given period.

PeoplePay360's Payrun employee selection also uses the applicable contract for the selected payroll context.

---

## 9. Payslip Generation & Delivery

The existing payroll infrastructure provides:

- Salary Slip generation.
- Salary Slip processing.
- Salary calculation.
- Salary Slip submission.
- Payslip PDF/print infrastructure.
- Email delivery infrastructure.

PeoplePay360 adds a bulk Payrun delivery action that processes submitted payslips associated with the selected Payrun.

---

## 10. Existing HR & Payroll Modules

The repository already contains mature HR/payroll functionality including:

- Employee management.
- Employment contracts.
- Shift and attendance.
- Leave management.
- Salary structures.
- Salary components.
- Salary structure assignments.
- Payroll entries.
- Salary slips.
- Payroll reports.
- Payroll dashboards.
- Print formats.

These capabilities are reused rather than unnecessarily duplicated.

---

# 🟡 Platform Foundation

The following capabilities are available through the underlying Frappe/ERPNext/HRMS platform and form the foundation of PeoplePay360.

## HR Foundation

- Employee records.
- Employee lifecycle.
- Department relationships.
- User relationships.
- Employment contracts.
- Working schedules.
- Shift assignments.
- Employee check-ins.
- Attendance.
- Leave applications.
- Leave allocations.

## Payroll Foundation

- Salary Structures.
- Salary Components.
- Salary Structure Assignments.
- Payroll Entry.
- Salary Slip.
- Payroll Period.
- Payroll reports.
- Accounting integration.
- Payroll print formats.

## Platform Infrastructure

- Frappe ORM.
- Document lifecycle.
- Permissions.
- User/session management.
- Background jobs.
- Redis.
- Reporting.
- PDF rendering.
- Application hooks.
- Database migrations.

PeoplePay360 builds its custom experience around these existing primitives instead of maintaining parallel implementations.

---

# 🚧 Planned Features

The following features are **planned enhancements and are not represented as completed functionality**.

## 1. Automated Demo Seed

One-command creation of:

- Company.
- Departments.
- Employees.
- Contracts.
- Working schedules.
- Leave allocations.
- Salary structures.
- Sample payroll data.

---

## 2. Self-Service Mobile Polish

Further refinement of the Vue/Ionic PWA for:

- Attendance.
- Check-in/check-out.
- Time Off requests.
- Employee self-service.

Employees should not receive payroll administration capabilities.

---

## 3. Contract Amendment Workflow

Planned capabilities:

- Versioned contract amendments.
- Approval workflow.
- Effective dates.
- Automatic Salary Structure Assignment synchronization.
- Contract history visualization.

---

## 4. Advanced Payroll Validation

Future validation improvements include:

- Rule-level salary simulation.
- More detailed salary component validation.
- Advanced payroll readiness checks.
- Better warning severity classification.
- Pre-compute validation.

---

## 5. Advanced Salary Calculation Visibility

Planned improvements include:

- Basic salary totals.
- Allowance totals.
- Gross totals.
- Contribution totals.
- Deduction totals.
- Net totals.
- Calculation trace visualization.

---

## 6. Production Edge Security

Planned deployment architecture:

```text
Internet
   ↓
Cloudflare
   ↓
Nginx
   ↓
Application
   ↓
Database / Queue
```

Potential additions:

- Rate limiting.
- TLS termination.
- Security headers.
- Prometheus metrics.
- Grafana dashboards.
- Centralized observability.

---

## 7. Advanced Observability

Future improvements:

- Application metrics.
- Payroll processing metrics.
- Background-job monitoring.
- Database metrics.
- Request latency monitoring.
- Error-rate dashboards.

---

# 🔄 Core Workflow

## HR Setup

```text
Company
   ↓
Departments / Employee Types
   ↓
Working Schedule
   ↓
Time Off Types
   ↓
Salary Components
   ↓
Salary Structure
   ↓
Employees
   ↓
Contracts
   ↓
Salary Assignments
```

## Daily Operations

```text
Employee
   ↓
Check In / Check Out
   ↓
Attendance
   ↓
Exception Review

Employee
   ↓
Time Off Request
   ↓
Approval
   ↓
Leave Balance
```

## Payroll

```text
Payroll Period
      ↓
Payrun Wizard
      ↓
Scope & Period
      ↓
Eligible Employees
      ↓
Warnings
      ↓
Explicit Employee Selection
      ↓
Payrun Creation
      ↓
Salary Calculation
      ↓
Payslips
      ↓
Validation
      ↓
Payment
      ↓
PDF / Email
      ↓
Payroll Dashboard
```

---

# 🏗️ Architecture

PeoplePay360 uses an extension-oriented architecture.

```text
┌─────────────────────────────────────────────┐
│                  USERS                      │
│                                             │
│          Frappe Desk + Vue / PWA            │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              PeoplePay360                  │
│                                             │
│ Employee │ Contract │ Attendance │ Time Off │
│ Salary   │ Payrun   │ Payslip    │ Dashboard│
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             Frappe Framework               │
│                                             │
│ ORM │ Documents │ APIs │ Permissions        │
│ Jobs │ Reports │ Workflows │ PDF            │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                  ERPNext                    │
│                                             │
│ Company │ Accounting │ Payments │ Journals  │
└──────────────────────┬──────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       ┌────────────┐      ┌────────────┐
       │  MariaDB   │      │   Redis    │
       │ Frappe DB  │      │ Cache/Jobs │
       └────────────┘      └────────────┘
```

---

# 🗄️ PeoplePay360 PostgreSQL Foundation

The repository also contains an independent PostgreSQL domain foundation.

```text
PeoplePay360 Services
        ↓
    PgBouncer
        ↓
 PostgreSQL 17
        ↓
┌───────────────────────────────┐
│ identity                      │
│ organization                  │
│ workforce                     │
│ time                          │
│ leave                         │
│ compensation                  │
│ payroll                       │
│ audit                         │
│ analytics                     │
└───────────────────────────────┘
```

This database layer is currently a **separate foundation from the Frappe HRMS database**.

It should not be described as the database currently powering every Frappe HRMS operation.

---

# 🧱 Technology Stack

| Layer | Technology |
|---|---|
| HR Framework | Frappe Framework |
| ERP Foundation | ERPNext |
| HR & Payroll | Frappe HR / HRMS |
| Backend | Python |
| UI | Frappe Desk |
| Operational Frontend | Vue |
| PWA | Ionic / Vue |
| Frappe Database | MariaDB |
| PeoplePay360 Database Foundation | PostgreSQL 17 |
| Connection Pooling | PgBouncer |
| Cache / Queue | Redis |
| Runtime | Docker Compose |
| Development | Frappe Bench |
| CI/CD | GitHub Actions |
| Reporting | Frappe Reports / Dashboards |
| PDF | Frappe Print Formats |

---

# 🗃️ Data Model

## HRMS Domain

```text
Employee
│
├── Employment Contract
├── Working Schedule / Shift
├── Employee Checkin
├── Attendance
├── Leave Allocation
├── Leave Application
├── Salary Structure Assignment
└── Salary Slip
       └── Payroll Entry
```

## PostgreSQL Foundation

```text
identity
   ├── user
   ├── role
   ├── permission
   ├── user_role
   └── role_permission

organization
   ├── company
   ├── department
   └── job_position

workforce
   ├── employee
   ├── employment
   ├── contract
   ├── employee_reporting_line
   └── employee_event

time
   ├── working_schedule
   ├── schedule_day
   ├── schedule_assignment
   ├── attendance_event
   ├── attendance_day
   ├── attendance_exception
   └── attendance_correction

leave
   ├── leave_type
   ├── leave_policy
   ├── leave_allocation
   ├── leave_request
   └── leave_ledger_entry

compensation
   ├── salary_plan
   ├── salary_rule
   ├── salary_rule_dependency
   └── employee_salary_assignment

payroll
   ├── payroll_run
   ├── payroll_run_employee
   ├── payroll_validation
   ├── payroll_validation_result
   ├── idempotency_key
   ├── payroll_calculation_snapshot
   ├── payslip
   ├── payslip_input
   ├── payslip_line
   ├── payslip_calculation_trace
   ├── payroll_adjustment
   └── payroll_reversal

audit
   ├── audit_event
   ├── entity_revision
   └── system_operation
```

---

# 🔐 Security

Payroll information is highly sensitive.

PeoplePay360 follows a role-oriented security model.

| Role | Intended Access |
|---|---|
| **Employee** | Own HR, attendance and Time Off information |
| **HR Manager** | HR operations without payroll administration |
| **HR Payroll User** | HR operations + Payruns/Payslips |
| **HR Payroll Manager** | HR + payroll configuration |
| **Admin** | Complete administration |

## Security Principles

### Server-Side Authorization

Frontend visibility is not treated as a security boundary.

Sensitive operations must be protected at the server/API layer.

### Record-Level Access

Users should only access records permitted by their role and scope.

### Payroll Protection

Sensitive operations include:

- Salary configuration.
- Payslip access.
- Payroll processing.
- Payment operations.
- Salary rule modification.

### API Security

Changing an identifier in a URL or API request should not bypass authorization.

---

# ⚡ Performance & Scalability

## Redis

Redis provides the infrastructure for:

- Caching.
- Background queues.
- Realtime workloads.
- Expensive asynchronous processing.

## Background Jobs

Suitable asynchronous operations include:

```text
Bulk Payslip Generation
        ↓
Background Queue
        ↓
Worker
        ↓
PDF Generation
        ↓
Email Delivery
```

The goal is to prevent expensive operations from unnecessarily blocking interactive requests.

---

# 🐘 PostgreSQL + PgBouncer

The PostgreSQL foundation uses:

```text
Application
    ↓
PgBouncer :6432
    ↓
PostgreSQL :5432
```

The repository configures PgBouncer using **session pooling**.

Migrations intentionally connect directly to PostgreSQL.

This separation helps keep migration operations independent from pooled application traffic.

---

# 🔒 Database Integrity

The PostgreSQL foundation includes database-level safeguards.

## Contract Integrity

Active employment contracts use PostgreSQL exclusion constraints to prevent overlapping active periods for the same employee.

## Leave Ledger

Leave ledger records use append-only protection.

## Salary Rule Dependencies

Salary-rule dependency protection prevents invalid dependency cycles.

## Payslip Integrity

Payslip records have immutability protections after posting.

## Payroll Run Integrity

Payroll runs include state-transition and post-processing protections.

## Idempotency

The PostgreSQL foundation includes a dedicated idempotency-key model.

## Auditability

Dedicated audit structures are present for:

- Audit events.
- Entity revisions.
- System operations.

These constraints provide database-level protection rather than relying only on application code.

---

# 🔁 Payroll State Model

The product workflow is designed around explicit payroll states.

```text
Draft
  ↓
Computed
  ↓
Validation Required
  ↓
Validated
  ↓
Paid
  ↓
Sent
```

The underlying Frappe Payroll Entry lifecycle remains authoritative for the current HRMS implementation.

The PeoplePay360 presentation layer provides clearer Payrun terminology and processing visibility.

---

# 🧠 Engineering Principles

## Data Integrity

Payroll decisions should be based on authoritative server-side records.

## Security by Design

Authorization must exist independently of frontend visibility.

## Auditability

Historical payroll and employment records should remain traceable.

## Idempotency

Repeated payroll operations should not create unintended duplicate results.

## Separation of Concerns

PeoplePay360-specific functionality should remain separate from generic platform infrastructure.

## Reuse Before Rebuild

Mature HR, payroll, accounting and framework functionality should be reused wherever appropriate.

## Validate Before Finalization

Potential payroll issues should be surfaced before final payroll completion.

---

# 🧪 Testing

Testing is divided between the Frappe/HRMS application and the PostgreSQL foundation.

## Application Testing

The repository contains tests across HRMS modules including payroll and employee-related functionality.

Important payroll scenarios include:

- Payroll Entry processing.
- Salary Structure Assignment.
- Salary calculations.
- Salary Slip processing.
- Attendance.
- Leave.
- Employee workflows.

## PostgreSQL Foundation Tests

The database test suite explicitly validates constraints including:

- Foreign-key integrity.
- Empty date-range rejection.
- Overlapping active contracts.
- Leave ledger amount constraints.
- Append-only ledger behavior.
- Salary-rule dependency cycles.
- Invalid payroll periods.
- Duplicate payslips.

Example:

```text
Invalid Contract
       ↓
Database Constraint
       ↓
Rejected

Duplicate Payslip
       ↓
Unique Constraint
       ↓
Rejected
```

---

# 🔧 CI/CD

The repository contains GitHub Actions workflows for automated quality checks.

Current workflow infrastructure includes:

- Application tests.
- Patch testing.
- Documentation checks.
- Pull-request labeling.
- Coverage reporting.
- Release automation.

The CI environment also uses dependency caching and multiple supported runtime configurations where applicable.

---

# 📁 Project Structure

```text
HPR360-main/
│
├── .github/
│   └── workflows/
│
├── database/
│   ├── init/
│   ├── migrations/
│   ├── pgbouncer/
│   ├── scripts/
│   ├── tests/
│   └── docker-compose.yml
│
├── docker/
│   ├── docker-compose.yml
│   ├── init.sh
│   └── verify_peoplepay.sh
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── composables/
│       ├── router/
│       └── views/
│
├── roster/
│   └── src/
│
├── hrms/
│   ├── api/
│   ├── hr/
│   ├── leaves/
│   ├── payroll/
│   ├── recruitment/
│   ├── shift_and_attendance/
│   ├── tax_and_benefits/
│   ├── tenure/
│   ├── controllers/
│   ├── overrides/
│   └── hooks.py
│
├── PeoplePay360-ROADMAP.md
├── PeoplePay360 HR & Payroll.md
├── SECURITY.md
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Depending on which part of the repository you are working with:

- Git
- Docker
- Docker Compose
- Python
- Node.js
- Yarn
- Frappe Bench
- PostgreSQL 17
- `psql`

## Clone

```bash
git clone <repository-url>
cd HPR360-main
```

---

## Start Frappe/HRMS

Use the repository's configured Frappe Bench/Docker development environment.

```bash
docker compose up -d
```

Check services:

```bash
docker compose ps
```

Then use the configured Bench environment to run the Frappe site.

---

# 🐘 PostgreSQL Foundation Setup

The PostgreSQL layer is located under:

```text
database/
```

### 1. Create local environment

```bash
cd database
cp .env.example .env
```

Set unique local development passwords in `.env`.

### 2. Start PostgreSQL and PgBouncer

```bash
docker compose --env-file .env up -d
```

### 3. Database endpoints

```text
PostgreSQL
localhost:5432

PgBouncer
localhost:6432
```

Application traffic should use PgBouncer.

Migration operations intentionally use PostgreSQL directly.

### 4. Run migration

Use:

```text
database/scripts/migrate.ps1
```

with the configured migration database connection.

### 5. Run database tests

Use:

```text
database/scripts/test.ps1
```

with the dedicated test database.

> Do not use `docker compose down -v` against a database containing data that matters.

---

# 🎬 Hackathon Demo Flow

The recommended five-minute demonstration is a complete business workflow.

```text
01  Open Employee
        ↓
02  Show Contract
        ↓
03  Show Working Schedule
        ↓
04  Show Attendance
        ↓
05  Show Time Off
        ↓
06  Open Payroll
        ↓
07  New Payrun
        ↓
08  Step 1 — Scope & Period
        ↓
09  Step 2 — Employee Selection
        ↓
10  Review Applicable Contracts
        ↓
11  Review Payroll Warnings
        ↓
12  Create Payrun
        ↓
13  Open Payrun Processing
        ↓
14  Compute / Review Payslips
        ↓
15  Validate
        ↓
16  Mark Paid
        ↓
17  Generate / Print Payslip
        ↓
18  Send Payslips
        ↓
19  Open Payroll Dashboard
```

### What this demonstrates

- Employee-centric HR.
- Contract awareness.
- Attendance integration.
- Time Off integration.
- Explicit employee selection.
- Payroll warnings.
- Salary calculation.
- Payslip processing.
- Delivery.
- Operational analytics.

---

# 🏆 Engineering Highlights

| Area | Current Approach |
|---|---|
| Employee | Central HR record |
| Contract | Historical/date-effective model |
| Payrun | Two-step creation wizard |
| Eligibility | Server-side employee lookup |
| Contract Resolution | Applicable contract for payroll context |
| Warnings | Payroll Processing + Dashboard |
| Attendance | HRMS attendance + warning infrastructure |
| Time Off | Existing leave allocation/request workflow |
| Salary | Existing Salary Structure / Component engine |
| Payslip | Existing Salary Slip infrastructure |
| Dashboard | PeoplePay360 payroll dashboard |
| Security | Frappe permissions + server checks |
| Cache | Redis |
| Background Work | Frappe background-job infrastructure |
| Database Foundation | PostgreSQL 17 |
| Connection Pooling | PgBouncer |
| Data Integrity | PostgreSQL constraints/triggers |
| Audit | PostgreSQL audit foundation |
| CI/CD | GitHub Actions |
| Runtime | Docker + Frappe Bench |

---

# 🧩 Why This Architecture?

Payroll is a high-risk business domain.

Rebuilding authentication, employee records, leave management, salary calculation, permissions, PDF generation, accounting relationships and document lifecycle from scratch would create unnecessary complexity.

PeoplePay360 therefore uses a layered strategy:

```text
Mature Open-Source Platform
            +
PeoplePay360 Product Experience
            +
PeoplePay360 Business Rules
            =
Integrated HR & Payroll Platform
```

The existing Frappe/ERPNext ecosystem provides the platform primitives.

PeoplePay360 focuses on:

- Connected workflows.
- Payroll correctness.
- Period-aware context.
- Validation.
- Warning visibility.
- Employee selection.
- Operational analytics.
- Product-specific UX.

---

# 📊 Current vs Planned

## ✅ Implemented Today

```text
✓ PeoplePay360 branding
✓ HRMS foundation
✓ Employee management foundation
✓ Employment contracts
✓ Attendance
✓ Time Off
✓ Salary Structures
✓ Salary Components
✓ Salary Structure Assignments
✓ Two-step Payrun wizard
✓ Employee eligibility lookup
✓ Applicable contract lookup
✓ Payrun Processing screen
✓ Missing bank warnings
✓ Duplicate payslip detection
✓ Payroll Dashboard
✓ Payroll filters
✓ Payroll KPIs
✓ Department salary analysis
✓ Attendance overview
✓ Time Off overview
✓ Payslip infrastructure
✓ Bulk payslip email action
✓ PostgreSQL foundation
✓ PgBouncer configuration
✓ Database integrity constraints
✓ Database integration tests
✓ CI/CD workflows
```

## 🚧 Planned / Enhancement

```text
□ Automated demo seed
□ Contract amendment workflow
□ Advanced payroll validation
□ Detailed salary calculation trace UI
□ Mobile self-service polish
□ Cloudflare edge layer
□ Nginx production rate limiting
□ Prometheus/Grafana observability
□ Advanced payroll forecasting
□ Payroll anomaly detection
□ Advanced compliance automation
```

> This separation is intentional: **implemented functionality represents the current repository; planned functionality represents the future roadmap.**

---

# 🗺️ Roadmap

## Phase 1 — Foundation

- Stabilize current HRMS workflow.
- Verify representative payroll data.
- Maintain database integrity tests.

## Phase 2 — Payroll Correctness

- Improve contract resolution.
- Expand payroll validation.
- Improve duplicate protection.
- Strengthen salary calculation validation.

## Phase 3 — Product Experience

- Contract amendment workflow.
- Better Payrun review.
- Improved salary calculation trace.
- Improved employee self-service.

## Phase 4 — Production Hardening

- Cloudflare.
- Nginx.
- Rate limiting.
- Observability.
- Performance testing.
- Monitoring.

## Phase 5 — Intelligent Operations

- Payroll anomaly detection.
- Forecasting.
- Advanced analytics.
- Intelligent HR insights.

---

# 🔮 Future Vision

PeoplePay360 can evolve into a broader HR operations platform with:

- Employee self-service.
- Advanced payroll forecasting.
- Payroll anomaly detection.
- Automated compliance workflows.
- Workforce analytics.
- Attendance intelligence.
- Payroll cost forecasting.
- Multi-company analytics.
- Advanced workflow automation.

These capabilities remain **future enhancements** unless implemented and verified in the repository.

---

# 📌 Project Philosophy

> **Connect HR decisions to payroll outcomes.**

An employee should not be treated as an isolated database record.

Their:

```text
Employee
   ↓
Employment
   ↓
Contract
   ↓
Schedule
   ↓
Attendance + Time Off
   ↓
Salary Configuration
   ↓
Payroll
   ↓
Payslip
   ↓
Payment
```

should form a coherent operational chain.

PeoplePay360 focuses on making that chain more visible, validated, secure and operationally useful.

---

# 👥 Team

## PeoplePay360

**HR & Payroll Operations Platform**

Built for the hackathon with a focus on:

**Business Logic · System Design · Security · Scalability · Data Integrity · Auditability · User Experience**

---

# 📜 License

This project is developed as a hackathon implementation using the applicable open-source Frappe, ERPNext and Frappe HR ecosystem.

Refer to the repository's license files and applicable upstream project licenses for licensing terms.

---

<div align="center">

## PeoplePay360

### Connect HR. Simplify Payroll. Improve Operational Visibility.

**Built with a focus on correctness, security and scalable system design.**

</div>
