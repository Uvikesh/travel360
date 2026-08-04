<?php

namespace App\Models;

use CodeIgniter\Model;

class CityModel extends Model
{
    protected $table = 'cities';
    protected $primaryKey = 'id';
    protected $returnType = 'array';
    protected $allowedFields = ['state_id', 'name'];

    protected $validationRules = [
        'state_id' => 'required|is_natural_no_zero',
        'name' => 'required|max_length[100]',
    ];

    public function withState(): array
    {
        return $this->select('cities.*, states.name AS state_name')
            ->join('states', 'states.id = cities.state_id', 'left')
            ->orderBy('states.name', 'ASC')
            ->orderBy('cities.name', 'ASC')
            ->findAll();
    }
}
