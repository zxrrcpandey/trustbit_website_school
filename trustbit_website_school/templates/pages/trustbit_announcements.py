import frappe
from trustbit_website_school.api.webshop import get_categories
from trustbit_website_school.trustbit_website_school.doctype.trustbit_announcement.trustbit_announcement import get_announcements

def get_context(context):
    """Announcements page context"""
    settings = frappe.get_single("Trustbit Settings")
    
    context.no_cache = 1
    context.active_page = "announcements"
    context.settings = settings
    context.announcements = get_announcements(limit=50)
    context.categories = get_categories()
    
    return context
