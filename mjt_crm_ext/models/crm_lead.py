# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    product_id = fields.Many2one('product.template', string='Product')
    crm_lead_document_ids = fields.One2many('crm.lead.document', 'lead_id', string='Document Requirement')


    # dokumen pribadi
    requested_amount = fields.Integer(string="Requested Amount")
    approved_amount = fields.Integer(string="Approved Amount")
    salary = fields.Integer(string="Salary")
    age = fields.Integer(string="Age")
    bi_checking = fields.Boolean("BI Checking")
    installment_amount = fields.Integer("Installment Amount", default=0)
    installment_duration = fields.Integer("Installment Duration", default=0)
    cost_of_living = fields.Integer(string='Cost of Living')
    prescreening_percentage = fields.Integer(string='Pre-Screening', compute='_compute_prescreening_percentage')
    completenes_doc_percentage = fields.Integer(string='Completeness of Document', compute='_compute_completenes_doc_percentage')

    @api.multi        
    @api.depends('requested_amount','age','crm_lead_document_ids', 'salary', 'bi_checking', 'product_id')
    def _compute_prescreening_percentage(self):
        percentage = 0
        if self.product_id:
            if self.product_id.id == 1:
                print(self.age)
                if (self.salary * 3) > self.requested_amount:
                    percentage += 40
                if self.age >= 20 and self.age <= 55:
                    percentage += 30
                if self.bi_checking == True:
                    percentage += 30
            elif self.product_id.id == 2:
                percentage = 0
                if (self.salary * 0.3) > self.installment_amount:
                    percentage += 20
                if (self.salary - self.cost_of_living) > self.installment_amount:
                    percentage += 20
                if self.age and self.age >= 20:
                    age_applied = (self.age + self.installment_duration)
                    if age_applied < 55:
                        percentage += 30
                if self.bi_checking == True:
                    percentage += 30
        else:
            percentage = 0

        self.prescreening_percentage = percentage

    @api.multi
    @api.depends('crm_lead_document_ids')
    def _compute_completenes_doc_percentage(self):
        point = 0
        count_all_document = len(self.crm_lead_document_ids)
        if count_all_document > 0:
            point = 100/count_all_document

        count_completenes_document = len(self.crm_lead_document_ids.filtered(lambda r: r.status == True and r.is_mandatory == True))

        percentage = (count_completenes_document * point)
        self.completenes_doc_percentage = percentage

    def next_step_from_rm_to_rmsupport(self):
        if self.completenes_doc_percentage < 100 or self.prescreening_percentage < 100:
            raise ValidationError(_('Sorry, your request is refused. Please check your submission data!'))
        else:
            self.write({
                'stage_id': 2
                })

    # @api.multi
    # @api.onchange('product_id')
    def generate_requirement_document(self):
        for lead in self:
            if lead.product_id:
                CrmLeadDocument = self.env['crm.lead.document']
                if not lead.crm_lead_document_ids:
                    for record in lead.product_id.crm_required_document_ids:
                        crm_lead_document_id = CrmLeadDocument.create({
                            'lead_id': lead.id,
                            'document_id': record.id,
                            'is_mandatory': True,
                            'description': "",
                          })
                else:
                    for data in lead.product_id.crm_required_document_ids:
                        if data.id not in lead.crm_lead_document_ids.mapped('document_id').ids:
                            crm_lead_document_id = CrmLeadDocument.create({
                                'lead_id': lead.id,
                                'document_id': data.id,
                                'is_mandatory': True,
                                'description': "",
                              })

                    for doc in lead.crm_lead_document_ids:
                        if doc.document_id.id not in lead.product_id.crm_required_document_ids.ids:
                            doc.is_mandatory = False

                if lead.crm_lead_document_ids:
                    for data in lead.crm_lead_document_ids:
                        if lead.partner_id.dms_id.files:
                            for record in lead.partner_id.dms_id.files:
                                if record.document_type_id == data.document_id:
                                    data.file = record.content
                                    data.name = record.name
                                    if data.file:
                                        data.status = True
