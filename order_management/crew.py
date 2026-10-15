"""CrewAI agents, tasks, and orchestration for order support."""

import os

from crewai import Agent, Crew, LLM, Process, Task
from pydantic import BaseModel, Field

from order_management.tools import (
    EscalationPolicyTool,
    InventoryLookupTool,
    OrderLookupTool,
    OrderTrackingTool,
)


class ResolutionOutput(BaseModel):
    escalated: bool = Field(description="True when a human support representative is required.")
    escalation_reason: str = Field(description="Reason for escalation, or empty when not escalated.")
    customer_response: str = Field(description="Concise, accurate response for the customer.")
    internal_summary: str = Field(description="Brief handoff summary for human support.")


def build_order_crew() -> Crew:
    """Create the four-agent sequential workflow, sharing prior task outputs."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Add it to the environment before starting the app."
        )
    llm = LLM(
        model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
        api_key=api_key,
    )

    support = Agent(
        role="Customer Support Agent",
        goal="Understand the customer's issue and verify the supplied order ID.",
        backstory="You triage customer questions and retrieve the relevant order record.",
        tools=[OrderLookupTool()],
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    inventory = Agent(
        role="Inventory Agent",
        goal="Verify stock for the ordered item and identify viable alternatives.",
        backstory="You use the inventory system as the source of truth for availability.",
        tools=[InventoryLookupTool()],
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    delivery = Agent(
        role="Delivery Agent",
        goal="Check carrier status, estimated arrival, and whether delivery is delayed.",
        backstory="You retrieve shipment updates from the tracking system.",
        tools=[OrderTrackingTool()],
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    resolution = Agent(
        role="Resolution Agent",
        goal="Recommend a safe, accurate resolution and escalate complaints that need a person.",
        backstory=(
            "You combine the support, stock, and shipping findings. You never promise "
            "a refund, replacement, or delivery date that the records do not support."
        ),
        tools=[EscalationPolicyTool()],
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    support_task = Task(
        description=(
            "For order {order_id}, understand the customer's issue: {customer_question}\n"
            "Use order_lookup to verify the order and summarize its ID, product, quantity, "
            "and order status. If the order cannot be found, clearly report that."
        ),
        expected_output="A concise verified order summary, or a clear not-found result.",
        agent=support,
    )
    inventory_task = Task(
        description=(
            "Use the customer support findings and order {order_id}. Check inventory for "
            "the order's product SKU using inventory_lookup. Report stock and alternatives; "
            "do not claim an alternative is a confirmed replacement."
        ),
        expected_output="The ordered product's stock count and any alternative SKUs.",
        agent=inventory,
        context=[support_task],
    )
    delivery_task = Task(
        description=(
            "Check shipment tracking for order {order_id} using order_tracking. Report "
            "carrier status, estimated delivery, and whether it is late against the expected date."
        ),
        expected_output="Verified tracking status, estimated delivery, and delay assessment.",
        agent=delivery,
        context=[support_task],
    )
    resolution_task = Task(
        description=(
            "Prepare a resolution using the customer question and all preceding task findings. "
            "Call human_escalation_policy with the full customer question and the tracking status. "
            "Set escalated=true whenever the policy says required=true; you may also escalate "
            "when the evidence shows the issue cannot safely be resolved automatically. "
            "For escalated cases, do not present a proposed remedy as already approved. "
            "For non-escalated cases, answer the customer's question directly and give only "
            "evidence-based next steps. If the order was not found, do not invent order details."
        ),
        expected_output=(
            "A structured resolution containing escalated, escalation_reason, "
            "customer_response, and internal_summary."
        ),
        agent=resolution,
        context=[support_task, inventory_task, delivery_task],
        output_pydantic=ResolutionOutput,
    )

    return Crew(
        agents=[support, inventory, delivery, resolution],
        tasks=[support_task, inventory_task, delivery_task, resolution_task],
        process=Process.sequential,
        verbose=False,
    )
