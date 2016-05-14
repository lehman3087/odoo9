# -*- coding: utf-8 -*-
from openerp import http

# class Sift(http.Controller):
#     @http.route('/sift/sift/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sift/sift/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sift.listing', {
#             'root': '/sift/sift',
#             'objects': http.request.env['sift.sift'].search([]),
#         })

#     @http.route('/sift/sift/objects/<model("sift.sift"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sift.object', {
#             'object': obj
#         })