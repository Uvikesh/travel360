<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($title ?? 'Travel360') ?></title>
    <script src="https://cdn.tailwindcss.com?plugins=forms"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= base_url('assets/css/travel360.css') ?>">
</head>
<body class="min-h-screen bg-[#f8f9fa] text-slate-950">
    <header class="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <nav class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <a href="<?= site_url('/') ?>" class="flex items-center gap-3 font-extrabold tracking-tight text-slate-950">
                <span class="grid h-10 w-10 place-items-center rounded-xl bg-[#115cb9] text-white">
                    <span class="material-symbols-outlined text-[22px]">travel_explore</span>
                </span>
                <span class="text-xl">Travel360</span>
            </a>
            <div class="hidden items-center gap-7 text-sm font-bold text-slate-700 md:flex">
                <a class="hover:text-[#115cb9]" href="<?= site_url('companies') ?>">Companies</a>
                <a class="hover:text-[#115cb9]" href="<?= site_url('about') ?>">About</a>
                <a class="hover:text-[#115cb9]" href="<?= site_url('contact') ?>">Contact</a>
            </div>
            <div class="flex items-center gap-2">
                <?php if (session()->get('isLoggedIn')): ?>
                    <a href="<?= session()->get('role') === 'admin' ? site_url('admin/dashboard') : site_url('dashboard') ?>" class="hidden rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50 sm:inline-flex">Dashboard</a>
                    <a href="<?= site_url('logout') ?>" class="rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white hover:bg-slate-800">Sign out</a>
                <?php else: ?>
                    <a href="<?= site_url('login') ?>" class="hidden rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50 sm:inline-flex">Sign in</a>
                    <a href="<?= site_url('register') ?>" class="rounded-xl bg-[#115cb9] px-4 py-2 text-sm font-bold text-white hover:bg-[#0d4f9f]">Join</a>
                <?php endif; ?>
            </div>
        </nav>
    </header>

    <main>
        <?= $this->renderSection('content') ?>
    </main>

    <footer class="border-t border-slate-200 bg-white">
        <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-8 text-sm text-slate-600 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
            <p>&copy; <?= date('Y') ?> Travel360. Trusted travel company directory.</p>
            <div class="flex gap-5 font-semibold">
                <a href="<?= site_url('companies') ?>" class="hover:text-[#115cb9]">Browse</a>
                <a href="<?= site_url('register') ?>" class="hover:text-[#115cb9]">Register agency</a>
                <a href="<?= site_url('contact') ?>" class="hover:text-[#115cb9]">Support</a>
            </div>
        </div>
    </footer>
</body>
</html>
