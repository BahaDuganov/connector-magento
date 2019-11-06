# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class WizardModel(models.TransientModel):
    _inherit = "connector_magento.add_backend.wizard"

    @api.multi
    def get_default_products(self):
        return self.get_default_object('product.product')

    @api.multi
    def get_default_product_templates(self):
        return self.get_default_object('product.template')

    @api.multi
    def get_default_category(self):
        return self.get_default_object('product.category')

    @api.multi
    def _get_ids_and_model(self):
        active_model = self.env.context.get('active_model', False)
        if active_model == 'product.template':
            return (self.temp_export_ids, 'magento.product.template')
        elif active_model == 'product.product':
            return (self.to_export_ids, 'magento.product.product')
        elif active_model == 'product.category':
            return (self.categ_to_export_ids, 'magento.product.category')
        else:
            return super(WizardModel, self)._get_ids_and_model()

    @api.multi
    def check_backend_binding(self, to_export_ids=None, dest_model=None):
        if not dest_model or not to_export_ids:
            (to_export_ids, dest_model) = self._get_ids_and_model()
        if dest_model == 'magento.product.template':
            for template in to_export_ids:
                if template.product_variant_count > 1:
                    dest_model = 'magento.product.template'
                    model = template
                else:
                    dest_model = 'magento.product.product'
                    model = template.product_variant_ids[0]
                bind_count = self.env[dest_model].search_count([
                    ('odoo_id', '=', model.id),
                    ('backend_id', '=', self.backend_id.id)
                ])
                if not bind_count:
                    vals = {
                        'odoo_id': model.id,
                        'backend_id': self.backend_id.id
                    }
                    self.env[dest_model].create(vals)
            return
        return super(WizardModel, self).check_backend_binding(to_export_ids, dest_model)

    model = fields.Selection(selection_add=[
        ('product.template', _(u'Product templates')),
        ('product.product', _(u'Product')),
        ('product.category', _(u'Product category')),
    ], string='Model')
    to_export_ids = fields.Many2many(string='Products to export',
                                     comodel_name='product.product', default=get_default_products)
    temp_export_ids = fields.Many2many(string='Product Templates to export',
                                       comodel_name='product.template', default=get_default_product_templates)

    categ_to_export_ids = fields.Many2many(string='Category To export',
                                           comodel_name='product.category', default=get_default_category)
