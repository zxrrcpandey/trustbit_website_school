import frappe
from trustbit_website_school.api.webshop import get_bundle_detail, get_categories

def get_context(context):
    """Bundle detail page context"""
    settings = frappe.get_single("Trustbit Settings")
    bundle_id = frappe.form_dict.get("bundle_id")
    
    if not bundle_id:
        frappe.throw("Bundle not found", frappe.PageDoesNotExistError)
    
    try:
        bundle = get_bundle_detail(bundle_id)
    except Exception:
        frappe.throw("Bundle not found", frappe.PageDoesNotExistError)
    
    context.no_cache = 1
    context.active_page = "bundles"
    context.settings = settings
    context.bundle = bundle
    context.categories = get_categories()
    
    return context
