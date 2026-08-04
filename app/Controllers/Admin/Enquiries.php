<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\EnquiryModel;
use Throwable;

class Enquiries extends BaseController
{
    public function index(): string
    {
        try {
            $enquiries = (new EnquiryModel())->recentWithCompany(100);
        } catch (Throwable) {
            $enquiries = [];
        }

        return view('admin/enquiries', [
            'title' => 'Enquiries - Travel360',
            'enquiries' => $enquiries,
        ]);
    }
}
