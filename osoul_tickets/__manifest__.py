{
    'name': 'Ticket Job Order',
    'version': '1.0.0',
    'category': 'Operations',
    'summary': 'Manage tickets and create job orders',
    'description': 'A module to manage tickets that generate job orders',
    'author': 'Osoul Information Technology',
    'website': '',
    'depends':['base', 'project','hr',
               'board',
               'osoul_human_resources',
               'mail',
               'web'], 
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/unit_heads_data.xml',
        'menu/menu.xml',
        'views/ticket_view.xml',
        'views/template.xml',
        'views/osoul_tickets_settings.xml',
        'views/osoul_unit_member.xml',
        'views/ticket_approval_view.xml',
            ],
    'assets': {
        'web.assets_backend': [
            '/osoul_tickets/static/src/js/runaway_button.js',
            '/osoul_tickets/static/src/css/osoul_custom_notification_styles.css',
            '/osoul_tickets/static/src/css/osoul_accommodation_styles.css',
            '/osoul_tickets/static/src/css/kanban.css',
        ],
        'web.assets_qweb': [
            'osoul_tickets/static/src/xml/notiy_templates.xml',
            
        ],
        'web.assets_frontend': [
        ],
        },
    'installable': True,
    'application': True,
    'sequence':4
}
