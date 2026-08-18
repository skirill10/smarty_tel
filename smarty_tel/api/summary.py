import frappe
from frappe import _
from frappe.utils import add_days, now_datetime

CACHE_KEY = "smarty_tel:home_summary:{user}"
CACHE_TTL_SECONDS = 45

CRM_ROLES = {"Sales User", "Sales Manager", "Sales Master Manager", "System Manager"}
SUPPORT_ROLES = {"Agent", "Agent Manager", "System Manager"}


@frappe.whitelist()
def get_summary():
	"""Permission-aware, cached counts for the Raven sidebar badges (open deals,
	open tickets, unread chat). Read-only, no business logic duplicated from
	CRM/HelpDesk/Raven — only their own status/type classifications are used."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	cache_key = CACHE_KEY.format(user=frappe.session.user)
	cached = frappe.cache().get_value(cache_key)
	if cached is not None:
		return cached

	roles = set(frappe.get_roles())
	result = {}

	if roles & CRM_ROLES:
		result["crm"] = _get_crm_summary()

	if roles & SUPPORT_ROLES:
		result["support"] = _get_support_summary()

	result["chat"] = _get_chat_summary()

	frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL_SECONDS)
	return result


def _get_crm_summary():
	open_statuses = frappe.get_all(
		"CRM Deal Status",
		filters={"type": ["not in", ["Won", "Lost"]]},
		pluck="name",
	)
	open_deals = frappe.db.count(
		"CRM Deal",
		filters={
			"deal_owner": frappe.session.user,
			"status": ["in", open_statuses or [""]],
		},
	)
	new_leads = frappe.db.count(
		"CRM Lead",
		filters={"creation": [">=", add_days(now_datetime(), -7)]},
	)
	return {"open_deals": open_deals, "new_leads_this_week": new_leads}


def _get_support_summary():
	open_statuses = frappe.get_all(
		"HD Ticket Status",
		filters={"category": ["in", ["Open", "Paused"]]},
		pluck="label_agent",
	)
	open_tickets = frappe.db.count(
		"HD Ticket",
		filters={
			"_assign": ["like", f"%{frappe.session.user}%"],
			"status": ["in", open_statuses or [""]],
		},
	)
	return {"open_tickets": open_tickets}


def _get_chat_summary():
	try:
		channels = frappe.get_attr("raven.api.raven_message.get_unread_count_for_channels")()
	except Exception:
		frappe.log_error(title="smarty_tel: failed to fetch Raven unread summary")
		return {"unread_channels": 0, "unread_messages": 0}

	channels = channels or []
	unread_messages = sum(c.get("unread_count", 0) for c in channels)
	unread_channels = sum(1 for c in channels if c.get("unread_count", 0) > 0)
	return {"unread_channels": unread_channels, "unread_messages": unread_messages}
