<?php

namespace App\Services;

use App\Support\InvoiceJsonNormalizer;
use Illuminate\Support\Facades\Artisan;
use RuntimeException;

class LlamaExtractRunner
{
    /**
     * @param array<string, mixed> $options
     * @return array<string, mixed>
     */
    public function run(string $path, array $options = []): array
    {
        $params = [
            'path' => $path,
            '--json' => true,
        ];

        $params['--agent-name'] = (string) ($options['agent_name'] ?? env('AGENT_NAME', 'Nota Fiscal'));

        if (!empty($options['fallback_schema'])) {
            $params['--fallback-schema'] = (string) $options['fallback_schema'];
        }

        $exitCode = Artisan::call('llama:extract-invoice', $params);
        if ($exitCode !== 0) {
            $output = trim(Artisan::output());
            throw new RuntimeException($output !== '' ? $output : 'Laravel runner failed.');
        }

        $output = trim(Artisan::output());
        $decoded = json_decode($output, true);
        if (!is_array($decoded)) {
            throw new RuntimeException('Runner returned invalid JSON.');
        }

        return InvoiceJsonNormalizer::normalizePayload($decoded);
    }
}
