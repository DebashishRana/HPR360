"""Serve PeoplePay360 branded login (no website chrome)."""

import frappe
from frappe import _


def get_context(context):
	# Standalone page — hide navbar/footer from website template if used
	context.no_cache = 1
	context.no_header = 1
	context.no_sidebar = 1
	context.no_breadcrumbs = 1
	context.title = _("PeoplePay360 Sign In")

	# If someone hits this while already logged in, send them home
	if frappe.session.user != "Guest":
		from hrms.peoplepay360.roles import get_home_route_for_user

		frappe.local.flags.redirect_location = get_home_route_for_user()
		raise frappe.Redirect
