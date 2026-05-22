# -*- coding: utf-8 -*-
#############################################################################
#
#    German Ponce

{
    'name': "CRM Robotix",
    'description': """CRM Customs""",
    'summary': """Agrega nuevas funcionalidades muy especificas para Robotix.""",
    'category': 'Sales',
    'version': '16.0.1.0.0',
    'author': 'German Ponce Dominguez',
    'company': 'German Ponce Dominguez',
    'maintainer': 'german.ponce',
    'website': "https://www.anfepi.com",
    'depends': ['base', 'crm', 'sale_management'],
    'data':[
                "views/data.xml",
                "views/crm_view.xml",
                "security/ir.model.access.csv",
           ],
    # "external_dependencies": {
    #                 "python" : ["cfdiclient", "suds-jurko"]
    #                 },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',

}
