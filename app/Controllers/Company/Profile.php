<?php

namespace App\Controllers\Company;

use App\Controllers\BaseController;
use App\Models\CategoryModel;
use App\Models\CityModel;
use App\Models\CompanyModel;
use Throwable;

class Profile extends BaseController
{
    public function index(): string
    {
        $company = null;
        $categories = [];
        $cities = [];

        try {
            $company = (new CompanyModel())->findForUser((int) session()->get('user_id'));
            $categories = (new CategoryModel())->orderBy('name')->findAll();
            $cities = (new CityModel())->withState();
        } catch (Throwable) {
            session()->setFlashdata('error', 'Database is not ready. Start MySQL and run migrations to manage your profile.');
        }

        return view('company/dashboard', [
            'title' => 'Company Dashboard - Travel360',
            'company' => $company,
            'categories' => $categories,
            'cities' => $cities,
        ]);
    }

    public function update()
    {
        $id = (int) $this->request->getPost('id');

        if ($id < 1) {
            return redirect()->back()->with('error', 'Company profile could not be found.');
        }

        try {
            (new CompanyModel())->update($id, [
                'category_id' => $this->request->getPost('category_id') ?: null,
                'city_id' => $this->request->getPost('city_id') ?: null,
                'agency_name' => $this->request->getPost('agency_name'),
                'about_text' => $this->request->getPost('about_text'),
                'phone' => $this->request->getPost('phone'),
                'whatsapp' => $this->request->getPost('whatsapp'),
                'website_url' => $this->request->getPost('website_url'),
                'logo_url' => $this->request->getPost('logo_url'),
            ]);

            return redirect()->back()->with('success', 'Profile updated.');
        } catch (Throwable) {
            return redirect()->back()->withInput()->with('error', 'Profile could not be updated.');
        }
    }
}
