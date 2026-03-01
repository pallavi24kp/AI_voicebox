from app.responses.response_templates import RESPONSE_TEMPLATES

def generate_response(intent: str, user_text: str):
    
    base_response = RESPONSE_TEMPLATES.get(
        intent,
        "Thank you for contacting support. How may I assist you further?"
    )

    return base_response