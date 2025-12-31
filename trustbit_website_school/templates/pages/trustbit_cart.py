import frappe
from webshop.webshop.shopping_cart.cart import get_cart_quotation
from trustbit_website_school.api.webshop import get_categories

no_cache = 1

def get_context(context):
    """Cart page context"""
    settings = frappe.get_single("Trustbit Settings")

    context.no_cache = 1
    context.active_page = "cart"
    context.settings = settings
    context.categories = get_categories()

    # Get cart data from webshop
    try:
        cart_data = get_cart_quotation()
        context.update(cart_data)

        # Calculate totals
        if cart_data.get("doc") and cart_data["doc"].get("items"):
            context.cart_items = cart_data["doc"]["items"]
            context.cart_count = sum(item.qty for item in context.cart_items)
            context.cart_total = cart_data["doc"].get("grand_total", 0)
            context.net_total = cart_data["doc"].get("net_total", 0)
            context.taxes_total = cart_data["doc"].get("total_taxes_and_charges", 0)
        else:
            context.cart_items = []
            context.cart_count = 0
            context.cart_total = 0
            context.net_total = 0
            context.taxes_total = 0
    except Exception as e:
        frappe.log_error(f"Cart error: {str(e)}")
        context.cart_items = []
        context.cart_count = 0
        context.cart_total = 0
        context.net_total = 0
        context.taxes_total = 0
        context.cart_error = str(e)

    return context
