<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

class Travel360Seeder extends Seeder
{
    public function run(): void
    {
        $now = date('Y-m-d H:i:s');

        $adminId = $this->ensureUser('Travel360 Admin', 'admin@travel360.local', 'admin', $now);
        $horizonUserId = $this->ensureUser('Aarav Mehta', 'horizon@travel360.local', 'agent', $now);
        $coastalUserId = $this->ensureUser('Maya Iyer', 'coastal@travel360.local', 'agent', $now);
        $summitUserId = $this->ensureUser('Nina Rao', 'summit@travel360.local', 'agent', $now);

        $luxuryId = $this->ensureCategory('Luxury Escapes', 'luxury-escapes');
        $adventureId = $this->ensureCategory('Adventure Tours', 'adventure-tours');
        $familyId = $this->ensureCategory('Family Holidays', 'family-holidays');

        $goaId = $this->ensureState('Goa');
        $keralaId = $this->ensureState('Kerala');
        $himachalId = $this->ensureState('Himachal Pradesh');

        $panajiId = $this->ensureCity($goaId, 'Panaji');
        $kochiId = $this->ensureCity($keralaId, 'Kochi');
        $manaliId = $this->ensureCity($himachalId, 'Manali');

        $horizonAgentId = $this->ensureAgent([
            'user_id' => $horizonUserId,
            'category_id' => $luxuryId,
            'city_id' => $panajiId,
            'agency_name' => 'Horizon & Co Travel',
            'slug' => 'horizon-co-travel',
            'logo_url' => 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=400&q=80',
            'about_text' => 'Bespoke beach escapes, private villas, cruises, and celebratory itineraries across India, Europe, and the islands.',
            'phone' => '+91 98765 43001',
            'whatsapp' => '+91 98765 43001',
            'website_url' => 'https://example.com/horizon',
            'rating' => 4.90,
            'status' => 'approved',
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        $coastalAgentId = $this->ensureAgent([
            'user_id' => $coastalUserId,
            'category_id' => $familyId,
            'city_id' => $kochiId,
            'agency_name' => 'Coastal Compass Holidays',
            'slug' => 'coastal-compass-holidays',
            'logo_url' => 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80',
            'about_text' => 'Slow travel, family-friendly stays, guided food walks, and culture-rich itineraries along India\'s coast.',
            'phone' => '+91 98765 43002',
            'whatsapp' => '+91 98765 43002',
            'website_url' => 'https://example.com/coastal',
            'rating' => 4.70,
            'status' => 'approved',
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        $this->ensureAgent([
            'user_id' => $summitUserId,
            'category_id' => $adventureId,
            'city_id' => $manaliId,
            'agency_name' => 'Summitline Adventures',
            'slug' => 'summitline-adventures',
            'logo_url' => 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=400&q=80',
            'about_text' => 'Trekking, bike trips, alpine camps, and high-altitude adventures planned with safety-first local teams.',
            'phone' => '+91 98765 43003',
            'whatsapp' => '+91 98765 43003',
            'website_url' => 'https://example.com/summitline',
            'rating' => 4.80,
            'status' => 'pending',
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        $this->ensureEnquiry($horizonAgentId, 'Priya Shah', 'priya@example.com', 'We are planning a honeymoon in Greece and Italy for late October. Can you share suggested packages?', $now);
        $this->ensureEnquiry($coastalAgentId, 'Daniel Thomas', 'daniel@example.com', 'Looking for a relaxed Kerala family itinerary with child-friendly hotels and transfers.', $now);
        unset($adminId);
    }

    private function ensureUser(string $name, string $email, string $role, string $now): int
    {
        $table = $this->db->table('users');
        $existing = $table->where('email', $email)->get()->getRowArray();

        if ($existing !== null) {
            return (int) $existing['id'];
        }

        $table->insert([
            'name' => $name,
            'email' => $email,
            'password' => password_hash('password123', PASSWORD_DEFAULT),
            'role' => $role,
            'created_at' => $now,
            'updated_at' => $now,
        ]);

        return (int) $this->db->insertID();
    }

    private function ensureCategory(string $name, string $slug): int
    {
        $table = $this->db->table('categories');
        $existing = $table->where('slug', $slug)->get()->getRowArray();

        if ($existing !== null) {
            return (int) $existing['id'];
        }

        $table->insert(['name' => $name, 'slug' => $slug]);

        return (int) $this->db->insertID();
    }

    private function ensureState(string $name): int
    {
        $table = $this->db->table('states');
        $existing = $table->where('name', $name)->get()->getRowArray();

        if ($existing !== null) {
            return (int) $existing['id'];
        }

        $table->insert(['name' => $name]);

        return (int) $this->db->insertID();
    }

    private function ensureCity(int $stateId, string $name): int
    {
        $table = $this->db->table('cities');
        $existing = $table->where('state_id', $stateId)->where('name', $name)->get()->getRowArray();

        if ($existing !== null) {
            return (int) $existing['id'];
        }

        $table->insert(['state_id' => $stateId, 'name' => $name]);

        return (int) $this->db->insertID();
    }

    private function ensureAgent(array $data): int
    {
        $table = $this->db->table('agents');
        $existing = $table->where('slug', $data['slug'])->get()->getRowArray();

        if ($existing !== null) {
            return (int) $existing['id'];
        }

        $table->insert($data);

        return (int) $this->db->insertID();
    }

    private function ensureEnquiry(int $agentId, string $name, string $email, string $message, string $now): void
    {
        $table = $this->db->table('enquiries');
        $existing = $table
            ->where('agent_id', $agentId)
            ->where('sender_email', $email)
            ->get()
            ->getRowArray();

        if ($existing !== null) {
            return;
        }

        $table->insert([
            'agent_id' => $agentId,
            'sender_name' => $name,
            'sender_email' => $email,
            'message' => $message,
            'created_at' => $now,
        ]);
    }
}
