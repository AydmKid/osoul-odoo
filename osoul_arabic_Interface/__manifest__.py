 # -*- coding: utf-8 -*-
{
    'name': "Osoul Arabic Interface",
    'summary':'',
    'description':'',
    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'category': 'Localization',
    'version': '15.0.0.0',
    'depends': ['web'],
    'qweb': [],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'auto_install': True,
    'installable': True,
    'application':True,
    'live_test_url': 'https://youtu.be/aR3ZmDu8OjI',
    'assets': {
        'web.assets_common': [
            'osoul_arabic_Interface/static/src/scss/almaraifont.scss',
            'osoul_arabic_Interface/static/src/scss/cairofont.scss',
            'osoul_arabic_Interface/static/src/scss/droidfont.scss',
            'osoul_arabic_Interface/static/src/css/web_style.css',
        ],
        'web.report_assets_common': [
            'osoul_arabic_Interface/static/src/scss/almaraifont.scss',
            'osoul_arabic_Interface/static/src/scss/cairofont.scss',
            'osoul_arabic_Interface/static/src/scss/droidfont.scss',
        ],
    },
}