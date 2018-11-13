
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, tools, fields

class DecorationServiceCategory(models.Model):
    _name = "decoration.service.category"
    _inherit = ["website.seo.metadata"]
    _description = "Decoration Service Category"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one('product.public.category', string='Parent Category', index=True)
    child_id = fields.One2many('product.public.category', 'parent_id', string='Children Categories')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.")


class ResLogoSurcharge(models.Model):
    _name = 'emb_base.decoration_logo_surcharge'

    # Decoration Type
    category_id = fields.Many2one('decoration.service.category', string="Decoration Type")
    # Name
    name = fields.Char('Surcharge Name')
    # Amount
    amount = fields.Float(string='Surcharge Amount', required=True)

class ProductSurcharge(models.Model):
    _name = 'emb_base.product_surcharge'
    # Decoration Type
    category_id = fields.Many2one('product.public.category', string="Product Public Category")
    # Name
    name = fields.Char('Surcharge Name')
    # Amount
    amount = fields.Float(string='Surcharge Amount', required=True)

class DecorationServiceSurcharge(models.Model):
    _name = 'emb_base.decoration_service_surcharge'

    # Decoration Type
    category_id = fields.Many2one('decoration.service.category', string="Decoration Category")
    # Name
    name = fields.Char('Surcharge Name')
    # Amount
    amount = fields.Float(string='Surcharge Amount', required=True)