"""Parser for the TPRM workflow."""

import mistralai.workflows as workflows

from ..common.ocr import ocr_document
from ..cyber_ticket.utils import is_valid_url
from .models import ParsedSupplierContent, TPRMInput


@workflows.activity()
async def parse_input(input_data: TPRMInput) -> list[ParsedSupplierContent]:
    """
    Convert supplier inputs into normalized contents.

    Each supplier can have:
    - a description
    - text documents
    - questionnaires
    - emails
    - PDF/image files
    """

    print("DEBUG - start TPRM parse_input")

    parsed_contents: list[ParsedSupplierContent] = []

    for supplier in input_data.suppliers:
        print(f"DEBUG - processing supplier: {supplier.supplier_id}")

        if supplier.description:
            parsed_contents.append(
                ParsedSupplierContent(
                    supplier_id=supplier.supplier_id,
                    supplier_name=supplier.supplier_name,
                    source_type="text",
                    content=supplier.description,
                    document_id="description",
                )
            )

        for document in supplier.documents:
            if document.content:
                parsed_contents.append(
                    ParsedSupplierContent(
                        supplier_id=supplier.supplier_id,
                        supplier_name=supplier.supplier_name,
                        source_type="text",
                        content=document.content,
                        document_id=document.document_id,
                    )
                )

            if document.file_url or document.file_type:
                if not document.file_url or not document.file_type:
                    raise ValueError(
                        f"{supplier.supplier_id}/{document.document_id}: "
                        "file_url and file_type must be provided together."
                    )

                if not is_valid_url(document.file_url):
                    raise ValueError(
                        f"{supplier.supplier_id}/{document.document_id}: "
                        f"invalid URL: {document.file_url}"
                    )

                parsed_contents.append(
                    ParsedSupplierContent(
                        supplier_id=supplier.supplier_id,
                        supplier_name=supplier.supplier_name,
                        source_type=document.file_type,
                        content=document.file_url,
                        document_id=document.document_id,
                    )
                )

    if not parsed_contents:
        raise ValueError("No supplier content to analyze.")

    print("DEBUG - end TPRM parse_input")
    print("DEBUG - parsed count:", len(parsed_contents))

    return parsed_contents


async def build_raw_content(
    parsed_contents: list[ParsedSupplierContent],
) -> str:
    """
    Build the final text sent to the model.

    PDF/images go through OCR first.
    """

    parts: list[str] = []

    for parsed in parsed_contents:
        print(
            "DEBUG - TPRM Processing "
            f"{parsed.supplier_id} / {parsed.source_type}"
        )

        if parsed.source_type in ["pdf", "image"]:
            extracted_text = await ocr_document(
                parsed.content,
                parsed.source_type,
            )

            if not extracted_text.strip():
                raise ValueError(f"OCR empty for file: {parsed.content}")

            print("DEBUG - extracted_text length:", len(extracted_text))

            content = extracted_text[:2500]
        else:
            content = parsed.content

        parts.append(
            f"--- SUPPLIER: {parsed.supplier_id} | "
            f"NAME: {parsed.supplier_name or 'unknown'} | "
            f"DOCUMENT: {parsed.document_id or 'unknown'} | "
            f"SOURCE: {parsed.source_type} ---\n"
            f"{content}"
        )

    raw_content = "\n\n".join(parts)

    print(f"DEBUG - TPRM raw_content length: {len(raw_content)} characters")

    return raw_content
