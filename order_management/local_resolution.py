"""Deterministic order responses for running without an LLM API key."""

from dataclasses import dataclass

from order_management.data import assess_escalation, get_inventory, get_order, get_tracking


@dataclass(frozen=True)
class LocalResolution:
    escalated: bool
    escalation_reason: str
    customer_response: str
    internal_summary: str


def resolve_locally(order_id: str, customer_question: str) -> LocalResolution:
    """Resolve a customer question using only the bundled sample records."""
    order = get_order(order_id)
    tracking = get_tracking(order["order_id"])
    inventory = get_inventory(order["product_sku"])
    escalation = assess_escalation(customer_question, tracking["tracking_status"])

    handoff = (
        f"Order {order['order_id']} ({order['product_name']}): "
        f"{customer_question.strip()} Tracking status: {tracking['tracking_status']}; "
        f"estimated delivery: {tracking['estimated_delivery']}. "
        f"Escalation reason: {escalation['reason'].replace('_', ' ')}."
    )
    if escalation["required"]:
        return LocalResolution(
            escalated=True,
            escalation_reason=escalation["reason"],
            customer_response=(
                "Your request needs assistance from a human support representative. "
                "No refund, replacement, or other account change has been made."
            ),
            internal_summary=handoff,
        )

    product = order["product_name"]
    if tracking["delayed"]:
        response = (
            f"Your {product} order is delayed in transit. The latest estimated delivery "
            f"is {tracking['estimated_delivery']} (the original expected date was "
            f"{tracking['expected_delivery']})."
        )
    elif tracking["tracking_status"].casefold() == "delivered":
        response = (
            f"Tracking shows your {product} order was delivered on "
            f"{tracking['estimated_delivery']}."
        )
    else:
        response = (
            f"Your {product} order status is “{tracking['tracking_status']}”. "
            f"The current estimated delivery is {tracking['estimated_delivery']}."
        )

    if inventory["stock"] == 0:
        alternatives = ", ".join(inventory["alternatives"])
        response += f" The ordered item is currently out of stock ({inventory['sku']})."
        if alternatives:
            response += (
                f" Possible alternatives are {alternatives}; contact support to discuss "
                "whether one is suitable."
            )
    else:
        response += (
            f" The item is currently in stock ({inventory['stock']} available)."
        )

    return LocalResolution(
        escalated=False,
        escalation_reason="",
        customer_response=response,
        internal_summary="",
    )
