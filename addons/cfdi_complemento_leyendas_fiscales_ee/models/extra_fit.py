from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    complemento_leyendas_fiscales = fields.Boolean(
        'C. Leyendas Fiscales',
        help='Este Campo activa el complemento Leyendas Fiscales en el XML durante la Facturacion.')

    leyendas_fiscales_ids = fields.Many2many(
        'complemento.leyenda.fiscal', 'invoice_leyendas_rel', 'move_id', 'leyenda_id',
        'Leyendas Fiscales')

    @api.constrains('leyendas_fiscales_ids', 'complemento_leyendas_fiscales')
    def _constraint_complemento_leyendas_fiscales(self):
        if self.complemento_leyendas_fiscales and not self.leyendas_fiscales_ids:
            raise UserError(
                "Si se habilita el complemento de leyendas fiscales, debes ingresar las leyendas fiscales "
                "que incluira el comprobante.\nPestaña -> Leyendas Fiscales.")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.leyendas_fiscales_ids:
            self.complemento_leyendas_fiscales = True
            self.leyendas_fiscales_ids = self.partner_id.leyendas_fiscales_ids
        return super()._onchange_partner_id()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('leyendas_fiscales_ids') and vals.get('partner_id'):
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if partner.complemento_leyendas_fiscales:
                    vals.update({
                        'leyendas_fiscales_ids': [Command.set(partner.leyendas_fiscales_ids.ids)],
                        'complemento_leyendas_fiscales': True,
                    })
        return super().create(vals_list)

    @api.depends('partner_id', 'complemento_leyendas_fiscales', 'leyendas_fiscales_ids')
    def _compute_l10n_mx_edi_addenda_ids(self):
        super()._compute_l10n_mx_edi_addenda_ids()
        leyendas_addenda = self.env.ref(
            'cfdi_complemento_leyendas_fiscales_ee.l10n_mx_edi_addenda_leyendas_fiscales',
            raise_if_not_found=False,
        )
        if not leyendas_addenda:
            return
        for move in self:
            if move.complemento_leyendas_fiscales and move.leyendas_fiscales_ids:
                move.l10n_mx_edi_addenda_ids |= leyendas_addenda
            else:
                move.l10n_mx_edi_addenda_ids -= leyendas_addenda


class ComplementoLeyendaFiscal(models.Model):
    _name = 'complemento.leyenda.fiscal'
    _description = 'Normativas para agregar al Complemento'
    _rec_name = 'disposicion'

    partner_id = fields.Many2one('res.partner', 'ID Ref')
    norma = fields.Char('Norma', size=128)
    disposicion = fields.Char('Disposicion Fiscal')
    texto_leyenda = fields.Char('Texto Leyenda', size=128, required=True)
