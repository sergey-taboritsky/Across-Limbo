# -*- coding: utf-8 -*-
"""按用户清单重分配 province 到 state，并同步 strategic region 与 owner/core。
每条改动都保留文件原有换行符(BOM/CRLF/LF)与缩进。"""
import os, re, glob

ROOT = 'C:/Users/edwar/Documents/GitHub/Across-Limbo'
STATEDIR = os.path.join(ROOT, 'history/states')
SRDIR = os.path.join(ROOT, 'map/strategicregions')

# ---------- 用户清单: 目标 state -> 省列表 ----------
MOVES = {
    1525: [10434,12426,607],
    862:  [11945,1053,7199,4083],
    600:  [11961],
    909:  [1628,10114,7653,11988,10501,10057,4183,9942],
    750:  [7201],
    861:  [10335,7665,12017,12053,4480],
    1233: [13851,8071,15911],
    1610: [2068],
    794:  [10771,13844,8035],
    1234: [15907,15903,15900,15896],
    795:  [12851,15910,15908],
}

def readf(path):
    raw = open(path,'rb').read()
    bom = raw[:3]==b'\xef\xbb\xbf'
    txt = raw[3:].decode('utf-8') if bom else raw.decode('utf-8')
    sep = '\r\n' if '\r\n' in txt else '\n'
    return txt, bom, sep

def writef(path, txt, bom, sep):
    out = txt.replace('\n','\n')  # no-op; we keep sep in txt
    data = out.encode('utf-8')
    if bom: data = b'\xef\xbb\xbf'+data
    open(path,'wb').write(data)

def get_state_file(sid):
    for f in glob.glob(os.path.join(STATEDIR, f'{sid}-*.txt')):
        return f
    return None

def provinces_of(text):
    m = re.search(r'provinces\s*=\s*\{(.*?)\}', text, re.S)
    if not m: return []
    return [int(p) for p in re.findall(r'\d+', m.group(1))]

def state_id_of(text):
    m = re.search(r'id\s*=\s*(\d+)', text)
    return int(m.group(1)) if m else None

# 建立 province -> 当前所在 state 的映射
prov2state = {}
for f in glob.glob(os.path.join(STATEDIR,'*.txt')):
    t = open(f,'rb').read().decode('utf-8','ignore')
    sid = state_id_of(t)
    for p in provinces_of(t):
        prov2state[p] = sid

# 建立 province -> 当前 strategic region
sr_files = {}
sr_provs = {}
prov2sr = {}
for f in glob.glob(os.path.join(SRDIR,'*.txt')):
    t = open(f,'rb').read().decode('utf-8','ignore')
    m = re.search(r'id\s*=\s*(\d+)', t)
    if not m: continue
    srid = int(m.group(1)); sr_files[srid] = f
    mp = re.search(r'provinces\s*=\s*\{(.*?)\}', t, re.S)
    ps = [int(p) for p in re.findall(r'\d+', mp.group(1))] if mp else []
    sr_provs[srid] = ps
    for p in ps: prov2sr[p] = srid

# 目标 state -> 其所属 strategic region (取其 province 多数派)
def target_sr(sid):
    f = get_state_file(sid)
    t = open(f,'rb').read().decode('utf-8','ignore')
    provs = provinces_of(t)
    # 取移动后该 state 的 SR：用其 present provinces 的 SR 多数
    from collections import Counter
    cnt = Counter(prov2sr.get(p) for p in provs if p in prov2sr)
    if not cnt: return None
    return cnt.most_common(1)[0][0]

# 构建 province -> (src, tgt)
prov_map = {}
for tgt, provs in MOVES.items():
    for p in provs:
        prov_map[p] = (prov2state.get(p), tgt)

# ---------- 两遍处理: 先抽离(源) 再插入(目标) ----------
captured_vp = {}     # prov -> (val,)
captured_bld = {}    # prov -> inner_text

# Pass A: 从源 state 抽离 outgoing 省的 VP / 建筑，并移出 provinces
src_states = {}
for p,(src,tgt) in prov_map.items():
    if src is not None: src_states.setdefault(src, []).append(p)

for src, provs in src_states.items():
    fp = get_state_file(src)
    txt, bom, sep = readf(fp)
    # 1) 抽离 victory_points
    for p in provs:
        m = re.search(r'victory_points\s*=\s*\{\s*'+str(p)+r'\s+(\d+)\s*\}', txt)
        if m:
            captured_vp[p] = int(m.group(1))
            txt = re.sub(r'\s*victory_points\s*=\s*\{\s*'+str(p)+r'\s+\d+\s*\}\s*', '', txt, count=1)
    # 2) 抽离 每省建筑块
    for p in provs:
        m = re.search(r'\b'+str(p)+r'\s*=\s*\{([^}]*)\}', txt)
        if m:
            captured_bld[p] = m.group(1).strip()
            txt = re.sub(r'\s*'+str(p)+r'\s*=\s*\{[^}]*\}\s*', '', txt, count=1)
    # 3) 从 provinces 移除
    def repl_prov(m):
        inner = m.group(1)
        toks = re.findall(r'\d+', inner)
        toks = [t for t in toks if int(t) not in set(provs)]
        return 'provinces = {\n\t\t' + ' '.join(toks) + ' \n\t}'
    txt = re.sub(r'provinces\s*=\s*\{(.*?)\}', repl_prov, txt, count=1, flags=re.S)
    writef(fp, txt, bom, sep)

# Pass B: 把 incoming 省 + 其 VP/建筑 插入目标 state
tgt_states = {}
for p,(src,tgt) in prov_map.items():
    tgt_states.setdefault(tgt, []).append(p)

for tgt, provs in tgt_states.items():
    fp = get_state_file(tgt)
    txt, bom, sep = readf(fp)
    # 1) provinces 增加
    def repl_prov2(m):
        inner = m.group(1)
        toks = re.findall(r'\d+', inner)
        toks = [t for t in toks if int(t) not in set(provs)] + [str(p) for p in provs]
        return 'provinces = {\n\t\t' + ' '.join(toks) + ' \n\t}'
    txt = re.sub(r'provinces\s*=\s*\{(.*?)\}', repl_prov2, txt, count=1, flags=re.S)
    # 2) 插入 victory_points (在各 VP 之后 / buildings 之前)
    vps = [p for p in provs if p in captured_vp]
    if vps:
        blk = ''
        for p in vps:
            blk += '\t\tvictory_points = {' + sep + '\t\t\t' + str(p) + ' ' + str(captured_vp[p]) + sep + '\t\t}' + sep
        txt = re.sub(r'(\t*buildings\s*=\s*\{)', lambda m: blk + m.group(1), txt, count=1)
    # 3) 插入 每省建筑块 (在 buildings 块闭合 } 之前)
    blds = [p for p in provs if p in captured_bld]
    if blds:
        # 定位 buildings 块闭合 }
        mb = re.search(r'buildings\s*=\s*\{', txt)
        if mb:
            depth=0; i=mb.end()-1; close=None
            while i < len(txt):
                if txt[i]=='{': depth+=1
                elif txt[i]=='}':
                    depth-=1
                    if depth==0: close=i; break
                i+=1
            if close is not None:
                ins = ''
                for p in blds:
                    ins += '\t\t\t' + str(p) + ' = {' + sep + '\t\t\t\t' + captured_bld[p] + sep + '\t\t\t}' + sep
                txt = txt[:close] + ins + txt[close:]
    writef(fp, txt, bom, sep)

# ---------- strategic region 同步 ----------
print("=== strategic region 同步 ===")
sr_moves = []
for p,(src,tgt) in prov_map.items():
    cur = prov2sr.get(p)
    tgt_sr = target_sr(tgt)
    if cur is None or tgt_sr is None:
        print(f"  prov {p}: SR 无法判定 (cur={cur}, tgt_sr={tgt_sr})"); continue
    if cur != tgt_sr:
        sr_moves.append((p, cur, tgt_sr))
        # 从 cur 移除 (只动 provinces 块内部 token，不压缩换行)
        cf = sr_files[cur]
        t1,b1,s1 = readf(cf)
        def rm_sr(m):
            toks = [x for x in re.findall(r'\d+', m.group(1)) if int(x) != p]
            return 'provinces = {' + ' '.join(toks) + ' }'
        t1 = re.sub(r'provinces\s*=\s*\{(.*?)\}', rm_sr, t1, count=1, flags=re.S)
        writef(cf, t1, b1, s1)
        # 加入 tgt_sr
        tf = sr_files[tgt_sr]
        t2,b2,s2 = readf(tf)
        def add_sr(m):
            toks = re.findall(r'\d+', m.group(1))
            if str(p) not in toks: toks.append(str(p))
            return 'provinces = {' + ' '.join(toks) + ' }'
        t2 = re.sub(r'provinces\s*=\s*\{(.*?)\}', add_sr, t2, count=1, flags=re.S)
        writef(tf, t2, b2, s2)
        print(f"  prov {p}: SR {cur} -> {tgt_sr}")
print(f"  共 {len(sr_moves)} 个省跨战略区移动")

# ---------- 验证: 每个省最终所在 state 与 SR ----------
print("=== 验证 ===")
prov2state2 = {}
for f in glob.glob(os.path.join(STATEDIR,'*.txt')):
    t = open(f,'rb').read().decode('utf-8','ignore')
    sid = state_id_of(t)
    for p in provinces_of(t):
        prov2state2[p] = sid
prov2sr2 = {}
for srid, f in sr_files.items():
    t = open(f,'rb').read().decode('utf-8','ignore')
    for p in re.findall(r'\d+', re.search(r'provinces\s*=\s*\{(.*?)\}', t, re.S).group(1)):
        prov2sr2[int(p)] = srid
allok = True
for p,(src,tgt) in prov_map.items():
    fs = prov2state2.get(p); fsr = prov2sr2.get(p); tsr = target_sr(tgt)
    ok = (fs == tgt) and (fsr == tsr)
    if not ok: allok = False
    print(f"  prov {p}: 现state={fs}(期望{tgt}) 现SR={fsr}(期望{tsr}) {'OK' if ok else 'FAIL'}")
print("全部正确?" , allok)

# ---------- owner/core 修改: 1122/795/1232 ----------
print("=== owner/core 修改 ===")
def edit_owner_core(sid, new_owner, new_core):
    fp = get_state_file(sid)
    txt, bom, sep = readf(fp)
    txt = re.sub(r'(\t*owner\s*=\s*)\w+', r'\1'+new_owner, txt, count=1)
    if new_core:
        txt = re.sub(r'(\t*add_core_of\s*=\s*)\w+', r'\1'+new_core, txt, count=1)
    writef(fp, txt, bom, sep)
    print(f"  state {sid}: owner -> {new_owner}, core -> {new_core}")

edit_owner_core(1122, 'SOK', 'SOK')   # 改 owner 与 core 为 SOK
edit_owner_core(795,  'IVO', 'VOL')   # owner IVO, 保留 VOL core (无 IVO core)
edit_owner_core(1232, 'IVO', 'VOL')

print("DONE")
