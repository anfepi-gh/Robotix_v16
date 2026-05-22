# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Complemento CFDI para Donaciones',
    'version': '15.0.1.0.0',
    "license": "LGPL-3",
    "author": "German Ponce Dominguez",
    'category': 'Hidden',
    'summary': 'Complementos CFDI',
    'depends': [
        'l10n_mx_edi_extended',
        'l10n_mx_edi_40',
    ],
    'data': [
        "data/donations.xml",
        "views/res_company_view.xml",
        "views/res_partner_view.xml",
        "views/account_move_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
