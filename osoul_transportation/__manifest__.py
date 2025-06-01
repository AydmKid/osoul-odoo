{
    'name':'Osoul Transportation',
    'version':'1.0.0',
    'summary':'Managing osoul Transportation',
    'description':'',
    'author':'Osoul Information Technology',
    'category':'Osoul',
    'website':'www.osoul.sa',
    'depends':['base','hr','board','osoul_human_resources','osoul_contacts','contacts'],
    'data':['security/security.xml',
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'menu/menu.xml', 
            'views/osoul_driver.xml', 
            'views/osoul_transportation_vehicle.xml',
            'views/osoul_vehicle_exit_permit.xml',
            'views/osoul_transportation_consent.xml'
          
            ],
    'application':True,
    'auto_install':False,
    'installable':True,
    'sequence':2
}