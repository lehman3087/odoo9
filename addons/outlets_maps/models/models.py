# -*- coding: utf-8 -*-

from openerp import models, fields, api

class outlets_maps(models.Model):
    _name = 'outlets_maps.outlets_maps'

    name=fields.Char(string='请填写门店名称')
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100


