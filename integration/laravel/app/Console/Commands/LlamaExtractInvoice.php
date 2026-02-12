<?php

namespace App\Console\Commands;

use App\Support\InvoiceJsonNormalizer;
use Illuminate\Console\Command;
use Illuminate\Support\Str;
use Symfony\Component\Process\Process;

class LlamaExtractInvoice extends Command
{
    protected $signature = 'llama:extract-invoice
        {path : Path to invoice file}
        {--agent-name=Nota Fiscal : Published LlamaCloud agent name}
        {--fallback-schema=../../schema.json : Fallback schema JSON path}
        {--out= : Explicit output path}
        {--json : Print JSON only}';

    protected $description = 'Run Python LlamaExtract script and return normalized invoice JSON.';

    public function handle(): int
    {
        $apiKey = env('LLAMA_CLOUD_API_KEY');
        if (!is_string($apiKey) || trim($apiKey) === '') {
            $this->error('Missing LLAMA_CLOUD_API_KEY.');
            return self::FAILURE;
        }

        $inputPath = $this->resolvePath((string) $this->argument('path'));
        if (!is_file($inputPath)) {
            $this->error("File not found: {$inputPath}");
            return self::FAILURE;
        }

        $python = (string) env('LLAMA_EXTRACT_PYTHON', 'python3');
        $script = $this->resolvePath((string) env('LLAMA_EXTRACT_SCRIPT', 'integration/python/extract_invoice.py'));
        if (!is_file($script)) {
            $this->error("Python script not found: {$script}");
            return self::FAILURE;
        }

        $explicitOut = (string) $this->option('out');
        $outputPath = $explicitOut !== '' ? $this->resolvePath($explicitOut) : $this->defaultOutPath();
        $createdTempOut = $explicitOut === '';

        $args = [
            $python,
            $script,
            '--file', $inputPath,
            '--agent-name', (string) $this->option('agent-name'),
            '--fallback-schema', $this->resolvePath((string) $this->option('fallback-schema')),
            '--out', $outputPath,
        ];

        $process = new Process($args, base_path(), ['LLAMA_CLOUD_API_KEY' => $apiKey], null, 300);
        $process->run();

        if (!$process->isSuccessful()) {
            $stderr = trim($process->getErrorOutput());
            $stdout = trim($process->getOutput());
            $message = $stderr !== '' ? $stderr : $stdout;
            $this->error($message !== '' ? $message : 'Python extraction failed.');
            if ($createdTempOut && is_file($outputPath)) {
                @unlink($outputPath);
            }
            return self::FAILURE;
        }

        if (!is_file($outputPath)) {
            $this->error("Expected output file not found: {$outputPath}");
            return self::FAILURE;
        }

        $raw = file_get_contents($outputPath);
        if (!is_string($raw)) {
            $this->error('Could not read extraction output.');
            if ($createdTempOut && is_file($outputPath)) {
                @unlink($outputPath);
            }
            return self::FAILURE;
        }

        $decoded = json_decode($raw, true);
        if (!is_array($decoded)) {
            $this->error('Extraction output is not valid JSON.');
            if ($createdTempOut && is_file($outputPath)) {
                @unlink($outputPath);
            }
            return self::FAILURE;
        }

        $normalized = InvoiceJsonNormalizer::normalizePayload($decoded);
        $jsonOnly = (bool) $this->option('json');

        if ($jsonOnly) {
            $this->line(json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
        } else {
            $this->info('Extraction finished.');
            $this->line(json_encode($normalized, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
        }

        if ($createdTempOut && is_file($outputPath)) {
            @unlink($outputPath);
        }

        return self::SUCCESS;
    }

    private function defaultOutPath(): string
    {
        $dir = storage_path('app/tmp');
        if (!is_dir($dir)) {
            @mkdir($dir, 0755, true);
        }

        return $dir . DIRECTORY_SEPARATOR . 'extract_' . Str::uuid() . '.json';
    }

    private function resolvePath(string $path): string
    {
        if ($path === '') {
            return '';
        }

        if (Str::startsWith($path, ['/', '\\']) || preg_match('/^[A-Za-z]:[\/\\\\]/', $path) === 1) {
            return $path;
        }

        return base_path($path);
    }
}
