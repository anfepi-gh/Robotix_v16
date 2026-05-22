# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MailActivityExtend(models.Model):
    _inherit = 'mail.activity'
    
    #activity_type_id = fields.Many2one(domain="['|', ('res_model_id', '=', False), ('res_model_id', '=', res_model_id)]")
    
    @api.onchange('date_deadline')
    def _check_activity_type_id_domain_bool(self):
        if self.res_model == "crm.lead":
            model_object = self.env["ir.model"]
            crm_id = model_object.search([("model", "=", 'crm.lead')]).ids
            return {'domain': {'activity_type_id': [('res_model_id', '=', crm_id)]}}
        #else:
        #    return {'domain': {'activity_type_id': ['|', ('res_model_id', '=', False), ('res_model_id', '=', self.res_model_id)]}}