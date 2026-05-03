import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url=os.getenv("NVIDIA_BASE_URL"),
  api_key=os.getenv("NVIDIA_API_KEY")
)

try:
    completion = client.chat.completions.create(
      model="stepfun-ai/step-3.5-flash",
      messages=[{"role":"user","content":"Analyze this item and respond in JSON: {name: 'Gold Ring'}. Provide estimated_price."}],
      temperature=1,
      top_p=0.9,
      max_tokens=500
    )
    print("API Response Object:", completion)
    print("API Response Content:", completion.choices[0].message.content)
except Exception as e:
    print("API Error:", e)
