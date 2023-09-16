# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    owner = fields.Many2one("res.users", string="Owner")
    reviewer = fields.Many2one("res.users", string="Reviewer")
    custom_start_date = fields.Date('Start Date', readonly=True, copy=False, )
    custom_end_date = fields.Date('Start Date', readonly=True)
    date_deadline = fields.Date(string='End Date', readonly=True, copy=False, tracking=True, task_dependency_tracking=True)
    is_milestone_task = fields.Boolean(string="Is Milestone Task")
    related_task = fields.One2many('project.task.related.task', 'task_id', string='Related Task')
    man_hours_budget = fields.Float(string="Man Hours Budget", compute='_compute_man_hours_budget')
    is_in_progress = fields.Boolean(string="Is in Progress", compute='_compute_is_in_progress')
    is_review = fields.Boolean(string="Is in review")
    is_draft = fields.Boolean(string="Is Draft", default=True)
    show_return = fields.Boolean(string="Show Return")
    current_user = fields.Many2one("res.users", string="current user", compute='_compute_current_user')
    is_owner = fields.Boolean("Is Owner")
    can_edit_body = fields.Boolean('Can Edit Body', compute='_compute_can_edit_body')

    @api.depends_context('uid')
    def _compute_can_edit_body(self):
        is_lead_consultant = self.user_has_groups('project_extend.group_project_lead_consultant')
        for item in self:
            # is_approver and sheet.employee_id.user_id != self.env.user
            item.can_edit_body = is_lead_consultant

    def _compute_current_user(self):
        self.current_user = self.env.context.get('uid', False)
        if self.owner == self.current_user:
            self.is_owner = True
        else:
            self.is_owner = False

    def complete_task(self):
        project_stage_list = self.project_id.type_ids.filtered(lambda line: line.code == 'review')
        if project_stage_list:
            self.stage_id = project_stage_list[0].id
        else:
            raise UserError(_("The Review stage is not in this project. Please add it first."))

    def return_task(self):
        project_stage_list = self.project_id.type_ids.filtered(lambda line: line.code == 'in_progress')
        if project_stage_list:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Return Task'),
                'res_model': 'project.task.return.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_id': self.id},
                'views': [[False, 'form']]
            }
            # self.stage_id = project_stage_list[0].id
        else:
            raise UserError(_("The In Progress stage is not in this project. Please add it first."))

    def approve_task(self):
        project_stage_list = self.project_id.type_ids.filtered(lambda line: line.code == 'done')
        if project_stage_list:
            self.stage_id = project_stage_list[0].id
        else:
            raise UserError(_("The Done stage is not in this project. Please add it first."))

    def _compute_is_in_progress(self):
        self.is_in_progress = False
        self.is_review = False
        self.show_return = False
        if self.stage_id.code == "in_progress":
            self.is_in_progress = True
            self.is_review = False
            self.is_draft = False
        elif self.stage_id.code == "review":
            self.is_in_progress = False
            self.is_review = True
            self.show_return = True
            self.is_draft = False
        elif self.stage_id.code in ["done", 'cancelled']:
            self.is_draft = False
        asd = 123

    def _compute_man_hours_budget(self):
        for item in self:
            total_hours = sum(item.timesheet_ids.filtered(lambda line: line.exclude is True).mapped("unit_amount"))
            item.man_hours_budget = total_hours

    @api.depends('timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        if not any(self._ids):
            for task in self:
                task.effective_hours = sum(task.timesheet_ids.filtered(lambda line: line.exclude is False).mapped('unit_amount'))
            return
        timesheet_read_group = self.env['account.analytic.line'].read_group([('task_id', 'in', self.ids), ('exclude', "=", False)], ['unit_amount', 'task_id'], ['task_id'])
        timesheets_per_task = {res['task_id'][0]: res['unit_amount'] for res in timesheet_read_group}
        for task in self:
            task.effective_hours = timesheets_per_task.get(task.id, 0.0)


class ProjectTaskRalatedTask(models.Model):
    _name = 'project.task.related.task'

    name = fields.Char(string="Task Name")
    project = fields.Many2one("project.project", string="Project")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    task_id = fields.Many2one("project.task", string="Parent Task")

    # is_confirmed = fields.Boolean(string="Is Confirmed")
    # man_hours_budget = fields.Float(string="Man Hours Budget")
    # total_timesheet_hours = fields.Integer(
    #     compute='_compute_total_timesheet_hours', groups='hr_timesheet.group_hr_timesheet_user')
    # type_ids = fields.Many2many(default=lambda self: self._get_default_type_common())
    #
    # def _get_default_type_common(self):
    #     ids = self.env["project.task.type"].search([("case_default", "=", True)])
    #     return ids
    #
    # @api.depends('timesheet_ids')
    # def _compute_total_timesheet_hours(self):
    #     for rec in self:
    #         rec.total_timesheet_hours = sum(rec.timesheet_ids.filtered(lambda x: x.exclude != True).mapped('unit_amount'))
    #
    # def action_confirm(self):
    #     self.write({'is_confirmed': True})
