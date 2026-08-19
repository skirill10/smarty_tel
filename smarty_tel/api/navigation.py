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
		# Children mirror CRM's own real sidebar exactly (source: frontend/src/
		# components/Layouts/AppSidebar.vue `links` + frontend/src/router.js),
		# not an invented subset, so the unified panel never drifts from what
		# CRM itself actually offers.
		"id": "crm",
		"label": "Smarty Sales",
		"icon": "users",
		"route": "/crm",
		"roles": ["Sales User", "Sales Manager", "Sales Master Manager", "System Manager"],
		"children": [
			{"label": "Notifications", "route": "/crm", "icon": "bell"},
			{"label": "Dashboard", "route": "/crm/dashboard", "icon": "layout-dashboard"},
			{"label": "Leads", "route": "/crm/leads/view", "icon": "user-plus"},
			{"label": "Deals", "route": "/crm/deals/view", "icon": "handshake"},
			{"label": "Contacts", "route": "/crm/contacts/view", "icon": "contact"},
			{"label": "Organizations", "route": "/crm/organizations/view", "icon": "building"},
			{"label": "Notes", "route": "/crm/notes/view", "icon": "file-text"},
			{"label": "Tasks", "route": "/crm/tasks/view", "icon": "check-square"},
			{"label": "Calendar", "route": "/crm/calendar", "icon": "calendar"},
			{"label": "Call Logs", "route": "/crm/call-logs/view", "icon": "phone"},
		],
	},
	{
		# Children mirror HelpDesk's own agent-portal sidebar (source: desk/src/
		# components/layouts/layoutSettings.ts `agentPortalSidebarOptions` +
		# desk/src/router/index.ts). "Public Views" isn't a distinct HelpDesk
		# route today (ticket views live inside Tickets), so it points there
		# rather than a fabricated path.
		"id": "support",
		"label": "Support",
		"icon": "life-buoy",
		"route": "/helpdesk",
		"roles": ["Agent", "Agent Manager", "System Manager"],
		"children": [
			{"label": "Search", "route": "/helpdesk/search", "icon": "search"},
			{"label": "Home", "route": "/helpdesk/home", "icon": "home"},
			{"label": "Dashboard", "route": "/helpdesk/dashboard", "icon": "layout-dashboard"},
			{"label": "Tickets", "route": "/helpdesk/tickets", "icon": "ticket"},
			{"label": "Knowledge Base", "route": "/helpdesk/kb", "icon": "book-open"},
			{"label": "Customers", "route": "/helpdesk/customers", "icon": "building"},
			{"label": "Contacts", "route": "/helpdesk/contacts", "icon": "users"},
			{"label": "Public Views", "route": "/helpdesk/tickets", "icon": "eye"},
		],
	},
	{
		"id": "chat",
		"label": "Smarty Chat",
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
