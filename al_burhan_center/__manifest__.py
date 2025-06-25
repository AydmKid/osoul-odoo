{
    'name': 'AL Burhan Center',
    'version': '15.1.0.0.0',
    'summary': '',
    'description': '',
    'category': '',
    'author': '',
    'company': '',
    'maintainer': '',
    'website': "",
    'depends': ['base','mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'menu/menu.xml',
        'menu/sequence.xml',
        'views/student_registration_form.xml',
        'views/student_memorization_schedule.xml',
        'views/circles_views.xml',
        'views/quran.xml', 
        'views/quran_stage.xml',
        'views/student_stage_transition_test.xml',
        'views/student_schedule_line.xml',
        'views/student_review_line.xml',
        'views/teacher.xml',
    ],
    'assets': {
        'web.assets_backend': [ 
            
        ],
         
        
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence':20,
}