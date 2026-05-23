# -*- coding: utf-8 -*-
from odoo import fields, models


class EtiProjectTaskTypeAction(models.Model):
    _name = "project.task.type.action"

    name = fields.Char(
        required=True,
        string="Nombre"
    )
    duration = fields.Integer(
        required=True,
        string="Duración"
    )
