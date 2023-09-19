# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProjectTaskReturnWizard(models.TransientModel):
    _name = 'project.task.return.wizard'
    _description = 'Project task return'

    reason = fields.Text(string="Reason")

    def action_return(self):
        self.ensure_one()
        task_id = self.env.context.get('active_id')
        task = self.env['project.task'].browse(task_id)
        project_stage_list = task.project_id.type_ids.filtered(lambda line: line.code == 'in_progress')
        task.write({'stage_id': project_stage_list[0].id})
        task._compute_is_in_progress()
        message = _("Return Task: {reason}".format(reason=self.reason))
        task.message_post(body=message, subject='Return Task')
