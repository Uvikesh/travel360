<?= $this->extend('layout/main') ?>

<?= $this->section('content') ?>
<section class="page-band border-b border-slate-200">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <?= $this->include('layout/alerts') ?>
        <p class="text-sm font-extrabold uppercase tracking-[0.16em] text-[#115cb9]">Directory</p>
        <h1 class="mt-2 text-4xl font-extrabold tracking-tight">Browse travel companies</h1>
        <form action="<?= site_url('companies') ?>" method="get" class="mt-8 grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_220px_220px_auto]">
            <input class="form-input" name="q" value="<?= esc($filters['q'] ?? '') ?>" placeholder="Search agencies or specialties">
            <select class="form-input" name="category_id">
                <option value="">All categories</option>
                <?php foreach ($categories as $category): ?>
                    <option value="<?= esc($category['id']) ?>" <?= (string) ($filters['category_id'] ?? '') === (string) $category['id'] ? 'selected' : '' ?>><?= esc($category['name']) ?></option>
                <?php endforeach; ?>
            </select>
            <select class="form-input" name="city_id">
                <option value="">All cities</option>
                <?php foreach ($cities as $city): ?>
                    <option value="<?= esc($city['id']) ?>" <?= (string) ($filters['city_id'] ?? '') === (string) $city['id'] ? 'selected' : '' ?>><?= esc($city['name']) ?><?= ! empty($city['state_name']) ? ', ' . esc($city['state_name']) : '' ?></option>
                <?php endforeach; ?>
            </select>
            <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#115cb9] px-5 py-3 text-sm font-extrabold text-white hover:bg-[#0d4f9f]">
                <span class="material-symbols-outlined text-[20px]">filter_alt</span>
                Filter
            </button>
        </form>
    </div>
</section>

<section class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
    <?php if ($companies === []): ?>
        <div class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
            <h2 class="text-2xl font-extrabold">No companies found</h2>
            <p class="mt-2 text-slate-600">Try a different search or clear the filters.</p>
        </div>
    <?php else: ?>
        <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            <?php foreach ($companies as $company): ?>
                <?= view('public/partials/company_card', ['company' => $company]) ?>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>
</section>
<?= $this->endSection() ?>
