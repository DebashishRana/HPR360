/** Demo role login presets for PeoplePay360 (distinct passkeys per role). */
export const DEMO_ROLE_LOGINS = [
	{
		id: "employee",
		label: "Employee",
		description: "Own profile, attendance & time off",
		email: "alex.employee@example.com",
		password: "Emp@360!",
	},
	{
		id: "hr_manager",
		label: "HR Manager",
		description: "Employees, contracts, schedules, leave",
		email: "hr.manager@example.com",
		password: "HrMgr@360!",
	},
	{
		id: "payroll_user",
		label: "HR Payroll User",
		description: "HR + payruns & payslips (structures read-only)",
		email: "payroll.user@example.com",
		password: "PayUser@360!",
	},
	{
		id: "payroll_manager",
		label: "HR Payroll Manager",
		description: "Full HR & payroll configuration",
		email: "payroll.manager@example.com",
		password: "PayMgr@360!",
	},
	{
		id: "admin",
		label: "Admin",
		description: "Full system administration",
		email: "admin.pp@example.com",
		password: "Admin@360!",
	},
]
