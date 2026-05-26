import mistralai.workflows as workflows
from mistralai.workflows.plugins.mistralai import mistralai_ocr
from mistralai.workflows.plugins.mistralai.activities import mistralai_models

from .cyber_models import FileType


@workflows.activity()
async def ocr_document(file_url: str, file_type: FileType) -> str:
    """
    Lit le texte d’un PDF ou d’une image.

    OCR = Optical Character Recognition.
    L’URL doit être publique.
    """

    print("DEBUG - start ocr_document:", file_url)

    if file_type == "pdf":
        document = {
            "type": "document_url",
            "document_url": file_url,
        }
    else:
        document = {
            "type": "image_url",
            "image_url": file_url,
        }

    request = mistralai_models.OCRRequest(
        model="mistral-ocr-latest",
        document=document,
    )

    try:
        ocr_result = await mistralai_ocr(request)
    except Exception as error:
        raise RuntimeError(
            f"OCR Mistral impossible pour {file_url}: {error}"
        ) from error

    print("DEBUG - end ocr_document")
    print("DEBUG - OCR result type:", type(ocr_result))

    if hasattr(ocr_result, "pages"):
        texts: list[str] = []

        for page in ocr_result.pages:
            if hasattr(page, "markdown") and page.markdown:
                texts.append(page.markdown)
            elif hasattr(page, "text") and page.text:
                texts.append(page.text)
            else:
                texts.append(str(page))

        return "\n\n".join(texts)

    if hasattr(ocr_result, "markdown"):
        return str(ocr_result.markdown)

    if hasattr(ocr_result, "text"):
        return str(ocr_result.text)

    return str(ocr_result)