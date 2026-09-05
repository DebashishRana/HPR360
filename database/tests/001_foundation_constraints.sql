\set ON_ERROR_STOP on
BEGIN;

INSERT INTO organization.company (id, legal_name, code, currency_code, timezone)
VALUES ('00000000-0000-0000-0000-000000000001', 'PeoplePay Test Company', 'PPC', 'USD', 'UTC');
INSERT INTO workforce.employee (id, company_id, employee_number, legal_first_name, legal_last_name)
VALUES ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'E-001', 'Ada', 'Lovelace');
INSERT INTO workforce.employment (id, employee_id, company_id, employment_type, effective_period)
VALUES ('00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'employee', daterange('2026-01-01', NULL, '[)'));

DO $$
BEGIN
  BEGIN
    INSERT INTO workforce.employment (id, employee_id, company_id, employment_type, effective_period)
    VALUES ('00000000-0000-0000-0000-000000000021', '00000000-0000-0000-0000-000000000099', '00000000-0000-0000-0000-000000000001', 'employee', daterange('2026-01-01', NULL, '[)'));
    RAISE EXCEPTION 'expected foreign-key violation';
  EXCEPTION WHEN foreign_key_violation THEN NULL;
  END;
END $$;

DO $$
BEGIN
  BEGIN
    INSERT INTO workforce.contract (id, employment_id, employee_id, company_id, effective_period, contract_type, currency_code, base_pay)
    VALUES ('00000000-0000-0000-0000-000000000030', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', daterange('2026-02-01', '2026-02-01', '[)'), 'permanent', 'USD', 1000);
    RAISE EXCEPTION 'expected empty-range check violation';
  EXCEPTION WHEN check_violation THEN NULL;
  END;
END $$;

INSERT INTO workforce.contract (id, employment_id, employee_id, company_id, effective_period, contract_type, currency_code, base_pay)
VALUES ('00000000-0000-0000-0000-000000000031', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', daterange('2026-01-01', NULL, '[)'), 'permanent', 'USD', 1000);
DO $$
BEGIN
  BEGIN
    INSERT INTO workforce.contract (id, employment_id, employee_id, company_id, effective_period, contract_type, currency_code, base_pay)
    VALUES ('00000000-0000-0000-0000-000000000032', '00000000-0000-0000-0000-000000000020', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', daterange('2026-06-01', NULL, '[)'), 'permanent', 'USD', 1100);
    RAISE EXCEPTION 'expected overlapping-contract exclusion violation';
  EXCEPTION WHEN exclusion_violation THEN NULL;
  END;
END $$;

INSERT INTO leave.leave_type (id, company_id, code, name, unit)
VALUES ('00000000-0000-0000-0000-000000000050', '00000000-0000-0000-0000-000000000001', 'ANNUAL', 'Annual Leave', 'days');
DO $$
BEGIN
  BEGIN
    INSERT INTO leave.leave_ledger_entry (id, employee_id, company_id, leave_type_id, entry_type, effective_on, amount)
    VALUES ('00000000-0000-0000-0000-000000000051', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000050', 'allocation', DATE '2026-01-01', 0);
    RAISE EXCEPTION 'expected leave-ledger check violation';
  EXCEPTION WHEN check_violation THEN NULL;
  END;
END $$;
INSERT INTO leave.leave_ledger_entry (id, employee_id, company_id, leave_type_id, entry_type, effective_on, amount)
VALUES ('00000000-0000-0000-0000-000000000052', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000050', 'allocation', DATE '2026-01-01', 10);
DO $$
BEGIN
  BEGIN
    DELETE FROM leave.leave_ledger_entry WHERE id = '00000000-0000-0000-0000-000000000052';
    RAISE EXCEPTION 'expected append-only violation';
  EXCEPTION WHEN object_not_in_prerequisite_state THEN NULL;
  END;
END $$;

INSERT INTO compensation.salary_plan (id, company_id, code, name, effective_period, currency_code)
VALUES ('00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000001', 'STANDARD', 'Standard', daterange('2026-01-01', NULL, '[)'), 'USD');
INSERT INTO compensation.salary_rule (id, salary_plan_id, code, name, rule_type, fixed_amount)
VALUES ('00000000-0000-0000-0000-000000000061', '00000000-0000-0000-0000-000000000060', 'BASE', 'Base', 'fixed', 1000), ('00000000-0000-0000-0000-000000000062', '00000000-0000-0000-0000-000000000060', 'BONUS', 'Bonus', 'fixed', 100);
INSERT INTO compensation.salary_rule_dependency (salary_plan_id, salary_rule_id, depends_on_rule_id)
VALUES ('00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000061', '00000000-0000-0000-0000-000000000062');
DO $$
BEGIN
  BEGIN
    INSERT INTO compensation.salary_rule_dependency (salary_plan_id, salary_rule_id, depends_on_rule_id)
    VALUES ('00000000-0000-0000-0000-000000000060', '00000000-0000-0000-0000-000000000062', '00000000-0000-0000-0000-000000000061');
    RAISE EXCEPTION 'expected salary-rule cycle violation';
  EXCEPTION WHEN check_violation THEN NULL;
  END;
END $$;

DO $$
BEGIN
  BEGIN
    INSERT INTO payroll.payroll_run (id, company_id, code, payroll_period)
    VALUES ('00000000-0000-0000-0000-000000000070', '00000000-0000-0000-0000-000000000001', 'EMPTY', daterange('2026-02-01', '2026-02-01', '[)'));
    RAISE EXCEPTION 'expected payroll-period check violation';
  EXCEPTION WHEN check_violation THEN NULL;
  END;
END $$;
INSERT INTO payroll.payroll_run (id, company_id, code, payroll_period)
VALUES ('00000000-0000-0000-0000-000000000071', '00000000-0000-0000-0000-000000000001', 'JAN-2026', daterange('2026-01-01', '2026-02-01', '[)'));
INSERT INTO payroll.payroll_run_employee (payroll_run_id, employee_id, company_id, contract_id)
VALUES ('00000000-0000-0000-0000-000000000071', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000031');
INSERT INTO payroll.payslip (id, payroll_run_id, employee_id, company_id, gross_amount, deduction_amount, net_amount)
VALUES ('00000000-0000-0000-0000-000000000072', '00000000-0000-0000-0000-000000000071', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 1000, 100, 900);
DO $$
BEGIN
  BEGIN
    INSERT INTO payroll.payslip (id, payroll_run_id, employee_id, company_id, gross_amount, deduction_amount, net_amount)
    VALUES ('00000000-0000-0000-0000-000000000073', '00000000-0000-0000-0000-000000000071', '00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 1000, 100, 900);
    RAISE EXCEPTION 'expected unique payslip violation';
  EXCEPTION WHEN unique_violation THEN NULL;
  END;
END $$;

ROLLBACK;
