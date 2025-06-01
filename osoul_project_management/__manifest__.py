{
    'name': 'Osoul Project Management',
    'version': '1.0.0',
    'summary': 'A clean, standalone project management solution.',
    'description': '''
        Manage projects, tasks, and milestones with this independent project management module.
        Features include:
        - Task Duration Tracking
        - Milestone Management
        - Expense Monitoring
        - Automatic Daily Updates
    ''',
    'author': 'Osoul Information Technology',
    'website': 'https://www.osoul.sa',
    'category': 'Project Management',
    'depends': ['base', 'hr'],
    'data': [
        'data/project_management_data.xml',
        'data/osoul_project_sequence.xml',
        'data/osoul_project_cron.xml',
        'security/security_groups.xml',
        'views/osoul_project_contracts.xml',
        'views/osoul_project_expenses.xml',
        'views/osoul_project_milestone.xml',
        'views/osoul_project_project.xml',
        'views/osoul_project_quotations.xml',
        'views/osoul_project_task.xml',
        'menu/menu.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'sequence':-100
}
