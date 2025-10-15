# Credit Card PDF Parser

A web application to extract key details and transactions from credit card PDF statements using **Python (FastAPI)** for backend parsing and **React** for the frontend.

---

## Features

- Upload PDF credit card statements from multiple banks (ICICI, HDFC, SBI, Axis, Kotak).  
- Automatically extract:  
  - Issuer  
  - Card Number (last 4 digits)  
  - Card Variant  
  - Statement Period  
  - Payment Due Date  
  - Total Amount Due  
  - Minimum Amount Due  
  - Transaction history (Date, Type, Description, Debit, Credit)  
- Drag & drop support for PDFs.  
- Clean, responsive frontend built in React.  
- Fallback OCR using Tesseract for scanned PDFs.  
- Sample PDFs are included in the repo for testing.

---

## Tech Stack

- **Backend:** Python, FastAPI, pdfplumber, pdf2image, pytesseract  
- **Frontend:** React, HTML, CSS  
- **OCR:** Tesseract OCR (Windows)  

---

## Installation

### Backend

1. Clone the repo:

```bash
git clone <repo_url>
cd backend
````

2. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Make sure Tesseract OCR is installed:

* Download from [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* Update the path in `pdf_parser.py` if necessary:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

5. Run the backend server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Frontend

1. Navigate to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the React app:

```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Usage

1. Drag & drop a credit card PDF statement into the upload area, or click to select a file.
2. Click **Upload & Parse**.
3. The parsed details will appear below, including transactions.
4. You can test the parser with the **sample PDFs included** in this repository.

---

## File Structure

```
Credit_Card_PDF_Parser/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   └── pdf_parser.py     # PDF parsing logic
│   ├── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── PdfUpload.js
│   │   └── PdfUpload.css
│   ├── package.json
├── sample_pdfs/              # Folder containing sample PDF statements
├── README.md
```

---

## Notes

* Works best with **standardized PDF statements**.
* OCR fallback allows parsing scanned PDFs but may reduce accuracy.
* Currently supports banks: **ICICI, HDFC, SBI, Axis, Kotak**.
* Statement Period is automatically extracted when available.
* Sample PDFs are provided for testing and reference.

---

## License

This project is **MIT Licensed**.

```
## Screenshots
<img width="1417" height="725" alt="Screenshot 2025-10-15 181732" src="https://github.com/user-attachments/assets/b34a29f2-a052-491d-8833-e1205624e1fc" />

<img width="1416" height="729" alt="Screenshot 2025-10-15 181724" src="https://github.com/user-attachments/assets/2f915254-9eef-410d-a472-d8ea7fa9c8cc" />


