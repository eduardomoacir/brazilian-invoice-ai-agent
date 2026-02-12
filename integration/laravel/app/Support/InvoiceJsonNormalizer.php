<?php

namespace App\Support;

final class InvoiceJsonNormalizer
{
    /**
     * @param array<string, mixed> $payload
     * @return array<string, mixed>
     */
    public static function normalizePayload(array $payload): array
    {
        $normalized = self::normalizeKeys($payload);

        return [
            'numero_fatura' => self::asString($normalized['numero_fatura'] ?? null),
            'data_emissao' => self::asString($normalized['data_emissao'] ?? null),
            'data_vencimento' => self::asString($normalized['data_vencimento'] ?? null),
            'empresa_emissora' => self::sanitizeParty($normalized['empresa_emissora'] ?? null),
            'cliente' => self::sanitizeParty($normalized['cliente'] ?? null),
            'itens' => self::sanitizeItems($normalized['itens'] ?? null),
            'tributos' => self::sanitizeTaxes($normalized['tributos'] ?? null),
            'subtotal_itens_centavos' => self::toInt($normalized['subtotal_itens_centavos'] ?? null),
            'valor_total_fatura_centavos' => self::toInt($normalized['valor_total_fatura_centavos'] ?? null),
        ];
    }

    private static function normalizeKeys(mixed $value): mixed
    {
        if (!is_array($value)) {
            return $value;
        }

        if (array_is_list($value)) {
            return array_map(static fn (mixed $item): mixed => self::normalizeKeys($item), $value);
        }

        $output = [];
        foreach ($value as $key => $item) {
            $normalizedKey = self::normalizeKey((string) $key);
            $output[$normalizedKey] = self::normalizeKeys($item);
        }
        return $output;
    }

    private static function normalizeKey(string $key): string
    {
        $key = trim($key);
        $key = str_replace(' ', '_', $key);
        $ascii = iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $key);
        return is_string($ascii) && $ascii !== '' ? $ascii : $key;
    }

    /**
     * @return array{nome:string,cnpj:string,endereco:string}
     */
    private static function sanitizeParty(mixed $value): array
    {
        $source = is_array($value) ? $value : [];
        return [
            'nome' => self::asString($source['nome'] ?? null),
            'cnpj' => self::asString($source['cnpj'] ?? null),
            'endereco' => self::asString($source['endereco'] ?? null),
        ];
    }

    /**
     * @return array<int, array{descricao:string,quantidade:int,valor_unitario_centavos:int,valor_total_item_centavos:int}>
     */
    private static function sanitizeItems(mixed $value): array
    {
        if (!is_array($value) || !array_is_list($value)) {
            return [];
        }

        $out = [];
        foreach ($value as $item) {
            if (!is_array($item)) {
                continue;
            }
            $out[] = [
                'descricao' => self::asString($item['descricao'] ?? null),
                'quantidade' => self::toInt($item['quantidade'] ?? null),
                'valor_unitario_centavos' => self::toInt($item['valor_unitario_centavos'] ?? null),
                'valor_total_item_centavos' => self::toInt($item['valor_total_item_centavos'] ?? null),
            ];
        }

        return $out;
    }

    /**
     * @return array<int, array{tipo:string,valor_centavos:int}>
     */
    private static function sanitizeTaxes(mixed $value): array
    {
        if (!is_array($value) || !array_is_list($value)) {
            return [];
        }

        $out = [];
        foreach ($value as $tax) {
            if (!is_array($tax)) {
                continue;
            }
            $out[] = [
                'tipo' => self::asString($tax['tipo'] ?? null),
                'valor_centavos' => self::toInt($tax['valor_centavos'] ?? null),
            ];
        }

        return $out;
    }

    private static function asString(mixed $value): string
    {
        if ($value === null) {
            return '';
        }
        return trim((string) $value);
    }

    private static function toInt(mixed $value): int
    {
        if ($value === null) {
            return 0;
        }
        if (is_bool($value)) {
            return (int) $value;
        }
        if (is_int($value)) {
            return $value;
        }
        if (is_float($value)) {
            return (int) round($value);
        }
        if (is_string($value)) {
            $raw = str_replace(' ', '', trim($value));
            if ($raw === '') {
                return 0;
            }
            if (str_contains($raw, ',') && str_contains($raw, '.')) {
                $raw = str_replace('.', '', $raw);
                $raw = str_replace(',', '.', $raw);
            } elseif (str_contains($raw, ',')) {
                $raw = str_replace(',', '.', $raw);
            }

            if (!is_numeric($raw)) {
                return 0;
            }

            return (int) round((float) $raw);
        }
        return 0;
    }
}
