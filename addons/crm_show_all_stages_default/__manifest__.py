# -*- coding: utf-8 -*-
#############################################################################
#
#    German Ponce

{
    'name': "CRM Show all Stages in Leads",
    'description': """CRM All Leads""",
    'summary': """Muestra todas las etapas de las oportunidades.""",
    'category': 'Sales',
    'version': '16.0.1.0.0',
    'author': 'German Ponce Dominguez',
    'company': 'German Ponce Dominguez',
    'maintainer': 'german.ponce',
    'website': "https://www.anfepi.com",
    'depends': ['base', 'crm', 'sale_management'],
    'data':[
                "views/crm_view.xml",
           ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
