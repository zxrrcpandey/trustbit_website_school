# Trustbit Website School

Custom School Supplies Webshop for ERPNext with Product Bundles.

## Features

### 🛒 Product Bundles
- Display product bundles (school book sets)
- Add all bundle items to cart with one click
- Stock validation for each item
- Filter by school and class

### 🔍 Advanced Search (25K+ Items)
- Debounced search (500ms delay)
- Multi-field search (item code, name, barcode)
- Fuzzy matching for typos
- Filters by school, class, type
- Keyboard navigation

### 📄 Pages Included

| Page | Route | Description |
|------|-------|-------------|
| Homepage | `/shop` | Hero, categories, latest & trending products |
| Bundles | `/shop/bundles` | All bundles with filters |
| Bundle Detail | `/shop/bundles/<id>` | Bundle items, add to cart |
| Categories | `/shop/categories` | Category grid |
| Category | `/shop/category/<name>` | Products in category |
| Search | `/shop/search` | Search results |
| About | `/shop/about` | Company info, team |
| Contact | `/shop/contact` | Contact form |
| News | `/shop/announcements` | Announcements |
| Orders | `/shop/orders` | Order history |
| Track Order | `/shop/track-order` | Order tracking |

### ⚙️ Admin Doctypes

| Doctype | Purpose |
|---------|---------|
| Trustbit Settings | Site settings (hero, contact, about) |
| Trustbit Announcement | News and offers |
| Trustbit Banner | Homepage slider |
| Trustbit Team Member | Team for About page |

## Installation

```bash
# Get the app
cd ~/frappe-bench/apps
unzip trustbit_website_school.zip

# Install
bench --site your-site.local install-app trustbit_website_school

# Migrate
bench --site your-site.local migrate

# Clear cache
bench --site your-site.local clear-cache

# Restart
bench restart
```

## Configuration

After installation, go to:
- **Trustbit Website School > Trustbit Settings** - Configure hero, contact, about
- **Trustbit Website School > Trustbit Announcement** - Add news/offers
- **Trustbit Website School > Trustbit Banner** - Add homepage banners
- **Trustbit Website School > Trustbit Team Member** - Add team members

## Custom Fields Added

**Item:**
- `trustbit_school` - School name
- `trustbit_class` - Class level
- `trustbit_is_featured` - Featured on homepage

**Item Group:**
- `trustbit_icon` - Emoji icon
- `trustbit_color` - Category color

## File Structure

```
trustbit_website_school/
├── trustbit_website_school/
│   ├── api/webshop.py              # All APIs
│   ├── trustbit_website_school/
│   │   └── doctype/
│   │       ├── trustbit_settings/
│   │       ├── trustbit_announcement/
│   │       ├── trustbit_banner/
│   │       └── trustbit_team_member/
│   ├── public/
│   │   ├── css/trustbit_webshop.css
│   │   └── js/trustbit_webshop.js
│   ├── templates/
│   │   ├── includes/trustbit_base.html
│   │   └── pages/ (11 pages)
│   ├── hooks.py
│   ├── install.py
│   └── tasks.py
├── setup.py
└── requirements.txt
```

## License

MIT License
