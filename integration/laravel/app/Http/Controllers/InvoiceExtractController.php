<?php

namespace App\Http\Controllers;

use App\Data\InvoiceExtractDTO;
use App\Http\Requests\InvoiceExtractRequest;
use App\Services\LlamaExtractRunner;
use App\Support\InvoiceJsonNormalizer;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Storage;
use Throwable;

class InvoiceExtractController extends Controller
{
    public function __construct(private readonly LlamaExtractRunner $runner)
    {
    }

    public function store(InvoiceExtractRequest $request): JsonResponse
    {
        $storedPath = null;

        try {
            $storedPath = Storage::disk('local')->putFile('tmp', $request->file('file'));
            if (!is_string($storedPath) || $storedPath === '') {
                throw new \RuntimeException('Could not persist temporary upload.');
            }

            $absolutePath = Storage::disk('local')->path($storedPath);
            $result = $this->runner->run($absolutePath, [
                'agent_name' => $request->input('agent_name'),
                'fallback_schema' => $request->input('fallback_schema'),
            ]);

            $dto = InvoiceExtractDTO::fromArray(InvoiceJsonNormalizer::normalizePayload($result));

            return response()->json([
                'ok' => true,
                'data' => $dto->toArray(),
            ]);
        } catch (Throwable $e) {
            return response()->json([
                'ok' => false,
                'message' => 'Invoice extraction failed.',
                'error' => config('app.debug') ? $e->getMessage() : null,
            ], 422);
        } finally {
            if (is_string($storedPath) && $storedPath !== '') {
                Storage::disk('local')->delete($storedPath);
            }
        }
    }
}
