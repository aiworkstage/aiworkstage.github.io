#!/usr/bin/env python3
import re
import os
import glob

BASE = '/home/ubuntu/.openclaw/workspace/aiworkstage-hp'

# ===== 1. index.html light theme =====
with open(f'{BASE}/index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

replacements_idx = [
    ('#0a0e1a', '#f8faff'),
    ('#12121e', '#ffffff'),
    ('#1e1e2e', '#e2e8f0'),
    ('#e0e0ff', '#1a202c'),
    ('#8888aa', '#64748b'),
    ('#7c6bff', '#6366f1'),
]
for old, new in replacements_idx:
    idx = idx.replace(old, new)

# Hero gradient
idx = re.sub(
    r'(\.hero\s*\{[^}]*background\s*:[^;]+;)',
    lambda m: re.sub(r'background\s*:[^;]+;',
        'background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #00d4ff 100%);', m.group(0)),
    idx
)

# Nav background
idx = re.sub(
    r'(nav|\.navbar|header)\s*\{([^}]*)\}',
    lambda m: m.group(0).replace(
        'background:', 'background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0; /* replaced-bg: '
    ) if 'background' in m.group(0) else m.group(0),
    idx
)

# Service card styles - add box-shadow
idx = idx.replace(
    'border: 1px solid #e2e8f0;',
    'border: 1px solid #e2e8f0;\n            box-shadow: 0 2px 12px rgba(0,0,0,0.06);'
)

# Section backgrounds - add after </style> or inject via direct string ops
# We'll inject a <style> block just before </style>
light_section_css = """
    /* Light theme section backgrounds */
    .services { background: #f8faff !important; }
    .why, #why { background: #ffffff !important; }
    .blog, #blog { background: #f0f4ff !important; }
    nav, header { background: rgba(255,255,255,0.95) !important; backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0 !important; color: #1a202c !important; }
    nav a, header a { color: #1a202c !important; }
    .logo, .nav-logo { color: #6366f1 !important; }
    footer { background: linear-gradient(135deg, #1e1b4b, #312e81) !important; color: #e0e7ff !important; }
    .service-card:hover { box-shadow: 0 8px 24px rgba(99,102,241,0.15) !important; }
"""
idx = idx.replace('</style>', light_section_css + '\n    </style>', 1)

with open(f'{BASE}/index.html', 'w', encoding='utf-8') as f:
    f.write(idx)
print('index.html done')

# ===== 2. service-*.html light theme + accent colors =====
service_accents = {
    'service-hp.html':      ('#0288d1', 'linear-gradient(135deg, #e3f2fd, #bbdefb)'),
    'service-lp.html':      ('#f57c00', 'linear-gradient(135deg, #fff3e0, #ffe0b2)'),
    'service-seo.html':     ('#2e7d32', 'linear-gradient(135deg, #e8f5e9, #c8e6c9)'),
    'service-ai-agent.html':('#5e35b1', 'linear-gradient(135deg, #ede7f6, #d1c4e9)'),
    'service-chatbot.html': ('#1565c0', 'linear-gradient(135deg, #e3f2fd, #e8eaf6)'),
    'service-blog.html':    ('#455a64', 'linear-gradient(135deg, #eceff1, #cfd8dc)'),
    'service-line.html':    ('#1b5e20', 'linear-gradient(135deg, #e8f5e9, #a5d6a7)'),
    'service-notion.html':  ('#37474f', 'linear-gradient(135deg, #fafafa, #eceff1)'),
    'service-minutes.html': ('#1a237e', 'linear-gradient(135deg, #e8eaf6, #c5cae9)'),
    'service-sns-link.html':('#ad1457', 'linear-gradient(135deg, #fce4ec, #f8bbd9)'),
    'service-hp-check.html':('#0277bd', 'linear-gradient(135deg, #e1f5fe, #b3e5fc)'),
    'service-bbs.html':     ('#e65100', 'linear-gradient(135deg, #fff3e0, #ffe0b2)'),
}

tooltip_css = """
    /* Tooltip styles */
    .tooltip { position: relative; border-bottom: 1px dotted #6366f1; cursor: help; }
    .tooltip::after { content: attr(data-tip); position: absolute; bottom: 125%; left: 50%; transform: translateX(-50%); background: #1a202c; color: #fff; padding: 6px 10px; border-radius: 6px; font-size: 0.78rem; white-space: nowrap; opacity: 0; pointer-events: none; transition: opacity 0.2s; z-index: 100; }
    .tooltip:hover::after { opacity: 1; }
    @media(max-width:600px){ .tooltip::after { white-space: normal; width: 200px; left: 0; transform: none; } }
"""

terms = {
    'CVR改善レポート': '<span class="tooltip" data-tip="申し込み率を上げるための分析・改善提案書">CVR改善レポート</span>',
    'CTAボタン': '<span class="tooltip" data-tip="「今すぐ申し込む」など、お客さんの行動を促すボタンのこと">CTAボタン</span>',
    'SEO最適化': '<span class="tooltip" data-tip="Googleで検索上位に表示されるようページを最適化すること">SEO最適化</span>',
    'SEO対策': '<span class="tooltip" data-tip="Googleなどの検索エンジンで上位表示されるための施策">SEO対策</span>',
    'Google Analytics': '<span class="tooltip" data-tip="Googleの無料アクセス解析ツール。訪問者数・行動を把握できる">Google Analytics</span>',
    'CRM連携': '<span class="tooltip" data-tip="顧客管理システムとの連携。問い合わせ情報を自動で顧客データベースに登録">CRM連携</span>',
    'API連携': '<span class="tooltip" data-tip="異なるシステム同士を連携させる仕組み。例：フォーム送信→Slackに自動通知">API連携</span>',
    'リッチメニュー': '<span class="tooltip" data-tip="LINEのトーク画面下部に表示されるメニューボタン">リッチメニュー</span>',
    'シナリオ配信': '<span class="tooltip" data-tip="友達登録から何日後にどのメッセージを送るか自動設定する機能">シナリオ配信</span>',
    'ガントチャート': '<span class="tooltip" data-tip="タスクの期間・進捗を横棒グラフで表したスケジュール表">ガントチャート</span>',
    'モデレーション': '<span class="tooltip" data-tip="不適切な投稿を削除・非表示にする管理機能">モデレーション</span>',
    'ヒートマップ': '<span class="tooltip" data-tip="ページのどこがよく見られているかを色で可視化するツール">ヒートマップ</span>',
    'A/Bテスト': '<span class="tooltip" data-tip="2種類のデザインや文章を比較して、どちらが効果的か測定する手法">A/Bテスト</span>',
    'CVR': '<span class="tooltip" data-tip="Conversion Rate：訪問者のうち実際に申し込みに至った割合">CVR</span>',
    'CTA': '<span class="tooltip" data-tip="Call To Action：「今すぐ申し込む」などの行動を促すボタン">CTA</span>',
    'SEO': '<span class="tooltip" data-tip="Search Engine Optimization：Googleなどで検索上位に表示されるよう最適化すること">SEO</span>',
    'LCP': '<span class="tooltip" data-tip="Largest Contentful Paint：ページの主要コンテンツが表示されるまでの時間">LCP</span>',
}

def apply_tooltips_in_li(html):
    """Apply tooltip spans only inside <li> tags, skip if already has tooltip"""
    def replace_in_li(m):
        li_content = m.group(0)
        if 'class="tooltip"' in li_content:
            return li_content  # skip already processed
        for term, replacement in terms.items():
            # Only replace if not already wrapped in tooltip
            if term in li_content and f'>{term}<' not in li_content and f'">{term}</' not in li_content:
                # Make sure we don't double-replace inside already replaced spans
                li_content = li_content.replace(term, replacement, 1)
        return li_content
    
    return re.sub(r'<li>.*?</li>', replace_in_li, html, flags=re.DOTALL)

all_service_files = glob.glob(f'{BASE}/service-*.html')

for fpath in all_service_files:
    fname = os.path.basename(fpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic dark->light replacements
    dark_to_light = [
        ('#0a0e1a', '#f8faff'),
        ('#12121e', '#ffffff'),
        ('#0d1117', '#f8faff'),
        ('#1e1e2e', '#e2e8f0'),
        ('#e0e0ff', '#1a202c'),
        ('#8888aa', '#64748b'),
        ('#7c6bff', '#6366f1'),
        ('#0f0f23', '#f8faff'),
        ('#16213e', '#f8faff'),
    ]
    for old, new in dark_to_light:
        content = content.replace(old, new)

    # Get accent for this file
    accent_color, hero_gradient = service_accents.get(fname, ('#6366f1', 'linear-gradient(135deg, #e8eaf6, #c5cae9)'))

    # Inject CSS variables and light theme overrides before </style>
    light_css = f"""
    /* === Light Theme === */
    :root {{ --accent: {accent_color}; }}
    body {{ background: #f8faff !important; color: #1a202c !important; }}
    .hero, .service-hero {{ background: {hero_gradient} !important; color: #1a202c !important; }}
    .hero h1, .service-hero h1 {{ color: #1a202c !important; }}
    .hero p, .service-hero p {{ color: #2d3748 !important; }}
    .price-card {{ background: #fff !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important; }}
    .price-card:hover {{ box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important; transform: translateY(-4px); }}
    .price-card.featured {{ border: 2px solid {accent_color} !important; }}
    .faq-item {{ background: #fff !important; border: 1px solid #e2e8f0 !important; }}
    section h2 {{ color: #1a202c !important; border-left-color: {accent_color} !important; }}
    .plan-price {{ color: {accent_color} !important; }}
    .btn, .cta-btn, button[type=submit], .apply-btn {{ background: {accent_color} !important; border-color: {accent_color} !important; color: #fff !important; }}
    nav, header {{ background: rgba(255,255,255,0.95) !important; backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0 !important; }}
    nav a, header a {{ color: #1a202c !important; }}
    .logo, .nav-logo {{ color: {accent_color} !important; }}
    footer {{ background: linear-gradient(135deg, #1e1b4b, #312e81) !important; color: #e0e7ff !important; }}
    footer a {{ color: #c7d2fe !important; }}
{tooltip_css}
"""
    content = content.replace('</style>', light_css + '\n    </style>', 1)

    # Apply tooltips in <li> tags
    content = apply_tooltips_in_li(content)

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{fname} done')

print('All done!')
