# -*- coding: utf-8 -*-
#############################################################################
#
#    German Ponce

import ast
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class CrmLeadStagesChanges(models.Model):
    _name = 'crm.lead.stages.changes'
    _description = 'Registro de Cambios de Etapas'
    _rec_name = "lead_id"
    _order="date"

    lead_id = fields.Many2one('crm.lead', string="Iniciativa/Oportunidad")
    previous_stage_id = fields.Many2one('crm.stage', string="Etapa Previa")
    new_stage_id = fields.Many2one('crm.stage', string="Etapa Nueva")
    date = fields.Date('Fecha Cambio')
    count_won = fields.Integer('Ganadas')
    count_lost = fields.Integer('Perdidas')


class CrmStageNextAutoWizard(models.TransientModel):
    _name = 'crm.stage.next.auto.wizard'
    _description = "Asistente - Asignación automatica de etapa"

    stage_id = fields.Many2one('crm.stage', string="Saltar a esta etapa", required=True)


    def execute_report(self):
        context = self.env.context
        stage_obj = self.env['crm.stage']
        active_ids = context.get('active_ids')
        for stage in stage_obj.browse(active_ids).sudo():
            stage.linked_stage_name = self.stage_id.name
            stage.linked_stage_id = self.stage_id.id
        return True


class ResUsers(models.Model):
    _inherit ='res.users'

    x_studio_objetivo_facturacion_mes = fields.Float('Objetivo de Facturación Mensual')


class CRMTeam(models.Model):
    _inherit ='crm.team'

    target_from_users = fields.Boolean("Objetivo Distribuido", help="Indica que el total se calcula en base a la sumatoria de los objetivos de cada uno de sus integrantes.")

    def update_target_monthly_from_users(self):
        for rec in self:
            invoiced_target = 0.0
            if rec.target_from_users:
                for user in rec.member_ids:
                    invoiced_target += user.x_studio_objetivo_facturacion_mes
                rec.invoiced_target = invoiced_target
            else:
                raise UserError("No se puede actualizar debido a que no es un objetivo distribuido.")
        return True

class CRMStage(models.Model):
    _inherit ='crm.stage'

    linked_stage_name = fields.Char('Saltar a la Etapa')
    linked_stage_id = fields.Integer('Saltar a Etapa (ID)')

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.depends('create_date', 'date_won')
    def _get_days_won(self):
        """Calcula los días desde la fecha de creación hasta la fecha de cierre (ganada)."""
        for rec in self:
            if rec.create_date and rec.date_won:
                # Convertir las fechas a objetos datetime para calcular la diferencia
                create_date = fields.Datetime.to_datetime(rec.create_date).date()
                date_won = rec.date_won
                rec.days_won = (date_won - create_date).days
            else:
                rec.days_won = 0

    @api.depends('create_date', 'date_lost')
    def _get_days_lost(self):
        """Calcula los días desde la fecha de creación hasta la fecha de pérdida."""
        for rec in self:
            if rec.create_date and rec.date_lost:
                # Convertir las fechas a objetos datetime para calcular la diferencia
                create_date = fields.Datetime.to_datetime(rec.create_date).date()
                date_lost = rec.date_lost
                rec.days_lost = (date_lost - create_date).days
            else:
                rec.days_lost = 0

    crm_changes_ids = fields.One2many( 'crm.lead.stages.changes', 'lead_id', string="Cambios de Etapa")

    date_won = fields.Date('Fecha Cierre', help="Fecha Marcada como Ganada")
    days_won = fields.Integer('Dias al Cierre', compute="_get_days_won", store=True)
    date_lost = fields.Date('Fecha Perdida', help="Fecha Marcada como Perdida")
    days_lost = fields.Integer('Dias a Perdida', compute="_get_days_lost", store=True)

    team_first_workflow = fields.Char('Equipo de Ventas E. 01', help="Equipo Cierre Etapa 01")
    team_first_workflow_date_won = fields.Date('Fecha Cierre E. 01', help="Fecha Cierre Etapa 01")

    team_second_workflow = fields.Char('Equipo de Ventas E. 01', help="Equipo Cierre Etapa 01")
    team_second_workflow_date_won = fields.Date('Fecha Cierre E. 01', help="Fecha Cierre Etapa 01")

    def action_set_lost(self, **additional_values):
        for rec in self:
            rec.date_lost = fields.Date.context_today(self)
        res = super(CRMLead, self).action_set_lost(**additional_values)
        return res

    def action_set_won(self):
        for rec in self:
            rec.date_won = fields.Date.context_today(self)
            if rec.stage_id and rec.stage_id.team_id:
                if not rec.team_first_workflow:
                    rec.team_first_workflow = rec.stage_id.team_id.name
                    rec.team_first_workflow_date_won = fields.Date.context_today(self)
                else:
                    rec.team_second_workflow = rec.stage_id.team_id.name
                    rec.team_second_workflow_date_won = fields.Date.context_today(self)
        res = super(CRMLead, self.with_context(trigger_onchange_set_won_applied=True)).action_set_won()

        for rec in self:
            if rec.stage_id.linked_stage_id:
                stage_obj = self.env['crm.stage'].sudo()
                stage_br = stage_obj.browse(rec.stage_id.linked_stage_id)
                rec.stage_id = stage_br.id
                rec.team_id = stage_br.team_id.id if stage_br.team_id else False

        return res

    def create_stage_change(self, lead, previous_stage_id, new_stage_id):
        """
        Crea un registro en el modelo crm.lead.stages.changes.
        """
        self.env['crm.lead.stages.changes'].create({
            'lead_id': lead.id,
            'previous_stage_id': previous_stage_id,
            'new_stage_id': new_stage_id,
            'date': fields.Date.context_today(self),  # Fecha actual
        })
    
    def write(self, vals):
        """
        Sobrescribe el método write para capturar los cambios en stage_id.
        """
        if 'stage_id' in vals:
            for lead in self:
                previous_stage_id = lead.stage_id.id  # Etapa actual antes del cambio
                new_stage_id = vals['stage_id']  # Nueva etapa

                # Llamar al método para registrar el cambio de etapa
                self.create_stage_change(lead, previous_stage_id, new_stage_id)

        # Continuar con el write normal
        return super(CRMLead, self).write(vals)

    @api.onchange('stage_id')
    def onchange_stage_linked_new(self):
        context = self.env.context
        trigger_onchange_set_won_applied = context.get('trigger_onchange_set_won_applied', False)
        _logger.info("\n############ trigger_onchange_set_won_applied (el cambio ya se aplico previo en el boton marcar como ganado): %s" % trigger_onchange_set_won_applied)
        if self.stage_id:
            if self.stage_id.is_won:
                if not trigger_onchange_set_won_applied:
                    self.date_won = fields.Date.context_today(self)
                    if self.stage_id and self.stage_id.team_id:
                        if not self.team_first_workflow:
                            self.team_first_workflow = self.stage_id.team_id.name
                            self.team_first_workflow_date_won = fields.Date.context_today(self)
                        else:
                            self.team_second_workflow = self.stage_id.team_id.name
                            self.team_second_workflow_date_won = fields.Date.context_today(self)

            if self.stage_id.linked_stage_id:
                stage_obj = self.env['crm.stage'].sudo()
                stage_br = stage_obj.browse(self.stage_id.linked_stage_id)
                self.stage_id = stage_br.id
                self.team_id = stage_br.team_id.id if stage_br.team_id else False

    @api.model
    def _automatic_update_invoice_target(self):
        _logger.info("\n:::::::::::::::::::::::::: Actualizando el objetivo de factura en CRM (_automatic_update_invoice_target). Fecha: %s >>>>>>>  " % fields.Date.context_today(self))                          
        all_crm_team = self.env['crm.team'].sudo().search([])
        for team in all_crm_team:
            if team.target_from_users:
                _logger.info("\n########## Actualizando el equipo: %s ....................... " % team.name)
                team.update_target_monthly_from_users()

class CRMLeadsCountLine(models.Model):
    _name = 'crm.leads.count.line'
    _description = "Tabla Reporte - Analisis de Iniciativas"

    name = fields.Char('Descripción Etapa', related="stage_id.name", store=True)
    stage_id = fields.Many2one('crm.stage', 'Etapa')
    team_id = fields.Many2one('crm.team', string="Equipo de ventas")
    leads_count = fields.Integer('No. Registros')
    leads_percentage = fields.Float('Porcentaje')
    count_won = fields.Integer('Ganadas')
    count_lost = fields.Integer('Perdidas')

class CRMLeadsCountWizard(models.TransientModel):
    _name = 'crm.leads.count.wizard'
    _description = "Asistente - Analisis de Iniciativas"

    team_id = fields.Many2one('crm.team', string="Equipo de ventas")


    def fix_date(self, date, hours, hour, minute, second):
        """METODO QUE HACE QUE LA HORA DE LAS FECHAS SEA IGUAL A 0 Y LA DEVUELVE"""

        fixed_date = False
        #SE LES DA FORMATO A LAS FECHAS
        fixed_date = datetime.strptime(str(date),"%Y-%m-%d %H:%M:%S")
        #fixed_date = datetime.strptime(str(date),"%Y-%m-%d")
        #SE RESTA 7 HORAS A CADA FECHA, DEBIDO A QUE SE CALCULAN CON 1 DIA DE MAS
        #fixed_date = fixed_date - timedelta(hours=hours)
        #SE ELIMINA LA HORA EN LA FECHA
        fixed_date = fixed_date.replace(hour=hour,minute=minute,second=second)
        fixed_date = fixed_date + timedelta(hours=hours)
        return fixed_date

    def get_name_from_translation(self, term_dict_str):

        #en_US
        #es_MX
        # es
        if term_dict_str:
            if type(term_dict_str) == str:
                term_dict = ast.literal_eval(term_dict_str)
            else:
                term_dict = term_dict_str
            if 'es_MX' in term_dict:
                return term_dict['es_MX']
            elif 'es' in term_dict:
                return term_dict['es']
            else:
                return term_dict['en_US']
        return ""


    def execute_report(self):
        cr = self.env.cr
        # Limpiar la tabla crm_leads_count_line
        cr.execute("""
            TRUNCATE TABLE crm_leads_count_line;
            ALTER SEQUENCE crm_leads_count_line_id_seq RESTART WITH 1;
        """)

        # Inicializar los objetos y variables necesarias
        stage_line_analysis_list = []
        stage_line_analysis_obj = self.env['crm.leads.count.line']
        total_leads = self.env['crm.lead'].search([('active','in',(True,False))])  # Buscar todas las iniciativas
        total_count = len(total_leads)  # Contar el total de registros de iniciativas

        # Obtener las iniciativas agrupadas por etapa
        stages = self.env['crm.stage'].search([('team_id','=',self.team_id.id)])  # Obtener todas las etapas posibles
        for stage in stages:
            # Obtener el número de iniciativas por etapa
            leads_in_stage = self.env['crm.lead'].search([('stage_id', '=', stage.id),('active','in',(True,False))])

            # Calcular el número de iniciativas ganadas y perdidas
            won_leads = leads_in_stage.filtered(lambda lead: lead.stage_id.is_won and lead.active)  # Etapas marcadas como "ganadas"
            lost_leads = leads_in_stage.filtered(lambda lead: not lead.active)  # Etapas inactivas como "perdidas"

            won_count = len(won_leads)  # Contar las ganadas
            lost_count = len(lost_leads)  # Contar las perdidas

            # Calcular el porcentaje de la etapa
            #stage_percentage = (len(leads_in_stage) / total_count) * 100 if total_count else 0
            stage_percentage = (len(leads_in_stage) / total_count) if total_count else 0.0

            # Crear el registro en la tabla crm.leads.count.line
            stage_line_analysis_id = stage_line_analysis_obj.create({
                                                                        'name': stage.name,
                                                                        'stage_id': stage.id,
                                                                        'team_id': self.team_id.id,  # Asignar el equipo de ventas seleccionado en el wizard
                                                                        'leads_count': len(leads_in_stage),
                                                                        'leads_percentage': stage_percentage,
                                                                        'count_won': won_count,
                                                                        'count_lost': lost_count,
                                                                    })
            stage_line_analysis_list.append(stage_line_analysis_id.id)

        # Devuelve el reporte en el formato requerido
        return {
            'domain': [('id', 'in', stage_line_analysis_list)],
            'name': 'Análisis de Flujo CRM',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'tree_view_ref': 'crm_robotix.crm_leads_count_line_tree_view'},
            'res_model': 'crm.leads.count.line',
            'type': 'ir.actions.act_window'
        }



class CRMLeadsWonAnalisisLine(models.Model):
    _name = 'crm.leads.won.analisis.line'
    _description = "Tabla Reporte - Analisis de Cumplimiento"

    name = fields.Char('Descripción Etapa', related="stage_id.name", store=True)
    stage_id = fields.Many2one('crm.stage', 'Etapa')
    team_id = fields.Many2one('crm.team', string="Equipo de ventas")
    leads_count = fields.Integer('No. Registros')
    amount_target_stage = fields.Float('Objetivo de Facturación')
    amount_target_real = fields.Float('Total Facturado')
    target_percentage = fields.Float('Porcentaje Cumplimiento')
    period = fields.Char('Periodo')

class CRMLeadsWonAnalisisWizard(models.TransientModel):
    _name = 'crm.leads.won.analisis.wizard'
    _description = "Asistente - Analisis de Iniciativas Ganadas"

    team_id = fields.Many2one('crm.team', string="Equipo de ventas")
    start_date = fields.Date('Fecha Inicio')
    end_date = fields.Date('Fecha Fin')

    type_date = fields.Selection([('create_date','Fecha Creación'),('won_date','Fecha Cierre')], 
                                 string="Analizar por", default="won_date")

    @api.constrains('start_date','end_date')
    def _check_dates(self):
        """VALIDA QUE LA FECHA FINAL NO SEA ANTES QUE LA INICIAL"""
        if self.end_date < self.start_date:
            raise UserError("La fecha es incorrecta.")
        return True


    def execute_report(self):
        cr = self.env.cr
        # Limpiar la tabla crm_leads_count_line
        cr.execute("""
            TRUNCATE TABLE crm_leads_won_analisis_line;
            ALTER SEQUENCE crm_leads_won_analisis_line_id_seq RESTART WITH 1;
        """)

        period = str(self.start_date)+" al "+str(self.end_date)
        # Inicializar los objetos y variables necesarias
        target_analisis_list = []
        line_analysis_obj = self.env['crm.leads.won.analisis.line']
        team_list = [self.team_id] if self.team_id else []
        if not self.team_id:
            team_list = self.env['crm.team'].search(['|',('company_id','in',self.env.companies.ids),('company_id','=',False)])

        for team in team_list:
            # Obtener las iniciativas agrupadas por etapa
            # Obtener el número de iniciativas por etapa
            if self.type_date == 'date_won':
                leads_in_stage = self.env['crm.lead'].search([('stage_id.is_won', '=', True),
                                                              ('date_won','>=',self.start_date),
                                                              ('date_won','<=',self.end_date)])
            else:
                leads_in_stage = self.env['crm.lead'].search([('stage_id.is_won', '=', True),
                                                              ('create_date','>=',self.start_date),
                                                              ('create_date','<=',self.end_date)])
            if not leads_in_stage:
                raise UserError("No encontro información con los parametros.")
            stage_id = leads_in_stage[0].stage_id.id
            team_id = team.id
            leads_count = len(leads_in_stage.ids)
            amount_target_stage = team.invoiced_target
            amount_target_real = 0.0
            target_percentage = 0.0

            for lead in leads_in_stage:
                amount_target_real += lead.sale_amount_total

            if amount_target_real and amount_target_stage:
                target_percentage = (abs(amount_target_real) / amount_target_stage) if amount_target_real else 0.0
            else:
                if amount_target_real and not amount_target_stage:
                    target_percentage = 1.0
                else:
                    target_percentage = 0.0
            # Crear el registro en la tabla crm.leads.count.line
            stage_line_analysis_id = line_analysis_obj.create({
                                                                        'stage_id': stage_id,
                                                                        'team_id': team_id,
                                                                        'leads_count': leads_count,
                                                                        'amount_target_stage': amount_target_stage,
                                                                        'amount_target_real': amount_target_real,
                                                                        'target_percentage': target_percentage,
                                                                        'period': period,
                                                                    })
            target_analisis_list.append(stage_line_analysis_id.id)

        # Devuelve el reporte en el formato requerido
        return {
            'domain': [('id', 'in', target_analisis_list)],
            'name': 'Análisis de Cumplimiento',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'tree_view_ref': 'crm_robotix.crm_leads_won_analisis_line_tree_view'},
            'res_model': 'crm.leads.won.analisis.line',
            'type': 'ir.actions.act_window'
        }

