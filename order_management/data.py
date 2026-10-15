"""Read-only access to the local sample order and inventory CSV files."""

import csv
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


def _read_csv(filename: str) -> list[dict[str, str]]:
    with (DATA_DIR / filename).open(encoding="utf-8", newline="") as data_file:
        return list(csv.DictReader(data_file))


def get_order(order_id: str) -> dict[str, Any]:
    """Return an order by ID, or raise LookupError when it does not exist."""
    normalized_id = order_id.strip().upper()
    order = next(
        (row for row in _read_csv("orders.csv") if row["order_id"] == normalized_id),
        None,
    )
    if order is None:
        raise LookupError(f"No order was found for {normalized_id or 'the supplied ID'}.")
    order["quantity"] = int(order["quantity"])
    return order


def get_inventory(sku: str) -> dict[str, Any]:
    """Return current stock and available alternatives for a product SKU."""
    normalized_sku = sku.strip().upper()
    product = next(
        (row for row in _read_csv("inventory.csv") if row["sku"] == normalized_sku),
        None,
    )
    if product is None:
        raise LookupError(f"No inventory record was found for SKU {normalized_sku}.")
    product["stock"] = int(product["stock"])
    product["alternatives"] = [
        alternative for alternative in product["alternatives"].split(";") if alternative
    ]
    return product


def get_tracking(order_id: str) -> dict[str, Any]:
    """Return the mock carrier status and estimated delivery for an order."""
    order = get_order(order_id)
    return {
        "order_id": order["order_id"],
        "tracking_status": order["tracking_status"],
        "estimated_delivery": order["estimated_delivery"],
        "expected_delivery": order["expected_delivery"],
        "delayed": order["tracking_status"].lower() == "delayed in transit",
    }


def assess_escalation(
    customer_question: str, tracking_status: str = ""
) -> dict[str, Any]:
    """Identify cases that must be handled by a person rather than automated."""
    question = customer_question.casefold()
    status = tracking_status.casefold()
    triggers = (
        (
            "explicit_human_request",
            (
                "human",
                "representative",
                "real person",
                "speak to someone",
                "talk to someone",
                "live agent",
                "speak to an agent",
                "talk to an agent",
            ),
        ),
        ("safety_concern", ("injury", "injured", "unsafe", "safety", "fire", "smoke")),
        ("suspected_fraud", ("fraud", "unauthorized", "not my purchase", "stolen card")),
        ("payment_dispute", ("chargeback", "dispute this charge", "charged twice")),
        ("refund_or_cancellation_request", ("refund", "cancel my order", "cancellation")),
    )
    for reason, phrases in triggers:
        if any(phrase in question for phrase in phrases):
            return {"required": True, "reason": reason}
    if "delivered" in status and any(
        phrase in question
        for phrase in (
            "not received",
            "didn't receive",
            "never received",
            "never arrived",
            "missing",
        )
    ):
        return {"required": True, "reason": "marked_delivered_not_received"}
    return {"required": False, "reason": ""}
