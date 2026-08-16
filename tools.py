from database import con


def get_order_summary():
    """
    Return a summary of order statuses.

    Returns:
        Dictionary containing total, delivered, cancelled,
        and shipped order counts.
    """

    query = """
        SELECT
            COUNT(*) AS total_orders,

            COUNT(
                CASE
                    WHEN order_status = 'delivered'
                    THEN 1
                END
            ) AS delivered_orders,

            COUNT(
                CASE
                    WHEN order_status = 'canceled'
                    THEN 1
                END
            ) AS cancelled_orders,

            COUNT(
                CASE
                    WHEN order_status = 'shipped'
                    THEN 1
                END
            ) AS shipped_orders

        FROM orders
    """

    result = con.execute(query).fetchone()

    return {
        "total_orders": int(result[0]),
        "delivered_orders": int(result[1]),
        "cancelled_orders": int(result[2]),
        "shipped_orders": int(result[3])
    }

def get_order_status_summary():
    """
    Return the number and percentage of orders by order status.

    Returns:
        List of dictionaries containing status, order count,
        and percentage.
    """

    result = con.execute("""
        SELECT
            order_status,
            COUNT(*) AS orders
        FROM orders
        GROUP BY order_status
        ORDER BY orders DESC
    """).fetchall()

    total = sum(row[1] for row in result)

    return [
        {
            "status": row[0],
            "orders": int(row[1]),
            "percentage": round((row[1] / total) * 100, 2)
        }
        for row in result
    ]


def get_category_revenue(limit: int = 10) -> list[dict]:
    """
    Return product categories ranked by total revenue.

    Args:
        limit: Number of categories to return.

    Returns:
        List of categories with revenue and order counts.
    """

    result = con.execute("""
        SELECT
            c.product_category_name_english AS category,
            SUM(oi.price) AS revenue,
            COUNT(DISTINCT oi.order_id) AS orders
        FROM order_items oi
        JOIN products p
            ON oi.product_id = p.product_id
        JOIN categories c
            ON p.product_category_name = c.product_category_name
        GROUP BY c.product_category_name_english
        ORDER BY revenue DESC
        LIMIT ?
    """, [limit]).fetchall()

    return [
        {
            "category": row[0],
            "revenue": round(float(row[1]), 2),
            "orders": int(row[2])
        }
        for row in result
    ]


def get_review_summary():
    """
    Return an overall summary of customer review scores.

    Returns:
        Total reviews, average score, positive reviews,
        negative reviews, and reviews containing text.
    """

    result = con.execute("""
        SELECT
            COUNT(*) AS total_reviews,
            ROUND(AVG(review_score), 2) AS average_score,

            COUNT(
                CASE
                    WHEN review_score >= 4 THEN 1
                END
            ) AS positive_reviews,

            COUNT(
                CASE
                    WHEN review_score <= 2 THEN 1
                END
            ) AS negative_reviews,

            COUNT(
                CASE
                    WHEN review_comment_message IS NOT NULL
                         AND TRIM(review_comment_message) <> ''
                    THEN 1
                END
            ) AS reviews_with_text

        FROM reviews
    """).fetchone()

    return {
        "total_reviews": int(result[0]),
        "average_score": float(result[1]),
        "positive_reviews": int(result[2]),
        "negative_reviews": int(result[3]),
        "reviews_with_text": int(result[4])
    }

def get_payment_method_summary():
    """
    Return order counts and total payment value by payment method.

    Returns:
        List of payment methods with order counts and total value.
    """

    result = con.execute("""
        SELECT
            payment_type,
            COUNT(DISTINCT order_id) AS orders,
            ROUND(SUM(payment_value), 2) AS total_value
        FROM order_payments
        GROUP BY payment_type
        ORDER BY total_value DESC
    """).fetchall()

    return [
        {
            "payment_method": row[0],
            "orders": int(row[1]),
            "total_value": float(row[2])
        }
        for row in result
    ]

def get_revenue_by_state(limit: int = 10) -> list[dict]:
    """
    Return states ranked by total order revenue.

    Args:
        limit: Number of states to return.

    Returns:
        List of states with revenue and order counts.
    """

    result = con.execute("""
        SELECT
            c.customer_state AS state,
            ROUND(SUM(oi.price), 2) AS revenue,
            COUNT(DISTINCT oi.order_id) AS orders
        FROM order_items oi
        JOIN orders o
            ON oi.order_id = o.order_id
        JOIN customers c
            ON o.customer_id = c.customer_id
        GROUP BY c.customer_state
        ORDER BY revenue DESC
        LIMIT ?
    """, [limit]).fetchall()

    return [
        {
            "state": row[0],
            "revenue": float(row[1]),
            "orders": int(row[2])
        }
        for row in result
    ]

def get_revenue_summary():
    """
    Return overall sales revenue and order statistics.

    Returns:
        Total revenue, total orders, average order value.
    """

    result = con.execute("""
        SELECT
            ROUND(SUM(oi.price), 2) AS total_revenue,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(
                SUM(oi.price) / COUNT(DISTINCT oi.order_id),
                2
            ) AS average_order_value
        FROM order_items oi
    """).fetchone()

    return {
        "total_revenue": float(result[0]),
        "total_orders": int(result[1]),
        "average_order_value": float(result[2])
    }

