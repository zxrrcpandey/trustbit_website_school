import frappe
from frappe.utils import cint
from trustbit_website_school.api.webshop import get_categories, get_order_history

def get_context(context):
    """Order history page context"""
    settings = frappe.get_single("Trustbit Settings")
    page = cint(frappe.form_dict.get("page", 1))
    
    context.no_cache = 1
    context.active_page = "orders"
    context.settings = settings
    context.categories = get_categories()
    
    # Only fetch orders if logged in
    if frappe.session.user != "Guest":
        result = get_order_history(limit=10, page=page)
        context.orders = result.get("orders", [])
        context.total = result.get("total", 0)
        context.page = page
        context.total_pages = result.get("total_pages", 1)
    else:
        context.orders = []
        context.total = 0
        context.page = 1
        context.total_pages = 1
    
    return context
