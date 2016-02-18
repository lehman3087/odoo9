# -*- coding: utf-8 -*-

from openerp import models, fields, api

class routes(models.Model):
    _name = 'routes.routes'

    name = fields.Char()
    car = fields.Many2one(comodel_name='fleet.vehicle.model')
    orgin = fields.one2many('res.partner.address', 'partner_id', 'Contacts')
    des_city=fields.related('address','city',type='char', string='City')
    des_country=fields.related('address','country_id',type='many2one', relation='res.country', string='Country')
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100



