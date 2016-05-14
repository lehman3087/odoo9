# -*- coding: utf-8 -*-
from openerp import http

class Logistics(http.Controller):
    @http.route('/logistics/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/logistics/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('logistics.listing', {
            'root': '/logistics/logistics',
            'objects': http.request.env['logistics.logistics'].search([]),
        })

    @http.route('/logistics/objects/<model("logistics.logistics"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('logistics.object', {
            'object': obj
        })


    @http.route('/logistics/camera/', auth='public')
    def camera(self,**kw):
        return http.request.render('logistics.camera_asset', {

        })