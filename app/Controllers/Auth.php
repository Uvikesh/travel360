<?php

namespace App\Controllers;

use App\Models\CategoryModel;
use App\Models\CityModel;
use App\Models\CompanyModel;
use App\Models\UserModel;
use Throwable;

class Auth extends BaseController
{
    public function login(): string
    {
        return view('auth/login', [
            'title' => 'Sign In - Travel360',
        ]);
    }

    public function attemptLogin()
    {
        $rules = [
            'email' => 'required|valid_email',
            'password' => 'required',
        ];

        if (! $this->validate($rules)) {
            return redirect()->back()->withInput()->with('error', 'Please enter a valid email and password.');
        }

        try {
            $user = (new UserModel())->where('email', $this->request->getPost('email'))->first();
        } catch (Throwable) {
            return redirect()->back()->withInput()->with('error', 'Database is not ready. Start MySQL, create the database, then run migrations and the seeder.');
        }

        if ($user === null || ! password_verify((string) $this->request->getPost('password'), $user['password'])) {
            return redirect()->back()->withInput()->with('error', 'The email or password is incorrect.');
        }

        session()->set([
            'isLoggedIn' => true,
            'user_id' => (int) $user['id'],
            'user_name' => $user['name'],
            'user_email' => $user['email'],
            'role' => $user['role'],
        ]);

        if ($user['role'] === 'admin') {
            return redirect()->to(site_url('admin/dashboard'));
        }

        return redirect()->to(site_url('dashboard'));
    }

    public function register(): string
    {
        return view('auth/register', [
            'title' => 'Register Agency - Travel360',
            'categories' => $this->safeList(static fn () => (new CategoryModel())->orderBy('name')->findAll()),
            'cities' => $this->safeList(static fn () => (new CityModel())->withState()),
        ]);
    }

    public function storeRegister()
    {
        $rules = [
            'name' => 'required|min_length[2]',
            'email' => 'required|valid_email',
            'password' => 'required|min_length[8]',
            'agency_name' => 'required|min_length[2]',
        ];

        if (! $this->validate($rules)) {
            return redirect()->back()->withInput()->with('error', implode(' ', $this->validator->getErrors()));
        }

        $db = db_connect();
        $db->transStart();

        try {
            $userModel = new UserModel();
            $companyModel = new CompanyModel();

            $userId = $userModel->insert([
                'name' => $this->request->getPost('name'),
                'email' => $this->request->getPost('email'),
                'password' => password_hash((string) $this->request->getPost('password'), PASSWORD_DEFAULT),
                'role' => 'agent',
            ], true);

            $agencyName = (string) $this->request->getPost('agency_name');
            $companyModel->insert([
                'user_id' => $userId,
                'category_id' => $this->request->getPost('category_id') ?: null,
                'city_id' => $this->request->getPost('city_id') ?: null,
                'agency_name' => $agencyName,
                'slug' => $this->uniqueSlug($agencyName),
                'phone' => $this->request->getPost('phone'),
                'whatsapp' => $this->request->getPost('whatsapp'),
                'website_url' => $this->request->getPost('website_url'),
                'about_text' => $this->request->getPost('about_text'),
                'status' => 'pending',
            ]);

            $db->transComplete();
        } catch (Throwable) {
            $db->transRollback();

            return redirect()->back()->withInput()->with('error', 'Registration could not be saved. Make sure the database is migrated and try again.');
        }

        return redirect()->to(site_url('check-email'))->with('success', 'Your agency profile has been submitted for review.');
    }

    public function forgotPassword(): string
    {
        return view('auth/forgot_password', [
            'title' => 'Forgot Password - Travel360',
        ]);
    }

    public function sendResetLink()
    {
        return redirect()->to(site_url('check-email'))->with('success', 'If that email exists, a reset link has been prepared.');
    }

    public function checkEmail(): string
    {
        return view('auth/check_email', [
            'title' => 'Check Your Email - Travel360',
        ]);
    }

    public function emailResent(): string
    {
        return view('auth/check_email', [
            'title' => 'Email Resent - Travel360',
            'resent' => true,
        ]);
    }

    public function logout()
    {
        session()->destroy();

        return redirect()->to(site_url('/'))->with('success', 'You have been signed out.');
    }

    private function safeList(callable $callback): array
    {
        try {
            return $callback();
        } catch (Throwable) {
            return [];
        }
    }

    private function uniqueSlug(string $name): string
    {
        $base = url_title($name, '-', true);
        $slug = $base;
        $count = 2;
        $model = new CompanyModel();

        while ($model->where('slug', $slug)->first() !== null) {
            $slug = $base . '-' . $count;
            $count++;
        }

        return $slug;
    }
}
