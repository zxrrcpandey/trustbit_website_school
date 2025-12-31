app_name = "trustbit_website_school"
app_title = "Trustbit Website School"
app_publisher = "Trustbit"
app_description = "Custom School Supplies Webshop with Product Bundles"
app_email = "info@trustbit.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext", "webshop"]

# Includes in <head>
# ------------------

app_include_css = "/assets/trustbit_website_school/css/trustbit_webshop.css"
app_include_js = "/assets/trustbit_website_school/js/trustbit_webshop.js"

# Website includes
web_include_css = "/assets/trustbit_website_school/css/trustbit_webshop.css"
web_include_js = "/assets/trustbit_website_school/js/trustbit_webshop.js"

# Installation
# ------------

after_install = "trustbit_website_school.install.after_install"

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "trustbit_website_school.tasks.update_trending_products"
    ],
}

# Fixtures
# --------

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["name", "in", [
                "Item-trustbit_school",
                "Item-trustbit_class",
                "Item-trustbit_is_featured",
                "Item Group-trustbit_icon",
                "Item Group-trustbit_color",
            ]]
        ]
    },
]

# Website Route Rules
# -------------------

website_route_rules = [
    {"from_route": "/shop", "to_route": "trustbit_shop"},
    {"from_route": "/shop/bundles", "to_route": "trustbit_bundles"},
    {"from_route": "/shop/bundles/<bundle_id>", "to_route": "trustbit_bundle_detail"},
    {"from_route": "/shop/categories", "to_route": "trustbit_categories"},
    {"from_route": "/shop/category/<category>", "to_route": "trustbit_category"},
    {"from_route": "/shop/search", "to_route": "trustbit_search"},
    {"from_route": "/shop/about", "to_route": "trustbit_about"},
    {"from_route": "/shop/contact", "to_route": "trustbit_contact"},
    {"from_route": "/shop/announcements", "to_route": "trustbit_announcements"},
    {"from_route": "/shop/orders", "to_route": "trustbit_orders"},
    {"from_route": "/shop/track-order", "to_route": "trustbit_track_order"},
    {"from_route": "/shop/cart", "to_route": "trustbit_cart"},
]
