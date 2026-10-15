import unittest

from order_management.data import (
    assess_escalation,
    get_inventory,
    get_order,
    get_tracking,
)
from order_management.local_resolution import resolve_locally


class OrderDataTests(unittest.TestCase):
    def test_delayed_order_has_tracking_and_replacement_availability(self):
        order = get_order("ord1025")
        tracking = get_tracking("ORD1025")
        inventory = get_inventory(order["product_sku"])

        self.assertEqual(order["product_name"], "Wireless Headphones")
        self.assertTrue(tracking["delayed"])
        self.assertEqual(tracking["estimated_delivery"], "2026-10-17")
        self.assertEqual(inventory["stock"], 0)
        self.assertIn("WH-110", inventory["alternatives"])

    def test_delivered_order_is_not_delayed(self):
        self.assertFalse(get_tracking("ORD1026")["delayed"])

    def test_out_of_stock_product_has_alternative(self):
        inventory = get_inventory(get_order("ORD1027")["product_sku"])

        self.assertEqual(inventory["stock"], 0)
        self.assertEqual(inventory["alternatives"], ["SP-310"])

    def test_unknown_order_raises_lookup_error(self):
        with self.assertRaises(LookupError):
            get_order("ORD9999")


class EscalationTests(unittest.TestCase):
    def test_explicit_human_request_escalates(self):
        result = assess_escalation("Please connect me to a human.")

        self.assertTrue(result["required"])
        self.assertEqual(result["reason"], "explicit_human_request")

    def test_late_delivery_alone_does_not_escalate(self):
        result = assess_escalation(
            "My package is late. Can you check the delivery estimate?",
            "Delayed in transit",
        )

        self.assertFalse(result["required"])

    def test_delivered_but_not_received_escalates(self):
        result = assess_escalation(
            "Tracking says delivered, but I never received it.", "Delivered"
        )

        self.assertTrue(result["required"])
        self.assertEqual(result["reason"], "marked_delivered_not_received")

    def test_refund_request_escalates(self):
        self.assertTrue(
            assess_escalation("I want a refund.")["required"]
        )


class LocalResolutionTests(unittest.TestCase):
    def test_delayed_order_gets_estimate_without_api(self):
        result = resolve_locally(
            "ORD1025", "My order is late. Can you check the status?"
        )

        self.assertFalse(result.escalated)
        self.assertIn("delayed in transit", result.customer_response)
        self.assertIn("2026-10-17", result.customer_response)
        self.assertIn("WH-110", result.customer_response)

    def test_customer_requesting_refund_is_escalated(self):
        result = resolve_locally("ORD1025", "I want a refund.")

        self.assertTrue(result.escalated)
        self.assertEqual(result.escalation_reason, "refund_or_cancellation_request")
        self.assertIn("Order ORD1025", result.internal_summary)

    def test_unknown_order_is_not_guessed(self):
        with self.assertRaises(LookupError):
            resolve_locally("ORD9999", "Where is my order?")


if __name__ == "__main__":
    unittest.main()
