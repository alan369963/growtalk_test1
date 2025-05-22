"""
whatsapp_webhook.py

FastAPI application that receives WhatsApp messages from the Node.js bot and
routes them into the appropriate training session (vocab, reading, etc.).

Core responsibilities:
- Log and store incoming messages
- Match student messages to training functions (e.g., start vocab)
- Maintain separation between input reception and logic execution

This serves as the bridge from WhatsApp to Python.
"""

# Run in Terminal
# uvicorn whatsapp_webhook:app --reload --port 8000

# Run in another Terminal
# cd whatsapp bot
# node .\index.js

from fastapi import FastAPI, Request
import uvicorn
from llm_utils import (
    generate_answer_to_student_question,
    greet_student,
    handle_irrelevant_input_with_llm,
    is_reply_relevant_to_learning,
    is_student_answering_question,
)
from sheet_utils import connect_to_sheet, get_student_name_by_phone
from vocab_session_controller import (
    start_vocab_session,
    handle_vocab_reply,
    vocab_sessions,
)
from whatsapp_utils import send_whatsapp_message, last_sent_messages
from reading_session_controller import (
    start_reading_session,
    handle_reading_reply,
    reading_sessions,
)
from open_reading_session_controller import (
    start_open_reading_session,
    handle_open_reading_reply,
    open_reading_sessions,
)


app = FastAPI()

user_sheet = connect_to_sheet("User List", "Sheet1")
open_reading_sheet = connect_to_sheet(
    "Copy of ielts文本素材1標準化文本_v1", "Part 2-Open-End Que"
)
close_reading_sheet = connect_to_sheet(
    "Copy of ielts文本素材1標準化文本_v1", "Part 3-Closed-End Que"
)

vocab_sheet = connect_to_sheet("Question List", "vocab")


@app.post("/receive-whatsapp")
async def receive_message(request: Request):
    data = await request.json()
    phone_number = data["phone_number"]
    message = data["message"].strip().lower()
    student_name = get_student_name_by_phone(user_sheet, phone_number)

    print(f"📥 Received message from {phone_number}: {message}")

    # 1. Command-based triggers
    if "start" in message:
        print("💬 Greeting student...")
        greet = greet_student(student_name)
        send_whatsapp_message(phone_number, greet)
        return

    elif "vocab" in message:
        print("🧠 Starting vocab session...")
        start_vocab_session(phone_number, user_sheet, vocab_sheet)
        return

    elif "reading" in message:
        print("📘 Starting reading session...")
        start_reading_session(phone_number, user_sheet, close_reading_sheet)
        return

    elif "warm up" in message:
        print("🪞 Starting open-ended reading session...")
        start_open_reading_session(phone_number, user_sheet, open_reading_sheet)
        return

    # 2. Ongoing session check
    elif phone_number in open_reading_sessions:
        handle_open_reading_reply(phone_number, message, user_sheet, open_reading_sheet)
        return

    elif phone_number in reading_sessions:
        handle_reading_reply(phone_number, message, user_sheet, close_reading_sheet)
        return

    # 3. Default fallback: check if they are answering previous vocab question
    question_prompt = last_sent_messages.get(phone_number, "")

    if is_student_answering_question(message, question_prompt):
        print("💡 Student is trying to answer a question.")
        handle_vocab_reply(phone_number, message, user_sheet, vocab_sheet)
        return

    elif is_reply_relevant_to_learning(message, question_prompt):
        print("💬 Related to English, but not answering.")
        response = generate_answer_to_student_question(message)
        send_whatsapp_message(phone_number, response)
        start_vocab_session(phone_number, user_sheet, vocab_sheet)
        return

    else:
        print("⛔️ Irrelevant input. Redirecting.")
        response = handle_irrelevant_input_with_llm(message)
        send_whatsapp_message(phone_number, response)
        return
