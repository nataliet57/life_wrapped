from openai import OpenAI
from dotenv import load_dotenv
import os 
from models import DayRecord
from datetime import datetime



load_dotenv()

client = OpenAI(
  api_key=os.getenv("DEEPSEEK_KEY"),
  base_url="https://openrouter.ai/api/v1",
)

def format_daily_prompt(days: [DayRecord]):
    prompt_lines = []

    for day in days:
        entry = f"Date: {day.dt}\nHighlight: {day.highlight}\nDay Score: {day.day_score}\n"
        prompt_lines.append(entry)

    # Join into a single prompt string
    return "\n".join(prompt_lines)
prompt = format_daily_prompt(days)


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

result = generate_response(prompt)
# print(result)


    