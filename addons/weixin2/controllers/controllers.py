# -*- coding: utf-8 -*-
from openerp import http



# class Weixin2(http.Controller):
#     @http.route('/weixin2/weixin2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/weixin2/weixin2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('weixin2.listing', {
#             'root': '/weixin2/weixin2',
#             'objects': http.request.env['weixin2.weixin2'].search([]),
#         })

#     @http.route('/weixin2/weixin2/objects/<model("weixin2.weixin2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('weixin2.object', {
#             'object': obj
#         })