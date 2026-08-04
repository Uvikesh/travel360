<?php

namespace App\Models;

use CodeIgniter\Model;

class CompanyModel extends Model
{
    protected $table = 'agents';
    protected $primaryKey = 'id';
    protected $returnType = 'array';
    protected $allowedFields = [
        'user_id',
        'category_id',
        'city_id',
        'agency_name',
        'slug',
        'logo_url',
        'about_text',
        'phone',
        'whatsapp',
        'website_url',
        'rating',
        'status',
    ];
    protected $useTimestamps = true;

    protected $validationRules = [
        'agency_name' => 'required|max_length[255]',
        'slug' => 'required|max_length[255]|is_unique[agents.slug,id,{id}]',
        'status' => 'permit_empty|in_list[pending,approved,rejected]',
    ];

    public function directoryList(array $filters = [], ?int $limit = null): array
    {
        $builder = $this->db->table('agents');
        $builder
            ->select('agents.*, users.name AS owner_name, users.email, categories.name AS category_name, cities.name AS city_name, states.name AS state_name')
            ->join('users', 'users.id = agents.user_id', 'left')
            ->join('categories', 'categories.id = agents.category_id', 'left')
            ->join('cities', 'cities.id = agents.city_id', 'left')
            ->join('states', 'states.id = cities.state_id', 'left');

        if (($filters['status'] ?? null) !== null) {
            $builder->where('agents.status', $filters['status']);
        }

        if (($filters['category_id'] ?? null) !== null && $filters['category_id'] !== '') {
            $builder->where('agents.category_id', (int) $filters['category_id']);
        }

        if (($filters['city_id'] ?? null) !== null && $filters['city_id'] !== '') {
            $builder->where('agents.city_id', (int) $filters['city_id']);
        }

        if (($filters['q'] ?? '') !== '') {
            $term = trim((string) $filters['q']);
            $builder->groupStart()
                ->like('agents.agency_name', $term)
                ->orLike('agents.about_text', $term)
                ->orLike('categories.name', $term)
                ->orLike('cities.name', $term)
                ->orLike('states.name', $term)
                ->groupEnd();
        }

        $builder
            ->orderBy('agents.status = "pending"', 'DESC', false)
            ->orderBy('agents.rating', 'DESC')
            ->orderBy('agents.agency_name', 'ASC');

        if ($limit !== null) {
            $builder->limit($limit);
        }

        return $builder->get()->getResultArray();
    }

    public function findBySlug(string $slug): ?array
    {
        $result = $this->directoryList([
            'status' => null,
            'q' => '',
        ]);

        foreach ($result as $company) {
            if ($company['slug'] === $slug) {
                return $company;
            }
        }

        return null;
    }

    public function findForUser(int $userId): ?array
    {
        return $this->where('user_id', $userId)->first();
    }
}
