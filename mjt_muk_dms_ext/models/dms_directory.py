# -*- coding: utf-8 -*-

import os
import json
import base64
import logging

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

_img_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/src/img'))

class Directory(dms_base.DMSModel):
    _inherit = 'muk_dms.directory'

    partner_id = fields.Many2one('res.partner', string='Customer')

    @api.multi
    @api.onchange('partner_id')
    def onchange_dms_form_value(self):
        if self.partner_id:
        	directory_id = self.env.ref('mjt_muk_dms_ext.customer_dms_directory', False)
        	self.name = self.partner_id.name
        	self.parent_directory = directory_id
