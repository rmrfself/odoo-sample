# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.tools import config
import base64
import tempfile
import md5
import os
from subprocess import call
import shutil
import json
import hashlib

from odoo.exceptions import AccessError, UserError
import logging
_logger = logging.getLogger(__name__)

from odoo.http import request


def compare_lists(list1, list2):
    if len(list1) != len(list2):  # Weed out unequal length lists.
        return False
    for item in list1:
        if item not in list2:
            return False
    return True


class Portal(http.Controller):
    @http.route('/portal/index/', auth='user', website=True)
    def index(self, **kw):
        return http.request.render('emb_portal.portal_layout')

    @http.route('/portal/cart', auth='user', website=True)
    def cartList(self, **kw):
        return http.request.render('emb_portal.cart_list')

    @http.route('/portal/load_cart_list', auth='user', type="json")
    def loadCartList(self, **kw):
        sale_order_id = request.session.get('sale_last_order_id')
        order_lines = []
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            order_lines = request.env['sale.order.line'].search_read(
                [("order_id", "=", int(sale_order_id))], ['logo_ids', 'product_sbu', 'product_color', 'service_surcharge_ids', 'service_surcharge_quantity', 'unit_price', 'discount'])
        return order_lines

    @http.route('/portal/logo_list', type="json", auth='user')
    def logoList(self, **kw):
        return http.request.env['emb_base.res_logo'].get_all()

    @http.route('/portal/get_logo', type="json", auth='user')
    def getLogo(self, **kw):
        logo_id = kw.get("logo_id", '')
        logo = http.request.env['emb_base.res_logo'].browse(int(logo_id))
        img_data = base64.b64decode(logo.svg_image)
        return {'data': img_data}

    @http.route('/portal/product_list', type="json", auth='user')
    def garmentList(self, **kw):
        categoryId = kw.get("category_id", [])
        return http.request.env['product.template'].search_read([("public_categ_ids", "in", (int(categoryId)))])

    @http.route('/portal/get_service_surcharges', type="json", auth='user')
    def getServiceSurcharges(self, **kw):
        categoryId = kw.get("cid", [])
        return http.request.env['emb_base.decoration_service_surcharge'].search_read([("category_id", "=", (int(categoryId)))])

    @http.route('/portal/get_decoration_services', type="json", auth='user')
    def getDecorationServices(self, **kw):
        return http.request.env['decoration.service.category'].search_read([])

    @http.route('/portal/get_product_sizes', type="json", auth='user')
    def getProductSizes(self, **kw):
        pid = kw.get("product_id", '')
        product_attr_line = http.request.env['product.attribute.line'].search_read(
            [("product_tmpl_id", "=", int(pid)), ("attribute_id", "=", 6)], ["value_ids"], limit=1)
        if product_attr_line and len(product_attr_line) > 0:
            line_ids = product_attr_line[0][
                'value_ids'
            ]
            attr_values = http.request.env['product.attribute.value'].search_read(
                [("id", "in", line_ids)])
            return attr_values
        return []

    @http.route('/portal/get_product_colors', type="json", auth='user')
    def getProductColors(self, **kw):
        pid = kw.get("product_id", '')
        product_attr_line = http.request.env['product.attribute.line'].search_read(
            [("product_tmpl_id", "=", int(pid)), ("attribute_id", "=", 5)], ["value_ids"], limit=1)
        if product_attr_line and len(product_attr_line) > 0:
            line_ids = product_attr_line[0][
                'value_ids'
            ]
            attr_values = http.request.env['product.attribute.value'].search_read(
                [("id", "in", line_ids)])
            return attr_values
        return []

    @http.route('/portal/get_product_types', type="json", auth='user')
    def getProductTypes(self, **kw):
        return http.request.env['product.public.category'].search_read([])

    @http.route('/portal/get_sale_line', type="json", auth='user')
    def getSaleLine(self, **kw):
        id = kw.get("id", '')
        SaleOrderLine = request.env['sale.order.line']
        sale_line_id = SaleOrderLine.browse(int(id))
        sale_line_rawdata = sale_line_id.raw_data
        return sale_line_rawdata

    @http.route('/portal/remove_sale_line', type="json", auth='user')
    def removeSaleLine(self, **kw):
        old_sale_line_id = kw.get("id", '')
        SaleOrderLine = request.env['sale.order.line']
        result = SaleOrderLine.search(
            [('id', '=', int(old_sale_line_id))]).unlink()
        return result

    @http.route('/emb_portal/res_logo/image/<id>', type='http', auth="public", website=False, multilang=False)
    def content_image(self, id=None, **kw):
        ResLogo = request.env['emb_base.res_logo'].browse(int(id))
        headers = []
        image_base64 = base64.b64decode(ResLogo.svg_image)
        headers.append(('Content-Length', len(image_base64)))
        headers.append(('Content-Type', 'image/svg+xml'))
        response = request.make_response(image_base64, headers)
        response.status_code = 200
        return response

    @http.route(['/portal/upload_logo/dst'], type='json', auth='user', methods=['POST'], website=True)
    def upload_logo_dst(self, *args, **post):
        # Create dst file image
        values = dict((fname, post[fname]) for fname in [
            'file_name', 'image_height', 'image_width', 'size_unit', 'image', 'website_published'] if post.get(fname))
        if post.get('category_id'):
            values['category_id'] = str(post['category_id'][0])
        # handle exception during creation of slide and sent error notification to the client
        # otherwise client slide create dialog box continue processing even server fail to create a slide.
        try:
            logo_id = request.env['emb_base.res_logo'].create(values)
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        except Exception as e:
            _logger.error(e)
            return {'error': _('Internal server error, please try again later or contact administrator.\nHere is the error message: %s') % e.message}
        return {'url': "/portal/index/"}

    @http.route(['/portal/upload_logo/ai'], type='json', auth='user', methods=['POST'], website=True)
    def upload_logo_ai(self, *args, **post):
        values = dict((fname, post[fname]) for fname in [
            'file_name', 'image_height', 'image_width', 'size_unit', 'image', 'website_published'] if post.get(fname))

        if post.get('category_id'):
            values['category_id'] = str(post['category_id'][0])
        # handle exception during creation of slide and sent error notification to the client
        # otherwise client slide create dialog box continue processing even server fail to create a slide.
        try:
            logo_id = request.env['emb_base.res_logo'].create(values)
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        except Exception as e:
            _logger.error(e)
            return {'error': _('Internal server error, please try again later or contact administrator.\nHere is the error message: %s') % e.message}
        return {'url': "/portal/index/"}

    @http.route(['/portal/upload_product'], type='json', auth='user', methods=['POST'], website=True)
    def upload_product(self, *args, **post):
        # Set unit of meature to be unit.
        Product = request.env['product.product']
        ProductTemplate = request.env['product.template']
        Uom = request.env['product.uom']

        # Product attributes
        uom_unit = request.env.ref('product.product_uom_unit')

        # Product attributes
        product_template_vals = {}
        # Product category
        category_id = post['category_id'][0]
        image_raw_data = post['image']
        if image_raw_data:
            product_template_vals['image'] = image_raw_data
        if not category_id:
            return {'error': 'category can not be empty'}
        product_template_vals['public_categ_ids'] = [int(category_id)]
        # Size Attr
        size_attr = request.env['product.attribute'].search(
            [('name', '=', 'European Size')], limit=1)
        size_attr_val_ids = size_attr.value_ids.ids

        # Color attr
        color_attr = request.env['product.attribute'].search(
            [('name', '=', 'Color')], limit=1)
        colors_data = post['colors']
        # Check the colors fields
        color_attr_val_ids = False
        if colors_data:
            for color in colors_data:
                color_count = request.env['product.attribute.value'].search_count(
                    [('name', '=', color), ('attribute_id', '=', color_attr.id)])
                if color_count == 0:
                    request.env['product.attribute.value'].create(
                        {'name': color, 'attribute_id': color_attr.id})
            color_attr_val_ids = request.env['product.attribute.value'].search(
                [('name', 'in', colors_data)]).ids

        # Product template
        attribute_line_ids_domain = []
        if len(size_attr_val_ids) > 0:
            attribute_line_ids_domain = [(0, 0, {
                'attribute_id': size_attr.id,
                'value_ids': [(4, size_attr_val_ids)],
            })]
        if color_attr_val_ids and len(color_attr_val_ids) > 0:
            attribute_line_ids_domain = attribute_line_ids_domain + [(0, 0, {
                'attribute_id': color_attr.id,
                'value_ids': [(4, color_attr_val_ids)],
            })]
        # Create product template
        product = Product.sudo().create({
            'image': image_raw_data,
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id,
            'website_published': True,
            'public_categ_ids': [(4, int(category_id))],
            'attribute_line_ids': attribute_line_ids_domain
        })
        return {'url': "/portal/index/"}

    @http.route(['/portal/add_to_cart'], type='json', auth='user', methods=['POST'], website=True)
    def add_to_cart(self, *args, **post):
        # Sales order
        SaleOrder = request.env['sale.order']
        SaleOrderLine = request.env['sale.order.line']
        partner_id = request.env.user.partner_id
        product_id = post['product']['id']
        product_color = post['product']['color']
        product_vpt = post['product']['viewportTransform']
        product_count = post['product']['count']
        image = post['screenImage'].replace('data:image/png;base64,', '')
        service_surcharge_ids = []
        service_surcharge_qty = 0
        if 'surcharges' in post['service']:
            service_surcharge_ids = post['service']['surcharges']
            service_surcharge_qty = post['service']['surcharges_count']
        # 解码用户上传数据
        user_logos = json.loads(post['logos']['data'])
        sale_order_id = request.session.get('sale_last_order_id')
        raw_post_data = post.copy()
        raw_post_data.pop('screenImage', None)
        # 监测是否存在旧的订单ID
        old_sale_line_id = None
        if 'sale_line' in post and len(post['sale_line']['id']) > 0:
            old_sale_line_id = post['sale_line']['id'][0]
        # Set user logos
        user_logo = False
        uploaded_logos = []
        for key, value in user_logos.iteritems():
            # 判断logo是否曾经上传过
            searched_logo = False
            if 'paths' in value:
                logo_id = value['resourceId']
                emb_lines = json.dumps(value['paths'])
                key_secret = "%s" % logo_id + emb_lines
                hashlib_md5 = hashlib.md5()
                hashlib_md5.update(key_secret.encode('utf-8'))
                logo_key = hashlib_md5.hexdigest()
                searched_logo = request.env['emb_base.user_logo'].search(
                    [('logo_key', '=', logo_key)])
            # 判断条件: 如果存在相同的logo ， 则使用以前design的logo
            if searched_logo:
                uploaded_logos.append(searched_logo[0])
            else:
                # 如果logo不存在， 则创建一个新的
                # 编码位置信息:
                pos_dict = {}
                pos_dict['x'] = value['left']
                pos_dict['y'] = value['top']
                # Compute postion information: TOPLEFT, TOPRIGHT, BOTTOMLEFT, BOTTOMRIGHT
                position_info = json.dumps(pos_dict)
                user_logo = request.env['emb_base.user_logo'].create({
                    'logo_id': int(value['resourceId']),
                    'cid': int(value['cid']),
                    'position_info': position_info,
                    'emb_lines': json.dumps(value['paths']) if 'paths' in value else value['fill'],
                    'svgUid': value['svgUid']
                })
                uploaded_logos.append(user_logo)
        # 简单的校验
        if len(uploaded_logos) == 0:
            return False
        # 保存上传过的logo信息[key][id]
        uploaded_logo_keys = []
        uploaded_logo_ids = []
        for ul in uploaded_logos:
            logo_key = ul.logo_key
            uploaded_logo_keys.append(logo_key)
            uploaded_logo_ids.append(ul.id)
        print(uploaded_logo_ids)
        # 如果是编辑模式，直接解除
        if old_sale_line_id:
            # 这里应该判断 用户是否真的编辑过logo的信息【判断路径的颜色是否编辑过】
            SaleOrderLine.search([('id', '=', int(old_sale_line_id))]).unlink()
        if sale_order_id:
            # 取到订单对象
            sale_order = SaleOrder.browse(sale_order_id)
            order_lines = sale_order.order_line
            searched_order_line = False
            # 查找当前订单下，是否存在 garmart、 logo、和着色信息完全一样的订单
            # 如果存在这样的订单， 不再创建， 直接更新下单的数量信息
            for ol in order_lines:
                ol_product_id = ol.product_id
                exist_logos = ol.logo_ids
                logo_ids = []
                for el in exist_logos:
                    logo_ids.append(el.logo_key)
                checked_result = compare_lists(logo_ids, uploaded_logo_keys)
                if checked_result and ol_product_id.id == int(product_id):
                    searched_order_line = ol
                    break
            # 如果存在完全一样的订单，直接更新相关字段
            if searched_order_line:
                request_quantity_data = searched_order_line.request_quantity
                if request_quantity_data:
                    request_quantity_list = json.loads(request_quantity_data)
                    checked_contains = False
                    # 如果是完全一样的订单， 仅仅是数量发生了变化，则直接更新数量
                    for rql in request_quantity_list:
                        rql_color = rql['color']
                        rql_size = rql['size']
                        if rql_color == product_color:
                            rql_size.append(json.loads(product_count))
                            checked_contains = True
                    # 如果是完全一样的订单，但是garment的颜色发生了变化，则追加新的颜色信息和数量信息
                    if not checked_contains:
                        request_quantity_dict = {}
                        request_quantity_dict['color'] = product_color
                        request_quantity_dict['size'] = [
                            json.loads(product_count)]
                        request_quantity_list.append(request_quantity_dict)
                    # 重新编码更新后的列表信息
                    quantity_encoded_data = json.dumps(request_quantity_list)
                    # 保存找到的订单项
                    searched_order_line.write(
                        {"request_quantity": quantity_encoded_data})
                    order_line = searched_order_line
            else:
                # 如果没找到完全一样的订单， 则创建一个新的订单项目
                # 编码颜色和数量信息
                request_quantity_dict = {}
                request_quantity_dict['color'] = product_color
                request_quantity_dict['size'] = [json.loads(product_count)]
                request_quantity = json.dumps([request_quantity_dict])
                #  创建信息的订单项目
                #  (6, 0, uploaded_logo_ids), 关联已经创建的logo
                order_line = SaleOrderLine.create({
                    'order_id': sale_order_id,
                    'name': 'Order Line',
                    'logo_ids': [(6, 0, uploaded_logo_ids)],
                    'product_id': int(product_id),
                    'request_quantity': request_quantity,
                    'product_vp_transform': product_vpt,
                    'product_uom_qty': 1,
                    'product_uom': request.env.ref('product.product_uom_unit').id,
                    'image_variant': image,
                    'surcharge_ids': [(4, r) for r in map(int, service_surcharge_ids)],
                    'surcharge_quantity': int(service_surcharge_qty),
                    'price_unit': 0
                })
        else:
            # 如果连订单也不存在， 则全部创建新记录
            # 编码数量和颜色信息
            request_quantity_dict = {}
            request_quantity_dict['color'] = product_color
            request_quantity_dict['size'] = [json.loads(product_count)]
            request_quantity = json.dumps([request_quantity_dict])
            # 开始创建
            sale_order = SaleOrder.create({
                'partner_id': partner_id.id,
                'partner_invoice_id': partner_id.id,
                'partner_shipping_id': partner_id.id,
                'order_line': [(0, 0, {
                    'name': 'Order Line',
                    'logo_ids': (6, 0, uploaded_logo_ids),
                    'product_id': int(product_id),
                    'request_quantity': request_quantity,
                    'product_vp_transform': product_vpt,
                    'product_uom_qty': 1,
                    'product_uom': request.env.ref('product.product_uom_unit').id,
                    'image_variant': image,
                    'surcharge_ids': [(4, r) for r in map(int, service_surcharge_ids)],
                    'surcharge_quantity': int(service_surcharge_qty),
                    'price_unit': 0
                })]
            })
            order_line = sale_order.order_line[0]
            request.session['sale_last_order_id'] = sale_order.id
        return {'sale_order_line_id': order_line.id}
