"""
bookkeeping/ocr.py

Receipt OCR using Claude (Anthropic) or GPT-4o (OpenAI) vision APIs.
The user supplies their own API key via their account settings.

Returns a dict:
    {
        "date": "2024-03-15",        # ISO format or empty string
        "amount": "49.99",           # Net amount (excluding VAT) or total
        "vat_amount": "10.00",       # VAT amount or empty string
        "vat_rate": "20",            # VAT % or empty string
        "supplier": "Tesco PLC",     # Merchant name or empty string
        "description": "Groceries", # Brief description or empty string
        "error": None,               # Error message if extraction failed
    }
"""

import base64
import json
import re
from pathlib import Path


EXTRACTION_PROMPT = """You are a UK bookkeeping assistant. Extract the following fields from this receipt image.

Return ONLY a JSON object with these exact keys (no markdown, no explanation):
{
  "date": "<YYYY-MM-DD or empty string>",
  "amount": "<net amount as decimal string, e.g. 41.66, or total if VAT not shown>",
  "vat_amount": "<VAT amount as decimal string, e.g. 8.33, or empty string>",
  "vat_rate": "<VAT percentage as integer string, e.g. 20, or empty string>",
  "supplier": "<merchant or supplier name, or empty string>",
  "description": "<brief description of what was purchased, or empty string>"
}

Rules:
- For UK receipts: if you see a VAT line, separate net amount and VAT. Otherwise put the total in "amount".
- Date must be ISO format YYYY-MM-DD. Convert any format (e.g. 15/03/2024 → 2024-03-15).
- Amount must be a plain decimal number without currency symbol.
- If a field cannot be determined, use an empty string — never null or undefined.
"""


def _encode_file(file_field) -> tuple[str, str]:
    """Read an uploaded file and return (base64_data, media_type)."""
    file_field.seek(0)
    data = file_field.read()
    file_field.seek(0)
    encoded = base64.standard_b64encode(data).decode("utf-8")

    name = getattr(file_field, "name", "") or ""
    suffix = Path(name).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".pdf": "application/pdf",
    }
    media_type = mime_map.get(suffix, "image/jpeg")
    return encoded, media_type


def _parse_json_response(text: str) -> dict:
    """Extract JSON from a model response, tolerating markdown fences."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find the first {...} block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def _empty_result(error: str) -> dict:
    return {
        "date": "",
        "amount": "",
        "vat_amount": "",
        "vat_rate": "",
        "supplier": "",
        "description": "",
        "error": error,
    }


def extract_receipt_data(file_field, api_key: str, provider: str = "anthropic") -> dict:
    """
    Main entry point. Pass the Django FieldFile (expense.receipt) or an
    InMemoryUploadedFile, plus the user's API key and provider.
    """
    if not api_key or not api_key.strip():
        return _empty_result("No API key configured. Add your key in Account Settings.")

    try:
        b64_data, media_type = _encode_file(file_field)
    except Exception as exc:
        return _empty_result(f"Could not read receipt file: {exc}")

    try:
        if provider == "openai":
            return _extract_openai(b64_data, media_type, api_key.strip())
        else:
            return _extract_anthropic(b64_data, media_type, api_key.strip())
    except Exception as exc:
        return _empty_result(f"OCR request failed: {exc}")


def _extract_anthropic(b64_data: str, media_type: str, api_key: str) -> dict:
    """Call Anthropic Messages API with the receipt image."""
    import urllib.request
    import urllib.error

    # Claude takes images as `image` blocks and PDFs as `document` blocks
    # (native PDF support, no beta header). Build whichever matches the upload.
    if media_type == "application/pdf":
        media_block = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": b64_data,
            },
        }
    else:
        media_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            },
        }

    payload = json.dumps({
        "model": "claude-haiku-4-5",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    media_block,
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        return _empty_result(f"Anthropic API error {exc.code}: {err_body[:200]}")

    text = body["content"][0]["text"]
    try:
        data = _parse_json_response(text)
    except Exception:
        return _empty_result(f"Could not parse model response: {text[:200]}")

    data.setdefault("error", None)
    return data


def _extract_openai(b64_data: str, media_type: str, api_key: str) -> dict:
    """Call OpenAI Chat Completions API with the receipt image."""
    import urllib.request
    import urllib.error

    if media_type == "application/pdf":
        return _empty_result(
            "PDF receipts aren't supported by the OpenAI provider. Switch to the "
            "Anthropic (Claude) provider in Account Settings to scan PDFs, or upload "
            "a JPEG/PNG image."
        )

    data_url = f"data:{media_type};base64,{b64_data}"

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "high"},
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        return _empty_result(f"OpenAI API error {exc.code}: {err_body[:200]}")

    text = body["choices"][0]["message"]["content"]
    try:
        result = _parse_json_response(text)
    except Exception:
        return _empty_result(f"Could not parse model response: {text[:200]}")

    result.setdefault("error", None)
    return result
