import logging
import pprint

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class EpayncController(http.Controller):

    # ── Return redirect from gateway ──────────────────────────────────────────
    @http.route(
        '/payment/epaync/return',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        save_session=False,
    )
    def epaync_return(self, **data):
        _logger.info("EpayNC return | data:\n%s", pprint.pformat(data))
        try:
            tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'epaync', data
            )
            tx._process_notification_data(data)
            tx._execute_callback()
        except ValidationError as e:
            _logger.exception("EpayNC return error: %s", str(e))
        return request.redirect('/payment/status')

    # ── IPN / Webhook (server-to-server) ─────────────────────────────────────
    @http.route(
        '/payment/epaync/ipn',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
        save_session=False,
    )
    def epaync_ipn(self, **data):
        _logger.info("EpayNC IPN | data:\n%s", pprint.pformat(data))

        provider = None
        site_id = data.get('vads_site_id')
        if site_id:
            provider = request.env['payment.provider'].sudo().search([
                ('code', '=', 'epaync'),
                ('epaync_merchant_id', '=', site_id),
            ], limit=1)

        try:
            tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'epaync', data
            )

            # Verify shop ID
            if tx.provider_id.epaync_merchant_id and \
                    tx.provider_id.epaync_merchant_id != data.get('vads_site_id'):
                raise ValidationError("EpayNC IPN: Shop ID mismatch.")

            # Verify amount — vads_amount is in minor currency units
            currency = tx.currency_id
            decimal_places = currency.decimal_places if currency else 0
            expected_amount = int(round(tx.amount * (10 ** decimal_places)))
            received_amount = int(data.get('vads_amount', -1))
            if expected_amount != received_amount:
                raise ValidationError(
                    f"EpayNC IPN: Amount mismatch — expected {expected_amount}, got {received_amount}."
                )

            # Verify currency — compare ISO 4217 numeric codes
            from odoo.addons.payment_epaync.models.payment_transaction import ISO4217_NUMERIC
            expected_currency_numeric = ISO4217_NUMERIC.get(currency.name if currency else 'XPF', '953')
            received_currency = data.get('vads_currency', '')
            if received_currency and expected_currency_numeric != received_currency:
                raise ValidationError(
                    f"EpayNC IPN: Currency mismatch — expected {expected_currency_numeric}, got {received_currency}."
                )

            tx._process_notification_data(data)
            tx._execute_callback()

        except ValidationError as e:
            _logger.exception("EpayNC IPN validation error: %s", str(e))
            if provider:
                request.env['payment.epaync.log'].sudo()._log(
                    provider=provider,
                    log_type='error',
                    error_message=str(e),
                    webhook_payload=str(data),
                )
            return request.make_response(
                f"ERROR: {e}",
                headers=[('Content-Type', 'text/plain')],
                status=400,
            )
        except Exception as e:
            _logger.exception("EpayNC IPN unexpected error: %s", str(e))
            return request.make_response(
                "ERROR",
                headers=[('Content-Type', 'text/plain')],
                status=500,
            )

        return request.make_response('OK', headers=[('Content-Type', 'text/plain')])

    # ── Status landing pages ──────────────────────────────────────────────────
    @http.route(
        '/payment/epaync/success',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        website=True,
        save_session=False,
    )
    def epaync_success(self, **data):
        _logger.info("EpayNC success redirect")
        if data:
            try:
                tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'epaync', data
                )
                tx._process_notification_data(data)
                tx._execute_callback()
            except Exception:
                pass
        return request.redirect('/payment/status')

    @http.route(
        '/payment/epaync/cancel',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        website=True,
        save_session=False,
    )
    def epaync_cancel(self, **data):
        _logger.info("EpayNC cancel redirect")
        if data:
            try:
                tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'epaync', data
                )
                tx._process_notification_data(data)
                tx._execute_callback()
            except Exception:
                pass
        return request.redirect('/payment/status')

    @http.route(
        '/payment/epaync/refused',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        website=True,
        save_session=False,
    )
    def epaync_refused(self, **data):
        _logger.info("EpayNC refused redirect")
        if data:
            try:
                tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'epaync', data
                )
                tx._process_notification_data(data)
                tx._execute_callback()
            except Exception:
                pass
        return request.redirect('/payment/status')

    @http.route(
        '/payment/epaync/error',
        type='http',
        auth='public',
        methods=['GET', 'POST'],
        csrf=False,
        website=True,
        save_session=False,
    )
    def epaync_error(self, **data):
        _logger.info("EpayNC error redirect")
        if data:
            try:
                tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'epaync', data
                )
                tx._process_notification_data(data)
                tx._execute_callback()
            except Exception:
                pass
        return request.redirect('/payment/status')
