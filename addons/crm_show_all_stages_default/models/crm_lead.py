# -*- coding: utf-8 -*-
#############################################################################
#
#    German Ponce

import calendar

from odoo import models, fields, api
from odoo.tools import date_utils
from odoo.http import request

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import SUPERUSER_ID


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    # @api.model
    # def default_get(self, fields):
    #     print ("#************* default_get >>>>>>>>>>>>>>>>> ")
    #     context = self._context
    #     stage_obj = self.env['crm.stage']
    #     print ("##### context: ", context)
    #     force_team_id = context.get('force_team_id', False)
    #     res = super(CRMLead, self).default_get(fields)
    #     if force_team_id:
    #         all_stage_ids = stage_obj.sudo().search([('team_id','=',force_team_id)], order="name")
    #         for stage in all_stage_ids:
    #             print ("#### stage:", stage)
    #             print ("#### stage.name:", stage.name)
    #     return res
      
    @api.depends('stage_id')
    def _get_allow_crm_stages(self):
        for rec in self:
            allow_stage_ids = []
            context = self._context
            stage_obj = self.env['crm.stage']
            force_team_id = context.get('force_team_id', False)
            if force_team_id:
                all_stage_ids = stage_obj.sudo().search([('team_id','=',force_team_id)], order="name")
                if all_stage_ids:
                    allow_stage_ids = all_stage_ids.ids
            else:
                team_id = rec.team_id.id if rec.team_id else False
                if team_id:
                    all_stage_ids = stage_obj.sudo().search(['|', ('team_id', '=', False), ('team_id', '=', team_id)], order="name")
                else:
                    all_stage_ids = stage_obj.sudo().search([('team_id', '=', False)], order="name")
                if all_stage_ids:
                    allow_stage_ids = all_stage_ids.ids

            rec.allow_stage_ids = [(6,0,allow_stage_ids)]

    
    allow_stage_ids = fields.Many2many( 'crm.stage', compute="_get_allow_crm_stages")



    stage_id = fields.Many2one(
        'crm.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict')
        #domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")


    @api.depends('team_id', 'type')
    def _compute_stage_id(self):
        context = self._context
        stage_obj = self.env['crm.stage']
        force_team_id = context.get('force_team_id', False)
        if force_team_id:
            all_stage_ids = stage_obj.sudo().search([('team_id','=',force_team_id)], order="name")
            if all_stage_ids:
                for lead in self:
                    if not lead.stage_id:
                        lead.stage_id = all_stage_ids[0].id
            else:
                for lead in self:
                    if not lead.stage_id:
                        lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id

        else:
            for lead in self:
                if not lead.stage_id:
                    lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id
        


    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        user = self.env.user

        context = self._context
        #print ("##### context: ", context)
        force_team_id = context.get('force_team_id', False)
        # Obtener los equipos de ventas donde el usuario es miembro
        user_team_ids = self.env['crm.team'].search([('alias_user_id', '=', user.id)]).ids

        # Obtener las empresas permitidas en el entorno
        company_ids = self.env.companies.ids
        
        # Crear el dominio para buscar las etapas que:
        # - Incluyen las etapas especificadas (stages.ids) para mostrar todas las etapas existentes.
        # - Pertenecen a los equipos de ventas del usuario actual.
        # - Están asociadas a una de las empresas activas seleccionadas.
        #search_domain = ['|', ('id', 'in', stages.ids), ('fold', '=', False)]
        
        stage_obj = self.env['crm.stage']
        company_ids = self.env.companies.ids
        new_stage_ids = []

        if force_team_id:
            all_stage_ids = stage_obj.sudo().search([])
            for stage in all_stage_ids:
                if stage.team_id and stage.team_id.id == force_team_id:
                    if stage.team_id.company_id.id in company_ids:
                        if self.env.user.id in stage.team_id.member_ids.ids:
                            new_stage_ids.append(stage.id)
        else:
            all_stage_ids = stage_obj.sudo().search([])
            for stage in all_stage_ids:
                if stage.team_id:
                    if stage.team_id.company_id.id in company_ids:
                        if self.env.user.id in stage.team_id.member_ids.ids:
                            new_stage_ids.append(stage.id)
                else:
                    new_stage_ids.append(stage.id)

        search_domain = [('id', 'in', new_stage_ids)]

        # Realizar la búsqueda de las etapas, usando SUPERUSER_ID para evitar restricciones de acceso
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)

        return stages.browse(stage_ids)

