from dataclasses import asdict
from datetime import datetime
from domain.entities.document import Document

import fitz  # pymupdf
import re
import json


TOPIC_HEADERS = [
    "Sobre o Agi",
    "Conta Corrente",
    "Empréstimos",
    "Cartão de Débito e Crédito",
    "Seguros",
    "Seguro de vida",
    "Seguro residencial",
    "Seguro auto",
    "Proteção urbana",
    "Investimentos",
    "Benefício INSS",
]


def extract_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)

    pages = []

    for page in doc:
        pages.append(page.get_text())

    return "\n".join(pages)


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")

    # remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_inline_text(text: str) -> str:
    """
    Remove line breaks and normalize spaces.
    """
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_topics(text: str):
    escaped = [re.escape(h) for h in TOPIC_HEADERS]

    pattern = rf"(?=^({'|'.join(escaped)})\s*$)"

    parts = re.split(pattern, text, flags=re.MULTILINE)

    topics = []

    i = 1
    while i < len(parts):
        topic = parts[i].strip()
        content = parts[i + 1].strip()

        topics.append((topic, content))

        i += 2

    return topics


def extract_qa_pairs(topic_text: str):
    """
    Extract:
      Question?
      Answer text...

    until next question.
    """

    lines = [
        line.strip()
        for line in topic_text.splitlines()
        if line.strip()
    ]

    qa_pairs = []

    current_question = None
    current_answer = []

    for line in lines:

        # detect question
        if line.endswith("?"):

            # save previous QA
            if current_question:
                qa_pairs.append(
                    (
                        clean_inline_text(current_question),
                        clean_inline_text(" ".join(current_answer))
                    )
                )

            current_question = line
            current_answer = []

        else:
            if current_question:
                current_answer.append(line)

    # save last pair
    if current_question:
        qa_pairs.append(
            (
                clean_inline_text(current_question),
                clean_inline_text(" ".join(current_answer))
            )
        )

    return qa_pairs


def build_documents(pdf_path: str) -> list[Document]:
    text = extract_pdf_text(pdf_path)

    text = normalize_text(text)

    topics = split_topics(text)

    documents = []

    for topic_name, topic_content in topics:

        qa_pairs = extract_qa_pairs(topic_content)

        for question, answer in qa_pairs:

            doc = Document(
                title=question,
                content=answer,
                date=datetime.now(),
                source=pdf_path,
                tag=topic_name.lower(),
            )

            documents.append(doc)

    return documents


def save_documents_to_json(documents: list[Document], output_path: str):
    data = [asdict(doc) for doc in documents]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    docs = build_documents("faq.pdf")

    save_documents_to_json(docs, "documents.json")

    print(f"Saved {len(docs)} documents to documents.json")