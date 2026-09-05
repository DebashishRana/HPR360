Implement the PeoplePay360 unified Payroll Dashboard in the existing Frappe HR repository.

Important:
- Do not create a new frontend framework.
- Reuse the existing Frappe Framework, ERPNext, Frappe HR, Vue, workspace, dashboard, chart, number-card, report, and permission patterns.
- Do not use mock, static, or hardcoded business data.
- Inspect the existing Payroll, HR, Attendance, Leave, Employee, Contract, Salary Slip, Payroll Entry, and Salary Structure models before editing.
- Keep all calculations server-side and permission-aware.
- Do not modify Frappe core or ERPNext core files unless absolutely necessary.
- Add changes inside the HRMS application layer.

Business requirement:

The Payroll Dashboard must integrate live data from:

1. Employee records
2. Employment Contracts
3. Salary Structure Assignments
4. Salary Slips
5. Payroll Entries
6. Attendance
7. Employee Checkins
8. Leave Applications
9. Leave Allocations
10. Departments
11. Employee Types

Dashboard filters:

- Payroll Period
- Start Date
- End Date
- Company
- Department
- Employee Type
- Branch
- Payroll Entry status

All dashboard cards, charts, warnings, and tables must use the selected filters consistently.

Required KPI cards:

1. Total Net Salary Paid
   - Sum the final net amount from submitted or paid Salary Slips within the selected period.

2. Payslips Generated
   - Count Salary Slips matching the selected filters.

3. Average Salary
   - Calculate total net salary divided by the number of matching employees.
   - Avoid division by zero.

4. Approved Time Off
   - Count approved Leave Applications within the selected date range.

5. Attendance Health
   - Show attendance percentage based on marked attendance versus expected working days.
   - Respect the current HRMS payroll and attendance settings.

6. Payroll Warnings
   - Count blocking and review-level payroll warnings.

Required charts:

1. Salary Cost by Department
   - Group net salary by Department.

2. Monthly Net Salary Trend
   - Group submitted or paid Salary Slips by month.

3. Attendance Health by Department
   - Compare expected working days with present, absent, and unmarked days.

4. Time Off Usage by Type
   - Group approved leave by Leave Type.

5. Employee Type Salary Distribution
   - Compare total net salary across Employee Types.

Required warning panel:

Show live warnings for:

- Employees without an active Employment Contract for the selected period
- Employees without a Salary Structure Assignment
- Overlapping Employment Contracts
- Duplicate Salary Slips
- Missing employee bank details
- Missing employee email address
- Unapproved or incomplete attendance
- Pending Leave Applications
- Missing payroll payable account
- Failed payslip email delivery
- Salary Structure Assignment with an invalid effective date

Each warning must include:

- Severity: Blocking, Review, or Informational
- Employee or document reference
- Description
- Link to the relevant Frappe document
- Count
- Filter context

Required dashboard tables:

1. Payroll Readiness
   Columns:
   - Employee
   - Employee Type
   - Department
   - Active Contract
   - Salary Structure
   - Attendance Status
   - Leave Status
   - Bank Details
   - Readiness Status

2. Payroll Summary
   Columns:
   - Employee
   - Salary Slip
   - Gross Pay
   - Total Deduction
   - Net Pay
   - Payroll Status

3. Contract Attention
   Columns:
   - Employee
   - Contract
   - Start Date
   - End Date
   - Status
   - Warning

Implementation requirements:

Backend:
- Add a dedicated server-side dashboard module under the HRMS application.
- Use Frappe Query Builder or safe parameterized database queries.
- Validate filters on the server.
- Apply Frappe permissions to every query.
- Do not trust frontend filters for authorization.
- Reuse existing DocTypes and fields.
- Reuse the existing Payroll Entry, Salary Slip, Employee, Contract, Attendance, Leave Application, Leave Allocation, and Salary Structure Assignment models.
- Centralize date filtering so every metric uses the same period boundaries.
- Return a predictable JSON response containing:
  - filters
  - kpis
  - charts
  - warnings
  - tables
  - metadata

Frontend:
- Reuse the existing Vue frontend and Frappe UI components.
- Add the dashboard to the existing Payroll navigation.
- Provide a clear filter bar.
- Add loading, empty, error, and permission-denied states.
- Refresh all cards, charts, warnings, and tables when filters change.
- Debounce filter requests where appropriate.
- Do not duplicate backend calculation logic in Vue.
- Use existing project styling and components.

Permissions:
- Employees must see only their own permitted data.
- HR Managers must not see payroll data if their role configuration prohibits it.
- Payroll Users must see only permitted companies/departments.
- Payroll Managers can see and process authorized payroll data.
- Admin has full access.
- Test direct API access, not only UI visibility.

Testing:
Add automated tests for:

1. Period filtering.
2. Department filtering.
3. Employee Type filtering.
4. Company filtering.
5. Combined filters.
6. Empty results.
7. Permission restrictions.
8. Net salary calculation.
9. Approved leave calculation.
10. Attendance health calculation.
11. Contract warning detection.
12. Missing Salary Structure Assignment detection.
13. Duplicate payslip detection.
14. Dashboard response format.

Acceptance criteria:

- Every metric comes from actual database records.
- No hardcoded dashboard numbers exist.
- Changing Period updates every dashboard element.
- Changing Department updates every dashboard element.
- Changing Employee Type updates every dashboard element.
- Salary charts match Salary Slip totals.
- Leave metrics match approved Leave Applications.
- Attendance metrics match Attendance and payroll settings.
- Warnings link to real documents.
- Unauthorized users cannot retrieve restricted records through API calls.
- Dashboard works with no records and does not crash.
- Dashboard is accessible from the existing Payroll navigation.
- Existing payroll calculation behavior remains unchanged.
- Add documentation describing the new endpoints, filters, data sources, and permission behavior.