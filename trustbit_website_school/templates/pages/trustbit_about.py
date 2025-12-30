import frappe
from trustbit_website_school.api.webshop import get_categories
from trustbit_website_school.trustbit_website_school.doctype.trustbit_team_member.trustbit_team_member import get_team_members

def get_context(context):
    """About Us page context"""
    settings = frappe.get_single("Trustbit Settings")
    
    context.no_cache = 1
    context.active_page = "about"
    context.settings = settings
    context.team_members = get_team_members()
    context.categories = get_categories()
    
    return context
