import cv2
import re
import json
import pytesseract
import unicodedata
import google.generativeai as genai

# ---------- Configure Gemini ----------
genai.configure(api_key="Gemini key")

# ---------- Step 1: Preprocess Image ----------
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    if image.shape[1] < 800:
        image = cv2.resize(image, (800, int(image.shape[0] * (800 / image.shape[1]))))

    image = cv2.GaussianBlur(image, (3, 3), 0)
    temp_path = "temp_processed.png"
    cv2.imwrite(temp_path, image)
    return temp_path

# ---------- Step 2: OCR Text Extraction ----------
def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    return normalize_text(text)

# ---------- Step 3: Normalize Unicode Text ----------
def normalize_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace('\u2022', '').replace('\u00a0', ' ')
    return text.strip()

# ---------- Step 4: Gemini Extraction ----------
def extract_with_gemini(text, doc_type):
    """
    Use Gemini to extract document details in JSON format based on the selected document type.
    """
    # Dynamic field mapping based on doc_type
    doc_field_map = {
        "aadhaar": ["aadhaar_number", "name", "date_of_birth", "gender", "address"],
        "pan": ["pan_number", "name", "date_of_birth", "father_name"],
        "salary": ["employee_name", "net_salary", "month"],
        "bank": ["bank_account_number", "bank_name", "ifsc_code"],
        "address": ["name", "address"]
    }

    expected_fields = doc_field_map.get(doc_type.lower(), [])

    prompt = f"""
You are an expert document parser.
Given the OCR text below, extract the following fields for a {doc_type} document:
{', '.join(expected_fields)}

Rules:
- Return a valid JSON object with these keys.
- If a field is missing, return it as null.
- Do not include any extra text or formatting.

OCR Text:
{text}
"""

    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    output = response.text.strip()

    # Remove accidental code block markers
    output = re.sub(r"```json|```", "", output).strip()

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"gemini_error": "Failed to parse JSON", "raw_output": output}

# ---------- Step 5: Master Processor ----------
def process_document(image_path, doc_type):
    try:
        processed_image_path = preprocess_image(image_path)
        text = extract_text_from_image(processed_image_path)
    except Exception as e:
        return {
            "error": str(e),
            "document_type": doc_type,
            "text_extracted": "",
            "gemini_extracted_fields": {}
        }

    gemini_extracted = extract_with_gemini(text, doc_type)

    return {
        "document_type": doc_type,
        "text_extracted": text,
        "gemini_extracted_fields": gemini_extracted
    }
