{
    'name': 'Osoul ITAM',
    'version': '1.0.0',
    'summary': 'Manage IT assets including hardware, software, and cloud infrastructure.',
    'description': """
Osoul itam Asset Management
===========================
This module provides functionality to manage IT assets within the Osoul itam environment. 
It includes features for asset categorization, vendor management, lifecycle state tracking, 
and integration with Odoo chatter and activity systems.
""",
    'category': 'IT Management',
    'author': 'Osoul Information Technology',
    'website': 'https://www.osoul.sa',
    'license': 'AGPL-3',
    'depends': ['base', 'mail'],
    "data": [
        "data/sequence.xml",
        "data/osoul_assets_category_data.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/osoul_assets_vendor.xml",
        "views/osoul_assets_software.xml",
        "views/osoul_assets_hardware.xml",
        "views/osoul_assets_brand.xml",
        "views/osoul_assets_category.xml",
        "views/osoul_assets_sub_category.xml",
        "views/osoul_assets_model.xml",
        "menu/menu.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': -100
}