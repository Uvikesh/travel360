# CodeIgniter 4 Project Structure: travel360

This document outlines the directory structure and key files for implementing the **travel360** directory using the CodeIgniter 4 framework.

## 1. Directory Structure

```text
travel360/
├── app/
│   ├── Config/
│   │   ├── Routes.php          # Route definitions for Admin, Company, and Public areas
│   │   └── Database.php        # MySQL connection settings
│   ├── Controllers/
│   │   ├── Admin/              # Admin Panel Controllers
│   │   │   ├── Dashboard.php
│   │   │   ├── Companies.php
│   │   │   ├── Categories.php
│   │   │   └── Locations.php
│   │   ├── Company/            # Company Dashboard Controllers
│   │   │   ├── Profile.php
│   │   │   └── Enquiries.php
│   │   └── Home.php            # Public facing Controllers
│   ├── Models/
│   │   ├── CompanyModel.php
│   │   ├── CategoryModel.php
│   │   ├── LocationModel.php
│   │   └── EnquiryModel.php
│   ├── Views/
│   │   ├── admin/              # Admin Panel Views
│   │   ├── company/            # Company Dashboard Views
│   │   ├── public/             # Home, Browse, and Details Views
│   │   └── layout/             # Shared Layouts (Admin Sidebar, TopNav, Footer)
│   └── Filters/
│       └── Auth.php            # Authentication middleware
├── public/
│   ├── assets/
│   │   ├── css/                # Tailwind / Compiled CSS
│   │   ├── js/                 # Interaction scripts
│   │   └── images/             # Brand and placeholder assets
│   └── index.php
├── writable/
├── .env                        # Environment variables (Base URL, DB Creds)
└── spark
```

## 2. Core Implementation Strategy

### Database Configuration (`app/Config/Database.php`)
Configure the `default` group to use the schema provided in your `DOCUMENT_29`.

### Routing (`app/Config/Routes.php`)
```php
// Public Routes
$routes->get('/', 'Home::index');
$routes->get('companies', 'Home::browse');
$routes->get('company/(:segment)', 'Home::details/$1');

// Admin Routes (Auth Required)
$routes->group('admin', ['filter' => 'auth'], function($routes) {
    $routes->get('dashboard', 'Admin\Dashboard::index');
    $routes->get('companies', 'Admin\Companies::index');
    $routes->get('categories', 'Admin\Categories::index');
    $routes->get('locations', 'Admin\Locations::index');
});

// Company Routes (Auth Required)
$routes->group('dashboard', ['filter' => 'auth'], function($routes) {
    $routes->get('/', 'Company\Profile::index');
    $routes->post('update', 'Company\Profile::update');
    $routes->get('enquiries', 'Company\Enquiries::index');
});
```

### Models Example (`app/Models/CompanyModel.php`)
```php
namespace App\Models;
use CodeIgniter\Model;

class CompanyModel extends Model
{
    protected $table = 'agents'; // Mapped to the agents table from your schema
    protected $primaryKey = 'id';
    protected $allowedFields = [
        'user_id', 'category_id', 'city_id', 'agency_name', 
        'slug', 'logo_url', 'about_text', 'status'
    ];
    protected $useTimestamps = true;
}
```