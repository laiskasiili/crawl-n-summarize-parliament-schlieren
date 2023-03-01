import openai
import PyPDF2
import os

api_key = os.getenv("OPENAPI_KEY")
assert api_key
openai.api_key = api_key

with open("./crawler/downloads/2023-01-24_Kl.A._Hauptstrassen_fur_Alle.pdf", "rb") as f:
    pdf = PyPDF2.PdfReader(f)
    full_text = (
        " ".join(page.extract_text() for page in pdf.pages)
        .replace("\n", " ")
        .replace("\r", " ")
    )
print(full_text)
assert len(full_text) // 4 < 3500

summary = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Summarize the this german text briefly and use no more than 120 words: {full_text}",
    temperature=0.5,
    max_tokens=500,
    # best_of=3,
)
summary_text = summary["choices"][0]["text"]
print("-------------")
print(summary_text)
