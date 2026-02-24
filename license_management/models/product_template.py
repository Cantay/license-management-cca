# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(
        selection_add=[
            ('support_package', 'Destek Paketi'),
            ('software', 'Program'),
            ('server_service', 'Sunucu Hizmeti'),
            ('domain_tracking', 'Domain Takibi'),
            ('backup_service', 'Yedekleme Servisi'),
        ],
        ondelete={
            'support_package': 'set default',
            'software': 'set default',
            'server_service': 'set default',
            'domain_tracking': 'set default',
            'backup_service': 'set default',
        }
    )

    is_license_product = fields.Boolean(
        string='Is License Product',
        default=False
    )

    # YENİ EKLENEN ALAN BAŞLANGICI
    has_maintenance_agreement = fields.Boolean(
        string='Has Maintenance Agreement',
        help="Check this if this product represents a maintenance or support agreement."
    )
    # YENİ EKLENEN ALAN SONU

    reference_code = fields.Char(
        string='Reference Code'
    )
    license_type = fields.Selection([
        ('perpetual', 'Perpetual'),
        ('subscription', 'Subscription'),
        ('trial', 'Trial'),
    ], string='License Type', default='subscription')

    # Link to license program
    license_program_id = fields.Many2one(
        'license.program',
        string='License Program'
    )
    program_code = fields.Char(
        string='Program Code',
        related='license_program_id.code',
    )
    allowed_term_ids = fields.Many2many(
        'license.term',
        'product_license_term_rel',
        'product_id',
        'term_id',
        string='Allowed License Terms',
        help="Specify which license terms are available for this product."
    )

    @api.onchange('is_license_product')
    def _onchange_is_license_product(self):
        if self.is_license_product:
            self.type = 'service'
            self.sale_ok = True
            self.purchase_ok = False
