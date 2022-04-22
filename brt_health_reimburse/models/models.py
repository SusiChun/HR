# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import time
from Tkconstants import LEFT
from datetime import date
from time import gmtime, strftime

class brt_health_reimburse(models.Model):
    _name 			= 'brt_health.reimburse'
    _inherit 		= ['mail.thread', 'ir.needaction_mixin']
    _description 	= "Health Reimburse"
    _order 			= "date desc, id desc"

    name 			= fields.Char(string='Reimburse Health Description', required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    date 			= fields.Date(default=fields.Date.context_today, string="Date",readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    employee_id     = fields.Many2one('hr.employee', string="Employee", required=True, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    # employee_id 	= fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    product_id 		= fields.Many2one('product.product', string='Product', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, domain=[('can_be_expensed', '=', True)], required=True)
    product_uom_id 	= fields.Many2one('product.uom', string='Unit of Measure', required=True, default=lambda self: self.env['product.uom'].search([], limit=1, order='id'))
    unit_amount 	= fields.Float(string='Unit Price',required=True,readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    quantity 		= fields.Float(required=True,default=1,readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    tax_ids 		= fields.Many2many('account.tax', 'expense_tax', 'expense_id', 'tax_id', string='Taxes', states={'done': [('readonly', True)], 'post': [('readonly', True)]})
    untaxed_amount 	= fields.Float(string='Subtotal', store=True, compute='_compute_amount')
    total_amount 	= fields.Float(string='Total', store=True, compute='_compute_amount')
    company_id 		= fields.Many2one('res.company', string='Company',readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    currency_id 	= fields.Many2one('res.currency', string='Currency', readonly=False,  default=lambda self: self.env.user.company_id.currency_id)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', oldname='analytic_account')
    account_id 		= fields.Many2one('account.account', string='Account', default=lambda self: self.env['ir.property'].get('property_account_expense_categ_id', 'product.category'),
        help="An expense account is expected")
    description 	= fields.Text()
    payment_mode 	= fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")], default='own_account', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, string="Payment By")
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    state 			= fields.Selection([('draft', 'To Submit'),('waitmanager', 'Confirm Manager'),('waithrd', 'Confirm HRD'),('done', 'Posted')], string='Status', default='draft', copy=False, index=True, readonly=True, store=True,help="Status", track_visibility='onchange')
    sheet_id 		= fields.Many2one('brt_health.reimburse.sheet', string="Expense Report", readonly=True, copy=False)
    reference 		= fields.Char(string="Bill Reference")
    limit_reimbers_year = fields.Float(string="Limit", compute='compute_limit_for_wage')
    berobat             = fields.Float(string="Berobat", compute='compute_limit_for_wage')
    kacamata            = fields.Float(string="Kacamata", compute='compute_limit_for_wage')
    sisa                = fields.Float(string="Sisa", compute='compute_limit_for_wage')
    
    @api.multi
    def compute_limit_for_wage(self):
        for x in self:
            data = self.env[('hr.contract')].search([('employee_id','=',self.employee_id.id)],order='id desc', limit=1)
            for y in data:
                if y:
                    self.limit_reimbers_year    = data.limit_reimbers_year
                    self.berobat                = data.berobat
                    self.kacamata               = data.kacamata
                    self.sisa                   = data.sisa

    @api.onchange('employee_id')
    def _onchange_employee_limit(self):
        data = self.env[('hr.contract')].search([('employee_id','=',self.employee_id.id),('state','=','pending')])
        self.limit_reimbers_year    = data.limit_reimbers_year
        self.berobat                = data.berobat
        self.kacamata               = data.kacamata
        self.sisa                   = data.sisa

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id, expense.employee_id.user_id.partner_id)
            expense.total_amount = taxes.get('total_included')

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'brt_health.reimburse'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name or ''
            self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id
            self.tax_ids = self.product_id.supplier_taxes_id
            account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                self.account_id = account

    @api.onchange('product_uom_id')
    def _onchange_product_uom_id(self):
        if self.product_id and self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            raise UserError(_('Selected Unit of Measure does not belong to the same category as the product Unit of Measure'))

    @api.multi
    def view_sheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'brt_health.reimburse.sheet',
            'target': 'current',
            'res_id': self.sheet_id.id
        }

    @api.multi
    def submit_approve_hrd(self):
        total_harga     = self.total_amount
        # self.env.cr.execute(""" UPDATE hr_contract SET sisa = sisa + %s WHERE employee_id = %s""", (total_harga,self.employee_id.id,))
        data = self.env[('hr.contract')].search([('employee_id','=',self.employee_id.id),('state','=','pending')])
        nilai_kacamata = data.kacamata + total_harga
        nilai_berobat = data.berobat + total_harga
        if self.product_id.name == 'Kacamata':
            # self.env['hr.contract'].write({'name': record.buyer_full_name.title(), 'city': record.buyer_city.title(), 'street': record.buyer_address_1.title(), 'street2': record.buyer_address_2.title(), 'zip': postcode.upper(),'email': record.buyer_email.lower(), 'phone': record.buyer_phone_number})
            print ' ================= ========== CEK 1'
            self.env.cr.execute(""" UPDATE hr_contract SET kacamata = %s WHERE employee_id = %s""", (nilai_kacamata,self.employee_id.id))
            self.env.cr.commit()
        else:
            print ' ================= ========== CEK 2'
            self.env.cr.execute(""" UPDATE hr_contract SET berobat = %s WHERE employee_id = %s""", (nilai_berobat,self.employee_id.id,))
            self.env.cr.commit()
        self.state = 'done'
        

    @api.multi
    def submit_approve_manager(self):
        self.state = 'waithrd'

    @api.multi
    def reset_to_draft(self):
        self.state = 'draft'
    
    @api.multi
    def submit_expenses(self):
        print ' ================= ==========  Belum Ada',self.total_amount
        total_harga     = self.total_amount
        data = self.env[('hr.contract')].search([('employee_id','=',self.employee_id.id)])
        # for y in data:
        # if data.sisa < self.total_amount:
            # print ' ================= ========== TIDAK BISA',data.sisa
        # else:
        self.state = 'waitmanager'
            # print ' ================= ========== BISA',data.sisa

    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        partner_id = self.employee_id.address_home_id.commercial_partner_id.id
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and - line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or - abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'tax_ids': line.get('tax_ids'),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
            'payment_id': line.get('payment_id'),
        }

    @api.multi
    def _compute_expense_totals(self, company_currency, account_move_lines, move_date):
        '''
        internal method used for computation of total amount of an expense in the company currency and
        in the expense currency, given the account_move_lines that will be created. It also do some small
        transformations at these account_move_lines (for multi-currency purposes)

        :param account_move_lines: list of dict
        :rtype: tuple of 3 elements (a, b ,c)
            a: total in company currency
            b: total in brt_health.reimburse currency
            c: account_move_lines potentially modified
        '''
        self.ensure_one()
        total = 0.0
        total_currency = 0.0
        for line in account_move_lines:
            line['currency_id'] = False
            line['amount_currency'] = False
            if self.currency_id != company_currency:
                line['currency_id'] = self.currency_id.id
                line['amount_currency'] = line['price']
                line['price'] = self.currency_id.with_context(date=move_date or fields.Date.context_today(self)).compute(line['price'], company_currency)
            total -= line['price']
            total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, account_move_lines

    @api.multi
    def _prepare_move_values(self):
        """
        This function prepares move values related to an expense
        """
        self.ensure_one()
        journal = self.sheet_id.bank_journal_id if self.payment_mode == 'company_account' else self.sheet_id.journal_id
        acc_date = self.sheet_id.accounting_date or self.date
        move_values = {
            'journal_id': journal.id,
            'company_id': self.env.user.company_id.id,
            'date': acc_date,
            'ref': self.sheet_id.name,
            # force the name to the default value, to avoid an eventual 'default_name' in the context
            # to set it to '' which cause no number to be given to the account.move when posted.
            'name': '/',
        }
        return move_values

   

    @api.multi
    def _prepare_move_line_value(self):
        self.ensure_one()
        if self.account_id:
            account = self.account_id
        elif self.product_id:
            account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            if not account:
                raise UserError(
                    _("No Expense account found for the product %s (or for it's category), please configure one.") % (self.product_id.name))
        else:
            account = self.env['ir.property'].with_context(force_company=self.company_id.id).get('property_account_expense_categ_id', 'product.category')
            if not account:
                raise UserError(
                    _('Please configure Default Expense account for Product expense: `property_account_expense_categ_id`.'))
        aml_name = self.employee_id.name + ': ' + self.name.split('\n')[0][:64]
        move_line = {
            'type': 'src',
            'name': aml_name,
            'price_unit': self.unit_amount,
            'quantity': self.quantity,
            'price': self.total_amount,
            'account_id': account.id,
            'product_id': self.product_id.id,
            'uom_id': self.product_uom_id.id,
            'analytic_account_id': self.analytic_account_id.id,
        }
        return move_line

    @api.multi
    def _move_line_get(self):
        account_move = []
        for expense in self:
            move_line = expense._prepare_move_line_value()
            account_move.append(move_line)

            # Calculate tax lines and adjust base line
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            account_move[-1]['price'] = taxes['total_excluded']
            account_move[-1]['tax_ids'] = [(6, 0, expense.tax_ids.ids)]
            for tax in taxes['taxes']:
                account_move.append({
                    'type': 'tax',
                    'name': tax['name'],
                    'price_unit': tax['amount'],
                    'quantity': 1,
                    'price': tax['amount'],
                    'account_id': tax['account_id'] or move_line['account_id'],
                    'tax_line_id': tax['id'],
                })
        return account_move

    @api.multi
    def unlink(self):
        for expense in self:
            if expense.state in ['done']:
                raise UserError(_('You cannot delete a posted expense.'))
        super(brt_health_reimburse, self).unlink()

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'brt_health.reimburse'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'brt_health.reimburse', 'default_res_id': self.id}
        return res

    @api.model
    def get_empty_list_help(self, help_message):
        if help_message and help_message.find("oe_view_nocontent_create") == -1:
            alias_record = self.env.ref('hr_expense.mail_alias_expense')
            if alias_record and alias_record.alias_domain and alias_record.alias_name:
                link = "<a id='o_mail_test' href='mailto:%(email)s?subject=Lunch%%20with%%20customer%%3A%%20%%2412.32'>%(email)s</a>" % {
                    'email': '%s@%s' % (alias_record.alias_name, alias_record.alias_domain)
                }
                return '<p class="oe_view_nocontent_create oe_view_nocontent_alias">%s<br/>%s</p>%s' % (
                    _('Click to add a new expense,'),
                    _('or send receipts by email to %s.') % (link,),
                    help_message)
        return super(brt_health_reimburse, self).get_empty_list_help(help_message)

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}

        email_address = email_split(msg_dict.get('email_from', False))[0]

        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)

        expense_description = msg_dict.get('subject', '')

        # Match the first occurence of '[]' in the string and extract the content inside it
        # Example: '[foo] bar (baz)' becomes 'foo'. This is potentially the product code
        # of the product to encode on the expense. If not, take the default product instead
        # which is 'Fixed Cost'
        default_product = self.env.ref('hr_expense.product_product_fixed_cost')
        pattern = '\[([^)]*)\]'
        product_code = re.search(pattern, expense_description)
        if product_code is None:
            product = default_product
        else:
            expense_description = expense_description.replace(product_code.group(), '')
            products = self.env['product.product'].search([('default_code', 'ilike', product_code.group(1))]) or default_product
            product = products.filtered(lambda p: p.default_code == product_code.group(1)) or products[0]
        account = product.product_tmpl_id._get_product_accounts()['expense']

        pattern = '[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
        # Match the last occurence of a float in the string
        # Example: '[foo] 50.3 bar 34.5' becomes '34.5'. This is potentially the price
        # to encode on the expense. If not, take 1.0 instead
        expense_price = re.findall(pattern, expense_description)
        # TODO: International formatting
        if not expense_price:
            price = 1.0
        else:
            price = expense_price[-1][0]
            expense_description = expense_description.replace(price, '')
            try:
                price = float(price)
            except ValueError:
                price = 1.0

        custom_values.update({
            'name': expense_description.strip(),
            'employee_id': employee.id,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'quantity': 1,
            'unit_amount': price,
            'company_id': employee.company_id.id,
        })
        if account:
            custom_values['account_id'] = account.id
        return super(brt_health_reimburse, self).message_new(msg_dict, custom_values)