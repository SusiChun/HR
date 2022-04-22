# -*- coding: utf-8 -*-

import os
import re
import json
import base64
import logging
import mimetypes

from odoo import _
from odoo import models, api, fields
from odoo.tools import ustr
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base

_logger = logging.getLogger(__name__)

_img_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/src/img'))

class File(dms_base.DMSModel):
    _inherit = 'muk_dms.file'

    document_type_id = fields.Many2one('document.type', string='Document Type')
