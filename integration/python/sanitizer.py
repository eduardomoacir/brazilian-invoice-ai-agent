from __future__ import annotations

import math
import unicodedata
from typing import Any, Dict, List

ROOT_KEYS = {
    "numero_fatura",
    "data_emissao",
    "data_vencimento",
    "empresa_emissora",
    "cliente",
    "itens",
    "tributos",
    "subtotal_itens_centavos",
    "valor_total_fatura_centavos",
}
PARTY_KEYS = {"nome", "cnpj", "endereco"}
ITEM_KEYS = {
    "descricao",
    "quantidade",
    "valor_unitario_centavos",
    "valor_total_item_centavos",
}
TAX_KEYS = {"tipo", "valor_centavos"}
MOJIBAKE_MARKERS = ("Ã", "Â", "Ð", "�")


def normalize_key(key: str) -> str:
    normalized = key.strip().replace(" ", "_")
    normalized = (
        unicodedata.normalize("NFKD", normalized)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return normalized


def normalize_keys(value: Any) -> Any:
    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for key, item in value.items():
            out[normalize_key(str(key))] = normalize_keys(item)
        return out
    if isinstance(value, list):
        return [normalize_keys(item) for item in value]
    return value


def to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            return default
        return int(round(value))
    if isinstance(value, str):
        raw = value.strip().replace(" ", "")
        if raw == "":
            return default

        if "," in raw and "." in raw:
            raw = raw.replace(".", "").replace(",", ".")
        elif "," in raw and "." not in raw:
            raw = raw.replace(",", ".")

        try:
            parsed = float(raw)
        except ValueError:
            return default

        if not math.isfinite(parsed):
            return default
        return int(round(parsed))
    return default


def _as_string(value: Any) -> str:
    if value is None:
        return ""
    return _fix_mojibake(str(value).strip())


def _fix_mojibake(text: str) -> str:
    if text == "":
        return text
    if not any(marker in text for marker in MOJIBAKE_MARKERS):
        return text
    try:
        fixed = text.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return text
    original_noise = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)
    fixed_noise = sum(fixed.count(marker) for marker in MOJIBAKE_MARKERS)
    return fixed if fixed_noise < original_noise else text


def _sanitize_party(value: Any) -> Dict[str, str]:
    source = value if isinstance(value, dict) else {}
    return {
        "nome": _as_string(source.get("nome")),
        "cnpj": _as_string(source.get("cnpj")),
        "endereco": _as_string(source.get("endereco")),
    }


def _sanitize_items(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    out: List[Dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "descricao": _as_string(item.get("descricao")),
                "quantidade": to_int(item.get("quantidade")),
                "valor_unitario_centavos": to_int(item.get("valor_unitario_centavos")),
                "valor_total_item_centavos": to_int(item.get("valor_total_item_centavos")),
            }
        )
    return out


def _sanitize_taxes(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []

    out: List[Dict[str, Any]] = []
    for tax in value:
        if not isinstance(tax, dict):
            continue
        out.append(
            {
                "tipo": _as_string(tax.get("tipo")),
                "valor_centavos": to_int(tax.get("valor_centavos")),
            }
        )
    return out


def sanitize_extracted_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_keys(raw)

    payload: Dict[str, Any] = {
        "numero_fatura": _as_string(normalized.get("numero_fatura")),
        "data_emissao": _as_string(normalized.get("data_emissao")),
        "data_vencimento": _as_string(normalized.get("data_vencimento")),
        "empresa_emissora": _sanitize_party(normalized.get("empresa_emissora")),
        "cliente": _sanitize_party(normalized.get("cliente")),
        "itens": _sanitize_items(normalized.get("itens")),
        "tributos": _sanitize_taxes(normalized.get("tributos")),
        "subtotal_itens_centavos": to_int(normalized.get("subtotal_itens_centavos")),
        "valor_total_fatura_centavos": to_int(normalized.get("valor_total_fatura_centavos")),
    }

    return payload


def assert_payload_contract(payload: Dict[str, Any]) -> None:
    assert set(payload.keys()) == ROOT_KEYS, "Invalid root keys"

    for party_key in ("empresa_emissora", "cliente"):
        party = payload.get(party_key)
        assert isinstance(party, dict), f"{party_key} must be object"
        assert set(party.keys()) == PARTY_KEYS, f"{party_key} keys invalid"
        assert "itens" not in party and "tributos" not in party

    items = payload.get("itens")
    assert isinstance(items, list), "itens must be array"
    for item in items:
        assert isinstance(item, dict), "item must be object"
        assert set(item.keys()) == ITEM_KEYS, "item keys invalid"
        assert "itens" not in item and "tributos" not in item
        assert isinstance(item["quantidade"], int), "quantidade must be int"
        assert isinstance(item["valor_unitario_centavos"], int), "valor_unitario_centavos must be int"
        assert isinstance(item["valor_total_item_centavos"], int), "valor_total_item_centavos must be int"

    taxes = payload.get("tributos")
    assert isinstance(taxes, list), "tributos must be array"
    for tax in taxes:
        assert isinstance(tax, dict), "tributo must be object"
        assert set(tax.keys()) == TAX_KEYS, "tributo keys invalid"
        assert "itens" not in tax and "tributos" not in tax
        assert isinstance(tax["valor_centavos"], int), "valor_centavos must be int"

    assert isinstance(payload["subtotal_itens_centavos"], int), "subtotal_itens_centavos must be int"
    assert isinstance(payload["valor_total_fatura_centavos"], int), "valor_total_fatura_centavos must be int"
