# -*- coding: utf-8 -*-

import base64
from datetime import datetime

from odoo import api, fields, models, _
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
DEFAULT_SERVER_DATETIME_FORMAT as DSDTF

import xlwt
from cStringIO import StringIO


LEAVE_STATE = {
        'draft':'New', 
        'confirm':'Waiting Pre-Approval',
        'refuse':'Refused',
        'validate1':'Waiting Final Approval',
        'validate':'Approved',
        'cancel':'Cancelled'
        }
LEAVE_REQUEST = {
        'remove': 'Leave Request',
        'add':'Allocation Request'
        }
PAYSLIP_STATE ={
        'draft':'Draft',
        'verify':'Waiting',
        'done':'Done',
        'cancel':'Rejected'
        }


class ExportEmployeeDataRecordXls(models.TransientModel):
    _name = 'export.employee.data.record.xls'

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name", readonly=True, invisible=True,
                       default='Employee Summary.xls')


class ExportEmployeeSummaryWiz(models.TransientModel):
    _name = 'export.employee.summary.wiz'
    
    @api.onchange('employee_information')
    def onchange_employee_information(self):
        if self.employee_information:
            self.user_id = self.active = self.department = \
            self.direct_manager = self.indirect_manager = True
        else:
            if not self.user_id:
                self.user_id = False
            if not self.active:
                self.active = False
            if not self.department:
                self.department = False
            if not self.direct_manager:
                self.direct_manager = False
            if not self.indirect_manager:
                self.indirect_manager = False
            if self.user_id and self.active and self.department and \
            self.direct_manager and self.indirect_manager:
                self.user_id = self.active = self.department = \
                self.indirect_manager = self.direct_manager = False

    @api.onchange('user_id', 'active', 'department', 'direct_manager',
                  'indirect_manager')
    def check_all_empl_select(self):
        # check if one of these fields will be false then select all field will
        # will b false
        if ((not self.user_id) or (not self.active) or (not self.department) \
        or (not self.direct_manager) or (not self.indirect_manager)) and \
        self.employee_information:
            self.employee_information = False
        # If all fields are true select all field also become true
        if self.user_id and self.active and self.department and \
        self.direct_manager and self.indirect_manager:
            self.employee_information = True

    @api.onchange('job_information')
    def onchange_job_information(self):
        if self.job_information:
            self.job_title = self.emp_status = self.join_date = \
            self.confirm_date = self.date_changed = self.changed_by = \
            self.date_confirm_month = True
        else:
            if not self.job_title:
                self.job_title = False
            if not self.emp_status:
                self.emp_status = False
            if not self.join_date:
                self.join_date = False
            if not self.confirm_date:
                self.confirm_date = False
            if not self.date_changed:
                self.date_changed = False
            if not self.changed_by:
                self.changed_by = False
            if not self.date_confirm_month:
                self.date_confirm_month = False
            if self.job_title and self.emp_status and self.join_date and \
            self.confirm_date and self.date_changed and self.changed_by and \
            self.date_confirm_month:
                self.job_title = self.emp_status = self.join_date = \
                self.confirm_date = self.date_changed = self.changed_by = \
                self.date_confirm_month = False

    @api.onchange('job_title', 'emp_status', 'join_date', 'confirm_date',
                  'date_changed', 'changed_by', 'date_confirm_month')
    def check_all_job_info_select(self):
        # check if one of these fields will be false then select all field will
        # will b false
        if ((not self.job_title) or (not self.emp_status) or \
        (not self.join_date) or (not self.confirm_date) or \
        (not self.date_changed) or (not self.changed_by) or \
        (not self.date_confirm_month)) and self.job_information:
            self.job_information = False
        # If all fields are true select all field also become true
        if self.job_title and self.emp_status and self.join_date and \
        self.confirm_date and self.date_changed and self.changed_by and \
        self.date_confirm_month:
            self.job_information = True

    @api.onchange('emp_health_information')
    def onchange_emp_health_information(self):
        if self.emp_health_information:
            self.health_condition = self.bankrupt = self.suspend_employment = \
            self.court_law = self.about = True
        else:
            if not self.health_condition:
                self.health_condition = False
            if not self.bankrupt:
                self.bankrupt = False
            if not self.suspend_employment:
                self.suspend_employment = False
            if not self.court_law:
                self.court_law = False
            if not self.about:
                self.about = False

            if self.health_condition and self.bankrupt and \
            self.suspend_employment and self.court_law and self.about :
                self.health_condition = self.bankrupt = self.suspend_employment = \
                self.court_law = self.about = False

    @api.onchange('health_condition', 'bankrupt', 'suspend_employment',
                  'court_law', 'about')
    def check_all_health_info_select(self):
        # check if one of these fields will be false then select all field will
        # will b false
        if ((not self.health_condition) or (not self.bankrupt) or \
        (not self.suspend_employment) or (not self.court_law) or \
        (not self.about)) and self.emp_health_information:
            self.emp_health_information = False
        # If all fields are true select all field also become true
        if self.health_condition and self.bankrupt and self.suspend_employment \
        and self.court_law and self.about:
            self.emp_health_information = True

    @api.onchange('emp_payroll_detail')
    def onchange_emp_payroll_detail(self):
        if self.emp_payroll_detail:
            self.payslip = self.contract = True
        else:
            if not self.payslip:
                self.payslip = False
            if not self.contract:
                self.contract = False
            if self.payslip and self.contract:
                self.contract = self.payslip = False

    @api.onchange('payslip', 'contract')
    def check_payslip_select(self):
        # check if one of these fields will be false then select all field will
        # will b false
        if ((not self.payslip) or (not self.contract)) and \
        self.emp_payroll_detail:
            self.emp_payroll_detail = False
        # If all fields are true select all field also become true
        if self.payslip and self.contract:
            self.emp_payroll_detail = True

    @api.onchange('personal_information')
    def onchange_personal_information(self):
        if self.personal_information:
            self.identification_id = self.passport_id = self.gender = \
            self.martial = self.nationality = self.dob = self.pob = self.age = \
            self.home_address = self.country_id = self.state_id = \
            self.city_id = self.phone = self.mobile = self.email = \
            self.dialet = self.driving_licence = self.own_car = \
            self.emp_type_id = True
        else:
            if not self.identification_id:
                self.identification_id = False
            if not self.passport_id:
                self.passport_id = False
            if not self.gender:
                self.gender = False
            if not self.martial:
                self.martial = False
            if not self.nationality:
                self.nationality = False
            if not self.dob:
                self.dob = False
            if not self.pob:
                self.pob = False
            if not self.age:
                self.age = False
            if not self.home_address:
                self.home_address = False
            if not self.country_id:
                self.country_id = False
            if not self.state_id:
                self.state_id = False
            if not self.city_id:
                self.city_id = False
            if not self.phone:
                self.phone = False
            if not self.mobile:
                self.mobile = False
            if not self.email:
                self.email = False
            if not self.dialet:
                self.dialet = False
            if not self.driving_licence:
                self.driving_licence = False
            if not self.own_car:
                self.own_car = False
            if not self.emp_type_id:
                self.emp_type_id = False
            if self.emp_type_id and self.own_car and self.driving_licence and \
            self.dialet and self.email and self.mobile and self.phone and \
            self.city_id and self.state_id and self.country_id and \
            self.home_address and self.age and self.pob and self.dob and \
            self.nationality and self.martial and self.gender and \
            self.passport_id and self.identification_id:
                self.identification_id = self.passport_id = self.gender = \
                self.martial = self.nationality = self.dob = self.pob = \
                self.age = self.home_address = self.country_id = \
                self.state_id = self.city_id = self.phone = self.mobile = \
                self.email = self.dialet = self.driving_licence = \
                self.own_car = self.emp_type_id = False

    @api.onchange('emp_type_id', 'own_car', 'driving_licence', 'dialet',
                  'email', 'mobile', 'phone', 'city_id', 'state_id',
                  'country_id', 'home_address', 'age', 'pob', 'dob',
                  'nationality', 'martial', 'gender', 'passport_id',
                  'identification_id')
    def check_personal_details_select(self):
        # check if one of these fields will be false then select all field will
        # will b false
        if ((not self.emp_type_id) or (not self.own_car) or \
            (not self.driving_licence) or \
            (not self.dialet) or (not self.email) or \
            (not self.mobile) or (not self.phone) or (not self.city_id) or \
            (not self.state_id) or (not self.country_id) or \
            (not self.home_address) or (not self.age) or (not self.pob) or \
            (not self.dob) or (not self.nationality) or (not self.martial) or \
            (not self.gender) or (not self.passport_id) or \
            (not self.identification_id)) and self.personal_information:
            self.personal_information = False
        # If all fields are true select all field also become true
        if self.emp_type_id and self.own_car and self.driving_licence and \
        self.dialet and self.email and self.mobile and self.phone and \
        self.city_id and self.state_id and self.country_id and \
        self.home_address and self.age and self.pob and self.dob and \
        self.nationality and self.martial and self.gender and \
        self.passport_id and self.identification_id:
            self.personal_information = True

    employee_ids = fields.Many2many('hr.employee', 'ihrms_hr_employee_export_summary_rel','emp_id','employee_id','Employee Name', required=True)
    user_id = fields.Boolean('User')
    active = fields.Boolean('Active')
    department = fields.Boolean('Department')
    direct_manager = fields.Boolean('Direct Manager')
    indirect_manager = fields.Boolean('Indirect Manager')
    personal_information = fields.Boolean('Select All')
    employee_information = fields.Boolean("Select All")
    job_information = fields.Boolean("Select All")
    emp_health_information = fields.Boolean("Select All")
    emp_payroll_detail = fields.Boolean("Select All")
    identification_id = fields.Boolean('Identification')
    passport_id = fields.Boolean('Passport')
    gender = fields.Boolean('Gender')
    martial = fields.Boolean('Martial Status')
    nationality = fields.Boolean('Nationality')
    dob = fields.Boolean('Date Of Birth')
    pob = fields.Boolean('Place Of Birth')
    age = fields.Boolean('Age')
    home_address = fields.Boolean('Home Address')
    country_id = fields.Boolean('Country')
    state_id = fields.Boolean('State')
    city_id = fields.Boolean('City')
    phone = fields.Boolean('Phone')
    mobile = fields.Boolean('Mobile')
    email = fields.Boolean('Email')
    dialet = fields.Boolean('Dialet')
    driving_licence = fields.Boolean('Driving Licence Class')
    own_car = fields.Boolean('Do Your Own Car')
    emp_type_id = fields.Boolean('Type Of ID')
    evaluation_date = fields.Boolean('Next Appraisal Date')
    edu_ids = fields.Boolean('Education')
    job_title = fields.Boolean('Job Title')
    emp_status = fields.Boolean('Employment Status')
    join_date = fields.Boolean('Joined Date')
    confirm_date = fields.Boolean('Confirmation Date')
    date_changed = fields.Boolean('Date Changed')
    changed_by = fields.Boolean('Changed By')
    date_confirm_month = fields.Boolean('Date Confirm Month')
    category_ids = fields.Boolean('Categories')
    immigration_ids = fields.Boolean('Immigration')
    tarining_ids = fields.Boolean('Training Workshop')
    emp_leave_ids = fields.Boolean('Leave History')
    health_condition = fields.Boolean('Are you suffering from any physical disability or illness that requires you to be medication for a prolonged period?')
    court_law = fields.Boolean('Have you ever been convicted in a court of law in any country?')
    suspend_employment = fields.Boolean('Have you ever been dismissed or suspended from employement?')
    bankrupt = fields.Boolean('Have you ever been declared a bankrupt?')
    about = fields.Boolean('About Yourself')
    bank_detail_ids = fields.Boolean('Bank Details')
    notes = fields.Boolean('Notes')
    payslip = fields.Boolean('Payslips')
    contract = fields.Boolean('Contract')

    @api.multi
    def export_employee_summary_xls(self):
        context = dict(self._context)
        if context is None:
            context = {}
        data = self.read()[0]
        context.update({'datas': data})
        # Create xls file and write selected employee record.
        workbook = xlwt.Workbook()
        font = xlwt.Font()
        font.bold = True
        user_lang = self.env['res.users'].browse(self._uid).lang
        lang_ids = self.env['res.lang'].search([('code', '=', user_lang)])
        date_format = "%d/%m/%Y"
        month_year_format = "%m/%Y"
        if lang_ids:
            date_format = lang_ids[0].date_format
        header = xlwt.easyxf('font: name Arial, bold on, height 200; align: wrap off;')
        style = xlwt.easyxf('align: wrap off')
        number_format = xlwt.easyxf('align: wrap off')
        number_format.num_format_str = '#,##0.00'
        personal_information = False
        emp_payslip_row = emp_contract_row = emp_note_row = emp_edu_info_row = emp_extra_info_row = emp_info_row = emp_per_info_row = \
                            emp_bank_row = emp_leave_row = emp_training_row = emp_job_row = emp_immigration_row = emp_categories_row = 0
        emp_info_col = emp_per_info_col = emp_extra_info_col = 0

        if context and context.get('datas') and context.get('datas')['employee_ids']:
            emp_info_ws = workbook.add_sheet('Employee Information')
            emp_info_ws.col(emp_info_col).width = 6000
            emp_info_ws.write(emp_info_row, emp_info_col, 'Employee Name', header)
            if context.get('datas')['user_id'] or context.get('datas')['active'] or context.get('datas')['department'] or \
                 context.get('datas')['direct_manager'] or context.get('datas')['indirect_manager']:

                if context.get('datas')['user_id']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'User', header)
                if context.get('datas')['active']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Active', header)
                if context.get('datas')['department']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Department', header)
                if context.get('datas')['direct_manager']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Direct Manager', header)
                if context.get('datas')['indirect_manager']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Indirect Manager', header)
            #Employee Personal Information
            if context.get('datas').get('identification_id') or context.get('datas').get('passport_id') \
                or context.get('datas').get('gender') or context.get('datas').get('martial') or context.get('datas').get('nationality') \
                or context.get('datas').get('dob') or context.get('datas').get('pob') or context.get('datas').get('age') \
                or context.get('datas').get('home_address') or context.get('datas').get('country_id') or context.get('datas').get('state_id') \
                or context.get('datas').get('city_id') or context.get('datas').get('phone') or context.get('datas').get('mobile') \
                or context.get('datas').get('email') or  context.get('datas').get('dialet') \
                or context.get('datas').get('driving_licence') or context.get('datas').get('own_car') \
                or context.get('datas').get('emp_type_id'):
                personal_information = True
            if personal_information:
                emp_personal_info_ws = workbook.add_sheet('Personal Information')
                emp_per_info_col = 0
                emp_personal_info_ws.col(emp_per_info_col).width = 6000
                emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Employee Name : ', header)
                if context.get('datas')['identification_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Identification', header)
                if context.get('datas')['passport_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Passport No', header)

                if context.get('datas')['gender']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Gender', header)
                if context.get('datas')['martial']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Marital Status', header)
                if context.get('datas')['nationality']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Nationality', header)
                if context.get('datas')['dob']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Birthdate', header)
                if context.get('datas')['pob']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Place Of Birth', header)
                if context.get('datas')['age']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Age', header)
                
                if context.get('datas')['home_address']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Home Address', header)
                if context.get('datas')['country_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Country', header)
                if context.get('datas')['state_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'State', header)
                if context.get('datas')['city_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'City', header)
                if context.get('datas')['phone']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Phone', header)
                if context.get('datas')['mobile']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Mobile', header)
                if context.get('datas')['email']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Email', header)
                
                if context.get('datas')['dialet']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Dialet', header)
                if context.get('datas')['driving_licence']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Driving Licence', header)
                if context.get('datas')['own_car']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Car', header)
                if context.get('datas')['emp_type_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Type Of ID', header)
            
            #Extra Information
            if context.get('datas')['health_condition'] or context.get('datas')['bankrupt'] or context.get('datas')['suspend_employment'] or context.get('datas')['court_law'] or context.get('datas')['about']:
                emp_extra_info_ws = workbook.add_sheet('Extra Information')
                emp_extra_info_ws.col(emp_extra_info_col).width = 6000
                emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Employee Name', header)
                if context.get('datas')['health_condition']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Are you suffering from any physical disability or illness that requires you to be medication for a prolonged period? ', header)
                if context.get('datas')['bankrupt']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been declared a bankrupt?', header)
                if context.get('datas')['suspend_employment']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been dismissed or suspended from employement? ', header)
                if context.get('datas')['court_law']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been convicted in a court of law in any country? ', header)
                if context.get('datas')['about']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'About Yourself', header)
            #Educational Information
            if context.get('datas')['edu_ids'] :
                emp_edu_info_ws = workbook.add_sheet('Educational Information')
                emp_edu_info_ws.col(0).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 0, 'Employee Name', header)
                emp_edu_info_ws.col(1).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 1, 'Computer Program Knowledge', header)
                emp_edu_info_ws.col(2).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 2, 'Shorthand', header)
                emp_edu_info_ws.col(3).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 3, 'Courses', header)
                emp_edu_info_ws.col(4).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 4, 'Typing', header)
                emp_edu_info_ws.col(4).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 5, 'Other Knowledge & Skills', header)
                
#            
            if context.get('datas')['job_title'] or context.get('datas')['emp_status'] \
                or context.get('datas')['join_date'] \
                or context.get('datas')['confirm_date'] \
                or context.get('datas')['date_changed'] \
                or context.get('datas')['changed_by'] \
                or context.get('datas')['date_confirm_month']:
                
                emp_job_ws = workbook.add_sheet('Job')
                emp_job_col = 0
                emp_job_ws.col(emp_job_col).width = 6000
                emp_job_ws.write(emp_job_row, emp_job_col, 'Employee Name', header)
                if context.get('datas')['job_title']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Job Title', header)
                if context.get('datas')['emp_status']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Employment Status', header)
                if context.get('datas')['join_date']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Join Date', header)
                if context.get('datas')['confirm_date']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Confirmation', header)
                if context.get('datas')['date_changed']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Changed', header)
                if context.get('datas')['changed_by']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Changed By', header)
                if context.get('datas')['date_confirm_month']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Confirmation Month', header)
            
            if context.get('datas')['category_ids']:
                emp_categories_ws = workbook.add_sheet('Categories')
                emp_categories_ws.col(0).width = 6000
                emp_categories_ws.col(1).width = 6000
                emp_categories_ws.col(2).width = 6000
                emp_categories_ws.write(emp_categories_row, 0, 'Employee Name', header)
                emp_categories_ws.write(emp_categories_row, 1, 'Category', header)
                emp_categories_ws.write(emp_categories_row, 2, 'Parent Category', header)
            
            #Immigration
            if context.get('datas')['immigration_ids']:
                emp_immigration_ws = workbook.add_sheet('Immigration')
                emp_immigration_ws.col(0).width = 6000
                emp_immigration_ws.col(1).width = 6000
                emp_immigration_ws.col(2).width = 6000
                emp_immigration_ws.col(3).width = 6000
                emp_immigration_ws.col(4).width = 6000
                emp_immigration_ws.col(5).width = 6000
                emp_immigration_ws.col(6).width = 6000
                emp_immigration_ws.col(7).width = 6000
                emp_immigration_ws.col(8).width = 6000
                emp_immigration_ws.write(emp_immigration_row, 0, 'Employee Name', header)
                emp_immigration_ws.write(emp_immigration_row, 1, 'Document', header)
                emp_immigration_ws.write(emp_immigration_row, 2, 'Number', header)
                emp_immigration_ws.write(emp_immigration_row, 3, 'Issue Date', header)
                emp_immigration_ws.write(emp_immigration_row, 4, 'Expiry Date', header)
                emp_immigration_ws.write(emp_immigration_row, 5, 'Eligible Status', header)
                emp_immigration_ws.write(emp_immigration_row, 6, 'Eligible Review Date', header)
                emp_immigration_ws.write(emp_immigration_row, 7, 'Issue By', header)
                emp_immigration_ws.write(emp_immigration_row, 8, 'Comment', header)
            
            #Trainig Workshop
            if context.get('datas')['tarining_ids']:
                emp_training_ws = workbook.add_sheet('Training Workshop')
                emp_training_ws.col(0).width = 6000
                emp_training_ws.col(1).width = 6000
                emp_training_ws.col(2).width = 6000
                emp_training_ws.col(3).width = 6000
                emp_training_ws.col(4).width = 15000
                emp_training_ws.write(emp_training_row, 0, 'Employee Name', header)
                emp_training_ws.write(emp_training_row, 1, 'Training Workshop', header)
                emp_training_ws.write(emp_training_row, 2, 'Institution', header)
                emp_training_ws.write(emp_training_row, 3, 'Date', header)
                emp_training_ws.write(emp_training_row, 4, 'Comment', header)
            
            #Leave History
            if context.get('datas')['emp_leave_ids']:
                emp_leave_ws = workbook.add_sheet('Leave History')
                emp_leave_ws.col(0).width = 6000
                emp_leave_ws.col(1).width = 9000
                emp_leave_ws.col(2).width = 3000
                emp_leave_ws.col(3).width = 6000
                emp_leave_ws.col(4).width = 6000
                emp_leave_ws.col(5).width = 6000
                emp_leave_ws.col(6).width = 6000
                emp_leave_ws.write(emp_leave_row, 0, 'Employee Name', header)
                emp_leave_ws.write(emp_leave_row, 1, 'Description', header)
                emp_leave_ws.write(emp_leave_row, 2, 'Start Date', header)
                emp_leave_ws.write(emp_leave_row, 3, 'End Date', header)
                emp_leave_ws.write(emp_leave_row, 4, 'Request Type', header)
                emp_leave_ws.write(emp_leave_row, 5, 'Leave Type', header)
                emp_leave_ws.write(emp_leave_row, 6, 'Number Of Days', header)
                emp_leave_ws.write(emp_leave_row, 7, 'State', header)
                emp_leave_ws.write(emp_leave_row, 8, 'Reason', header)
            #Bank Details
            if context.get('datas')['bank_detail_ids']:
                emp_bank_ws = workbook.add_sheet('Bank Details')
                emp_bank_ws.col(0).width = 6000
                emp_bank_ws.col(1).width = 6000
                emp_bank_ws.col(2).width = 6000
                emp_bank_ws.col(3).width = 6000
                emp_bank_ws.col(4).width = 6000
                emp_bank_ws.write(emp_bank_row, 0, 'Employee Name', header)
                emp_bank_ws.write(emp_bank_row, 1, 'Name Of Bank', header)
                emp_bank_ws.write(emp_bank_row, 2, 'Bank Code', header)
                emp_bank_ws.write(emp_bank_row, 3, 'Branch Code', header)
                emp_bank_ws.write(emp_bank_row, 4, 'Bank Account Number', header)
            
            #Notes
            if context.get('datas')['notes']:
                emp_note_ws = workbook.add_sheet('Notes')
                emp_note_ws.col(0).width = 6000
                emp_note_ws.col(1).width = 15000
                emp_note_ws.write(emp_note_row, 0, 'Employee Name', header)
                emp_note_ws.write(emp_note_row, 1, 'Note', header)
            #Payslip
            if context.get('datas')['payslip']:
                emp_payslip_ws = workbook.add_sheet('Payroll - Payslips')
                emp_payslip_ws.col(0).width = 6000
                emp_payslip_ws.col(2).width = 16000
                emp_payslip_ws.write(emp_payslip_row, 0, 'Employee Name', header)
                emp_payslip_ws.write(emp_payslip_row, 1, 'Reference', header)
                emp_payslip_ws.write(emp_payslip_row, 2, 'Description', header)
                emp_payslip_ws.write(emp_payslip_row, 3, 'Date from', header)
                emp_payslip_ws.write(emp_payslip_row, 4, 'Date to', header)
                emp_payslip_ws.write(emp_payslip_row, 5, 'Amount', header)
                emp_payslip_ws.write(emp_payslip_row, 6, 'State', header)

            #Contract
            if context.get('datas')['contract']:
                emp_contract_ws = workbook.add_sheet('Contract')
                emp_contract_ws.col(0).width = 6000
                emp_contract_ws.col(1).width = 6000
                emp_contract_ws.col(5).width = 6000
                emp_contract_ws.write(emp_contract_row, 0, 'Employee Name', header)
                emp_contract_ws.write(emp_contract_row, 1, 'Reference', header)
                emp_contract_ws.write(emp_contract_row, 2, 'Wage', header)
                emp_contract_ws.write(emp_contract_row, 3, 'Start date', header)
                emp_contract_ws.write(emp_contract_row, 4, 'End date', header)
                emp_contract_ws.write(emp_contract_row, 5, 'Salary structure', header)

            for emp in self.env['hr.employee'].browse(context.get('datas')['employee_ids']):
                emp_info_row += 1
                emp_info_col = emp_per_info_col = 0
                emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.name or ''), style)
                if context.get('datas')['user_id'] or context.get('datas')['active'] or context.get('datas')['department'] \
                        or context.get('datas')['direct_manager'] or context.get('datas')['indirect_manager']:
                    emp_info_col = emp_per_info_col = 0
                    if context.get('datas')['user_id']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.user_id.name or ''), style)
                    if context.get('datas')['active']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.active or ''), style)
                    if context.get('datas')['department']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.department_id.name or ''), style)
                    if context.get('datas')['direct_manager']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.parent_id.name or ''), style)
                    if context.get('datas')['indirect_manager']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.parent_id2.name or ''), style)
                #Employee Personal Information
                if personal_information:
                    emp_per_info_row += 1
                    emp_per_info_col = 0
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['identification_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.identification_id or ''), style)
                    if context.get('datas')['passport_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.passport_id or ''), style)
                    if context.get('datas')['gender']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.gender or ''), style)
                    if context.get('datas')['martial']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.marital or ''), style)
                    if context.get('datas')['nationality']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_country_id or ''), style)
                    if context.get('datas')['dob']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.birthday or ''), style)
                    if context.get('datas')['pob']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.place_of_birth or ''), style)
                    if context.get('datas')['age']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.age or ''), style)
                    
                    if context.get('datas')['home_address']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.address_home_id.name or ''), style)
                    if context.get('datas')['country_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.country_id.name or ''), style)
                    if context.get('datas')['state_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_state_id.name or ''), style)
                    if context.get('datas')['city_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_city_id.name or ''), style)
                    if context.get('datas')['phone']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.work_phone or ''), style)
                    if context.get('datas')['mobile']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.mobile_phone or ''), style)
                    if context.get('datas')['email']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.work_email or ''), style)
                    
                    if context.get('datas')['dialet']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.dialect or ''), style)
                    if context.get('datas')['driving_licence']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.driving_licence or ''), style)
                    if context.get('datas')['own_car']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.car or ''), style)
                    if context.get('datas')['emp_type_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.employee_type_id.name or ''), style)
                
                #Extra Information
                if context.get('datas')['health_condition'] or context.get('datas')['bankrupt'] or context.get('datas')['suspend_employment'] or context.get('datas')['court_law'] or context.get('datas')['about']:
                    emp_extra_info_col = 0
                    emp_extra_info_row += 1
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['health_condition']:
                        emp_extra_info_col += 1
                        helath_condition = ''
                        if emp.physical_stability:
                            helath_condition = 'Yes'
                        if emp.physical_stability_no:
                            helath_condition = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(helath_condition or ''), style)
                    if context.get('datas')['bankrupt']:
                        emp_extra_info_col += 1
                        bankrupt = ''
                        if emp.bankrupt_b:
                            bankrupt = 'Yes'
                        if emp.bankrupt_no:
                            bankrupt = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(bankrupt or ''), style)
                    if context.get('datas')['suspend_employment']:
                        emp_extra_info_col += 1
                        supspend = ''
                        if emp.dismissed_b:
                            supspend = 'Yes'
                        if emp.dismissed_no:
                            supspend = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(supspend or ''), style)
                    if context.get('datas')['court_law']:
                        emp_extra_info_col += 1
                        court = ''
                        if emp.court_b:
                            court = "Yes"
                        if emp.court_no:
                            court = "No"
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(court or ''), style)
                    if context.get('datas')['about']:
                        emp_extra_info_col += 1
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(emp.about or ''), style)

                #Educational Information
                if context.get('datas')['edu_ids']:
                    for edu in emp:
                        emp_edu_info_row += 1
                        emp_edu_info_ws.write(emp_edu_info_row, 0, tools.ustr(emp.name or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 1, tools.ustr(emp.comp_prog_knw or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 2, tools.ustr(emp.shorthand or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 3, tools.ustr(emp.course or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 4, tools.ustr(emp.typing or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 5, tools.ustr(emp.other_know or ''), style)

                #Job
                if context.get('datas')['job_title'] or context.get('datas')['emp_status'] \
                    or context.get('datas')['join_date'] \
                    or context.get('datas')['confirm_date'] \
                    or context.get('datas')['date_changed'] \
                    or context.get('datas')['changed_by'] \
                    or context.get('datas')['date_confirm_month']:
                    for job in emp.history_ids:
                        emp_job_col = 0
                        emp_job_row += 1
                        emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(emp.name or ''), style)
                        if context.get('datas')['job_title']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.job_id.name or ''), style)
                        if context.get('datas')['emp_status']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.emp_status or ''), style)
                        if context.get('datas')['join_date']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.join_date and datetime.strptime(job.join_date, DSDF).strftime(date_format) or '', style)
                        if context.get('datas')['confirm_date']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.confirm_date and datetime.strptime(job.confirm_date, DSDF).strftime(date_format) or '', style)
                        if context.get('datas')['date_changed']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.date_changed and datetime.strptime(job.date_changed, DSDTF).strftime(date_format) or '', style)
                        if context.get('datas')['changed_by']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.user_id.name or ''), style)
                        if context.get('datas')['date_confirm_month']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.confirm_date and datetime.strptime(job.confirm_date, DSDF).strftime(month_year_format) or '', style)

                #Categories
                if context.get('datas')['category_ids']:
                    for category in emp.category_ids:
                        emp_categories_row += 1
                        emp_categories_ws.write(emp_categories_row, 0, tools.ustr(emp.name or ''), style)
                        emp_categories_ws.write(emp_categories_row, 1, tools.ustr(category.name or ''), style)
                        emp_categories_ws.write(emp_categories_row, 2, tools.ustr((category.name) or ''), style)

                #Immigration
                if context.get('datas')['immigration_ids']:
                    for immigration in emp.immigration_ids:
                        emp_immigration_row += 1
                        emp_immigration_ws.write(emp_immigration_row, 0, tools.ustr(emp.name or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 1, tools.ustr(immigration.documents or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 2, tools.ustr(immigration.number or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 3, immigration.issue_date and datetime.strptime(immigration.issue_date, DSDF).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 4, immigration.exp_date and datetime.strptime(immigration.exp_date, DSDF).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 5, tools.ustr(immigration.eligible_status or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 6, immigration.eligible_review_date and datetime.strptime(immigration.eligible_review_date, DSDF).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 7, tools.ustr(immigration.issue_by.name or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 8, tools.ustr(immigration.comments or ''), style)

                #Trainig Workshop
                if context.get('datas')['tarining_ids']:
                    for training in emp.training_ids:
                        emp_training_row += 1
                        emp_training_ws.write(emp_training_row, 0, tools.ustr(emp.name or ''), style)
                        emp_training_ws.write(emp_training_row, 1, tools.ustr(training.tr_title or ''), style)
                        emp_training_ws.write(emp_training_row, 2, tools.ustr(training.tr_institution or ''), style)
                        emp_training_ws.write(emp_training_row, 3, training.tr_date and datetime.strptime(training.tr_date, DSDF).strftime(date_format) or '', style)
                        emp_training_ws.write(emp_training_row, 4, tools.ustr(training.comments or ''), style)

                #Leave History
                if context.get('datas')['emp_leave_ids']:
                    for leave in emp.employee_leave_ids:
                        emp_leave_row += 1
                        emp_leave_ws.write(emp_leave_row, 0, tools.ustr(emp.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 1, tools.ustr(leave.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 2, leave.date_from and datetime.strptime(leave.date_from.split(' ')[0], DSDF).strftime(date_format) or '', style)
                        emp_leave_ws.write(emp_leave_row, 3, leave.date_to and datetime.strptime(leave.date_to.split(' ')[0], DSDF).strftime(date_format) or '', style)
                        emp_leave_ws.write(emp_leave_row, 4, tools.ustr(LEAVE_REQUEST.get(leave.type, '')), style)
                        emp_leave_ws.write(emp_leave_row, 5, tools.ustr(leave.holiday_status_id.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 6, tools.ustr(leave.number_of_days_temp or ''), style)
                        emp_leave_ws.write(emp_leave_row, 7, tools.ustr(LEAVE_STATE.get(leave.state, '')), style)
                        emp_leave_ws.write(emp_leave_row, 8, tools.ustr(leave.notes or ''), style)
                #Bank Details
                if context.get('datas')['bank_detail_ids']:
                    emp_bank_row += 1
                    bank_rec = emp.bank_account_id or False
                    emp_bank_ws.write(emp_bank_row, 0, tools.ustr(emp.name or ''), style)
                    emp_bank_ws.write(emp_bank_row, 1, tools.ustr(bank_rec and bank_rec.bank_id and bank_rec.bank_id.name or ''), style)
                    emp_bank_ws.write(emp_bank_row, 2, tools.ustr(bank_rec and bank_rec.bank_id and bank_rec.bank_id.bic or ''), style)
                    emp_bank_ws.write(emp_bank_row, 3, tools.ustr(bank_rec and bank_rec.branch_id or ''), style)
                    emp_bank_ws.write(emp_bank_row, 4, tools.ustr(bank_rec and bank_rec.acc_number or ''), style)
                
                #Notes
                if context.get('datas')['notes']:
                    emp_note_row += 1
                    emp_note_ws.write(emp_note_row, 0, tools.ustr(emp.name or ''), style)
                    emp_note_ws.write(emp_note_row, 1, tools.ustr(emp.notes or ''), style)

                #Payslip
                if context.get('datas')['payslip']:
                    payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', emp.id)])
                    for payslip in payslip_ids:
                        net_amount = 0.0
                        for line in payslip.line_ids:
                            if line.code == "NET":
                                net_amount = line.amount
                        emp_payslip_row += 1
                        emp_payslip_ws.write(emp_payslip_row, 0, tools.ustr(emp.name or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 1, tools.ustr(payslip.number or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 2, tools.ustr(payslip.name or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 3, payslip.date_from and datetime.strptime(payslip.date_from, DSDF).strftime(date_format) or '', style)
                        emp_payslip_ws.write(emp_payslip_row, 4, payslip.date_to and datetime.strptime(payslip.date_to, DSDF).strftime(date_format) or '', style)
                        emp_payslip_ws.write(emp_payslip_row, 5, net_amount, number_format)
                        emp_payslip_ws.write(emp_payslip_row, 6, tools.ustr(PAYSLIP_STATE.get(payslip.state, '')), style)

                if context.get('datas')['contract']:
                    contract_ids = self.env['hr.contract'].search([('employee_id', '=', emp.id)])
                    for contract in contract_ids:
                        emp_contract_row += 1
                        emp_contract_ws.write(emp_contract_row, 0, tools.ustr(emp.name or ''), style)
                        emp_contract_ws.write(emp_contract_row, 1, tools.ustr(contract.name or ''), style)
                        emp_contract_ws.write(emp_contract_row, 2, contract.wage, number_format)
                        emp_contract_ws.write(emp_contract_row, 3, contract.date_start and datetime.strptime(contract.date_start, DSDF).strftime(date_format) or '', style)
                        emp_contract_ws.write(emp_contract_row, 4, contract.date_end and datetime.strptime(contract.date_end, DSDF).strftime(date_format) or '', style)
                        emp_contract_ws.write(emp_contract_row, 5, tools.ustr(contract.struct_id and contract.struct_id.name or ''), style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.b64encode(data)
        # Create record for Binary data.
        emp_excell_rec = self.env['export.employee.data.record.xls'].create({'name': 'Employee Summary.xls',
                                                                             'file': res,
                                                                             })
        
        return {
            'name': _('Binary'),
            'res_id': emp_excell_rec.id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'export.employee.data.record.xls',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
