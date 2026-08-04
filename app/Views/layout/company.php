<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($title ?? 'Travel360 Dashboard') ?></title>
    <script src="https://cdn.tailwindcss.com?plugins=forms"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= base_url('assets/css/travel360.css') ?>">
</head>
<body class="bg-slate-50 text-slate-950">
    <header class="border-b border-slate-200 bg-white">
        <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <a href="<?= site_url('dashboard') ?>" class="flex items-center gap-3 font-extrabold">
                <span class="grid h-10 w-10 place-items-center rounded-xl bg-[#115cb9] text-white">
                    <span class="material-symbols-outlined text-[22px]">business_center</span>
                </span>
                <span class="text-xl">Travel360</span>
            </a>
            <div class="flex items-center gap-2 text-sm font-bold">
                <a href="<?= site_url('dashboard') ?>" class="rounded-xl px-4 py-2 hover:bg-slate-100">Profile</a>
                <a href="<?= site_url('dashboard/enquiries') ?>" class="rounded-xl px-4 py-2 hover:bg-slate-100">Enquiries</a>
                <a href="<?= site_url('logout') ?>" class="rounded-xl bg-slate-950 px-4 py-2 text-white hover:bg-slate-800">Sign out</a>
            </div>
        </div>
    </header>
    <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <?= $this->include('layout/alerts') ?>
        <?= $this->renderSection('content') ?>
    </main>
</body>
</html>
