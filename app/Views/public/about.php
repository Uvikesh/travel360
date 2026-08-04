<?= $this->extend('layout/main') ?>

<?= $this->section('content') ?>
<section class="page-band border-b border-slate-200">
    <div class="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1fr_420px] lg:px-8">
        <div>
            <?= $this->include('layout/alerts') ?>
            <p class="text-sm font-extrabold uppercase tracking-[0.16em] text-[#115cb9]">About</p>
            <h1 class="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl">A focused directory for travel decision-makers.</h1>
            <p class="mt-6 text-lg leading-8 text-slate-700">Travel360 connects customers with agencies that are ready to receive detailed trip enquiries. It keeps browsing simple for travelers and gives agencies a clean company dashboard to maintain their profile.</p>
        </div>
        <img src="https://images.unsplash.com/photo-1526772662000-3f88f10405ff?auto=format&fit=crop&w=900&q=85" alt="Travel planning table" class="h-full min-h-[320px] rounded-3xl object-cover shadow-xl">
    </div>
</section>
<?= $this->endSection() ?>
