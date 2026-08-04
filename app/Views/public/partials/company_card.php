<article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <div class="flex items-start gap-4">
        <img src="<?= esc($company['logo_url'] ?: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80') ?>" alt="<?= esc($company['agency_name']) ?>" class="h-16 w-16 rounded-2xl object-cover">
        <div class="min-w-0 flex-1">
            <h3 class="truncate text-lg font-extrabold"><?= esc($company['agency_name']) ?></h3>
            <p class="mt-1 text-sm font-semibold text-slate-500"><?= esc($company['city_name'] ?? 'Remote') ?><?= ! empty($company['state_name']) ? ', ' . esc($company['state_name']) : '' ?></p>
        </div>
    </div>
    <div class="mt-5 flex flex-wrap items-center gap-2">
        <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-extrabold text-[#115cb9]"><?= esc($company['category_name'] ?? 'Travel') ?></span>
        <span class="rounded-full bg-amber-50 px-3 py-1 text-xs font-extrabold text-amber-700"><?= number_format((float) ($company['rating'] ?? 0), 1) ?> rating</span>
    </div>
    <p class="mt-4 line-clamp-3 text-sm leading-6 text-slate-600"><?= esc($company['about_text'] ?? '') ?></p>
    <a href="<?= site_url('company/' . $company['slug']) ?>" class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-extrabold text-slate-900 hover:border-[#115cb9] hover:text-[#115cb9]">
        View profile <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
    </a>
</article>
