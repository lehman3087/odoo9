# -*- coding: utf-8 -*-
from openerp import http

# class Jewelry(http.Controller):
#     @http.route('/jewelry/jewelry/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jewelry/jewelry/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jewelry.listing', {
#             'root': '/jewelry/jewelry',
#             'objects': http.request.env['jewelry.jewelry'].search([]),
#         })

#     @http.route('/jewelry/jewelry/objects/<model("jewelry.jewelry"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jewelry.object', {
#             'object': obj
#         })