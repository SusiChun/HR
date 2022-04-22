 # -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
DEFAULT_SERVER_DATETIME_FORMAT



class HrEmployeeExtended(models.Model):
    _inherit = 'hr.employee'



    emp_country_id = fields.Char('Nationality')
    relative_ids = fields.One2many('applicant.relative', 'employee_id',
                                   "Parents,Brothers & Sisters (Dependent)")

    employment_history_ids = fields.One2many('applicant.history',
                                             'employee_id',
                                             'Employment History')
    passport_exp_date = fields.Date('Passport Expiry Date')
    start_date = fields.Date('Start Date')

    training_ids = fields.One2many('employee.training', 'tr_id', 'Training')
    edu_ids = fields.One2many('applicant.edu', 'employee_id', 'Education')
    age = fields.Integer(compute='compute_age', store=True, string='Age')

    comp_prog_knw = fields.Char('Computer Programs Knowledge')
    typing = fields.Integer('Typing')
    shorthand = fields.Integer('Shorthand')
    other_know = fields.Char('Other Knowledge & Skills')
    course = fields.Char('Courses Taken')
    language_ids = fields.One2many('applicant.language', 'employee_id',
                                   'Language Proficiency')
    emp_child_ids = fields.One2many('employee.children', 'employee_id',
                                    'Child Details')
    is_children = fields.Boolean('Is Children?')
    birthday_day = fields.Integer('Day of Birthday',
                                  compute="get_day_birthdate", store=True)
    birthday_month = fields.Integer('Month of Birthday',
                                    compute="get_month_birthdate", store=True)
    organisasi_ids   = fields.One2many('riwayat.organisasi','employee_id','Organisasi')
    contact_ids      = fields.One2many(comodel_name='contact.hr',inverse_name='employee_id')
    contact_inform_ids = fields.One2many(comodel_name='contact.inform.hr', inverse_name='employee_id')
    work_phone2        = fields.Char(string='Work Phone 2')
    work_phone3         = fields.Char(string='Work Phone 3')
    is_phl              = fields.Char(string='Is PHL')
    nik                 = fields.Char(string='NIK')
    religion            = fields.Selection([('Islam', 'Islam'),
                                   ('Kristen', 'Kristen'),
                                   ('Katolik', 'Katolik'),
                                   ('Hindu', 'Hindu'),
                                   ('Budha', 'Budha'),
                                   ('Others', 'Others')],
                                   'Religion')
    address              = fields.Char(string='Address')
    grade            = fields.Selection([('1', '1'),
                                   ('2', '2'),
                                   ('3', '3'),
                                   ('4', '4'),
                                   ('5', '5'),
                                   ('6', '6'),
                                     ('7', '7'),
                                     ('8', '8')],
                                   'Grade')
    npwp            = fields.Char(string='NPWP')
    bpjs_kesehatan = fields.Char(string='BPJS Health')
    bpjs_ketenagakerjaan = fields.Char(string='BPJS Employeement')
    plan_no  = fields.Char(string='PLAN')
    card_no  = fields.Char(string='Card No')
    generali_no = fields.Char(string='Generali No')
    tax_status            = fields.Selection([('TK-0', 'TK-0'),
                                   ('K-0', 'K-0'),
                                   ('K-1', 'K-1'),
                                   ('K-2', 'K-2'),
                                   ('K-3', 'K-3')],

                                   'Tax Status')
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type',string='Employee Status')
    barcode             = fields.Char(string='Barcode')
    own_vehicle         = fields.Char(string='Owned Vehicle')
    sim_type            = fields.Char(string="Sim Type")
    insurance_no        = fields.Char(string="Insurance No")
    marital            = fields.Selection([('Single', 'Single'),
                                   ('Married', 'Married'),
                                   ('Widow', 'Widow'),
                                   ('Widower', 'Widower'),
                                   ('Divorced', 'Divorced')],
                                    'Marital Status')


    @api.multi
    def get_sequence(self):
        for rec in self:
            if rec.birthday:
                sequence_id = self.env['ir.sequence'].search([
                    ('code', '=', 'MGS-EMPLOYEE'),
                ],limit=1)
                default = datetime.now().strftime('%Y-%m-%d')
                bday = datetime.strptime(rec.birthday, "%Y-%m-%d")
                rec.birthday_year = bday.year
                if rec.company_id.company_registry:
                    seq = self.env['ir.sequence']
                    nik = default[2:4]+'/'+ str(rec.birthday[2:4]) + '/'+ rec.company_id.company_registry+ '/' + sequence_id.next_by_id()
                    self.nik = nik
                else:
                    raise ValidationError(_("Kode Company /Company Registry belum diisi di Master Company!"))



    @api.constrains('birthday')
    def _check_birthday(self):
        """
        This method used to check birthday should be less then current date.
        """
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        for rec in self:
            if rec.birthday and rec.birthday >= curr_date:
                raise ValidationError(_("Date of Birth should be \
                    less than the Current Date!"))




    @api.multi
    @api.depends('birthday')
    def get_day_birthdate(self):
        for rec in self:
            if rec.birthday:
                bday = datetime.strptime(rec.birthday, "%Y-%m-%d")
                rec.birthday_day = bday.day

    @api.multi
    @api.depends('birthday')
    def get_month_birthdate(self):
        for rec in self:
            if rec.birthday:
                bmonth = datetime.strptime(rec.birthday, "%Y-%m-%d")
                rec.birthday_month = bmonth.month

    @api.multi
    @api.depends('birthday')
    def compute_age(self):
        for rec in self:
            if rec.birthday:
                bday = datetime.strptime(rec.birthday, "%Y-%m-%d").date()
                curr_date = datetime.today().date()
                if bday > curr_date:
                    raise ValidationError("Birthday should be less then \
                    current date!")
                diff = curr_date.year - bday.year
                rec.age = str(diff)




    @api.onchange('children')
    def onchange_children(self):
        if self.children and self.children != 0:
            self.is_children = True
        else:
            self.is_children = False
        if self.children and self.emp_child_ids:
            self.children = len(self.emp_child_ids.ids)

    @api.multi
    def copy(self, default={}):
        default = default or {}
        default['employment_history_ids'] = []
        default['child_ids'] = []
        default['contract_ids'] = []
        return super(HrEmployeeExtended, self).copy(default)

    @api.multi
    def write(self, vals):
        """
        Override this method to add employee history according to change state.
        """
        context = dict(self._context)
        if context is None:
            context = {}
        if 'active' in vals:
            if self.user_id:
                self.user_id.write({'active': vals.get('active')})
        return super(HrEmployeeExtended, self).write(vals)

    @api.model
    def create(self, vals):
        """
        Override this method to add employee history according to change state.
        """
        context = dict(self._context)
        if context is None:
            context = {}
        employee_id = super(HrEmployeeExtended, self).create(vals)
        active = vals.get('active', False)
        user_obj = self.env['res.users']
        if vals.get('user_id') and not active:
            user_obj.browse(vals.get('user_id')).write({'active' : active})
        return employee_id



class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields):
        """
        This method override to set partener's language = False.
        """
        result = super(ResPartner, self).default_get(fields)
        result['lang'] = False
        return result



class ApplicantRelationship(models.Model):
    _name = 'applicant.relationship'

    seq_code = fields.Integer("Sequence")
    name = fields.Char('Relationship')


class ApplicantRelative(models.Model):
    _name = 'applicant.relative'
    _description = 'Applicant Relative'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    name = fields.Char('Name')
    relationship_id = fields.Many2one('applicant.relationship', 'Relationship')
    date_of_birth = fields.Date('Date of Birth')
    occupation = fields.Char('Occupation')
    address = fields.Char('Address')
    relative_id = fields.Many2one('hr.applicant')
    contact = fields.Boolean('Contact')
    emr_telephone = fields.Char('Phone')

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        """
        This constraint used to check relative birthday should be less then 
        current date.
        """
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth >= curr_date:
                raise ValidationError("Birthday of Relative should be \
                less then current date!")

    @api.onchange('date_of_birth')
    def onchange_date_of_birth(self):
        """This onchange is used to check relative birthday should be less then 
        current date."""
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        if self.date_of_birth and self.date_of_birth > curr_date:
            raise ValidationError("Birthday of Relative should be less then \
            current date!")


class ApplicantHistory(models.Model):
    _name = 'applicant.history'
    _description = 'Work Experience'
    _rec_name = "company"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    company             = fields.Char('Company Name',required=True)
    position            = fields.Char('Position')
    start_year          = fields.Integer('Start Year',size=4)
    end_year            = fields.Integer('End Year',size=4)
    reason              = fields.Text('Reason For Leaving')
    last_salary         = fields.Float(string='Last Salary')


    @api.constrains('start_year', 'end_year')
    def check_dates_history(self):
        """
        This constraint check the start date of employee history is less then 
        end date of employee history.
        """
        for rec in self:
            if rec.start_year and rec.end_year and rec.start_year > rec.end_year:
                raise ValidationError("End date should be greater than \
                start date!")

    @api.onchange('start_year', 'end_year')
    def onchange_history_dates(self):
        """
        This onchange method check to date should be greater than from date of 
        employee History.
        """
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValidationError("End date should be greater than Start date!")


class EducationLevel(models.Model):
    _name = "education.level"
    _description = 'Applicant Education Level'
    _rec_name = "type"

    code = fields.Char("Education Level Code", required=1)
    type = fields.Char("Level", required=1)


class ApplicantEdu(models.Model):
    _name = 'applicant.edu'
    _description = 'Applicant Education'
    _rec_name = 'edu_school'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    edu_level = fields.Many2one('education.level', 'Education Level')
    edu_school = fields.Char('Name & Country of School')
    period = fields.Char('Period')
    edu_certificate = fields.Char('Certificate Obtained')

class ApplLang(models.Model):
    _name = 'appl.lang'
    _description = 'Language'

    code = fields.Integer("Code", required=True)
    name = fields.Char('Language', required=True)


class ApplicantLanguage(models.Model):
    _name = 'applicant.language'
    _description = 'Applicant Language'
    _rec_name = 'lang_name_id'

    rate_list = [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'),
                 ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
                 ('10', '10')]

    employee_id = fields.Many2one('hr.employee', 'Employee')
    language_id = fields.Many2one('hr.applicant', 'Applicant')
    lang_name_id = fields.Many2one('appl.lang', 'Language')
    spoken = fields.Selection(rate_list, 'Spoken')
    written = fields.Selection(rate_list, 'Written')


class EmployeeChildren(models.Model):
    _name = 'employee.children'

    name = fields.Char('Name')
    age = fields.Integer('Age')
    employee_id = fields.Many2one('hr.employee', 'Employee ID')

    @api.model
    def create(self, vals):
        """
        Override create method to update number of children field.
        """
        res = super(EmployeeChildren, self).create(vals)
        employees = res.employee_id
        ttl_child = len(self.search([('employee_id', '=',
                                      employees.id)]).ids)
        employees.children = ttl_child
        age = vals.get('age')
        if age and len(str(age)) > 3:
            raise ValidationError("Please enter appropriate age of child!")
        return res

    @api.multi
    def write(self, vals):
        """
        Override write method to update number of children field.
        """
        res = super(EmployeeChildren, self).write(vals)
        for rec in self:
            employees = rec.employee_id
            ttl_child = len(self.search([('employee_id', '=',
                                      employees.id)]).ids)
            employees.children = ttl_child
            age = rec.age
            if age and len(str(age)) > 3:
                raise ValidationError("Please enter appropriate age of child!")
        return res

    @api.multi
    def unlink(self):
        """
        Override unlink method to update number of children field.
        """
        employees = False
        for rec in self:
            employees = rec.employee_id
        res = super(EmployeeChildren, self).unlink()
        if employees:
             ttl_child = len(employees.emp_child_ids.ids)
             if ttl_child == 0:
                 employees.is_children = False
             employees.children = ttl_child
        return res




class EmployeeIdType(models.Model):
    _name = 'employee.id.type'

    name = fields.Char("EP", required=True)
    s_pass = fields.Selection([('skilled', 'Skilled'),
                               ('unskilled', 'Un Skilled')], 'S Pass')
    wp = fields.Selection([('skilled', 'Skilled'),
                           ('unskilled', 'Un Skilled')], 'Wp')


class EmployeeTraining(models.Model):
    _name = 'employee.training'
    _description = 'Employee Certificate'
    _rec_name = 'tr_title'

    tr_id = fields.Many2one('hr.employee', 'Employee')
    tr_title = fields.Char('Certificate Name', required=True)
    tr_institution = fields.Char('Certificate Number')
    tr_date = fields.Date('Certificate Date')
    date_expire = fields.Date('Certificate Expired Date')
    training_attachment = fields.Binary('Attachment Data')

    @api.constrains('tr_date')
    def check_tr_date(self):
        """
        This method is used to check date of training / workshop should be 
        greater than current date.
        """
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        for rec in self:
            if rec.tr_date and rec.tr_date >= curr_date:
                raise ValidationError("Date of training / workshop should be \
                greater than current date")

    @api.onchange('tr_date')
    def onchange_tr_date(self):
        """
        This method is used to check date of training / workshop should be 
        greater than current date.
        """
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        if self.tr_date and self.tr_date > curr_date:
            raise ValidationError("Date of training / workshop should be \
            greater than current date")


class ResCompany(models.Model):
    _inherit = 'res.company'

    department_id = fields.Many2one('hr.department', 'Department')


class HrContractExtended(models.Model):
    _inherit = "hr.contract"

    @api.constrains('date_end', 'date_start', 'employee_id', 'trial_date_start',
                    'trial_date_end')
    def _check_date(self):
        """
        This method is used to check end date should be greater than start date,
         overlapping contract.
        """
        for contract in self:
            if contract.employee_id and contract.date_start:
                emploee_id = contract.employee_id
                # if emploee_id.emp_status == 'terminated':
                #     raise ValidationError("You can not create contract \
                #     for %s ! \n%s is Terminated ! " % (emploee_id.name,
                #     emploee_id.name))
                start_date = contract.date_start
                if not contract.date_end:
                    self._cr.execute("""select id from hr_contract where 
                    employee_id = %s and id != %s and 
                    (%s between TO_CHAR(date_start,'YYYY-MM-DD') and 
                    TO_CHAR(date_end,'YYYY-MM-DD'))""", (emploee_id.id,
                                                         contract.id,
                                                         start_date,))
                    contract_id = self._cr.fetchall()
                    contract_ids = self.search([
                                                ('employee_id', '=',
                                                 emploee_id.id),
                                                ('date_end', '=', False),
                                                ('id', '!=', contract.id)
                                                ])
                    if contract_id or contract_ids:
                        raise ValidationError("You can not create contract\
                        for same duration!")

                else:
                    end_date = contract.date_end
                    if contract.date_end < contract.date_start:
                        raise ValidationError("Start Date should be less then\
                        End date!")
                    self._cr.execute("""select id from hr_contract where 
                    employee_id = %s and id !=%s and
                    ((date_start between %s and %s) or
                    (date_end between %s and %s))""", (emploee_id.id,
                                                       contract.id, start_date,
                                                       end_date, start_date,
                                                       end_date,))
                    contract_ids = self._cr.fetchall()
                    if contract_ids:
                        raise ValidationError('You can not have 2 contract that \
                        overlaps on same period!')
                if contract.trial_date_start and contract.trial_date_end:
                    t_start_date = contract.trial_date_start
                    t_end_date = contract.trial_date_end
                    if contract.trial_date_start > contract.trial_date_end:
                        raise ValidationError("Start date of trial period should be\
                        less then end date of trial period!")
                    self._cr.execute("""select id from hr_contract where 
                    employee_id = %s and id !=%s and
                    ((date_start between %s and %s) or
                    (date_end between %s and %s))""", (emploee_id.id,
                                                       contract.id, t_start_date,
                                                       t_end_date, t_start_date,
                                                       t_end_date,))
                    trial_period_rec = self._cr.fetchall()
                    if trial_period_rec:
                        raise ValidationError("You can not have 2 contract that \
                        overlaps on same trial period!")

        return True

class Organisasi(models.Model):
    _name = 'riwayat.organisasi'
    _description = 'Riwayat Organisasi'


    employee_id = fields.Many2one(comodel_name='hr.employee')
    name       = fields.Char(string='Name of Organization',required=True)
    city        = fields.Char(string='City')
    major        = fields.Char(string='Major')
    position       = fields.Char(string='Position')
    start_year       = fields.Integer(string='Start Year',size=4)
    end_year        = fields.Integer(string='End Year',size=4)

class Contact(models.Model):
    _name = 'contact.hr'
    _description = 'Contact HR'


    employee_id         = fields.Many2one(comodel_name='hr.employee')
    name                = fields.Char(string='Name',required=True)
    position            = fields.Char(string='Position')
    no_handphone        = fields.Char(string='No Handphone',size=15)

class Contact_Inform(models.Model):
    _name = 'contact.inform.hr'
    _description = 'Contact Inform HR'


    employee_id         = fields.Many2one(comodel_name='hr.employee')
    name                = fields.Char(string='Name',required=True)
    relation            = fields.Char(string='Relation')
    no_handphone        = fields.Char(string='No Handphone',size=15)

