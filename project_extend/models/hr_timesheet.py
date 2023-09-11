# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    exclude = fields.Boolean(string="Exclude")


