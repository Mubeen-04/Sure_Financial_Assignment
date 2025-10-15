import io
import re
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract
import os
from typing import Dict, Any

# ----------------- Configure Tesseract -----------------
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.isfile(DEFAULT_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH

# ----------------- Known card variants mapping -----------------
CARD_VARIANTS = {
    "ICICI": ["Coral", "Ruby", "Sapphiro", "Emerald", "Platinum", "Gold", "Titanium", "Signature"],
    "HDFC": ["Regalia", "Millennia", "Infinia", "Platinum", "Emerald"],
    "SBI": ["Prime", "Elite", "Signature"],
    "AXIS": ["Ace", "Select", "Priority"],
    "KOTAK": ["Essentia", "Privilege", "Sapphiro", "Royale"],
}

# ----------------- Extract text from PDF -----------------
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception:
        pass

    if not text.strip():
        # Fallback OCR
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    # Normalize spaces and line breaks
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ----------------- Find card variant function -----------------
def find_card_variant(text: str, issuer: str) -> str:
    variants = CARD_VARIANTS.get(issuer.upper(), [])
    for variant in variants:
        pattern = rf"({issuer}\s+)?{re.escape(variant)}"
        if re.search(pattern, text, re.IGNORECASE):
            return variant
    return "N/A"

# ----------------- Parse key fields -----------------
def parse_credit_card(text: str) -> Dict[str, Any]:
    result = {
        "issuer": "N/A",
        "cardNo": "N/A",
        "cardVariant": "N/A",
        "statementPeriod": "N/A",      
        "paymentDueDate": "N/A",
        "totalAmountDue": "N/A",
        "minimumAmountDue": "N/A",
        "transactions": []
    }

    # ----------------- Issuer detection -----------------
    issuer_match = re.search(r"\b(ICICI|HDFC|SBI|AXIS|KOTAK)\b", text, re.IGNORECASE)
    issuer = None
    if issuer_match:
        issuer = issuer_match.group(1).upper()
        result["issuer"] = issuer

    # ----------------- Card Number + Variant -----------------
    card_line_match = re.search(
        r"Card\s+(?:Variant\s*[:\-]?\s*)?([A-Za-z]+)?\s*\(?(?:XXXX[-\s]*XXXX[-\s]*XXXX[-\s]*(\d{4}))\)?",
        text,
        re.IGNORECASE,
    )
    if card_line_match:
        if card_line_match.group(1):
            result["cardVariant"] = card_line_match.group(1).strip()
        else:
            if issuer:
                result["cardVariant"] = find_card_variant(text, issuer)
        result["cardNo"] = f"XXXX-XXXX-XXXX-{card_line_match.group(2)}"
    else:
        # fallback card number
        card_no_match = re.search(r"XXXX[-\s]*XXXX[-\s]*XXXX[-\s]*(\d{4})", text, re.IGNORECASE)
        if card_no_match:
            result["cardNo"] = f"XXXX-XXXX-XXXX-{card_no_match.group(1)}"
        # fallback variant
        if issuer:
            result["cardVariant"] = find_card_variant(text, issuer)

    # ----------------- Statement Period -----------------
    statement_period_match = re.search(
        r"Statement\s+Period[:\-]?\s*([0-9]{1,2}[-\s]?[A-Za-z]{3,}[-\s]?\d{4})\s*(?:-|to)\s*([0-9]{1,2}[-\s]?[A-Za-z]{3,}[-\s]?\d{4})",
        text,
        re.IGNORECASE,
    )
    if statement_period_match:
        result["statementPeriod"] = (
            statement_period_match.group(1).strip() + " - " + statement_period_match.group(2).strip()
        )

    # ----------------- Payment Due Date -----------------
    payment_date_match = re.search(r"(Payment Due Date|Due Date)[:\-]?\s*([A-Za-z0-9 ,/-]+)", text, re.IGNORECASE)
    if payment_date_match:
        date_match = re.search(r"\d{1,2}\s*[-/]?\s*[A-Za-z]{3,}\s*[-/]?\s*\d{4}", payment_date_match.group(2))
        if date_match:
            result["paymentDueDate"] = date_match.group(0).strip()
        else:
            result["paymentDueDate"] = payment_date_match.group(2).strip()

    # ----------------- Total & Minimum Amount Due -----------------
    total_due_match = re.search(r"Total Amount Due[:\-]?\s*(?:INR\s*)?([\d,]+\.\d{2})", text, re.IGNORECASE)
    if total_due_match:
        result["totalAmountDue"] = total_due_match.group(1)

    min_due_match = re.search(r"Minimum Amount Due[:\-]?\s*(?:INR\s*)?([\d,]+\.\d{2})", text, re.IGNORECASE)
    if min_due_match:
        result["minimumAmountDue"] = min_due_match.group(1)

    # ----------------- Transactions (flexible) -----------------
    txn_pattern = re.compile(
        r"(\d{2}[-/][A-Za-z]{3}[-/]\d{4})"        
        r"\s+([A-Z ]+)?"                          
        r"\s+([\w\s&\-.]+?)"                      
        r"\s+([\d,]+\.\d{2}|-)"                   
        r"(?:\s+([\d,]+\.\d{2}|-))?",             
        re.IGNORECASE
    )
    for m in txn_pattern.finditer(text):
        date = m.group(1)
        txn_type = (m.group(2) or "").strip().upper()
        description = m.group(3).strip()
        amount1 = None if m.group(4) == "-" else m.group(4)
        amount2 = None if (m.group(5) and m.group(5) == "-") else m.group(5)

        # Decide debit/credit if type not present
        if not txn_type:
            if amount1 and not amount2:
                txn_type = "DEBIT"
            elif amount2 and not amount1:
                txn_type = "CREDIT"
            else:
                txn_type = "N/A"

        result["transactions"].append({
            "date": date,
            "type": txn_type,
            "description": description,
            "debit": amount1 if txn_type == "DEBIT" else None,
            "credit": amount1 if txn_type == "CREDIT" else amount2
        })

    return result

# ----------------- Main parse function -----------------
def parse_pdf_bytes(pdf_bytes: bytes) -> Dict[str, Any]:
    text = extract_text_from_pdf(pdf_bytes)
    return parse_credit_card(text)
