from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .pdf_parser import extract_text_from_pdf, parse_credit_card

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse(file: UploadFile):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)
    data = parse_credit_card(text)
    return data
