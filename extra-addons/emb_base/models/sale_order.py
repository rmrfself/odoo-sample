# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import random

from odoo import api, models, fields, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
import json
from copy import copy

_logger = logging.getLogger(__name__)


class StSaleOrder(models.Model):
    _inherit = 'sale.order'

    # Custom field
    partner_email = fields.Char(
        'E-Mail', related='partner_id.email', readonly=True)

    # Custom field
    partner_addr = fields.Char(
        'Address', related='partner_id.street', readonly=True)

    # Custom field
    partner_title = fields.Char(
        'Job Name', related='partner_id.street', readonly=True)

    # Custom field
    partner_phone = fields.Char(
        'Job Name', related='partner_id.phone', readonly=True)

    # Custom field
    st_order_lines = fields.One2many('sale.order.line', 'order_id', string='Order Lines', compute="_get_order_lines", states={
                                     'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    # Custom field
    order_lines_broker = fields.Char(
        'Oder Line', compute='_extend_order_lines', store=False)

    # Custom field
    st_order_services = fields.One2many('sale.order.line', 'order_id', string='Services', compute="_compute_order_services", states={
        'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    # Custom field
    order_line_logos = fields.Many2many(
        'emb_base.user_logo', compute='_compute_logos', string="Logos")

    @api.one
    def _compute_order_services(self):
        for record in self:
            order_lines = self.env['sale.order.line'].search([], limit=1)
        self.st_order_services = order_lines

    @api.one
    def _get_order_lines(self):
        for record in self:
            order_lines = self.env['sale.order.line'].search([], limit=1)
        self.st_order_lines = order_lines

    @api.one
    def _extend_order_lines(self):
        for sale in self:
            order_lines = self.env['sale.order.line'].search_read(
                [('order_id', '=', sale.id), ('state', 'in', ['draft', 'new'])])
            sale.order_lines_broker = json.dumps(order_lines)
            # # Merge order lines
            # splited_order_lines = []
            # for ol in order_lines:
            #     request_quantity = ol['request_quantity']
            #     request_quantity_encoded = json.loads(request_quantity)
            #     for rq in request_quantity_encoded:
            #         if rq['color']:
            #             ol['broker_product_color'] = rq['color']
            #         else:
            #             ol['broker_product_color'] = 'No Color'
            #         rq_size_list = rq['size']
            #         size_seed = rq_size_list.pop()
            #         for ss in rq_size_list:
            #             for sss in ss:
            #                 if sss in size_seed:
            #                     size_seed[sss] = size_seed[sss] + ss[sss]
            #                 else:
            #                     size_seed[sss] = ss[sss]
            #         ol['broker_size_quantity'] = json.dumps(size_seed)
            #         # Dummy values that need to fill in
            #         ol['broker_product_picture'] = 'Mock'
            #         ol['description'] = 'Dummy Desc'
            #         splited_order_lines.append(ol)
            # sale.order_lines_broker = json.dumps(splited_order_lines)

    @api.one
    def _compute_logos(self):
        for record in self:
            user_logos = self.env['emb_base.user_logo'].search([], limit=1)
        self.order_line_logos = user_logos


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'
    _order = 'order_id, layout_category_id, sequence, id'

    # Logo ids with m2m relation
    logo_ids = fields.Many2many('emb_base.user_logo', 'sale_order_line_user_logo_rel',
                                'sale_order_line_id', 'user_logo_id', string="Logos")

    # Format [{color: '#FFFF',size: {s: 10, m: 10, l: 10}}
    request_quantity = fields.Char("Request Count Details")

    # Image: all image fields are base64 encoded and PIL-supported
    image_variant = fields.Binary(
        "Variant Image", attachment=True,
        help="This field holds the image used as image for the product variant, limited to 1024x1024px.")

    # Product viewport transform
    product_vp_transform = fields.Char("Product Viewport Transform")

    # Surcharge List
    surcharge_ids = fields.Many2many('emb_base.decoration_service_surcharge', 'sale_order_line_service_surcharge_rel',
                                     "order_line_id", "decoration_service_surcharge_id", string="Surcharge List", help="List Of Service Surcharges")
    # Surcharge quntity
    surcharge_quantity = fields.Integer("Surcharge Quantity")

    # Save order raw json data
    raw_data = fields.Char("Raw Data")

    # Description
    description = fields.Char("Description")

    # Cached field / Related field
    broker_product_brand = fields.Char(
        related='product_id.product_brand', store=False)

    # Cached field / Related field
    broker_product_style = fields.Char(
        related='product_id.product_uniq_id', store=False)

    # Cached field / Broker field
    broker_product_picture = fields.Binary(
        related='product_id.image_small', store=False)

    # Cached field / Broker field
    broker_product_location = fields.Char(
        related='product_id.product_location', store=False)

    # Cached field / Broker field
    broker_product_package = fields.Char(
        related='product_id.product_package', store=False)

    # Compute logo service UIDs
    logo_uids = fields.Char(compute="_compute_logo_uids", store=False)

    @api.one
    def _compute_logo_uids(self):
        logo_uids = []
        for record in self:
            user_logos = record.logo_ids
            logo_uids = [o.logo_uid for o in user_logos]
        if len(logo_uids) > 0:
            self.logo_uids = '<br />'.join(logo_uids)
        else:
            self.logo_uids = ''
