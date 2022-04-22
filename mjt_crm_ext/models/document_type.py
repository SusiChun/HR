# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    _name = 'document.type'

    name = fields.Char("Name")
    code = fields.Char("code")
