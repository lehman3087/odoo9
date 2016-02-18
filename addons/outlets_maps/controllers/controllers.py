# -*- coding: utf-8 -*-
from openerp import http

# class OutletsMaps(http.Controller):
#     @http.route('/outlets_maps/outlets_maps/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/outlets_maps/outlets_maps/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('outlets_maps.listing', {
#             'root': '/outlets_maps/outlets_maps',
#             'objects': http.request.env['outlets_maps.outlets_maps'].search([]),
#         })

#     @http.route('/outlets_maps/outlets_maps/objects/<model("outlets_maps.outlets_maps"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('outlets_maps.object', {
#             'object': obj
#         })