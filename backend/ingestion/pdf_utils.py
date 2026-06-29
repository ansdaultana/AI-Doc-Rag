from pypdf import PdfReader  # extracts text from PDF files


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)  # load PDF

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()  # extract text from page

        if page_text:
            text += page_text + "\n"  # append page text

    return text  # return full document text
