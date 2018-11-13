# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, tools, fields
import random
import uuid

class Product(models.Model):
    _inherit = "product.product"

    # Brand
    product_brand = fields.Char('Brand')

    # Product package
    product_package = fields.Char("Product Package")

    # Shelf location
    product_location = fields.Char("Location")

     # Product color
    product_color = fields.Char("Color")

    # Product Uniq Id
    product_uniq_id = fields.Char(
        compute='_compute_product_uid', string='Style', store=True)

    @api.one
    def _compute_product_uid(self):
        uniq_num = str(uuid.uuid4().fields[-1])[:6]
        self.design_uniq_id = random.choice("PD") + uniq_num