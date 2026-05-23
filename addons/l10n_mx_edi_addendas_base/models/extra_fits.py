# -*- coding: utf-8 -*-

from odoo import models, fields


class AddendaCompany(models.Model):
    _inherit = 'res.company'


class AddendaProductTemplate(models.Model):
    _inherit = 'product.template'


class AddendaProductVariant(models.Model):
    _inherit = 'product.product'


class AddendaSale(models.Model):
    _inherit = 'sale.order'

    addenda_type = fields.Selection([('na', 'No Aplica')], string="Addenda", default="na")


class AddendaSaleLine(models.Model):
    _inherit = 'sale.order.line'

    addenda_type = fields.Selection([('na', 'No Aplica')], string="Addenda", related="order_id.addenda_type")


class AddendaPicking(models.Model):
    _inherit = 'stock.picking'

    addenda_type = fields.Selection([('na', 'No Aplica')], string="Addenda", default="na")


class AccountMove(models.Model):
    _inherit = 'account.move'

    addenda_type = fields.Selection([('na', 'No Aplica')], string="Addenda", default="na")
