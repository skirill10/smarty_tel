import frappe
from frappe import _

# Single source of truth for smarty.tel's top-level navigation.
# `roles` is the set of roles that may see an entry; omit/empty = visible to
# any logged-in user. Raven (the shell) and CRM/HelpDesk (embedded) all read
# this same schema so nav never has to be hand-kept-in-sync across apps.
NAV_SCHEMA = [
	{
		"id": "home",
		"label": "Home",
		"icon": "home",
		"route": "/",
	},
	{
		"id": "crm",
		"label": "CRM",
		"icon": "users",
		"route": "/crm",
		"roles": ["Sales User", "Sales Manager", "Sales Master Manager", "System Manager"],
		"children": [
			{"label": "Leads", "route": "/crm/leads"},
			{"label": "Deals", "route": "/crm/deals"},
			{"label": "Contacts", "route": "/crm/contacts"},
			{"label": "Organizations", "route": "/crm/organizations"},
		],
	},
	{
		"id": "support",
		"label": "Support",
		"icon": "life-buoy",
		"route": "/helpdesk",
		"roles": ["Agent", "Agent Manager", "System Manager"],
	},
	{
		"id": "chat",
		"label": "Chat",
		"icon": "message-circle",
		"route": "/raven",
	},
]


@frappe.whitelist()
def get_navigation():
	"""Return the nav entries visible to the current user, role-filtered server-side."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	user_roles = set(frappe.get_roles())
	visible = []
	for item in NAV_SCHEMA:
		required_roles = item.get("roles")
		if required_roles and not (user_roles & set(required_roles)):
			continue
		visible.append({k: v for k, v in item.items() if k != "roles"})

	return visible
