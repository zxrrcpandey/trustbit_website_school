# Copyright (c) 2024, Trustbit and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    """Run after app installation"""
    create_custom_item_fields()
    create_custom_item_group_fields()
    setup_default_settings()
    frappe.db.commit()
    print("Trustbit Website School installed successfully!")


def create_custom_item_fields():
    """Add custom fields to Item doctype"""
    custom_fields = {
        "Item": [
            {
                "fieldname": "trustbit_section",
                "fieldtype": "Section Break",
                "label": "Trustbit Webshop",
                "insert_after": "website_specifications"
            },
            {
                "fieldname": "trustbit_school",
                "fieldtype": "Data",
                "label": "School Name",
                "insert_after": "trustbit_section",
                "description": "For school-specific products and bundles"
            },
            {
                "fieldname": "trustbit_class",
                "fieldtype": "Data",
                "label": "Class",
                "insert_after": "trustbit_school",
                "description": "e.g., Class 1, Class 8, UKG"
            },
            {
                "fieldname": "trustbit_column_break",
                "fieldtype": "Column Break",
                "insert_after": "trustbit_class"
            },
            {
                "fieldname": "trustbit_is_featured",
                "fieldtype": "Check",
                "label": "Featured on Homepage",
                "insert_after": "trustbit_column_break",
                "default": 0
            },
        ]
    }
    
    create_custom_fields(custom_fields)
    print("Custom Item fields created")


def create_custom_item_group_fields():
    """Add custom fields to Item Group doctype"""
    custom_fields = {
        "Item Group": [
            {
                "fieldname": "trustbit_icon",
                "fieldtype": "Data",
                "label": "Display Icon (Emoji)",
                "insert_after": "image",
                "description": "Emoji icon for category display, e.g., 📚, ✏️, 🎒"
            },
            {
                "fieldname": "trustbit_color",
                "fieldtype": "Color",
                "label": "Display Color",
                "insert_after": "trustbit_icon",
                "description": "Color for category cards"
            },
        ]
    }
    
    create_custom_fields(custom_fields)
    print("Custom Item Group fields created")


def setup_default_settings():
    """Create default Trustbit Settings"""
    settings = frappe.get_single("Trustbit Settings")
    settings.store_name = "School Supplies Store"
    settings.hero_title = "Everything Your Child Needs for School"
    settings.hero_subtitle = "Books, stationery, bags & complete school bundles. Shop from 25,000+ products with fast delivery!"
    settings.hero_button_text = "Shop Bundles"
    settings.hero_button_link = "/shop/bundles"
    settings.sale_banner_text = "🎉 Back to School Sale - 20% OFF"
    settings.sale_banner_active = 1
    settings.show_latest_products = 1
    settings.latest_products_count = 8
    settings.show_trending_products = 1
    settings.trending_products_count = 8
    settings.trending_days_range = 30
    settings.years_in_business = 10
    settings.total_schools_served = 50
    settings.footer_about_text = "Your trusted partner for all school supplies. Quality products, competitive prices, and excellent service."
    settings.copyright_text = "© 2024 All rights reserved."
    settings.save()
    print("Default Trustbit Settings created")
