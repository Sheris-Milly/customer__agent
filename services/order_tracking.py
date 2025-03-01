# services/order_tracking.py
import logging
import re

logger = logging.getLogger(__name__)


def track_order(order_id: str) -> str:
    """
    Simulate order tracking functionality.

    Args:
        order_id: The order identifier to track

    Returns:
        str: Information about the order status
    """
    try:
        # Validate order ID format (example: simple validation for demo)
        if not re.match(r'^[A-Z0-9]{6,10}$', order_id.strip()):
            return "Invalid order ID format. Please provide a valid order ID."

        # Simulated response - in a real application, this would query a database
        # or external API
        mock_data = {
            "ABC123": {"status": "Shipped", "estimated_delivery": "2 days"},
            "XYZ789": {"status": "Processing", "estimated_delivery": "5-7 days"},
            "123456": {"status": "Delivered", "estimated_delivery": "Delivered on Feb 28, 2025"}
        }

        # Get order info or return a default response
        order_info = mock_data.get(
            order_id.strip(),
            {"status": "Pending", "estimated_delivery": "7-10 business days"}
        )

        return (f"Order {order_id} is {order_info['status']}. "
                f"Estimated delivery: {order_info['estimated_delivery']}.")

    except Exception as e:
        logger.error(f"Error tracking order: {str(e)}")
        return "Sorry, I encountered an error while tracking your order."


logger.info("Order tracking function initialized")