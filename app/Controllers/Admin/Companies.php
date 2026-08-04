<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\CompanyModel;
use Throwable;

class Companies extends BaseController
{
    public function index(): string
    {
        try {
            $companies = (new CompanyModel())->directoryList();
        } catch (Throwable) {
            $companies = [];
        }

        return view('admin/companies', [
            'title' => 'Manage Companies - Travel360',
            'companies' => $companies,
        ]);
    }

    public function approve(int $id)
    {
        return $this->setStatus($id, 'approved', 'Company approved successfully.');
    }

    public function reject(int $id)
    {
        return $this->setStatus($id, 'rejected', 'Company rejected.');
    }

    public function delete(int $id)
    {
        try {
            (new CompanyModel())->delete($id);

            return redirect()->back()->with('success', 'Company deleted.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'Company could not be deleted.');
        }
    }

    private function setStatus(int $id, string $status, string $message)
    {
        try {
            (new CompanyModel())->update($id, ['status' => $status]);

            return redirect()->back()->with('success', $message);
        } catch (Throwable) {
            return redirect()->back()->with('error', 'Company status could not be updated.');
        }
    }
}
