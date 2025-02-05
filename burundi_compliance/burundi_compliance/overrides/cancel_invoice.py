import frappe
from burundi_compliance.burundi_compliance.api_classes.base import OBRAPIBase
from burundi_compliance.burundi_compliance.data.sale_invoice_data import (
    InvoiceDataProcessor,
)
from burundi_compliance.burundi_compliance.data.cancel_invoice_data import (
    get_invoice_data,
)
from burundi_compliance.burundi_compliance.utils.background_jobs import (
    enqueue_cancel_invoice,
    enqueue_stock_movement,
)
from burundi_compliance.burundi_compliance.utils.get_stock_items import get_items

import datetime

base = OBRAPIBase()
auth_details = base.get_auth_details()


def cancel_invoice(doc, method=None):
    posting_date = ""
    if isinstance(doc.posting_date, str):
        posting_date = datetime.datetime.strptime(doc.posting_date, "%Y-%m-%d").date()
    else:
        posting_date = doc.posting_date

    if posting_date < auth_details.get("start_date"):
        return

    invoice_data = get_invoice_data(doc)
    base.authenticate()
    if doc.custom_reason_for_creditcancel is None:
        frappe.throw("Please provide a reason for cancelling the invoice")
    enqueue_cancel_invoice(invoice_data, doc)
    frappe.msgprint("Invoice cancellation job queued successfully!", alert=True)
