{
    "name": "Stock",
    "version": "1.2",
    "author": "vitraining.com",
    "category": "Inventory",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """
    Features :
- Backdate after done
""",
    "depends": [
        "stock","account"
    ],
    "data":[
        "views/stock_view.xml",
        "security/res_groups.xml",
    ],
    "demo": [],
    "qweb": [],
    "test": [],
    "installable": True,
    "auto_install": False,
    "application": True,
}