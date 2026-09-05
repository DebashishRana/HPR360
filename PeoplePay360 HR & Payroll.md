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
