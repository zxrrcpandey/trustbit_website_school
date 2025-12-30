import frappe
from trustbit_website_school.api.webshop import get_categories

def get_context(context):
    """Categories listing page context"""
    settings = frappe.get_single("Trustbit Settings")
    
    categories = get_categories()
    
    # Sort by count for popular
    popular = sorted(categories, key=lambda x: x.get("count", 0), reverse=True)
    
    # Total products
    total_products = sum(c.get("count", 0) for c in categories)
    
    context.no_cache = 1
    context.active_page = "categories"
    context.settings = settings
    context.categories = categories
    context.popular_categories = popular[:4]
    context.total_products = total_products
    
    return context
