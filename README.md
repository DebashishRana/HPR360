# PeoplePay360 — HR & Payroll Operations Platform

> **An integrated HR and Payroll platform connecting employee management, contracts, attendance, time off, salary computation, payroll processing, payslips, and analytics into one operational workflow.**

---

## 📌 Overview

**PeoplePay360** is a unified HR and Payroll operations platform designed to connect the complete employee-to-payroll lifecycle.

Instead of treating employee records, contracts, attendance, leave, and payroll as isolated modules, PeoplePay360 connects them through a consistent business workflow:

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

The platform focuses on practical payroll requirements such as **period-aware contract selection, payroll validation, salary-rule sequencing, employee eligibility, duplicate detection, role-based access control, historical record preservation, and operational reporting**.

PeoplePay360 is implemented as a focused product layer on top of the existing **Frappe HR / ERPNext ecosystem**, allowing the project to reuse mature HR, payroll, permissions, document, reporting, and accounting infrastructure while concentrating custom development on the product-specific workflow and business rules.

---

# 🎯 Problems to be fixed 

HR and payroll operations are highly interconnected.

However, many basic HR systems represent employees, contracts, attendance, leave, and payroll as separate CRUD workflows. This can create operational and financial risks.

Typical problems include:

* Payroll using an incorrect contract for a selected period.
* Attendance exceptions remaining unresolved before payroll.
* Leave balances becoming difficult to audit.
* Salary calculations being difficult to trace.
* Unintended employees being included in a payroll batch.
* Missing employee or banking information being discovered too late.
* Duplicate payslips or payroll processing.
* Historical payroll information being overwritten.
* Unauthorized users accessing sensitive payroll information.

### Our Approach

PeoplePay360 connects these records into a single operational flow and validates important dependencies **before payroll is finalized**.

The objective is not simply to provide HR screens, but to make the relationships between HR data and payroll decisions explicit and reliable.

---

# 💡 Core Solution

PeoplePay360 provides an integrated workflow covering:

### Employee Management

* Employee profiles
* Employment information
* Department and manager
* Employee type and status
* Related contracts
* Related attendance
* Related time off
* Related payroll information

### Contract Management

* Historical contracts
* Effective dates
* Salary information
* Department/designation context
* Salary structure assignment
* Period-specific contract resolution
* Contract overlap detection

### Working Schedule & Attendance

* Working schedules
* Check-in / check-out
* Worked hours
* Attendance status
* Attendance corrections
* Attendance exceptions
* Payroll readiness checks

### Time Off

* Time Off Types
* Allocations
* Requests
* Approval/refusal workflow
* Leave balances
* Validity periods
* Approved leave consumption

### Payroll

* Salary Structures
* Salary Rules / Salary Components
* Payrun creation
* Employee selection
* Salary computation
* Payslip generation
* Validation
* Payment status
* PDF generation
* Bulk employee delivery

### Analytics

* Payroll KPIs
* Salary cost analysis
* Department-level salary insights
* Monthly payroll trends
* Attendance health
* Time-off insights
* Operational payroll warnings

---

# 🔄 End-to-End Workflow

PeoplePay360 is designed around a complete employee-to-payslip workflow.

```text
                    ┌──────────────┐
                    │   Employee   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
       ┌──────────────┐          ┌───────────────┐
       │   Contract   │          │ Work Schedule │
       └──────┬───────┘          └───────┬───────┘
              │                          │
              └────────────┬─────────────┘
                           ↓
                 ┌───────────────────┐
                 │ Attendance / Leave│
                 └─────────┬─────────┘
                           ↓
                ┌────────────────────┐
                │ Salary Configuration│
                └──────────┬─────────┘
                           ↓
                    ┌─────────────┐
                    │   Payrun    │
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │  Payslips   │
                    └──────┬──────┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           Validate      Payment     PDF/Email
                           │
                           ↓
                  ┌─────────────────┐
                  │ Payroll Dashboard│
                  └─────────────────┘
```

---

# 🧑‍💼 Employee Hub

The Employee record acts as the central operational hub.

From an employee, authorized users can access related:

* Contracts
* Working schedules
* Attendance
* Time Off
* Allocations
* Salary assignments
* Payslips

This provides a connected employee-centric experience instead of forcing users to search through unrelated modules.

---

# 📑 Contract Management

Contracts are treated as **historical, date-effective records**.

Payroll should use the contract applicable to the selected payroll period rather than simply selecting whichever contract happens to be marked active.

### Contract validation

PeoplePay360 is designed to validate:

```text
Payroll Period
      ↓
Find applicable contracts
      ↓
Check date overlap
      ↓
Check active status
      ↓
Resolve applicable contract
      ↓
Use contract for payroll
```

The system should:

* Preserve historical contracts.
* Detect overlapping active contracts.
* Prevent ambiguous contract resolution.
* Warn when no applicable contract exists.
* Display the applicable contract during payroll processing.

This reduces the risk of payroll being calculated using outdated employment terms.

---

# 🕐 Working Schedule & Attendance

PeoplePay360 connects employee schedules with attendance operations.

### Supported workflow

```text
Working Schedule
      ↓
Employee / Contract Assignment
      ↓
Check In
      ↓
Check Out
      ↓
Worked Hours
      ↓
Attendance Status
      ↓
Exception Review
      ↓
Payroll Readiness
```

Attendance can include:

* Check-in time
* Check-out time
* Worked hours
* Attendance status
* Missing check-outs
* Manual corrections
* Exceptions

Authorized users can review and correct attendance issues before payroll processing.

---

# 🌴 Time Off Management

Time Off follows a structured lifecycle:

```text
Time Off Type
      ↓
Allocation
      ↓
Employee Request
      ↓
Approval / Refusal
      ↓
Balance Update
      ↓
Payroll Context
```

The platform tracks:

* Allocated leave
* Taken leave
* Remaining balance
* Pending requests
* Validity periods
* Approval status

Approved requests consume the appropriate allocation according to the configured policy.

---

# 💰 Salary Structures & Salary Rules

Salary Structures define how payroll calculations are assembled.

Salary Rules / Salary Components can represent:

* Basic salary
* Allowances
* Contributions
* Gross salary
* Deductions
* Net salary

Rules are executed in a defined sequence so that dependent calculations can use previously calculated values.

Example:

```text
Basic Salary
      ↓
Allowances
      ↓
Gross Salary
      ↓
Contributions / Deductions
      ↓
Net Salary
```

The objective is to provide a **traceable salary calculation**, rather than relying on hardcoded payroll values.

---

# 🧾 Payrun Creation

PeoplePay360 uses a two-step Payrun creation flow.

## Step 1 — Define Scope

The payroll user selects the applicable:

* Payroll period
* Company
* Salary structure
* Department
* Employee type
* Other filters

## Step 2 — Select Employees

The system presents eligible employees together with relevant payroll context and warnings.

The user explicitly selects the employees who should enter the Payrun.

### Important design principle

The browser selection is **not trusted as the final authorization or eligibility check**.

The server revalidates:

* Employee eligibility
* Contract
* Salary configuration
* Duplicate payslip conditions
* Permissions
* Payroll-period constraints

Only after successful validation is the payroll batch created.

```text
Configure Payrun
       ↓
Find Eligible Employees
       ↓
Review Warnings
       ↓
Select Employees
       ↓
Server-side Validation
       ↓
Create Payrun
       ↓
Generate Payslips
```

---

# 📄 Payslips

Each payslip provides a structured salary breakdown.

### Payslip information

* Employee
* Payroll period
* Contract
* Salary structure
* Worked days
* Basic salary
* Allowances
* Contributions
* Gross salary
* Deductions
* Net salary
* Processing status

Users can review the calculation before finalizing the payroll.

---

# 📤 Payslip PDF & Delivery

PeoplePay360 supports the final employee delivery stage of payroll.

```text
Validated Payslip
       ↓
Generate PDF
       ↓
Employee Delivery
       ↓
Communication Status
```

The system can support:

* Individual payslip PDF generation
* Bulk payslip distribution
* Employee email validation
* Delivery status
* Visible delivery failures

---

# 📊 Payroll Dashboard

The Payroll Dashboard provides a consolidated view of HR and payroll operations.

## Key Performance Indicators

* Total Net Salary Paid
* Payslips Generated
* Average Salary
* Approved Time Off
* Attendance Health
* Payroll Warning Count

## Analytics

* Salary Cost by Department
* Monthly Net Salary Trends
* Gross-to-Net Composition
* Attendance Trends
* Leave Trends

## Operational Warnings

Potential payroll issues can be surfaced before finalization:

* Missing bank details
* Missing applicable contract
* Duplicate payslips
* Missing salary assignment
* Attendance exceptions
* Pending approvals
* Failed delivery

Dashboard calculations should use the same payroll-period definitions and permissions as the underlying payroll system.

---

# 🔐 Security & RBAC

Payroll data is highly sensitive.

PeoplePay360 uses role-based access control with server-side authorization.

| Role                   | Access                                                           |
| ---------------------- | ---------------------------------------------------------------- |
| **Employee**           | Own employee information, attendance and Time Off operations     |
| **HR Manager**         | Employees, Contracts, Working Schedules, Attendance and Time Off |
| **HR Payroll User**    | HR operations + Payruns and Payslips                             |
| **HR Payroll Manager** | Full HR & Payroll configuration                                  |
| **Admin**              | Complete system and user administration                          |

### Security principles

* Server-side permission enforcement
* Role-based access control
* Record-level access restrictions
* Protected payroll operations
* Employee-level data isolation
* Permission checks on server methods
* Restricted salary configuration
* Historical payroll preservation

### Example security scenarios

An Employee must not be able to access another employee's payslip simply by modifying a URL or API parameter.

An HR Payroll User may process payroll but should not be able to modify salary configuration unless explicitly authorized.

Frontend visibility is therefore treated as a **UX mechanism**, not a security boundary.

---

# 🏗️ System Architecture

PeoplePay360 follows an extension-oriented architecture rather than rebuilding an HR/payroll platform from scratch.

```text
┌─────────────────────────────────────────────┐
│                 User Layer                  │
│          Frappe Desk + Vue UI               │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│            PeoplePay360 Layer               │
│                                             │
│ Employee │ Contract │ Attendance │ Time Off │
│ Salary   │ Payrun   │ Payslip    │ Dashboard │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│             Frappe Framework               │
│                                             │
│ ORM │ Documents │ Permissions │ APIs        │
│ Workflows │ Background Jobs │ Reports       │
│ Print/PDF │ Sessions │ Realtime             │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│                  ERPNext                    │
│                                             │
│ Company │ Accounting │ Payments │ Journals  │
└──────────────────────┬──────────────────────┘
                       │
              ┌────────┴────────┐
              ↓                 ↓
       ┌─────────────┐    ┌─────────────┐
       │   MariaDB   │    │    Redis    │
       │ Persistence │    │ Cache/Queue │
       └─────────────┘    └─────────────┘
```

The repository architecture is based on Frappe Framework, ERPNext, Frappe HR/HRMS, Python, Frappe Desk, Vue, MariaDB, Redis and Docker/Frappe Bench.

---

# 🧱 Technology Stack

| Layer                 | Technology                    |
| --------------------- | ----------------------------- |
| Application Framework | Frappe Framework              |
| ERP Foundation        | ERPNext                       |
| HR & Payroll          | Frappe HR / HRMS              |
| Backend               | Python                        |
| Frontend              | Vue + Frappe Desk             |
| Database              | MariaDB                       |
| Cache / Queue         | Redis                         |
| Runtime               | Docker Compose + Frappe Bench |
| Reporting             | Frappe Reports / Dashboards   |
| PDF                   | Frappe Print Formats          |
| Authentication        | Frappe User / Session System  |

---

# ⚡ Performance & Scalability

PeoplePay360 is designed with performance-sensitive operations in mind.

## Redis

Redis can be used for:

* Frequently accessed reference data
* Dashboard caching
* Expensive report results
* Background job infrastructure
* Realtime application support

Cache invalidation should occur when the underlying source data changes.

## Background Jobs

Long-running operations should not unnecessarily block user requests.

Suitable background operations include:

* Bulk payslip generation
* PDF generation
* Bulk email delivery
* Heavy reporting
* Large data aggregation

## Database Efficiency

The architecture favors:

* Relational data integrity
* Server-side filtering
* Efficient aggregate queries
* Appropriate indexing
* Reuse of the existing ORM
* Avoidance of duplicate data models

## Idempotency

Payroll operations must be protected against accidental duplicate execution.

For example:

```text
Employee + Payroll Period + Payroll Scope
                  ↓
             Duplicate Check
                  ↓
        Generate Only When Valid
```

This is especially important for payroll and payment-related workflows.

---

# 🔒 Data Integrity

Payroll requires stronger consistency guarantees than a typical CRUD application.

PeoplePay360 therefore emphasizes:

### Contract Integrity

One deterministic contract should be resolved for the selected payroll period unless a documented split-contract policy applies.

### Payroll Integrity

Duplicate payslips should be detected before finalization.

### Historical Integrity

Historical contracts and finalized payroll records should not be casually overwritten or deleted.

### Calculation Integrity

Salary components should execute in a deterministic order.

### Referential Integrity

Core relationships must remain intact:

```text
Employee
 ├── Contract
 ├── Schedule
 ├── Attendance
 ├── Time Off
 ├── Salary Assignment
 └── Payslip
        └── Payrun
```

---

# 🔁 Payroll State Management

A Payrun follows an explicit lifecycle.

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

Cancellation or correction paths are handled according to the underlying Frappe/ERPNext document lifecycle.

Actions such as **Compute, Validate, Mark Paid, Send and Print** should respect the current state and user permissions.

---

# 🧠 Engineering Principles

## 1. Data Integrity

Payroll decisions are validated against authoritative server-side records.

## 2. Security

Authorization is enforced at the server/API layer and is not dependent only on frontend visibility.

## 3. Auditability

Historical contracts and payroll records are preserved through the platform's document lifecycle.

## 4. Idempotency

Payroll generation and related operations should not create duplicate results when repeated.

## 5. Separation of Concerns

The product layer owns PeoplePay360-specific workflows while the underlying platform provides mature HR/payroll infrastructure.

## 6. Reuse Before Rebuild

Existing employee, leave, salary, payroll, accounting, PDF, permission, and background-job infrastructure is reused wherever it satisfies the requirement.

---

# 🧩 Why Frappe HR / ERPNext?

Payroll is a high-risk domain.

Rebuilding authentication, document lifecycle, payroll calculations, leave arithmetic, permissions, PDF rendering, accounting integration, and background processing from scratch would significantly increase:

* Development effort
* Testing requirements
* Security risk
* Maintenance burden
* Data consistency risks

PeoplePay360 instead uses the open-source platform as the operational foundation and concentrates custom engineering on the requirements that differentiate the product.

This includes:

* Employee-centric workflow
* Period-specific contract resolution
* Two-step Payrun creation
* Payroll readiness warnings
* Product-specific permissions
* Dashboard metrics
* Payslip presentation
* End-to-end validation

This extension-oriented approach is explicitly recommended by the project's architecture analysis.

---

# 🧪 Testing Strategy

Testing focuses on business rules that directly affect payroll correctness.

## Unit Tests

Examples include:

* Contract date intersection
* Contract overlap detection
* Contract-period resolution
* Weekly-hours calculation
* Attendance exception classification
* Leave balance consumption
* Leave restoration
* Salary-rule ordering
* Formula dependencies
* Duplicate payslip detection
* Dashboard aggregation

## Integration Tests

Critical flows include:

```text
Employee
   ↓
Contract
   ↓
Salary Assignment
   ↓
Payrun
   ↓
Salary Slip
```

and:

```text
Leave Allocation
   ↓
Leave Application
   ↓
Approval
   ↓
Balance Update
```

and:

```text
Salary Slip
   ↓
PDF
   ↓
Employee Delivery
```

## Permission Tests

Each role should be tested against sensitive objects and actions.

A successful UI test alone is not sufficient if an unauthorized API request can still access the same information.

---

# 🧪 Representative Acceptance Scenario

A representative payroll scenario can contain two employees:

### Employee A

* Has a contract ending during the payroll timeline.
* Has a replacement contract beginning afterward.

### Employee B

* Has an unresolved attendance exception.
* Has missing banking information.

When both employees are selected for payroll, the system should:

1. Resolve the applicable contract for Employee A.
2. Surface Employee B's warnings.
3. Prevent finalization when blocking warnings exist.
4. Generate auditable salary calculations after correction.
5. Generate a payslip PDF matching the calculated values.
6. Send payslips only where valid employee delivery information exists.
7. Reflect the completed payroll in dashboard metrics.

This scenario tests the most important business relationships rather than simply demonstrating static UI screens.

---

# 📁 Project Structure

The repository's main implementation areas include:

```text
hrms/
├── hr/
│   ├── doctype/
│   └── report/
│
├── payroll/
│   ├── doctype/
│   ├── page/
│   │   └── payrun_processing/
│   ├── workspace/
│   └── payroll_dashboard/
│
├── hooks.py
└── modules.txt

frontend/
└── src/
    ├── views/
    │   ├── attendance/
    │   └── salary_slip/
    └── router/
```

Important existing areas include the HR/Payroll DocTypes, payroll processing page, payroll workspace/dashboard, attendance views, salary-slip views, application hooks and module configuration.

---

# 🚀 Getting Started

> The exact commands may vary depending on the repository's current development environment. The project uses the Frappe Bench / Docker-based development architecture described above.

### Prerequisites

* Docker
* Docker Compose
* Git
* A supported Frappe/ERPNext development environment

### Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Start the development environment

Use the repository's configured Docker/Frappe Bench startup procedure.

After the services are running, access the configured Frappe site through the development URL provided by the environment.

### Initial Configuration

Configure representative:

* Company
* Departments
* Employee types
* Working schedules
* Time Off types
* Salary components
* Salary structures
* Employees
* Contracts
* Salary assignments

Then execute the complete Employee → Payroll workflow.

---

# 🎬 Hackathon Demo Flow

The recommended five-minute demonstration focuses on one connected business scenario.

```text
01  Employee
      ↓
02  Contract + Working Schedule
      ↓
03  Attendance
      ↓
04  Time Off
      ↓
05  Payrun Wizard
      ↓
06  Eligible Employees + Warnings
      ↓
07  Employee Selection
      ↓
08  Salary Computation
      ↓
09  Payslip Review
      ↓
10  Validate Payrun
      ↓
11  Mark Paid
      ↓
12  Generate Payslip PDF
      ↓
13  Send Payslip
      ↓
14  Payroll Dashboard
```

The objective is to demonstrate **business continuity across modules**, not merely individual screens.

---

# ⭐ Engineering Highlights

| Area                 | PeoplePay360 Approach                                   |
| -------------------- | ------------------------------------------------------- |
| Payroll              | Period-aware processing                                 |
| Contracts            | Historical + date-effective                             |
| Payrun               | Two-step employee selection                             |
| Validation           | Server-side revalidation                                |
| Salary               | Ordered rule/component calculation                      |
| Attendance           | Exception-aware                                         |
| Leave                | Allocation → request → approval → balance               |
| Security             | Role + record-level permissions                         |
| Duplicate Protection | Idempotency / duplicate validation                      |
| Reporting            | Cross-module payroll analytics                          |
| PDF                  | Framework print infrastructure                          |
| Background Work      | Redis-backed job infrastructure                         |
| Architecture         | Extension over mature open-source HR/payroll foundation |

---

# 🗺️ Roadmap

## Phase 1 — Foundation

* Verify existing HR and payroll workflows
* Configure representative data
* Validate the employee-to-payroll flow

## Phase 2 — Business Logic

* Period-specific contract resolution
* Contract overlap validation
* Attendance readiness rules
* Leave integration
* Salary-rule validation

## Phase 3 — PeoplePay360 Experience

* Two-step Payrun wizard
* Employee hub
* Payroll warning system
* Processing workflow

## Phase 4 — Analytics & Delivery

* Payroll dashboard
* Reports
* Payslip print format
* Bulk delivery

## Phase 5 — Hardening

* Automated tests
* Permission testing
* Integration testing
* Migration and recovery testing

---

# 🔮 Future Enhancements

Potential extensions include:

* Employee self-service portal
* Advanced payroll forecasting
* Payroll anomaly detection
* Advanced attendance analytics
* Payroll cost forecasting
* Configurable approval workflows
* Multi-company analytics
* Automated compliance reporting
* Intelligent HR insights
* Advanced notifications and workflow automation

These are roadmap items and should not be considered part of the current implementation unless explicitly completed.

---

# 🏆 Project Vision

PeoplePay360 is built around a simple principle:

> **Connect HR decisions to payroll outcomes.**

An employee is not just a record.

Their:

**contract → schedule → attendance → leave → salary configuration → payroll → payslip**

must form a consistent operational chain.

By extending a mature open-source HR/payroll foundation instead of duplicating it, PeoplePay360 focuses engineering effort where it creates the most value:

**Payroll correctness · Data integrity · Security · Scalability · Auditability · User experience**

---

# 📜 License

This project is developed as a hackathon implementation on top of the applicable open-source Frappe, ERPNext and Frappe HR ecosystem.

Refer to the upstream project licenses and repository license files for applicable licensing terms.

---

# 👥 Team

**PeoplePay360 — HR & Payroll**

Built for the hackathon with a focus on:

**Business Logic · System Design · Security · Scalability · User Experience**

---
