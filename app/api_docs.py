import streamlit as st
import json

def api_documentation():
    st.title("API Documentation")

    st.write("""
    This page provides documentation for the MediaHost API. 
    You can use these endpoints to interact with our platform programmatically.
    """)

    st.header("Authentication")
    st.write("""
    All API requests must be authenticated using a JWT token. 
    To obtain a token, use the `/api/login` endpoint with your username and password.
    Include the token in the `Authorization` header of your requests:
    
    ```
    Authorization: Bearer <your_token_here>
    ```
    """)

    endpoints = [
        {
            "name": "Login",
            "method": "POST",
            "url": "/api/login",
            "description": "Authenticate a user and receive a JWT token",
            "parameters": [
                {"name": "username", "type": "string", "required": True},
                {"name": "password", "type": "string", "required": True}
            ],
            "response": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        },
        {
            "name": "List Events",
            "method": "GET",
            "url": "/api/events",
            "description": "Get a list of all events",
            "parameters": [
                {"name": "page", "type": "integer", "required": False, "default": 1},
                {"name": "per_page", "type": "integer", "required": False, "default": 10}
            ],
            "response": [
                {
                    "id": 1,
                    "title": "Sample Event",
                    "description": "This is a sample event",
                    "start_time": "2023-06-01T10:00:00Z",
                    "end_time": "2023-06-01T12:00:00Z",
                    "price": 10.00
                }
            ]
        },
        # Add more endpoints here...
    ]

    for endpoint in endpoints:
        st.header(f"{endpoint['method']} {endpoint['url']}")
        st.write(endpoint['description'])
        
        st.subheader("Parameters")
        for param in endpoint['parameters']:
            required = "Required" if param.get('required', False) else "Optional"
            default = f" (Default: {param['default']})" if 'default' in param else ""
            st.write(f"- **{param['name']}** ({param['type']}): {required}{default}")
        
        st.subheader("Example Response")
        st.code(json.dumps(endpoint['response'], indent=2), language='json')
        
        st.markdown("---")

    st.header("Error Responses")
    st.write("""
    In case of errors, the API will return appropriate HTTP status codes along with a JSON response containing more details:

    ```json
    {
        "error": "Error message describing the issue"
    }
    ```

    Common error status codes:
    - 400: Bad Request
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Not Found
    - 500: Internal Server Error
    """)

# Remove this if statement as it's not needed in this file
# if __name__ == "__main__":
#     main()
