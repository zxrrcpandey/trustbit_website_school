# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, today


def update_trending_products():
    """Daily task to update trending products cache"""
    settings = frappe.get_single("Trustbit Settings")
    days = settings.trending_days_range or 30
    limit = settings.trending_products_count or 8
    
    from_date = add_days(today(), -days)
    
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
                AND i.show_in_website = 1 
                AND i.disabled = 0
            )
        GROUP BY sii.item_code
        ORDER BY total_qty DESC
        LIMIT %s
    """, (from_date, limit), as_dict=True)
    
    frappe.cache().set_value("trustbit_trending_products", trending, expires_in_sec=86400)
    
    frappe.log_error(
        message=f"Updated trending products cache: {len(trending)} items",
        title="Trustbit Trending Products Updated"
    )
