# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RefuseLeave(models.TransientModel):
    _name = 'refuse.leave'

    reason = fields.Text ('Reason')

    @api.multi
    def add_reason(self):
        """
        This method open wizard to add reason of refusing leave.
        """
        context = self._context
        hr_holidays_obj = self.env['hr.holidays']
        active_id = context.get('active_id')
        user = self.env.user
        if not user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse \
            leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', user.id)],
                                                 limit=1)

        if active_id:
            holiday_id = hr_holidays_obj.browse(active_id)
            for data in self:
                if holiday_id.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_('Leave request must be confirmed or \
                    validated in order to refuse it.'))
                if data.reason:
                    new_data = ''
                    new_data = "Leave Refused Reason. (%s) \n----------------------------------------------------------------------------" % user.name
                    orignal_note = ''
                    if holiday_id.notes:
                        orignal_note = holiday_id.notes
                    reason = orignal_note + "\n\n" + new_data + "\n\n" + \
                    data.reason or ''

                if holiday_id.state == 'validate1':
                    holiday_id.write({'state': 'refuse',
                                      'manager_id': manager.id,
                                      'notes': reason,
                                      'rejection' : data.reason})
                else:
                    holiday_id.write({'state': 'refuse',
                                      'manager_id2': manager.id,
                                      'notes': reason,
                                      'rejection' : data.reason})
                # Delete the meeting
                if holiday_id.meeting_id:
                    holiday_id.meeting_id.unlink()
                # If a category that created several holidays, cancel all related
                holiday_id.linked_request_ids.action_refuse()
                holiday_id._remove_resource_leave()
        return True
