# -*- encoding: utf-8 -*-
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

from lxml.objectify import fromstring
from odoo import api, fields, models

from odoo.exceptions import UserError

import re

import logging
_logger = logging.getLogger(__name__)


#### Librerias LdM E.E. ###
from lxml import etree
from xml.dom import minidom
from xml.dom.minidom import parse, parseString

from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
import base64
from io import BytesIO
from lxml.objectify import fromstring

### Reemplazo de las Cadenas XSLT Para Cadena
CFDI_TEMPLATE_33 = 'l10n_mx_edi_40.cfdiv40'

def create_list_html(array):
    '''Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise.
    '''
    if not array:
        return ''
    msg = ''
    for item in array:
        msg += '<li>' + item + '</li>'
    return '<ul>' + msg + '</ul>'


# Cambiar el error
msg2 = "Contacta a tu administrador de Sistema o contactanos info@argil.mx"

#### Metodos de la LdM E.E. ####

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'
    
    def _l10n_mx_edi_export_invoice_cfdi(self, invoice):
        self.ensure_one()
        if not invoice.complemento_donaciones:
            return super(AccountEdiFormat, self)._l10n_mx_edi_export_invoice_cfdi(invoice)

        # == CFDI values ==
        cfdi_values = self._l10n_mx_edi_get_invoice_cfdi_values(invoice)

        ### Vista Custom ####
        activate_view_tax = False
        view_br = self.env['ir.ui.view'].browse(3428)
        for line in invoice.invoice_line_ids:
            if line.product_id.x_studio_objeto_de_impuestos == '01':
                activate_view_tax = True
                break
        if activate_view_tax:
            view_br.active = True

        # == Generate the CFDI ==
        qweb_template, xsd_attachment_name = self._l10n_mx_edi_get_invoice_templates()

        # == Generate the CFDI ==
        cfdi = self.env['ir.qweb']._render(qweb_template, cfdi_values)

        cfdi_minidom = minidom.parseString(cfdi)
        
        ######## Agregamos los Prefijos de Carta Porte en la Cabecera Principal #########       
        subnode_cfdi_comprobante = cfdi_minidom.getElementsByTagName('cfdi:Comprobante')[0]
        ### Agregamos el Atributo de la Carta porte Prefix ####
        subnode_cfdi_comprobante.setAttribute('xmlns:donat', "http://www.sat.gob.mx/donat")
        subnode_cfdi_comprobante.setAttribute('xsi:schemaLocation', "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/donat http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd")

        # #### Eliminando el Namespace Secundario de Carta Porte ####
        # if cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte'):
        #     subnode_cfdi_complemento_carta_porte = cfdi_minidom.getElementsByTagName('cartaporte20:CartaPorte')[0]                    
        #     subnode_cfdi_complemento_carta_porte.removeAttribute('xsi:schemaLocation')
        #     # subnode_cfdi_complemento_carta_porte.removeAttribute('xmlns:cartaporte20')
            
        cfdi_custom = cfdi_minidom.toxml('UTF-8')
        cfdi = cfdi_custom
            
        #### Proceso Normal ####
        decoded_cfdi_values = invoice._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi)
        cfdi_cadena_crypted = cfdi_values['certificate'].sudo()._get_encrypted_cadena(decoded_cfdi_values['cadena'])
        decoded_cfdi_values['cfdi_node'].attrib['Sello'] = cfdi_cadena_crypted

        # == Optional check using the XSD ==
        # xsd_attachment = self.env.ref('l10n_mx_edi.xsd_cached_cfdv33_xsd', False)
        # xsd_datas = base64.b64decode(xsd_attachment.datas) if xsd_attachment else None

        # if xsd_datas:
        #     try:
        #         with BytesIO(xsd_datas) as xsd:
        #             _check_with_xsd(decoded_cfdi_values['cfdi_node'], xsd)
        #     except (IOError, ValueError):
        #         _logger.info(_('The xsd file to validate the XML structure was not found'))
        #     except Exception as e:
        #         return {'errors': str(e).split('\\n')}
        cfdi_previo = etree.tostring(decoded_cfdi_values['cfdi_node'], pretty_print=True, xml_declaration=True, encoding='UTF-8')
        cfdi_previo_debug = str(cfdi_previo).replace('\n','')
        _logger.info("\nCFDI Previo con Complemento Carta Porte:\n%s" % cfdi_previo_debug)

        ### Vista Custom ####
        if activate_view_tax:
            view_br.active = False

        return {
            'cfdi_str': cfdi_previo,
        }

class AccountMove(models.Model):
    _inherit = 'account.move'

    complemento_donaciones = fields.Boolean(
        'Complemento - Donatarias',
        help='Use this field when the invoice require the complement to '
        '"Donations". This value will be used to indicate the use of the '
        'information from the document that authorize to receive '
        'deductible donations, granted by SAT')


    def _l10n_mx_edi_decode_cfdi(self, cfdi_data=None):
        """If the CFDI was signed, try to adds the schemaLocation correctly"""
        result = super()._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi_data)
        if not cfdi_data:
            return result
        if not isinstance(cfdi_data, bytes):
            cfdi_data = cfdi_data.encode()
        cfdi_data = cfdi_data.replace(b'xmlns__donat', b'xmlns:donat')
        cfdi = fromstring(cfdi_data)
        if 'donat' not in cfdi.nsmap:
            return result
        cfdi.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'] = '%s %s %s' % (
            cfdi.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'),
            'http://www.sat.gob.mx/donat', 'http://www.sat.gob.mx/sitio_internet/cfd/donat/donat11.xsd')
        result['cfdi_node'] = cfdi
        return result

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id.complemento_donaciones:
            self.complemento_donaciones = True
        return super()._onchange_partner_id()

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.complemento_donaciones:
                vals.update({
                                'complemento_donaciones': True,
                            })
        return super().create(vals)

