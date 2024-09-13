import bcrypt
import jwt
import datetime
from app.database.db import execute_query
import os
from dotenv import load_dotenv
from functools import wraps
import streamlit as st
import logging

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

logger = logging.getLogger(__name__)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def register_user(username, email, password, is_content_provider=False):
    try:
        hashed_password = hash_password(password)
        query = """
        INSERT INTO users (username, email, password_hash, is_content_provider, role_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        role_id = 2 if is_content_provider else 3  # 2 for content_manager, 3 for viewer
        params = (username, email, hashed_password, is_content_provider, role_id)
        result = execute_query(query, params)
        if result is not None:
            logger.info(f"User registered successfully: {username}")
            return True
        else:
            logger.error(f"Failed to register user: {username}")
            return False
    except Exception as e:
        logger.exception(f"Exception occurred while registering user {username}: {str(e)}")
        return False

def get_user_role(user_id):
    query = """
    SELECT r.name FROM users u
    JOIN roles r ON u.role_id = r.id
    WHERE u.id = %s
    """
    params = (user_id,)
    result = execute_query(query, params)
    return result[0]['name'] if result else None

def login_user(username, password):
    query = "SELECT * FROM users WHERE username = %s"
    params = (username,)
    result = execute_query(query, params)
    
    if result and len(result) > 0:
        user = result[0]
        if verify_password(password, user['password_hash']):
            role = get_user_role(user['id'])
            access_token = create_access_token({"sub": user['username'], "role": role})
            user_data = {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "is_content_provider": user['is_content_provider'],
                "role": role
            }
            return {"access_token": access_token, "token_type": "bearer", "user": user_data}
    return None

def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in st.session_state or st.session_state['user'].get('role') != role:
                st.error("You don't have permission to access this page.")
                return None
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_profile(username):
    query = """
    SELECT id, username, email, is_content_provider, created_at
    FROM users
    WHERE username = %s
    """
    params = (username,)
    result = execute_query(query, params)
    return result[0] if result else None

def update_user_profile(username, email):
    query = """
    UPDATE users
    SET email = %s
    WHERE username = %s
    """
    params = (email, username)
    result = execute_query(query, params)
    return result is not None
