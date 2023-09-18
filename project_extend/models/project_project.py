# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    is_confirmed = fields.Boolean(string="Is Confirmed")
    man_hours_budget = fields.Float(string="Man Hours Budget")
    total_timesheet_hours = fields.Integer(
        compute='_compute_total_timesheet_hours', groups='hr_timesheet.group_hr_timesheet_user')
    type_ids = fields.Many2many(default=lambda self: self._get_default_type_common())
    can_edit_body_lead = fields.Boolean('Can Edit Body', compute='_compute_can_edit_body')
    can_edit_body_team_manager = fields.Boolean('Can Edit Body', compute='_compute_can_edit_body')

    @api.depends_context('uid')
    def _compute_can_edit_body(self):
        is_lead_consultant = self.user_has_groups('project_extend.group_project_lead_consultant')
        is_team_manager = self.user_has_groups('project_extend.group_project_team_manager')
        for item in self:
            # is_approver and sheet.employee_id.user_id != self.env.user
            item.can_edit_body_lead = is_lead_consultant
            item.can_edit_body_team_manager = is_team_manager

    def _get_default_type_common(self):
        ids = self.env["project.task.type"].search([("case_default", "=", True)])
        return ids

    @api.depends('timesheet_ids')
    def _compute_total_timesheet_hours(self):
        for rec in self:
            rec.total_timesheet_hours = sum(rec.timesheet_ids.filtered(lambda x: x.exclude != True).mapped('unit_amount'))

    def action_confirm(self):
        self.write({'is_confirmed': True})

