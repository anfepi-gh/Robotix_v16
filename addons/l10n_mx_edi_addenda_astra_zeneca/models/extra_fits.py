# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'


class AddendaProduct(models.Model):
    _inherit = 'product.template'


class AddendaSale(models.Model):
    _inherit = 'sale.order'

    addenda_type = fields.Selection(selection_add=[('astra_zeneca', 'AstraZeneca')], ondelete={'astra_zeneca': 'set null'})
    orden_compra_astra_zeneca = fields.Char(string='Numero de la Orden de Compra')


class AccountMove(models.Model):
    _inherit = 'account.move'

    addenda_type = fields.Selection(selection_add=[('astra_zeneca', 'AstraZeneca')], ondelete={'astra_zeneca': 'set null'})
    orden_compra_astra_zeneca = fields.Char(string='Numero de la Orden de Compra')

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for res in moves:
            if res.move_type == 'out_invoice':
                sale_model = 'sale_line_ids' in res.invoice_line_ids._fields
                sale_id = res.mapped('invoice_line_ids.sale_line_ids.order_id') if sale_model else False
                if sale_id:
                    sale = sale_id[0]
                    res.addenda_type = sale.addenda_type
                    res.orden_compra_astra_zeneca = sale.orden_compra_astra_zeneca
                    for line in res.invoice_line_ids:
                        line.no_identificacion_astra_zeneca = str(line.quantity) + ' ' + line.product_uom_id.name
        return moves


class AddendaOrderLine(models.Model):
    _inherit = 'sale.order.line'

    addenda_type = fields.Selection(selection_add=[('astra_zeneca', 'AstraZeneca')], ondelete={'astra_zeneca': 'set null'})


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    no_identificacion_astra_zeneca = fields.Char('No. Identificacion Addenda')

    @api.onchange('product_id', 'quantity')
    def onchange_no_identificacion_astra_zeneca(self):
        if self.product_id:
            self.no_identificacion_astra_zeneca = self.product_id.default_code
