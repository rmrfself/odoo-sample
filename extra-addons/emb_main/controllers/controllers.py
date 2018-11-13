# -*- coding: utf-8 -*-
from odoo import http

# class EmbMain(http.Controller):
#     @http.route('/emb_main/emb_main/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/emb_main/emb_main/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('emb_main.listing', {
#             'root': '/emb_main/emb_main',
#             'objects': http.request.env['emb_main.emb_main'].search([]),
#         })

#     @http.route('/emb_main/emb_main/objects/<model("emb_main.emb_main"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('emb_main.object', {
#             'object': obj
#         })