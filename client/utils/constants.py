import random

API_BASE_URL = "http://localhost:8080"


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
