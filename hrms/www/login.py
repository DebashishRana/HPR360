"""Override default /login with PeoplePay360 role-picker login."""

import frappe
from frappe import _
from frappe.utils import get_url


no_cache = 1


def get_context(context):
	# Force the branded role login for /login
	frappe.local.flags.redirect_location = "/peoplepay360_login"
	raise frappe.Redirect
