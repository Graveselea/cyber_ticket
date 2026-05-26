import mistralai.workflows as workflows

from .cyber_models import CyberTicketInput, ParsedContent
from .cyber_ocr import ocr_document
from .cyber_utils import is_valid_url, logs_to_text


@workflows.activity()
async def parse_input(input_data: CyberTicketInput) -> list[ParsedContent]:
    """
    Transforme l’input utilisateur en contenus normalisés.

    Chaque ticket peut produire plusieurs contenus :
    - texte
    - logs
    - PDF/image
    """

    print("DEBUG - start parse_input")

    parsed_contents: list[ParsedContent] = []

    for ticket in input_data.tickets:
        print(f"DEBUG - processing ticket: {ticket.ticket_id}")

        if ticket.ticket_text:
            parsed_contents.append(
                ParsedContent(
                    ticket_id=ticket.ticket_id,
                    source_type="text",
                    content=ticket.ticket_text,
                )
            )

        if ticket.logs:
            parsed_contents.append(
                ParsedContent(
                    ticket_id=ticket.ticket_id,
                    source_type="logs",
                    content=logs_to_text(ticket.logs),
                )
            )

        if ticket.file_url or ticket.file_type:
            if not ticket.file_url or not ticket.file_type:
                raise ValueError(
                    f"{ticket.ticket_id}: file_url et file_type doivent "
                    "être fournis ensemble."
                )

            if not is_valid_url(ticket.file_url):
                raise ValueError(
                    f"{ticket.ticket_id}: URL invalide : {ticket.file_url}"
                )

            parsed_contents.append(
                ParsedContent(
                    ticket_id=ticket.ticket_id,
                    source_type=ticket.file_type,
                    content=ticket.file_url,
                )
            )

    if not parsed_contents:
        raise ValueError("Aucun contenu à analyser.")

    print("DEBUG - end parse_input")
    print("DEBUG - parsed count:", len(parsed_contents))

    return parsed_contents


async def build_raw_content(parsed_contents: list[ParsedContent]) -> str:
    """
    Construit le texte final envoyé au modèle.

    Les PDF/images passent par OCR.
    """

    parts: list[str] = []

    for parsed in parsed_contents:
        print(
            "DEBUG - Processing "
            f"{parsed.ticket_id} / {parsed.source_type}"
        )

        if parsed.source_type in ["pdf", "image"]:
            extracted_text = await ocr_document(
                parsed.content,
                parsed.source_type,
            )

            if not extracted_text.strip():
                raise ValueError(
                    f"OCR vide pour le fichier : {parsed.content}"
                )

            print("DEBUG - extracted_text length:", len(extracted_text))

            content = extracted_text[:2500]
        else:
            content = parsed.content

        parts.append(
            f"--- TICKET: {parsed.ticket_id} | "
            f"SOURCE: {parsed.source_type} ---\n"
            f"{content}"
        )

    raw_content = "\n\n".join(parts)

    print(f"DEBUG - Final raw_content length: {len(raw_content)} characters")

    return raw_content