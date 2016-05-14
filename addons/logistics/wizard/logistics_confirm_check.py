# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class LgConfirmCheckWizard(models.TransientModel):

    _name = "logistics.confirm.check.wizard"
    _description = "Check receive verify code wizard"

    code = fields.Char(string='Code', required=True)

    @api.multi
    def package_check(self):
        self.ensure_one()

        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        package = self.env['logistics.package'].browse(active_ids)
        if  package.check_code(self.code):
            return {'type': 'ir.actions.act_window_close'}
        # package.check_code(self.code)

