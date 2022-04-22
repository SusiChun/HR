# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrmLeadDocument(models.Model):
    _name = 'crm.lead.document'

    name = fields.Char(string='Name')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    document_id = fields.Many2one('document.type', string='Document Type')
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Attachment name')
    description = fields.Char('Description')
    is_mandatory = fields.Boolean(string="Mandatory")
    status = fields.Boolean('Status')

    @api.multi
    def name_get(self):
        res = []
        for lead_document in self:
            res.append((lead_document.id, "%s" % (lead_document.document_id.name)))
        return res

    @api.onchange('file')
    def onchange_product_expired_status(self):
        if self.file:
            self.update({
                'status': True
                })
