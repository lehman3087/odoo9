# -*- coding: utf-8 -*-
from openerp import http

# class OutletsMaps2(http.Controller):
#     @http.route('/outlets_maps2/outlets_maps2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outlets_maps2/outlets_maps2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outlets_maps2.listing', {
#             'root': '/outlets_maps2/outlets_maps2',
#             'objects': http.request.env['outlets_maps2.outlets_maps2'].search([]),
#         })

#     @http.route('/outlets_maps2/outlets_maps2/objects/<model("outlets_maps2.outlets_maps2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outlets_maps2.object', {
#             'object': obj
#         })