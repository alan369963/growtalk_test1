from sheet_utils import (
    get_passage,
    get_current_question,
    get_current_answer,
    advance_question_progress,
    get_student_name_by_phone,
)
from llm_utils import (
    generate_question_message,
    evaluate_answer,
    give_hint_or_explanation,
    ask_why_correct,
    handle_irrelevant_input_with_llm,
    respond_to_reflection,
    is_student_answering_question,
    is_reply_relevant_to_learning,
    generate_answer_to_student_question,
)
from whatsapp_utils import send_whatsapp_message

reading_sessions = {}


def start_reading_session(
    phone_number: int, sheet_user, sheet_comprehension, prior_learning: str = None
):
    passage = get_passage(sheet_user, sheet_comprehension, phone_number)
    question = get_current_question(sheet_user, sheet_comprehension, phone_number)
    student_name = get_student_name_by_phone(sheet_user, phone_number)
    prior_learning = prior_learning if prior_learning else ""

    full_message = generate_question_message(question, student_name, prior_learning)
    reading_sessions[phone_number] = {
        "passage": passage,
        "question": question,
        "attempt": 1,
        "mode": "",  # empty or 'reflection'
        "last_user_answer": "",
    }
    send_whatsapp_message(phone_number, full_message)


def handle_reading_reply(
    phone_number: int, user_reply: str, sheet_user, sheet_comprehension
):
    if phone_number not in reading_sessions:
        send_whatsapp_message(phone_number, "請先輸入 'reading' 開始今日閱讀任務 ✍️")
        return

    session = reading_sessions[phone_number]

    # 🔁 Reflection mode
    if session.get("mode") == "reflection":
        print("📥 Handling reflection response...")
        reflection_reply = user_reply
        question = session["question"]
        correct_answer = get_current_answer(
            sheet_user, sheet_comprehension, phone_number
        )
        passage = session["passage"]

        response = respond_to_reflection(
            reflection_text=reflection_reply,
            question_text=question,
            correct_answer=correct_answer,
            passage=passage,
        )
        print(f"📥 Sending reflection response")
        send_whatsapp_message(phone_number, response)

        # ✅ Move to next question
        advance_question_progress(sheet_user, phone_number)
        print("Advance to next question")
        del reading_sessions[phone_number]
        start_reading_session(
            phone_number, sheet_user, sheet_comprehension, reflection_reply
        )
        return

    # 🧠 Standard question/answer logic
    passage = session["passage"]
    question = session["question"]
    attempt = session["attempt"]
    correct_answer = get_current_answer(sheet_user, sheet_comprehension, phone_number)

    if not is_student_answering_question(user_reply, question):
        print("Not answering the question")
        if is_reply_relevant_to_learning(user_reply, question):
            reply = generate_answer_to_student_question(user_reply)
            send_whatsapp_message(phone_number, reply)
        else:
            print("Not relevant to learning")
            response = handle_irrelevant_input_with_llm(user_reply)
            send_whatsapp_message(phone_number, response)
        return

    is_correct = evaluate_answer(user_reply, correct_answer)

    if is_correct:
        print("🎉 Student answered correctly.")

        # 🌟 Ask for reflection
        why_msg = ask_why_correct(question, user_reply, passage)
        send_whatsapp_message(phone_number, why_msg)

        session["mode"] = "reflection"
        session["last_user_answer"] = user_reply
        return

    else:
        # ❌ Incorrect
        print("❌ Incorrect")
        if attempt < 3:
            hint_msg = give_hint_or_explanation(
                user_reply, correct_answer, question, passage, attempt
            )
            session["attempt"] += 1
            send_whatsapp_message(phone_number, hint_msg)
            send_whatsapp_message(phone_number, f"❓再試吓回答呢條問題啦：{question}")

        else:
            explanation = give_hint_or_explanation(
                user_reply, correct_answer, question, passage, attempt=3
            )
            send_whatsapp_message(phone_number, explanation)
            advance_question_progress(sheet_user, phone_number)
            del reading_sessions[phone_number]
            start_reading_session(phone_number, sheet_user, sheet_comprehension)
