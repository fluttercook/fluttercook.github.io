export const locales = ['en', 'vi'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

// Map an English path to its localized counterpart (vi is prefixed with /vi).
export function localizePath(path: string, lang: Locale): string {
  const clean = path.replace(/^\/(vi)(?=\/|$)/, '') || '/';
  if (lang === 'en') return clean;
  return clean === '/' ? '/vi/' : `/vi${clean}`;
}

// Strip a locale prefix to get the canonical English path.
export function stripLocale(path: string): { lang: Locale; path: string } {
  if (path === '/vi' || path.startsWith('/vi/')) {
    return { lang: 'vi', path: path.replace(/^\/vi/, '') || '/' };
  }
  return { lang: 'en', path };
}

type Dict = Record<string, string>;
export const ui: Record<Locale, Dict> = {
  en: {
    'nav.recipes': 'Recipes',
    'nav.news': 'News',
    'nav.github': 'GitHub',
    'nav.youtube': 'YouTube',
    'nav.about': 'About',
    'nav.repo': 'Repo',
    'lang.switch': 'Tiếng Việt',
    'site.tagline': 'A cookbook for the best Flutter libraries.',
    'home.kicker': 'Open-source · AI-first · trend-driven',
    'home.browse': 'Browse recipes',
    'home.trends': 'Live GitHub trends',
    'home.trendingNow': 'Trending right now',
    'home.byCategory': 'By category',
    'recipes.title': 'All recipes',
    'recipes.sub': 'open-source Flutter projects & components — filter by category, ranked by momentum.',
    'recipes.loadMore': 'Load more',
    'news.kicker': 'Daily developer news',
    'news.title': 'Mobile & Flutter News',
    'news.sub': 'Reviews and analysis on Apple, iOS, Google Android, Flutter, iPhone & macOS — written for people who build mobile apps.',
    'article.related': 'Related',
    'article.sources': 'Sources',
    'article.faq': 'Frequently asked questions',
    'article.by': 'By',
    'footer.tagline': 'FlutterCook — 500 open-source Flutter recipes, AI-first.',
  },
  vi: {
    'nav.recipes': 'Công thức',
    'nav.news': 'Tin tức',
    'nav.github': 'GitHub',
    'nav.youtube': 'YouTube',
    'nav.about': 'Giới thiệu',
    'nav.repo': 'Mã nguồn',
    'lang.switch': 'English',
    'site.tagline': 'Sổ tay các thư viện Flutter tốt nhất.',
    'home.kicker': 'Mã nguồn mở · Ưu tiên AI · Theo xu hướng',
    'home.browse': 'Xem công thức',
    'home.trends': 'Xu hướng GitHub trực tiếp',
    'home.trendingNow': 'Đang thịnh hành',
    'home.byCategory': 'Theo danh mục',
    'recipes.title': 'Tất cả công thức',
    'recipes.sub': 'dự án & thành phần Flutter mã nguồn mở — lọc theo danh mục, xếp theo độ hot.',
    'recipes.loadMore': 'Xem thêm',
    'news.kicker': 'Tin tức lập trình hằng ngày',
    'news.title': 'Tin Mobile & Flutter',
    'news.sub': 'Đánh giá và phân tích về Apple, iOS, Google Android, Flutter, iPhone & macOS — dành cho người làm ứng dụng di động.',
    'article.related': 'Liên quan',
    'article.sources': 'Nguồn',
    'article.faq': 'Câu hỏi thường gặp',
    'article.by': 'Bởi',
    'footer.tagline': 'FlutterCook — 500 công thức Flutter mã nguồn mở, ưu tiên AI.',
  },
};

export function t(lang: Locale) {
  return (key: string) => ui[lang][key] ?? ui.en[key] ?? key;
}
