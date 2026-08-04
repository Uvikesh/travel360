<?php

use CodeIgniter\Router\RouteCollection;

/**
 * @var RouteCollection $routes
 */
$routes->get('/', 'Home::index');
$routes->get('companies', 'Home::companies');
$routes->get('company/(:segment)', 'Home::details/$1');
$routes->post('company/(:segment)/enquire', 'Home::enquire/$1');
$routes->get('about', 'Home::about');
$routes->match(['get', 'post'], 'contact', 'Home::contact');

$routes->get('login', 'Auth::login');
$routes->post('login', 'Auth::attemptLogin');
$routes->get('register', 'Auth::register');
$routes->post('register', 'Auth::storeRegister');
$routes->get('forgot-password', 'Auth::forgotPassword');
$routes->post('forgot-password', 'Auth::sendResetLink');
$routes->get('check-email', 'Auth::checkEmail');
$routes->get('email-resent', 'Auth::emailResent');
$routes->get('logout', 'Auth::logout');

$routes->group('admin', ['filter' => 'auth:admin'], static function ($routes) {
    $routes->get('dashboard', 'Admin\Dashboard::index');
    $routes->get('companies', 'Admin\Companies::index');
    $routes->post('companies/(:num)/approve', 'Admin\Companies::approve/$1');
    $routes->post('companies/(:num)/reject', 'Admin\Companies::reject/$1');
    $routes->post('companies/(:num)/delete', 'Admin\Companies::delete/$1');
    $routes->get('categories', 'Admin\Categories::index');
    $routes->post('categories', 'Admin\Categories::create');
    $routes->post('categories/(:num)/delete', 'Admin\Categories::delete/$1');
    $routes->get('locations', 'Admin\Locations::index');
    $routes->post('locations/states', 'Admin\Locations::createState');
    $routes->post('locations/cities', 'Admin\Locations::createCity');
    $routes->post('locations/cities/(:num)/delete', 'Admin\Locations::deleteCity/$1');
    $routes->get('enquiries', 'Admin\Enquiries::index');
});

$routes->group('dashboard', ['filter' => 'auth:agent,admin'], static function ($routes) {
    $routes->get('/', 'Company\Profile::index');
    $routes->post('update', 'Company\Profile::update');
    $routes->get('enquiries', 'Company\Enquiries::index');
});
