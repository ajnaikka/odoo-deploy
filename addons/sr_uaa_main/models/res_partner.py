from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('child_ids','child_ids.active_check')
    def get_active_child_partner(self):
        for rec in self:
            active_child_id = False
            for child_id in rec.child_ids:
                if child_id.active_check:
                    active_child_id = child_id.id
            rec.active_child_id = active_child_id

    account_type = fields.Selection([('agent', 'Agent'),
                                     ('privilege_customer','Privilege Customer')],
                                    string='Customer Type')
    emergency_number = fields.Char('Emergency Contact')
    active_check = fields.Boolean('Active', default=False)
    active_child_id = fields.Many2one('res.partner', 'Active Address',compute="get_active_child_partner", store=True)
    passport_number = fields.Char('Passport Number')
    passport_expiry_date = fields.Date('Passport Expiry Date')
    is_passport_expired = fields.Boolean(compute='_compute_is_expired',string='Is Passport Expired?')

    @api.model
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        if res.active_check:
            if res.parent_id:
                child_records = res.parent_id.child_ids
                for child in child_records:
                    if child != res:
                        child.active_check = False
        return res

    @api.depends('passport_expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for partner in self:
            partner.is_passport_expired = partner.passport_expiry_date and partner.passport_expiry_date < today

    def write(self, vals):
        if vals.get('active_check', False):
            if vals.get('parent_id', False) or self.parent_id:
                if vals.get('parent_id', False):
                    parent = self.env['res.partner'].sudo().browse(vals.get('parent_id', False))
                else:
                    parent = self.parent_id
                if parent:
                    child_records = parent.child_ids
                    for child in child_records:
                        if child != self.id:
                            child.active_check = False
        params = vals.keys()
        if 'name' in params or 'active' in params:
            for record in self:
                new_name = vals.get('name', '')
                old_name = record.name
                
                if new_name:
                    name_msg = "Name is changed " + old_name + " -> " + new_name
                    record.message_post(body=name_msg)
                if 'active' in params:
                    active_msg = "Active is set to "+ str(vals.get('active'))
                    record.message_post(body=active_msg)
                    
        res = super(ResPartner, self).write(vals)
        
        return res

    def button_attachment(self):
        for record in self:
            return {
                'name': _('Attachments'),
                'domain': [('res_model', '=', self._name),
                           ('res_id', '=', record.id)],
                'res_model': 'ir.attachment',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                'help': _('''<p class="oe_view_nocontent_create">

                                                            Attach your personal
                        documents.</p>'''),
                'limit': 80,
                'context': "{'default_res_model': '%s', 'default_res_id': %d}"
                           % (self._name, record.id)
            }
