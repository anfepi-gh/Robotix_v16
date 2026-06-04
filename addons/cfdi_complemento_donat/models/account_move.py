from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    complemento_donaciones = fields.Boolean(
        'Complemento - Donatarias',
        help='Use this field when the invoice require the complement to '
        '"Donations". This value will be used to indicate the use of the '
        'information from the document that authorize to receive '
        'deductible donations, granted by SAT')

    @api.depends('partner_id', 'partner_id.complemento_donaciones', 'complemento_donaciones')
    def _compute_l10n_mx_edi_addenda_ids(self):
        super()._compute_l10n_mx_edi_addenda_ids()
        donat_addenda = self.env.ref(
            'cfdi_complemento_donat.l10n_mx_edi_addenda_donatarias',
            raise_if_not_found=False,
        )
        if not donat_addenda:
            return
        for move in self:
            if move.complemento_donaciones or move.partner_id.complemento_donaciones:
                move.l10n_mx_edi_addenda_ids |= donat_addenda
            else:
                move.l10n_mx_edi_addenda_ids -= donat_addenda
