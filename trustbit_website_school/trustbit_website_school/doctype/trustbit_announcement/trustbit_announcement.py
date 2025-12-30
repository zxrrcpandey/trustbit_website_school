# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate


class TrustbitAnnouncement(Document):
    def validate(self):
        if self.expiry_date and getdate(self.expiry_date) < getdate(self.publish_date):
            frappe.throw("Expiry date cannot be before publish date")


@frappe.whitelist(allow_guest=True)
def get_announcements(limit=10):
    """Get active announcements for frontend"""
    today_date = today()
    
    announcements = frappe.get_all(
        "Trustbit Announcement",
        filters={
            "is_active": 1,
            "publish_date": ["<=", today_date],
        },
        or_filters=[
            ["expiry_date", "is", "not set"],
            ["expiry_date", ">=", today_date]
        ],
        fields=[
            "name", "title", "content", "announcement_type",
            "publish_date", "is_pinned", "image"
        ],
        order_by="is_pinned desc, publish_date desc",
        limit_page_length=limit
    )
    
    return announcements
