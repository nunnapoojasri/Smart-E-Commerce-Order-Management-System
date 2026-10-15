"""CrewAI tools that expose the local order, inventory, and tracking data."""

import json
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from order_management.data import assess_escalation, get_inventory, get_order, get_tracking


class OrderIdInput(BaseModel):
    order_id: str = Field(description="The customer's order ID, such as ORD1025.")


class SkuInput(BaseModel):
    sku: str = Field(description="The product SKU, such as WH-100.")


class EscalationInput(BaseModel):
    customer_question: str = Field(description="The customer's full question or complaint.")
    tracking_status: str = Field(
        default="", description="Shipment status, if this is a delivery-related request."
    )


class OrderLookupTool(BaseTool):
    name: str = "order_lookup"
    description: str = "Look up the details of an order using its order ID."
    args_schema: Type[BaseModel] = OrderIdInput

    def _run(self, order_id: str) -> str:
        return json.dumps(get_order(order_id))


class InventoryLookupTool(BaseTool):
    name: str = "inventory_lookup"
    description: str = "Check product stock and suggested replacement product SKUs."
    args_schema: Type[BaseModel] = SkuInput

    def _run(self, sku: str) -> str:
        return json.dumps(get_inventory(sku))


class OrderTrackingTool(BaseTool):
    name: str = "order_tracking"
    description: str = "Check mock carrier status and estimated delivery for an order."
    args_schema: Type[BaseModel] = OrderIdInput

    def _run(self, order_id: str) -> str:
        return json.dumps(get_tracking(order_id))


class EscalationPolicyTool(BaseTool):
    name: str = "human_escalation_policy"
    description: str = (
        "Check whether a complaint requires human support. Always use this before "
        "deciding whether to respond automatically."
    )
    args_schema: Type[BaseModel] = EscalationInput

    def _run(self, customer_question: str, tracking_status: str = "") -> str:
        return json.dumps(assess_escalation(customer_question, tracking_status))
