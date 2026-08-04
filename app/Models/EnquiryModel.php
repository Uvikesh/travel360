<?php

namespace App\Models;

use CodeIgniter\Model;

class EnquiryModel extends Model
{
    protected $table = 'enquiries';
    protected $primaryKey = 'id';
    protected $returnType = 'array';
    protected $allowedFields = ['agent_id', 'sender_name', 'sender_email', 'message'];
    protected $useTimestamps = false;
    protected $createdField = 'created_at';

    protected $validationRules = [
        'agent_id' => 'required|is_natural_no_zero',
        'sender_name' => 'required|max_length[255]',
        'sender_email' => 'required|valid_email|max_length[255]',
        'message' => 'required|min_length[10]',
    ];

    public function recentWithCompany(int $limit = 20): array
    {
        return $this->select('enquiries.*, agents.agency_name')
            ->join('agents', 'agents.id = enquiries.agent_id', 'left')
            ->orderBy('enquiries.created_at', 'DESC')
            ->findAll($limit);
    }
}
