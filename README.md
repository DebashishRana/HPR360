<p align="center">
  <img src="docs/assets/peoplepay360-logo.png" alt="PeoplePay360 Logo" width="220">
</p>

<h1 align="center">PeoplePay360</h1>

<p align="center"><strong>HR & Payroll Operations Platform</strong></p>

<p align="center">Connecting employee lifecycle, contracts, attendance, time off, compensation, payroll processing, payslips and operational analytics.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Hackathon%20Build-0f766e?style=for-the-badge" alt="Hackathon Build">
  <img src="https://img.shields.io/badge/Platform-Frappe%20%2F%20ERPNext-red?style=for-the-badge" alt="Frappe ERPNext">
  <img src="https://img.shields.io/badge/Backend-Python-3776AB?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/Frontend-Vue%203-42B883?style=for-the-badge" alt="Vue 3">
  <img src="https://img.shields.io/badge/Database-MariaDB-003545?style=for-the-badge" alt="MariaDB">
  <img src="https://img.shields.io/badge/Cache%20%26%20Queue-Redis-DC382D?style=for-the-badge" alt="Redis">
  <img src="https://img.shields.io/badge/Deployment-Docker-2496ED?style=for-the-badge" alt="Docker">
  <img src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge" alt="GitHub Actions">
</p>

---

# 📚 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Implementation Status](#-implementation-status)
- [Implemented Features](#-implemented-features)
- [Platform Foundation](#-platform-foundation)
- [Planned Features](#-planned-features)
- [Complete Business Workflow](#-complete-business-workflow)
- [Architecture](#-architecture)
- [Architecture Diagram](#-architecture-diagram)
- [ERP Business Architecture](#-erp-business-architecture)
- [Workflows](#-workflows)
- [ER Diagram](#-er-diagram)
- [Sequence Diagrams](#-sequence-diagrams)
- [Security Architecture](#-security-architecture)
- [RBAC](#-role-based-access-control)
- [Performance & Scalability](#-performance--scalability)
- [Redis Architecture](#-redis-architecture)
- [Caching Strategy](#-caching-strategy)
- [Background Processing](#-background-processing)
- [Deployment Architecture](#-deployment-architecture)
- [Technology Stack](#-technology-stack)
- [Data Model](#-data-model)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Hackathon Demo](#-hackathon-demo)
- [Engineering Highlights](#-engineering-highlights)
- [Architecture Trade-offs](#-architecture-trade-offs)
- [Performance Metrics](#-performance-metrics)
- [Database Foundation](#-database-foundation)
- [Roadmap](#-roadmap)
- [Why PeoplePay360](#-why-peoplepay360)
- [License](#-license)

---

# 📌 Overview

**PeoplePay360** is an integrated Human Resource and Payroll Operations Platform built around one connected employee-to-payroll lifecycle.

The central idea is to avoid treating HR records as disconnected CRUD screens. Employee information, employment terms, working schedules, attendance, time off, compensation and payroll are connected so that payroll users can make decisions with the relevant context visible.

```text
Employee
   │
   ├──────────────► Employment Contract
   │
   ├──────────────► Working Schedule
   │
   ├──────────────► Attendance
   │
   ├──────────────► Time Off
   │
   └──────────────► Salary Structure Assignment
                           │
                           ▼
                    Salary Structure
                           │
                           ▼
                      Payrun Wizard
                           │
                           ▼
                  Employee Eligibility
                           │
                           ▼
                    Payroll Warnings
                           │
                           ▼
                      Payrun Created
                           │
                           ▼
                    Salary Slips
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Validate      Payment     PDF / Email
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Payroll Dashboard
                           │
                           ▼
                  PeoplePay360 Assistant
```

The current application uses the **Frappe / ERPNext / Frappe HRMS** ecosystem as the operational foundation. PeoplePay360-specific work is concentrated around the product workflow, Payrun experience, eligibility visibility, warnings, dashboard and assistant. The repository also contains an independent PostgreSQL foundation under `database/`; it is documented separately and is **not claimed here as the database currently powering the Frappe HRMS runtime**.

---

# 🎯 Problem Statement

HR and payroll operations depend on the same underlying employee facts, but conventional systems often expose them as disconnected modules.

Typical operational risks include:

- Payroll using the wrong employment context for a period.
- Missing or overlapping contracts.
- Incomplete attendance reaching payroll.
- Leave balances that are difficult to reconcile.
- Salary rules that are hard to understand or audit.
- Employees entering a payroll batch unintentionally.
- Missing bank or email information discovered too late.
- Duplicate payslips or repeated processing.
- Historical payroll becoming difficult to reproduce.
- Sensitive payroll data being visible to unauthorized roles.
- Limited management visibility across HR and payroll data.

### Product Goal

Build a connected workflow in which important dependencies are **visible, validated and operationally useful before payroll is finalized**.

---

# 💡 Solution

PeoplePay360 connects the major HR and payroll domains around the employee as the central business object.

| Domain | Connected responsibility |
|---|---|
| Employee | Master profile and employment context |
| Contract | Historical, date-effective employment terms |
| Schedule | Expected working pattern |
| Attendance | Actual time and exceptions |
| Time Off | Allocation, request, approval and balance |
| Compensation | Salary structures and components |
| Payrun | Payroll scope, employee selection and processing |
| Payslip | Employee-level payroll result |
| Dashboard | Cross-module operational visibility |
| Assistant | Role-aware HR/payroll context |

---

# 🚦 Implementation Status

This README intentionally separates what exists in the repository from future product evolution.

| Marker | Meaning |
|---|---|
| ✅ | Implemented in the current repository / demonstrable |
| 🟡 | Existing platform foundation reused by PeoplePay360 |
| 🚧 | Planned enhancement; not represented as completed |

---

# ✅ Implemented Features

## 1. PeoplePay360 Branding & Navigation

Implemented:

- PeoplePay360 application branding.
- PeoplePay360 application home/navigation.
- HR and Payroll workspace customization.
- PeoplePay360-specific product presentation.
- Custom PeoplePay360 payslip presentation.
- Dedicated Assistant entry point.

The logo used by this README is expected at:

```text
docs/assets/peoplepay360-logo.png
```

---

## 2. Two-Step Payrun Creation Wizard

The repository contains a dedicated Payrun Wizard instead of relying only on a single generic payroll creation form.

```text
STEP 1 — Scope & Period
          │
          ▼
STEP 2 — Employee Selection
          │
          ▼
Eligibility / Warning Context
          │
          ▼
Create Payroll Entry
```

### Step 1 — Scope

Supported payroll scope inputs include:

- Company.
- Salary Structure.
- Posting Date.
- Payroll Frequency.
- Start Date.
- End Date.
- Department.
- Designation.
- Branch.
- Currency.
- Payroll Payable Account.
- Salary-slip-based-on-timesheet option.

### Step 2 — Employee Selection

The selection view provides server-derived payroll candidates and employee context, including:

- Employee.
- Employee name.
- Department.
- Designation.
- Contract context.
- Withheld / payroll-related status.
- Select All / Deselect All.
- Selection summary.

The final Payroll Entry is created using the employees selected in the wizard.

> **Accuracy note:** the repository contains server-side eligibility lookup and validation logic. This README does not claim that every possible crafted browser selection is revalidated by a separate final authorization service unless that behavior is explicitly wired into the insert path.

---

## 3. Period-Aware Employee Eligibility

The Payrun backend resolves applicable employee payroll context using the selected period.

Conceptually:

```text
Employee
   │
   ▼
Company / Scope Filters
   │
   ▼
Applicable Contract
   │
   ▼
Salary Structure / Assignment
   │
   ▼
Payroll Context
```

The implementation uses `get_applicable_contract(...)` for period-aware contract resolution and can fall back to Salary Structure Assignment where applicable.

---

## 4. Payroll Warning Detection

The Payrun flow exposes operational warning information before processing.

Examples include:

### Blocking / high-risk conditions

- Missing applicable contract.
- Invalid payroll scope.
- Duplicate payslip conditions.
- Salary configuration issues.
- Attendance-related payroll readiness issues where validation is enabled.

### Review conditions

- Missing bank details.
- Missing email details.
- Contract attention / overlap situations.

The exact warning policy remains configurable and should be treated separately from the underlying platform's generic validation behavior.

---

## 5. Payrun Processing Page

A dedicated payroll processing interface provides operational visibility into a Payroll Entry.

It can surface:

- Payrun name.
- Company.
- Payroll period.
- Payroll frequency.
- Employee count.
- Salary Slip count.
- Submitted Salary Slip count.
- Missing bank details.
- Duplicate payslip information.
- Payment / processing information.
- Salary Slip details.

Supported workflow actions include the underlying payroll processing operations such as:

```text
Compute
   ↓
Validate / Review
   ↓
Mark Paid
   ↓
Send Payslips
```

---

## 6. Payroll Dashboard

The repository contains a dedicated Payroll Dashboard with live metrics derived from application records.

### Filters

- From Date.
- To Date.
- Company.
- Department.
- Employment Type.

### KPI examples

- Total Net Salary.
- Payslips Generated.
- Average Salary.
- Approved Time Off.
- Active Employees.
- Attendance Health.

### Analytics

```text
Payroll Cost Trend
Department Salary Breakdown
Attendance Overview
Time Off Overview
Payroll Alerts
```

### Operational warnings

The dashboard can surface items such as:

- Queued payruns.
- Failed payruns.
- Unmarked attendance.
- Missing bank details.
- Duplicate payslips.
- Contract attention.

---

## 7. Attendance Warning Infrastructure

Attendance data can be used as payroll-readiness context.

```text
Employee Check-in / Check-out
             │
             ▼
         Attendance
             │
             ▼
       Exception Review
             │
             ▼
     Payroll Readiness Context
```

The repository also uses asynchronous Frappe job infrastructure for expensive attendance processing.

---

## 8. Employment Contract Validation

Employment Contract logic contains validation to prevent multiple active contracts for the same period.

```text
Contract A: Jan ───────── Jun
Contract B:        May ───────── Dec
                     │
                     ▼
                 OVERLAP
                     │
                     ▼
                 VALIDATION
```

The Payrun path additionally resolves an applicable contract for the selected payroll date/period.

---

## 9. Payslip Generation & Delivery

The platform provides employee-level Salary Slips and PeoplePay360-specific presentation.

```text
Payroll Entry
      │
      ▼
Salary Slip
      │
      ├── Earnings
      ├── Deductions
      ├── Gross Pay
      └── Net Pay
      │
      ├────────► Print / PDF
      │
      └────────► Bulk Email Queue
```

The bulk email action uses Frappe's asynchronous job infrastructure rather than making the user wait for every email operation.

---

## 10. PeoplePay360 Assistant

The repository contains a PeoplePay360 Assistant layer for HR/payroll-oriented context.

It is designed around the authenticated user's capabilities and relevant HR/payroll data.

Example questions:

```text
How many active employees are there?
Which employees need attention?
Show attendance status.
Show pending Time Off.
Which contracts need attention?
Show payroll information.
```

---

## 11. Demo Seed Infrastructure

The repository contains PeoplePay360 demo-seeding infrastructure to help create a realistic demonstration environment.

Conceptual seed flow:

```text
Company
   ↓
Departments
   ↓
Employees
   ↓
Contracts / Schedules
   ↓
Attendance / Time Off
   ↓
Salary Configuration
   ↓
Payroll
   ↓
Payslips
```

---

# 🟡 Platform Foundation

PeoplePay360 intentionally reuses mature capabilities already provided by Frappe / ERPNext / HRMS.

These are **platform capabilities**, not all custom PeoplePay360 code.

## HR Foundation

- Employee management.
- Company and organization records.
- Departments.
- Designations.
- Branches.
- Employee Types.
- Employment Contracts.
- Working Schedules / shifts.
- Employee Check-ins.
- Attendance.
- Attendance Requests.
- Leave Types.
- Leave Allocations.
- Leave Applications.
- Leave Policies.
- Holiday Lists.
- Shift Assignments.

## Payroll Foundation

- Payroll Entry.
- Payroll Employee Detail.
- Salary Slip.
- Salary Structure.
- Salary Component.
- Salary Structure Assignment.
- Payroll Period.
- Additional Salary.
- Employee Benefits.
- Payroll accounting.
- Payment Entry.
- Payroll reports.

## Frappe Platform Foundation

- Authentication.
- Sessions.
- CSRF protection.
- Role and DocType permissions.
- ORM / document lifecycle.
- Server methods.
- Reports.
- Print formats.
- PDF rendering.
- Email infrastructure.
- Background jobs.
- Redis queues.
- Realtime infrastructure.
- Workspaces.

---

# 🚧 Planned Features

The following are future enhancements and should **not** be presented as completed functionality.

## 1. Advanced Payroll Validation

- Advanced payroll readiness scoring.
- More granular blocking/review/informational rules.
- Advanced compliance validation.
- More payroll-period consistency checks.

## 2. Contract Amendment Workflow

```text
Existing Contract
       ↓
Amendment Request
       ↓
Approval
       ↓
Effective Date
       ↓
New Contract Version
       ↓
Payroll Synchronization
```

## 3. Advanced Salary Calculation Trace

Future employee-level traceability:

```text
Basic
  +
Allowances
  +
Variable Pay
  ↓
Gross
  ↓
Contributions / Deductions
  ↓
Net Salary
```

## 4. Payroll Intelligence

Potential future features:

- Payroll anomaly detection.
- Payroll forecasting.
- Workforce cost forecasting.
- Attendance anomaly detection.
- Intelligent payroll recommendations.

## 5. Production Edge Security

Potential production additions:

- Cloudflare WAF.
- Nginx reverse proxy.
- Rate limiting.
- TLS termination.
- Load balancing.

## 6. Advanced Observability

Potential production additions:

- Prometheus.
- Grafana.
- Distributed tracing.
- Centralized logs.
- Error monitoring.
- Queue-depth dashboards.

## 7. Advanced Mobile Experience

Potential future improvements:

- Employee self-service polish.
- Attendance UX improvements.
- Time Off UX improvements.
- Mobile payroll/payslip experience.

---

# 🔄 Complete Business Workflow

```text
                         COMPANY
                            │
                            ▼
                        EMPLOYEE
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
       CONTRACT          SCHEDULE          SALARY
          │                 │                 │
          ▼                 ▼                 ▼
      EMPLOYMENT         ATTENDANCE       SALARY
        STATE                              ASSIGNMENT
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                         TIME OFF
                            │
                            ▼
                       PAYRUN WIZARD
                            │
                            ▼
                    EMPLOYEE ELIGIBILITY
                            │
                 ┌──────────┼──────────┐
                 ▼          ▼          ▼
              ELIGIBLE    REVIEW    BLOCKED
                 │          │
                 └────┬─────┘
                      ▼
                EMPLOYEE SELECTION
                      │
                      ▼
                 CREATE PAYRUN
                      │
                      ▼
               SALARY CALCULATION
                      │
                      ▼
                    PAYSLIPS
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
          VALIDATE   PAY     DELIVERY
                              │
                         PDF / EMAIL
                              │
                              ▼
                     PAYROLL DASHBOARD
                              │
                              ▼
                    PEOPLEPAY360 ASSISTANT
```

---

# 🏗️ Architecture

PeoplePay360 follows an **extension-first architecture**.

The principle is:

```text
Mature Open-Source HR / ERP Foundation
                  +
       PeoplePay360 Product Layer
                  +
      Connected Operational UX
                  +
       Validation / Visibility
                  ↓
        Integrated HR & Payroll
```

---

# 🧱 Architecture Diagram

```text
                         ┌─────────────────────┐
                         │        USERS        │
                         │ Employee / HR /     │
                         │ Payroll / Admin     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────┐
                │          EXPERIENCE LAYER          │
                │                                    │
                │ Frappe Desk                        │
                │ Vue 3 / Ionic                      │
                │ Workspaces                         │
                │ Payrun Wizard                      │
                │ Payrun Processing                  │
                │ Payroll Dashboard                  │
                │ PeoplePay360 Assistant             │
                └────────────────┬───────────────────┘
                                 │
                                 ▼
                ┌────────────────────────────────────┐
                │     PEOPLEPAY360 PRODUCT LAYER     │
                │                                    │
                │ Eligibility                        │
                │ Payroll warnings                   │
                │ Payrun workflow                    │
                │ Dashboard aggregation              │
                │ Role-aware assistant               │
                │ Product presentation               │
                │ Demo seed                          │
                └────────────────┬───────────────────┘
                                 │
                                 ▼
                ┌────────────────────────────────────┐
                │       FRAPPE / HRMS / ERPNext      │
                │                                    │
                │ HR │ Attendance │ Leave            │
                │ Payroll │ Accounting │ Permissions │
                │ Documents │ ORM │ Reports          │
                │ Print │ Email │ Background Jobs    │
                └───────────────┬────────────────────┘
                                │
                     ┌──────────┴───────────┐
                     ▼                      ▼
             ┌────────────────┐     ┌────────────────┐
             │    MariaDB     │     │     Redis      │
             │                │     │                │
             │ Durable data   │     │ Cache          │
             │ HR records     │     │ Queue          │
             │ Payroll data   │     │ Realtime       │
             │ ERP records    │     │ coordination   │
             └────────────────┘     └───────┬────────┘
                                            │
                                            ▼
                                      Background
                                        Workers
```

---

# 🏢 ERP Business Architecture

```text
                         COMPANY
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
       Departments      Employees      Accounting
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
          Contract       Schedule       Salary
             │              │              │
             ▼              ▼              ▼
        Attendance      Time Off     Salary Assignment
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                          PAYRUN
                            │
                    ┌───────┴───────┐
                    ▼               ▼
                PAYSLIPS         PAYMENT
                    │
               ┌────┴────┐
               ▼         ▼
              PDF      EMAIL
                    │
                    ▼
                DASHBOARD
                    │
                    ▼
                ASSISTANT
```

---

# 🔄 Workflows

## HR Setup Workflow

```text
Company
   ↓
Departments / Designations / Employee Types
   ↓
Working Schedule / Shift
   ↓
Time Off Types
   ↓
Salary Components
   ↓
Salary Structure
   ↓
Employee
   ↓
Contract + Salary Assignment
   ↓
Payroll Ready
```

---

## Employee Lifecycle Workflow

```text
Employee Creation
       │
       ▼
Personal / Employment Information
       │
       ▼
Department / Designation
       │
       ▼
Employment Contract
       │
       ▼
Working Schedule
       │
       ▼
Attendance / Check-ins
       │
       ▼
Time Off
       │
       ▼
Salary Assignment
       │
       ▼
Payroll
       │
       ▼
Payslip
       │
       ▼
Payment
```

---

## Attendance Workflow

```text
Employee
   │
   ▼
Check In / Check Out
   │
   ▼
Employee Checkin
   │
   ▼
Attendance Processing
   │
   ▼
Attendance Status
   │
   ├──────────────► Normal
   │
   └──────────────► Exception
                         │
                         ▼
                       Review
                         │
                         ▼
                     Correction
```

---

## Time Off Workflow

```text
Employee
   │
   ▼
Time Off Request
   │
   ▼
Manager Approval
   │
   ├──────────────► Rejected
   │
   └──────────────► Approved
                         │
                         ▼
                    Leave Balance
                         │
                         ▼
                  Attendance / Payroll
```

---

## Salary Configuration Workflow

```text
Salary Components
       │
       ▼
Salary Structure
       │
       ▼
Salary Structure Assignment
       │
       ▼
Effective Date
       │
       ▼
Employee
       │
       ▼
Payrun
```

---

## Payrun Workflow

```text
Open Payrun Wizard
       │
       ▼
Define Payroll Scope
       │
       ▼
Validate Scope
       │
       ▼
Load Employee Candidates
       │
       ▼
Resolve Applicable Contract
       │
       ▼
Resolve Salary Context
       │
       ▼
Attendance / Duplicate / Required-Data Checks
       │
       ▼
Warnings + Eligibility Context
       │
       ▼
Explicit Employee Selection
       │
       ▼
Create Payroll Entry
```

---

## Payroll Warning Workflow

```text
                 EMPLOYEE CANDIDATE
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      CONTRACT         SALARY       ATTENDANCE
        CHECK           CHECK          CHECK
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  DUPLICATE CHECK
                         │
                         ▼
                  REQUIRED DATA
                         │
                         ▼
                WARNING CLASSIFIER
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          BLOCKING     REVIEW      CLEAR
              │          │          │
              ▼          ▼          ▼
           Blocked    Review     Eligible
```

---

## Payrun Processing Workflow

```text
Payroll Entry
      │
      ▼
Generate Salary Slips
      │
      ▼
Salary Calculation
      │
      ▼
Review Results
      │
      ▼
Validate / Submit
      │
      ▼
Payment Entry / Payment Flow
      │
      ▼
Print / PDF / Email
      │
      ▼
Dashboard
```

---

## Payslip Workflow

```text
Payroll Entry
      │
      ▼
Salary Calculation
      │
      ▼
Salary Slip
      │
      ├── Basic
      ├── Allowances
      ├── Contributions
      ├── Gross
      ├── Deductions
      └── Net
      │
      ▼
Submit
      │
      ├────────► PDF
      └────────► Email Queue
```

---

## Payroll Dashboard Data Flow

```text
Employee Records
      │
Attendance Records
      │
Leave Applications
      │
Employment Contracts
      │
Payroll Entries
      │
Salary Slips
      │
      └──────────────┐
                     ▼
             Dashboard Backend
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
         KPIs     Analytics    Alerts
          │          │          │
          ├ Salary   ├ Trends   ├ Queued
          ├ Headcount├ Dept     ├ Failed
          ├ Attendance├ Attendance├ Missing Bank
          └ Time Off └ Time Off ├ Duplicate
                                └ Contract
```

---

# 🗄️ ER Diagram

```text
                         ┌──────────────┐
                         │    COMPANY   │
                         └──────┬───────┘
                                │ 1:N
                                ▼
                         ┌──────────────┐
                         │   EMPLOYEE   │
                         └──────┬───────┘
                                │
       ┌────────────────────────┼─────────────────────────┐
       │                        │                         │
       ▼                        ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌────────────────┐
│ EMPLOYMENT    │       │ EMPLOYEE      │       │  ATTENDANCE    │
│ CONTRACT      │       │ CHECKIN       │       │                │
└───────────────┘       └───────────────┘       └────────────────┘
       │
       ▼
┌───────────────┐
│ WORKING       │
│ SCHEDULE      │
└───────────────┘

EMPLOYEE
   │
   ├──────────────► LEAVE ALLOCATION
   │                     │
   │                     ▼
   │               LEAVE APPLICATION
   │                     │
   │                     ▼
   │                  LEAVE TYPE
   │
   └──────────────► SALARY STRUCTURE ASSIGNMENT
                         │
                         ▼
                  SALARY STRUCTURE
                         │
                         ▼
                  SALARY COMPONENTS

PAYROLL ENTRY
      │
      ├──────────────► PAYROLL EMPLOYEE DETAIL ─────► EMPLOYEE
      │
      ├──────────────► SALARY SLIP ─────────────────► EMPLOYEE
      │                                      │
      │                                      ├── Earnings
      │                                      ├── Deductions
      │                                      └── Net Pay
      │
      └──────────────► PAYMENT ENTRY
```

---

# 🔗 Entity Relationships

```text
EMPLOYEE
│
├── Employment Contract
├── Working Schedule / Shift Assignment
├── Employee Checkin
├── Attendance
├── Leave Allocation
├── Leave Application
├── Salary Structure Assignment
└── Salary Slip

SALARY STRUCTURE
└── Salary Components

PAYROLL ENTRY
├── Payroll Employee Detail
├── Salary Slips
├── Payroll Period
└── Payment Entry
```

---

# 🔄 Sequence Diagrams

## Payrun Creation Sequence

```text
USER
 │
 │ Configure payroll scope
 ▼
PAYRUN WIZARD
 │
 │ Request eligible employees
 ▼
PAYRUN BACKEND
 │
 ├── Validate company / period
 ├── Resolve employees
 ├── Resolve applicable contract
 ├── Resolve salary context
 ├── Check attendance context
 ├── Check duplicate payslips
 └── Build warnings
 │
 ▼
EMPLOYEE SELECTION
 │
 │ Selected employee IDs
 ▼
PAYROLL ENTRY CREATION
 │
 ▼
PAYROLL RECORDS
```

---

## Payroll Processing Sequence

```text
PAYROLL USER
     │
     ▼
PAYRUN PROCESSING PAGE
     │
     ▼
LOAD PAYROLL DATA
     │
     ▼
COMPUTE SALARY SLIPS
     │
     ▼
SALARY SLIPS
     │
     ▼
VALIDATE / SUBMIT
     │
     ▼
PAYMENT FLOW
     │
     ▼
SEND PAYSLIPS
     │
     ▼
REDIS-BACKED BACKGROUND JOB
     │
     ▼
EMAIL DELIVERY
```

---

## Assistant Sequence

```text
USER
 │
 ▼
ASSISTANT UI
 │
 ▼
ASSISTANT API
 │
 ▼
AUTHENTICATED USER / ROLE CONTEXT
 │
 ▼
CONTEXT RESOLUTION
 │
 ├── Employee
 ├── Attendance
 ├── Time Off
 ├── Contracts
 └── Payroll
 │
 ▼
RESPONSE ENGINE
 │
 ▼
ROLE-AWARE RESPONSE
```

---

# 🔐 Security Architecture

HR and payroll contain sensitive personal and financial information. Security is therefore enforced as a server-side concern.

```text
                         USER
                          │
                          ▼
                   AUTHENTICATION
                          │
                          ▼
                    FRAPPE SESSION
                          │
                          ▼
                     ROLE RESOLUTION
                          │
               ┌──────────┴──────────┐
               ▼                     ▼
       UI Capability Check     Server Permission
               │                     │
               └──────────┬──────────┘
                          ▼
                 Business Validation
                          │
                          ▼
                    HR / PAYROLL
                          │
                          ▼
                       MariaDB
```

### Security principles

- Server-side authorization.
- Role and DocType permissions.
- Record-level restrictions where required.
- Sensitive payroll configuration restricted by role.
- Frontend visibility is not treated as the security boundary.
- Payroll history should not be casually rewritten.
- Privileged operations should remain auditable.
- Secrets must stay outside source control.

---

# 👥 Role-Based Access Control

The intended product role model is:

| Role | Core responsibility |
|---|---|
| Employee | Own employee, attendance, Time Off and payslip context |
| HR Manager | Employee, contracts, schedules, attendance and Time Off |
| HR Payroll User | HR operations plus payroll processing and payslips |
| HR Payroll Manager | Full HR + payroll configuration and processing |
| Admin | Full system and permission administration |

Conceptual hierarchy:

```text
                         ADMIN
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        HR PAYROLL MANAGER       HR MANAGER
                │                     │
                ▼                     ▼
        HR PAYROLL USER          HR OPERATIONS
                │
                ▼
             EMPLOYEE
```

> Exact permissions should be verified against the current Frappe Role / DocType configuration before treating the matrix as a security certification.

---

# ⚡ Performance & Scalability

The architecture separates durable business data from fast/temporary infrastructure.

```text
MariaDB = Durable Source of Truth
Redis   = Cache + Queue + Realtime Coordination
Workers = Expensive Background Processing
```

Performance strategy:

```text
Interactive Request
       │
       ▼
Fast Validation / Read
       │
       ├────────► Redis HIT → Fast Response
       │
       └────────► DB Read → Optional Cache Population

Expensive Work
       │
       ▼
Redis-backed Queue
       │
       ▼
Background Worker
       │
       ▼
Result / Status Update
```

---

# 🔴 Redis Architecture

Redis is already integrated through Frappe infrastructure; it is not an artificial Node/Express Redis layer.

Redis serves multiple roles:

```text
                         REDIS
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
         CACHE           QUEUE          REALTIME
           │               │               │
           ▼               ▼               ▼
       Fast Reads      Workers        Push Events
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Payroll     Attendance      Email
```

The repository Docker setup uses the Compose service name `redis` for container-to-container connectivity.

---

# 🧠 Caching Strategy

The repository uses real Frappe cache APIs for suitable data.

### Cache-aside pattern

```text
Request
  │
  ▼
Check Redis
  │
  ├── HIT ───────► Return Cached Value
  │
  └── MISS
       │
       ▼
   Read / Calculate
       │
       ▼
    Store Cache
       │
       ▼
   Return Result
```

Examples documented in the repository's Redis system-design material include holiday calculations and leave-type mappings.

### Cache invalidation

Payroll correctness matters more than blindly maximizing cache hit rate.

```text
Update Source Data
       │
       ▼
Invalidate Dependent Cache
       │
       ▼
Next Read
       │
       ▼
Fresh Value
```

The repository includes cache invalidation for payroll-relevant configuration such as leave types and salary component data.

---

# 🔁 Background Processing

Long-running operations should not monopolize the interactive HTTP request.

Frappe's `frappe.enqueue()` is used for real asynchronous workloads.

```text
User Action
    │
    ▼
Fast Validation
    │
    ▼
Enqueue Job
    │
    ▼
Redis Queue
    │
    ▼
Background Worker
    │
    ├── Payroll Processing
    ├── Attendance Processing
    ├── Bulk Payslip Email
    └── Other Expensive Work
    │
    ▼
Status / Result
```

The repository's Redis guide documents examples for:

- Large payroll salary-slip generation.
- Attendance processing.
- Bulk salary-slip email.
- Overtime processing.
- Realtime infrastructure.

This gives the project a genuine latency/concurrency strategy rather than merely claiming that Redis is installed.

---

# 🌐 Realtime Architecture

```text
Browser / PWA
     │
     │ WebSocket / realtime event
     ▼
Frappe Realtime Layer
     │
     ▼
Redis Socket / Realtime Infrastructure
     │
     ▼
Connected Clients
```

Useful cases include:

- Job status.
- Progress notifications.
- Dashboard refreshes.
- Server-to-client events.

---

# 🐳 Docker Architecture

The main Docker environment provisions the Frappe runtime together with MariaDB and Redis.

```text
┌──────────────────────────────────────────┐
│              Docker Compose              │
│                                          │
│   ┌─────────────┐                        │
│   │   Frappe    │                        │
│   │   Bench     │                        │
│   └──────┬──────┘                        │
│          │                               │
│     ┌────┴────┐                          │
│     ▼         ▼                          │
│  MariaDB    Redis                        │
│     │         │                          │
│     ▼         ├── Cache                  │
│   Durable     ├── Queue                  │
│    Data       └── Realtime               │
└──────────────────────────────────────────┘
```

Configured development services include the Frappe web service and Redis/MariaDB infrastructure. The repository's compose file exposes the configured development ports, including port `8000` for the web interface.

---

# 🚀 Deployment Architecture

## Current development topology

```text
Developer / Browser
        │
        ▼
Docker Compose
        │
        ├── Frappe Bench
        ├── MariaDB
        └── Redis
```

## Production evolution

```text
                         INTERNET
                            │
                            ▼
                       CLOUDFLARE
                            │
                            ▼
                          NGINX
                            │
                            ▼
                     LOAD BALANCER
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          APP-01         APP-02         APP-03
             │              │              │
             └──────────────┼──────────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
                REDIS              MariaDB
                  │
                  ▼
               WORKERS
```

> Cloudflare, Nginx, multi-node application scaling and advanced observability are production evolution plans, not claims about the current hackathon deployment.

---

# 🗃️ Data Model

## Employee-centric model

```text
Employee
│
├── Employment Contract
├── Working Schedule / Shift Assignment
├── Employee Checkin
├── Attendance
├── Leave Allocation
├── Leave Application
├── Salary Structure Assignment
└── Salary Slip
```

## Payroll-centric model

```text
Payroll Entry
│
├── Payroll Employee Detail
│       └── Employee
│
├── Salary Slip
│       ├── Employee
│       ├── Salary Structure
│       ├── Earnings
│       ├── Deductions
│       └── Net Pay
│
└── Payment Entry
```

---

# 🧾 Salary Calculation Model

```text
Salary Structure
       │
       ▼
Ordered Salary Components
       │
       ├── Basic
       ├── Allowances
       ├── Contributions
       └── Deductions
       │
       ▼
Gross Salary
       │
       ▼
Deductions / Contributions
       │
       ▼
Net Salary
       │
       ▼
Salary Slip
```

The existing Frappe payroll calculation engine remains the authoritative calculation foundation rather than introducing an unnecessary parallel formula engine.

---

# 🔒 Payroll State Model

The underlying Frappe payroll lifecycle can be represented conceptually as:

```text
Draft
  │
  ▼
Compute / Queue
  │
  ▼
Salary Slips Generated
  │
  ▼
Review / Validate
  │
  ▼
Submitted
  │
  ▼
Payment
  │
  ▼
Paid
  │
  ▼
Payslip Delivery
```

PeoplePay360 adds operational visibility around these states rather than inventing a second financial ledger.

---

# 🧪 Testing

Testing spans the application layer and the independent PostgreSQL foundation.

## Application testing

The repository includes Frappe/HRMS unit-test infrastructure and dedicated Payrun Wizard tests.

Important areas:

- Payrun scope validation.
- Employee eligibility.
- Contract resolution.
- Salary assignment context.
- Duplicate payslip detection.
- Payroll processing behavior.
- Dashboard data retrieval.
- Assistant behavior where applicable.

## Database foundation testing

The `database/tests/` suite exercises failure conditions including:

- Foreign-key integrity.
- Invalid/empty ranges.
- Overlapping contracts.
- Append-only leave ledger behavior.
- Salary-rule dependency cycle violations.
- Invalid payroll periods.
- Duplicate payslip prevention.

---

# 🧪 Test Matrix

| Scenario | Expected outcome |
|---|---|
| Missing company | Reject payroll scope |
| Missing payroll period | Reject payroll scope |
| Invalid date range | Reject |
| Missing payroll frequency | Reject |
| Missing applicable contract | Warning / block according to policy |
| Overlapping contracts | Validation / review |
| Invalid salary configuration | Blocking validation |
| Duplicate payslip | Blocking validation |
| Missing bank details | Review warning |
| Missing email | Review warning |
| Attendance validation failure | Warning / block according to policy |
| Valid employee | Eligible |

---

# 🔁 CI/CD

The repository contains GitHub Actions workflows for automated checks and Frappe/HRMS testing.

Conceptual pipeline:

```text
Developer Push / Pull Request
              │
              ▼
       GitHub Actions
              │
       ┌──────┴──────┐
       ▼             ▼
 Python Setup     Node Setup
       │             │
       └──────┬──────┘
              ▼
      Compilation / Checks
              │
              ▼
        MariaDB Service
              │
              ▼
      Install Dependencies
              │
              ▼
       Frappe / HRMS Tests
              │
          ┌───┴───┐
          ▼       ▼
        PASS     FAIL
          │       │
          ▼       ▼
      Coverage  Pipeline
```

CI capabilities include automated test execution, compilation checks, dependency caching and coverage reporting.

---

# 🧰 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Frappe Framework | Documents, ORM, APIs, permissions, jobs |
| ERP | ERPNext | Accounting, company and payment foundation |
| HR / Payroll | Frappe HR / HRMS | Employee, attendance, leave and payroll |
| Backend | Python | Business logic and controllers |
| Main UI | Frappe Desk | Operational HR/payroll interface |
| Frontend | Vue 3 | Modern operational/self-service UI |
| Mobile/PWA | Ionic Vue | Mobile-oriented experience |
| Build | Vite | Frontend tooling |
| Styling | Tailwind / Frappe UI | UI presentation |
| Database | MariaDB | Current Frappe operational persistence |
| Cache | Redis | Fast reads / cache |
| Queue | Redis + Frappe Workers | Background processing |
| Runtime | Docker Compose / Frappe Bench | Reproducible environment |
| CI/CD | GitHub Actions | Automated validation |
| Coverage | Codecov | Coverage reporting |
| DB Foundation | PostgreSQL 17 | Independent PeoplePay360 SQL foundation |
| DB Pooling | PgBouncer | PostgreSQL foundation connection pooling |

---

# 🗄️ Database Foundation

The repository also contains an independent PostgreSQL foundation under `database/`.

## Important distinction

```text
CURRENT FRAPPE RUNTIME
Frappe / HRMS
     │
     ▼
 MariaDB
     │
     ▼
 Redis

SEPARATE PEOPLEPAY360 FOUNDATION
PeoplePay360 SQL Domain Model
     │
     ▼
 PgBouncer
     │
     ▼
PostgreSQL 17
```

The PostgreSQL layer should **not** be described as the current Frappe application's operational database unless application integration is completed.

## PostgreSQL schemas

```text
identity
organization
workforce
time
leave
compensation
payroll
audit
analytics
```

## Foundation protections

The SQL foundation includes structures for:

- Foreign-key integrity.
- Effective-date contract ranges.
- Contract overlap protection.
- Salary-rule dependency protection.
- Payroll state transitions.
- Payroll locking.
- Idempotency keys.
- Posted payroll immutability.
- Payslip immutability.
- Append-only audit structures.
- Analytics views.

The database documentation specifies transaction-scoped payroll locking and idempotency patterns for that foundation.

---

# 🔐 Data Integrity Principles

## Contract integrity

```text
Employee
  ↓
Date-effective contracts
  ↓
One deterministic applicable context
```

## Salary-rule integrity

```text
Rule A
  ↓
Rule B
  ↓
Rule C
```

Dependencies must form a valid calculation graph rather than a cycle.

## Payslip integrity

A payslip should remain associated with:

- Employee.
- Payroll period.
- Payroll run.
- Salary context.
- Calculated component values.

## Historical integrity

Finalized payroll should be treated as historical financial data.

```text
Current Configuration
        ≠
Historical Payroll Result
```

---

# 📁 Project Structure

```text
HPR360-main/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── release.yml
│       ├── docs_checker.yml
│       └── other repository automation
│
├── database/
│   ├── migrations/
│   ├── tests/
│   ├── pgbouncer/
│   ├── scripts/
│   ├── docker-compose.yml
│   └── README.md
│
├── docker/
│   ├── docker-compose.yml
│   ├── init.sh
│   └── seed / verification helpers
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── router/
│   │   ├── utils/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
│
├── hrms/
│   ├── hr/
│   │   ├── doctype/
│   │   ├── report/
│   │   └── workspace/
│   │
│   ├── payroll/
│   │   ├── doctype/
│   │   ├── page/
│   │   │   ├── payrun_wizard/
│   │   │   ├── payrun_processing/
│   │   │   └── payroll_dashboard/
│   │   ├── print_format/
│   │   └── workspace/
│   │
│   ├── peoplepay360/
│   │   ├── chatbot/
│   │   ├── demo_seed.py
│   │   └── roles.py
│   │
│   ├── shift_and_attendance/
│   ├── tax_and_benefits/
│   └── hooks.py
│
├── docs/
│   └── assets/
│       └── peoplepay360-logo.png
│
├── main.md
├── PeoplePay360 HR & Payroll.md
├── PeoplePay360-ROADMAP.md
├── SECURITY.md
├── pyproject.toml
├── package.json
└── README.md
```

---

# 🔌 Key Components

## Payrun Wizard

```text
hrms/payroll/page/payrun_wizard/
```

Responsibilities:

- Payroll scope.
- Period selection.
- Employee eligibility lookup.
- Contract context.
- Salary context.
- Payroll warnings.
- Employee selection.
- Payroll Entry creation.

## Payrun Processing

```text
hrms/payroll/page/payrun_processing/
```

Responsibilities:

- Payrun status.
- Salary Slip status.
- Warning display.
- Processing actions.
- Payment flow.
- Payslip delivery.

## Payroll Dashboard

```text
hrms/payroll/page/payroll_dashboard/
```

Responsibilities:

- KPIs.
- Salary trends.
- Department breakdown.
- Attendance analytics.
- Time Off analytics.
- Payroll alerts.

## PeoplePay360 Assistant

```text
hrms/peoplepay360/chatbot/
```

Core areas include API/context/engine logic and supporting role/data utilities.

---

# ⚙️ Configuration & Environment

Do not commit credentials.

Typical environment-sensitive configuration includes:

- Database credentials.
- PostgreSQL foundation credentials.
- PgBouncer credentials.
- Site configuration.
- Email configuration.
- Deployment-specific secrets.

The PostgreSQL foundation provides `.env.example` as the local configuration starting point.

---

# 🚀 Getting Started

## Prerequisites

- Git.
- Docker.
- Docker Compose.
- Python 3.10+.
- Node.js.
- Yarn.
- Frappe Bench where required by the development workflow.

## Start the main Frappe environment

```bash
cd docker
docker compose up -d
```

Check services:

```bash
docker compose ps
```

The repository Docker setup includes:

```text
MariaDB
Redis
Frappe Bench / Application
```

## Frappe development commands

Inside the configured Bench environment:

```bash
bench --site <site-name> migrate
bench --site <site-name> clear-cache
bench --site <site-name> enable-scheduler
```

## Frontend

```bash
cd frontend
yarn install
yarn build
```

For development:

```bash
yarn dev
```

## PostgreSQL foundation

The PostgreSQL foundation is independent:

```bash
cd database
cp .env.example .env
docker compose --env-file .env up -d
```

Then follow `database/README.md` for migrations, PgBouncer and SQL tests.

> Do not mix the PostgreSQL foundation with the current Frappe MariaDB runtime when describing the application architecture.

---

# 🧪 Verification Checklist

```text
1. Start Docker
      ↓
2. Verify MariaDB
      ↓
3. Verify Redis
      ↓
4. Verify Frappe
      ↓
5. Verify PeoplePay360 workspace
      ↓
6. Seed / prepare demo data
      ↓
7. Verify Employee
      ↓
8. Verify Contract
      ↓
9. Verify Schedule
      ↓
10. Verify Attendance
      ↓
11. Verify Time Off
      ↓
12. Open Payrun Wizard
      ↓
13. Verify eligibility / warnings
      ↓
14. Create Payrun
      ↓
15. Process Salary Slips
      ↓
16. Validate / Pay
      ↓
17. Verify Payslip PDF
      ↓
18. Send Payslips
      ↓
19. Verify Dashboard
      ↓
20. Verify Assistant
```

---

# 🎬 Hackathon Demo

The strongest demo is one continuous business scenario rather than disconnected screens.

## Recommended 5–7 minute flow

```text
01  Login
     ↓
02  PeoplePay360 Home
     ↓
03  Employee
     ↓
04  Contract + Working Schedule
     ↓
05  Attendance
     ↓
06  Time Off
     ↓
07  Payroll
     ↓
08  Payrun Wizard — Scope
     ↓
09  Employee Eligibility
     ↓
10  Warnings
     ↓
11  Explicit Employee Selection
     ↓
12  Create Payrun
     ↓
13  Payrun Processing
     ↓
14  Generate / Review Payslips
     ↓
15  Validate / Mark Paid
     ↓
16  PDF / Send Payslips
     ↓
17  Payroll Dashboard
     ↓
18  PeoplePay360 Assistant
```

## What judges should see

### 1. Connected workflow

```text
Employee → Contract → Time → Compensation → Payroll
```

### 2. Payroll correctness

```text
Period
  ↓
Eligibility
  ↓
Warnings
  ↓
Processing
```

### 3. Security

```text
Authentication
  ↓
Role
  ↓
Permission
  ↓
Business Action
```

### 4. Scalability

```text
Redis Cache
+
Redis Queue
+
Background Workers
```

### 5. Operational visibility

```text
Payroll
  ↓
Dashboard
  ↓
KPIs + Trends + Alerts
```

---

# 🏆 Engineering Highlights

## 1. Employee-to-Payroll Continuity

Employee data is connected to contracts, schedules, attendance, Time Off, compensation and payroll.

## 2. Guided Payroll UX

Payroll creation is transformed from a generic record creation action into:

```text
Scope
→ Eligibility
→ Warning Context
→ Selection
→ Payrun
```

## 3. Period-Aware Contract Context

Payroll context is resolved against the selected payroll date/period rather than blindly using current configuration.

## 4. Warning-Driven Operations

The system surfaces missing or suspicious information before the payroll user completes the workflow.

## 5. Live Dashboard

Dashboard metrics are derived from operational records and combine HR and payroll context.

## 6. Async Processing

Real Frappe queue infrastructure keeps expensive payroll/attendance/email operations away from the interactive request where appropriate.

## 7. Open-Source Reuse

Mature HR, payroll, accounting, authentication, permission, print and background-job capabilities are reused instead of duplicated.

---

# ⚖️ Architecture Trade-Offs

## Why Frappe / ERPNext / HRMS?

### Advantages

- Mature HR domain model.
- Existing payroll engine.
- Accounting integration.
- Existing authentication and sessions.
- Existing permission system.
- Existing reporting.
- Existing PDF / print infrastructure.
- Existing background jobs.
- Existing realtime infrastructure.

### Trade-Off

PeoplePay360 remains coupled to the Frappe/ERPNext ecosystem.

### Decision

For a payroll-heavy application, reusing mature financial and HR infrastructure reduces implementation risk and lets the project focus on the differentiated product layer.

---

# ⚡ Latency Strategy

The interactive path should remain small.

```text
Request
  ↓
Permission / Validation
  ↓
Fast Read or Enqueue
  ↓
Immediate Response

Expensive Work
  ↓
Worker
```

Redis supports both sides:

```text
Redis Cache  → repeated read optimization
Redis Queue  → asynchronous processing
Redis Realtime → push-style communication
```

---

# 🧠 Correctness vs Performance

Payroll is a financial workflow.

Therefore:

```text
Correctness > Aggressive Caching
```

Redis must never become the permanent source of truth for payroll.

```text
MariaDB = Durable Business Data
Redis   = Temporary / Fast / Coordination Layer
```

---

# 📊 Performance Metrics

The following are recommended production measurements, not claims of measured benchmark results from the hackathon repository.

## Application

- API p50/p95/p99 latency.
- Request rate.
- Error rate.
- Dashboard latency.

## Payroll

- Employees processed per Payrun.
- Salary Slip generation duration.
- Payroll processing duration.
- Payslip delivery success rate.
- Warning count.
- Failed payroll count.

## Infrastructure

- Redis cache hit ratio.
- Queue depth.
- Worker utilization.
- Database query latency.
- Background job duration.
- Memory and CPU utilization.

### Example future SLO targets

| Metric | Example target |
|---|---:|
| Normal API p95 | < 300 ms |
| Dashboard p95 | < 1 s |
| Suitable cache hit ratio | > 80% |
| Background job success | > 99% |
| Payslip delivery success | > 99% |
| Critical availability | > 99.9% |

These are engineering targets for future production deployment, not measured results.

---

# 🧩 Requirement-to-Implementation Mapping

| Requirement | Current approach |
|---|---|
| Employee management | Frappe HRMS Employee foundation |
| Historical contracts | Employment Contract foundation + validation |
| Working schedules | HRMS scheduling/shift foundation |
| Attendance | HRMS attendance + check-in foundation |
| Time Off | Leave Types / Allocations / Applications |
| Salary structures | HRMS Salary Structure |
| Salary rules/components | HRMS Salary Component |
| Payrun | Payroll Entry + PeoplePay360 wizard |
| Employee selection | PeoplePay360 Payrun Wizard |
| Payroll warnings | PeoplePay360 validation/context layer |
| Payrun processing | PeoplePay360 Processing page + HRMS payroll |
| Payslips | Salary Slip + PeoplePay360 presentation |
| PDF | Frappe print/PDF infrastructure |
| Bulk email | Frappe asynchronous delivery infrastructure |
| Dashboard | PeoplePay360 payroll dashboard |
| Assistant | PeoplePay360 Assistant |
| Cache | Frappe/Redis cache |
| Background jobs | Redis-backed Frappe queues |
| Realtime | Frappe realtime + Redis |
| CI/CD | GitHub Actions |
| SQL foundation | Independent PostgreSQL layer |

---

# 🧭 Current vs Planned

## ✅ Current / Demonstrable

```text
✓ PeoplePay360 branding
✓ PeoplePay360 navigation/workspaces
✓ Employee / HR foundation
✓ Employment Contracts
✓ Working Schedules / shifts
✓ Attendance
✓ Time Off
✓ Salary Structures / Components
✓ Two-step Payrun Wizard
✓ Server-side eligibility lookup
✓ Contract-aware payroll context
✓ Payroll warning information
✓ Payrun Processing page
✓ Salary Slip workflow
✓ PeoplePay360 payslip presentation
✓ Bulk payslip email queueing
✓ Payroll Dashboard
✓ Payroll analytics / alerts
✓ PeoplePay360 Assistant
✓ Demo seed infrastructure
✓ Redis cache / queue / realtime infrastructure
✓ Docker environment
✓ GitHub Actions CI
✓ PostgreSQL foundation and SQL integrity tests
```

## 🚧 Planned / Future

```text
□ Advanced payroll readiness scoring
□ Advanced compliance validation
□ Full contract amendment workflow
□ Advanced salary calculation trace
□ Payroll anomaly detection
□ Payroll forecasting
□ Workforce cost forecasting
□ Advanced mobile polish
□ Cloudflare production edge
□ Nginx production reverse proxy
□ WAF / rate limiting
□ Prometheus / Grafana observability
□ Horizontal production scaling
□ Advanced load testing
□ PostgreSQL application integration if selected as an authoritative data layer
```

---

# 🛣️ Roadmap

## Phase 1 — Product Foundation

```text
✓ PeoplePay360 branding
✓ HR / Payroll foundation
✓ Payrun Wizard
✓ Payrun Processing
✓ Dashboard
✓ Assistant
✓ Demo environment
```

## Phase 2 — Payroll Correctness

```text
✓ Eligibility lookup
✓ Contract validation
✓ Duplicate checks
✓ Warning context

Future:
□ Advanced readiness scoring
□ Advanced compliance validation
```

## Phase 3 — Experience

```text
✓ Guided payroll workflow
✓ Custom payslip presentation
✓ Dashboard
✓ Assistant

Future:
□ Contract amendment workflow
□ Calculation trace
□ Mobile polish
```

## Phase 4 — Production Hardening

```text
□ Cloudflare
□ Nginx
□ WAF
□ Rate limiting
□ Horizontal scaling
□ Load testing
□ Observability
```

## Phase 5 — Intelligent Operations

```text
□ Payroll anomaly detection
□ Forecasting
□ Workforce cost intelligence
□ Advanced HR copilot capabilities
```

---

# 📚 Documentation Map

| File | Purpose |
|---|---|
| `main.md` | Problem statement, repository analysis and implementation analysis |
| `PeoplePay360 HR & Payroll.md` | Product brief and acceptance requirements |
| `PeoplePay360-ROADMAP.md` | Future enhancements and priorities |
| `database/README.md` | PostgreSQL foundation, pooling, migrations and tests |
| `SECURITY.md` | Security guidance |
| `docker/docker-compose.yml` | Main development infrastructure |
| `docker/init.sh` | Frappe / Redis environment initialization |
| `hrms/hooks.py` | Application registration, integrations and hooks |
| `hrms/payroll/page/payrun_wizard/` | Payrun Wizard |
| `hrms/payroll/page/payrun_processing/` | Payrun Processing |
| `hrms/payroll/page/payroll_dashboard/` | Payroll Dashboard |
| `hrms/peoplepay360/chatbot/` | Assistant |

---

# 🧠 Engineering Principles

## Data Integrity

Payroll decisions should use authoritative and validated records.

## Security by Default

Server-side permissions are the security boundary.

## Auditability

Historical payroll should remain understandable and reproducible.

## Idempotency

Repeated operations should not silently create duplicate financial results.

## Separation of Concerns

PeoplePay360 product logic belongs in the product layer; mature platform primitives remain reusable.

## Reuse Before Rebuild

Do not duplicate authentication, payroll calculation, leave arithmetic, accounting, PDF rendering or generic document lifecycle behavior without a proven requirement.

---

# 🚫 What Not to Do

- Do not create a second Employee master when the Frappe Employee model already satisfies the requirement.
- Do not create a second authentication system.
- Do not rely only on frontend filters for sensitive authorization.
- Do not overwrite historical contracts to represent new terms.
- Do not create a parallel salary formula engine unless the existing one is demonstrably insufficient.
- Do not treat Redis as the permanent payroll database.
- Do not mark payroll as paid merely because Salary Slips were generated.
- Do not use dashboard calculations with different period definitions from payroll.
- Do not commit real credentials or `.env` secrets.
- Do not describe planned Cloudflare/Nginx/observability infrastructure as already deployed.
- Do not describe the independent PostgreSQL foundation as the current Frappe runtime database.

---

# 🏆 Hackathon Evaluation Mapping

| Evaluation area | PeoplePay360 response |
|---|---|
| Problem understanding | Connected HR-to-payroll workflow |
| Functional depth | Employee + Contract + Time + Compensation + Payroll |
| UX | Guided Payrun Wizard + Processing page |
| Validation | Contract, salary, attendance and duplicate context |
| Security | Frappe authentication + RBAC + server-side permissions |
| Scalability | Redis cache, queue, workers and Docker topology |
| Analytics | Payroll Dashboard |
| Intelligence | PeoplePay360 Assistant |
| Testing | Frappe tests + Payrun Wizard tests + SQL foundation tests |
| DevOps | Docker + GitHub Actions |
| Extensibility | Frappe / ERPNext extension architecture |
| Demonstrability | Seed/demo workflow + continuous end-to-end scenario |

---

# 💎 Product USP

## Connected HR-to-Payroll Operations

```text
Employee
  ↓
Employment
  ↓
Time
  ↓
Compensation
  ↓
Payroll
  ↓
Payslip
  ↓
Insight
```

## Guided Payrun

```text
Scope
→ Eligibility
→ Warnings
→ Selection
→ Processing
→ Payslip
```

## Operational Visibility

```text
Payroll
  +
Attendance
  +
Time Off
  +
Contracts
  +
Employees
  ↓
Dashboard
```

## Scalable Infrastructure

```text
Frappe / Python
      │
 ┌────┼────┐
 ▼    ▼    ▼
DB  Redis Workers
```

---

# 📌 Final System Summary

```text
                         PEOPLEPAY360
                              │
                              ▼
                    CONNECTED HR OPERATIONS
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
       HR                  PAYROLL             INTELLIGENCE
        │                     │                     │
   Employee               Payrun                Assistant
   Contract               Eligibility           Context
   Schedule               Warnings               Role-aware
   Attendance             Processing
   Time Off               Payslip
                          Payment
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                         DASHBOARD
                              │
                     KPIs + Trends + Alerts
```

The overall architecture can be summarized in one sentence:

> **Frappe/Python handles HR and payroll business logic and permissions, MariaDB remains the durable operational source of truth, Redis accelerates suitable reads and coordinates asynchronous/realtime work, and the PeoplePay360 product layer provides the connected Payrun, validation, dashboard and assistant experience.**

---

# 📜 License

This repository follows the license included in:

```text
license.txt
```

The project builds on the Frappe / ERPNext / Frappe HR ecosystem; refer to the relevant upstream projects for their respective licenses and notices.

---

# 💚 PeoplePay360

<p align="center"><strong>Connect HR. Simplify Payroll. Improve Operational Visibility.</strong></p>

<p align="center">Employee → Contract → Time → Compensation → Payroll → Payslip → Insight</p>

<p align="center"><strong>Built as a product-focused HR & Payroll Operations Platform on an open-source ERP foundation.</strong></p>
