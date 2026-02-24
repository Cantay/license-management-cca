# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

class LicenseTerm(models.Model):
    _name = 'license.term'
    _description = 'License Term'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True,
                       help="e.g., '1 Month Trial', '1 Year Standard', '3 Years Enterprise'")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    warning_days = fields.Integer(
        string="Warning Period (Days)",
        default=30,
        help="Start showing a 'Expiring Soon' warning this many days before the end date."
    )
    urgent_warning_days = fields.Integer(
        string="Urgent Warning (Days)",
        default=7,
        help="Start showing an 'Urgent' warning this many days before the end date."
    )
    # Süre Detayları
    duration = fields.Integer(string='Duration', default=1, required=True)
    unit = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Unit', default='years', required=True)

    description = fields.Text(string="Description")
    subscription_template_id = fields.Many2one(
        'sale.subscription.template',
        string="Subscription Template",
        help="The subscription template to use when creating a subscription from a license with this term."
    )
    # DÜZELTİLDİ: Yardımcı metot iyileştirildi
    def _get_end_date(self, start_date):
        """Verilen başlangıç tarihine göre bitiş tarihini hesaplar."""
        self.ensure_one()
        if not start_date:
            return None

        # start_date string ise date nesnesine çevir
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        elif isinstance(start_date, datetime):
            start_date = start_date.date()

        # relativedelta kullanarak doğru hesaplama
        if self.unit == 'days':
            from datetime import timedelta
            return start_date + timedelta(days=self.duration)
        elif self.unit == 'weeks':
            from datetime import timedelta
            return start_date + timedelta(weeks=self.duration)
        else:
            # months ve years için relativedelta kullan
            delta_args = {self.unit: self.duration}
            return start_date + relativedelta(**delta_args)

    @api.depends('name')
    def _compute_display_name(self):
        for term in self:
            term.display_name = term.name
