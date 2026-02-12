<?php

namespace App\Data;

use InvalidArgumentException;

final class InvoiceExtractDTO
{
    /**
     * @param array<int, array{descricao:string,quantidade:int,valor_unitario_centavos:int,valor_total_item_centavos:int}> $itens
     * @param array<int, array{tipo:string,valor_centavos:int}> $tributos
     */
    public function __construct(
        public readonly string $numeroFatura,
        public readonly string $dataEmissao,
        public readonly string $dataVencimento,
        public readonly array $empresaEmissora,
        public readonly array $cliente,
        public readonly array $itens,
        public readonly array $tributos,
        public readonly int $subtotalItensCentavos,
        public readonly int $valorTotalFaturaCentavos,
    ) {
    }

    public static function fromArray(array $data): self
    {
        $required = [
            'numero_fatura',
            'data_emissao',
            'data_vencimento',
            'empresa_emissora',
            'cliente',
            'itens',
            'tributos',
            'subtotal_itens_centavos',
            'valor_total_fatura_centavos',
        ];

        foreach ($required as $key) {
            if (!array_key_exists($key, $data)) {
                throw new InvalidArgumentException("Missing required key: {$key}");
            }
        }

        if (!is_array($data['empresa_emissora']) || !is_array($data['cliente'])) {
            throw new InvalidArgumentException('empresa_emissora and cliente must be objects.');
        }

        if (!is_array($data['itens']) || !is_array($data['tributos'])) {
            throw new InvalidArgumentException('itens and tributos must be arrays.');
        }

        $itens = array_values(array_filter($data['itens'], static fn (mixed $v): bool => is_array($v)));
        $tributos = array_values(array_filter($data['tributos'], static fn (mixed $v): bool => is_array($v)));

        return new self(
            numeroFatura: (string) $data['numero_fatura'],
            dataEmissao: (string) $data['data_emissao'],
            dataVencimento: (string) $data['data_vencimento'],
            empresaEmissora: [
                'nome' => (string) ($data['empresa_emissora']['nome'] ?? ''),
                'cnpj' => (string) ($data['empresa_emissora']['cnpj'] ?? ''),
                'endereco' => (string) ($data['empresa_emissora']['endereco'] ?? ''),
            ],
            cliente: [
                'nome' => (string) ($data['cliente']['nome'] ?? ''),
                'cnpj' => (string) ($data['cliente']['cnpj'] ?? ''),
                'endereco' => (string) ($data['cliente']['endereco'] ?? ''),
            ],
            itens: array_map(
                static fn (array $item): array => [
                    'descricao' => (string) ($item['descricao'] ?? ''),
                    'quantidade' => (int) ($item['quantidade'] ?? 0),
                    'valor_unitario_centavos' => (int) ($item['valor_unitario_centavos'] ?? 0),
                    'valor_total_item_centavos' => (int) ($item['valor_total_item_centavos'] ?? 0),
                ],
                $itens
            ),
            tributos: array_map(
                static fn (array $tax): array => [
                    'tipo' => (string) ($tax['tipo'] ?? ''),
                    'valor_centavos' => (int) ($tax['valor_centavos'] ?? 0),
                ],
                $tributos
            ),
            subtotalItensCentavos: (int) $data['subtotal_itens_centavos'],
            valorTotalFaturaCentavos: (int) $data['valor_total_fatura_centavos'],
        );
    }

    public function toArray(): array
    {
        return [
            'numero_fatura' => $this->numeroFatura,
            'data_emissao' => $this->dataEmissao,
            'data_vencimento' => $this->dataVencimento,
            'empresa_emissora' => $this->empresaEmissora,
            'cliente' => $this->cliente,
            'itens' => $this->itens,
            'tributos' => $this->tributos,
            'subtotal_itens_centavos' => $this->subtotalItensCentavos,
            'valor_total_fatura_centavos' => $this->valorTotalFaturaCentavos,
        ];
    }
}
