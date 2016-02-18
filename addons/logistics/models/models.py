# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class logistics(models.Model):
#     _name = 'logistics.logistics'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


# class routes(models.Model):
#     _name = 'logistics.routes'
#
#     name = fields.Char()
#     car = fields.Many2one(comodel_name='fleet.vehicle.model')
#     # orgin = fields.One2many('res.partner.address', 'partner_id', 'Contacts')
#     #des_city=fields.Char(related='f.city',string='City',store=True)
#     #des_county=fields.Char(related="address.country_id", string='County',store=True)
#     # des_longitude=fields.Float()
#     # des_latitude=fields.Float()
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
#
#
# class comprise(models.Model):
#     _name='logistics.comprise'
#
#     name = fields.Char(string="包裹内容")
#
# class package(models.Model):
#     _name = 'logistics.package'
#
#     # orgin = fields.Many2one(comodel_name='res.partner.address')
#     car = fields.Many2one(comodel_name='fleet.vehicle.model')
#     comprise=fields.One2many("logistics.comprise")