# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class TrustbitBanner(Document):
    def validate(self):
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw("End date cannot be before start date")


@frappe.whitelist(allow_guest=True)
def get_banners():
    """Get active banners for frontend"""
    today_date = today()
    
    banners = frappe.get_all(
        "Trustbit Banner",
        filters={"is_active": 1},
        or_filters=[
            ["start_date", "is", "not set"],
            ["start_date", "<=", today_date]
        ],
        fields=[
            "name", "title", "subtitle", "image", "image_alt_text",
            "button_text", "button_link", "button_style", "open_in_new_tab"
        ],
        order_by="display_order asc"
    )
    
    # Filter out expired banners
    active_banners = []
    for banner in banners:
        doc = frappe.get_doc("Trustbit Banner", banner.name)
        if not doc.end_date or getdate(doc.end_date) >= getdate(today_date):
            active_banners.append(banner)
    
    return active_banners
