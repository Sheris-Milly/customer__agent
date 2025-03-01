from langchain.tools import Tool

def track_order(order_id: str) -> str:
    """
    Simulate order tracking.
    """
    response = {"status": "Shipped", "estimated_delivery": "2 days"}
    return f"Order {order_id} is {response['status']}. Estimated delivery: {response['estimated_delivery']}."

track_order_tool = Tool(
    name="Order Tracker",
    func=track_order,
    description="Check order status by providing an order ID."
)
