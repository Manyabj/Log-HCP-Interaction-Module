from groq import Groq
from app.config import settings

print("API key loaded:", bool(settings.groq_api_key))
print("Reasoning model:", settings.groq_reasoning_model)
print("Chat model:", settings.groq_chat_model)

client = Groq(api_key=settings.groq_api_key)

response = client.chat.completions.create(
    model=settings.groq_chat_model,
    messages=[
        {"role": "user", "content": "Reply with only the word: Hello"}
    ]
)

print(response.choices[0].message.content)