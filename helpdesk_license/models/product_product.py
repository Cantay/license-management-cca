# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('default_code', 'name', 'product_tmpl_id.program_code')
    def _compute_display_name(self):
        """
        Ürün görünen adını özelleştir: [Program_Code-Kod] Ürün Adı veya [Kod] Ürün Adı
        """
        for product in self:
            code_parts = []

            # Program kodunu ekle (varsa)
            if hasattr(product.product_tmpl_id, 'program_code') and product.product_tmpl_id.program_code:
                code_parts.append(product.product_tmpl_id.program_code)

            # Ürün kodunu ekle (varsa)
            if product.default_code:
                code_parts.append(product.default_code)

            # Kod varsa formatla, yoksa sadece isim
            if code_parts:
                code_str = "-".join(code_parts)
                product.display_name = f"[{code_str}] {product.name}"
            else:
                product.display_name = product.name
