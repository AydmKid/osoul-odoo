{
    'name': 'Osoul Fleet Management',
    'version': '1.0.0',
    'summary': '',
    'description': "",
    'category': 'Fleet Management',
    'author': 'Osoul Information Technology',
    'website': 'https://www.osoul.sa',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'bus'],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/osoul_fleet_default_data.xml",
        'reports/osoul_fleet_vehicle_report.xml',
        "views/osoul_fleet_brand.xml",
        "views/osoul_fleet_category.xml",
        "views/osoul_fleet_classification.xml",
        "views/osoul_fleet_owner.xml",
        "views/osoul_fleet_plate_type.xml",
        "views/osoul_fleet_vehicle.xml",
        "views/osoul_fleet_work_location.xml",
        "views/osoul_fleet_work_role.xml",
        "menu/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'osoul_fleet_management/static/src/js/year_picker.js',
            # 'osoul_fleet_management/static/src/js/tree_button_confirm.js'
        ],
    },
    'installable': True,
    'application': True,
    'sequence': -100
}