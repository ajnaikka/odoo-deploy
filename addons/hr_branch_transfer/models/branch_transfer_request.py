# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class BranchStockTransferRequest(models.Model):
    _name = 'branch.stock.transfer.request'
    _description = "Branch Stock Transfer Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Contact",
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    request_date = fields.Datetime(
        string="Requested Date",
        default=lambda self: fields.Datetime.now(),
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}, tracking=True
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string="Operation Type",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    location_id = fields.Many2one(
        'stock.location',
        string="Source Location",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string="Destination Location",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        store=True,
        change_default=True,
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    created_user_id = fields.Many2one(
        'res.users',
        string="Created By",
        readonly=True,
        default=lambda self: self.env.user,
        copy=False, tracking=True
    )
    hq_admin_id = fields.Many2one(
        'res.users',
        string="Approved/ Rejected By",
        readonly=True,
        copy=False, tracking=True
    )
    processed_user_id = fields.Many2one(
        'res.users',
        string="Processed By",
        readonly=True,
        copy=False, tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        ('processed', 'Processed'),
        ('done', 'Received'),
        ('cancel', 'Cancelled')],
        default='draft',
        string="Status",
        copy=False, tracking=True,
    )
    branch_stock_transfer_request_line_ids = fields.One2many(
        'branch.stock.transfer.request.line',
        'branch_stock_transfer_request_id',
        string="Request Lines",
        readonly=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )
    note = fields.Text(
        string="Notes",
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)], 'to_approve': [('readonly', False)]}
    )

    @api.model
    def default_get(self, default_fields):
        res = super(BranchStockTransferRequest, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id': self.env.user.branch_id.id or False
            })
        return res

    branch_id = fields.Many2one('res.branch', string="Branch", readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError(
                    "Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        for rec in self:
            rec.location_dest_id = rec.picking_type_id.default_location_dest_id.id

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group('hr_user_group.hr_group_branch_user'):
            raise AccessError(_("You don't have the access rights to create branch Transfer."))
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('branch.stock.transfer.request')
        return super(BranchStockTransferRequest, self).create(vals_list)

    def action_cancel(self):
        for rec in self:
            picking = self.env['stock.picking'].sudo().search([('branch_stock_transfer_request_id', '=', rec.id)])
            if picking:
                if picking.state == 'done':
                    stock_return_picking = self.env['stock.return.picking'].sudo().create({'picking_id': picking.id})
                    stock_return_picking.sudo()._onchange_picking_id()
                    return_picking = stock_return_picking.sudo().create_returns()
                    rec.state = 'cancel'
                    return return_picking
                else:
                    picking.sudo().action_cancel()
                    rec.state = 'cancel'
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            if (self.env.su or self.env.user.has_group('hr_user_group.hr_group_hq_admin') or
                    self.env.user.branch_id == rec.branch_id):
                rec.state = 'draft'
            else:
                raise AccessError(_("You don't have the access rights to set this request to draft stage."))

    def rejected_by_admin(self):
        for record in self:
            partners = [record.created_user_id.partner_id.id]
            body = _(u'' + self.env.user.name + ' Rejected The branch transfer ' + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="branch.stock.transfer.request">@' + record.name + '</a>. Please Check')
            record.message_post(body=body, partner_ids=partners)
            record.state = 'reject'
            record.hq_admin_id = self.env.user.id

    def send_for_hq_admin_approval(self):
        for record in self:
            if self.env.user.branch_id == record.branch_id:
                hq_admin = self.env.ref('hr_user_group.hr_group_hq_admin').users
                partners = []
                for user in hq_admin:
                    partners.append(user.partner_id.id)
                message = "Branch Transfer Request created " + '<a href="#" data-oe-id=' + str(
                    record.id) + ' data-oe-model="branch.stock.transfer.request">@' + record.name + '</a>. Please Verify and Confirm'
                record.message_post(body=message, partner_ids=partners)
                record.state = 'to_approve'
            else:
                raise AccessError(_("You don't have the permission. This request belongs to another branch"))

    def action_approved_by_admin(self):
        for record in self:
            picking_data = {
                'partner_id': record.partner_id.id,
                'picking_type_id': record.picking_type_id.id,
                'location_id': record.location_id.id,
                'location_dest_id': record.location_dest_id.id,
                'scheduled_date': record.request_date,
                'branch_stock_transfer_request_id': record.id,
                'origin': record.name,
            }
            line_vals = []
            for line in self.branch_stock_transfer_request_line_ids:
                line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.approved_qty,
                    'product_uom': line.product_uom.id,
                    'description_picking': line.description,
                    'name': line.description,
                    'company_id': line.company_id.id,
                    'picking_type_id': line.branch_stock_transfer_request_id.picking_type_id.id,
                    'location_id': line.branch_stock_transfer_request_id.location_id.id,
                    'location_dest_id': line.branch_stock_transfer_request_id.location_dest_id.id,
                }))
            if line_vals:
                picking_data.update({
                    'move_ids_without_package': line_vals
                })
            self.env['stock.picking'].sudo().create(picking_data)
            record.state = 'approved'
            record.hq_admin_id = self.env.user.id
            partners = [record.created_user_id.partner_id.id]
            body = _(u'' + self.env.user.name + ' Approved The Branch Transfer Request ' + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="branch.stock.transfer.request">@' + record.name + '</a>. Please Check')
            record.message_post(body=body, partner_ids=partners)
            supply_users = self.env.ref('stock.group_stock_user').users.filtered(lambda l: l.branch_id == record.location_id.transfer_request_branch_id)
            supply_partners = [user.partner_id.id for user in supply_users]
            body = _(
                u'' + self.env.user.name + ' Approved The Branch Transfer Request ' + '<a href="#" data-oe-id=' + str(
                    record.id) + ' data-oe-model="branch.stock.transfer.request">@' + record.name + '</a> Created By' + record.created_user_id.name + '. Please Process The Order')
            record.message_post(body=body, partner_ids=supply_partners)

    def action_process_request_by_supplier(self):
        for record in self:
            if self.env.user.branch_id == record.location_id.transfer_request_branch_id:
                picking = self.env['stock.picking'].sudo().search([('branch_stock_transfer_request_id', '=', record.id)])
                if picking.state == 'draft':
                    res = picking.sudo().action_confirm()
                record.state = 'processed'
                record.processed_user_id = self.env.user.id
                partners = [record.created_user_id.partner_id.id]
                body = _(
                    u'' + self.env.user.name + ' Processed The Branch Transfer Request ' + '<a href="#" data-oe-id=' + str(
                        record.id) + ' data-oe-model="branch.stock.transfer.request">@' + record.name + '</a>. Please Check and Confirm')
                record.message_post(body=body, partner_ids=partners)
                return res
            else:
                raise AccessError(_("You don't have the permission. This request belongs to another branch"))

    def action_receive_products(self):
        for record in self:
            if self.env.user.branch_id == record.branch_id:
                picking = self.env['stock.picking'].sudo().search([('branch_stock_transfer_request_id', '=', record.id)])
                if picking.state != 'assigned':
                    picking.sudo().action_assign()
                    if picking.state != 'assigned':
                        raise UserError(
                            _("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                picking.move_ids.sudo()._set_quantities_to_reservation()
                res = picking.sudo().button_validate()
                record.state = 'done'
                return res
            else:
                raise AccessError(_("You don't have the permission. This request belongs to another branch"))

    def show_product_on_hand(self):
        self.ensure_one()
        action = self.env.ref("stock.dashboard_open_quants")
        action = action.sudo().read()[0]
        product_ids = []
        for line in self.branch_stock_transfer_request_line_ids:
            product_ids.append(line.product_id.id)
        action['domain'] = str([('product_id', 'in', product_ids)])
        action['context'] = {
            'search_default_on_hand': 1,
            'search_default_productgroup': 1,
        }
        return action

    def show_transfers_picking(self):
        self.ensure_one()
        action = self.env.ref("stock.action_picking_tree_all")
        action = action.sudo().read()[0]
        action['domain'] = str([('branch_stock_transfer_request_id', '=', self.id)])
        action['context'] = {'default_branch_stock_transfer_request_id': self.id}
        return action

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        for record in self:
            if record.state in ['done']:
                raise UserError(_('You can not delete a request after receiving products.'))
            picking = self.env['stock.picking'].sudo().search([('branch_stock_transfer_request_id', '=', record.id)])
            if picking:
                return picking.sudo().unlink()


class BranchStockTransferRequestLine(models.Model):
    _name = 'branch.stock.transfer.request.line'
    _description = "Branch Stock Transfer Request Line"

    branch_stock_transfer_request_id = fields.Many2one(
        'branch.stock.transfer.request',
        string="Branch Stock Transfer Request",
        copy=False, ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string="UOM",
        required=True
    )
    demand_qty = fields.Float(
        string="Requested Quantity",
        required=True, digits='Product Unit of Measure', readonly=True, states={'draft': [('readonly', False)]}, store=True,
    )
    company_id = fields.Many2one(
        string='Company',
        store=True,
        readonly=True,
        related='branch_stock_transfer_request_id.company_id',
        change_default=True,
        default=lambda self: self.env.company
    )
    approved_qty = fields.Float(string="Approved Quantity", readonly=True, states={'to_approve': [('readonly', False)]},
                                digits='Product Unit of Measure', store=True,)
    destination_onhand_quantity = fields.Float(
        'Destination Onhand Quantity', readonly=True, digits='Product Unit of Measure',
        compute="compute_destination_product_onhand")
    source_onhand_quantity = fields.Float(
        'Source Onhand Quantity', readonly=True, digits='Product Unit of Measure',
        compute="compute_source_product_onhand")
    state = fields.Selection(related="branch_stock_transfer_request_id.state", store=True, readonly=True)

    @api.onchange('product_id')
    def onchange_product(self):
        for rec in self:
            rec.description = rec.product_id.display_name
            rec.product_uom = rec.product_id.uom_id.id

    @api.onchange('demand_qty')
    def onchange_demand_qty(self):
        for rec in self:
            rec.approved_qty = rec.demand_qty

    @api.depends('product_id', 'branch_stock_transfer_request_id.location_dest_id', 'company_id')
    def compute_destination_product_onhand(self):
        for record in self:
            quantity = 0
            if record.product_id and record.branch_stock_transfer_request_id.location_dest_id:
                quants = self.env['stock.quant'].search(
                    [('location_id', '=', record.branch_stock_transfer_request_id.location_dest_id.id),
                     ('product_id', '=', record.product_id.id),
                     ('company_id', '=', record.company_id.id),
                     ('product_uom_id', '=', record.product_uom.id)])
                for quant in quants:
                    quantity += quant.quantity
            record.destination_onhand_quantity = quantity

    @api.depends('product_id', 'branch_stock_transfer_request_id.location_id', 'company_id')
    def compute_source_product_onhand(self):
        for record in self:
            quantity = 0
            if record.product_id and record.branch_stock_transfer_request_id.location_id:
                quants = self.env['stock.quant'].search(
                    [('location_id', '=', record.branch_stock_transfer_request_id.location_id.id),
                     ('product_id', '=', record.product_id.id),
                     ('company_id', '=', record.company_id.id),
                     ('product_uom_id', '=', record.product_uom.id)])
                for quant in quants:
                    quantity += quant.quantity
            record.source_onhand_quantity = quantity
