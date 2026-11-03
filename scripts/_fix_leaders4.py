# -*- coding: utf-8 -*-
import re, os

BASE = 'C:/Users/edwar/Documents/GitHub/Across-Limbo'
HIST = os.path.join(BASE, 'history/countries')
CHARS = os.path.join(BASE, 'common/characters')
LOC = os.path.join(BASE, 'localisation/simp_chinese')

def rd(path):
    raw = open(path, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    txt = raw[3:].decode('utf-8') if bom else raw.decode('utf-8')
    return txt, bom

def wr(path, txt, bom):
    data = txt.encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    open(path, 'wb').write(data)

def replace_set_pop(text, new_inner):
    m = re.search(r'set_popularities\s*=\s*\{', text)
    if not m:
        return text
    start = m.start()            # position BEFORE 'set_popularities'
    k = text.index('{', m.start())
    depth = 0
    j = k
    while j < len(text):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    new_block = 'set_popularities = {\n' + new_inner + '}\n'
    return text[:start] + new_block + text[j + 1:]

# ---- set_popularities 内容模板（9 桶，和=100）----
POP_ABSOLUTISM = (
    "\tcommunist = 1\n\tsyndicalism = 0\n\tsocialism = 0\n\tSocial_democracy = 0\n"
    "\tLiberalism = 1\n\tConservatism = 0\n\tAuthoritarianism = 0\n\tAbsolutism = 93\n\tNationalism = 5\n"
)
POP_COMMUNIST = (
    "\tcommunist = 93\n\tsyndicalism = 0\n\tsocialism = 0\n\tSocial_democracy = 0\n"
    "\tLiberalism = 1\n\tConservatism = 0\n\tAuthoritarianism = 1\n\tAbsolutism = 0\n\tNationalism = 5\n"
)
POP_NATIONALISM = (
    "\tcommunist = 1\n\tsyndicalism = 0\n\tsocialism = 0\n\tSocial_democracy = 0\n"
    "\tLiberalism = 1\n\tConservatism = 0\n\tAuthoritarianism = 5\n\tAbsolutism = 0\n\tNationalism = 93\n"
)

results = []

# =========================================================
# 1) KNM - Kanem / Bornu Emirate  (Sanda Kyarimi, monarchy)
# =========================================================
f = os.path.join(HIST, 'KNM - Kanem.txt')
txt, bom = rd(f)
txt = re.sub(r'\truling_party\s*=\s*\w+', '\truling_party = Absolutism', txt, count=1)
txt = replace_set_pop(txt, POP_ABSOLUTISM)
lines = [l.rstrip('\r') for l in txt.split('\n')]
for idx, l in enumerate(lines):
    if l.strip().startswith('capital ='):
        lines.insert(idx + 1, 'recruit_character = KNM_Sanda_Kyarimi')
        break
wr(f, '\r\n'.join(lines), bom)
results.append(('KNM', 'KNM_Sanda_Kyarimi'))

# =========================================================
# 2) SRL - Sri Lanka  (Bandaranaike, liberalism)
# =========================================================
f = os.path.join(HIST, 'SRL - Sri Lanka.txt')
txt, bom = rd(f)
# ruling_party 已是 Liberalism，无需改；set_popularities 已是 Liberalism 主导，保留
lines = [l.rstrip('\r') for l in txt.split('\n')]
for idx, l in enumerate(lines):
    if l.strip().startswith('capital ='):
        lines.insert(idx + 1, 'recruit_character = SRL_Solomon_Bandaranaike')
        break
wr(f, '\r\n'.join(lines), bom)
results.append(('SRL', 'SRL_Solomon_Bandaranaike'))

# =========================================================
# 3) SAU - Saudi Arabia / Nejd  (Ibn Saud, monarchy)
# =========================================================
f = os.path.join(HIST, 'SAU - Saudi Arabia.txt')
txt, bom = rd(f)
txt = re.sub(r'\truling_party\s*=\s*\w+', '\truling_party = Absolutism', txt, count=1)
txt = replace_set_pop(txt, POP_ABSOLUTISM)
lines = [l.rstrip('\r') for l in txt.split('\n')]
lines = [l for l in lines if 'recruit_character' not in l]
for idx, l in enumerate(lines):
    if l.strip().startswith('set_convoys'):
        lines.insert(idx + 1, 'recruit_character = SAU_abdulaziz_ibn_saud')
        break
wr(f, '\r\n'.join(lines), bom)
results.append(('SAU', 'SAU_abdulaziz_ibn_saud'))

# =========================================================
# 4) GNB - Guinea-Bissau -> socialist (Amilcar Cabral)
# =========================================================
f = os.path.join(HIST, 'GNB - Guinea-Bissau.txt')
txt, bom = rd(f)
txt = re.sub(r'^ruling_party\s*=\s*\w+', 'ruling_party = communist', txt, count=1, flags=re.M)
txt = replace_set_pop(txt, POP_COMMUNIST)
lines = [l.rstrip('\r') for l in txt.split('\n')]
for idx, l in enumerate(lines):
    if l.strip().startswith('recruit_character'):
        lines[idx] = 'recruit_character = GNB_Amilcar_Cabral'
        break
wr(f, '\r\n'.join(lines), bom)
results.append(('GNB', 'GNB_Amilcar_Cabral'))

# =========================================================
# 5) DJI - Djibouti -> local (Mahamoud Harbi)
# =========================================================
f = os.path.join(HIST, 'DJI - Djibouti.txt')
txt, bom = rd(f)
txt = re.sub(r'^ruling_party\s*=\s*\w+', 'ruling_party = Nationalism', txt, count=1, flags=re.M)
txt = replace_set_pop(txt, POP_NATIONALISM)
lines = [l.rstrip('\r') for l in txt.split('\n')]
for idx, l in enumerate(lines):
    if l.strip().startswith('recruit_character'):
        lines[idx] = 'recruit_character = DJI_Mahamoud_Harbi'
        break
wr(f, '\r\n'.join(lines), bom)
results.append(('DJI', 'DJI_Mahamoud_Harbi'))

# =========================================================
# 角色文件 (无 BOM + CRLF)
# =========================================================
def char_file(tag, key, sub_ideology, name_loc):
    return (
        'characters = {\n'
        '\t' + key + ' = {\n'
        '\t\tname = ' + key + '\n'
        '\t\tportraits = {\n'
        '\t\t\tcivilian = {\n'
        '\t\t\t\tlarge = GFX_portrait_large_' + key + '\n'
        '\t\t\t}\n'
        '\t\t}\n'
        '\t\tcountry_leader = {\n'
        '\t\t\tdesc = ' + key + '_desc\n'
        '\t\t\tideology = ' + sub_ideology + '\n'
        '\t\t\ttraits = {\n'
        '\t\t\t}\n'
        '\t\t\texpire = "1965.1.1"\n'
        '\t\t\tid = -1\n'
        '\t\t}\n'
        '\t}\n'
        '}\n'
    )

chars = {
    'KNM': ('KNM_Sanda_Kyarimi', 'absolute_monarchy'),
    'SRL': ('SRL_Solomon_Bandaranaike', 'National_liberalism'),
    'SAU': ('SAU_abdulaziz_ibn_saud', 'absolute_monarchy'),
    'GNB': ('GNB_Amilcar_Cabral', 'Marxism'),
    'DJI': ('DJI_Mahamoud_Harbi', 'nationalism'),
}
for tag, (key, sub) in chars.items():
    p = os.path.join(CHARS, f'TNW_{tag}_characters.txt')
    wr(p, char_file(tag, key, sub, key), bom=False)
    results.append((tag + '_char', key))

# =========================================================
# 本地化文件 (BOM + CRLF)
# =========================================================
loc_data = {
    'KNM': ('KNM_Sanda_Kyarimi', '桑达·基亚里米',
            '博尔努谢胡（1937–1967年在位），卡内米王朝世袭君主，1948年实际掌权者。（生于1872，君主豁免）'),
    'SRL': ('SRL_Solomon_Bandaranaike', '所罗门·班达拉奈克',
            '锡兰（斯里兰卡）民族主义政治家，1948年前后政坛核心人物，后创立斯里兰卡自由党。（生于1899）'),
    'SAU': ('SAU_abdulaziz_ibn_saud', '阿卜杜勒阿齐兹·伊本·沙特',
            '沙特阿拉伯开国国王（1932–1953年在位），现代沙特建国者。（生于1876，君主豁免）'),
    'GNB': ('GNB_Amilcar_Cabral', '阿米尔卡·卡布拉尔',
            '葡属几内亚社会主义革命者，几内亚和佛得角非洲独立党（PAIGC）创始人，马克思主义者。（生于1924）'),
    'DJI': ('DJI_Mahamoud_Harbi', '马哈茂德·哈尔比',
            '吉布提索马里族政治家、泛索马里主义者，主张法属索马里并入索马里，1948年时已在当地政坛活跃。（生于1921）'),
}
for tag, (key, name, desc) in loc_data.items():
    content = (
        'l_simp_chinese:\n'
        '\t' + key + ':0 "' + name + '"\n'
        '\t' + key + '_desc:0 "' + desc + '"\n'
    )
    p = os.path.join(LOC, f'TNW_{tag}_l_simp_chinese.yml')
    wr(p, content, bom=True)
    results.append((tag + '_loc', key))

print("DONE")
for r in results:
    print(r)
