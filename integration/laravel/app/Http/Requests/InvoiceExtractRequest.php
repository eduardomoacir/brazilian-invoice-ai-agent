<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class InvoiceExtractRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'file' => [
                'required',
                'file',
                'mimes:pdf,docx,png,jpg,jpeg',
                'mimetypes:application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/png,image/jpeg',
                'max:10240',
            ],
            'agent_name' => ['nullable', 'string', 'max:255'],
            'fallback_schema' => ['nullable', 'string', 'max:500'],
        ];
    }

    protected function prepareForValidation(): void
    {
        if (!$this->filled('agent_name')) {
            $this->merge(['agent_name' => env('AGENT_NAME', 'Nota Fiscal')]);
        }
    }
}
