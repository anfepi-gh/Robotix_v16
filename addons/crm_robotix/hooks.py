# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, fields, SUPERUSER_ID
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Procesar mensajes del chatter para registrar los cambios de etapas en crm.lead.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    ######################################################################################
    ####################### REGISTRO DE ETAPAS ###########################################
    # Obtener todos los leads
    lead_all = env['crm.lead'].search([('active','in',(True,False))])
    crm_stage_obj = env['crm.stage']
    crm_stage = env['crm.stage']
    for lead in lead_all:
        date_won = False
        date_lost = False
        _logger.info("\n ########## Procesando lead: %s" % lead.name)

        team_first_workflow = False

        # Obtener mensajes relacionados con el lead
        messages = env['mail.message'].search([('res_id', '=', lead.id), 
                                               ('model', '=', 'crm.lead')])
        for message in messages:
            _logger.info("\n ########## Mensaje ID: %s" % message.id)
            message_subtype_id = message.subtype_id
            message_subtype_name = message_subtype_id.name
            _logger.info("\n ########## message_subtype_id: %s" % message_subtype_id)
            _logger.info("\n ########## message_subtype_name: %s" % message_subtype_name)
            # Procesar el contenido del mensaje para buscar cambios de etapa
            old_value_integer = False
            new_value_integer = False
            tracking_field_stage_id = False
            date_message = message.date
            for tracking_msg in message.tracking_value_ids:
                _logger.info("\n ***** tracking_msg: %s" % tracking_msg)
                _logger.info("\n ***** tracking_msg.field_id: %s" % tracking_msg.field_id)
                _logger.info("\n ***** tracking_msg.field_id.name: %s" % tracking_msg.field_id.name)
                if tracking_msg.field_id and tracking_msg.field_id.name == 'stage_id':
                    old_value_integer = tracking_msg.old_value_integer
                    new_value_integer = tracking_msg.new_value_integer
                    old_value_integer_exist = crm_stage.search([('id','=',old_value_integer)])
                    new_value_integer_exist = crm_stage.search([('id','=',new_value_integer)])
                    _logger.info("\n ########## old_value_integer_exist: %s" % old_value_integer_exist)
                    _logger.info("\n ########## new_value_integer_exist: %s" % new_value_integer_exist)
                    if new_value_integer_exist:
                        tracking_field_stage_id = True
                        crm_stage_new_br = crm_stage_obj.browse(new_value_integer)
                        if crm_stage_new_br.is_won:
                            if crm_stage_new_br.team_id:
                                team_first_workflow = crm_stage_new_br.team_id.name
                            date_won = message.date
                if tracking_msg.field_id and tracking_msg.field_id.name == 'active':
                    if tracking_msg.new_value_integer <= 0:
                        date_lost = message.date
            _logger.info("\n ########## tracking_field_stage_id: %s" % tracking_field_stage_id)
            _logger.info("\n ########## old_value_integer: %s" % old_value_integer)
            _logger.info("\n ########## new_value_integer: %s" % new_value_integer)
            crm_stage = env['crm.stage']
            if tracking_field_stage_id:
                # Crear registro del cambio de etapa
                if old_value_integer and new_value_integer:
                    old_value_integer_exist = crm_stage.search([('id','=',old_value_integer)])
                    new_value_integer_exist = crm_stage.search([('id','=',new_value_integer)])
                    _logger.info("\n ########## old_value_integer_exist: %s" % old_value_integer_exist)
                    _logger.info("\n ########## new_value_integer_exist: %s" % new_value_integer_exist)
                    if old_value_integer_exist and new_value_integer_exist:
                        stage_change_id = env['crm.lead.stages.changes'].create({
                                                                                    'lead_id': lead.id,
                                                                                    'previous_stage_id': old_value_integer,
                                                                                    'new_stage_id': new_value_integer,
                                                                                    'date': date_message
                                                                                })
                        _logger.info("\n ########## stage_change_id: %s" % stage_change_id)
        lead.date_won = date_won
        lead.date_lost = date_lost
        lead.team_first_workflow_date_won = date_won
        lead.team_first_workflow = team_first_workflow
    ######################################################################################
    ######################################################################################

