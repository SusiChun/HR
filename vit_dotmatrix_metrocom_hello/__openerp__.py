{
	"name": "Direct Print to Dot Matrix Pinter",
	"version": "1.1",
	"depends": [
		"sale",
		"account",
		"stock",
		"purchase",
		"mail"
	],
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"category": "Utilities",
	'website': 'http://www.vitraining.com',
	'images': ['static/description/images/main_screenshot.jpg'],
	'price': '60',
	'currency': 'USD',
	'summary': 'This is modul is used to print PO, SO, Invoice directly to dot matrix printers',
	"description": """\

Manage
======================================================================

* this is modul is used to print PO, SO, Invoice directly to dot matrix printer
* no special hardware needed
* using printer proxy script (apache/ngnix+php)
* add printer_data field on account.invoice, sale.order, purchase.order
* printer template data from mail.template named "Dot Matrix *"

Installation
======================================================================
* install this addon on the database
* download the print.php script from this <a href="/vit_dotmatrix/static/print.php">link</a>
* install apache+php or nginx+php on the local computer and copy print.php script to the htdocs
* print Invoice, SO, PO directly to local dotmatrix printer

""",
	"data": [
		"view/web_asset.xml",
		"view/invoice.xml",
		"view/po.xml",
		"data/templates.xml",
	],
	'qweb': [
		'static/src/xml/web_print_button.xml',
	],
	
	"installable": True,
	"auto_install": False,
    "application": True,
}