# -*- coding: utf-8 -*-
from openerp import http

# class Trafic(http.Controller):
#     @http.route('/trafic/trafic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/trafic/trafic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('trafic.listing', {
#             'root': '/trafic/trafic',
#             'objects': http.request.env['trafic.trafic'].search([]),
#         })

#     @http.route('/trafic/trafic/objects/<model("trafic.trafic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('trafic.object', {
#             'object': obj
#         })