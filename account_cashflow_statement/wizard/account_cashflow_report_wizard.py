# -*- coding: utf-8 -*-

from odoo import fields, models, api

class AccountingCashFlowStatementReport(models.TransientModel):
    _inherit = "accounting.report"
    _description = 'Accounting Cash Flow Statement Report'

    is_cash_flow = fields.Boolean(
        string="Is Cash Flow Statement?",
        help='If tick mean it is cash flow statement wizard.',
    )
    init_balance_amount = fields.Float(
        string="Cash Initial Balance",
        help='Cash at Beginning of Period/Year in company currency.',
    )
    init_balance_date = fields.Date(
        string="For the Period/Year Ending",
    )

    @api.multi
    def check_report(self):#Override Odoo FR method.
        res = super(AccountingCashFlowStatementReport, self).check_report()
        if res.get('data', False):
            if res['data'].get('form', False):
                res['data']['form'].update(self.read(['is_cash_flow', 'init_balance_amount', 'init_balance_date'])[0])
        return res
