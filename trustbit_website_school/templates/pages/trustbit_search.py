import frappe
from trustbit_website_school.api.webshop import get_categories, search_items

def get_context(context):
    """Search results page context"""
    settings = frappe.get_single("Trustbit Settings")
    query = frappe.form_dict.get("q", "").strip()
    item_type = frappe.form_dict.get("type", "")
    category = frappe.form_dict.get("category", "")
    
    context.no_cache = 1
    context.active_page = "search"
    context.settings = settings
    context.categories = get_categories()
    context.query = query
    context.type = item_type
    context.category = category
    
    # Search if query provided
    if query:
        filters = {}
        if item_type:
            filters["type"] = item_type
        if category:
            filters["item_group"] = category
        
        context.results = search_items(query, filters=filters, limit=50)
    else:
        context.results = []
    
    return context
