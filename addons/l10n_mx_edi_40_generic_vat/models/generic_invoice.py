# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2021 German Ponce Dominguez
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError

from odoo.tools import float_is_zero, float_compare
from itertools import groupby
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


############# Contactos ####################
class ResPartner(models.Model):
    _inherit ='res.partner'

    @api.depends('vat')
    def _is_contact_general_public(self):
        for rec in self:
            contact_general_public = False
            if rec.vat:
                if 'XAXX010101000' in rec.vat:# or 'XEXX010101000' in self.vat:
                    contact_general_public = True    
            rec.contact_general_public = contact_general_public


    l10n_mx_edi_usage = fields.Selection([
        ('G01', 'G01 - Adquisición de mercancias'),
        ('G02', 'G02 - Devoluciones, descuentos o bonificaciones'),
        ('G03', 'G03 - Gastos en general'),
        ('I01', 'I01 - Construcciones'),
        ('I02', 'I02 - Mobilario y equipo de oficina por inversiones'),
        ('I03', 'I03 - Equipo de transporte'),
        ('I04', 'I04 - Equipo de computo y accesorios'),
        ('I05', 'I05 - Dados, troqueles, moldes, matrices y herramienta'),
        ('I06', 'I06 - Comunicaciones telefónicas'),
        ('I07', 'I07 - Comunicaciones satelitales'),
        ('I08', 'I08 - Otra maquinaria y equipo'),
        ('D01', 'D01 - Honorarios médicos, dentales y gastos hospitalarios.'),
        ('D02', 'D02 - Gastos médicos por incapacidad o discapacidad'),
        ('D03', 'D03 - Gastos funerales'),
        ('D04', 'D04 - Donativos'),
        ('D05', 'D05 - Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)'),
        ('D06', 'D06 - Aportaciones voluntarias al SAR'),
        ('D07', 'D07 - Primas por seguros de gastos médicos'),
        ('D08', 'D08 - Gastos de transportación escolar obligatoria'),
        ('D09', 'D09 - Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.'),
        ('D10', 'D10 - Pagos por servicios educativos (colegiaturas)'),
        ('P01', 'P01 - Por definir'),
        ('S01', 'Sin efectos fiscales'),
    ], 'Uso CFDI', default='P01')

    contact_general_public    = fields.Boolean(string='Cliente Publico en General', help="Comodin cliente para facturas globales.", compute="_is_contact_general_public")
    
    # @api.onchange('vat')
    # def on_change_use_as_general_public(self):
    #     res = {}
    #     if self.vat:
    #         if 'XAXX010101000' in self.vat:# or 'XEXX010101000' in self.vat:
    #             self.contact_general_public = True    

    # @api.constrains('vat')
    # def _constraint_uniq_vat(self):
    #    if self.is_company and self.vat:
    #         other_partner = self.search([('vat','=',self.vat),('id','!=',self.id),('is_company','=',True)])
    #         if other_partner:
    #             raise UserError(_("Error!\nEl RFC ya existe en la Base de Datos"))



############# Herencia Facturas ####################


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit ='account.move'

    l10n_mx_edi_usage = fields.Selection([
        ('G01', 'G01 - Adquisición de mercancias'),
        ('G02', 'G02 - Devoluciones, descuentos o bonificaciones'),
        ('G03', 'G03 - Gastos en general'),
        ('I01', 'I01 - Construcciones'),
        ('I02', 'I02 - Mobilario y equipo de oficina por inversiones'),
        ('I03', 'I03 - Equipo de transporte'),
        ('I04', 'I04 - Equipo de computo y accesorios'),
        ('I05', 'I05 - Dados, troqueles, moldes, matrices y herramienta'),
        ('I06', 'I06 - Comunicaciones telefónicas'),
        ('I07', 'I07 - Comunicaciones satelitales'),
        ('I08', 'I08 - Otra maquinaria y equipo'),
        ('D01', 'D01 - Honorarios médicos, dentales y gastos hospitalarios.'),
        ('D02', 'D02 - Gastos médicos por incapacidad o discapacidad'),
        ('D03', 'D03 - Gastos funerales'),
        ('D04', 'D04 - Donativos'),
        ('D05', 'D05 - Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)'),
        ('D06', 'D06 - Aportaciones voluntarias al SAR'),
        ('D07', 'D07 - Primas por seguros de gastos médicos'),
        ('D08', 'D08 - Gastos de transportación escolar obligatoria'),
        ('D09', 'D09 - Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones.'),
        ('D10', 'D10 - Pagos por servicios educativos (colegiaturas)'),
        ('P01', 'P01 - Por definir'),
        ('S01', 'Sin efectos fiscales'),
    ], 'Uso CFDI', default='P01')


    #### Factura Global ####

    global_invoice = fields.Boolean('Factura Global')

    invoice_general_public = fields.Boolean('Factura Publico en General')

    fg_periodicity = fields.Selection(
        selection=[('01', '01 - Diario'),
                   ('02', '02 - Semanal'),
                   ('03', '03 - Quincenal'),
                   ('04', '04 - Mensual'),
                   ('05', '05 - Bimestral'),],
        string=_('Periodicidad'),
    )

    fg_months = fields.Selection(
        selection=[('01', '01 - Enero'),
                   ('02', '02 - Febrero'),
                   ('03', '03 - Marzo'),
                   ('04', '04 - Abril'),
                   ('05', '05 - Mayo'),
                   ('06', '06 - Junio'),
                   ('07', '07 - Julio'),
                   ('08', '08 - Agosto'),
                   ('09', '09 - Septiembre'),
                   ('10', '10 - Octubre'),
                   ('11', '11 - Noviembre'),
                   ('12', '12 - Diciembre'),
                   ('13', '13 - Enero - Febrero'),
                   ('14', '14 - Marzo - Abril'),
                   ('15', '15 - Mayo - Junio'),
                   ('16', '16 - Julio - Agosto'),
                   ('17', '17 - Septiembre - Octubre'),
                   ('18', '18 - Noviembre - Diciembre'),],
        string=_('Meses'),
    )

    fg_year =  fields.Char(string=_('Año'))


    # @api.constrains('l10n_mx_edi_payment_method_id','l10n_mx_edi_payment_method_id')
    # def _constraint_general_public(self):
    #     for rec in self:
    #         if rec.move_type == 'out_invoice':
    #             if rec.invoice_general_public:
    #                 if rec.l10n_mx_edi_payment_method_id and rec.l10n_mx_edi_payment_method_id.code == '99':
    #                     raise UserError("No se puede utilizar la Forma de Pago 'Por definir' cuando facturamos a publico en general.")
    #     return True

    def action_process_edi_web_services(self, with_commit=True):
        for rec in self:
            if rec.move_type == 'out_invoice':
                if rec.invoice_general_public:
                    if rec.l10n_mx_edi_payment_method_id and rec.l10n_mx_edi_payment_method_id.code == '99':
                        raise UserError("No se puede utilizar la Forma de Pago 'Por definir' cuando facturamos a publico en general.")
                    # if rec.l10n_mx_edi_payment_policy == 'PPD':
                    #     raise UserError("No se puede utilizar el metodo de Pago PPD cuando facturamos a publico en general.")

        res = super(AccountMove, self).action_process_edi_web_services(with_commit=with_commit)
        return res

    def action_post(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                if rec.invoice_general_public:
                    if rec.l10n_mx_edi_payment_method_id and rec.l10n_mx_edi_payment_method_id.code == '99':
                        raise UserError("No se puede utilizar la Forma de Pago 'Por definir' cuando facturamos a publico en general.")
                    # if rec.l10n_mx_edi_payment_policy == 'PPD':
                    #     raise UserError("No se puede utilizar el metodo de Pago PPD cuando facturamos a publico en general.")

        res = super(AccountMove, self).action_post()
        return res

    @api.depends('move_type', 'invoice_date_due', 'invoice_date', 'invoice_payment_term_id', 'invoice_payment_term_id.line_ids')
    def _compute_l10n_mx_edi_payment_policy(self):
        for move in self:
            if move.is_invoice(include_receipts=True) and move.invoice_date_due and move.invoice_date:
                if move.move_type == 'out_invoice':
                    # In CFDI 3.3 - rule 2.7.1.43 which establish that
                    # invoice payment term should be PPD as soon as the due date
                    # is after the last day of  the month (the month of the invoice date).
                    if move.invoice_general_public:
                        move.l10n_mx_edi_payment_policy = 'PUE'
                    else:
                        if move.invoice_date_due.month > move.invoice_date.month or \
                           move.invoice_date_due.year > move.invoice_date.year or \
                           len(move.invoice_payment_term_id.line_ids) > 1:  # to be able to force PPD
                            move.l10n_mx_edi_payment_policy = 'PPD'
                        else:
                            move.l10n_mx_edi_payment_policy = 'PUE'
                else:
                    move.l10n_mx_edi_payment_policy = 'PUE'
            else:
                if move.move_type == 'out_refund':
                    move.l10n_mx_edi_payment_policy = 'PUE'
                else:
                    move.l10n_mx_edi_payment_policy = False


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.contact_general_public:
            self.invoice_general_public = True
            self.l10n_mx_edi_payment_policy = 'PUE'
            self.l10n_mx_edi_usage = 'S01'
        return super()._onchange_partner_id()
    

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        #if not res.l10n_mx_edi_usage:
        if res.move_type == 'out_invoice':
            if res.invoice_general_public:
                res.l10n_mx_edi_payment_policy = 'PUE'
                res.l10n_mx_edi_usage = 'S01'
            else:
                if res.partner_id.vat:
                    if 'XAXX010101000' in res.partner_id.vat:# or 'XEXX010101000' in self.vat:
                        contact_general_public = True 
                        res.invoice_general_public = True
                        res.l10n_mx_edi_payment_policy = 'PUE'
                        res.l10n_mx_edi_usage = 'S01'
        return res

    def write(self, vals):
        partner_obj = self.env['res.partner']
        if vals.get('partner_id',False):
            partner_br = partner_obj.browse(vals.get('partner_id'))
            if partner_br.contact_general_public:
                vals.update({'l10n_mx_edi_payment_policy': 'PUE'})
                vals.update({'l10n_mx_edi_usage': 'S01'})
                vals.update({'invoice_general_public': True})
        ret = super(AccountMove, self).write(vals)
        return ret

    @api.onchange('invoice_general_public','partner_id','invoice_date')
    def onchange_invoice_general_public(self):
        if self.invoice_general_public or self.partner_id.vat == 'XAXX010101000':

            self.l10n_mx_edi_payment_policy = 'PUE'
            self.l10n_mx_edi_usage = 'S01'

            invoice_date = self.invoice_date or fields.Date.context_today(self)
            current_date = datetime.strptime(str(invoice_date)[0:10], DEFAULT_SERVER_DATE_FORMAT)
            month = str(current_date.month)
            if current_date.month < 10:
                month = '0'+str(current_date.month)

            year = current_date.year
            
            if not self.fg_periodicity:
                self.fg_periodicity = '01'

            if self.fg_periodicity in ('01', '02', '03', '04'):
                self.fg_months = str(month)
            else:
                if month in ('01','02'):
                    self.fg_months = '13'
                elif month in ('03','04'):
                    self.fg_months = '14'
                elif month in ('05','06'):
                    self.fg_months = '15'
                elif month in ('07','08'):
                    self.fg_months = '16'
                elif month in ('09','10'):
                    self.fg_months = '17'
                else:
                    self.fg_months = '18'
                    
            self.fg_year = str(year)
            self.global_invoice  = True

    def get_edi_receptor_dynamic_info(self, edi_attr, current_info):
        description_edi = ""
        invoice_general_public = self.invoice_general_public
        if not invoice_general_public:
            if self.partner_id.vat:
                if 'XAXX010101000' in self.partner_id.vat or self.partner_id.contact_general_public:# or 'XEXX010101000' in self.vat:
                    invoice_general_public = True 
        self.invoice_general_public = invoice_general_public
        if invoice_general_public:
            self.onchange_invoice_general_public()
        if edi_attr == 'rfc':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'XAXX010101000'
        if edi_attr == 'codigopostalreceptor':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                issued_address = self._get_l10n_mx_edi_issued_address()
                description_edi =issued_address.zip
        if edi_attr == 'usocfdi':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'S01'
        if edi_attr == 'regimenfiscalreceptor':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = '616'
        if edi_attr == 'nombre':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'PUBLICO EN GENERAL'

        if edi_attr == 'metodopago':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'PUE'

        if edi_attr == 'condicionesdepago':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'Contado'
                description_edi = 'Pago de Contado'
        if not description_edi:
            return False
        return description_edi


class AccountPayment(models.Model):
    _inherit ='account.payment'

    def get_edi_receptor_dynamic_info(self, edi_attr, current_info):
        description_edi = ""
        invoice_general_public = self.invoice_general_public
        if self.partner_id.vat:
            if 'XAXX010101000' in self.partner_id.vat or self.partner_id.contact_general_public:# or 'XEXX010101000' in self.vat:
                invoice_general_public = True 

        if invoice_general_public:
            self.onchange_invoice_general_public()
        if edi_attr == 'rfc':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'XAXX010101000'
        if edi_attr == 'codigopostalreceptor':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                issued_address = self._get_l10n_mx_edi_issued_address()
                description_edi =issued_address.zip
        if edi_attr == 'usocfdi':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'S01'
        if edi_attr == 'regimenfiscalreceptor':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = '616'
        if edi_attr == 'nombre':
            if current_info:
                description_edi = current_info
            if invoice_general_public:
                description_edi = 'PUBLICO EN GENERAL'
        return description_edi