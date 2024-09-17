from odoo import models, fields, api
from datetime import date
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PaymentApproval(models.Model):
    _name = 'payment.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payment Approval'

    name = fields.Char(string='Description', required=True,tracking=True)
    amount = fields.Float(string='Amount', required=True,tracking=True)
    # description = fields.Text(string='Description')
    reference = fields.Char("Reference", required=True,tracking=True)
    submitted_by = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user, required=True,tracking=True)
    payment_date = fields.Date("Payment Date", default=fields.date.today(), required=True,tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft',tracking=True)
    # from_journal = fields.Many2one('account.journal', string="Journal", required=True)
    from_journal_destination = fields.Many2one('account.journal', string="Destination Journal",default=lambda self: self.env['payment.approval']._default_destination_journal() , required=True)
    account_id_from = fields.Many2one('account.account', "Account From",default=lambda self: self.env['payment.approval']._default_default_account_id())
    account_id_to = fields.Many2one('account.account', "Account To")
    # approval_id = fields.Many2one('res.users', "Approval",default=lambda self: self.env['payment.approval']._default_from_approval())
    account_from_balance=fields.Float("Account From Balance", compute="_compute_account_from_balance", store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account",default=lambda self: self.env['payment.approval']._default_destination_analytic())

    @api.depends('account_id_from')
    def _compute_account_from_balance(self):
        for approval in self:
            if approval.account_id_from:
                # Get the balance from account.move.line for the selected account
                account_balance = self.env['account.move.line'].search(
                    [('account_id', '=', approval.account_id_from.id)]).mapped('balance')
                approval.account_from_balance = sum(account_balance)
            else:
                approval.account_from_balance = 0.0

    @api.model
    def _default_from_journal(self):
        # Set default value for 'from_journal' based on user's settings
        user = self.env.user
        user_settings = self.env['user.journal.settings'].search([('name', '=', user.id)], limit=1)
        if user_settings:
            return user_settings.journal_id.id
        return False

    @api.model
    def _default_from_approval(self):
        # Set default value for 'from_journal' based on user's settings
        user = self.env.user
        user_settings = self.env['user.journal.settings'].search([('name', '=', user.id)], limit=1)
        if user_settings:
            return user_settings.approval_id.id
        return False


    def _default_destination_journal(self):
        # Set default value for 'from_journal' based on user's settings
        user = self.env.user
        user_settings = self.env['user.journal.settings'].search([('name', '=', user.id)], limit=1)
        if user_settings:
            return user_settings.journal_id.id
        return False

    def _default_destination_analytic(self):
        # Set default value for 'from_journal' based on user's settings
        user = self.env.user
        user_settings = self.env['user.journal.settings'].search([('name', '=', user.id)], limit=1)
        if user_settings:
            return user_settings.analytic_account_id.id
        return False

    def _default_default_account_id(self):
        # Set default value for 'from_journal' based on user's settings
        user = self.env.user
        user_settings = self.env['user.journal.settings'].search([('name', '=', user.id)], limit=1)
        if user_settings:
            return user_settings.account_id_from
        return False

    def action_submit_for_approval(self):
        for approval in self:
            approval.state = 'submitted'

    def action_approve(self):
        for approval in self:
            approval.state = 'approved'
            # Create corresponding account.payment record
            self._create_account_payment(approval)

    def action_reject(self):
        for approval in self:
            approval.state = 'rejected'

    def _create_account_payment(self, approval):


        payment_data = {
            'partner_id': approval.submitted_by.partner_id.id,
            'payment_type': 'outbound',
            'payment_method_id': 1,  # Assuming you have a payment method ID
            'amount': approval.amount,
            'journal_id': self.from_journal.id,
            'destination_journal_id': self.from_journal_destination.id,
            'date': fields.Date.today(),
            'is_internal_transfer': True,
            'bank_ref_no':self.reference
            # Add other necessary fields
        }
        existing_payment = self.env['account.payment'].search([('bank_ref_no', '=', self.reference)], limit=1)
        if existing_payment:
            raise ValidationError(_('The reference (New Bank reference) "%s" is already used in another payment.') % self.reference)
        else:
            self.env['account.payment'].create(payment_data).action_post()

    # Create a button for generating a journal entry
    def button_create_journal_entry(self):
        self._create_journal_entry()

    def _create_journal_entry(self):
        # Create the journal entry (account.move) for the payment approval
        if not self.account_id_from or not self.account_id_to:
            raise ValidationError(_("Both 'Account From' and 'Account To' must be set."))

        journal_id = self.from_journal_destination.id
        if not journal_id:
            raise ValidationError(_("No journal linked to the 'Account From'."))

        # Create the journal entry (account.move)
        journal_entry = self.env['account.move'].create({
            'journal_id': journal_id,  # Journal linked to account_from
            'date': self.payment_date,
            'ref': self.reference,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_id_from.id,
                    'name': self.name,
                    'debit': 0.0,
                    'credit': self.amount,
                }),
                (0, 0, {
                    'account_id': self.account_id_to.id,
                    'name': self.name,
                    'debit': self.amount,
                    'credit': 0.0,
                })
            ]
        })

        # Post the journal entry
        self.state='approved'
        journal_entry.action_post()



class UserJournalSettings(models.Model):
    _name = 'user.journal.settings'
    _description = 'Settings for Journal and bank'
    name = fields.Many2one('res.users', "User", required=True)
    journal_id = fields.Many2one('account.journal', "Journal", required=True)
    journal_id_to = fields.Many2one('account.journal', "Destination Journal", required=True)
    account_id_from=fields.Many2one('account.account',"Account From")
    # approval_id=fields.Many2one('res.users',"Approval")
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account")


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    bank_ref_no=fields.Char("New Bank Reference")

    # @api.constrains('ref')
    # def _check_unique_ref(self):
    #     for record in self:
    #         if record.ref:
    #             existing_payment = self.search([('ref', '=', record.ref)])
    #             if existing_payment:
    #                 raise ValidationError("Payment reference must be unique. The reference '%s' is already in use." % record.ref)

    def action_post(self):
        for payment in self:
            if payment.bank_ref_no:
                existing_payment = self.search([
                    ('bank_ref_no', '=', payment.bank_ref_no),
                    ('id', '!=', payment.id),
                ], limit=1)
                if existing_payment:
                    raise ValidationError(_('The reference (New Payment Reference) "%s" is already used in another payment.') % payment.bank_ref_no)
        return super(AccountPayment, self).action_post()






