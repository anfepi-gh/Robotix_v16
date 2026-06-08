# -*- coding: utf-8 -*-
# Coded by German Ponce Dominguez 
#     ▬▬▬▬▬.◙.▬▬▬▬▬  
#       ▂▄▄▓▄▄▂  
#    ◢◤█▀▀████▄▄▄▄▄▄ ◢◤  
#    █▄ █ █▄ ███▀▀▀▀▀▀▀ ╬  
#    ◥ █████ ◤  
#     ══╩══╩═  
#       ╬═╬  
#       ╬═╬ Dream big and start with something small!!!  
#       ╬═╬  
#       ╬═╬ You can do it!  
#       ╬═╬   Let's go...
#    ☻/ ╬═╬   
#   /▌  ╬═╬   
#   / \
# Cherman Seingalt - german.ponce@outlook.com

import ast
from datetime import datetime, timedelta

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

#### Modelos ####
class PartnerPlanHotel(models.Model):
    _name = 'partner.plan.hotel'
    _description = 'Plan Hotel'
    
    name = fields.Char('Nombre', size=512, required=True)

class PartnerSegmentGroup(models.Model):
    _name = 'partner.segment.group'
    _description = 'Grupos Partner'
    
    name = fields.Char('Nombre', size=512, required=True)

class PartnerFinancialBranch(models.Model):
    _name = 'partner.financial.branch'
    _description = 'Unidad Financiera Partner'
    
    name = fields.Char('Nombre', size=512, required=True)

class PartnerChannelComercial(models.Model):
    _name = 'partner.channel.comercial'
    _description = 'Canal Partner'
    
    name = fields.Char('Nombre', size=512, required=True)

class PartnerSubChannelComercial(models.Model):
    _name = 'partner.subchannel.comercial'
    _description = 'Subcanal Partner'
    
    name = fields.Char('Nombre', size=512, required=True)

class PartnerConsumptionSegment(models.Model):
    _name = 'partner.consumption.segment'
    _description = 'Segmento de Consumo Partner'
    
    name = fields.Char('Nombre', size=512, required=True)

#### Cambios Agosto 2024 ######
class PartnerDriverMan(models.Model):
    _name = 'partner.driver.man'
    _description = 'Choferes'
    _order = "name"

    name = fields.Char('Nombre', size=512, required=True)

class PartnerSalesmanManager(models.Model):
    _name = 'partner.salesman.manager'
    _description = 'Ejecutivos de Ventas'
    _order = "name"

    name = fields.Char('Nombre', size=512, required=True)


class PartnerSalesmanCollection(models.Model):
    _name = 'partner.collection.manager'
    _description = 'Ejecutivos de Cobranza'
    _order = "name"

    name = fields.Char('Nombre', size=512, required=True)

#### Herencia Res Partner ####

class ResPartner(models.Model):
    _inherit ='res.partner'

    plan_hotel_id = fields.Many2one('partner.plan.hotel', 'Plan Hotel')

    city_operation_work = fields.Char('Ciudad donde Opera')

    partner_group_id = fields.Many2one('partner.segment.group', 'Grupo')

    is_driver = fields.Boolean('Es Chofer')

    is_salesman_manager = fields.Boolean('Ejecutivo Ventas')

    is_salesman_collection = fields.Boolean('Ejecutivo Cobranza')

    driver_id = fields.Many2one("partner.driver.man", "Chofer")
    salesman_id = fields.Many2one("partner.salesman.manager", "Ejecutivo de Ventas")
    collection_id = fields.Many2one("partner.collection.manager", "Ejecutivo de Cobranza")

    financial_branch_id = fields.Many2one('partner.financial.branch', 'Unidad Financiera')

    comercial_channel_id = fields.Many2one('partner.channel.comercial', 'Canal')

    comercial_subchannel_id = fields.Many2one('partner.subchannel.comercial', 'Subcanal')

    consumption_segment_id = fields.Many2one('partner.consumption.segment', 'Segmento de Consumo')

    # 17.- Plan Hotel.
    # 18.- Ciudad donde opera.
    # 19.- Grupo.
    # 20.- Es chofer.
    # 21.- Ejecutivo Ventas.
    # 22.- Ejecutivo Cobranza.
    # 23.- Unidad financiera.
    # 24.- Canal.
    # 25.- Subcanal.
    # 26.- Segmento de consumo.

class AccountJournal(models.Model):
    _inherit ='account.journal'

    report_invoice_line_access = fields.Boolean('Reporte líneas de factura')
        

class MoveLineAnalysisByJournals(models.Model):
    _name = 'move.line.analysis.by.journals'
    _description = 'Analisis de Lineas de Factura'
    _rec_name = "numero_factura"
    _order = "fecha_factura desc"

    factura_id = fields.Many2one('account.move', 'Factura')
    numero_factura =  fields.Char('Número Factura', size=512 )
    fecha_factura = fields.Date('Fecha Factura')
    tipo_documento = fields.Selection([
                                        ('out_invoice','Factura'),
                                        ('out_refund','Nota de Cŕedito')
                                      ], string="Tipo de Documento")
    tipo_operacion = fields.Char('Tipo de Operación', size=512 )
    diario =  fields.Char('Diario', size=512 )
    total_factura = fields.Float('Total Factura', digits=(14,4))
    nombre_partner = fields.Char('Cliente', size=512 )
    rfc_partner = fields.Char('RFC', size=512 )
    nombre_comercial = fields.Char('Nombre Comercial', size=512 )
    nombre_branch = fields.Char('Branch', size=512 )
    plan_hotel = fields.Char('Plan Hotel', size=512 )
    ciudad_donde_opera = fields.Char('Ciudad donde Opera', size=512 )
    grupo  = fields.Char('Grupo', size=512 )
    es_chofer = fields.Char('Es Chofer', size=512 )
    es_ejecutivo_ventas = fields.Char('Es Ejecutivo de Ventas', size=512 )
    es_ejecutivo_cobranza = fields.Char('Es Ejecutivo de Cobranza', size=512 )
    chofer = fields.Char('Chofer', size=512 )
    ejecutivo_ventas = fields.Char('Ejecutivo de Cobranza', size=512 )
    ejecutivo_cobranza = fields.Char('Ejecutivo de Cobranza', size=512 )

    unidad_financiera = fields.Char('Unidad Financiera', size=512 )
    canal = fields.Char('Canal', size=512 )
    subcanal = fields.Char('Subcanal', size=512 )
    segmento_de_consumo = fields.Char('Segmento de Consumo', size=512 )
    factura_linea_id = fields.Many2one('account.move.line', 'Linea de Factura')
    descripcion_producto  = fields.Char('Descripción', size=512 )
    nombre_producto = fields.Char('Producto', size=512 )
    referencia_interna_producto = fields.Char('Referencia Interna', size=512 )
    codigo_barras_producto = fields.Char('Código de Barras', size=512 )
    nombre_categoria_producto = fields.Char('Categoria', size=512 )
    cantidad_producto = fields.Float('Cantidad', digits=(14,4))
    precio_unitario = fields.Float('Precio Unitario', digits=(14,4))
    precio_unitario_sin_impuestos = fields.Float('Precio Unitario sin Impuestos', digits=(14,4))
    subtotal = fields.Float('Subtotal', digits=(14,4))
    impuestos_en_linea = fields.Char('Impuestos', size=1024 )
    base_sin_impuestos = fields.Float('Base sin Impuestos', digits=(14,4))
    monto_iva = fields.Float('Monto IVA', digits=(14,4))
    monto_ieps = fields.Float('Monto IEPS', digits=(14,4))
    porcentaje_iva = fields.Float('% IVA', digits=(14,4))
    porcentaje_ieps = fields.Float('% IEPS', digits=())
    monto_total = fields.Float('Total')
    origen_factura = fields.Char('Origen de Factura', size=512 )
    tipo_venta = fields.Char('Tipo de Venta')

class MoveLineAnalysisWizard(models.TransientModel):
    _name = 'move.line.analysis.wizard'
    _description = "Asistente - Analisis de Lineas de Factura"

    def _get_company_defaults(self):
        return Command.set(self.env.companies.ids)

    #CAMPOS PARA GENERAR EL ARCHIVO
    datas_fname = fields.Char('File Name',size=256)
    file = fields.Binary('Layout')
    download_file = fields.Boolean('Descargar Archivo')
    cadena_decoding = fields.Text('Binario sin encoding')

    company_ids = fields.Many2many( 'res.company',
                                    'move_line_wizard_analysis_rel', 'wizard_id', 'company_id',
                                    'Compañias', default=_get_company_defaults, required=True)
    start_date = fields.Datetime("Fecha Inicio", help="Fecha inicial", required=True)
    end_date = fields.Datetime("Fecha Final", help="Fecha final", required=True)

    # company_id = fields.Many2one('res.company', 'Compania', default=lambda self: self.env.company, required=True)
    # report_date = fields.Date('Fecha de Consulta', default=fields.Date.context_today)
    

    @api.constrains('start_date','end_date')
    def _check_dates(self):
        """VALIDA QUE LA FECHA FINAL NO SEA ANTES QUE LA INICIAL"""
        if self.end_date < self.start_date:
            raise UserError("La fecha es incorrecta.")
        return True


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


    def execute_report(self,):
        cr = self.env.cr
        cr.execute("""
                    Truncate table move_line_analysis_by_journals;
                    ALTER SEQUENCE move_line_analysis_by_journals_id_seq RESTART WITH 1;
                    """)

        invoice_line_analysis = self.env['move.line.analysis.by.journals']
        account_journal = self.env['account.journal']

        query_sql_initial = """
WITH invoice_lines AS (
    SELECT
        ai.id AS factura_id,
        ai.name AS numero_factura,
        ai.invoice_date AS fecha_factura,
        ai.move_type AS tipo_documento,
        CASE 
            WHEN ai.move_type = 'out_invoice' THEN 
                '1'
            ELSE '2' 
        END AS tipo_operacion,
        acj.name AS diario,
        ai.amount_total AS total_factura,
        rp.name AS nombre_partner,
        rp.vat AS rfc_partner,
        rp.ref AS nombre_comercial,
        bc.name AS nombre_branch,
        pph.name AS plan_hotel,
        rp.city_operation_work as ciudad_donde_opera,
        psg.name as grupo,
        CASE 
            WHEN rp.is_driver = True THEN 
                'Sí'
            ELSE '' 
        END AS es_chofer,
        CASE 
            WHEN rp.is_salesman_manager = True THEN 
                'Sí'
            ELSE '' 
        END AS es_ejecutivo_ventas,
        CASE 
            WHEN rp.is_salesman_collection = True THEN 
                'Sí'
            ELSE '' 
        END AS es_ejecutivo_cobranza,
        pdrmn.name chofer, 
        pslmngr.name ejecutivo_ventas, 
        pcllmngr.name ejecutivo_cobranza,

        pfb.name AS unidad_financiera,
        pchc.name AS canal,
        pschc.name AS subcanal,
        pcsg.name AS segmento_de_consumo,
        ail.id AS factura_linea_id,
        ail.name AS descripcion_producto,
        COALESCE(pt.name->>'es_MX', pt.name->>'es_ES', pt.name->>'en_US') AS nombre_producto,
        pt.default_code AS referencia_interna_producto,
        pp.barcode AS codigo_barras_producto,
        pc.complete_name AS nombre_categoria_producto,
        ail.quantity AS cantidad_producto,
        ail.price_unit AS precio_unitario,
        ail.x_studio_unitario_sin_impuestos AS precio_unitario_sin_impuestos,
        ail.price_subtotal AS subtotal,
        ARRAY_TO_STRING(ARRAY_AGG(DISTINCT at.name), ', ') AS impuestos_en_linea,
        LEFT(COALESCE(ai.invoice_origin, ''), 500) AS origen_factura,
        SUM(CASE 
            WHEN at.name LIKE '%IVA%' THEN 
               ail.price_subtotal
            ELSE 0 
        END) AS base_sin_impuestos,
        SUM(CASE 
            WHEN at.name LIKE '%IVA%' THEN 
              ail.price_subtotal * (at.amount / 100.0)
            ELSE 0 
        END) AS monto_iva,
        SUM(CASE 
            WHEN at.name LIKE '%IEPS%' THEN 
                ail.price_subtotal * (at.amount / 100.0)
            ELSE 0 
        END) AS monto_ieps,

        SUM(CASE 
            WHEN at.name LIKE '%IVA%' THEN 
              at.amount
            ELSE 0 
        END) AS porcentaje_iva,
        SUM(CASE 
            WHEN at.name LIKE '%IEPS%' THEN 
                at.amount
            ELSE 0 
        END) AS porcentaje_ieps,
        ail.price_total AS monto_total,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM sale_order_line_invoice_rel solir
                WHERE solir.invoice_line_id = ail.id
            ) THEN 'Orden de Venta (SO)'
            WHEN EXISTS (
                SELECT 1 FROM pos_order po
                WHERE po.account_move = ai.id
            ) THEN 'Punto de Venta (POS)'
            ELSE ''
        END AS tipo_venta
    FROM 
        account_move_line ail
    JOIN 
        account_move ai ON ail.move_id = ai.id
    JOIN 
        res_partner rp ON ai.partner_id = rp.id
    LEFT JOIN
        partner_plan_hotel pph on pph.id = rp.plan_hotel_id
    LEFT JOIN
        partner_segment_group psg on psg.id = rp.partner_group_id

    LEFT JOIN
        partner_financial_branch pfb on pfb.id = rp.financial_branch_id
    LEFT JOIN
        partner_channel_comercial pchc on pchc.id = rp.comercial_channel_id
    LEFT JOIN
        partner_subchannel_comercial pschc on pschc.id = rp.comercial_subchannel_id
    LEFT JOIN
        partner_consumption_segment pcsg on psg.id = rp.consumption_segment_id
    LEFT JOIN
        partner_driver_man pdrmn on pdrmn.id = rp.driver_id
    LEFT JOIN
        partner_salesman_manager pslmngr on pslmngr.id = rp.salesman_id
    LEFT JOIN
        partner_collection_manager pcllmngr on pcllmngr.id = rp.collection_id

    JOIN 
        account_journal acj ON acj.id = ai.journal_id
    JOIN 
        product_product pp ON ail.product_id = pp.id
    JOIN 
        product_template pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN 
        res_branch bc ON rp.branch_id = bc.id
    LEFT JOIN 
        product_category pc ON pt.categ_id = pc.id
    LEFT JOIN 
        account_move_line_account_tax_rel amltr ON ail.id = amltr.account_move_line_id
    LEFT JOIN 
        account_tax at ON amltr.account_tax_id = at.id
    """

        query_sql_where = """
    WHERE
     
        ai.move_type IN ('out_invoice', 'out_refund')  -- Filtrar facturas de venta y reembolsos
        AND ai.state = 'posted' 
        AND ail.display_type = 'product' -- Filtrar solo líneas de producto 
        AND acj.type = 'sale' 
        AND acj.report_invoice_line_access = True
    """
        query_sql_where_companies = ""
        if len(self.company_ids.ids) > 1:
            query_sql_where_companies = "AND acj.company_id in "+str(tuple(self.company_ids.ids))
        else:
            query_sql_where_companies = "AND acj.company_id = "+str(self.company_ids.ids[0])

        query_sql_where = query_sql_where+" "+query_sql_where_companies
        
        start_date = str(self.start_date)[0:19]
        end_date = str(self.end_date)[0:19]
        query_sql_where_dates = "AND ai.invoice_date AT TIME ZONE 'UTC-6' BETWEEN '%s' AND '%s' " % (start_date, end_date)
        query_sql_where = query_sql_where+" "+query_sql_where_dates

        query_sql_group_by = """
    GROUP BY 
        ai.id, ail.id, rp.name, rp.vat, rp.ref, ai.invoice_date, ai.name,
        pt.default_code, pt.name, ail.name, pp.barcode, ail.price_unit, ail.x_studio_unitario_sin_impuestos,
        ail.quantity, 
        bc.name, pc.complete_name, ai.move_type, acj.name, pph.name, rp.city_operation_work,
        psg.name, rp.is_driver, rp.is_salesman_manager, rp.is_salesman_collection,
        pdrmn.name, pslmngr.name, pcllmngr.name,
        ai.invoice_origin,
        pfb.name, pchc.name, pschc.name, pcsg.name
    ORDER BY ail.id desc
)"""

        query_sql_insert = """
INSERT INTO move_line_analysis_by_journals (factura_id, numero_factura, fecha_factura, tipo_documento, 
tipo_operacion, diario, total_factura, nombre_partner, rfc_partner, nombre_comercial, nombre_branch, 
plan_hotel, ciudad_donde_opera, grupo, es_chofer, es_ejecutivo_ventas, es_ejecutivo_cobranza, 
chofer, ejecutivo_ventas, ejecutivo_cobranza,
unidad_financiera, canal, subcanal, segmento_de_consumo, factura_linea_id, descripcion_producto, 
nombre_producto, referencia_interna_producto, codigo_barras_producto, nombre_categoria_producto, 
cantidad_producto, precio_unitario, precio_unitario_sin_impuestos, subtotal, impuestos_en_linea, 
base_sin_impuestos, monto_iva, monto_ieps, porcentaje_iva, porcentaje_ieps, monto_total, origen_factura, 
tipo_venta)
SELECT 
        factura_id,
        numero_factura,
        fecha_factura,
        tipo_documento,
        tipo_operacion,
        diario,
        total_factura,
        nombre_partner,
        rfc_partner,
        nombre_comercial,
        nombre_branch,
        plan_hotel,
        ciudad_donde_opera,
        grupo,
        es_chofer,
        es_ejecutivo_ventas,
        es_ejecutivo_cobranza,
        chofer,
        ejecutivo_ventas,
        ejecutivo_cobranza,
        unidad_financiera,
        canal,
        subcanal,
        segmento_de_consumo,
        factura_linea_id,
        descripcion_producto,
        nombre_producto,
        referencia_interna_producto,
        codigo_barras_producto,
        nombre_categoria_producto,
        cantidad_producto,
        precio_unitario,
        precio_unitario_sin_impuestos,
        subtotal,
        impuestos_en_linea,
        base_sin_impuestos,
        monto_iva,
        monto_ieps,
        porcentaje_iva,
        porcentaje_ieps,
        monto_total,
        origen_factura,
        tipo_venta
FROM 
    invoice_lines;

"""
        query_sql = query_sql_initial+" "+query_sql_where+" "+query_sql_group_by+" "+query_sql_insert
        
        cr.execute(query_sql)

        cr.execute("""
update move_line_analysis_by_journals
                                     set total_factura = total_factura * -1,
                                         subtotal = subtotal * -1,
                                         base_sin_impuestos = base_sin_impuestos * -1,
                                         precio_unitario = precio_unitario * -1,
                                         precio_unitario_sin_impuestos = precio_unitario_sin_impuestos * -1,
                                         monto_iva = monto_iva * -1,
                                         monto_ieps = monto_ieps * -1,
                                         monto_total = monto_total * -1
                                where 
                                      tipo_documento = 'out_refund';
""")

        cr.execute("select id from move_line_analysis_by_journals;")
        cr_res = cr.fetchall()
        analysis_lines_ids = []
        if cr_res and cr_res[0] and cr_res[0][0]:
            analysis_lines_ids = [x[0] for x in cr_res]
        return {
            'domain': [('id', 'in', analysis_lines_ids)],
            'name': _('Análisis de Lineas de Factura'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'tree_view_ref': 'crm_robotix.move_line_analysis_by_journals_tree_view'},
            'res_model': 'move.line.analysis.by.journals',
            'type': 'ir.actions.act_window'
            }
                
        
    def monto_linea_iva(self,line):
        total_tax_amount=0.00
        taxes = line.tax_ids
        # tax_line = {tax['id']: tax for tax in line.tax_ids.compute_all(
            #     price, line.currency_id, line.quantity, line.product_id, line.partner_id, self.move_type in ('in_refund', 'out_refund'))['taxes']}
        with_iva = False
        for tax in taxes:
            if 'IVA 16%' in tax.tax_group_id.name.upper():
                with_iva = True
        if with_iva:
            #total_tax_amount = (1+(tax.amount/100))
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))

            taxes_res = line.tax_ids.compute_all(
                line_discount_price_unit,
                quantity=line.quantity,
                currency=line.currency_id,
                product=line.product_id,
                partner=line.partner_id,
                is_refund=line.is_refund,
            )
            taxes = taxes_res['taxes']
            tax_obj = self.env['account.tax']
            for tax_vals in taxes:
                tax_id = tax_vals['id']
                tax_name = tax_vals['name']
                tax_amount = tax_vals['amount']
                tax_br = tax_obj.browse(tax_id)
                if 'IVA 16%' in tax_br.tax_group_id.name.upper():
                    total_tax_amount += tax_amount
        return round(total_tax_amount,2)


    def monto_linea_ieps(self,line):
        total_tax_amount=0.00
        taxes = line.tax_ids
        # tax_line = {tax['id']: tax for tax in line.tax_ids.compute_all(
            #     price, line.currency_id, line.quantity, line.product_id, line.partner_id, self.move_type in ('in_refund', 'out_refund'))['taxes']}
        with_ieps = False
        for tax in taxes:
            if 'IEPS' in tax.name.upper():
                with_ieps = True
        if with_ieps:
            #total_price = (1+(tax.amount/100))
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))

            taxes_res = line.tax_ids.compute_all(
                line_discount_price_unit,
                quantity=line.quantity,
                currency=line.currency_id,
                product=line.product_id,
                partner=line.partner_id,
                is_refund=line.is_refund,
            )
            taxes = taxes_res['taxes']
            tax_obj = self.env['account.tax']
            for tax_vals in taxes:
                tax_id = tax_vals['id']
                tax_name = tax_vals['name']
                tax_amount = tax_vals['amount']
                tax_br = tax_obj.browse(tax_id)
                if 'IEPS' in tax_br.name.upper():
                    total_tax_amount += tax_amount
        return round(total_tax_amount,2)