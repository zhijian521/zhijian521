"""把 D 方案排成可用于 GitHub README 的字体轮廓 SVG，避免字体替换和窄屏小字。"""

import argparse
from functools import lru_cache
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--font', required=True, help='霞鹜文楷屏幕阅读版的 TTF 或 WOFF2 文件')
ARGS = PARSER.parse_args()
FONT = TTFont(ARGS.font)
FONTS = {'serif': FONT, 'sans': FONT}
GLYPHS = {key: font.getGlyphSet() for key, font in FONTS.items()}
CMAPS = {key: font.getBestCmap() for key, font in FONTS.items()}
EM = {key: font['head'].unitsPerEm for key, font in FONTS.items()}
# 度量和绘制共用倍率，保证朱砂强调的连续文字与右对齐文字同步缩小。
TEXT_SCALE = 0.88 * 2 / 3
# 正文与竖签分别补偿可读性，不联动已经确定的姓名、主张和项目标题。
BODY_TEXT_BOOST = 1.25
VERTICAL_TEXT_BOOST = 1.5
PALETTES = {
    'light': dict(paper='#ffffff', ink='#252725', muted='#60635f', line='#d8dad4', red='#b6402d', white='#ffffff'),
    'dark': dict(paper='#0d1117', ink='#ecece5', muted='#aeb3ad', line='#3c433f', red='#ef8c76', white='#ffffff'),
}


@lru_cache(maxsize=None)
def glyph(key, character):
    name = CMAPS[key].get(ord(character))
    if name is None:
        raise ValueError(f'{key} 字体缺少字形：{character}')
    pen = SVGPathPen(GLYPHS[key])
    GLYPHS[key][name].draw(pen)
    return pen.getCommands(), GLYPHS[key][name].width


def measure(text, size, key='sans', tracking=0):
    return sum(glyph(key, char)[1] * size / EM[key] + tracking for char in text) * TEXT_SCALE


class Canvas:
    def __init__(self, width, height, palette, title, description):
        self.width, self.height, self.palette = width, height, palette
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width * 2}" height="{height * 2}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<!-- 全部字形来自霞鹜文楷屏幕阅读版；来源及许可见 FONT-LICENSES.txt。 -->',
            f'<rect width="{width}" height="{height}" fill="{palette["paper"]}"/>',
        ]

    def text(self, content, x, y, size, color='ink', family='sans', tracking=0):
        scale = size * TEXT_SCALE / EM[family]
        tracking *= TEXT_SCALE
        self.parts.append(f'<g fill="{self.palette[color]}" aria-label="{escape(content, quote=True)}">')
        for character in content:
            outline, advance = glyph(family, character)
            if outline:
                self.parts.append(f'<path transform="translate({x:.3f} {y:.3f}) scale({scale:.8f} {-scale:.8f})" d="{outline}"/>')
            x += advance * scale + tracking
        self.parts.append('</g>')

    def line(self, x1, y, x2, color='line', width=1):
        self.parts.append(f'<path d="M{x1} {y}H{x2}" fill="none" stroke="{self.palette[color]}" stroke-width="{width}"/>')

    def arrow(self, x, y):
        self.parts.append(f'<path d="M{x} {y + 14}l14-14m-13 0h13v13" fill="none" stroke="{self.palette["red"]}" stroke-width="1.6"/>')

    def save(self, name):
        (ASSETS / name).write_text('\n'.join(self.parts + ['</svg>', '']), encoding='utf-8')


WORKS = [
    dict(slug='work-ledger', number='一', title='一本游戏里的手账',
         description=['梦幻养老助手 / 管理角色、识别截图、记录收益。', '让养成有记录，让数据留在本地。'],
         mobile=['梦幻养老助手 / 管理角色、识别截图、', '记录收益。让养成有记录，', '让数据留在本地。'],
         tech='mh-toolbox-rs · Vue / Tauri / Rust', url='https://github.com/zhijian521/mh-toolbox-rs'),
    dict(slug='work-blog', number='二', title='一处写字的地方',
         description=['语无边 · Simple Blog / 极简的静态博客。', '放下笔记、项目，以及没来得及说完的想法。'],
         mobile=['语无边 · Simple Blog / 极简静态博客。', '放下笔记、项目，', '以及没来得及说完的想法。'],
         tech='simple-blog · Astro / Markdown', url='https://github.com/zhijian521/simple-blog'),
    dict(slug='work-earth', number='三', title='一个可以探索的世界',
         description=['Cesium 三维地球 / 航线、空域、粒子与天气。', '让抽象的空间，变成眼前的风景。'],
         mobile=['Cesium 三维地球 / 航线、空域、', '粒子与天气。让抽象的空间，', '变成眼前的风景。'],
         tech='cesium-example · CesiumJS / WebGL', url='https://github.com/zhijian521/cesium-example'),
]


def render(mode, mobile):
    palette = PALETTES[mode]
    width, inset = (420, 8) if mobile else (840, 8)
    end = width - inset
    suffix = ('-mobile' if mobile else '') + ('-dark' if mode == 'dark' else '') + '.svg'
    title = '知简。不必繁复，把简单做得再好一点。'
    c = Canvas(width, 435 if mobile else 414, palette, title, 'D · 朱砂极简。前端开发者，在代码与文字之间，简静造物。')
    c.text('ZHIJIAN / FRONTEND DEVELOPER', inset, 28, 12 if mobile else 15, color='muted', tracking=.4)
    stamp_x, stamp_y = (inset, 51) if mobile else (end - 104, 7)
    c.parts.append(f'<rect x="{stamp_x}" y="{stamp_y}" width="104" height="32" fill="#b6402d"/>')
    stamp_text_x = stamp_x + (104 - measure('简静造物', 17, 'serif', tracking=3)) / 2
    c.text('简静造物', stamp_text_x, stamp_y + (32 + 17 * TEXT_SCALE * .75) / 2, 17, color='white', family='serif', tracking=3)
    c.text('知简。', inset, 197 if mobile else 164, 91 if mobile else 112, family='serif', tracking=-5)
    vertical_x, vertical_top = (307, 112) if mobile else (379, 72)
    c.parts.append(f'<path d="M{vertical_x - 17} {vertical_top - 10}v100" stroke="{palette["line"]}"/>')
    for index, char in enumerate('代码与文字之间'):
        c.text(char, vertical_x, vertical_top + index * 15, 12 * VERTICAL_TEXT_BOOST, color='muted', family='serif')
    slogan_y = 254 if mobile else 232
    c.text('不必繁复，', inset, slogan_y, 31 if mobile else 33, family='serif')
    lead = '把'
    c.text(lead, inset, slogan_y + 49, 31 if mobile else 33, family='serif')
    red_x = inset + measure(lead, 31 if mobile else 33, 'serif')
    c.text('简单', red_x, slogan_y + 49, 31 if mobile else 33, color='red', family='serif')
    rest_x = red_x + measure('简单', 31 if mobile else 33, 'serif')
    c.text('做得再好一点。', rest_x, slogan_y + 49, 31 if mobile else 33, family='serif')
    intro_y = 350 if mobile else 333
    lines = ['我写前端，做工具，也记录日常。', '喜欢简洁的设计，', '和那些经得起使用的小东西。'] if mobile else ['我写前端，做工具，也记录日常。', '喜欢简洁的设计，和那些经得起使用的小东西。']
    for index, line in enumerate(lines):
        c.text(line, inset, intro_y + index * 29, 19 * BODY_TEXT_BOOST, color='muted')
    c.line(inset, 433 if mobile else 412, end, color='ink', width=2)
    c.save('banner' + suffix)

    c = Canvas(width, 71, palette, '以作品，作介绍。', '三件作品，一本手账、一处文字、一个世界。')
    c.text('以作品，作介绍。', inset, 39, 18)
    label = 'SELECTED / 03' if mobile else 'THREE SMALL THINGS'
    label_size = 12 if mobile else 14
    c.text(label, end - measure(label, label_size), 39, label_size, color='red')
    c.save('works-title' + suffix)

    for work in WORKS:
        height = 227 if mobile else 174
        c = Canvas(width, height, palette, work['title'], ' '.join(work['description']) + ' ' + work['tech'])
        content_x = 47 if mobile else 65
        c.text(work['number'], inset, 40, 25 if mobile else 29, color='muted', family='serif')
        c.text(work['title'], content_x, 40, 25 if mobile else 29, family='serif')
        c.arrow(end - 19, 20)
        for index, line in enumerate(work['mobile'] if mobile else work['description']):
            c.text(line, content_x, 82 + index * 31, (18 if mobile else 19) * BODY_TEXT_BOOST, color='muted')
        c.text(work['tech'], content_x, 194 if mobile else 144, 14 if mobile else 16, color='muted')
        c.line(inset, height - 1, end)
        c.save(work['slug'] + suffix)

    c = Canvas(width, 88 if mobile else 74, palette, '认真生活 · 简单做人 · 用心做事', '语无边 yuwb.dev')
    c.text('认真生活 · 简单做人 · 用心做事', inset, 34 if mobile else 44, 17 * BODY_TEXT_BOOST, color='muted')
    c.text('yuwb.dev', inset if mobile else end - measure('yuwb.dev', 17) - 26, 73 if mobile else 44, 17, color='red')
    c.arrow(105 if mobile else end - 14, 59 if mobile else 30)
    c.save('footer' + suffix)


def picture(slug, alt):
    return '\n'.join([
        '<picture>',
        f'    <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="./assets/{slug}-mobile-dark.svg">',
        f'    <source media="(max-width: 600px)" srcset="./assets/{slug}-mobile.svg">',
        f'    <source media="(prefers-color-scheme: dark)" srcset="./assets/{slug}-dark.svg">',
        f'    <img src="./assets/{slug}.svg" alt="{escape(alt, quote=True)}" width="100%">',
        '</picture>',
    ])


for mode in PALETTES:
    for mobile in (False, True):
        render(mode, mobile)

readme = [picture('banner', '知简。不必繁复，把简单做得再好一点。我写前端，做工具，也记录日常。喜欢简洁的设计，和那些经得起使用的小东西。'),
          picture('works-title', '以作品，作介绍。')]
for work in WORKS:
    alt = work['title'] + '：' + ' '.join(work['description']) + ' ' + work['tech']
    readme.append(f'<a href="{work["url"]}">\n{picture(work["slug"], alt)}\n</a>')
readme.append('<a href="https://yuwb.dev">\n' + picture('footer', '认真生活 · 简单做人 · 用心做事。前往语无边 yuwb.dev。') + '\n</a>')
(ROOT / 'README.md').write_text('\n\n'.join(readme) + '\n', encoding='utf-8')

# 许可证正文保留原文件中的标准 OFL，仅替换字体来源及版权声明。
license_path = ASSETS / 'FONT-LICENSES.txt'
original_license = license_path.read_text(encoding='utf-8')
start = original_license.index('-----------------------------------------------------------')
end_marker = 'OTHER DEALINGS IN THE FONT SOFTWARE.'
end = original_license.index(end_marker, start) + len(end_marker)
ofl = original_license[start:end]
copyrights = []
for font in FONTS.values():
    for record in font['name'].names:
        if record.nameID == 0:
            value = record.toUnicode()
            if value not in copyrights:
                copyrights.append(value)
license_path.write_text('Profile typography: LXGW WenKai Screen (Regular), all text.\n'
                        + FONT['name'].getDebugName(5) + '\n\n'
                        'https://github.com/lxgw/LxgwWenKai-Screen\n\n'
                        + '\n'.join(copyrights) + '\n\n' + ofl + '\n', encoding='utf-8')
print(f'Generated {len(list(ASSETS.glob("*.svg")))} SVG assets and README.md.')
