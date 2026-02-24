# -*- coding: utf-8 -*-
from odoo import fields, models, api

class LicenseSubscription(models.Model):
    _inherit = 'license.subscription'

    # helpdesk_mgmt modülündeki mevcut alanı kullanarak
    # lisansın müşterisinin toplam ticket sayısını buraya taşıyoruz.
    customer_ticket_count = fields.Integer(
        related='customer_id.helpdesk_ticket_count',
        string="Ticket Sayısı",
        store=True,  # Performans ve gruplama için
        readonly=True,
        help="Bu lisansın ait olduğu müşterinin toplam ticket sayısı."
    )

    @api.depends('license_no', 'product_id', 'program_code')
    def _compute_display_name(self):
        """Display name hesaplama - Odoo 17+ yeni yaklaşım"""
        for record in self:
            if record.license_no and record.product_id and record.product_id:
                record.display_name = f"[{record.license_no}] [{record.program_code}] {record.product_id.name} "
            elif record.license_no:
                record.display_name = record.license_no
            elif record.product_id:
                record.display_name = record.product_id.name
            else:
                record.display_name = "Unnamed License"
