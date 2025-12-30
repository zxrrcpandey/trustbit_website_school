import frappe
from trustbit_website_school.api.webshop import get_categories

def get_context(context):
    """Contact page context"""
    settings = frappe.get_single("Trustbit Settings")
    
    context.no_cache = 1
    context.active_page = "contact"
    context.settings = settings
    context.categories = get_categories()
    
    return context
