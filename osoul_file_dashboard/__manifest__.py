{
    'name': 'File Dashboard',
    'version': '1.0',
    'summary': 'Manage and import/export Excel files',
    'description': 'Module to import/export Excel files and display them on a dashboard',
    'author': 'Your Name',
    'depends': ['base', 'web', 'board'],
    'data': [
        'security/ir.model.access.csv',
        'menu/menu.xml',
        'views/osoul_file_dashboard.xml',
       
    ],
    'installable': True,
    'application': True,
    'sequence':5
}
