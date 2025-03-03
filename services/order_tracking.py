import json
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config import ORDER_DATA_PATH

# Configure logging
logger = logging.getLogger(__name__)


class OrderTrackingService:
    """
    A service for tracking and retrieving order information.
    """

    def __init__(self):
        """Initialize the order tracking service."""
        logger.info("Initializing order tracking service")

        try:
            # Load or create order data
            self.create_or_load_order_data()
            logger.debug("Order tracking service initialized")

        except Exception as e:
            logger.error(f"Error initializing order tracking service: {str(e)}")
            raise RuntimeError(f"Failed to initialize order tracking service: {str(e)}")

    def create_or_load_order_data(self):
        """Create order data file if it doesn't exist, or load existing data."""
        try:
            if not os.path.exists(ORDER_DATA_PATH):
                logger.info(f"Order data file not found. Creating sample order data at {ORDER_DATA_PATH}")

                # Create sample order data
                current_date = datetime.now()
                sample_orders = {}

                # Generate 20 sample orders with different statuses
                for i in range(1, 21):
                    order_id = f"ORD-{100000 + i}"
                    order_date = current_date - timedelta(days=random.randint(1, 30))

                    # Randomize status based on order date
                    days_since_order = (current_date - order_date).days

                    if days_since_order < 2:
                        status = random.choice(["Processing", "Confirmed"])
                        shipping_date = None
                        delivery_date = None
                    elif days_since_order < 5:
                        status = random.choice(["Shipped", "In Transit"])
                        shipping_date = order_date + timedelta(days=1)
                        delivery_date = shipping_date + timedelta(days=random.randint(3, 7))
                    else:
                        status = random.choice(["Delivered", "Delivered"])
                        shipping_date = order_date + timedelta(days=1)
                        delivery_date = shipping_date + timedelta(days=random.randint(3, 5))

                    # Generate random items
                    num_items = random.randint(1, 5)
                    items = []
                    total = 0

                    for j in range(num_items):
                        price = round(random.uniform(10, 200), 2)
                        quantity = random.randint(1, 3)
                        item_total = price * quantity
                        total += item_total

                        items.append({
                            "id": f"ITEM-{j + 1}",
                            "name": f"Product {random.randint(1, 100)}",
                            "price": price,
                            "quantity": quantity,
                            "total": item_total
                        })

                    # Create the order
                    sample_orders[order_id] = {
                        "order_id": order_id,
                        "customer_name": f"Customer {i}",
                        "email": f"customer{i}@example.com",
                        "order_date": order_date.strftime("%Y-%m-%d"),
                        "status": status,
                        "shipping_date": shipping_date.strftime("%Y-%m-%d") if shipping_date else None,
                        "delivery_date": delivery_date.strftime("%Y-%m-%d") if delivery_date else None,
                        "shipping_address": f"{random.randint(100, 999)} Main St, City {i}, State",
                        "items": items,
                        "subtotal": total,
                        "tax": round(total * 0.08, 2),
                        "shipping_cost": 9.99,
                        "total": round(total * 1.08 + 9.99, 2),
                        "tracking_number": f"TRK-{random.randint(10000, 99999)}" if status in ["Shipped", "In Transit",
                                                                                               "Delivered"] else None
                    }

                # Save the sample orders
                os.makedirs(os.path.dirname(ORDER_DATA_PATH), exist_ok=True)
                with open(ORDER_DATA_PATH, 'w') as f:
                    json.dump(sample_orders, f, indent=2)

                self.orders = sample_orders
                logger.info(f"Created sample order data with {len(sample_orders)} orders")
            else:
                # Load existing orders
                logger.debug(f"Loading existing order data from {ORDER_DATA_PATH}")
                with open(ORDER_DATA_PATH, 'r') as f:
                    self.orders = json.load(f)

                logger.info(f"Loaded {len(self.orders)} orders")

        except Exception as e:
            logger.error(f"Error creating or loading order data: {str(e)}")
            raise RuntimeError(f"Failed to create or load order data: {str(e)}")

    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get information about a specific order.

        Args:
            order_id: The ID of the order to retrieve

        Returns:
            Order information dictionary or None if not found
        """
        try:
            logger.debug(f"Retrieving order: {order_id}")

            # Check if order exists
            if order_id in self.orders:
                logger.debug(f"Found order: {order_id}")
                return self.orders[order_id]

            # Try case-insensitive search (for convenience)
            for key, order in self.orders.items():
                if key.lower() == order_id.lower():
                    logger.debug(f"Found order with case-insensitive match: {key}")
                    return order

            logger.debug(f"Order not found: {order_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            return None

    def get_order_status(self, order_id: str) -> Optional[str]:
        """
        Get the status of a specific order.

        Args:
            order_id: The ID of the order

        Returns:
            Order status string or None if not found
        """
        try:
            order = self.get_order(order_id)
            if order:
                logger.debug(f"Order {order_id} status: {order['status']}")
                return order["status"]

            logger.debug(f"Could not get status for order {order_id} (not found)")
            return None

        except Exception as e:
            logger.error(f"Error retrieving order status for {order_id}: {str(e)}")
            return None

    def search_orders_by_email(self, email: str) -> List[Dict]:
        """
        Search for orders associated with an email address.

        Args:
            email: The customer's email address

        Returns:
            List of matching order dictionaries
        """
        try:
            logger.debug(f"Searching orders for email: {email}")

            matching_orders = []

            for order_id, order in self.orders.items():
                if order.get("email", "").lower() == email.lower():
                    matching_orders.append(order)

            logger.debug(f"Found {len(matching_orders)} orders for email {email}")
            return matching_orders

        except Exception as e:
            logger.error(f"Error searching orders by email {email}: {str(e)}")
            return []