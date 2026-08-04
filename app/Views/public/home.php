<?= $this->extend('layout/main') ?>

<?= $this->section('content') ?>
<section class="hero-image min-h-[620px]">
    <div class="mx-auto flex min-h-[620px] max-w-7xl items-center px-4 py-16 sm:px-6 lg:px-8">
        <div class="max-w-3xl text-white">
            <?= $this->include('layout/alerts') ?>
            <p class="mb-4 inline-flex rounded-full bg-white/15 px-4 py-2 text-sm font-bold backdrop-blur">Verified travel specialists across destinations</p>
            <h1 class="text-4xl font-extrabold leading-tight sm:text-6xl">Find a travel company that fits the journey.</h1>
            <p class="mt-5 max-w-2xl text-lg leading-8 text-white/85">Compare agencies by destination, expertise, and location, then send enquiries directly from a clean public profile.</p>
            <form action="<?= site_url('companies') ?>" method="get" class="mt-8 grid gap-3 rounded-2xl bg-white p-3 shadow-2xl md:grid-cols-[1fr_1fr_auto]">
                <label class="flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-3 text-slate-700">
                    <span class="material-symbols-outlined text-[#115cb9]">search</span>
                    <input name="q" class="w-full border-0 bg-transparent p-0 text-sm font-semibold text-slate-900 placeholder:text-slate-400 focus:ring-0" placeholder="Destination, agency, or specialty">
                </label>
                <label class="flex items-center gap-3 rounded-xl bg-slate-50 px-4 py-3 text-slate-700">
                    <span class="material-symbols-outlined text-[#115cb9]">map</span>
                    <input name="location" class="w-full border-0 bg-transparent p-0 text-sm font-semibold text-slate-900 placeholder:text-slate-400 focus:ring-0" placeholder="City or state">
                </label>
                <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#115cb9] px-6 py-3 text-sm font-extrabold text-white hover:bg-[#0d4f9f]">
                    <span class="material-symbols-outlined text-[20px]">travel_explore</span>
                    Search
                </button>
            </form>
        </div>
    </div>
</section>

<section class="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
    <div class="mb-8 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
            <p class="text-sm font-extrabold uppercase tracking-[0.16em] text-[#115cb9]">Featured agencies</p>
            <h2 class="mt-2 text-3xl font-extrabold tracking-tight text-slate-950">Top travel companies</h2>
        </div>
        <a href="<?= site_url('companies') ?>" class="inline-flex items-center gap-1 text-sm font-extrabold text-[#115cb9]">
            View all <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
        </a>
    </div>
    <div class="grid gap-5 md:grid-cols-3">
        <?php foreach ($featuredCompanies as $company): ?>
            <?= view('public/partials/company_card', ['company' => $company]) ?>
        <?php endforeach; ?>
    </div>
</section>

<section class="page-band border-y border-slate-200">
    <div class="mx-auto grid max-w-7xl gap-8 px-4 py-14 sm:px-6 lg:grid-cols-3 lg:px-8">
        <div>
            <span class="material-symbols-outlined mb-4 text-4xl text-[#115cb9]">verified</span>
            <h3 class="text-xl font-extrabold">Approved profiles</h3>
            <p class="mt-2 text-slate-600">Admin review keeps the directory focused on credible travel businesses.</p>
        </div>
        <div>
            <span class="material-symbols-outlined mb-4 text-4xl text-[#006058]">route</span>
            <h3 class="text-xl font-extrabold">Browse by need</h3>
            <p class="mt-2 text-slate-600">Visitors can search by specialty, city, agency name, or destination style.</p>
        </div>
        <div>
            <span class="material-symbols-outlined mb-4 text-4xl text-[#9d4300]">forward_to_inbox</span>
            <h3 class="text-xl font-extrabold">Direct enquiries</h3>
            <p class="mt-2 text-slate-600">Each company profile includes an enquiry form and contact information.</p>
        </div>
    </div>
</section>
<?= $this->endSection() ?>
