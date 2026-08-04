<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\CityModel;
use App\Models\StateModel;
use Throwable;

class Locations extends BaseController
{
    public function index(): string
    {
        try {
            $states = (new StateModel())->orderBy('name')->findAll();
            $cities = (new CityModel())->withState();
        } catch (Throwable) {
            $states = [];
            $cities = [];
        }

        return view('admin/locations', [
            'title' => 'Manage Locations - Travel360',
            'states' => $states,
            'cities' => $cities,
        ]);
    }

    public function createState()
    {
        $name = trim((string) $this->request->getPost('name'));

        if ($name === '') {
            return redirect()->back()->with('error', 'State name is required.');
        }

        try {
            (new StateModel())->insert(['name' => $name]);

            return redirect()->back()->with('success', 'State added.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'State could not be added.');
        }
    }

    public function createCity()
    {
        if (! $this->validate(['state_id' => 'required', 'name' => 'required'])) {
            return redirect()->back()->with('error', 'Select a state and enter a city name.');
        }

        try {
            (new CityModel())->insert([
                'state_id' => $this->request->getPost('state_id'),
                'name' => $this->request->getPost('name'),
            ]);

            return redirect()->back()->with('success', 'City added.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'City could not be added.');
        }
    }

    public function deleteCity(int $id)
    {
        try {
            (new CityModel())->delete($id);

            return redirect()->back()->with('success', 'City deleted.');
        } catch (Throwable) {
            return redirect()->back()->with('error', 'City could not be deleted.');
        }
    }
}
