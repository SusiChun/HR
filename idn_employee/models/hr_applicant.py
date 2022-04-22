# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    @api.model
    def create(self, vals):
        '''
            This method sends mail to hr manager whenever new applicant is 
            created into the system
            And also send mail to applicant.
        '''
        res = super(HrApplicant, self).create(vals)
        obj_mail_server = self.env['ir.mail_server']
        mail_server_ids = obj_mail_server.search([])
        if not mail_server_ids.ids:
            raise ValidationError(_('Mail Error'),
                                  _('No outgoing mail server is specified!'))
        # fetch users who have rights of HR manager
        res_user_rec = self.env['res.users'].search([])
        res_user_ids = res_user_rec.filtered(lambda x :
                                             x.has_group('hr.group_hr_manager')
                                             ).ids

        emp_ids = self.env['hr.employee'].search([
                                              ('user_id', 'in', res_user_ids)
                                              ])
        # fetch work email of HR manager
        work_email = list(set([str(emp.work_email or emp.user_id.login)
                               for emp in emp_ids]))
        email_to = str(",".join(work_email))
        if not work_email:
            raise ValidationError(_("Please configure as Hr Manager !"))
        # fetch mail template which send mail to HR
        template_ref = 'idn_employee.email_template_application_create'
        template_id = self.env.ref(template_ref)
        template_id.write({'email_to': email_to,
                           'email_from':res.email_from})
        template_id.send_mail(res.id, force_send=True)
        # fetch mail template which sent to applicant
        template_ref1 = 'idn_employee.email_template_application_create_to_applicant'
        template_id1 = self.env.ref(template_ref1)
        template_id1.write({'email_from': email_to,
                            'email_to':res.email_from})
        template_id1.send_mail(res.id, force_send=True)
        return res

    @api.onchange('partner_id')
    def onchange_partner_address_id(self):
        """
        This onchange method is used to check if email_from found
        then delete it and and set email id which mention in partner.
        """
        res = super(HrApplicant, self).onchange_partner_id()
        if res and res.get('value', False) and \
        res['value'].has_key('email_from'):
           del res['value']['email_from']
        return res

        job_id = fields.Many2one('hr.job', 'Job',
                                 domain=[('state', '=', 'open')])
