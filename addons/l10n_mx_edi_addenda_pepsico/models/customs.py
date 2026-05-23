# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AddendaPicking(models.Model):
    _inherit = 'stock.picking'

    addenda_type = fields.Selection(selection_add=[('pepsico', 'Pepsico')], ondelete={'pepsico': 'set null'})


class AddendaSale(models.Model):
    _inherit = 'sale.order'

    addenda_type = fields.Selection(selection_add=[('pepsico', 'Pepsico')], ondelete={'pepsico': 'set null'})
    x_pepsico_idPedido = fields.Char('ID Pedido', size=64)
    x_payment_request = fields.Char('Solicitud de pago', size=64)
    x_reception = fields.Char('Número de recepción', size=64)


class AccountMove(models.Model):
    _inherit = 'account.move'

    addenda_type = fields.Selection(selection_add=[('pepsico', 'Pepsico')], ondelete={'pepsico': 'set null'})
    x_pepsico_idPedido = fields.Char('ID Pedido', size=64)
    x_payment_request = fields.Char('Solicitud de pago', size=64)
    x_reception = fields.Char('Número de recepción', size=64)

    def get_invoice_lines(self):
        return self.invoice_line_ids

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for res in moves:
            if res.move_type == 'out_invoice':
                sale_model = 'sale_line_ids' in res.invoice_line_ids._fields
                sale_id = res.mapped('invoice_line_ids.sale_line_ids.order_id') if sale_model else False
                if sale_id:
                    sale = sale_id[0]
                    res.x_pepsico_idPedido = sale.x_pepsico_idPedido
                    res.x_payment_request = sale.x_payment_request
                    res.x_reception = sale.x_reception
        return moves
