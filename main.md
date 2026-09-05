## PeoplePay360: HR & Payroll

An Integrated Human Resource and Payroll Operations Platform

This hackathon project is an HR and Payroll platform called “HR & Payrollˮ, designed to

handle:

- information, and employment history Complete employee management including employee profiles, contracts, salary

- hours and attendance corrections Attendance and working schedule management with check-in, check-out, worked

- Time off management covering leave requests, approvals, allocations, leave balances, and configurable time off types

- warnings, validation, payment status, and payroll history Payroll processing through Payruns and Payslips, including salary computation,

- allowances, deductions, contributions, and final net salary Configurable Salary Structures and Salary Rules for calculating earnings,

- Payslip PDF generation, bulk employee email delivery, and a Payroll Dashboard that combines employee, attendance, leave, contract, and payroll information

Many basic HR tools store employee details, attendance, leave, and salary data as

separate records. Real HR and payroll teams need these records to work together. An

employee may have multiple contracts over time, but payroll must use the contract that

applies to the payroll period. Working hours come from an assigned schedule, attendance

contains exceptions that may need review, leave balances depend on allocations and

approved requests, and payroll must transform all of that into understandable payslips

before payment.


The goal of this project is to build an HR and Payroll platform that goes beyond simple

employee CRUD screens and becomes a connected operational flow. The Employee

record acts as the central hub, related Contracts and Working Schedules provide payroll

context, Attendance and Time Off capture day-to-day HR activity, Salary Structures and

Rules define salary computation, and Payruns turn eligible employee records into

validated payslips that can be printed as PDF and sent to employees.

Teams are free to use any programming language, framework, or database technology to

build this solution. The focus is on the business logic, data relationships, payroll

calculation flow, and end-to-end user experience, not on any specific platform or vendor.

## Main Goal

Develop an integrated HR and payroll platform managing the full employee lifecycle-from

master data and time tracking to payroll calculation and reporting.

## Key Outcomes

- Contracts, Attendance, and Time Off. Unified HR Flow: Centralized employee records with seamless navigation to

- only the active, period-specific contract. Contract Management: Maintain historical records while ensuring payroll uses

- Operational Tracking: Implement flexible Working Schedules, attendance tracking (with exception handling), and comprehensive Time Off (requests/allocations).

- Allowances, Deductions) and validation warnings. Payroll Processing: Enable a two-step pay run workflow: select scope/period, then select employees. Generate payslips with clear breakdowns (Basic,

- Reporting: A centralized Payroll Dashboard aggregating HR/Payroll data across Periods, Departments, and Employee types.


## Employee

- View own employee details, attendance records, and leave balances

- administration access Create attendance entries and Time Off Requests, with no payroll or HR

## HR Manager

- Time Off modules Full CRUD access to Employees, Attendance, Contracts, Working Schedules, and

- Approve or refuse Time Off Requests, with no access to payroll features

## HR Payroll User

- Payslips All HR Manager permissions plus Create, Read, and Update access to Payruns and

- Read-only access to Salary Structures and Salary Rules

## HR Payroll Manager

- Structures, and Salary Rules. All HR Payroll User permissions with full CRUD access to Payruns, Payslips, Salary

- Full control over HR and payroll-related records and configurations

## Admin

- Full access to all modules and models across the platform

- administration User management, role assignment, permission updates, and complete system


## A) HR Backend (Configuration & Master Data Area)

## A1) Employee Master Management

- Support Kanban, List, and Form views for employee records.

- and status on the employee form. Capture essential work details like department, manager, schedule, job position,

- view related Contracts, Attendance, and Time Off records. Provide quick list-view access and direct links from the employee form to filter and

## A2) Contract Management

- Maintain historical contract records linked to employees to track changes over time.

- highlighting the active contract. List view must display key contract details like dates, wages, and status, clearly

- position, wage, and salary structure. Contract forms should capture employment terms including duration, department,

- Ensure payroll processes only the contract applicable to the selected period, avoiding concurrent active contracts.

## A3) Working Schedule Setup

- like name, type, and weekly hours. Implement List and Form views for scheduling; list view should show key metrics

- Form view defines the weekly pattern using Day, Start Time, End Time, and Break.

- entering them manually. Calculate total weekly hours automatically from the defined schedule rather than

- and payroll expectations. Assign working schedules to employees or contracts to standardize attendance

## A4) Time Off Type & Allocation Setup


- configured Time Off Types. Time Off is accessible via the main navigation, housing Requests, Allocations, and

- requirements, approval workflows, and payroll integration. Time Off Types define leave policies including units (days/hours), allocation

- tracking detailed metrics like taken, remaining, and validity periods. Allocations manage employee balances, requiring approval before availability, and

- balances are accurately consumed and transparently linked. Approved leave requests automatically deduct from assigned allocations, ensuring

## A5) Salary Structure Setup

- as a "Regular Salary" structure. Salary Structures act as containers for organized collections of Salary Rules, such

- number of rules, employees, and active status. Structures require List and Form views to display associated details like the

- The form view manages included salary rules and their execution sequence.

- calculate employee payslips. Selected structures on a Payrun dictate the specific set of rules applied to

## A6) Salary Rule Setup

- Form views to manage attributes like Name, Code, Category, and Sequence. Salary Rules define how earnings and deductions are calculated, utilizing List and

- Categories allow for the clear distinction of salary components, including Basic, Allowances, Gross, Deductions, and Net salary.

- respected, allowing complex totals to build upon earlier calculations. Rules are processed in a specific sequence to ensure dependencies are

- formulas-drive the actual salary calculations visible on final payslips. Flexible computation methods-including fixed amounts, percentages, and

## A7) Reporting & Dashboard Configuration

- live metrics derived from actual system records. The Payroll Dashboard integrates data from HR and Payroll modules, displaying


- attendance, and leave patterns across specific timeframes or business units. Flexible filtering by Period and Department allows users to analyze salary costs,

- Employee Type filters enable focused analysis, restricting dashboard data to specific groups like full-time or contract staff.

## B) HR & Payroll Frontend (Operational Experience)

## B1) Main Navigation & Employee Views

- Reports Top navigation exposes Employees, Contracts, Attendance, Time Off, Payroll, and

- Employee Form acting as the operational hub Employees can be accessed via Kanban or List views, both leading to a unified

## B2) Employee Form & Related Record Navigation

- status Employee Form displays identity, role, department, manager, schedule, and active

- Smart-button actions display counts and open filtered views for related Contracts, Attendance, Time Off, and Allocations

## B3) Attendance List & Form

- Employee Form Attendance is accessible globally from the main menu or directly from an individual

- of entries and exceptions List view displays Check In, Check Out, Worked Hours, and Status for quick review

- restricted to authorized users Attendance Form provides detailed records and supports manual corrections

- Attendance data remains available for reporting and Payroll Dashboard insights

## B4) Time Off Requests

- Requests are accessed exclusively via Time Off → Requests in the top navigation


- Request List provides an overview of Employee, Type, Dates, Duration, and Status

- workflow Request Form details the request and supports a simple approval or refusal

- allocation Approved requests automatically reduce balances for leave types requiring

## B5) Payrun Creation Wizard

- Clicking NEW launches a setup wizard instead of immediately creating a record

- Step 1 defines scope including Salary Structure, and Period

- Clicking Continue moves to employee selection without creating the Payrun

- Step 2 filters eligible staff for explicit user selection

- the processing view Create Payrun initializes the batch containing only selected employees and opens

## B6) Payrun Processing Screen

- Payruns group generated Payslips for a specific payroll period

- Payslips Payrun Form provides processing actions: Compute, Validate, Mark Paid, and Send

- Displays run name, structure, period, status, and summary list of payslips

- finalization Highlights warnings such as missing bank details or duplicate payslips prior to

- Preserves finalized or paid payroll batches as historical records

## B7) Payslip & Salary Computation Screen

- view Payslips can be accessed via parent Payruns or from the dedicated Payslips list

- and Worked Days Displays key identification attributes: Employee, Structure, Pay Run, Period, Status,

- Allowances, Deductions, Gross, and Net amounts Salary Computation section details individual rule breakdowns including Basic,


- Payrun's assigned Salary Structure Computation logic automatically uses the applicable period contract alongside the

## B8) Payslip PDF & Employee Delivery

- Print Payslip action generates a printable PDF document for individual employees

- Parent Payrun includes a Send Payslips action for bulk email distribution

## B9) Payroll Dashboard

The Payroll Dashboard should help Payroll and HR users understand payments, staffing

impact, leave patterns, attendance quality, and payroll warnings for the selected filters.

- Average Salary, Approved Time Off, and Attendance Health KPI cards display key metrics like Total Net Salary Paid, Payslips Generated,

- historical data Charts plot Salary Cost by Department and Monthly Net Salary Trends using

- Operational alerts surface payroll statuses, missing required information, duplicate payslips, and contract attention items

---

# PeoplePay360: Implementation and Open-Source Architecture Analysis

## 1. Purpose of This Document

This document converts the PeoplePay360 product brief above into an implementation analysis for the current repository. It answers five questions:

1. What problem is the application solving?
2. How does the existing open-source Frappe HR solution solve that problem?
3. Which requested capabilities already exist in the repository?
4. Which capabilities should be implemented or customized by the PeoplePay360 team?
5. Why is extending the existing open-source solution preferable to rebuilding the platform from scratch?

The repository is not an empty HR application. It is a Frappe HR application built on the Frappe Framework and integrated with ERPNext. The correct strategy is therefore to preserve the framework's document, permission, workflow, reporting, background-job, accounting, and print infrastructure while adding the PeoplePay360-specific product experience and business rules.

## 2. Executive Summary

### 2.1 Current baseline

The codebase already provides a broad HR and payroll foundation:

- Employee master data and employee lifecycle records.
- Employment contracts and employee-specific context.
- Working schedules, shifts, check-ins, attendance, and attendance reports.
- Leave types, leave allocations, leave applications, approval flow, and leave balance reporting.
- Salary structures, salary components, salary assignments, salary slips, payroll entries, payroll periods, and payroll reports.
- Print formats and PDF-capable document rendering through Frappe.
- Payroll dashboards, charts, number cards, workspaces, and reports.
- Vue-based operational screens for attendance and salary slips.
- Role-based access control and server-side permission enforcement through Frappe.
- Integration points for Employee, User, Company, Payment Entry, Journal Entry, Loan, Holiday List, and accounting workflows.

### 2.2 Main product gap

The brief describes a simplified domain model with:

- `Payrun` as the payroll batch.
- `Salary Rule` as the formula-bearing payroll component.
- A two-step Payrun creation wizard.
- A payroll dashboard with filters and operational warnings.

The open-source baseline uses Frappe and ERPNext terminology and models that are similar but not identical:

- `Payroll Entry` is the closest baseline equivalent to `Payrun`.
- `Salary Slip` is the generated employee-level payroll result.
- `Salary Structure` groups payroll components.
- `Salary Component` is the closest baseline equivalent to `Salary Rule`.
- `Employee Checkin`, `Attendance`, `Shift Type`, `Shift Assignment`, and related records provide attendance and scheduling behavior.
- `Leave Application`, `Leave Allocation`, and leave-type configuration provide Time Off behavior.

This difference should be handled by a compatibility layer and product UI, not by duplicating payroll calculation logic. PeoplePay360 can display product language such as Payrun and Salary Rule while using the mature underlying Frappe/ERPNext documents where their behavior already satisfies the requirement.

### 2.3 Recommended implementation position

Use the repository as the operational core and implement the project-specific layer in the HRMS app:

1. Reuse standard Employee, Contract, attendance, leave, Salary Structure, Salary Component, Salary Slip, and Payroll Entry behavior.
2. Add a PeoplePay360 naming and navigation layer for Payrun and Salary Rule where the brief requires those terms.
3. Add missing validation rules, especially period-specific contract selection and duplicate active contract prevention.
4. Build the two-step payroll creation experience without creating a partial payroll record before employee selection is complete.
5. Add a dashboard query layer that combines payroll, attendance, leave, employee, and contract data.
6. Add focused tests for the business rules that distinguish PeoplePay360 from the generic open-source baseline.

## 3. Problem Statement

### 3.1 Business problem

HR and payroll data is operationally connected, but many basic applications represent it as disconnected CRUD screens. That creates risks such as:

- Payroll using the wrong contract when an employee changes terms during a pay period.
- Attendance corrections not being visible to payroll users.
- Leave balances being shown without a transparent relationship to allocations and approved leave.
- Salary formulas being difficult to audit because the calculation sequence is hidden.
- Payroll batches being generated for unintended employees.
- Missing bank, contract, schedule, or employee data being discovered after payroll finalization.
- Historical payroll records being overwritten instead of preserved as auditable records.
- Managers seeing payroll information they should not access.

### 3.2 Product problem to solve

PeoplePay360 must provide one connected flow:

```text
Employee
	-> Contract and Working Schedule
	-> Attendance and Time Off
	-> Salary Structure and Salary Components
	-> Payrun / Payroll Entry
	-> Payslips / Salary Slips
	-> Validation, Payment, PDF, Email, Dashboard
```

The central design requirement is not merely that these records exist. The application must enforce the relationships and make them visible to the user at the point where a decision is made.

### 3.3 Success criteria

The implementation is successful when a payroll user can:

1. Identify eligible employees for a selected payroll period.
2. See which contract and salary configuration will be applied to each employee.
3. Review attendance and approved leave inputs.
4. Create a payroll batch only for explicitly selected employees.
5. Compute payslips with a traceable component breakdown.
6. See warnings before finalization.
7. Validate, mark paid, print, and send payslips.
8. Reopen historical payroll records without changing their historical meaning.
9. Do all of this within role-specific permissions.

## 4. Existing Open-Source Architecture

### 4.1 Technology layers

The repository uses the following architecture:

| Layer | Existing technology | Responsibility |
|---|---|---|
| Application framework | Frappe Framework | Documents, ORM, APIs, permissions, workflows, background jobs, files, sessions, print rendering |
| ERP foundation | ERPNext | Company, accounting, payment, employee integration, financial posting, shared master data |
| HR application | Frappe HR / `hrms` | Employee lifecycle, leave, attendance, payroll, recruitment, performance, expenses, tax, tenure |
| Backend language | Python | Business rules, DocType controllers, hooks, reports, APIs, patches, scheduled work |
| Desk interface | Frappe Desk | List, form, report, workspace, dashboard, role-aware navigation |
| Operational frontend | Vue | Modern employee, attendance, request, and salary-slip experiences |
| Database | MariaDB in the Docker setup | Persistent document and accounting data |
| Cache and queues | Redis | Cache, background jobs, realtime support |
| Development runtime | Docker Compose and Frappe Bench | Reproducible local application environment |

### 4.2 Application registration and integration

The application metadata and integration contract are declared in `hrms/hooks.py`. Important existing integration points include:

- `required_apps = ["frappe/erpnext"]`, which establishes ERPNext as a dependency.
- `app_home = "/desk/hr-setup"`, which provides the HR application entry point.
- `app_include_js` and `app_include_css`, which load the HRMS desk assets.
- `doctype_js` entries that extend standard ERPNext documents such as Employee, Company, Timesheet, Payment Entry, Journal Entry, and Bank Transaction.
- `override_doctype_class` entries that extend Employee, Timesheet, Payment Entry, and Project behavior without forking the framework.
- `doc_events` handlers that connect HR behavior to User, Company, Holiday List, Timesheet, Payment Entry, Journal Entry, Loan, and Employee lifecycle events.
- `after_install`, `after_migrate`, `before_uninstall`, and application enable/disable hooks for installation and lifecycle management.

This hook architecture is the main reason the PeoplePay360 implementation should extend existing documents instead of introducing a parallel database and authentication system.

### 4.3 Domain modules already present

The repository declares these modules in `hrms/modules.txt`:

- HR Setup
- Tenure
- Recruitment
- Shift and Attendance
- Leaves
- Expenses
- Performance
- Payroll
- Tax and Benefits
- HR

These modules represent a much wider product surface than the minimum hackathon scope. PeoplePay360 can initially expose only the relevant HR and payroll navigation while keeping the broader platform available for future lifecycle features.

## 5. Requirement-to-Repository Mapping

### 5.1 Employee master

**Brief requirement:** Employee records act as the central hub and expose identity, employment, department, manager, schedule, status, and related records.

**Existing solution:** The application extends the standard Employee document through `hrms.overrides.employee_master.EmployeeMaster` and registers Employee-specific client behavior in `hrms/hooks.py`. Employee is therefore already a shared integration point between HRMS and ERPNext.

**Reuse decision:** Reuse the standard Employee document and add PeoplePay360-specific related-record actions, indicators, and validation where needed.

**PeoplePay360 work:**

- Confirm that the required fields are visible in the chosen employee form.
- Add or configure related-record buttons for Contracts, Attendance, Time Off, Allocations, Salary Structure Assignment, and Salary Slips.
- Add an employee status and eligibility summary that is safe for the current user role.
- Add list, form, and Kanban configuration only if the existing Employee views do not meet the product demonstration requirements.

### 5.2 Contracts

**Brief requirement:** Maintain historical contracts and use only the contract applicable to the selected payroll period.

**Existing solution:** Contract records are part of the Frappe HR/ERPNext employee model and can be linked to employees, dates, wages, departments, designations, and salary configuration.

**Reuse decision:** Reuse Contract records and add explicit PeoplePay360 validation around date overlap, active status, and payroll-period resolution.

**PeoplePay360 work:**

- Define the contract-selection function with inclusive period rules.
- Reject or warn on overlapping active contracts for the same employee.
- Require exactly one applicable contract before payroll computation, unless a documented split-contract policy exists.
- Display the selected contract on the Payrun employee selection and payslip review screens.
- Preserve historical contracts and never replace an old contract merely to update current terms.

### 5.3 Working schedules and attendance

**Brief requirement:** Configure weekly schedules, calculate weekly hours, assign schedules, capture check-in/check-out, and support corrections and exceptions.

**Existing solution:** The repository contains the Shift and Attendance module, including working schedule and attendance DocType areas. The frontend router exposes attendance request, shift request, shift assignment, and employee check-in views. Reports include monthly attendance, shift attendance, and employees working on a holiday.

**Reuse decision:** Reuse the scheduling, check-in, attendance, and reporting model. Add a focused operational experience for exception review and payroll readiness.

**PeoplePay360 work:**

- Confirm whether `Working Schedule` or the current shift model is the authoritative schedule object for this product.
- Calculate and display weekly scheduled hours from child rows rather than relying on manual totals.
- Define how overnight shifts, breaks, holidays, missing check-outs, and manual corrections are handled.
- Add payroll readiness flags for unapproved or incomplete attendance.
- Link attendance exceptions to the employee and the relevant payroll period.

### 5.4 Time Off

**Brief requirement:** Provide Time Off Types, Allocations, Requests, approval/refusal, balances, validity, and automatic consumption.

**Existing solution:** The HR module includes leave applications, leave allocations, leave balance reporting, calendars, and leave-related workflows. The application declares a Leave Application calendar and includes an Employee Leave Balance Summary report.

**Reuse decision:** Reuse Leave Type, Leave Allocation, and Leave Application behavior, with product terminology and workflow configuration layered on top.

**PeoplePay360 work:**

- Present the navigation as `Time Off` if that is the product language, while preserving the underlying model names where compatibility matters.
- Verify that allocation approval is required before balance consumption.
- Verify that approved requests consume the correct allocation and that cancellation restores balance as expected.
- Expose remaining, taken, validity, and pending values in the employee and payroll views.
- Add payroll treatment for paid leave, unpaid leave, and leave-based salary deductions if the selected policy requires it.

### 5.5 Salary structures and salary rules

**Brief requirement:** Configure a salary structure containing ordered rules for basic pay, allowances, contributions, gross, deductions, and net salary.

**Existing solution:** Payroll contains Salary Structure, Salary Component, Salary Structure Assignment, Salary Detail, and Salary Slip areas. Salary Component is the closest existing equivalent to a Salary Rule, and Salary Structure provides the ordered collection and calculation context.

**Reuse decision:** Reuse Salary Structure and Salary Component calculation behavior. Use a PeoplePay360 display label or compatibility view for `Salary Rule` rather than creating a second formula engine.

**PeoplePay360 work:**

- Define the permitted component categories and their ordering.
- Verify fixed amount, percentage, formula, and dependency behavior for the required demo cases.
- Add validation for duplicate component codes and invalid formula references.
- Show the calculation trace on the payslip review screen.
- Restrict structural changes by role and preserve the structure used by historical salary slips.

### 5.6 Payrun and payslips

**Brief requirement:** Select period and scope, select employees, generate payslips, compute, validate, mark paid, send, and preserve history.

**Existing solution:** Payroll contains Payroll Entry, Payroll Employee Detail, Salary Slip, Payroll Period, Payroll Correction, and a Payrun Processing page area. The baseline also includes salary registers and payroll dashboards.

**Reuse decision:** Treat Payroll Entry as the underlying Payrun implementation unless a demonstrated requirement cannot be represented by it. Reuse Salary Slip as the employee-level result.

**PeoplePay360 work:**

- Build or complete a two-step creation wizard.
- Make employee selection explicit and auditable.
- Resolve the contract and salary assignment for every selected employee before creation.
- Prevent duplicate payslips for the same employee, period, and payroll scope.
- Provide warning severity levels: blocking, review required, and informational.
- Keep state transitions explicit: Draft, Computed, Validated, Paid, Sent, Cancelled where supported by the underlying document model.
- Add a summary of gross, deductions, net, employee count, and warning count.

### 5.7 Payroll dashboard and reporting

**Brief requirement:** Aggregate payroll, employee, contract, attendance, and leave data with period, department, and employee-type filters.

**Existing solution:** The Payroll workspace defines charts and number cards such as outgoing salary, total salary structure, and incentives. The Payroll dashboard defines cards for declaration, salary structure, incentives, and outgoing salary, plus outgoing salary, designation salary, and department salary charts. HR and payroll reports cover attendance, leave balances, salary registers, and tax deductions.

**Reuse decision:** Reuse workspace, dashboard, number-card, chart, and report infrastructure. Add PeoplePay360-specific cards and queries instead of building a separate analytics frontend first.

**PeoplePay360 work:**

- Add filters for payroll period, department, employee type, and status.
- Add KPI cards for total net salary paid, payslips generated, average salary, approved time off, and attendance health.
- Add charts for salary cost by department and monthly net salary trends.
- Add operational warning lists for missing bank details, missing contract, duplicate payroll, unapproved attendance, and incomplete employee data.
- Ensure every metric is permission-filtered and uses the same period boundaries as payroll calculation.

## 6. Open-Source Solution Versus Custom Implementation

### 6.1 Capability matrix

| Capability | Open-source baseline | PeoplePay360 implementation decision | Justification |
|---|---|---|---|
| Employee master | Existing Employee document and HR extensions | Reuse and customize views | Employee is already integrated with ERPNext and HR lifecycle events |
| Historical contracts | Existing Contract model | Reuse plus period validation | Avoid duplicate employment history and payroll context |
| Working schedules | Existing HR/shift scheduling model | Reuse plus weekly-hours presentation | Scheduling already connects to attendance and shifts |
| Check-in/check-out | Employee Checkin and attendance frontend | Reuse plus exception review | Existing realtime and operational paths reduce implementation risk |
| Attendance | Attendance DocType and reports | Reuse plus payroll readiness | Existing reports and validation can be extended |
| Time Off types | Leave Type configuration | Reuse with product labels | Mature balance and policy behavior already exists |
| Allocations | Leave Allocation | Reuse and configure approvals | Avoid reimplementing balance arithmetic |
| Requests | Leave Application | Reuse and configure approval/refusal | Existing leave workflow is a close match |
| Salary rules | Salary Component | Reuse as compatibility model | Existing formulas, categories, and dependencies are safer than a new engine |
| Salary structures | Salary Structure | Reuse and extend summaries | Existing assignment and payslip integration is valuable |
| Payrun | Payroll Entry and processing page | Extend or wrap as Payrun | The business concept matches, but product flow and naming differ |
| Payslip | Salary Slip | Reuse and customize print/review | It is the stable employee payroll result |
| PDF | Frappe print formats and PDF rendering | Reuse and add PeoplePay360 format | Avoid custom document rendering and email attachment code |
| Bulk email | Existing Frappe/ERPNext communication facilities | Configure and validate | Reuse queueing, templates, and audit trail |
| Dashboard | Workspace, dashboard, charts, number cards | Extend with PeoplePay360 metrics | Existing dashboard infrastructure supports filters and permissions |
| Roles | Frappe Role and DocType permissions | Configure and add custom role rules | Server-side permissions are already part of the platform |
| Database | MariaDB/Frappe ORM | Reuse | Keeps document links, migrations, and accounting consistency |
| Authentication | Frappe User/session system | Reuse | Avoid building a second identity and authorization system |

### 6.2 What must be implemented by us

The PeoplePay360 team should own the requirements that express the product's differentiating behavior:

1. The two-step Payrun creation UX.
2. Payrun terminology and navigation where user research requires it.
3. Contract selection by payroll period.
4. Duplicate and overlap validations specific to the product.
5. Payroll readiness and warning classification.
6. Dashboard metrics and cross-module filters.
7. The employee-centric related-record experience.
8. The exact role matrix from the brief.
9. Product-specific print format and email template.
10. Automated acceptance tests for the complete HR-to-payroll journey.

### 6.3 What should remain open source

The following should remain based on the existing open-source platform unless a hard requirement proves otherwise:

- Document persistence and migrations.
- User authentication and sessions.
- Role and permission evaluation.
- Generic CRUD forms and list views.
- Database transactions and document lifecycle.
- Background jobs and realtime notifications.
- Print rendering and PDF generation.
- Accounting links and payment records.
- Standard payroll formula execution.
- Leave balance arithmetic.
- Standard employee and company relationships.

Replacing these systems would increase code volume, testing burden, security risk, and migration cost without improving the PeoplePay360 user outcome.

## 7. Proposed PeoplePay360 Module Design

### 7.1 Module: Employee Master

**Input:** identity, employment details, department, manager, employee type, status, schedule, user account.

**Output:** a central employee record linked to contract, schedule, attendance, time off, salary assignment, and payslip data.

**Implementation:** extend the existing Employee document and form scripts. Add server-side validation for required payroll fields and role-aware related-record queries.

**Acceptance tests:**

- An authorized user can create and update an employee.
- An employee can see only permitted personal and operational records.
- Related buttons return only records linked to the selected employee.
- Payroll users can identify missing fields before creating a Payrun.

### 7.2 Module: Contract Management

**Input:** employee, start date, end date, department, designation, wage, salary structure, status.

**Output:** historical contract records and one deterministic contract for payroll-period selection.

**Implementation:** reuse Contract and add a service function such as `get_applicable_contract(employee, period_start, period_end)`. The function should be used by payroll validation and payslip generation, not only by the UI.

**Acceptance tests:**

- A contract outside the selected period is ignored.
- A contract active for the selected period is selected.
- Overlapping active contracts produce a blocking warning.
- A missing applicable contract prevents finalization.

### 7.3 Module: Working Schedule

**Input:** schedule name, schedule type, day rows, start time, end time, break duration, employee or contract assignment.

**Output:** calculated weekly hours and a schedule used for attendance expectations.

**Implementation:** use the existing schedule/shift model and add a deterministic weekly-hours calculator. Handle overnight intervals explicitly.

**Acceptance tests:**

- Weekly hours are calculated from child rows.
- Breaks reduce payable scheduled time where policy requires it.
- An overnight shift does not produce a negative duration.
- Employees can be filtered by schedule.

### 7.4 Module: Attendance

**Input:** employee check-in, check-out, schedule, date, status, correction reason.

**Output:** worked hours, attendance status, exception status, payroll input.

**Implementation:** reuse Employee Checkin and Attendance. Add correction permissions, exception states, and a payroll-period readiness query.

**Acceptance tests:**

- Manual corrections are restricted to authorized users.
- Missing check-out is visible as an exception.
- Worked hours are consistent with the assigned schedule and policy.
- Payroll can identify unresolved attendance exceptions.

### 7.5 Module: Time Off

**Input:** time-off type, allocation, employee, date range, duration, reason, approver decision.

**Output:** approved balance movements and payroll-relevant leave data.

**Implementation:** reuse Leave Type, Leave Allocation, and Leave Application. Configure workflow states and add a balance summary to the employee and payroll context.

**Acceptance tests:**

- Unapproved allocations do not become available.
- Approved requests reduce the correct balance.
- Cancelled requests restore balance according to policy.
- Employees cannot approve their own requests unless explicitly allowed.

### 7.6 Module: Salary Structure and Salary Rule

**Input:** structure, ordered components, category, code, formula, amount, percentage, dependencies, effective date.

**Output:** an auditable component calculation used by salary slips.

**Implementation:** reuse Salary Structure and Salary Component. Add a PeoplePay360 view model if the product must call components `Salary Rules`.

**Acceptance tests:**

- Components execute in deterministic sequence.
- Basic, allowance, gross, deduction, contribution, and net totals are correct.
- Invalid component references are rejected before payroll computation.
- Historical salary slips retain their original amounts after structure changes.

### 7.7 Module: Payrun Creation Wizard

**Step 1:** choose payroll period, company, salary structure or scope, department, employee type, and optional filters.

**Step 2:** show eligible employees with contract, schedule, attendance, leave, salary assignment, and warning summaries.

**Commit:** create the underlying Payroll Entry/Payrun only after explicit employee selection.

**Implementation:** use a Frappe page or Vue route backed by whitelisted server methods. The server must repeat eligibility checks; the browser selection cannot be trusted as the only control.

**Acceptance tests:**

- Continue from step 1 does not create a payroll record.
- The employee list reflects the selected period and filters.
- Removed employees do not receive payslips.
- An ineligible employee cannot be forced into the batch through a crafted request.

### 7.8 Module: Payrun Processing

**States:** Draft, Computed, Validation Required, Validated, Paid, Sent, Cancelled.

**Actions:** Compute, Validate, Mark Paid, Send, Print, Cancel where permitted.

**Implementation:** map PeoplePay360 states to the underlying Payroll Entry and Salary Slip lifecycle. Use database transactions for batch creation and idempotency checks for compute/send actions.

**Acceptance tests:**

- Compute is repeatable without creating duplicate payslips.
- Validation blocks on missing required data.
- Mark Paid is unavailable before successful validation.
- Send records communication status and does not silently discard failures.

### 7.9 Module: Payslip and delivery

**Output fields:** employee, period, contract, structure, worked days, basic, allowances, contributions, gross, deductions, net, status.

**Implementation:** reuse Salary Slip and Frappe print formats. Add a PeoplePay360 payslip format with a calculation breakdown and a bulk email action on the parent Payrun.

**Acceptance tests:**

- Individual PDF output matches the salary slip values.
- Bulk delivery uses the same selected Payrun population.
- Missing employee email creates a visible warning.
- Historical PDF output remains reproducible after current configuration changes.

### 7.10 Module: Payroll dashboard

**Filters:** period, company, department, employee type, contract status, Payrun status.

**KPIs:** total net salary paid, payslips generated, average salary, approved time off, attendance health, warning count.

**Charts:** salary cost by department, monthly net salary, gross-to-net composition, leave and attendance trend.

**Warnings:** missing bank details, no applicable contract, duplicate payslip, incomplete salary assignment, unresolved attendance, pending approval, failed delivery.

**Implementation:** add number cards, charts, reports, and server-side query methods using the same permissions and period definitions as payroll. Do not calculate dashboard totals independently from payroll rules.

## 8. Roles and Permission Model

### 8.1 Required roles from the brief

| Role | Required access |
|---|---|
| Employee | Own employee data, own attendance, own leave balances, create own attendance/time-off requests, no payroll administration |
| HR Manager | Employee, attendance, contract, working schedule, and Time Off CRUD; approve/refuse requests; no payroll features |
| HR Payroll User | HR Manager access plus Payrun and Payslip create/read/update; read-only salary configuration |
| HR Payroll Manager | Full HR and payroll operations plus Salary Structure and Salary Rule administration |
| Admin | Complete system access, users, roles, permissions, and configuration |

### 8.2 Implementation guidance

Frappe permissions should be configured at both the DocType and record level:

- DocType permissions restrict create, read, write, submit, cancel, and print operations.
- User permissions restrict access to the employee, department, company, or branch scope where required.
- Server methods must call permission checks and must not rely on hidden buttons.
- Employee self-service must use owner/employee linkage, not only a frontend filter.
- Payroll configuration should be read-only for HR Payroll Users.
- Payroll actions such as Mark Paid and Send should require explicit role permissions.

### 8.3 Security acceptance tests

- An Employee cannot query another employee's payslip by changing a URL identifier.
- An HR Manager cannot open payroll configuration through a direct API call.
- An HR Payroll User cannot modify Salary Components.
- A Payroll Manager can process payroll but still receives only permitted company/department data.
- Admin can audit user role changes.

## 9. Data Relationships

```text
Employee
	|-- Contract (historical, date-effective)
	|-- Working Schedule / Shift Assignment
	|-- Employee Checkin
	|-- Attendance
	|-- Leave Allocation
	|-- Leave Application
	|-- Salary Structure Assignment
	|-- Salary Slip
	|     |-- Salary Detail rows
	|     |-- Worked Days rows
	|     |-- Payroll Entry / Payrun link
	|     |-- Contract context
	|-- User account

Salary Structure
	|-- Salary Component / Salary Rule rows

Payroll Entry / Payrun
	|-- Payroll Employee Detail rows
	|-- Salary Slips
	|-- Payroll Period
	|-- Company and accounting context
```

### 9.1 Referential rules

- Every payroll employee row must point to an Employee.
- Every Salary Slip must point to the Payrun/Payroll Entry that generated it.
- Every Salary Slip must have a period and company context.
- Every salary calculation must resolve a valid structure or assignment.
- Every attendance and leave record must retain its employee link.
- Historical records should be cancelled or superseded using framework lifecycle rules, not deleted casually.

## 10. End-to-End Operational Workflow

### 10.1 HR setup flow

1. Create Company and required payroll accounts through ERPNext configuration.
2. Define departments, designations, employee types, and holiday lists.
3. Define Working Schedules or Shift Types.
4. Define Time Off Types and approval rules.
5. Define Salary Components / Salary Rules.
6. Build Salary Structures with ordered components.
7. Create employees and link user accounts where self-service is required.
8. Create date-effective contracts and salary assignments.

### 10.2 Daily operations flow

1. Employees check in and out or submit attendance data.
2. Supervisors review exceptions and corrections.
3. Employees submit Time Off requests.
4. Managers approve or refuse requests.
5. Approved requests update available balances.
6. HR monitors employee, contract, attendance, and leave readiness.

### 10.3 Payroll flow

1. Payroll user opens the Payrun wizard.
2. User selects period, company, structure, department, and employee type.
3. Server returns eligible employees and warnings.
4. User explicitly selects employees.
5. Server revalidates contracts, salary assignments, duplicates, attendance, and permissions.
6. Underlying Payroll Entry/Payrun is created.
7. Salary Slips are generated.
8. Salary calculations run using ordered Salary Components/Rules.
9. User reviews warnings and payslip breakdowns.
10. User validates the batch.
11. User marks the batch paid through the appropriate accounting/payment flow.
12. User prints or sends payslips.
13. Dashboard and reports reflect the completed batch.

## 11. Open-Source Reuse Justification

### 11.1 Lower delivery risk

Payroll is a high-risk domain. Existing Frappe HR and ERPNext behavior already addresses many difficult concerns: document lifecycle, permissions, database transactions, payroll data structures, accounting relationships, reporting, print formats, and background execution. Reusing these reduces the chance of subtle financial and audit defects.

### 11.2 Better auditability

Frappe documents have owners, timestamps, status, links, and lifecycle events. Using those records gives PeoplePay360 a stronger audit trail than a custom collection of tables and frontend state.

### 11.3 Less duplicate logic

Leave balance calculation, salary component execution, PDF generation, email delivery, and role enforcement are all areas where duplicate implementations can diverge. Reuse gives the product one authoritative behavior and lets the team focus on the requested experience.

### 11.4 Extension without a fork

`hooks.py`, DocType class overrides, document events, client scripts, reports, workspaces, Vue routes, and patches allow behavior to be extended in the application layer. This keeps upgrades more manageable than modifying the framework directly.

### 11.5 Better integration path

ERPNext already supplies company and accounting concepts. A custom payroll engine would eventually need to recreate payment entries, journal entries, company settings, tax behavior, and financial audit rules. The open-source foundation avoids that duplication.

## 12. What Not to Do

- Do not create a second employee table.
- Do not create a second authentication system.
- Do not calculate leave balances only in the frontend.
- Do not trust browser-selected employees without server-side revalidation.
- Do not overwrite historical contracts to represent current terms.
- Do not create a second salary formula engine unless the existing component behavior is proven insufficient.
- Do not mark a payroll batch paid merely because payslips were generated.
- Do not expose payroll through hidden navigation alone; enforce permissions on the server.
- Do not build dashboard totals with different date boundaries from payroll.
- Do not delete historical payroll records to correct a current configuration mistake.

## 13. Implementation Phases

### Phase 1: Baseline verification

- Install the Docker environment.
- Create a sample company, department, employee, schedule, contract, leave type, allocation, salary component, and salary structure.
- Run a complete sample payroll using the existing Payroll Entry and Salary Slip flow.
- Record the exact gaps against the brief.

### Phase 2: Domain correctness

- Implement period-specific contract selection.
- Implement overlap and duplicate validations.
- Define attendance and leave readiness rules.
- Define salary component categories and calculation acceptance cases.
- Configure roles and server-side access rules.

### Phase 3: PeoplePay360 workflow

- Build the two-step Payrun wizard.
- Add explicit employee selection and warning summaries.
- Add Payrun processing actions and state presentation.
- Add related-record navigation from Employee.

### Phase 4: Reporting and delivery

- Add dashboard cards, charts, filters, and warning lists.
- Add the PeoplePay360 payslip print format.
- Add bulk email templates and delivery status.
- Add reports for payroll readiness and exception management.

### Phase 5: Hardening

- Add unit tests for contract and payroll-period rules.
- Add integration tests for leave balance and salary slip generation.
- Add permission tests for all five roles.
- Add browser tests for the Payrun wizard and payslip review.
- Test restart, migration, backup, and recovery behavior.

## 14. Testing Strategy

### 14.1 Unit tests

- Contract date intersection and selection.
- Overlap detection.
- Weekly-hours calculation.
- Attendance exception classification.
- Leave balance consumption and restoration.
- Salary component ordering and formula dependencies.
- Duplicate payslip detection.
- Dashboard period aggregation.

### 14.2 Integration tests

- Employee to Contract to Salary Assignment.
- Employee Checkin to Attendance.
- Leave Allocation to Leave Application to balance.
- Salary Structure to Salary Slip.
- Payroll Entry to Salary Slip batch.
- Salary Slip to print format and email communication.
- Payroll completion to dashboard metrics.

### 14.3 Permission tests

Test each required role against every sensitive object and action. A passing UI test is insufficient if the corresponding API request is not also denied for unauthorized users.

### 14.4 Acceptance scenario

Create two employees:

- Employee A has a contract ending halfway through the period and a replacement contract beginning afterward.
- Employee B has an unresolved attendance exception and no bank details.

Create a payroll period and select both employees. The system should:

1. Resolve Employee A's applicable contract according to the period policy.
2. Display Employee B warnings before finalization.
3. Prevent finalization if warnings are blocking.
4. Generate auditable payslip component rows after correction.
5. Produce a PDF matching the computed payslip.
6. Send only to employees with valid email addresses.
7. Reflect the final batch in dashboard totals.

## 15. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Terminology differs between brief and framework | User confusion and duplicated models | Use product labels and a clear compatibility layer around existing DocTypes |
| Contract overlap | Incorrect payroll | Server-side blocking validation and period-specific selection |
| Salary formula changes after payroll | Historical inconsistency | Preserve submitted slips and test historical reproducibility |
| Incomplete attendance | Incorrect worked days or salary | Readiness warnings and configurable blocking policy |
| Leave balance inconsistency | Employee trust and payroll errors | Reuse standard allocation/application logic and integration tests |
| Permission leakage | Confidential payroll exposure | DocType, record, API, and browser-level permission tests |
| Duplicate Payrun submission | Duplicate payments | Idempotency and unique period/employee checks |
| Open-source upgrades | Regression or migration cost | Avoid core edits, add patches and extension hooks, maintain upgrade tests |
| Dashboard mismatch | Loss of confidence | Use shared query services and payroll period definitions |
| Email delivery failure | Employees do not receive payslips | Track communication status and surface retryable failures |

## 16. Final Recommendation

PeoplePay360 should be implemented as a focused product layer on top of the current open-source Frappe HR and ERPNext foundation.

The existing open-source solution should own the platform primitives and mature domain behavior: employees, documents, permissions, attendance, leave balances, salary components, salary structures, salary slips, accounting integration, PDF rendering, email infrastructure, reports, and dashboards.

The PeoplePay360 team should own the connected experience and the rules that make the application match the problem statement: the employee hub, period-specific contract resolution, explicit two-step Payrun wizard, warning and validation model, product-specific roles, payroll dashboard, payslip presentation, and end-to-end tests.

This division is justified because it places custom effort where the product has unique value and leaves high-risk, general-purpose HR/payroll infrastructure to a maintained open-source platform. It also keeps the implementation upgradeable, auditable, and substantially smaller than rebuilding HR and payroll from first principles.

## 17. Evidence Index

The following repository areas should be used as the starting points for implementation and review:

- `PeoplePay360 HR & Payroll.md` - original product brief and acceptance intent.
- `hrms/hooks.py` - application registration, ERPNext dependency, overrides, document events, and lifecycle hooks.
- `hrms/modules.txt` - declared business modules.
- `hrms/hr/doctype/` - HR and employee-related DocTypes, including working schedule, attendance, leave, and lifecycle records.
- `hrms/hr/report/` - employee, attendance, leave, and operational reporting.
- `hrms/payroll/doctype/` - Payroll Entry, Salary Slip, Salary Structure, Salary Component, Payroll Period, and related payroll records.
- `hrms/payroll/page/payrun_processing/` - existing payroll processing page area.
- `hrms/payroll/workspace/payroll/payroll.json` - payroll workspace navigation, charts, number cards, and reports.
- `hrms/payroll/payroll_dashboard/payroll/payrolld.json` - payroll dashboard cards and charts.
- `frontend/src/views/attendance/` - modern attendance and shift operational views.
- `frontend/src/views/salary_slip/` - modern salary-slip view.
- `frontend/src/router/attendance.js` - attendance request, shift, assignment, and check-in routes.
- `frontend/src/router/salary_slips.js` - salary-slip detail route.
- `docker/docker-compose.yml` and `docker/init.sh` - local development runtime and bench initialization.

The evidence index is intentionally a starting map rather than a claim that every requested behavior is complete. Each product-specific requirement should be verified with a runnable scenario and an automated test before it is presented as done.

- Attendance and Time Off overviews track presence, overtime, approved days, pending requests, and leave balances

- Attendance Overview can show Present, Late, Absent, Overtime, missing check-outs, manual edits, and attendance coverage

- Department breakdown combines headcount with total salary expenditure

- Aggregates live data across Employees, Contracts, Payroll, Attendance, and Time Off modules

- for all HR interactions. Employees are managed via unified Kanban or List views, acting as the central hub

- processing uses the specific terms and time patterns valid for the current period. Contracts and Working Schedules are linked to employees, ensuring payroll


- users to verify and correct entries as needed. Attendance records capture daily presence and exceptions, allowing authorized

- allocating balances to processing and approving individual requests. Time Off management automates the lifecycle from defining leave types and

- Rules to dictate how earnings, deductions, and net salary are computed. Payroll configuration involves defining Salary Structures and sequencing Salary

- Payroll officers initiate a Payrun by defining the scope and period, then selecting specific employees before finalizing the batch creation.

- defined structure, and period context. The system computes individual Payslips based on the applicable contract,

- ensure accuracy before validating and marking the Payrun as paid. Officers review computed Payslip components and system-generated warnings to

- Payslips and distribute them to employees via email. Finalized Payruns are archived for history, with options to generate individual PDF

- payroll modules, offering filtered insights for strategic decision-making. The Payroll Dashboard aggregates real-time data across HR, attendance, and

- Integrates core HR and Payroll operations into one cohesive, end-to-end business flow, covering everything from employee master data to final payslip distribution.

- allocation, and ordered salary calculations over simple interface design. Prioritizes real-world business logic such as period-based contract handling, leave

- permissions, parent-child data relationships, and comprehensive historical payroll Encourages industry-standard system architecture, including role-based tracking.

- computation. stack, ensuring the focus remains on robust data relationships and accurate payroll Allows teams to demonstrate technical versatility by choosing their preferred


- database technology for their solution. Teams are free to select any backend language, frontend framework, and

- rather than using hardcoded values. calculations, leave logic, and payroll computation directly in the application logic Implement essential business rules such as contract selection, schedule

- be fully functional and integrated, not static mockups. Ensure Salary Rules actively drive Payslip generation; configuration screens must

- Surface potential payroll issues, such as duplicate entries or incomplete employee data, to users before finalization.

- payroll operations instead of relying on static charts. The Payroll Dashboard must reflect real-time, live data generated from HR and

- directly from the Payrun workflow. Include support for generating Payslip PDFs and facilitating bulk email distribution

- representative employee, contract, time, salary, and payroll data. Functional platform: Fully operational HR and payroll system populated with

- workflows. scenarios, such as the full employee-to-payslip and leave allocation-to-request Live demonstration: Five-minute walkthrough showcasing two end-to-end

- Future roadmap: Brief summary of proposed enhancements or extensions the team would prioritize with additional development time.

## Important Why This Hackathon Problem is


Unified HR & Payroll Workflow: Demonstrates an end-to-end employee-to-payslip

process, linking contracts, attendance, leave, and payroll into a single operational flow.

Business Logic Complexity: Focuses on real-world requirements like period-based

contract validation, leave balance consumption, salary rule sequencing, and payroll error

detection.

Systems Architecture: Promotes industry-standard designs, including role-based

access, comprehensive data relationships, historical record tracking, and aggregated

analytics.

Technical Versatility: Empowers teams to apply their preferred tech stack while

prioritizing robust data modeling and accurate payroll computation over surface-level UI

design.

## [Mockup Link: https://app.excalidraw.com/l/65VNwvy7c4X/17vHpCNFjex](https://app.excalidraw.com/l/65VNwvy7c4X/17vHpCNFjex)
