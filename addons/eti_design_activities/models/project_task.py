# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EtiProjectTask(models.Model):
    _inherit = "project.task"

    product_id = fields.Many2one(
        string="Producto",
        comodel_name="product.product",
    )

    task_type_id = fields.Many2one(
        comodel_name="project.task.type.action",
        string="Tipo de Tarea"
    )

    client_id = fields.Many2one(
        string="Cliente",
        comodel_name='res.partner',
        readonly=True,
        store=True)


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id.partner_id:
            self.client_id = self.product_id.partner_id
        else:
            self.client_id = False