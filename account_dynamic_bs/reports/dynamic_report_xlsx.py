from odoo import models, fields, api,_

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

class BalanceSheetXlsx(ReportXlsx):

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
            'bg_color': '#FFF58C',
            'border': False
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'bg_color': '#FFFFFF',
            'border': True
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFFF',
            'border': True
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'bg_color': '#FFFFFF',
            'border': False
        })

    def prepare_report_filters(self,filter):
        self.row_pos += 3
        if filter:
            # Date from
            print('iiiiiiiiiiiiiiiiiiiiiiiiiii',filter)
            self.sheet.write_string(self.row_pos, 0, _('Date from'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Date to'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Target moves'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Company'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('Comparison'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Filter By'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6, _('Comp- Date from'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 7, _('Comp- Date to'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 8, _('Show Dr/Cr'),
                                    self.format_header)
            self.row_pos += 1

            if filter.get('date_from'):
                self.sheet.write_string(self.row_pos, 0, str(filter.get('date_from','')),
                                    self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 0, 'None',
                                        self.content_header)
            if filter.get('date_to'):
                self.sheet.write_string(self.row_pos, 1, str(filter.get('date_to','')),
                                    self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 1, 'None',
                                        self.content_header)
            self.sheet.write_string(self.row_pos, 2, str(filter.get('target_move')),
                                    self.content_header)
            company_name = self.env['res.company'].browse(filter['company_ids'][0]).name
            self.sheet.write_string(self.row_pos, 3, str(company_name),
                                    self.content_header)
            if filter.get('enable_filter'):
                self.sheet.write_string(self.row_pos, 4, 'Yes',
                                        self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 4, 'No',
                                        self.content_header)
            if filter.get('filter_cmp') == 'filter_date':
                self.sheet.write_string(self.row_pos, 5, 'Filter By Date',
                                        self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 5, 'No Filter',
                                        self.content_header)
            self.sheet.write_string(self.row_pos, 6, str(filter.get('date_from_cmp')),
                                    self.content_header)
            self.sheet.write_string(self.row_pos, 7, str(filter.get('date_to_cmp')),
                                    self.content_header)
            if filter.get('debit_credit'):
                self.sheet.write_string(self.row_pos, 8, 'Yes',
                                        self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 8, 'No',
                                        self.content_header)

    def prepare_report_contents(self, Accounts, Filters):
        self.row_pos += 3
        if Accounts:
            if Filters['debit_credit']:
                self.sheet.write_string(self.row_pos, 0, _('Name'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 1, _('Debit'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 2, _('Credit'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 3, _('Balance'),
                                        self.format_header)
                for account in Accounts:
                    if account['level'] > 0:
                        self.row_pos += 1
                        name = ''
                        for i in account['list_len']:
                            name += ' '
                        if account['level'] < 3:
                            line_style = self.line_header
                        else:
                            line_style = self.line_header_light
                        self.sheet.write_string(self.row_pos, 0, name + str(account.get('name')) or '',
                                                line_style)
                        self.sheet.write_string(self.row_pos, 1,
                                                self._format_currency(account['debit'], account['precision']),
                                                line_style)
                        self.sheet.write_string(self.row_pos, 2,
                                                self._format_currency(account['credit'], account['precision']),
                                                line_style)
                        self.sheet.write_string(self.row_pos, 3,
                                                self._format_currency(account['balance'], account['precision']),
                                                line_style)

            if not Filters['debit_credit'] and not Filters['enable_filter']:
                self.sheet.write_string(self.row_pos, 0, _('Name'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 1, _('Balance'),
                                        self.format_header)
                for account in Accounts:
                    if account['level'] > 0:
                        self.row_pos += 1
                        name = ''
                        for i in account['list_len']:
                            name += ' '
                        if account['level'] < 3:
                            line_style = self.line_header
                        else:
                            line_style = self.line_header_light
                        self.sheet.write_string(self.row_pos, 0, name + str(account.get('name')) or '',
                                                line_style)
                        self.sheet.write_string(self.row_pos, 1,
                                                self._format_currency(account['balance'], account['precision']),
                                                line_style)
            if not Filters['debit_credit'] and Filters['enable_filter']:

                self.sheet.write_string(self.row_pos, 0, _('Name'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 1, _('Balance'),
                                        self.format_header)
                self.sheet.write_string(self.row_pos, 2, _('Balance Comparison'),
                                        self.format_header)
                for account in Accounts:
                    if account['level'] > 0:
                        self.row_pos += 1
                        name = ''
                        for i in account['list_len']:
                            name += ' '
                        if account['level'] < 3:
                            line_style = self.line_header
                        else:
                            line_style = self.line_header_light
                        self.sheet.write_string(self.row_pos, 0, name + str(account.get('name')) or '',
                                                line_style)
                        self.sheet.write_string(self.row_pos, 1, self._format_currency(account['balance'],account['precision']),
                                                line_style)
                        self.sheet.write_string(self.row_pos, 2, self._format_currency(account['balance_cmp'],account['precision']),
                                                line_style)

    def _format_currency(self, amount, precision):
        format_amount = b = '{:.' + str(precision) + 'f}'
        return format_amount.format(amount)

    def generate_xlsx_report(self, workbook, data, ids):
        data = self.env.context.get('data')
        self._define_formats(workbook)
        self.row_pos = 0
        self.sheet = workbook.add_worksheet('Balance Sheet')
        self.sheet.merge_range(0, 0, 0, 8, 'Balance Sheet', self.format_title)
        if data:
            # Filter section
            self.prepare_report_filters(data['data'])
            # Content section
            self.prepare_report_contents(data['lines'],data['data'])

BalanceSheetXlsx('report.account_dynamic_bs.balance_sheet_xlsx',
            'account.financial.report')
