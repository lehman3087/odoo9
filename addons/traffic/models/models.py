# -*- coding: utf-8 -*-

from openerp import models, fields, api

class traffic(models.Model):
    _name = 'traffic.traffic'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100



class position(models.Model):
    _name = 'traffic.position'

    lat=fields.Float(String=u"纬度",digits=(16,4))
    lt2=fields.Selection([
        ('N','N'),
        ('S','S'),
        ('W','W'),
        ('E','E')
    ])
    lon=fields.Float(String=u"经度",digits=(16,4))
    in2=fields.Selection([
        ('N','N'),
        ('S','S'),
        ('W','W'),
        ('E','E')
    ])
    altitude=fields.Float(String=u"海拔",digits=(16,4))
    angle=fields.Float(String=u"角度",digits=(16,4))
