# -*- coding: utf-8 -*-
from openerp import http

# class Routes(http.Controller):
#     @http.route('/routes/routes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/routes/routes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('routes.listing', {
#             'root': '/routes/routes',
#             'objects': http.request.env['routes.routes'].search([]),
#         })

#     @http.route('/routes/routes/objects/<model("routes.routes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('routes.object', {
#             'object': obj
#         })