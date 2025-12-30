# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrustbitTeamMember(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_team_members():
    """Get active team members for frontend"""
    return frappe.get_all(
        "Trustbit Team Member",
        filters={"is_active": 1},
        fields=["member_name", "role", "photo", "bio"],
        order_by="display_order asc"
    )
