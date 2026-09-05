BEGIN;

CREATE TABLE IF NOT EXISTS public.schema_migration (version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now());
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM public.schema_migration WHERE version = '0001_peoplepay360_foundation') THEN RAISE EXCEPTION 'migration already applied'; END IF;
END $$;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE SCHEMA identity; CREATE SCHEMA organization; CREATE SCHEMA workforce; CREATE SCHEMA time; CREATE SCHEMA leave; CREATE SCHEMA compensation; CREATE SCHEMA payroll; CREATE SCHEMA audit; CREATE SCHEMA analytics;

CREATE FUNCTION audit.reject_update_or_delete() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
  RAISE EXCEPTION '% records are append-only', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME USING ERRCODE = '55000';
END $$;

CREATE TABLE identity."user" (
  id uuid PRIMARY KEY, email text NOT NULL, display_name text NOT NULL, is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (email = btrim(email) AND position('@' IN email) > 1)
);
CREATE UNIQUE INDEX user_email_lower_key ON identity."user" (lower(email));
CREATE TABLE identity.role (id uuid PRIMARY KEY, code text NOT NULL UNIQUE, name text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), CHECK (code = lower(code) AND code ~ '^[a-z][a-z0-9_]*$'));
CREATE TABLE identity.permission (id uuid PRIMARY KEY, code text NOT NULL UNIQUE, description text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), CHECK (code = lower(code) AND code ~ '^[a-z][a-z0-9_.]*$'));
CREATE TABLE identity.user_role (user_id uuid NOT NULL REFERENCES identity."user", role_id uuid NOT NULL REFERENCES identity.role, assigned_at timestamptz NOT NULL DEFAULT now(), assigned_by_user_id uuid REFERENCES identity."user", PRIMARY KEY (user_id, role_id));
CREATE TABLE identity.role_permission (role_id uuid NOT NULL REFERENCES identity.role, permission_id uuid NOT NULL REFERENCES identity.permission, PRIMARY KEY (role_id, permission_id));

CREATE TABLE organization.company (
  id uuid PRIMARY KEY, legal_name text NOT NULL, code text NOT NULL UNIQUE, currency_code char(3) NOT NULL, timezone text NOT NULL, is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, code),
  CHECK (code = upper(code) AND code ~ '^[A-Z][A-Z0-9_]*$'), CHECK (currency_code ~ '^[A-Z]{3}$')
);
CREATE TABLE organization.department (
  id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, parent_department_id uuid, code text NOT NULL, name text NOT NULL, is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code),
  FOREIGN KEY (parent_department_id, company_id) REFERENCES organization.department (id, company_id), CHECK (parent_department_id IS NULL OR parent_department_id <> id)
);
CREATE TABLE organization.job_position (
  id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, department_id uuid, code text NOT NULL, title text NOT NULL, is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code),
  FOREIGN KEY (department_id, company_id) REFERENCES organization.department (id, company_id)
);

CREATE TABLE workforce.employee (
  id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, employee_number text NOT NULL, legal_first_name text NOT NULL, legal_last_name text NOT NULL, work_email text,
  hired_at timestamptz, terminated_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (id, company_id), UNIQUE (company_id, employee_number), CHECK (terminated_at IS NULL OR hired_at IS NULL OR terminated_at >= hired_at)
);
CREATE TABLE workforce.employment (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, employment_type text NOT NULL, status text NOT NULL DEFAULT 'active', effective_period daterange NOT NULL,
  job_position_id uuid, department_id uuid, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, employee_id, company_id),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (job_position_id, company_id) REFERENCES organization.job_position (id, company_id), FOREIGN KEY (department_id, company_id) REFERENCES organization.department (id, company_id),
  CHECK (NOT isempty(effective_period)), CHECK (status IN ('active','ended','cancelled'))
);
CREATE INDEX employment_employee_period_idx ON workforce.employment USING gist (employee_id, effective_period);
CREATE TABLE workforce.contract (
  id uuid PRIMARY KEY, employment_id uuid NOT NULL, employee_id uuid NOT NULL, company_id uuid NOT NULL, status text NOT NULL DEFAULT 'active', effective_period daterange NOT NULL,
  contract_type text NOT NULL, currency_code char(3) NOT NULL, base_pay numeric(19,4) NOT NULL, terms jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (id, employee_id, company_id),
  FOREIGN KEY (employment_id, employee_id, company_id) REFERENCES workforce.employment (id, employee_id, company_id),
  CHECK (NOT isempty(effective_period)), CHECK (status IN ('draft','active','superseded','ended','cancelled')), CHECK (currency_code ~ '^[A-Z]{3}$'), CHECK (base_pay >= 0), CHECK (jsonb_typeof(terms) = 'object'),
  EXCLUDE USING gist (employee_id WITH =, effective_period WITH &&) WHERE (status = 'active')
);
CREATE TABLE workforce.employee_reporting_line (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, manager_employee_id uuid NOT NULL, company_id uuid NOT NULL, effective_period daterange NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (manager_employee_id, company_id) REFERENCES workforce.employee (id, company_id),
  CHECK (employee_id <> manager_employee_id), CHECK (NOT isempty(effective_period)), EXCLUDE USING gist (employee_id WITH =, effective_period WITH &&)
);
CREATE TABLE workforce.employee_event (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, event_type text NOT NULL, occurred_at timestamptz NOT NULL, payload jsonb NOT NULL DEFAULT '{}'::jsonb, recorded_by_user_id uuid REFERENCES identity."user", created_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), CHECK (jsonb_typeof(payload) = 'object')
);
CREATE INDEX employee_event_employee_occurred_idx ON workforce.employee_event (employee_id, occurred_at DESC);

CREATE TABLE time.working_schedule (
  id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, code text NOT NULL, name text NOT NULL, timezone text NOT NULL, is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code)
);
CREATE TABLE time.schedule_day (
  id uuid PRIMARY KEY, working_schedule_id uuid NOT NULL REFERENCES time.working_schedule ON DELETE CASCADE, weekday smallint NOT NULL, is_working_day boolean NOT NULL, expected_minutes integer NOT NULL DEFAULT 0, start_local_time time, end_local_time time,
  UNIQUE (working_schedule_id, weekday), CHECK (weekday BETWEEN 0 AND 6), CHECK (expected_minutes BETWEEN 0 AND 1440),
  CHECK ((is_working_day AND expected_minutes > 0 AND start_local_time IS NOT NULL AND end_local_time IS NOT NULL) OR (NOT is_working_day AND expected_minutes = 0))
);
CREATE TABLE time.schedule_assignment (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, working_schedule_id uuid NOT NULL, effective_period daterange NOT NULL, status text NOT NULL DEFAULT 'active', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (working_schedule_id, company_id) REFERENCES time.working_schedule (id, company_id),
  CHECK (NOT isempty(effective_period)), CHECK (status IN ('active','superseded','cancelled')), EXCLUDE USING gist (employee_id WITH =, effective_period WITH &&) WHERE (status = 'active')
);
CREATE TABLE time.attendance_event (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, occurred_at timestamptz NOT NULL, event_type text NOT NULL, source text NOT NULL, source_event_id text, payload jsonb NOT NULL DEFAULT '{}'::jsonb, received_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), CHECK (event_type IN ('check_in','check_out','break_start','break_end','manual')), CHECK (jsonb_typeof(payload) = 'object')
);
CREATE UNIQUE INDEX attendance_event_source_event_key ON time.attendance_event (company_id, source, source_event_id) WHERE source_event_id IS NOT NULL;
CREATE INDEX attendance_event_employee_occurred_idx ON time.attendance_event (employee_id, occurred_at DESC);
CREATE TABLE time.attendance_day (
  id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, work_date date NOT NULL, schedule_assignment_id uuid, expected_minutes integer NOT NULL DEFAULT 0, worked_minutes integer NOT NULL DEFAULT 0, payroll_ready boolean NOT NULL DEFAULT false,
  calculated_at timestamptz NOT NULL DEFAULT now(), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (schedule_assignment_id, company_id) REFERENCES time.schedule_assignment (id, company_id), UNIQUE (employee_id, work_date), CHECK (expected_minutes BETWEEN 0 AND 1440), CHECK (worked_minutes BETWEEN 0 AND 1440)
);
CREATE INDEX attendance_day_employee_date_idx ON time.attendance_day (employee_id, work_date DESC);
CREATE TABLE time.attendance_exception (id uuid PRIMARY KEY, attendance_day_id uuid NOT NULL REFERENCES time.attendance_day, exception_type text NOT NULL, status text NOT NULL DEFAULT 'open', details jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz, CHECK (status IN ('open','resolved','dismissed')), CHECK (jsonb_typeof(details) = 'object'));
CREATE INDEX attendance_exception_open_idx ON time.attendance_exception (attendance_day_id) WHERE status = 'open';
CREATE TABLE time.attendance_correction (id uuid PRIMARY KEY, attendance_day_id uuid NOT NULL REFERENCES time.attendance_day, requested_by_user_id uuid REFERENCES identity."user", approved_by_user_id uuid REFERENCES identity."user", status text NOT NULL DEFAULT 'requested', corrected_expected_minutes integer, corrected_worked_minutes integer, reason text NOT NULL, requested_at timestamptz NOT NULL DEFAULT now(), decided_at timestamptz, CHECK (status IN ('requested','approved','rejected','applied')), CHECK (corrected_expected_minutes IS NULL OR corrected_expected_minutes BETWEEN 0 AND 1440), CHECK (corrected_worked_minutes IS NULL OR corrected_worked_minutes BETWEEN 0 AND 1440));

CREATE TABLE leave.leave_type (id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, code text NOT NULL, name text NOT NULL, unit text NOT NULL, allow_negative_balance boolean NOT NULL DEFAULT false, is_active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code), CHECK (unit IN ('days','hours')));
CREATE TABLE leave.leave_policy (id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, leave_type_id uuid NOT NULL, code text NOT NULL, effective_period daterange NOT NULL, rules jsonb NOT NULL DEFAULT '{}'::jsonb, status text NOT NULL DEFAULT 'active', created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code, effective_period), FOREIGN KEY (leave_type_id, company_id) REFERENCES leave.leave_type (id, company_id), CHECK (NOT isempty(effective_period)), CHECK (status IN ('draft','active','retired')), CHECK (jsonb_typeof(rules) = 'object'));
CREATE TABLE leave.leave_allocation (id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, leave_type_id uuid NOT NULL, leave_policy_id uuid, effective_period daterange NOT NULL, allocated_amount numeric(19,4) NOT NULL, status text NOT NULL DEFAULT 'active', created_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (leave_type_id, company_id) REFERENCES leave.leave_type (id, company_id), FOREIGN KEY (leave_policy_id, company_id) REFERENCES leave.leave_policy (id, company_id), CHECK (NOT isempty(effective_period)), CHECK (allocated_amount >= 0), CHECK (status IN ('draft','active','cancelled')));
CREATE INDEX leave_allocation_employee_type_period_idx ON leave.leave_allocation USING gist (employee_id, leave_type_id, effective_period);
CREATE TABLE leave.leave_request (id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, leave_type_id uuid NOT NULL, requested_period daterange NOT NULL, requested_amount numeric(19,4) NOT NULL, status text NOT NULL DEFAULT 'draft', reason text, requested_at timestamptz NOT NULL DEFAULT now(), approved_at timestamptz, decided_by_user_id uuid REFERENCES identity."user", FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (leave_type_id, company_id) REFERENCES leave.leave_type (id, company_id), CHECK (NOT isempty(requested_period)), CHECK (requested_amount > 0), CHECK (status IN ('draft','submitted','approved','rejected','cancelled')));
CREATE INDEX leave_request_employee_period_idx ON leave.leave_request USING gist (employee_id, requested_period);
CREATE TABLE leave.leave_ledger_entry (id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, leave_type_id uuid NOT NULL, leave_request_id uuid REFERENCES leave.leave_request, leave_allocation_id uuid REFERENCES leave.leave_allocation, entry_type text NOT NULL, effective_on date NOT NULL, amount numeric(19,4) NOT NULL, reversal_of_entry_id uuid REFERENCES leave.leave_ledger_entry, idempotency_key text, recorded_at timestamptz NOT NULL DEFAULT now(), recorded_by_user_id uuid REFERENCES identity."user", metadata jsonb NOT NULL DEFAULT '{}'::jsonb, FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (leave_type_id, company_id) REFERENCES leave.leave_type (id, company_id), CHECK (entry_type IN ('allocation','accrual','request_debit','adjustment','reversal','expiry')), CHECK (amount <> 0), CHECK (jsonb_typeof(metadata) = 'object'), CHECK (reversal_of_entry_id IS NULL OR entry_type = 'reversal'));
CREATE UNIQUE INDEX leave_ledger_entry_idempotency_key ON leave.leave_ledger_entry (company_id, idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX leave_ledger_employee_type_effective_idx ON leave.leave_ledger_entry (employee_id, leave_type_id, effective_on DESC);
CREATE TRIGGER leave_ledger_append_only BEFORE UPDATE OR DELETE ON leave.leave_ledger_entry FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();

CREATE TABLE compensation.salary_plan (id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, code text NOT NULL, name text NOT NULL, effective_period daterange NOT NULL, status text NOT NULL DEFAULT 'active', currency_code char(3) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), CHECK (NOT isempty(effective_period)), CHECK (status IN ('draft','active','retired')), CHECK (currency_code ~ '^[A-Z]{3}$'), EXCLUDE USING gist (company_id WITH =, code WITH =, effective_period WITH &&) WHERE (status = 'active'));
CREATE TABLE compensation.salary_rule (id uuid PRIMARY KEY, salary_plan_id uuid NOT NULL REFERENCES compensation.salary_plan ON DELETE CASCADE, code text NOT NULL, name text NOT NULL, rule_type text NOT NULL, fixed_amount numeric(19,4), percentage numeric(9,6), percentage_basis_code text, formula_expression text, calculation_order integer NOT NULL DEFAULT 0, is_active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, salary_plan_id), UNIQUE (salary_plan_id, code), CHECK (rule_type IN ('fixed','percentage','formula')), CHECK (calculation_order >= 0), CHECK ((rule_type = 'fixed' AND fixed_amount IS NOT NULL AND percentage IS NULL AND formula_expression IS NULL) OR (rule_type = 'percentage' AND percentage IS NOT NULL AND percentage_basis_code IS NOT NULL AND formula_expression IS NULL) OR (rule_type = 'formula' AND formula_expression IS NOT NULL AND fixed_amount IS NULL AND percentage IS NULL)));
CREATE TABLE compensation.salary_rule_dependency (salary_plan_id uuid NOT NULL, salary_rule_id uuid NOT NULL, depends_on_rule_id uuid NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (salary_rule_id, depends_on_rule_id), FOREIGN KEY (salary_rule_id, salary_plan_id) REFERENCES compensation.salary_rule (id, salary_plan_id) ON DELETE CASCADE, FOREIGN KEY (depends_on_rule_id, salary_plan_id) REFERENCES compensation.salary_rule (id, salary_plan_id) ON DELETE RESTRICT, CHECK (salary_rule_id <> depends_on_rule_id));
CREATE FUNCTION compensation.reject_salary_rule_cycle() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE creates_cycle boolean; BEGIN
  WITH RECURSIVE reachable(rule_id) AS (SELECT NEW.depends_on_rule_id UNION SELECT d.depends_on_rule_id FROM compensation.salary_rule_dependency d JOIN reachable r ON d.salary_rule_id = r.rule_id WHERE d.salary_plan_id = NEW.salary_plan_id)
  SELECT EXISTS (SELECT 1 FROM reachable WHERE rule_id = NEW.salary_rule_id) INTO creates_cycle;
  IF creates_cycle THEN RAISE EXCEPTION 'salary-rule dependency would create a cycle' USING ERRCODE = '23514'; END IF; RETURN NEW;
END $$;
CREATE FUNCTION compensation.reject_salary_rule_dependency_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'replace salary-rule dependencies with delete and insert' USING ERRCODE = '55000'; END $$;
CREATE TRIGGER salary_rule_dependency_no_cycle BEFORE INSERT ON compensation.salary_rule_dependency FOR EACH ROW EXECUTE FUNCTION compensation.reject_salary_rule_cycle();
CREATE TRIGGER salary_rule_dependency_no_update BEFORE UPDATE ON compensation.salary_rule_dependency FOR EACH ROW EXECUTE FUNCTION compensation.reject_salary_rule_dependency_update();
CREATE TABLE compensation.employee_salary_assignment (id uuid PRIMARY KEY, employee_id uuid NOT NULL, company_id uuid NOT NULL, salary_plan_id uuid NOT NULL, effective_period daterange NOT NULL, status text NOT NULL DEFAULT 'active', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (salary_plan_id, company_id) REFERENCES compensation.salary_plan (id, company_id), CHECK (NOT isempty(effective_period)), CHECK (status IN ('draft','active','superseded','cancelled')), EXCLUDE USING gist (employee_id WITH =, effective_period WITH &&) WHERE (status = 'active'));

CREATE TABLE payroll.payroll_run (id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, code text NOT NULL, payroll_period daterange NOT NULL, status text NOT NULL DEFAULT 'draft', selected_at timestamptz, validated_at timestamptz, approved_at timestamptz, posted_at timestamptz, paid_at timestamptz, created_by_user_id uuid REFERENCES identity."user", created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE (id, company_id), UNIQUE (company_id, code), CHECK (NOT isempty(payroll_period)), CHECK (status IN ('draft','validating','ready','processing','calculated','review','approved','posted','paid')));
CREATE FUNCTION payroll.lock_run(p_payroll_run_id uuid) RETURNS void LANGUAGE plpgsql AS $$ BEGIN
  -- Must be called inside the payroll calculation/posting transaction.
  PERFORM pg_advisory_xact_lock(hashtextextended(p_payroll_run_id::text, 947360));
END $$;
CREATE TABLE payroll.payroll_run_employee (payroll_run_id uuid NOT NULL, employee_id uuid NOT NULL, company_id uuid NOT NULL, contract_id uuid, eligibility_status text NOT NULL DEFAULT 'selected', exclusion_reason text, selected_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (payroll_run_id, employee_id), FOREIGN KEY (payroll_run_id, company_id) REFERENCES payroll.payroll_run (id, company_id) ON DELETE RESTRICT, FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), FOREIGN KEY (contract_id, employee_id, company_id) REFERENCES workforce.contract (id, employee_id, company_id), CHECK (eligibility_status IN ('selected','excluded','processed')), CHECK ((eligibility_status = 'excluded') = (exclusion_reason IS NOT NULL)));
CREATE INDEX payroll_run_employee_scope_idx ON payroll.payroll_run_employee (payroll_run_id, eligibility_status, employee_id);
CREATE FUNCTION payroll.reject_scope_change_after_processing() RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE target_run_id uuid; run_status text; BEGIN
  IF TG_OP = 'DELETE' THEN target_run_id := OLD.payroll_run_id; ELSE target_run_id := NEW.payroll_run_id; END IF;
  SELECT status INTO run_status FROM payroll.payroll_run WHERE id = target_run_id FOR KEY SHARE;
  IF run_status IN ('processing','calculated','review','approved','posted','paid') THEN RAISE EXCEPTION 'payroll employee scope is locked after processing begins' USING ERRCODE = '55000'; END IF;
  IF TG_OP = 'DELETE' THEN RETURN OLD; END IF; RETURN NEW;
END $$;
CREATE TRIGGER payroll_scope_lifecycle BEFORE INSERT OR UPDATE OR DELETE ON payroll.payroll_run_employee FOR EACH ROW EXECUTE FUNCTION payroll.reject_scope_change_after_processing();
CREATE TABLE payroll.payroll_validation (id uuid PRIMARY KEY, payroll_run_id uuid NOT NULL REFERENCES payroll.payroll_run ON DELETE CASCADE, code text NOT NULL, name text NOT NULL, is_blocking boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (payroll_run_id, code));
CREATE TABLE payroll.payroll_validation_result (id uuid PRIMARY KEY, payroll_validation_id uuid NOT NULL REFERENCES payroll.payroll_validation ON DELETE CASCADE, employee_id uuid, severity text NOT NULL, status text NOT NULL DEFAULT 'open', message text NOT NULL, details jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz, CHECK (severity IN ('warning','error')), CHECK (status IN ('open','resolved','dismissed')), CHECK (jsonb_typeof(details) = 'object'));
CREATE INDEX payroll_validation_pending_idx ON payroll.payroll_validation_result (payroll_validation_id, employee_id) WHERE status = 'open' AND severity = 'error';
CREATE TABLE payroll.idempotency_key (id uuid PRIMARY KEY, company_id uuid NOT NULL REFERENCES organization.company, operation text NOT NULL, key text NOT NULL, request_hash text NOT NULL, resource_type text, resource_id uuid, status text NOT NULL DEFAULT 'in_progress', created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz, UNIQUE (company_id, operation, key), CHECK (status IN ('in_progress','completed','failed')), CHECK ((resource_type IS NULL) = (resource_id IS NULL)));
CREATE TABLE payroll.payroll_calculation_snapshot (id uuid PRIMARY KEY, payroll_run_id uuid NOT NULL, employee_id uuid NOT NULL, contract_id uuid REFERENCES workforce.contract, salary_plan_id uuid REFERENCES compensation.salary_plan, snapshot jsonb NOT NULL, captured_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY (payroll_run_id, employee_id) REFERENCES payroll.payroll_run_employee, UNIQUE (payroll_run_id, employee_id), CHECK (jsonb_typeof(snapshot) = 'object'));
CREATE TRIGGER payroll_snapshot_immutable BEFORE UPDATE OR DELETE ON payroll.payroll_calculation_snapshot FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();
CREATE TABLE payroll.payslip (id uuid PRIMARY KEY, payroll_run_id uuid NOT NULL, employee_id uuid NOT NULL, company_id uuid NOT NULL, status text NOT NULL DEFAULT 'calculated', gross_amount numeric(19,4) NOT NULL DEFAULT 0, deduction_amount numeric(19,4) NOT NULL DEFAULT 0, net_amount numeric(19,4) NOT NULL DEFAULT 0, calculated_at timestamptz NOT NULL DEFAULT now(), posted_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY (payroll_run_id, employee_id) REFERENCES payroll.payroll_run_employee, FOREIGN KEY (employee_id, company_id) REFERENCES workforce.employee (id, company_id), UNIQUE (payroll_run_id, employee_id), CHECK (status IN ('calculated','reviewed','approved','posted','paid')), CHECK (net_amount = gross_amount - deduction_amount));
CREATE INDEX payslip_employee_history_idx ON payroll.payslip (employee_id, posted_at DESC);
CREATE FUNCTION payroll.enforce_payslip_immutability() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP = 'DELETE' AND OLD.status IN ('posted','paid') THEN RAISE EXCEPTION 'posted payslips are immutable' USING ERRCODE = '55000'; ELSIF TG_OP = 'UPDATE' AND OLD.status IN ('posted','paid') THEN RAISE EXCEPTION 'posted payslips are immutable; use adjustment or reversal records' USING ERRCODE = '55000'; END IF; IF TG_OP = 'DELETE' THEN RETURN OLD; END IF; RETURN NEW; END $$;
CREATE TRIGGER payslip_immutable_after_posting BEFORE UPDATE OR DELETE ON payroll.payslip FOR EACH ROW EXECUTE FUNCTION payroll.enforce_payslip_immutability();
CREATE TABLE payroll.payslip_input (id uuid PRIMARY KEY, payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, input_type text NOT NULL, source_reference text, value numeric(19,4), payload jsonb NOT NULL DEFAULT '{}'::jsonb, captured_at timestamptz NOT NULL DEFAULT now(), CHECK (value IS NOT NULL OR payload <> '{}'::jsonb), CHECK (jsonb_typeof(payload) = 'object'));
CREATE INDEX payslip_input_payslip_idx ON payroll.payslip_input (payslip_id, input_type);
CREATE TRIGGER payslip_input_immutable BEFORE UPDATE OR DELETE ON payroll.payslip_input FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();
CREATE TABLE payroll.payslip_line (id uuid PRIMARY KEY, payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, salary_rule_id uuid REFERENCES compensation.salary_rule, code text NOT NULL, description text NOT NULL, line_type text NOT NULL, amount numeric(19,4) NOT NULL, sequence integer NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (payslip_id, code), UNIQUE (payslip_id, sequence), CHECK (line_type IN ('earning','deduction','employer_cost','informational')));
CREATE TRIGGER payslip_line_immutable BEFORE UPDATE OR DELETE ON payroll.payslip_line FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();
CREATE TABLE payroll.payslip_calculation_trace (id uuid PRIMARY KEY, payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, payslip_line_id uuid REFERENCES payroll.payslip_line ON DELETE RESTRICT, sequence integer NOT NULL, event_type text NOT NULL, trace jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (payslip_id, sequence), CHECK (jsonb_typeof(trace) = 'object'));
CREATE INDEX payslip_calculation_trace_payslip_idx ON payroll.payslip_calculation_trace (payslip_id, sequence);
CREATE TRIGGER payslip_trace_append_only BEFORE UPDATE OR DELETE ON payroll.payslip_calculation_trace FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();
CREATE TABLE payroll.payroll_adjustment (id uuid PRIMARY KEY, original_payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, adjustment_payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, reason text NOT NULL, created_by_user_id uuid REFERENCES identity."user", created_at timestamptz NOT NULL DEFAULT now(), UNIQUE (adjustment_payslip_id), CHECK (original_payslip_id <> adjustment_payslip_id));
CREATE TABLE payroll.payroll_reversal (id uuid PRIMARY KEY, original_payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, reversal_payslip_id uuid NOT NULL REFERENCES payroll.payslip ON DELETE RESTRICT, reason text NOT NULL, created_by_user_id uuid REFERENCES identity."user", reversed_at timestamptz NOT NULL DEFAULT now(), UNIQUE (reversal_payslip_id), CHECK (original_payslip_id <> reversal_payslip_id));
CREATE FUNCTION payroll.enforce_run_state_transition() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.status = OLD.status THEN RETURN NEW; END IF; IF NOT ((OLD.status = 'draft' AND NEW.status = 'validating') OR (OLD.status = 'validating' AND NEW.status = 'ready') OR (OLD.status = 'ready' AND NEW.status = 'processing') OR (OLD.status = 'processing' AND NEW.status = 'calculated') OR (OLD.status = 'calculated' AND NEW.status = 'review') OR (OLD.status = 'review' AND NEW.status = 'approved') OR (OLD.status = 'approved' AND NEW.status = 'posted') OR (OLD.status = 'posted' AND NEW.status = 'paid')) THEN RAISE EXCEPTION 'invalid payroll state transition: % -> %', OLD.status, NEW.status USING ERRCODE = '23514'; END IF; RETURN NEW; END $$;
CREATE FUNCTION payroll.enforce_posted_run_immutability() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF TG_OP = 'DELETE' AND OLD.status IN ('posted','paid') THEN RAISE EXCEPTION 'posted payroll runs are immutable' USING ERRCODE = '55000'; ELSIF TG_OP = 'UPDATE' AND OLD.status IN ('posted','paid') THEN IF OLD.status = 'posted' AND NEW.status = 'paid' AND (to_jsonb(NEW) - ARRAY['status','updated_at','paid_at']) IS NOT DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','updated_at','paid_at']) THEN RETURN NEW; END IF; RAISE EXCEPTION 'posted payroll runs are immutable; use adjustment or reversal records' USING ERRCODE = '55000'; END IF; IF TG_OP = 'DELETE' THEN RETURN OLD; END IF; RETURN NEW; END $$;
CREATE TRIGGER payroll_run_state_transition BEFORE UPDATE OF status ON payroll.payroll_run FOR EACH ROW EXECUTE FUNCTION payroll.enforce_run_state_transition();
CREATE TRIGGER payroll_run_immutable_after_posting BEFORE UPDATE OR DELETE ON payroll.payroll_run FOR EACH ROW EXECUTE FUNCTION payroll.enforce_posted_run_immutability();

CREATE TABLE audit.audit_event (id uuid PRIMARY KEY, company_id uuid REFERENCES organization.company, actor_user_id uuid REFERENCES identity."user", occurred_at timestamptz NOT NULL DEFAULT now(), action text NOT NULL, entity_schema text NOT NULL, entity_table text NOT NULL, entity_id uuid, correlation_id uuid, before_data jsonb, after_data jsonb, metadata jsonb NOT NULL DEFAULT '{}'::jsonb, CHECK (before_data IS NULL OR jsonb_typeof(before_data) = 'object'), CHECK (after_data IS NULL OR jsonb_typeof(after_data) = 'object'), CHECK (jsonb_typeof(metadata) = 'object'));
CREATE INDEX audit_event_entity_idx ON audit.audit_event (entity_schema, entity_table, entity_id, occurred_at DESC);
CREATE TABLE audit.entity_revision (id uuid PRIMARY KEY, company_id uuid REFERENCES organization.company, entity_schema text NOT NULL, entity_table text NOT NULL, entity_id uuid NOT NULL, revision integer NOT NULL, snapshot jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), created_by_user_id uuid REFERENCES identity."user", UNIQUE (entity_schema, entity_table, entity_id, revision), CHECK (revision > 0), CHECK (jsonb_typeof(snapshot) = 'object'));
CREATE TABLE audit.system_operation (id uuid PRIMARY KEY, operation_type text NOT NULL, status text NOT NULL, started_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz, correlation_id uuid, details jsonb NOT NULL DEFAULT '{}'::jsonb, initiated_by_user_id uuid REFERENCES identity."user", CHECK (status IN ('started','completed','failed')), CHECK (completed_at IS NULL OR completed_at >= started_at), CHECK (jsonb_typeof(details) = 'object'));
CREATE INDEX system_operation_status_idx ON audit.system_operation (status, started_at DESC);
CREATE TRIGGER audit_event_append_only BEFORE UPDATE OR DELETE ON audit.audit_event FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();
CREATE TRIGGER entity_revision_append_only BEFORE UPDATE OR DELETE ON audit.entity_revision FOR EACH ROW EXECUTE FUNCTION audit.reject_update_or_delete();

CREATE VIEW analytics.leave_balance AS SELECT employee_id, company_id, leave_type_id, sum(amount) AS balance FROM leave.leave_ledger_entry GROUP BY employee_id, company_id, leave_type_id;
CREATE VIEW analytics.payroll_run_summary AS SELECT run.id AS payroll_run_id, run.company_id, run.payroll_period, run.status, count(payslip.id) AS payslip_count, coalesce(sum(payslip.net_amount), 0)::numeric(19,4) AS net_total FROM payroll.payroll_run run LEFT JOIN payroll.payslip payslip ON payslip.payroll_run_id = run.id GROUP BY run.id, run.company_id, run.payroll_period, run.status;

REVOKE ALL ON SCHEMA identity, organization, workforce, time, leave, compensation, payroll, audit, analytics FROM PUBLIC;
GRANT USAGE ON SCHEMA identity, organization, workforce, time, leave, compensation, payroll, audit, analytics TO peoplepay360_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA identity, organization, workforce, time, leave, compensation, payroll, audit TO peoplepay360_runtime;
GRANT USAGE ON SCHEMA analytics TO peoplepay360_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO peoplepay360_runtime, peoplepay360_analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA identity GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA organization GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA workforce GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA time GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA leave GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA compensation GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA payroll GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO peoplepay360_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO peoplepay360_runtime, peoplepay360_analytics;

INSERT INTO public.schema_migration (version) VALUES ('0001_peoplepay360_foundation');
COMMIT;
