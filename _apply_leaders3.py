# -*- coding: utf-8 -*-
import os, re, traceback

BASE = r'C:/Users/edwar/Documents/GitHub/Across-Limbo'
HIST = os.path.join(BASE, 'history', 'countries')
CHARS = os.path.join(BASE, 'common', 'characters')
LOC = os.path.join(BASE, 'localisation', 'simp_chinese')

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def decode(raw):
    if raw[:3] == b'\xef\xbb\xbf':
        return raw[3:].decode('utf-8'), True
    return raw.decode('utf-8'), False

def write_bom(path, text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    with open(path, 'wb') as f:
        f.write('\ufeff'.encode('utf-8'))
        f.write(text.replace('\n', '\r\n').encode('utf-8'))

def write_nobom(path, text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    with open(path, 'wb') as f:
        f.write(text.replace('\n', '\r\n').encode('utf-8'))

# (tag, history_suffix, key, name_loc, desc_loc, ideology, parent, mode)
DATA = [
    ('TZN', 'Tanzania', 'TZN_Hans_Jurgen_von_Arnim', '汉斯-于尔根·冯·阿尼姆',
     '北非德军末任总司令（1942–1943），1948年代表德国重掌坦噶尼喀殖民当局。',
     'oligarchy', 'Authoritarianism', 'history_only'),
    ('CMR', 'Cameroon', 'CMR_Walther_Nehring', '瓦尔特·内林',
     '非洲军装甲司令（1942–1943），1948年代表德国重掌喀麦隆殖民当局。',
     'oligarchy', 'Authoritarianism', 'history_only'),
    ('GAB', 'Gabon', 'GAB_Leon_Mba', '莱昂·姆巴',
     '加蓬本土政治领袖，战后重返政坛，后任独立后首任总统。',
     'oligarchy', 'Authoritarianism', 'full'),
    ('GNB', 'Guinea-Bissau', 'GNB_Ricardo_Vaz_Monteiro', '里卡多·瓦斯·蒙泰罗',
     '葡属几内亚总督（1945–1949在任），代表里斯本的殖民当局。（生年待核实）',
     'oligarchy', 'Authoritarianism', 'full'),
    ('DAH', 'Dahomey', 'DAH_Sourou_Migan_Apithy', '苏鲁-米甘·阿皮蒂',
     '达荷美本土政治家，参与法国国民议会，后任总统。',
     'oligarchy', 'Authoritarianism', 'full'),
    ('DJI', 'Djibouti', 'DJI_Jean_Chalvet', '让·沙尔韦',
     '法国殖民官员，曾任法属索马里海岸总督。（1948年实际已调任乌班吉-沙里）',
     'oligarchy', 'Authoritarianism', 'full'),
    ('MAD', 'Madagascar', 'MAD_Philibert_Tsiranana', '菲利贝尔·齐拉纳纳',
     '马达加斯加本土领袖，后任独立后首任总统。',
     'oligarchy', 'Authoritarianism', 'full'),
    ('KUW', 'Kuwait', 'KUW_Ahmad_Aljaber_Alsabah', '艾哈迈德·贾比尔·萨巴赫',
     '科威特第10任谢赫（1921–1950在位），统治近三十年的君主。',
     'absolute_monarchy', 'Absolutism', 'full'),
    ('ZNB', 'Zanzibar Sultanate', 'ZNB_Khalifa_bin_Harub', '哈里法·本·哈鲁卜',
     '桑给巴尔苏丹（1911–1960在位），布赛义迪王朝统治者。',
     'absolute_monarchy', 'Absolutism', 'full'),
    ('ETH', 'Ethiopia', 'ETH_haile_selassie', '海尔·塞拉西一世',
     '埃塞俄比亚皇帝（1930–1974在位），1941年从意大利占领下复位。',
     'absolute_monarchy', 'Absolutism', 'full'),
    ('OMA', 'Oman', 'OMA_said_bin_taimur', '赛义德·本·塔伊穆尔',
     '马斯喀特与阿曼苏丹（1932–1970在位），绝对君主。',
     'absolute_monarchy', 'Absolutism', 'full'),
    ('MLD', 'Maldives', 'MLD_Abdul_Majeed_Didi', '阿卜杜勒·马吉德·迪迪',
     '马尔代夫苏丹（1944–1952在位），英国保护国下的君主。',
     'absolute_monarchy', 'Absolutism', 'full'),
    ('YEM', 'Yeman', 'YEM_Ahmad_bin_Yahya', '艾哈迈德·本·叶海亚',
     '也门伊玛目（1948–1962在位），宰德派神权君主。',
     'absolute_monarchy', 'Absolutism', 'full'),
    # 多米尼加：仅修启动 recruit 大小写/顺序(1939 史实块不动)，ruling_party/set_pop 本就正确
    ('DOM', 'Dominican Republic', 'DOM_Rafael_Trujillo', '拉斐尔·特鲁希略',
     '多米尼加独裁者（1930–1961在位），1948年在任。',
     'nationalism', 'Nationalism', 'history_only'),
]

def pop_block(parent):
    a, ab = (0, 93) if parent == 'Absolutism' else (93, 0)
    return (
        'set_popularities = {\r\n'
        '\tcommunist = 1\r\n'
        '\tsyndicalism = 0\r\n'
        '\tsocialism = 0\r\n'
        '\tSocial_democracy = 0\r\n'
        '\tLiberalism = 1\r\n'
        '\tConservatism = 0\r\n'
        f'\tAuthoritarianism = {a}\r\n'
        f'\tAbsolutism = {ab}\r\n'
        '\tNationalism = 5\r\n'
        '}'
    )

def reorder_recruits(lines, key):
    # 只移除顶层(col-0,无缩进)的启动 recruit；保护日期块(如 1939.1.1 = {})内缩进的 recruit
    new = [l for l in lines if not (l.strip().startswith('recruit_character') and l[:1] not in '\t ')]
    cap = next((i for i, l in enumerate(new) if re.match(r'^capital\s*=', l)), None)
    if cap is None:
        raise RuntimeError('找不到 capital 行')
    new.insert(cap + 1, f'recruit_character = {key}')
    return new

def full_history(text, key, parent):
    lines = text.split('\n')
    lines = reorder_recruits(lines, key)
    # 顶层 ruling_party：有则替换(col-0)，无则插入
    # 注意：CRLF 拆分后行尾带 \r，故正则不用 $ 锚点
    rp_re = re.compile(r'^ruling_party\s*=\s*[A-Za-z]+')
    if any(rp_re.match(l) for l in lines):
        lines = [rp_re.sub(f'ruling_party = {parent}', l) for l in lines]
    else:
        cap = next(i for i, l in enumerate(lines) if re.match(r'^capital\s*=', l))
        lines.insert(cap + 1, f'ruling_party = {parent}')
    # 去重：顶层 ruling_party 只保留第一条（修复早期 \r 误判导致的重复插入）
    rp_idx = [i for i, l in enumerate(lines) if rp_re.match(l)]
    if len(rp_idx) > 1:
        for i in sorted(rp_idx[1:], reverse=True):
            del lines[i]
    # 首个 set_popularities 块（兼容缩进）
    start = next((i for i, l in enumerate(lines) if 'set_popularities = {' in l), None)
    if start is None:
        raise RuntimeError('找不到 set_popularities')
    depth = 0; end = None
    for j in range(start, len(lines)):
        depth += lines[j].count('{') - lines[j].count('}')
        if depth <= 0:
            end = j; break
    if end is None:
        raise RuntimeError('set_popularities 括号未闭合')
    lines = lines[:start] + pop_block(parent).split('\r\n') + lines[end + 1:]
    return '\n'.join(lines)

def history_only(text, key):
    lines = text.split('\n')
    lines = reorder_recruits(lines, key)
    return '\n'.join(lines)

def char_file(key, ideol):
    return (
        'characters = {\r\n'
        f'\t{key} = {{\r\n'
        f'\t\tname = {key}\r\n'
        '\t\tportraits = {\r\n'
        '\t\t\tcivilian = {\r\n'
        f'\t\t\t\tlarge = GFX_portrait_large_{key}\r\n'
        '\t\t\t}\r\n'
        '\t\t}\r\n'
        '\t\tcountry_leader = {\r\n'
        f'\t\t\tdesc = {key}_desc\r\n'
        f'\t\t\tideology = {ideol}\r\n'
        '\t\t\ttraits = {\r\n'
        '\t\t\t}\r\n'
        '\t\t\texpire = "1965.1.1"\r\n'
        '\t\t\tid = -1\r\n'
        '\t\t}\r\n'
        '\t}\r\n'
        '}\r\n'
    )

def loc_file(key, name, desc):
    return (
        'l_simp_chinese:\r\n'
        f'\t{key}:0 "{name}"\r\n'
        f'\t{key}_desc:0 "{desc}"\r\n'
    )

results = []
for tag, suffix, key, name, desc, ideol, parent, mode in DATA:
    try:
        hf = os.path.join(HIST, f'{tag} - {suffix}.txt')
        raw = read_bytes(hf)
        text, bom = decode(raw)
        if mode == 'full':
            new_text = full_history(text, key, parent)
        else:
            new_text = history_only(text, key)
        write_bom(hf, new_text)
        if mode == 'full':
            cf = os.path.join(CHARS, f'TNW_{tag}_characters.txt')
            write_nobom(cf, char_file(key, ideol))
            lf = os.path.join(LOC, f'TNW_{tag}_l_simp_chinese.yml')
            write_bom(lf, loc_file(key, name, desc))
        results.append((tag, 'OK', mode))
    except Exception as e:
        results.append((tag, f'ERROR: {e}', mode))
        traceback.print_exc()

print('==== 处理报告 ====')
for tag, status, mode in results:
    print(f'  {tag}: {status} ({mode})')

# 逐国校验
print('\n==== 校验 ====')
for tag, suffix, key, name, desc, ideol, parent, mode in DATA:
    if not any(r[0] == tag or r[1].startswith('OK') for r in results):
        continue
    hf = os.path.join(HIST, f'{tag} - {suffix}.txt')
    t = decode(read_bytes(hf))[0]
    recs = [l.strip() for l in t.split('\n') if l.strip().startswith('recruit_character')]
    first_ok = (recs and recs[0] == f'recruit_character = {key}')
    rp = [l.strip() for l in t.split('\n') if re.match(r'^ruling_party\s*=', l)]
    print(f'[{tag}] recruit数={len(recs)} 首位正确={first_ok} 顶层ruling_party={rp}')
print('SCRIPT 3 DONE')
