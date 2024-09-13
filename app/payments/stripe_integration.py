import stripe
from app.database.db import execute_query
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(event_id, user_id):
    event = get_event_details(event_id)
    if not event:
        return None

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(event['price'] * 100),
                    'product_data': {
                        'name': event['title'],
                        'description': event['description'],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('FRONTEND_URL')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/cancel",
            client_reference_id=f"{user_id}_{event_id}",
        )
        return checkout_session
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return None

def handle_successful_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user_id, event_id = session.client_reference_id.split('_')
        
        # Grant access to the event
        if grant_event_access(int(user_id), int(event_id)):
            return True
        else:
            print(f"Failed to grant access for user {user_id} to event {event_id}")
            return False
    except Exception as e:
        print(f"Error handling successful payment: {e}")
        return False

def grant_event_access(user_id, event_id):
    query = """
    INSERT INTO event_access (user_id, event_id, access_granted_at)
    VALUES (%s, %s, NOW())
    """
    params = (user_id, event_id)
    result = execute_query(query, params)
    return result is not None

def has_event_access(user_id, event_id):
    query = """
    SELECT * FROM event_access
    WHERE user_id = %s AND event_id = %s
    """
    params = (user_id, event_id)
    result = execute_query(query, params)
    return len(result) > 0

def get_event_details(event_id):
    query = "SELECT * FROM events WHERE id = %s"
    params = (event_id,)
    result = execute_query(query, params)
    return result[0] if result else None

def create_merchandise_checkout_session(merchandise_id, user_id):
    merchandise = get_merchandise_details(merchandise_id)
    if not merchandise:
        return None

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(merchandise['price'] * 100),
                    'product_data': {
                        'name': merchandise['name'],
                        'description': merchandise['description'],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('FRONTEND_URL')}/merchandise_success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/cancel",
            client_reference_id=f"{user_id}_{merchandise_id}",
        )
        return checkout_session
    except Exception as e:
        print(f"Error creating merchandise checkout session: {e}")
        return None

def handle_successful_merchandise_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        user_id, merchandise_id = session.client_reference_id.split('_')
        
        # Record the merchandise purchase
        if record_merchandise_purchase(int(user_id), int(merchandise_id)):
            return True
        else:
            print(f"Failed to record merchandise purchase for user {user_id}, merchandise {merchandise_id}")
            return False
    except Exception as e:
        print(f"Error handling successful merchandise payment: {e}")
        return False

def record_merchandise_purchase(user_id, merchandise_id):
    query = """
    INSERT INTO merchandise_purchases (user_id, merchandise_id, purchase_date)
    VALUES (%s, %s, NOW())
    """
    params = (user_id, merchandise_id)
    result = execute_query(query, params)
    return result is not None
