from app.database.db import execute_query

FAQ_CONTENT = [
    {
        "question": "How do I create an account?",
        "answer": "To create an account, click on the 'Register' option in the menu. Fill out the required information and submit the form. You'll then be able to log in with your new account."
    },
    {
        "question": "How can I purchase access to an event?",
        "answer": "To purchase access to an event, first browse or search for the event you're interested in. On the event page, click the 'Purchase Event' button and follow the payment process."
    },
    {
        "question": "Can I get a refund for an event I've purchased?",
        "answer": "Refund policies may vary depending on the event. Please contact the event organizer or our support team for specific refund requests."
    },
    {
        "question": "How do I access the content for an event I've purchased?",
        "answer": "After purchasing an event, you can access its content by going to the event page. The content will be available to you as long as you're logged in to your account."
    },
    {
        "question": "What should I do if I'm having technical issues during an event?",
        "answer": "If you're experiencing technical issues, try refreshing your browser or logging out and back in. If the problem persists, please contact our support team."
    },
    {
        "question": "How can I become a content provider?",
        "answer": "To become a content provider, register for an account and select the 'Content Provider' option during registration. Once approved, you'll have access to tools for creating and managing events."
    },
    {
        "question": "Is my payment information secure?",
        "answer": "Yes, we use industry-standard encryption and secure payment processing. We do not store your full credit card information on our servers."
    },
    {
        "question": "Can I share my account with others?",
        "answer": "No, account sharing is not allowed. Each user should have their own account for security and personalization purposes."
    },
    {
        "question": "How do I update my account information?",
        "answer": "You can update your account information by going to your profile page. Click on 'Profile' in the menu and you'll find options to edit your information."
    },
    {
        "question": "What types of events are available on the platform?",
        "answer": "Our platform hosts a wide variety of events, including webinars, workshops, conferences, and more. You can browse different categories to find events that interest you."
    }
]

def get_faq_content():
    query = "SELECT question, answer FROM faq ORDER BY id"
    result = execute_query(query)
    return result if result else []
