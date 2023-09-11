# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProjectTaskDateChangeWizard(models.TransientModel):
    _name = 'project.task.date.change.wizard'
    _description = 'Project Date Change'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    comment = fields.Text(string="Comment")

    def action_change_date(self):
        self.ensure_one()
        task_id = self.env.context.get('active_id')
        project_task = self.env['project.task'].browse(task_id)
        project_task.write({'custom_start_date': self.start_date, 'date_deadline': self.end_date})
        message = _("Start Date - {start_date} <br> Expire Date -{end_date} <br> Reason - {comment}"
                    .format(start_date=self.start_date, end_date=self.end_date, comment=self.comment))
        project_task.message_post(body=message, subject='Changed Project Task Dates')
