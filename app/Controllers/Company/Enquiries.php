<?php

namespace App\Controllers\Company;

use App\Controllers\BaseController;
use App\Models\CompanyModel;
use App\Models\EnquiryModel;
use Throwable;

class Enquiries extends BaseController
{
    public function index(): string
    {
        $company = null;
        $enquiries = [];

        try {
            $company = (new CompanyModel())->findForUser((int) session()->get('user_id'));

            if ($company !== null) {
                $enquiries = (new EnquiryModel())
                    ->where('agent_id', $company['id'])
                    ->orderBy('created_at', 'DESC')
                    ->findAll();
            }
        } catch (Throwable) {
            session()->setFlashdata('error', 'Database is not ready. Start MySQL and run migrations to view enquiries.');
        }

        return view('company/enquiries', [
            'title' => 'Company Enquiries - Travel360',
            'company' => $company,
            'enquiries' => $enquiries,
        ]);
    }
}
