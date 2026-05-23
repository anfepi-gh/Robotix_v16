# -*- coding: utf-8 -*-

from lxml.objectify import fromstring

from odoo import api, fields, models


# ---------------------------------------------------------------------------
# TODO v19: AccountEdiFormat._l10n_mx_edi_export_invoice_cfdi() fue eliminado
# en v17 junto con el modelo account.edi.format. La lógica que inyecta el
# namespace xmlns:donat y el nodo de complemento en el XML CFDI debe
# reimplementarse usando el mecanismo de v17+.
#
# Opciones a evaluar al tener acceso a la instancia v19:
#   A) Verificar si Odoo Enterprise v19 ya incluye soporte nativo del
#      complemento Donatarias en l10n_mx_edi. Si es así, este módulo sobra.
#   B) Si no hay soporte nativo, reimplementar vía override de método Python
#      en account.move que genere/modifique el CFDI XML, o vía QWeb template
#      que extienda el template CFDI principal de l10n_mx_edi.
# ---------------------------------------------------------------------------


class AccountMove(models.Model):
    _inherit = 'account.move'

    complemento_donaciones = fields.Boolean(
        'Complemento - Donatarias',
        help='Use this field when the invoice require the complement to '
        '"Donations". This value will be used to indicate the use of the '
        'information from the document that authorize to receive '
        'deductible donations, granted by SAT')

    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        """Adds donat schemaLocation when the complement is present."""
        result = super()._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi_data)
        if not cfdi_data:
            return result
        if not isinstance(cfdi_data, bytes):
            cfdi_data = cfdi_data.encode()
        cfdi_data = cfdi_data.replace(b'xmlns__donat', b'xmlns:donat')
        cfdi = fromstring(cfdi_data)
        if 'donat' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/donat',
            'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
        result['cfdi_node'] = cfdi
        return result

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.complemento_donaciones:
            self.complemento_donaciones = True
        return super()._onchange_partner_id()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_id'):
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if partner.complemento_donaciones:
                    vals['complemento_donaciones'] = True
        return super().create(vals_list)
