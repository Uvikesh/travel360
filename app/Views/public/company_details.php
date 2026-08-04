<?= $this->extend('layout/main') ?>

<?= $this->section('content') ?>
<section class="page-band border-b border-slate-200">
    <div class="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_360px] lg:px-8">
        <div>
            <?= $this->include('layout/alerts') ?>
            <div class="flex flex-col gap-5 sm:flex-row sm:items-center">
                <img src="<?= esc($company['logo_url'] ?: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80') ?>" alt="<?= esc($company['agency_name']) ?>" class="h-24 w-24 rounded-3xl object-cover shadow-lg">
                <div>
                    <p class="text-sm font-extrabold uppercase tracking-[0.16em] text-[#115cb9]"><?= esc($company['category_name'] ?? 'Travel company') ?></p>
                    <h1 class="mt-2 text-4xl font-extrabold tracking-tight"><?= esc($company['agency_name']) ?></h1>
                    <p class="mt-2 text-lg font-semibold text-slate-600"><?= esc($company['city_name'] ?? 'Remote') ?><?= ! empty($company['state_name']) ? ', ' . esc($company['state_name']) : '' ?> · <?= number_format((float) ($company['rating'] ?? 0), 1) ?> rating</p>
                </div>
            </div>
            <p class="mt-8 max-w-3xl text-lg leading-8 text-slate-700"><?= esc($company['about_text'] ?? '') ?></p>
            <div class="mt-8 grid gap-4 sm:grid-cols-3">
                <a href="tel:<?= esc($company['phone'] ?? '') ?>" class="rounded-2xl border border-slate-200 bg-white p-5 font-bold hover:border-[#115cb9]">
                    <span class="material-symbols-outlined text-[#115cb9]">call</span>
                    <span class="mt-3 block text-sm text-slate-500">Phone</span>
                    <span class="mt-1 block"><?= esc($company['phone'] ?? 'Not listed') ?></span>
                </a>
                <a href="https://wa.me/<?= preg_replace('/\D+/', '', (string) ($company['whatsapp'] ?? '')) ?>" class="rounded-2xl border border-slate-200 bg-white p-5 font-bold hover:border-[#006058]">
                    <span class="material-symbols-outlined text-[#006058]">chat</span>
                    <span class="mt-3 block text-sm text-slate-500">WhatsApp</span>
                    <span class="mt-1 block"><?= esc($company['whatsapp'] ?? 'Not listed') ?></span>
                </a>
                <a href="<?= esc($company['website_url'] ?? '#') ?>" class="rounded-2xl border border-slate-200 bg-white p-5 font-bold hover:border-[#9d4300]">
                    <span class="material-symbols-outlined text-[#9d4300]">language</span>
                    <span class="mt-3 block text-sm text-slate-500">Website</span>
                    <span class="mt-1 block">Open site</span>
                </a>
            </div>
        </div>
        <aside class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-2xl font-extrabold">Send enquiry</h2>
            <form action="<?= site_url('company/' . $company['slug'] . '/enquire') ?>" method="post" class="mt-5 grid gap-4">
                <?= csrf_field() ?>
                <input class="form-input" name="sender_name" value="<?= old('sender_name') ?>" placeholder="Your name">
                <input class="form-input" type="email" name="sender_email" value="<?= old('sender_email') ?>" placeholder="Email address">
                <textarea class="form-input min-h-36" name="message" placeholder="Trip details, dates, and preferences"><?= old('message') ?></textarea>
                <button class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#115cb9] px-5 py-3 text-sm font-extrabold text-white hover:bg-[#0d4f9f]">
                    <span class="material-symbols-outlined text-[20px]">send</span>
                    Send enquiry
                </button>
            </form>
        </aside>
    </div>
</section>
<?= $this->endSection() ?>
