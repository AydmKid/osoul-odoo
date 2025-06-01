{
    'name':'Osoul Accommodation',
    'version':'1.0.0',
    'summary':'Managing osoul employees housing',
    'description':'',
    'author':'Osoul Information Technology',
    'category':'Osoul',
    'website':'www.osoul.sa',
    'depends':['base',
               'hr',
               'board',
               'osoul_human_resources'],
    'data':['security/security.xml',
            'security/ir.model.access.csv',
            'reports/accom_housing_form.xml',
            'wizard/accomm_beds_control.xml',
            'wizard/accomm_cotracts.xml',
            'data/sequence.xml',
            'data/cron.xml',
            'menu/menu.xml',
            'views/accom_room.xml',
            'views/accom_housing.xml',
            'views/accom_building.xml',
            'views/accom_log.xml',
            'views/accom_floor.xml',
            'views/accom_apartment.xml', 
            'views/accom_kan_dash.xml',
            'views/accom_stock.xml'
            ],
    'assets': {
        'web.assets_backend': [ 
            '/osoul_accommodation/static/src/js/osoul_accommodation.js',
            '/osoul_accommodation/static/src/js/kanban_image_follow.js',
            '/osoul_accommodation/static/src/js/scorpion_follow.js',
            '/osoul_accommodation/static/src/js/kanban.js',
            '/osoul_accommodation/static/src/css/osoul_custom_notification_styles.css',
            '/osoul_accommodation/static/src/css/osoul_accommodation_styles.css',
            '/osoul_accommodation/static/src/css/kanban.css',
        ],
        'web.assets_qweb': [
            'osoul_accommodation/static/src/xml/notiy_templates.xml',
            
        ],
        'web.assets_frontend': [
        
        
    ],
    },
    'application':True,
    'auto_install':False,
    'installable':True,
    'sequence':4
}