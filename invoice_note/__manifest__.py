{
    'name': "invoice_note",

    'summary': """Default note on invoice""",

    'description': """
	This module replace default sale term and condition on invoice with default invoice term and condition
    """,

    'author': "Kusuma Ruslan",
    'website': "http://www.wangsamas.com",

    'category': 'Sale',
    'version': '0.1',

    'depends': ['sale_management'],

    'data': [
        'views/views.xml',
    ],
}