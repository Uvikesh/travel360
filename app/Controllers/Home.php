<?php

namespace App\Controllers;

use App\Models\CategoryModel;
use App\Models\CityModel;
use App\Models\CompanyModel;
use App\Models\EnquiryModel;
use Throwable;

class Home extends BaseController
{
    public function index(): string
    {
        $companies = $this->withDatabaseFallback(
            static fn () => (new CompanyModel())->directoryList(['status' => 'approved'], 4),
            $this->demoCompanies()
        );

        return view('public/home', [
            'title' => 'Travel360 - Find trusted travel companies',
            'featuredCompanies' => $companies,
        ]);
    }

    public function companies(): string
    {
        $filters = [
            'status' => 'approved',
            'q' => trim((string) $this->request->getGet('q')),
            'category_id' => $this->request->getGet('category_id'),
            'city_id' => $this->request->getGet('city_id'),
        ];

        $companies = $this->withDatabaseFallback(
            static fn () => (new CompanyModel())->directoryList($filters),
            $this->filterDemoCompanies($filters)
        );

        return view('public/companies', [
            'title' => 'Browse Companies - Travel360',
            'companies' => $companies,
            'categories' => $this->withDatabaseFallback(static fn () => (new CategoryModel())->orderBy('name')->findAll(), $this->demoCategories()),
            'cities' => $this->withDatabaseFallback(static fn () => (new CityModel())->withState(), $this->demoCities()),
            'filters' => $filters,
        ]);
    }

    public function details(string $slug): string
    {
        $company = $this->withDatabaseFallback(
            static fn () => (new CompanyModel())->findBySlug($slug),
            $this->findDemoCompany($slug)
        );

        if ($company === null) {
            throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound('Company not found.');
        }

        return view('public/company_details', [
            'title' => $company['agency_name'] . ' - Travel360',
            'company' => $company,
        ]);
    }

    public function enquire(string $slug)
    {
        $rules = [
            'sender_name' => 'required|max_length[255]',
            'sender_email' => 'required|valid_email|max_length[255]',
            'message' => 'required|min_length[10]',
        ];

        if (! $this->validate($rules)) {
            return redirect()->back()->withInput()->with('error', implode(' ', $this->validator->getErrors()));
        }

        $company = $this->withDatabaseFallback(
            static fn () => (new CompanyModel())->findBySlug($slug),
            $this->findDemoCompany($slug)
        );

        if ($company === null) {
            return redirect()->to(site_url('companies'))->with('error', 'That company could not be found.');
        }

        try {
            (new EnquiryModel())->insert([
                'agent_id' => $company['id'],
                'sender_name' => $this->request->getPost('sender_name'),
                'sender_email' => $this->request->getPost('sender_email'),
                'message' => $this->request->getPost('message'),
                'created_at' => date('Y-m-d H:i:s'),
            ]);
        } catch (Throwable) {
            return redirect()->back()->with('success', 'Thanks. Your enquiry has been captured in demo mode; connect the database to save it.');
        }

        return redirect()->back()->with('success', 'Thanks. Your enquiry has been sent to ' . $company['agency_name'] . '.');
    }

    public function about(): string
    {
        return view('public/about', [
            'title' => 'About Travel360',
        ]);
    }

    public function contact(): string
    {
        if ($this->request->getMethod() === 'post') {
            return view('public/contact', [
                'title' => 'Contact Travel360',
                'sent' => true,
            ]);
        }

        return view('public/contact', [
            'title' => 'Contact Travel360',
            'sent' => false,
        ]);
    }

    private function withDatabaseFallback(callable $callback, mixed $fallback): mixed
    {
        try {
            return $callback();
        } catch (Throwable) {
            return $fallback;
        }
    }

    private function demoCompanies(): array
    {
        return [
            [
                'id' => 1,
                'agency_name' => 'Horizon & Co Travel',
                'slug' => 'horizon-co-travel',
                'category_name' => 'Luxury Escapes',
                'city_name' => 'Panaji',
                'state_name' => 'Goa',
                'rating' => '4.90',
                'status' => 'approved',
                'phone' => '+91 98765 43001',
                'whatsapp' => '+91 98765 43001',
                'website_url' => 'https://example.com/horizon',
                'logo_url' => 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=80',
                'about_text' => 'Bespoke beach escapes, private villas, cruises, and celebratory itineraries across India, Europe, and the islands.',
            ],
            [
                'id' => 2,
                'agency_name' => 'Coastal Compass Holidays',
                'slug' => 'coastal-compass-holidays',
                'category_name' => 'Family Holidays',
                'city_name' => 'Kochi',
                'state_name' => 'Kerala',
                'rating' => '4.70',
                'status' => 'approved',
                'phone' => '+91 98765 43002',
                'whatsapp' => '+91 98765 43002',
                'website_url' => 'https://example.com/coastal',
                'logo_url' => 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80',
                'about_text' => 'Slow travel, family-friendly stays, guided food walks, and culture-rich itineraries along India\'s coast.',
            ],
            [
                'id' => 3,
                'agency_name' => 'Summitline Adventures',
                'slug' => 'summitline-adventures',
                'category_name' => 'Adventure Tours',
                'city_name' => 'Manali',
                'state_name' => 'Himachal Pradesh',
                'rating' => '4.80',
                'status' => 'approved',
                'phone' => '+91 98765 43003',
                'whatsapp' => '+91 98765 43003',
                'website_url' => 'https://example.com/summitline',
                'logo_url' => 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80',
                'about_text' => 'Trekking, bike trips, alpine camps, and high-altitude adventures planned with safety-first local teams.',
            ],
        ];
    }

    private function demoCategories(): array
    {
        return [
            ['id' => 1, 'name' => 'Luxury Escapes', 'slug' => 'luxury-escapes'],
            ['id' => 2, 'name' => 'Adventure Tours', 'slug' => 'adventure-tours'],
            ['id' => 3, 'name' => 'Family Holidays', 'slug' => 'family-holidays'],
        ];
    }

    private function demoCities(): array
    {
        return [
            ['id' => 1, 'name' => 'Panaji', 'state_name' => 'Goa'],
            ['id' => 2, 'name' => 'Kochi', 'state_name' => 'Kerala'],
            ['id' => 3, 'name' => 'Manali', 'state_name' => 'Himachal Pradesh'],
        ];
    }

    private function filterDemoCompanies(array $filters): array
    {
        $companies = $this->demoCompanies();
        $term = strtolower((string) ($filters['q'] ?? ''));

        if ($term === '') {
            return $companies;
        }

        return array_values(array_filter($companies, static function (array $company) use ($term): bool {
            return str_contains(strtolower(implode(' ', [
                $company['agency_name'],
                $company['category_name'],
                $company['city_name'],
                $company['state_name'],
                $company['about_text'],
            ])), $term);
        }));
    }

    private function findDemoCompany(string $slug): ?array
    {
        foreach ($this->demoCompanies() as $company) {
            if ($company['slug'] === $slug) {
                return $company;
            }
        }

        return null;
    }
}
