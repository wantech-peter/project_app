# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTags(models.Model):
    _inherit = "project.tags"

    code = fields.Char('Code')