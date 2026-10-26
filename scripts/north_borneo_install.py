# -*- coding: utf-8 -*-
"""北婆罗洲骨架：WES=砂拉越(借壳) / BRN=文莱 / SAB=沙巴
角色 + 饼图 + history 重写 + BRN capital 死键修复 + 颜色/gfx 修正 + loc + 壳位同步
房规：common/characters 无BOM+CRLF；history/countries BOM+CRLF；loc BOM+CRLF
幂等守卫：新建文件已存在且含标记则跳过该步
"""
import os, sys, hashlib, shutil

ROOT = r"C:\Users\苗灏\Documents\GitHub\Across Limbo"
SHELL = r"D:\SteamLibrary\steamapps\workshop\content\394360\2929339638"
BOM = b'\xef\xbb\xbf'

steps = []
def log(msg):
    print(msg); steps.append(msg)

def read_b(p):
    with open(p, 'rb') as f: return f.read()

def write_b(p, data):
    with open(p, 'wb') as f: f.write(data)

def to_crlf(s):
    s = s.replace('\r\n', '\n')
    return s.replace('\n', '\r\n')

def assert_clean(raw, want_bom, name):
    if want_bom:
        assert raw[:3] == BOM, f"{name}: BOM missing"
        body = raw[3:]
    else:
        assert raw[:3] != BOM, f"{name}: unexpected BOM"
        body = raw
    assert b'\r\r\n' not in raw, f"{name}: CR-CR-LF found"
    assert body.count(b'\xef\xbb\xbf') == 0, f"{name}: stray BOM in body"
    txt = body.decode('utf-8')
    assert txt.count('{') == txt.count('}'), f"{name}: brace unbalanced {{={txt.count('{')} }}={txt.count('}')}"
    assert '{{' not in txt and '}}' not in txt, f"{name}: double braces found"

def check_shell(rel):
    a = read_b(os.path.join(ROOT, rel))
    b = read_b(os.path.join(SHELL, rel))
    h1 = hashlib.md5(a).hexdigest(); h2 = hashlib.md5(b).hexdigest()
    assert h1 == h2, f"shell mismatch: {rel}"
    log(f"  shell OK  {rel}  md5={h1[:12]}")

# ---------- 1. 角色文件（common/characters：无BOM+CRLF） ----------
CHAR_DIR = os.path.join(ROOT, 'common', 'characters')

def make_char_file(tag, comment, char_id, ideol, name_loc, desc_loc):
    """生成角色文件 bytes（无BOM+CRLF）"""
    inner = (
        f"\t#{comment}\n"
        f"\t{char_id} = {{\n"
        f"\t\tname = {name_loc}\n"
        f"\t\tcountry_leader = {{\n"
        f"\t\t\tdesc = {desc_loc}\n"
        f"\t\t\tideology = {ideol}\n"
        f"\t\t\ttraits = {{\n"
        f"\t\t\t}}\n"
        f"\t\t}}\n"
        f"\t}}\n"
    )
    txt = "characters = {\n" + inner + "}\n"
    return to_crlf(txt).encode('utf-8')

char_jobs = [
    ('TNW_WES_characters.txt', 'characters_WES_done',
     '阿旺蓝里（砂拉越自治国领袖，十三太保首领，亲印尼激进马来民族主义者）',
     'WES_Awang_Rambli', 'Ultra_Nationalism'),
    ('TNW_BRN_characters.txt', 'characters_BRN_done',
     '艾哈迈德·塔吉丁（文莱第27世苏丹，1924年即位）',
     'BRN_Ahmad_Tajuddin', 'absolute_monarchy'),
    ('TNW_SAB_characters.txt', 'characters_SAB_done',
     '慕斯达法·哈伦（古达抗日游击领袖，巴瑶-苏禄贵族）',
     'SAB_Mustapha_Harun', 'Ultra_Nationalism'),
]
for fname, marker, comment, cid, ideol in char_jobs:
    p = os.path.join(CHAR_DIR, fname)
    if os.path.exists(p) and cid.encode() in read_b(p):
        log(f"SKIP char {fname} (exists)")
    else:
        data = make_char_file(fname, comment, cid, ideol, cid, cid + '_desc')
        write_b(p, data)
        assert_clean(read_b(p), want_bom=False, name=fname)
        log(f"WRITE char {fname} ({cid}, {ideol})")

# ---------- 2. history 重写（BOM+CRLF） ----------
HIST = os.path.join(ROOT, 'history', 'countries')

TECH_BLOCK = to_crlf("""set_technology = {
	infantry_weapons = 1
}

set_convoys = 20

1939.1.1 = {
	#generic focuses
	complete_national_focus = army_effort
	complete_national_focus = equipment_effort
	complete_national_focus = motorization_effort
	complete_national_focus = industrial_effort
	complete_national_focus = construction_effort
	complete_national_focus = production_effort

	set_technology = {
		tech_support = 1
		tech_recon = 1
		support_weapons = 1
		gw_artillery = 1

		#electronics
		electronic_mechanical_engineering = 1
		radio = 1
		radio_detection = 1
		mechanical_computing = 1
		computing_machine = 1

		#industry
		basic_machine_tools = 1
		improved_machine_tools = 1
		construction1 = 1
		construction2 = 1
		dispersed_industry = 1
		dispersed_industry2 = 1
	}
}
""")

def pop_block(pairs):
    order = ['communist','syndicalism','socialism','Social_democracy','Liberalism',
             'Conservatism','Authoritarianism','Absolutism','Nationalism']
    lines = ['set_popularities = {']
    for k in order:
        lines.append(f"\t{k} = {pairs[k]}")
    lines.append('}')
    return to_crlf('\n'.join(lines) + '\n')

def hist_bytes(capital, recruit, pops, ruling, election, elections_allowed, last_election_note=''):
    txt = "\ufeff" + f"capital = {capital}\n\n"
    txt += TECH_BLOCK + "\n"
    for r in recruit:
        txt += f"recruit_character = {r}\n"
    txt += "\n"
    txt += "set_politics = {\n"
    txt += f"\truling_party = {ruling}\n"
    txt += f"\tlast_election = \"{election}\"\n"
    txt += "\telection_frequency = 48\n"
    txt += f"\telections_allowed = {'yes' if elections_allowed else 'no'}\n"
    txt += "}\n"
    txt += pop_block(pops) if isinstance(pops, dict) else pops
    # txt 已含 BOM，直接 utf-8 编码（\ufeff 即 BOM 头）
    return txt.encode('utf-8')

# --- WES 砂拉越：民60/社民15/保10/共10/自5，Nationalism 执政，无选举 ---
wes_pops = {'communist':10,'syndicalism':0,'socialism':0,'Social_democracy':15,
            'Liberalism':5,'Conservatism':10,'Authoritarianism':0,'Absolutism':0,'Nationalism':60}
wes = hist_bytes(882, ['WES_Awang_Rambli'], wes_pops, 'Nationalism', '1946.7.1', False)
# hist_bytes 里 \ufeff 会被 encode 成 BOM —— 正确

# --- BRN 文莱：绝55/保20/民15/自7/共3，Absolutism 执政，无选举 ---
brn_pops = {'communist':3,'syndicalism':0,'socialism':0,'Social_democracy':0,
            'Liberalism':7,'Conservatism':20,'Authoritarianism':0,'Absolutism':55,'Nationalism':15}
brn = hist_bytes(881, ['BRN_Ahmad_Tajuddin'], brn_pops, 'Absolutism', '1936.1.1', False)

# --- SAB 沙巴：民50/自20/保15/社民10/共5，Nationalism 执政，有选举 ---
sab_pops = {'communist':5,'syndicalism':0,'socialism':0,'Social_democracy':10,
            'Liberalism':20,'Conservatism':15,'Authoritarianism':0,'Absolutism':0,'Nationalism':50}
sab = hist_bytes(333, ['SAB_Mustapha_Harun'], sab_pops, 'Nationalism', '1946.7.1', True)

hist_jobs = [
    (os.path.join(HIST, 'WES - Western Sahara.txt'), wes, 'WES(Sarawak)'),
    (os.path.join(HIST, 'BRN - Brunei.txt'), brn, 'BRN'),
    (os.path.join(HIST, 'SAB - Sabah.txt'), sab, 'SAB'),
]
for p, data, label in hist_jobs:
    old = read_b(p)
    data = data.replace(BOM + BOM, BOM)  # 防双BOM
    write_b(p, data)
    assert_clean(read_b(p), want_bom=True, name=os.path.basename(p))
    log(f"REWRITE history {label}: {os.path.basename(p)} ({len(old)}B -> {len(data)}B)")

# 汇总各档总和断言
for label, pops in [('WES', wes_pops), ('BRN', brn_pops), ('SAB', sab_pops)]:
    s = sum(pops.values())
    assert s == 100, f"{label} popularities sum={s} != 100"
    log(f"  {label} popularities sum = 100 OK")

# ---------- 3. Western Sahara.txt 颜色/gfx（common/countries：无BOM） ----------
p_ws = os.path.join(ROOT, 'common', 'countries', 'Western Sahara.txt')
raw = read_b(p_ws)
txt = raw.decode('utf-8').replace('\r\n', '\n')
txt = txt.replace('graphical_culture = african_gfx', 'graphical_culture = asian_gfx')
txt = txt.replace('graphical_culture_2d = african_2d', 'graphical_culture_2d = asian_2d')
import re
txt = re.sub(r'color = rgb \{[\d ]+\}', 'color = rgb { 255 204 41 }', txt)  # 布鲁克王朝黄
out = to_crlf(txt.strip('\n')) + b'' if False else to_crlf(txt).encode('utf-8')
write_b(p_ws, out)
assert_clean(read_b(p_ws), want_bom=False, name='Western Sahara.txt')
log("REWRITE common/countries/Western Sahara.txt: gfx->asian, color->Brooke yellow")

# ---------- 4. loc（BOM+CRLF，换行用字面\n规则仅用于值内；此处为独立行键） ----------
LOC_DIR = os.path.join(ROOT, 'localisation', 'simp_chinese')
loc_jobs = {
    'TNW_WES_l_simp_chinese.yml': [
        ('WES_Awang_Rambli', '阿旺蓝里'),
        ('WES_Awang_Rambli_desc', '十三太保首领，砂拉越马来青年运动的激进派。誓以生命换取独立，倾心于新生的印度尼西亚共和国。'),
    ],
    'TNW_BRN_l_simp_chinese.yml': [
        ('BRN_Ahmad_Tajuddin', '艾哈迈德·塔吉丁'),
        ('BRN_Ahmad_Tajuddin_desc', '文莱第27世苏丹，1924年即位。战后重建石油之国的君主，在王族与青年改革派之间维持平衡。'),
    ],
    'TNW_SAB_l_simp_chinese.yml': [
        ('SAB_Mustapha_Harun', '慕斯达法·哈伦'),
        ('SAB_Mustapha_Harun_desc', '古达巴瑶-苏禄贵族，抗日游击队领袖，其弟死于日军拷问。日本合作政府崩溃后，他成为北婆罗洲众望所归的领袖。'),
    ],
}
for fname, keys in loc_jobs.items():
    p = os.path.join(LOC_DIR, fname)
    if os.path.exists(p):
        log(f"SKIP loc {fname} (exists, manual check)")
        continue
    lines = ['l_simp_chinese:']
    for k, v in keys:
        assert '"' not in v or v.count('"') % 2 == 0
        v2 = v.replace('"', '\\"')
        lines.append(f' {k}:0 "{v2}"')
    txt = '\n'.join(lines) + '\n'
    data = BOM + to_crlf(txt).encode('utf-8')
    write_b(p, data)
    assert_clean(read_b(p), want_bom=True, name=fname)
    log(f"WRITE loc {fname} ({len(keys)} keys)")

# ---------- 5. 国家名 loc 检查（BRN/SAB） ----------
p_cl = os.path.join(LOC_DIR, 'countries_l_simp_chinese.yml')
raw = read_b(p_cl).decode('utf-8-sig')
for tag in ('BRN', 'SAB'):
    hit = [l for l in raw.split('\n') if l.strip().startswith(f'{tag}:')]
    log(f"  country loc {tag}: {hit[0].strip() if hit else 'MISSING!'}")

# ---------- 6. 壳位同步 ----------
sync_rels = [
    'common\\characters\\TNW_WES_characters.txt',
    'common\\characters\\TNW_BRN_characters.txt',
    'common\\characters\\TNW_SAB_characters.txt',
    'history\\countries\\WES - Western Sahara.txt',
    'history\\countries\\BRN - Brunei.txt',
    'history\\countries\\SAB - Sabah.txt',
    'common\\countries\\Western Sahara.txt',
    'localisation\\simp_chinese\\TNW_WES_l_simp_chinese.yml',
    'localisation\\simp_chinese\\TNW_BRN_l_simp_chinese.yml',
    'localisation\\simp_chinese\\TNW_SAB_l_simp_chinese.yml',
]
log("--- shell sync ---")
for rel in sync_rels:
    dst = os.path.join(SHELL, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, rel), dst)
    check_shell(rel)

log(f"ALL DONE: {len(steps)} steps")
