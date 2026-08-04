<?php

namespace App\Filters;

use CodeIgniter\Filters\FilterInterface;
use CodeIgniter\HTTP\RedirectResponse;
use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;

class AuthFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null): ?RedirectResponse
    {
        if (! session()->get('isLoggedIn')) {
            return redirect()->to(site_url('login'))->with('error', 'Please sign in to continue.');
        }

        if ($arguments !== null && $arguments !== []) {
            $role = (string) session()->get('role');

            if (! in_array($role, $arguments, true)) {
                return redirect()->to(site_url('/'))->with('error', 'You do not have permission to open that area.');
            }
        }

        return null;
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null): void
    {
    }
}
