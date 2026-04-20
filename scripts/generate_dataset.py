import csv
import random

intents = {
    "order_status": [
        "Where is my order?",
        "Can you tell me my order status?",
        "Has my package been shipped?",
        "Track my order please",
        "When will my package arrive?",
        "Check the delivery status",
        "Is my order on the way?",
        "Give me tracking details",
        "What is the shipping update?",
        "I want to know where my order is"
    ],
    "cancel_order": [
        "I want to cancel my order",
        "Cancel my recent purchase",
        "Stop my order immediately",
        "I need to cancel an item",
        "Please cancel my order",
        "Abort my purchase",
        "Can you stop my shipment?",
        "I changed my mind cancel it",
        "Remove my order",
        "Cancel the product I bought"
    ],
    "refund_request": [
        "I want a refund",
        "How do I get my money back?",
        "Refund my payment",
        "Return my money please",
        "I need a refund for this item",
        "Can I get a refund?",
        "Process my refund",
        "Give me back my payment",
        "I want to return this product",
        "Issue my refund"
    ],
    "subscription_issue": [
        "Cancel my subscription",
        "Update my subscription plan",
        "Pause my subscription",
        "Subscription is not working",
        "Change my subscription",
        "Modify my membership",
        "Stop auto renewal",
        "Upgrade my plan",
        "Downgrade my subscription",
        "Manage my subscription"
    ],
    "payment_problem": [
        "Payment failed",
        "My card was declined",
        "Why was I charged twice?",
        "There is a billing issue",
        "Transaction did not go through",
        "Payment not successful",
        "Money deducted but order not placed",
        "Billing error",
        "Double payment problem",
        "Card payment issue"
    ],
    "delivery_delay": [
        "My delivery is delayed",
        "Why is my order late?",
        "Package has not arrived yet",
        "Delivery is taking too long",
        "Order is stuck in transit",
        "Shipment delay problem",
        "Late delivery issue",
        "My package is overdue",
        "Expected date passed",
        "Delivery hasn’t come"
    ],
    "account_update": [
        "Update my email address",
        "Change my phone number",
        "Edit my account details",
        "Modify my profile",
        "Update my contact info",
        "Change my password",
        "Update personal information",
        "Correct my account details",
        "Edit my username",
        "Update account settings"
    ],
    "complaint": [
        "I want to file a complaint",
        "This service is terrible",
        "I am unhappy with the product",
        "Very disappointed with your service",
        "I have a complaint",
        "Bad customer experience",
        "Not satisfied with service",
        "This is unacceptable",
        "Poor quality product",
        "I am frustrated with this service"
    ],
    "product_info": [
        "Tell me about this product",
        "What are the features?",
        "Is this product available?",
        "Give me product details",
        "What is the price?",
        "Describe this item",
        "Product specifications please",
        "Do you have this in stock?",
        "More info about the product",
        "Explain the product features"
    ],
    "technical_support": [
        "App is not working",
        "I cannot log in",
        "There is a technical issue",
        "Website crashed",
        "Having trouble accessing my account",
        "System error message",
        "App keeps crashing",
        "Login problem",
        "Bug in the application",
        "Technical glitch issue"
    ]
}

rows = []

for intent, samples in intents.items():
    for _ in range(40):
        sentence = random.choice(samples)
        rows.append([sentence, intent])

random.shuffle(rows)

with open("data/intent_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["text", "intent"])
    writer.writerows(rows)

print("Improved dataset created with", len(rows), "samples!")