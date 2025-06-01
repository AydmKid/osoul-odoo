{
    'name':'Osoul Human Resources',
    'version':'1.0.0',
    'summary':'',
    'description':'',
    'author':'Osoul Information Technology',
    'category':'Osoul',
    'depends':['base','hr'],
    'data':['security/security.xml',
            'security/ir.model.access.csv',
            'views/hr_managements.xml',
            'views/hr_department.xml',
            'views/hr_unit.xml',
            'views/hr_employee.xml'
            ],
    'application':True,
    'auto_install':True,
    'installable':True,
    'sequence':-5
}