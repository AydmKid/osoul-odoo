{
    'name': 'Osoul Buffet Management',
    'version': '1.0.0',
    'summary': 'Manageing Buffet Orders and Stock With Notification System',
    'description': """
Osoul Buffet Management
===========================

""",
    'category': 'Productivity',
    'author': 'Osoul Information Technology',
    'website': 'https://www.osoul.sa',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr', 'contacts'],
    "data": [
        'security/security_access_data.xml',
        "security/security_access_data.xml",
        "data/options.xml",
        "data/sequence.xml",
        "views/osoul_buffet_category.xml",
        "views/osoul_buffet_subcategory.xml",
        "views/osoul_buffet_stock.xml",
        "views/osoul_buffet_movement.xml",
        "views/osoul_buffet_order.xml",
        "wizard/osoul_buffet_add_stock.xml",
        "views/osoul_buffet_operator.xml",
        "menu/menu.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': -100
}