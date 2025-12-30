import frappe
from trustbit_website_school.api.webshop import (
    get_categories, get_latest_products, get_trending_products, 
    get_store_stats, get_active_banners
)

def get_context(context):
    """Homepage context"""
    settings = frappe.get_single("Trustbit Settings")
    
    context.no_cache = 1
    context.active_page = "home"
    context.settings = settings
    context.categories = get_categories()[:6]  # Top 6 categories
    context.stats = get_store_stats()
    context.banners = get_active_banners()
    
    # Latest products
    if settings.show_latest_products:
        context.latest_products = get_latest_products(settings.latest_products_count or 8)
    
    # Trending products
    if settings.show_trending_products:
        context.trending_products = get_trending_products(
            settings.trending_products_count or 8,
            settings.trending_days_range or 30
        )
    
    return context
