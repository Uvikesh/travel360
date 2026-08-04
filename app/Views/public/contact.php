<?= $this->extend('layout/main') ?>

<?= $this->section('content') ?>
<section class="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1fr_440px] lg:px-8">
    <div>
        <?= $this->include('layout/alerts') ?>
        <?php if ($sent): ?>
            <div class="mb-6 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm font-semibold text-green-800">Thanks. The support message has been received.</div>
        <?php endif; ?>
        <p class="text-sm font-extrabold uppercase tracking-[0.16em] text-[#115cb9]">Support</p>
        <h1 class="mt-2 text-4xl font-extrabold tracking-tight">Contact Travel360</h1>
        <p class="mt-5 max-w-2xl text-lg leading-8 text-slate-700">Use this channel for account, approval, or listing questions.</p>
        <div class="mt-8 grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-slate-200 bg-white p-5">
                <span class="material-symbols-outlined text-[#115cb9]">mail</span>
                <p class="mt-3 text-sm font-bold text-slate-500">Email</p>
                <p class="font-extrabold">support@travel360.local</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white p-5">
                <span class="material-symbols-outlined text-[#006058]">schedule</span>
                <p class="mt-3 text-sm font-bold text-slate-500">Hours</p>
                <p class="font-extrabold">Mon-Fri, 10 AM-6 PM</p>
            </div>
        </div>
    </div>
    <form action="<?= site_url('contact') ?>" method="post" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <?= csrf_field() ?>
        <div class="grid gap-4">
            <input class="form-input" name="name" placeholder="Your name">
            <input class="form-input" type="email" name="email" placeholder="Email address">
            <textarea class="form-input min-h-40" name="message" placeholder="How can we help?"></textarea>
            <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#115cb9] px-5 py-3 text-sm font-extrabold text-white hover:bg-[#0d4f9f]">
                <span class="material-symbols-outlined text-[20px]">send</span>
                Send
            </button>
        </div>
    </form>
</section>
<?= $this->endSection() ?>
