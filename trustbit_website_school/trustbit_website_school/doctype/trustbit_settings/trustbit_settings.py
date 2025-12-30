# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrustbitSettings(Document):
    pass


def get_settings():
    """Get Trustbit Settings as dict"""
    return frappe.get_single("Trustbit Settings").as_dict()


@frappe.whitelist(allow_guest=True)
def get_public_settings():
    """Get public settings for frontend"""
    settings = frappe.get_single("Trustbit Settings")
    
    return {
        "hero": {
            "image": settings.hero_image,
            "title": settings.hero_title,
            "subtitle": settings.hero_subtitle,
            "button_text": settings.hero_button_text,
            "button_link": settings.hero_button_link,
            "sale_banner_text": settings.sale_banner_text if settings.sale_banner_active else None,
        },
        "contact": {
            "store_name": settings.store_name,
            "address": settings.store_address,
            "phone": settings.phone,
            "whatsapp": settings.whatsapp,
            "email": settings.email,
            "hours": settings.store_hours,
            "map_embed": settings.google_map_embed,
        },
        "about": {
            "story": settings.company_story,
            "mission": settings.mission_statement,
            "years": settings.years_in_business,
            "schools": settings.total_schools_served,
            "image": settings.about_image,
        },
        "social": {
            "facebook": settings.facebook_url,
            "instagram": settings.instagram_url,
            "twitter": settings.twitter_url,
            "youtube": settings.youtube_url,
        },
        "footer": {
            "about_text": settings.footer_about_text,
            "copyright": settings.copyright_text,
        }
    }
