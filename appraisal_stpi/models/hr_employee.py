from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    appraisal_reporting_officer = fields.Many2one('hr.employee', string='Appraisal Reporting Officer')
    appraisal_approving_officer = fields.Many2one('hr.employee', string='Appraisal Approving Officer')