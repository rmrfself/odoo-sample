# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api, tools, fields
from odoo.exceptions import UserError
import base64
import tempfile
import md5
import os
from subprocess import call
import shutil
import uuid
import random


class ResLogo(models.Model):
    _name = 'emb_base.res_logo'

    # Category ID
    category_id = fields.Selection([
        ('0', 'Tajima Dst File'), ('1', 'Adobe Illustrator File')], "Binary Type",
        required=True)

    # File Name
    file_name = fields.Char('File Name')

    # Image Width
    image_width = fields.Char('Image Width')

    # Image Height
    image_height = fields.Char('Image Height')

    # File Size
    size_unit = fields.Selection([
        ('inch', 'inch'), ('mm', 'mm')], "Size Unit",
        required=True)

    # Binary File
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used for this provider, limited to 1024x1024px")

    # Website Used Binary File
    svg_image = fields.Binary(
        'Website Image', compute="_transform_image", store=True, attachment=True)

    # Unique ID
    design_uniq_id = fields.Char(
        compute='_compute_logo_uid', string='Design#', store=True)

    @api.one
    def _compute_logo_uid(self):
        uniq_num = str(uuid.uuid4().fields[-1])[:6]
        self.design_uniq_id = random.choice("WE") + uniq_num

    @api.depends('image', 'category_id')
    def _transform_image(self):
        for record in self:
            if record.image:
                if record.category_id == '0':
                    # Create dst file image
                    dst_file, dst_filename = tempfile.mkstemp()
                    os.write(dst_file, base64.b64decode(record.image))
                    shutil.copy(dst_filename, dst_filename + '.dst')
                    new_dst_file = dst_filename + '.dst'
                    # Create website used image
                    svg_dir = tempfile.mkdtemp()
                    svg_filename = md5.new(record.image).hexdigest()
                    svg_file = svg_dir + '/' + svg_filename + '.svg'
                    # Image converter call
                    call(["libembroidery-convert", new_dst_file, svg_file])
                    svg_content = open(svg_file, 'r').read()
                    record.svg_image = base64.b64encode(svg_content)
                if record.category_id == '1':
                    # Create dst file image
                    ai_file, ai_filename = tempfile.mkstemp()
                    os.write(ai_file, base64.b64decode(record.image))
                    shutil.copy(ai_filename, ai_filename + '.ai')
                    new_ai_file = ai_filename + '.ai'
                    # create svg file image
                    svg_dir = tempfile.mkdtemp()
                    svg_filename = md5.new(record.image).hexdigest()
                    svg_file = svg_dir + '/' + svg_filename + '.svg'
                    # image converter call
                    call(["pdftocairo", new_ai_file, "-svg", svg_file])
                    svg_content = open(svg_file, 'r').read()
                    record.svg_image = base64.b64encode(svg_content)
            else:
                record.svg_image = False

    @api.model
    def get_all(self):
        return self.search_read([], ['category_id', 'image_width', 'image_height', 'file_name'], order='create_date DESC')

    @api.multi
    def get_logo_categories(self):
        result = []
        return result.extend([('0', 'Tajima Dst File'), ('1', 'Adobe Illustrator File')])
