from openai import OpenAI
from dotenv import load_dotenv
import os 
from life_wrapped.models import DayRecord
from datetime import datetime



load_dotenv()

client = OpenAI(
  api_key=os.getenv("DEEPSEEK_KEY"),
  base_url="https://openrouter.ai/api/v1",
)

def format_daily_prompt(days):
    prompt_lines = []

    for day in days:
        entry = f"Date: {day.dt}\nHighlight: {day.highlight}\nDay Score: {day.day_score}\n"
        prompt_lines.append(entry)

    # Join into a single prompt string
    return "\n".join(prompt_lines)
days=[DayRecord(dt=datetime(2025, 5, 15), day_score=8.0, highlight='in n out gift card from trivia night', sleep=3, movement=1, spiritual=2.0), DayRecord(dt=datetime(2025, 5, 26), day_score=8.75, highlight='biking ', sleep=4, movement=4, spiritual=1.0), DayRecord(dt=datetime(2025, 5, 30), day_score=7.2, highlight='blew a flat tire, gardened a bit with Ian', sleep=3, movement=3, spiritual=2.0), DayRecord(dt=datetime(2025, 5, 31), day_score=7.2, highlight='sunrise hike, talking with will about his life struggles', sleep=1, movement=4, spiritual=3.0)]
prompt = format_daily_prompt(days)
print(prompt)


def generate_response(prompt):
    # request goes to DeepSeek, not OpenAI
    completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
        {"role": "system", "content": "You are a life coach and behavioural doctor for a client in her twenties."},
        {"role": "user", "content": prompt}
    ],
    stream=False
    )
    return completion.choices[0].message.content

# result = generate_response(prompt)
# print(result)


    