from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning, UserError
from datetime import datetime, timedelta
import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # @api.multi
    # @api.depends('pack_operation_product_ids.qty_done','state','origin','partner_id.property_supplier_payment_term_id','date_done')
    def _get_date_amount(self):
        for pick in self:
            if pick.partner_id and pick.partner_id.supplier and pick.partner_id.property_supplier_payment_term_id and pick.date_done:
                term = pick.partner_id.property_supplier_payment_term_id
                days = term.line_ids.filtered(
                    lambda x: x.value == 'balance' and x.option == 'day_after_invoice_date').mapped('days')
                if days:
                    day = days[0]
                    dt = datetime.strptime(pick.date_done[:10], "%Y-%m-%d")
                    date = str(dt + timedelta(days=day))[:10]
                    pick.date_due = date

                if pick.origin and pick.move_lines :
                    t_amount = 0.0
                    for move in pick.move_lines :
                        amount = move.price_unit * move.product_qty
                        t_amount += amount
                    pick.total_amount = t_amount


    backdated = fields.Boolean(string='Backdated', copy=False)
    backdate_done = fields.Date(string='Backdate Done', copy=False, track_visibility='onchange')
    force_date = fields.Datetime(string='Forced on', readonly=True, copy=False)
    force_uid = fields.Many2one('res.users', string='Forced by', readonly=True, copy=False)
    date_due = fields.Date(string='Date Due', compute='_get_date_amount')
    total_amount = fields.Float(string='Total Amount', compute='_get_date_amount')


    @api.multi
    def action_backdate(self):
        for me_id in self :
            if me_id.backdated :
                raise Warning("Transaksi %s sudah backdate sebelumnya."%(me_id.name))
            if not me_id.backdate_done :
                raise Warning("Silahkan isi tanggal backdate done.")
            me_id.move_lines.write({'date':me_id.backdate_done})
            me_id.pack_operation_product_ids.write({'date':me_id.backdate_done})
            acc_move_ids = self.env['account.move'].search([('ref','=',me_id.name)])
            if acc_move_ids :
                for move_id in acc_move_ids :
                    update_posted = False
                    if not move_id.journal_id.update_posted :
                        move_id.journal_id.update_posted = True
                        update_posted = True
                    move_id.button_cancel()
                    move_id.write({'date':me_id.backdate_done})
                    move_id.line_ids.write({
                        'date': me_id.backdate_done,
                        'date_maturity': me_id.backdate_done
                    })
                    move_id.post()
                    if update_posted :
                        move_id.journal_id.update_posted = False
            quant_ids = me_id.move_lines.mapped('quant_ids')
            if quant_ids :
                quant_ids.write({'in_date':me_id.backdate_done})
            me_id.backdated = True

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for me_id in self :
            if me_id.location_id.usage == 'internal' and me_id.location_dest_id.usage == 'customer' :
                sale_id = self.env['sale.order'].search([('name','=',me_id.origin)], limit=1)
                if not sale_id :
                    continue
                picking_receive_id = self.search([
                    ('origin','=',sale_id.client_order_ref),
                    ('state','not in',['done','cancel']),
                ], limit=1)
                if not picking_receive_id :
                    continue
                products = {}
                for pack in me_id.pack_operation_product_ids :
                    products[pack.product_id] = products.get(pack.product_id, 0) + pack.qty_done
                for prod, qty in products.items():
                    pack = self.env['stock.pack.operation'].search([
                        ('picking_id','=',picking_receive_id.id),
                        ('product_id','=',prod.id),
                    ], limit=1)
                    if pack :
                        pack.write({'qty_done':qty})
        return res

    @api.multi
    def force_assign(self):
        for me_id in self :
            me_id.write({
                'force_date': fields.Datetime.now(),
                'force_uid': me_id.env.user.id,
            })
        return super(StockPicking, self).force_assign()

    @api.multi
    def fill_pack_operation(self):
        picking_ids = self.env['stock.picking'].search([
            ('state','=','done'),
            ('pack_operation_product_ids','=',False),
            ('move_lines','!=',False),
        ])
        for picking in picking_ids :
            for move in picking.move_lines :
                self.env['stock.pack.operation'].create({
                    'product_id': move.product_id.id,
                    'product_qty': move.product_qty,
                    'qty_done': move.product_qty,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'product_uom_id': move.product_uom.id,
                    'picking_id': move.picking_id.id,
                })

        # move_ids = self.env['stock.move'].search([
        #     ('state','=','done'),
        #     ('linked_move_operation_ids','=',False),
        #     ('picking_id','!=',False),
        # ])
        # print "move_ids=================================",move_ids
        # for move in move_ids :
        #     operation_ids = self.env['stock.pack.operation'].search([
        #         ('product_id','=',move.product_id.id),
        #         ('picking_id','=',move.picking_id.id)
        #     ])
        #     if operation_ids :
        #         continue
        #     print "move=====================================",move
        #     jkfdg
        #     self.env['stock.pack.operation'].create({
        #         'product_id': move.product_id.id,
        #         'product_qty': move.product_qty,
        #         'qty_done': move.product_qty,
        #         'location_id': move.location_id.id,
        #         'location_dest_id': move.location_dest_id.id,
        #         'product_uom_id': move.product_uom.id,
        #         'picking_id': move.picking_id.id,
        #     })

StockPicking()


class StockMove(models.Model):
    _inherit = 'stock.move'

    # @api.model
    # def create(self,vals):
    #     move = self.env['stock.move']
    #     if vals.get('picking_id', False) and vals.get('product_id', False):
    #         exist_move = move.sudo().search([('picking_id','=',vals['picking_id']),
    #                                               ('product_id','=',vals['product_id'])],limit=1)
    #         if exist_move and exist_move.product_uom_qty == vals['product_uom_qty']:
    #             raise Warning("Duplicate product on demand (%s) " % (exist_move.product_id.default_code))
    #     return super(StockMove, self).create(vals)

    @api.multi
    def action_done(self):
        move = self.env['stock.move']
        for mv in self :
            exist_move = move.sudo().search([('picking_id', '=', mv.picking_id.id),
                                            ('product_id', '=', mv.product_id.id),
                                             ('id','!=',mv.id)], limit=1)
            if exist_move and exist_move.product_uom_qty == mv.product_uom_qty :
                if not exist_move.purchase_line_id and exist_move.picking_id.picking_type_id.code == 'incoming':
                    #exist_move.action_cancel()
                    raise Warning("Duplicate incoming product on demand (%s), %s pcs " % (mv.product_id.default_code,str(mv.product_uom_qty)))
        return super(StockMove, self).action_done()

    @api.multi
    def action_done2(self):
        """ copy buat eksekusi data yg tercancel"""
        # import pdb;pdb.set_trace()
        if not self :
            try :
                self = self.browse(self._context['params']['id'])
            except:
                pass
        self.filtered(lambda move: move.state == 'draft').action_confirm()

        Uom = self.env['product.uom']
        Quant = self.env['stock.quant']

        pickings = self.env['stock.picking']
        procurements = self.env['procurement.order']
        operations = self.env['stock.pack.operation']

        remaining_move_qty = {}

        for move in self:
            if move.picking_id:
                pickings |= move.picking_id
            remaining_move_qty[move.id] = move.product_qty
            for link in move.linked_move_operation_ids:
                operations |= link.operation_id
                pickings |= link.operation_id.picking_id

        # Sort operations according to entire packages first, then package + lot, package only, lot only
        operations = operations.sorted(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))

        for operation in operations:

            # product given: result put immediately in the result package (if False: without package)
            # but if pack moved entirely, quants should not be written anything for the destination package
            quant_dest_package_id = operation.product_id and operation.result_package_id.id or False
            entire_pack = not operation.product_id and True or False

            # compute quantities for each lot + check quantities match
            lot_quantities = dict((pack_lot.lot_id.id, operation.product_uom_id._compute_quantity(pack_lot.qty, operation.product_id.uom_id)
            ) for pack_lot in operation.pack_lot_ids)

            qty = operation.product_qty
            if operation.product_uom_id and operation.product_uom_id != operation.product_id.uom_id:
                qty = operation.product_uom_id._compute_quantity(qty, operation.product_id.uom_id)
            if operation.pack_lot_ids and float_compare(sum(lot_quantities.values()), qty, precision_rounding=operation.product_id.uom_id.rounding) != 0.0:
                raise UserError(_('You have a difference between the quantity on the operation and the quantities specified for the lots. '))

            quants_taken = []
            false_quants = []
            lot_move_qty = {}

            prout_move_qty = {}
            for link in operation.linked_move_operation_ids:
                prout_move_qty[link.move_id] = prout_move_qty.get(link.move_id, 0.0) + link.qty

            # Process every move only once for every pack operation
            for move in prout_move_qty.keys():
                # TDE FIXME: do in batch ?
                move.check_tracking(operation)

                # TDE FIXME: I bet the message error is wrong
                if not remaining_move_qty.get(move.id):
                    raise UserError(_("The roundings of your unit of measure %s on the move vs. %s on the product don't allow to do these operations or you are not transferring the picking at once. ") % (move.product_uom.name, move.product_id.uom_id.name))

                if not operation.pack_lot_ids:
                    preferred_domain_list = [[('reservation_id', '=', move.id)], [('reservation_id', '=', False)], ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]]
                    quants = Quant.quants_get_preferred_domain(
                        prout_move_qty[move], move, ops=operation, domain=[('qty', '>', 0)],
                        preferred_domain_list=preferred_domain_list)
                    Quant.quants_move(quants, move, operation.location_dest_id, location_from=operation.location_id,
                                      lot_id=False, owner_id=operation.owner_id.id, src_package_id=operation.package_id.id,
                                      dest_package_id=quant_dest_package_id, entire_pack=entire_pack)
                else:
                    # Check what you can do with reserved quants already
                    qty_on_link = prout_move_qty[move]
                    rounding = operation.product_id.uom_id.rounding
                    for reserved_quant in move.reserved_quant_ids:
                        if (reserved_quant.owner_id.id != operation.owner_id.id) or (reserved_quant.location_id.id != operation.location_id.id) or \
                                (reserved_quant.package_id.id != operation.package_id.id):
                            continue
                        if not reserved_quant.lot_id:
                            false_quants += [reserved_quant]
                        elif float_compare(lot_quantities.get(reserved_quant.lot_id.id, 0), 0, precision_rounding=rounding) > 0:
                            if float_compare(lot_quantities[reserved_quant.lot_id.id], reserved_quant.qty, precision_rounding=rounding) >= 0:
                                qty_taken = min(reserved_quant.qty, qty_on_link)
                                lot_quantities[reserved_quant.lot_id.id] -= qty_taken
                                quants_taken += [(reserved_quant, qty_taken)]
                                qty_on_link -= qty_taken
                            else:
                                qty_taken = min(qty_on_link, lot_quantities[reserved_quant.lot_id.id])
                                quants_taken += [(reserved_quant, qty_taken)]
                                lot_quantities[reserved_quant.lot_id.id] -= qty_taken
                                qty_on_link -= qty_taken
                    lot_move_qty[move.id] = qty_on_link

                remaining_move_qty[move.id] -= prout_move_qty[move]

            # Handle lots separately
            if operation.pack_lot_ids:
                # TDE FIXME: fix call to move_quants_by_lot to ease understanding
                self._move_quants_by_lot(operation, lot_quantities, quants_taken, false_quants, lot_move_qty, quant_dest_package_id)

            # Handle pack in pack
            if not operation.product_id and operation.package_id and operation.result_package_id.id != operation.package_id.parent_id.id:
                operation.package_id.sudo().write({'parent_id': operation.result_package_id.id})

        # Check for remaining qtys and unreserve/check move_dest_id in
        move_dest_ids = set()
        for move in self:
            if float_compare(remaining_move_qty[move.id], 0, precision_rounding=move.product_id.uom_id.rounding) > 0:  # In case no pack operations in picking
                move.check_tracking(False)  # TDE: do in batch ? redone ? check this

                preferred_domain_list = [[('reservation_id', '=', move.id)], [('reservation_id', '=', False)], ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]]
                quants = Quant.quants_get_preferred_domain(
                    remaining_move_qty[move.id], move, domain=[('qty', '>', 0)],
                    preferred_domain_list=preferred_domain_list)
                Quant.quants_move(
                    quants, move, move.location_dest_id,
                    lot_id=move.restrict_lot_id.id, owner_id=move.restrict_partner_id.id)

            # If the move has a destination, add it to the list to reserve
            if move.move_dest_id and move.move_dest_id.state in ('waiting', 'confirmed'):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurements |= move.procurement_id

            # unreserve the quants and make them available for other operations/moves
            move.quants_unreserve()

        # Check the packages have been placed in the correct locations
        self.mapped('quant_ids').filtered(lambda quant: quant.package_id and quant.qty > 0).mapped('package_id')._check_location_constraint()

        # set the move as done
        self.write({'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        procurements.check()
        # assign destination moves
        if move_dest_ids:
            # TDE FIXME: record setise me
            self.browse(list(move_dest_ids)).action_assign()

        pickings.filtered(lambda picking: picking.state == 'done' and not picking.date_done).write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        return True


    @api.multi
    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        if self.location_id.valuation_out_account_id:
            acc_src = self.location_id.valuation_out_account_id.id
        else:
            acc_src = accounts_data['stock_input'].id

        if self.location_dest_id.valuation_in_account_id:
            acc_dest = self.location_dest_id.valuation_in_account_id.id
        else:
            acc_dest = accounts_data['stock_output'].id

        acc_valuation = accounts_data.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation. (%s)') % (self.product_id.name))
        journal_id = accounts_data['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation

StockMove()