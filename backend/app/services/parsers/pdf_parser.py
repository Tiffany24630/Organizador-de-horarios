import pdfplumber

def extract_text(pdf_path: str):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_tables(pdf_path: str):
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_tables()

            if extracted:
                tables.extend(extracted)

    return tables