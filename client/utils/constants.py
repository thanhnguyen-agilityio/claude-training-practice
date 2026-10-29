import random

API_BASE_URL = "http://localhost:8080"

# User-facing error messages (no technical terms)
ERROR_GENERIC = "Oops! Something went wrong. Please try again in a moment."
ERROR_CONNECTION = (
    "We're having trouble connecting right now. Please refresh the page and try again."
)
ERROR_REQUEST = (
    "We couldn't process your request. "
    "If this keeps happening, please contact support at hi@ecommerce.com"
)


WELCOME_MESSAGE = [
    "How can I assist you today?",
    "How can I help you today?",
    "Hello there! How can I assist you today?",
    "Do you need help?",
    "It's time for shopping! Do you have any favorite items?",
]


USER_AVATAR_CHOICE = [
    "./assets/images/user-boy.jpeg",
    "./assets/images/user-girl.jpeg",
    "./assets/images/user-avatar-animal.png",
]

BOT_AVATAR_CHOICE = [
    "./assets/images/bot-avatar-bg.jpeg",
    "./assets/images/bot-avatar.png",
]

USER_AVATAR = random.choice(USER_AVATAR_CHOICE)
BOT_AVATAR = random.choice(BOT_AVATAR_CHOICE)

QUICK_START = {
    "💁‍♀️ Services": [
        "Give me list categories",
        "Do you offer free shipping?",
        "How can I maintain the shape of my clothing?",
    ],
    "💁‍♀️ Products": [
        'Give me product "Velvet flared dress with puffy sleeves"',
        'Compare "Tapta Fitted Dress with Collared Neck" and "Eclipse Flared Lace Dress"',
    ],
    "💁‍♀️ Support": ["I want to create a support ticket."],
}
