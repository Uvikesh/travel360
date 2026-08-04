<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($title ?? 'Travel360 Admin') ?></title>
    <script src="https://cdn.tailwindcss.com?plugins=forms"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= base_url('assets/css/travel360.css') ?>">
</head>
<body class="bg-slate-100 text-slate-950">
    <div class="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
        <aside class="border-b border-slate-200 bg-slate-950 text-white lg:border-b-0 lg:border-r">
            <div class="flex items-center justify-between px-5 py-5 lg:block">
                <a href="<?= site_url('admin/dashboard') ?>" class="flex items-center gap-3 font-extrabold">
                    <span class="grid h-10 w-10 place-items-center rounded-xl bg-[#6bd8cb] text-slate-950">
                        <span class="material-symbols-outlined text-[22px]">travel_explore</span>
                    </span>
                    <span class="text-xl">Travel360</span>
                </a>
                <a href="<?= site_url('/') ?>" class="text-sm font-bold text-slate-300 hover:text-white lg:mt-8 lg:inline-flex">View site</a>
            </div>
            <nav class="grid gap-1 px-3 pb-5 text-sm font-bold lg:pt-2">
                <a href="<?= site_url('admin/dashboard') ?>" class="rounded-xl px-4 py-3 hover:bg-white/10">Dashboard</a>
                <a href="<?= site_url('admin/companies') ?>" class="rounded-xl px-4 py-3 hover:bg-white/10">Companies</a>
                <a href="<?= site_url('admin/categories') ?>" class="rounded-xl px-4 py-3 hover:bg-white/10">Categories</a>
                <a href="<?= site_url('admin/locations') ?>" class="rounded-xl px-4 py-3 hover:bg-white/10">Locations</a>
                <a href="<?= site_url('admin/enquiries') ?>" class="rounded-xl px-4 py-3 hover:bg-white/10">Enquiries</a>
                <a href="<?= site_url('logout') ?>" class="rounded-xl px-4 py-3 text-slate-300 hover:bg-white/10 hover:text-white">Sign out</a>
            </nav>
        </aside>
        <main class="min-w-0">
            <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <?= $this->include('layout/alerts') ?>
                <?= $this->renderSection('content') ?>
            </div>
        </main>
    </div>
</body>
</html>
