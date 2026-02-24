# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LicenseHistory(models.Model):
    _name = 'license.history'
    _description = 'License History'
    _order = 'date desc'
    _rec_name = 'action'

    license_id = fields.Many2one('license.subscription', string='License',
                                required=True, ondelete='cascade')
    action = fields.Selection([
        ('created', 'Created'),
        ('activated', 'Activated'),
        ('renewed', 'Renewed'),
        ('auto_renewed', 'Auto Renewed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('modified', 'Modified'),
        ('set_active', 'Set to Active'),
        ('archived', 'Archived'),
        ('unarchived', 'Unarchived'),
        ('subscription_created', 'Subscription Created'),
    ], string='Action', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='User', required=True)
    notes = fields.Text(string='Notes')
