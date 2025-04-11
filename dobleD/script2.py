from openai import OpenAI

client = OpenAI(api_key="<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>", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)