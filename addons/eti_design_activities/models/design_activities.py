# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from datetime import timedelta
from datetime import datetime


class EtiDesignActivities(models.TransientModel):
    _name = "design.activities"
    _description = "Wizard en producto que permite generar tareas en modulo de proyecto"

    task_type_id = fields.Many2one(
        comodel_name="project.task.type.action",
        string="Tipo de Tarea"
    )
    name = fields.Char(
        required=True,
        string="Nombre de tarea",
    )
    #tomamos el producto que está activo
    product_id = fields.Many2one(
        comodel_name="product.product",
        default=lambda self: self.env["product.product"].browse(self._context.get("active_id")),
        readonly=True,
        required=True,
        string="Producto"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        default=lambda self: self.env.user.partner_id,
        readonly=True,
        required=True,
        string="Usuario actual"
    )
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        string="Fecha de Entrega"
    )
    description = fields.Html(string="Descripción")

    @api.depends("task_type_id.duration")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.context_today(record) + timedelta(
                days=record.task_type_id.duration
            )

    def action_create_task(self):
        new_record = self.env["project.task"].create(
            {
                "name": self.name,
                "partner_id": self.partner_id.id,
                "product_id": self.product_id.id,
                "task_type_id": self.task_type_id.id,
                "date_deadline": self.date_deadline,
                "description": self.description,
                "date_assign": datetime.today(),
            }
        )
        return new_record
