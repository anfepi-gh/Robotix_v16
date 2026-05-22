# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, _
from odoo.tools.misc import ustr
from odoo.exceptions import ValidationError

class AddendaCompany(models.Model):
    """docstring for AddendaCompany"""
    _inherit = 'res.company'

class AddendaProduct(models.Model):
    _inherit = 'product.template'
    
class AddendaProduct(models.Model):
    _inherit = 'product.product'
    

class AddendaSale(models.Model):
    """docstring for AddendaFields"""
    _inherit = 'sale.order'
    
    addenda_type = fields.Selection([('na','No Aplica')], string="Addenda", default="na") 

class AddendaSaleLine(models.Model):
    """docstring for AddendaFields"""
    _inherit = 'sale.order.line'
    
    addenda_type = fields.Selection([('na','No Aplica')], string="Addenda", related="order_id.addenda_type") 

class AddendaPicking(models.Model):
    _inherit = 'stock.picking'

    addenda_type = fields.Selection([('na','No Aplica')], string="Addenda", default="na") 

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    addenda_type = fields.Selection([('na','No Aplica')], string="Addenda", default="na") 
