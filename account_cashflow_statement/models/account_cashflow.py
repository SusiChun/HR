# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    cash_flow_type = fields.Selection(
        selection=[('operating','Operating Activities'),
                    ('investing','Investing Activities'),
                    ('financing','Financing Activities'),
        ],
        string='Cash Flow Type',
        copy=False,
    )
    financial_report_id = fields.Many2one(
        'account.financial.report',
        string='Financial Report',
        copy=False,
    )

#    @api.onchange('cash_flow_type')
#    def onchange_cash_flow_type(self):
#        FinancialReport = self.env['account.financial.report']
#        operation = self.env.ref(
#            'account_cashflow_statement.account_financial_report_operations0'
#        )
#        investing_activity = self.env.ref(
#            'account_cashflow_statement.account_financial_report_investing0'
#        )
#        financing_activity = self.env.ref(
#            'account_cashflow_statement.account_financial_report_financing0'
#        )
#        parent_id = False
#        for rec in self:
#            rec.financial_report_id = False
#            if rec.cash_flow_type == 'operating':
#                parent_id = operation.id
#            elif rec.cash_flow_type == 'investing':
#                parent_id = investing_activity.id
#            elif rec.cash_flow_type == 'financing':
#                parent_id = financing_activity.id
#        report_ids = FinancialReport.search([('parent_id', '=', parent_id)])
#        return {'domain': {'financial_report_id': [('id', 'in', report_ids.ids)]}}

    @api.model
    def create(self, vals):
        account = super(AccountAccount, self).create(vals)
        if vals.get('financial_report_id', False):
            account_ids = account.financial_report_id.account_ids.ids
            account_ids.append(account.id)
            account.financial_report_id.write({'account_ids':[(6, 0, account_ids)]})
        return account

    @api.multi
    def write(self, vals):
        FinancialReport = self.env['account.financial.report']
        for account in self:
            if vals.get('financial_report_id', False):
                existing_financial_report = account.financial_report_id
                account_ids = existing_financial_report.account_ids.ids
                # Remove from existing Financial Report
                if account.id in account_ids:
                    account_ids.remove(account.id)
                    existing_financial_report.write({'account_ids':[(6, 0, account_ids)]})
                
                # Add to new Financial Report
                new_financial_report_id = FinancialReport.search([('id', '=', vals['financial_report_id'])])
                new_account_ids = new_financial_report_id.account_ids.ids
                new_account_ids.append(account.id)
                new_financial_report_id.write({'account_ids':[(6, 0, new_account_ids)]})

            if vals.get('financial_report_id', False) == False:
                existing_financial_report = account.financial_report_id
                # Remove from old financial report if we remove financial report
                account_ids = existing_financial_report.account_ids.ids
                if account.id in account_ids:
                    account_ids.remove(account.id)
                    existing_financial_report.write({'account_ids':[(6, 0, account_ids)]})
        return super(AccountAccount, self).write(vals)
