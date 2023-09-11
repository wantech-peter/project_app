# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProjectDateChangeWizard(models.TransientModel):
    _name = 'project.date.change.wizard'
    _description = 'Project Date Change'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    reason = fields.Text(string="Reason")

    def action_change_date(self):
        self.ensure_one()
        project_id = self.env.context.get('active_id')
        project = self.env['project.project'].browse(project_id)
        project.write({'date_start': self.start_date, 'date': self.end_date})
        message = _("Start Date - {start_date} <br> Expire Date -{end_date} <br> Reason - {reason}"
                    .format(start_date=self.start_date, end_date=self.end_date, reason=self.reason))
        project.message_post(body=message, subject='Changed Project Dates')
