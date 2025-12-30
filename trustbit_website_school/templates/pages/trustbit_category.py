import frappe
from frappe.utils import cint
from trustbit_website_school.api.webshop import get_category_products, get_categories

def get_context(context):
    """Category products page context"""
    settings = frappe.get_single("Trustbit Settings")
    category = frappe.form_dict.get("category")
    page = cint(frappe.form_dict.get("page", 1))
    sort_by = frappe.form_dict.get("sort", "item_name")
    
    if not category:
        frappe.throw("Category not found", frappe.PageDoesNotExistError)
    
    # URL decode category name
    import urllib.parse
    category = urllib.parse.unquote(category)
    
    if not frappe.db.exists("Item Group", category):
        frappe.throw("Category not found", frappe.PageDoesNotExistError)
    
    result = get_category_products(category, limit=20, page=page, sort_by=sort_by)
    
    context.no_cache = 1
    context.active_page = "categories"
    context.settings = settings
    context.category = result["category"]
    context.products = result["items"]
    context.total = result["total"]
    context.page = result["page"]
    context.total_pages = result["total_pages"]
    context.sort_by = sort_by
    context.categories = get_categories()
    
    return context
