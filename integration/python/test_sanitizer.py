from __future__ import annotations

from sanitizer import assert_payload_contract, sanitize_extracted_payload


def main() -> int:
    raw = {
        "numero_fatura": "FAT-2026-00125",
        "data_emissao": "2026-02-10",
        "data_vencimento": "2026-02-25",
        "empresa_emissora": {
            "nome": "Tech Solutions Brasil Ltda",
            "cnpj": "12.345.678/0001-90",
            "endereco": "Rua X",
            "itens": [],
            "tributos": [],
        },
        "cliente": {
            "nome": "Cliente",
            "cnpj": "98.765.432/0001-55",
            "endereco": "Rua Y",
            "itens": [],
            "tributos": [],
        },
        "itens": [
            {
                "descrição": "Servico A",
                "quantidade": "1.0",
                "valor_unitário_centavos": 350000.0,
                "valor_total_item_centavos": "350000",
                "itens": [],
                "tributos": [],
            }
        ],
        "tributos": [
            {
                "tipo": "ISS",
                "valor_centavos": "17500.0",
                "itens": [],
                "tributos": [],
            }
        ],
        "subtotal_itens_centavos": 560000.0,
        "valor_total_fatura_centavos": "586675.0",
        "extra_campo_indevido": "remove-me",
    }

    payload = sanitize_extracted_payload(raw)
    assert_payload_contract(payload)

    assert payload["itens"][0]["quantidade"] == 1
    assert payload["itens"][0]["valor_unitario_centavos"] == 350000
    assert payload["itens"][0]["valor_total_item_centavos"] == 350000
    assert payload["tributos"][0]["valor_centavos"] == 17500
    assert payload["subtotal_itens_centavos"] == 560000
    assert payload["valor_total_fatura_centavos"] == 586675
    assert payload["itens"][0]["descricao"] == "Servico A"

    mojibake_payload = sanitize_extracted_payload(
        {
            "numero_fatura": "X",
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-02",
            "empresa_emissora": {
                "nome": "Tech SoluÃ§Ãµes Brasil Ltda",
                "cnpj": "12.345.678/0001-90",
                "endereco": "Rua das Tecnologias, 1500 â FlorianÃ³polis â SC",
            },
            "cliente": {
                "nome": "ContÃ¡bil Moderna",
                "cnpj": "98.765.432/0001-55",
                "endereco": "Av. Empresarial, 220 â FlorianÃ³polis â SC",
            },
            "itens": [],
            "tributos": [],
            "subtotal_itens_centavos": 0,
            "valor_total_fatura_centavos": 0,
        }
    )
    assert mojibake_payload["empresa_emissora"]["nome"] == "Tech Soluções Brasil Ltda"
    assert mojibake_payload["cliente"]["nome"] == "Contábil Moderna"
    assert "Florianópolis" in mojibake_payload["cliente"]["endereco"]

    print("sanitizer-test-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
