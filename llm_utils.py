"""
llm_utils.py

This module handles all interactions with the LLM to facilitate
dialogic, personalized English vocabulary and reading comprehension learning.

Functions include:
- Generating vocabulary prompts and hints
- Evaluating student answers for meaning accuracy
- Giving correct-answer praise messages
- Producing final explanations and scaffolded teaching content

Used throughout the system for all student-facing instructional messaging.
"""

from openai import OpenAI
import config
import sheet_utils

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.OPENROUTER_API_KEY,
)

# General system prompt for GrowTalk
system_prompt_reading = f"""你是一位專為香港中學生設計的 AI 英文閱讀老師。你主要以廣東話教英文，只在需要提出英文閱讀問題、講解英文詞語、句式或例句時才用英文，並會用廣東話詳細解釋清楚。你的語言自然、親切，貼近香港學生的語境。

你的教學是根據閱讀圈（reading circle）模式進行：學生先閱讀一段英文文本，然後你會根據文章內容逐步提出問題。問題可以是開放式（例如問主旨或角色動機），也可以是針對字詞、句子理解或語言技巧的。你透過問題判斷學生已懂與未懂的地方，並針對未懂之處提供適當的語言策略或理解技巧（例如用上下文揣摩生字意思、如何判斷語氣、分析句構）。

當學生嘗試應用所學策略後，你會根據他們的回應判斷是否理解。如有需要，你會重新講解、舉例或改變方法，直到學生能理解和應用為止。

在整個過程中，你會靈活運用 Talk Moves（例如重述學生講法、鼓勵補充、追問原因）和 Academic Productive Talk (APT) 策略，引導學生建構知識、澄清想法與深化理解。你會用問題促進對話，而不是直接提供答案。

你不會長篇大論，每一句說話都經過思考，簡潔、有啟發性且自然。你像一位真正的老師，會觀察學生是否真正明白，並在適當時候作出提示或重構。你不會濫讚，只會在學生有具體表現（如嘗試推論、使用策略、清楚解釋）時給予具體回饋，例如：「你試下用上下文去估呢個字，好叻啊」、「你咁樣推斷角色，幾有道理，不過有冇漏咗第二段？」

你善於舉例，但唔會死板用標準例子，如果覺得例子唔貼地、唔自然，可以主動改用香港學生熟悉的情境或經驗（例如校園生活、搭地鐵、玩手機、社交媒體、家庭情況等）。

你最終目標係幫學生建立英文閱讀理解能力、自主學習能力、同埋學習自信（academic self-efficacy）。你係一個會思考、會觀察、會引導的老師。"""

system_prompt_open = (
    f"""你是一位專為香港中學生設計的 AI 英文閱讀老師。你主要以廣東話教英文"""
)

system_prompt_vocab = f"""你是一位專為香港中學生設計的 AI 英文閱讀老師。你主要以廣東話教英文，只在需要提出英文閱讀問題、講解英文詞語、句式或例句時才用英文，並會用廣東話詳細解釋清楚。你的語言自然、親切，貼近香港學生的語境。

你的教學是根據閱讀圈（reading circle）模式進行：學生先閱讀一段英文文本，然後你會根據文章內容逐步提出問題。問題可以是開放式（例如問主旨或角色動機），也可以是針對字詞、句子理解或語言技巧的。你透過問題判斷學生已懂與未懂的地方，並針對未懂之處提供適當的語言策略或理解技巧（例如用上下文揣摩生字意思、如何判斷語氣、分析句構）。

當學生嘗試應用所學策略後，你會根據他們的回應判斷是否理解。如有需要，你會重新講解、舉例或改變方法，直到學生能理解和應用為止。

在整個過程中，你會靈活運用 Talk Moves（例如重述學生講法、鼓勵補充、追問原因）和 Academic Productive Talk (APT) 策略，引導學生建構知識、澄清想法與深化理解。你會用問題促進對話，而不是直接提供答案。

你不會長篇大論，每一句說話都經過思考，簡潔、有啟發性且自然。你像一位真正的老師，會觀察學生是否真正明白，並在適當時候作出提示或重構。你不會濫讚，只會在學生有具體表現（如嘗試推論、使用策略、清楚解釋）時給予具體回饋，例如：「你試下用上下文去估呢個字，好叻啊」、「你咁樣推斷角色，幾有道理，不過有冇漏咗第二段？」

你善於舉例，但唔會死板用標準例子，如果覺得例子唔貼地、唔自然，可以主動改用香港學生熟悉的情境或經驗（例如校園生活、搭地鐵、玩手機、社交媒體、家庭情況等）。

你最終目標係幫學生建立英文閱讀理解能力、自主學習能力、同埋學習自信（academic self-efficacy）。你係一個會思考、會觀察、會引導的老師。

"""

"""
##############
GENERAL
##############
"""


def greet_student(student_name: str) -> str:
    """
    Generate a warm and encouraging greeting message to student

    The message introduces the student to today's training topic and invites the student to reply with "I'm ready"
    to begin.

    Parameters:
        student_name (str): Student name

    Returns:
        str: Cantonese greeting message generated by the LLM
    """

    prompt = (
        """請你向學生發出一個邀請，鼓勵佢哋參加今日嘅英語練習時間。
        Student Name: {student_name}

        Sample: 
        "Hello {student_name}～👋
        今日我準備咗一個好輕鬆又實用嘅英文小練習😎
        🧡你準備好一齊挑戰今日嘅任務未？"

        Keep it under 20 words

        Require the student to reply "vocab" to start the vocab training when they are ready

        Make sure there is no space before the first text
        """
    ).format(student_name=student_name)

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_vocab},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def evaluate_answer(user_answer: str, correct_answer: str) -> bool:
    """
    Return True or False
    Check whether the user's answer is correct, based on the meaning rather than exact wording.

    Parameters:
        user_answer (str): student's answer.
        correct_answer (str): model answer.

    Returns:
        bool: True if the LLM determines the answer is correct, else False.
    """
    prompt = f"""
    你係一位用廣東話教書嘅英文老師

    你而家要評估學生對某條問題嘅回答，睇下佢答得啱唔啱。

    ✅ 請你只用以下 JSON 格式回覆，不需要其他說明或解釋：

    {{
    "is_correct": true/false
    }}

    資料如下：

    💬 學生答案：
    {user_answer}

    📖 標準答案（意思方向）：
    {correct_answer}

    請小心分析語意，再判斷學生答法係咪接近正確。
    """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_vocab,
            },
            {"role": "user", "content": prompt},
        ],
    )

    reply = response.choices[0].message.content.strip()

    # Parse the JSON-like response
    try:
        if '"is_correct": true' in reply.lower():
            return True
        elif '"is_correct": false' in reply.lower():
            return False
        else:
            raise ValueError(f"Unexpected LLM response: {reply}")
    except Exception as e:
        print(f"⚠️ Failed to interpret LLM response: {reply}")
        raise e


def is_student_answering_question(user_reply: str, question_prompt: str) -> bool:
    """
    Uses LLM to determine whether the student is attempting to answer the actual question prompt.

    Parameters:
        user_reply (str): The student's message.
        question_prompt (str): The question the bot asked (e.g. '你知唔知道 "adapt" 嘅意思？').

    Returns:
        bool: True if the reply is a direct or indirect answer to the question, else False.
    """
    prompt = f"""
        你問學生：
        「{question_prompt}」

        而學生嘅回應係：
        「{user_reply}」

        請你首先判斷學生嘅回答係唔係回應緊你問嘅問題？

        你要判斷學生有冇嘗試回應你個問題。

        ✅ 請你當作「有回應」的情況包括：
        - 學生短答，例如 "適應？"
        - 用名詞、動詞、形容詞作簡單回答
        - 答法唔完整，但有明顯意圖想回應問題
        - 用疑問語氣猜測，例如「係咪意思係…？」

        {{"answered": true}}

        ❌ 如果學生回應例如：
        - 問你私人問題
        - 講笑、講八卦、講無關內容

        {{"answered": false}}

        請你回覆 JSON 格式：
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_reading},
            {"role": "user", "content": prompt},
        ],
    )

    reply = response.choices[0].message.content.lower()
    return '"answered": true' in reply


def is_reply_relevant_to_learning(user_reply: str, current_question: str) -> bool:
    """
    Uses LLM to determine whether the student's message is relevant to the learning task
    or English learning in general.

    Parameters:
        user_reply (str): The student's message.
        current_question (str): The current English learning prompt/question.

    Returns:
        bool: True if relevant to English learning, else False.
    """
    prompt = f"""
    你係一位用廣東話教英文嘅老師。

    學生啱啱回應咗一段訊息，你要判斷佢講嘅內容，係唔係同英文學習關。

    以下係你問佢嘅問題：
    「{current_question}」

    以下係學生嘅回應：
    「{user_reply}」

    請你判斷學生係咪：
    ✅ 正常回應問題、問英文問題、想學英文 → 回覆：{{"relevant": true}}
    ❌ 講其他無關話題（例如：煮飯、AI係咩、天氣、無厘頭）→ 回覆：{{"relevant": false}}

    e.g.: 想問吓book呢個字可唔可以轉做動詞？ is relevant
    e.g.: 想問吓英文裏面noun係乜嘢意思？ is relevant


    唔需要其他說明，只用 JSON 格式回覆。
    """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_vocab},
            {"role": "user", "content": prompt},
        ],
    )

    reply = response.choices[0].message.content.lower()
    return '"relevant": true' in reply


def generate_answer_to_student_question(user_question: str) -> str:
    """
    Use LLM to generate answer to student's english related question
    """

    prompt = f"""
    學生問咗一條有關英文學習嘅問題，請你用廣東話簡單解答，並引導佢繼續返學習任務。

    問題：
    「{user_question}」
    """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_vocab},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def handle_irrelevant_input_with_llm(user_input: str) -> str:
    """
    Uses LLM to politely handle off-topic or irrelevant messages
    and gently redirect the student back to English learning.

    Parameters:
        user_input (str): The off-topic or unrelated message from the student.

    Returns:
        str: A warm Cantonese reply that acknowledges and redirects.
    """
    prompt = f"""
        學生啱啱講咗一啲同學習無關、跳題、或者偏離英文練習嘅說話：

        學生講：
        「{user_input}」

        請你用以下方式回應佢：
        1. 回應學生
        2. 再用輕鬆、鼓勵語氣話返佢我哋要返嚟學英文
        3. 可以加 emoji、輕 humour，但唔好講太長

        Require the student to reply "vocab" to start the vocab training when they are ready
        """

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it",
            messages=[
                {"role": "system", "content": system_prompt_reading},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ LLM failed in handle_irrelevant_input: {e}")
        return "呢個問題好有趣，不過我哋而家專心學英文先啦 😊"


"""
##############
READING EXERCISE
##############
"""


def generate_question_message(
    question: str, student_name: str = None, prior_learning: str = None
) -> str:
    """
    Appends the provided question
    Uses the LLM to generate a warm Cantonese encouragement message

    Parameters:
        question (str): The comprehension question.
        student_name (str, optional): Student's name.
        prior_learning (str, optional): A brief mention of what the student just learned (for transition).

    Returns:
        str: A message to send to the student.
    """
    name_text = f"{student_name}～👋 " if student_name else ""
    prior_learning = f"{prior_learning}" if prior_learning else ""
    transition = (
        f"頭先你做得唔錯，我哋啱啱學咗關於：{prior_learning}。而家我哋再試一條題目，實踐下你啱啱學到嘅技巧。"
        if prior_learning
        else "我哋一齊睇下一條題目啦，準備好未？"
    )

    prompt = f"""
        學生名：{student_name if student_name else ""}
        學生剛剛學咗：{prior_learning if prior_learning else ""}
        問題： {question}

        Please start with a transition {transition}
        請你設計一段具鼓勵性、結構清晰、具啟發式提問（TalkMoves）、以生活例子支持學習嘅教學開場，內容包括：
        - 引導性開場白（自然過渡）
        - 明確學習目標（用學生語言講）
        - 一條封閉式理解問題（Question: {question}）
        - 引導學生參與、預期反應，並適時插入提示或比較
        - 生活化例子，幫助學生建構意義
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_reading},
            {"role": "user", "content": prompt},
        ],
    )

    encouragement = response.choices[0].message.content.strip()

    # Combine into final message
    full_message = f"""
    {encouragement}
{question}
    """
    return full_message.strip()


def give_hint_or_explanation(
    user_answer: str,
    correct_answer: str,
    question_text: str,
    passage: str,
    attempt: int,
) -> str:
    """
    Only call when the answer is incorrect
    Provides hint or explanation based on the number of attempts.

    Parameters:
        user_answer (str): The student's response.
        correct_answer (str): The expected answer.
        question_text (str): The original question.
        attempt (int): Current attempt (1–3)

    Logic:
        Attempt	Bot Response Type	Purpose
        1st attempt	- Minor hint > Encourage thinking, low pressure
        2nd attempt	- Stronger hint	> Guide toward key concept
        3rd attempt	- Reveal + explain > Give correct answer with explanation, invite reflection

    Returns:
        str: Cantonese feedback message (hint or explanation)
    """
    if attempt < 1 or attempt > 3:
        raise ValueError("Attempt must be between 1 and 3")

    if attempt == 3:
        tone = "溫柔而清楚"
        task = f"""學生已經試咗三次未答啱，請你：
        - 提供正確答案「{correct_answer}」
        - 具體講解點解係呢個答案
        - 用學生可能誤解嘅角度作對比
        - 最後鼓勵學生再試另一題"""
    elif attempt == 2:
        tone = "進一步鼓勵"
        task = "請唔好提供答案，但指出一個可以引導學生思考嘅關鍵詞或句子，幫佢聚焦理解方向，並鼓勵佢再解釋自己點解會咁諗。"
    else:  # attempt == 1
        tone = "輕鬆鼓勵"
        task = "請只提供一個提示，幫助學生再次細閱文章內容，但唔講出答案或者直接線索。可以問一條引導問題令佢再諗諗。"

    prompt = f"""
        你係一位經驗豐富、熟悉Scaffolding、懂得用TalkMoves嘅老師。學生答錯咗以下問題：

        文章內容：{passage}
        問題：{question_text}
        學生作答：{user_answer}
        正確答案：{correct_answer}

        請用「{tone}」語氣，根據以下教學任務生成回饋：
        {task}

        訊息應該：
        - 用廣東話
        - 有啟發式提問
        - 可能用生活化例子幫佢理解
        - 如係第三次錯，要總結學習點並幫助學生理解正確觀念
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_reading,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def ask_why_correct(question_text: str, user_answer: str, passage: str) -> str:
    """
    Only call when the answer is incorrect
    Asking the student to reflect on why they chose their (correct) answer.

    Parameters:
        question_text (str): The original question.
        user_answer (str): The student's correct answer.
        passage (str): The passage content for context.

    Returns:
        str: Cantonese prompt asking the student for reflection.
    """
    prompt = f"""
        學生啱啱答啱咗一條問題，你想邀請佢講吓佢點解會咁答，鼓勵佢反思自己嘅思考過程。

        問題：{question_text}
        學生答案：{user_answer}
        文章：{passage}

        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_reading,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def respond_to_reflection(
    reflection_text: str, question_text: str, correct_answer: str, passage: str
) -> str:
    """
    Generates a response to a student's reflective answer (e.g., "why did you choose that?"),
    providing affirmation, insight, and constructive support in Cantonese.

    Parameters:
        reflection_text (str): The student's explanation or reflection.
        question_text (str): The original question.
        correct_answer (str): The model answer.
        passage (str): The relevant passage text.

    Returns:
        str: A warm Cantonese reply affirming and engaging with the student’s reasoning.
    """
    prompt = f"""
        學生啱啱回答咗你之前問佢：「你點解會咁答呢？」依家佢分享咗佢嘅諗法。

        請你根據佢嘅回應：
        1. 肯定佢願意分享自己嘅想法
        2. 評價佢嘅解釋
        3. 如果佢有啲細節未掌握，可以輕輕指出並補充

        📝 學生回應：{reflection_text}
        ❓ 原問題：{question_text}
        ✅ 標準答案：{correct_answer}
        📖 文章：{passage}

        最後鼓勵學生準備試下一題
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_reading,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def ask_open_question(question: str):
    """
    Uses LLM to return an English open-ended question followed by its warm, short Cantonese translation.

    Parameters:
        question (str): The original open-ended English question.

    Returns:
        str: English question + natural Cantonese translation.
    """
    prompt = f"""
        請你幫我將下面一條英文開放式問題翻譯成自然、親切、廣東話口語版本，語氣溫柔唔壓力、適合中學生。

        請只回應以下格式：

        {question}
        翻譯內容
        """
    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": system_prompt_open},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def respond_to_open_answer(
    user_answer: str, question_text: str, learning_objectives: str, answer: str
) -> str:
    """
    Uses LLM to respond to a student's open-ended reflection, affirming their ideas and gently
    guiding them toward the intended learning objective.

    Parameters:
        user_answer (str): The student's open-ended response.
        question_text (str): The original reflective question.
        learning_objectives (str): Key concept or idea we want them to notice.
        answer(str): Answer of the question

    Returns:
        str: A warm, dialogic Cantonese response.
    """
    prompt = f"""
        你係一位用廣東話教閱讀理解嘅老師，目標係幫助學生深入思考文章內容，提升分析能力。

        學生啱啱對以下問題作出咗一個自由式回答：
        📝 問題：{question_text}
        💬 學生回應：{user_answer}
        Model Answer: {answer}

        請你回應佢：
        1. 肯定佢嘅觀點（可以稱讚佢觀察力、情感連結、或有意思嘅比喻）
        2. 引用一句佢講過嘅句子，表示你有認真聆聽
        3. 然後溫柔咁提出你想引導佢思考嘅「學習重點」：
        🎯 教學重點：{learning_objectives}
        4. 最後可以輕輕引入參考答案作補充：

        請你用自然廣東話，語氣要親切
        """

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it",
            messages=[
                {"role": "system", "content": system_prompt_open},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ LLM error in respond_to_open_answer: {e}")
        return "多謝你嘅分享，我哋而家一齊望一望今日嘅學習重點啦～😊"


"""
##############
VOCAB EXERCISE
##############
"""


def ask_vocab_meaning_question(vocab_row: dict) -> str:
    """
    Generate message asking the student if they know the meaning of a vocabulary word.

    Parameters:
        vocab_row (dict): A single vocab record (from the vocab sheet).

    Returns:
        str: Cantonese prompt asking if the student knows the word meaning.
    """
    vocab = vocab_row["Vocabulary"]
    part_of_speech = vocab_row.get("PartOfSpeech", "").lower()
    part_of_speech_phrase = {
        "noun": "呢個名詞",
        "verb": "呢個動詞",
        "adjective": "呢個形容詞",
    }.get(part_of_speech, "呢個字")

    prompt = f"""
        你係一位以廣東話教英文閱讀嘅AI老師，教學法係以 Dialogic Education 為基礎。

        你而家嘅任務係：**直接鼓勵學生估下某個英文生字嘅意思**。

        請你問學生：
        『{vocab}』{part_of_speech_phrase}，你覺得佢大約咩意思呀？試吓估下。

        **注意事項：**
        - 唔准講「Hello」、「大家好」、「你好」等等無謂招呼語
        - 唔好畀例句、唔好解釋
        - 唔好提供語境
        - 句式要自然、貼地，好似真老師咁

        你只需要出一條問題，目的是令學生開口，睇吓佢有幾多推測能力。
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_vocab,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def give_vocab_correct_reply(vocab_row: dict) -> str:
    """
    Generate a Cantonese message that praises the student
    for answering a vocabulary word correctly and reinforces the meaning.

    Parameters:
        vocab_row (dict): The vocabulary entry that was just answered correctly.

    Returns:
        str: A warm and encouraging message in Cantonese.
    """
    vocab = vocab_row["Vocabulary"]
    part_of_speech = vocab_row["PartOfSpeech"]
    meaning_zh = vocab_row["ChineseExplaination"]
    example = vocab_row["Examples"]
    root = vocab_row["Roots"]
    mem_story = vocab_row["MemStories"]

    prompt = f"""
        學生啱啱成功回答咗 “{vocab}” 呢個 {part_of_speech} 嘅意思。

        請你肯定學生答啱咗，並教導學生
        意思: {meaning_zh}」
        例句：「{example}」
        記憶法：「{mem_story}」

        Keep it simple
        不需要要求學生造句
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_vocab,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def give_vocab_hint_or_explanation(
    vocab_row: dict, user_answer: str, attempt: int
) -> str:
    """
    Uses LLM to provide either a hint (first attempt) or a full explanation
    (second attempt) for a vocabulary word, based on student progress.

    Parameters:
        vocab_row (dict): The vocabulary entry for today.
        attempt (int): Attempt number (1 or 2).

    Returns:
        str: A friendly Cantonese teaching message.
    """
    vocab = vocab_row["Vocabulary"]
    part_of_speech = vocab_row["PartOfSpeech"]
    example = vocab_row["Examples"]
    meaning_zh = vocab_row["ChineseExplaination"]
    tip = vocab_row["Tips"]
    root = vocab_row["Roots"]
    mem_story = vocab_row["MemStories"]

    if attempt not in [1, 2]:
        raise ValueError("Attempt must be either 1 or 2.")

    if attempt == 1:
        tone = "輕鬆鼓勵"
        task = f"""
            回應學生的回答{user_answer}
            不要提供正確答案
            例句：{example}
            提示：{tip}
            Ask Studnet to try again
            """
    else:
        tone = "溫柔而清楚"
        task = f"""
            請你提供正確答案「{meaning_zh}」
            記憶故事：「{mem_story}」
            詞根：{root}
            簡短點
            """

    prompt = f"""
        學生學緊 “{vocab}” 呢個 {part_of_speech}，但未掌握意思。
        請你用{tone}語氣，{task} 。
        Keep it simple
        不需要要求學生造句
        """

    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {
                "role": "system",
                "content": system_prompt_vocab,
            },
            {"role": "user", "content": prompt},
        ],
    )
    print("💡Hint!")
    return response.choices[0].message.content.strip()
