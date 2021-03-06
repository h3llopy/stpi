from odoo import models, fields, api,_
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError



class PfInterestDisbursement(models.Model):
    _name = 'pf.interest.disbursement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'pf.interest.disbursement'

    branch_id = fields.Many2many('res.branch', track_visibility='always')
    date_range = fields.Many2one('date.range', string='Ledger for the year')
    from_date = fields.Date('From Date', track_visibility='always')
    to_date = fields.Date('To Date', track_visibility='always')
    interest_rate = fields.Float('Interest Rate', track_visibility='always')
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted')
         ], required=True, default='draft',string="Status",track_visibility='always',)



    @api.onchange('branch_id','date_range')
    @api.constrains('branch_id','date_range')
    def check_existing_branch_sr(self):
        for rec in self:
            rec.from_date = rec.date_range.date_start
            rec.to_date = rec.date_range.date_end
            comp_model = self.env['pf.interest.disbursement'].search([('branch_id', 'in', rec.branch_id.ids),('date_range', '=', rec.date_range.id),('state', '=', 'submitted')])
            if comp_model:
                raise ValidationError(
                    _('Already Submitted'))
            company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
            if company:
                for com in company:
                    if rec.date_range.date_start and rec.date_range.date_end and rec.branch_id:
                        for line in com.pf_table:
                            if line.from_date >= rec.date_range.date_start and line.to_date <= rec.date_range.date_end:
                                rec.interest_rate = line.interest_rate



    # @api.constrains('from_date','to_date','branch_id','date_range')
    # @api.onchange('from_date','to_date','branch_id','date_range')
    # def onchange_date_branch_gi(self):
    #     for rec in self:
    #         company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
    #         if company:
    #             rec.date_range.date_start = rec.date_range.date_start
    #             rec.date_range.date_end = rec.date_range.date_end
    #             for com in company:
    #                 if rec.date_range.date_start and rec.date_range.date_end and rec.branch_id:
    #                     for line in com.pf_table:
    #                         if line.from_date >= rec.date_range.date_start and line.to_date <= rec.date_range.date_end:
    #                             rec.interest_rate = line.interest_rate



    @api.multi
    def unlink(self):
        for pf in self:
            if pf.state not in ('draft'):
                raise UserError(
                    'You cannot delete a PF Interest Disbursement which is not in draft state')
        return super(PfInterestDisbursement, self).unlink()


    @api.multi
    def button_submit(self):
        for rec in self:
            x = 0.00
            pf_details_ids = []
            pf_details_ids_cepf = []
            employee_interest = 0
            company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
            if company:
                for com in company:
                    if rec.date_range.date_start and rec.date_range.date_end and rec.branch_id:
                        for line in com.pf_table:
                            if line.from_date >= rec.date_range.date_start and line.to_date <= rec.date_range.date_end:
                                x = line.interest_rate
            print('===============X===================', x)
            pf_emp = self.env['pf.employee'].search([('employee_id.branch_id', 'in', rec.branch_id.ids)])
            print('===============pf_emp===================', pf_emp)
            print('===============rec.branch_id.ids===================', rec.branch_id.ids)
            for line in pf_emp:
                from_date = rec.date_range.date_start
                to_date = rec.date_range.date_end
                print('==============count========================')
                print('==============line.employee_id.id========================',line.employee_id.name)
                while from_date < rec.date_range.date_end:
                    print('===============from date===================', from_date)
                    print('===============To date===================', rec.date_range.date_end)
                    pay_rules = self.env['hr.payslip.line'].search(
                        [('slip_id.employee_id', '=', line.employee_id.id),
                         ('slip_id.state', '=', 'done'),
                         ('slip_id.date_from', '>=', from_date),
                         ('slip_id.date_to', '<', from_date + relativedelta(months=1)),
                         ('salary_rule_id.pf_register', '=', True),
                         ])
                    print('=============Payslip===============', pay_rules)
                    emp = 0
                    volun = 0
                    emplyr = 0
                    employee_interest = 0
                    employer_contribution = 0
                    for ln in pay_rules:
                        if ln.salary_rule_id.pf_eve_type == 'employee':
                            emp += ln.total
                        elif ln.salary_rule_id.pf_eve_type == 'voluntary':
                            volun += ln.total
                        elif ln.salary_rule_id.pf_eve_type == 'employer':
                            emplyr += ln.total
                    # print('==================Employee===================', emp)
                    # print('==================Voluntary===================', volun)
                    # print('==================Employer===================', emplyr)
                    if str(from_date.month) == '1':
                        month = 'January'
                        employee_interest = (((emp + volun) * x) * 3) / 12
                        employer_contribution = (((emplyr) * x) * 3) / 12
                    elif str(from_date.month) == '2':
                        month = 'February'
                        employee_interest = (((emp + volun) * x) * 2) / 12
                        employer_contribution = (((emplyr) * x) * 2) / 12
                    elif str(from_date.month) == '3':
                        month = 'March'
                        employee_interest = (((emp + volun) * x) * 1) / 12
                        employer_contribution = (((emplyr) * x) * 1) / 12
                    elif str(from_date.month) == '4':
                        month = 'April'
                        employee_interest = (((emp + volun) * x) * 12) / 12
                        employer_contribution = (((emplyr) * x) * 12) / 12
                    elif str(from_date.month) == '5':
                        month = 'May'
                        employee_interest = (((emp + volun) * x) * 11) / 12
                        employer_contribution = (((emplyr) * x) * 11) / 12
                    elif str(from_date.month) == '6':
                        month = 'June'
                        employee_interest = (((emp + volun) * x) * 10) / 12
                        employer_contribution = (((emplyr) * x) * 10) / 12
                    elif str(from_date.month) == '7':
                        month = 'July'
                        employee_interest = (((emp + volun) * x) * 9) / 12
                        employer_contribution = (((emplyr) * x) * 9) / 12
                    elif str(from_date.month) == '8':
                        month = 'August'
                        employee_interest = (((emp + volun) * x) * 8) / 12
                        employer_contribution = (((emplyr) * x) * 8) / 12
                    elif str(from_date.month) == '9':
                        month = 'September'
                        employee_interest = (((emp + volun) * x) * 7) / 12
                        employer_contribution = (((emplyr) * x) * 7) / 12
                    elif str(from_date.month) == '10':
                        month = 'October'
                        employee_interest = (((emp + volun) * x) * 6) / 12
                        employer_contribution = (((emplyr) * x) * 6) / 12
                    elif str(from_date.month) == '11':
                        month = 'November'
                        employee_interest = (((emp + volun) * x) * 5) / 12
                        employer_contribution = (((emplyr) * x) * 5) / 12
                    elif str(from_date.month) == '12':
                        month = 'December'
                        employee_interest = (((emp + volun) * x) * 4) / 12
                        employer_contribution = (((emplyr) * x) * 4) / 12
                    else:
                        month = ''
                        employee_interest = 0
                        employer_contribution = 0
                    total = emp + volun + emplyr + employee_interest + employer_contribution
                    print('==================amount===================', round(employee_interest))
                    pf_details_ids.append((0, 0, {
                        'pf_details_id': line.id,
                        'employee_id': line.employee_id.id,
                        'type': 'Deposit',
                        'pf_code': 'CEPF + VCPF',
                        'description': 'Interest on CEPF and VCPF - {}'.format(month),
                        'date': datetime.now().date(),
                        'amount': round(employee_interest),
                        'reference': 'Interest deposit on {}'.format(datetime.now().date()),
                    }))
                    pf_details_ids_cepf.append((0, 0, {
                        'pf_details_id': line.id,
                        'employee_id': line.employee_id.id,
                        'type': 'Deposit',
                        'pf_code': 'CEPF',
                        'description': 'Interest on CEPF',
                        'date': datetime.now().date(),
                        'amount': round(employer_contribution),
                        'reference': 'Interest deposit on {}'.format(datetime.now().date()),
                    }))
                    from_date = from_date + relativedelta(months=1)
                line.pf_details_ids = pf_details_ids
                line.pf_details_ids = pf_details_ids_cepf
            rec.write({'state': 'submitted'})