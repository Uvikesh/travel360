<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\CategoryModel;
use App\Models\CompanyModel;
use App\Models\EnquiryModel;
use Throwable;

class Dashboard extends BaseController
{
    public function index(): string
    {
        $stats = [
            'totalCompanies' => 0,
            'approvedCompanies' => 0,
            'pendingCompanies' => 0,
            'categories' => 0,
            'recentEnquiries' => [],
            'pendingListings' => [],
        ];

        try {
            $companyModel = new CompanyModel();
            $enquiryModel = new EnquiryModel();

            $stats['totalCompanies'] = $companyModel->countAllResults();
            $stats['approvedCompanies'] = (new CompanyModel())->where('status', 'approved')->countAllResults();
            $stats['pendingCompanies'] = (new CompanyModel())->where('status', 'pending')->countAllResults();
            $stats['categories'] = (new CategoryModel())->countAllResults();
            $stats['recentEnquiries'] = $enquiryModel->recentWithCompany(6);
            $stats['pendingListings'] = (new CompanyModel())->directoryList(['status' => 'pending'], 6);
        } catch (Throwable) {
            $stats['databaseNotice'] = 'Start MySQL and run migrations to populate live admin metrics.';
        }

        return view('admin/dashboard', [
            'title' => 'Admin Dashboard - Travel360',
            'stats' => $stats,
        ]);
    }
}
