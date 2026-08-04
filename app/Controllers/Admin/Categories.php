<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\CategoryModel;
use Throwable;

class Categories extends BaseController
{
    public function index(): string
    {
        try {
            $categories = (new CategoryModel())->orderBy('name')->findAll();
        } catch (Throwable) {
            $categories = [];
        }

        return view('admin/categories', [
            'title' => 'Manage Categories - Travel360',
            'categories' => $categories,
        ]);
    }

    public function create()
    {
        $name = trim((string) $this->request->getPost('name'));

        if ($name === '') {
            return redirect()->back()->with('error', 'Category name is required.');
        }

        try {
            (new CategoryModel())->insert([
                'name' => $name,
                'slug' => url_title($name, '-', true),
            ]);

            return redirect()->back()->with('success', 'Category added.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'Category could not be added.');
        }
    }

    public function delete(int $id)
    {
        try {
            (new CategoryModel())->delete($id);

            return redirect()->back()->with('success', 'Category deleted.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'Category could not be deleted.');
        }
    }
}
