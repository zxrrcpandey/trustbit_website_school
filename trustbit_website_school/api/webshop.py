# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, flt, cint
import json


# ============================================
# HOMEPAGE APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def get_homepage_data():
    """Get all data needed for homepage"""
    settings = frappe.get_single("Trustbit Settings")
    
    return {
        "hero": {
            "image": settings.hero_image,
            "title": settings.hero_title,
            "subtitle": settings.hero_subtitle,
            "button_text": settings.hero_button_text,
            "button_link": settings.hero_button_link,
            "sale_banner": settings.sale_banner_text if settings.sale_banner_active else None,
        },
        "categories": get_categories(),
        "latest_products": get_latest_products(settings.latest_products_count or 8) if settings.show_latest_products else [],
        "trending_products": get_trending_products(settings.trending_products_count or 8, settings.trending_days_range or 30) if settings.show_trending_products else [],
        "banners": get_active_banners(),
        "stats": get_store_stats(),
    }


@frappe.whitelist(allow_guest=True)
def get_categories():
    """Get all item groups with product counts"""
    item_groups = frappe.get_all(
        "Item Group",
        filters={
            "is_group": 0
        },
        fields=["name", "item_group_name", "image", "route", "trustbit_icon", "trustbit_color"],
        order_by="name asc"
    )

    for group in item_groups:
        group["count"] = frappe.db.count("Item", {
            "item_group": group["name"],
            "disabled": 0
        })
        group["icon"] = group.get("trustbit_icon") or "📦"
        group["color"] = group.get("trustbit_color") or "#7c3aed"

    return item_groups


@frappe.whitelist(allow_guest=True)
def get_latest_products(limit=8):
    """Get latest products by creation date"""
    items = frappe.get_all(
        "Item",
        filters={
            "disabled": 0,
            "is_sales_item": 1
        },
        fields=[
            "item_code", "item_name", "item_group", "image",
            "description", "stock_uom"
        ],
        order_by="creation desc",
        limit_page_length=cint(limit)
    )

    for item in items:
        item["price"] = get_item_price(item["item_code"])
        item["stock"] = get_item_stock(item["item_code"])
        item["tag"] = "New Arrival"

    return items


@frappe.whitelist(allow_guest=True)
def get_trending_products(limit=8, days=30):
    """Get trending products based on sales in last N days"""
    from_date = add_days(today(), -cint(days))
    
    trending = frappe.db.sql("""
        SELECT
            sii.item_code,
            SUM(sii.qty) as total_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
            AND si.posting_date >= %s
            AND EXISTS (
                SELECT 1 FROM `tabItem` i
                WHERE i.item_code = sii.item_code
                AND i.disabled = 0
            )
        GROUP BY sii.item_code
        ORDER BY total_qty DESC
        LIMIT %s
    """, (from_date, cint(limit)), as_dict=True)
    
    items = []
    for t in trending:
        item = frappe.get_doc("Item", t["item_code"])
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "item_group": item.item_group,
            "image": item.image,
            "price": get_item_price(item.item_code),
            "stock": get_item_stock(item.item_code),
            "sales": int(t["total_qty"])
        })

    return items


@frappe.whitelist(allow_guest=True)
def get_active_banners():
    """Get active banners"""
    from trustbit_website_school.trustbit_website_school.doctype.trustbit_banner.trustbit_banner import get_banners
    return get_banners()


@frappe.whitelist(allow_guest=True)
def get_store_stats():
    """Get store statistics"""
    return {
        "total_products": frappe.db.count("Item", {"disabled": 0, "is_sales_item": 1}),
        "total_bundles": frappe.db.count("Product Bundle"),
        "total_categories": frappe.db.count("Item Group", {"is_group": 0}),
    }


# ============================================
# SEARCH APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def search_items(query, filters=None, limit=10):
    """Fast search for 25K+ items"""
    if not query or len(query) < 2:
        return []
    
    query = query.strip()
    limit = cint(limit) or 10
    
    if filters:
        if isinstance(filters, str):
            filters = json.loads(filters)
    else:
        filters = {}
    
    search_conditions = """
        (
            item_code LIKE %(search)s
            OR item_name LIKE %(search)s
            OR barcode LIKE %(search)s
            OR description LIKE %(search)s
        )
    """
    
    base_filters = """
        disabled = 0
        AND is_sales_item = 1
    """
    
    additional_filters = ""
    if filters.get("item_group"):
        additional_filters += f" AND item_group = %(item_group)s"
    if filters.get("school"):
        additional_filters += f" AND trustbit_school = %(school)s"
    if filters.get("class"):
        additional_filters += f" AND trustbit_class = %(class)s"
    
    items = frappe.db.sql(f"""
        SELECT
            item_code, item_name, item_group, image,
            description, stock_uom, barcode
        FROM `tabItem`
        WHERE {base_filters}
            AND {search_conditions}
            {additional_filters}
        ORDER BY
            CASE
                WHEN item_code = %(exact)s THEN 1
                WHEN item_code LIKE %(starts)s THEN 2
                WHEN item_name LIKE %(starts)s THEN 3
                ELSE 4
            END,
            item_name ASC
        LIMIT %(limit)s
    """, {
        "search": f"%{query}%",
        "exact": query,
        "starts": f"{query}%",
        "item_group": filters.get("item_group"),
        "school": filters.get("school"),
        "class": filters.get("class"),
        "limit": limit
    }, as_dict=True)

    for item in items:
        item["price"] = get_item_price(item["item_code"])
        item["stock"] = get_item_stock(item["item_code"])
        item["type"] = "item"
    
    if not filters.get("type") or filters.get("type") == "bundles":
        bundles = search_bundles(query, limit=5)
        items = bundles + items
    
    return items[:limit]


def search_bundles(query, limit=5):
    """Search product bundles"""
    bundles = frappe.db.sql("""
        SELECT
            pb.name as item_code,
            pb.new_item_code,
            i.item_name,
            i.image,
            i.description
        FROM `tabProduct Bundle` pb
        INNER JOIN `tabItem` i ON i.item_code = pb.new_item_code
        WHERE (
            pb.new_item_code LIKE %(search)s
            OR i.item_name LIKE %(search)s
        )
        AND i.disabled = 0
        LIMIT %(limit)s
    """, {
        "search": f"%{query}%",
        "limit": limit
    }, as_dict=True)

    for bundle in bundles:
        bundle["item_code"] = bundle["new_item_code"]
        bundle["type"] = "bundle"
        bundle["price"] = get_bundle_price(bundle["item_code"])
        bundle["item_count"] = frappe.db.count("Product Bundle Item", {"parent": bundle["item_code"]})

    return bundles


# ============================================
# BUNDLE APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def get_bundles(limit=20, page=1):
    """Get all product bundles with details"""
    offset = (cint(page) - 1) * cint(limit)
    
    bundles = frappe.db.sql("""
        SELECT
            pb.name,
            pb.new_item_code as item_code,
            i.item_name,
            i.item_group,
            i.image,
            i.description,
            i.trustbit_school as school,
            i.trustbit_class as class
        FROM `tabProduct Bundle` pb
        INNER JOIN `tabItem` i ON i.item_code = pb.new_item_code
        WHERE i.disabled = 0
        ORDER BY i.item_name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """, {"limit": cint(limit), "offset": offset}, as_dict=True)

    for bundle in bundles:
        bundle["items"] = get_bundle_items(bundle["item_code"])
        bundle["price"] = sum(item["amount"] for item in bundle["items"])
        bundle["item_count"] = len(bundle["items"])
        bundle["availability"] = get_bundle_availability(bundle["item_code"])
    
    total = frappe.db.count("Product Bundle")
    
    return {
        "bundles": bundles,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@frappe.whitelist(allow_guest=True)
def get_bundle_detail(item_code):
    """Get detailed bundle information"""
    if not frappe.db.exists("Product Bundle", {"new_item_code": item_code}):
        frappe.throw(_("Bundle not found"))
    
    item = frappe.get_doc("Item", item_code)
    bundle_items = get_bundle_items(item_code)

    return {
        "item_code": item_code,
        "item_name": item.item_name,
        "description": item.description,
        "image": item.image,
        "school": item.get("trustbit_school"),
        "class": item.get("trustbit_class"),
        "items": bundle_items,
        "total_price": sum(i["amount"] for i in bundle_items),
        "item_count": len(bundle_items),
        "availability": get_bundle_availability(item_code),
        "out_of_stock_items": [i for i in bundle_items if i["stock"] <= 0]
    }


@frappe.whitelist(allow_guest=True)
def get_bundle_items(item_code):
    """Get items in a product bundle with stock and price"""
    bundle_items = frappe.get_all(
        "Product Bundle Item",
        filters={"parent": item_code},
        fields=["item_code", "qty", "description", "uom"]
    )
    
    items = []
    for bi in bundle_items:
        item = frappe.get_doc("Item", bi["item_code"])
        price = get_item_price(bi["item_code"])
        stock = get_item_stock(bi["item_code"])
        
        items.append({
            "item_code": bi["item_code"],
            "item_name": item.item_name,
            "qty": bi["qty"],
            "uom": bi["uom"] or item.stock_uom,
            "rate": price,
            "amount": price * bi["qty"],
            "stock": stock,
            "image": item.image,
            "in_stock": stock >= bi["qty"]
        })
    
    return items


@frappe.whitelist(allow_guest=True)
def get_bundle_availability(item_code):
    """Calculate how many complete bundles can be made from stock"""
    bundle_items = frappe.get_all(
        "Product Bundle Item",
        filters={"parent": item_code},
        fields=["item_code", "qty"]
    )
    
    if not bundle_items:
        return 0
    
    min_sets = float('inf')
    limiting_item = None
    
    for bi in bundle_items:
        stock = get_item_stock(bi["item_code"])
        sets_possible = stock // bi["qty"] if bi["qty"] > 0 else 0
        
        if sets_possible < min_sets:
            min_sets = sets_possible
            limiting_item = bi["item_code"]
    
    return {
        "available_sets": int(min_sets) if min_sets != float('inf') else 0,
        "limiting_item": limiting_item
    }


# ============================================
# CART APIs
# ============================================

@frappe.whitelist()
def add_bundle_to_cart(item_code, qty=1):
    """Add all bundle items to cart"""
    from webshop.webshop.shopping_cart.cart import add_to_cart
    
    bundle_items = get_bundle_items(item_code)
    added_items = []
    skipped_items = []
    
    for item in bundle_items:
        item_qty = item["qty"] * cint(qty)
        
        if item["stock"] >= item_qty:
            try:
                add_to_cart(item["item_code"])
                if item_qty > 1:
                    from webshop.webshop.shopping_cart.cart import update_cart
                    update_cart(item["item_code"], item_qty)
                
                added_items.append({
                    "item_code": item["item_code"],
                    "item_name": item["item_name"],
                    "qty": item_qty
                })
            except Exception as e:
                skipped_items.append({
                    "item_code": item["item_code"],
                    "item_name": item["item_name"],
                    "reason": str(e)
                })
        else:
            skipped_items.append({
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "reason": f"Only {item['stock']} available"
            })
    
    return {
        "success": len(added_items) > 0,
        "added": added_items,
        "skipped": skipped_items,
        "message": f"Added {len(added_items)} items to cart" + 
                   (f", {len(skipped_items)} items skipped" if skipped_items else "")
    }


# ============================================
# CATEGORY APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def get_category_products(category, limit=20, page=1, sort_by="item_name"):
    """Get products in a category"""
    offset = (cint(page) - 1) * cint(limit)
    
    valid_sorts = ["item_name", "creation desc", "modified desc"]
    if sort_by not in valid_sorts:
        sort_by = "item_name"
    
    items = frappe.get_all(
        "Item",
        filters={
            "item_group": category,
            "disabled": 0
        },
        fields=[
            "item_code", "item_name", "image",
            "description", "stock_uom"
        ],
        order_by=sort_by,
        limit_page_length=cint(limit),
        limit_start=offset
    )

    for item in items:
        item["price"] = get_item_price(item["item_code"])
        item["stock"] = get_item_stock(item["item_code"])

    total = frappe.db.count("Item", {
        "item_group": category,
        "disabled": 0
    })
    
    category_info = frappe.get_doc("Item Group", category)
    
    return {
        "category": {
            "name": category,
            "label": category_info.item_group_name,
            "image": category_info.image,
            "icon": category_info.get("trustbit_icon") or "📦"
        },
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


# ============================================
# ORDER APIs
# ============================================

@frappe.whitelist()
def get_order_history(limit=20, page=1):
    """Get customer's order history"""
    customer = get_current_customer()
    if not customer:
        return {"orders": [], "message": "Please login to view orders"}
    
    offset = (cint(page) - 1) * cint(limit)
    
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer},
        fields=[
            "name", "transaction_date", "status", "grand_total",
            "total_qty", "delivery_status"
        ],
        order_by="creation desc",
        limit_page_length=cint(limit),
        limit_start=offset
    )
    
    for order in orders:
        order["items_count"] = frappe.db.count("Sales Order Item", {"parent": order["name"]})
        bundle_items = frappe.db.sql("""
            SELECT soi.item_code, i.item_name
            FROM `tabSales Order Item` soi
            INNER JOIN `tabProduct Bundle` pb ON pb.new_item_code = soi.item_code
            INNER JOIN `tabItem` i ON i.item_code = soi.item_code
            WHERE soi.parent = %s
            LIMIT 1
        """, order["name"], as_dict=True)
        
        if bundle_items:
            order["bundle"] = bundle_items[0]["item_name"]
    
    total = frappe.db.count("Sales Order", {"customer": customer})
    
    return {
        "orders": orders,
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit
    }


@frappe.whitelist(allow_guest=True)
def track_order(order_id):
    """Track order status"""
    if not frappe.db.exists("Sales Order", order_id):
        return {"found": False, "message": "Order not found"}
    
    order = frappe.get_doc("Sales Order", order_id)
    
    delivery_info = {}
    if order.status in ["Completed", "Closed"] or order.delivery_status == "Fully Delivered":
        delivery_notes = frappe.get_all(
            "Delivery Note",
            filters={"docstatus": 1},
            fields=["name", "posting_date", "transporter_name", "lr_no"]
        )
        if delivery_notes:
            delivery_info = delivery_notes[0]
    
    return {
        "found": True,
        "order": {
            "id": order.name,
            "date": order.transaction_date,
            "status": order.status,
            "delivery_status": order.delivery_status,
            "total": order.grand_total,
            "items_count": len(order.items),
        },
        "timeline": get_order_timeline(order),
        "delivery": delivery_info
    }


def get_order_timeline(order):
    """Build order timeline"""
    timeline = [
        {
            "step": "Order Placed",
            "done": True,
            "date": str(order.transaction_date)
        },
        {
            "step": "Processing",
            "done": order.status not in ["Draft", "Cancelled"],
            "date": str(order.transaction_date) if order.status not in ["Draft", "Cancelled"] else None
        },
        {
            "step": "Shipped",
            "done": order.delivery_status in ["Partially Delivered", "Fully Delivered"],
            "date": None
        },
        {
            "step": "Delivered",
            "done": order.delivery_status == "Fully Delivered" or order.status in ["Completed", "Closed"],
            "date": None
        }
    ]
    
    return timeline


# ============================================
# CONTACT APIs
# ============================================

@frappe.whitelist(allow_guest=True)
def submit_contact_form(name, email, phone, message, subject="Website Enquiry"):
    """Submit contact form"""
    doc = frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "subject": f"[Website] {subject}",
        "content": f"""
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <hr>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
        """,
        "sender": email,
        "sent_or_received": "Received"
    })
    doc.insert(ignore_permissions=True)
    
    settings = frappe.get_single("Trustbit Settings")
    if settings.email:
        frappe.sendmail(
            recipients=[settings.email],
            subject=f"[Website] New Contact Form: {subject}",
            message=f"""
                <h3>New contact form submission</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <hr>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
            """
        )
    
    return {"success": True, "message": "Thank you! We will get back to you soon."}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_item_price(item_code, price_list=None):
    """Get item selling price"""
    if not price_list:
        price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list") or "Standard Selling"
    
    price = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": price_list, "selling": 1},
        "price_list_rate"
    )
    
    return flt(price) or 0


def get_item_stock(item_code, warehouse=None):
    """Get item stock quantity"""
    if not warehouse:
        warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    
    if warehouse:
        stock = frappe.db.get_value(
            "Bin",
            {"item_code": item_code, "warehouse": warehouse},
            "actual_qty"
        )
    else:
        stock = frappe.db.sql("""
            SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code = %s
        """, item_code)[0][0]
    
    return flt(stock) or 0


def get_bundle_price(item_code):
    """Get total price of bundle items"""
    bundle_items = get_bundle_items(item_code)
    return sum(item["amount"] for item in bundle_items)


def get_current_customer():
    """Get current logged in customer"""
    if frappe.session.user == "Guest":
        return None
    
    customer = frappe.db.get_value(
        "Customer",
        {"user": frappe.session.user},
        "name"
    )
    
    return customer
