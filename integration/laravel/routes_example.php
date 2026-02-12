<?php

use App\Http\Controllers\InvoiceExtractController;
use Illuminate\Support\Facades\Route;

Route::post('/api/extract/invoice', [InvoiceExtractController::class, 'store']);
