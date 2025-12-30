import frappe
from frappe.utils import cint
from trustbit_website_school.api.webshop import get_bundles, get_categories

def get_context(context):
    """Bundles page context"""
    settings = frappe.get_single("Trustbit Settings")
    page = cint(frappe.form_dict.get("page", 1))
    
    # Get bundles with pagination
    result = get_bundles(limit=12, page=page)
    
    # Get unique schools and classes for filters
    schools = frappe.db.sql("""
        SELECT DISTINCT i.trustbit_school 
        FROM `tabProduct Bundle` pb
        INNER JOIN `tabItem` i ON i.item_code = pb.new_item_code
        WHERE i.trustbit_school IS NOT NULL AND i.trustbit_school != ''
        ORDER BY i.trustbit_school
    """, as_dict=True)
    
    classes = frappe.db.sql("""
        SELECT DISTINCT i.trustbit_class 
        FROM `tabProduct Bundle` pb
        INNER JOIN `tabItem` i ON i.item_code = pb.new_item_code
        WHERE i.trustbit_class IS NOT NULL AND i.trustbit_class != ''
        ORDER BY i.trustbit_class
    """, as_dict=True)
    
    context.no_cache = 1
    context.active_page = "bundles"
    context.settings = settings
    context.bundles = result["bundles"]
    context.total = result["total"]
    context.page = result["page"]
    context.total_pages = result["total_pages"]
    context.schools = [s["trustbit_school"] for s in schools]
    context.classes = [c["trustbit_class"] for c in classes]
    context.categories = get_categories()
    
    return context
