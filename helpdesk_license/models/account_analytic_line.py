# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    ticket_license_id = fields.Many2one(
        comodel_name="license.subscription",
        string="License",
        related="ticket_id.license_id",
        store=True,
    )
    ticket_dealer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Dealer",
        related="ticket_id.dealer_id",
        store=True,
    )
    ticket_program_id = fields.Many2one(
        comodel_name="license.program",
        string="Program",
        related="ticket_id.license_id.program_id",
        store=True,
    )
