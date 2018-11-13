# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, tools, fields


class UserProduct(models.Model):
    _name = 'emb_base.user_product'

     # Many2many type Garment
    product_id = fields.Many2one('product.product', ondelete='cascade', required=True)

    # Selected Color
    selected_color = fields.Char('Selected Color')

    # Image Transform
    image_transform = fields.Char('Image Transform')

    # Package
    product_package = fields.Char('Package')