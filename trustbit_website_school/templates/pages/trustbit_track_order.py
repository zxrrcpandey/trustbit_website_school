import frappe
from trustbit_website_school.api.webshop import get_categories, track_order

def get_context(context):
    """Order tracking page context"""
    settings = frappe.get_single("Trustbit Settings")
    order_id = frappe.form_dict.get("order_id")
    
    context.no_cache = 1
    context.active_page = "orders"
    context.settings = settings
    context.categories = get_categories()
    context.order_id = order_id
    
    # Track order if ID provided
    if order_id:
        result = track_order(order_id)
        if result.get("found"):
            context.order = result.get("order")
            context.timeline = result.get("timeline")
            context.delivery = result.get("delivery")
        else:
            context.order = None
    else:
        context.order = None
    
    return context
