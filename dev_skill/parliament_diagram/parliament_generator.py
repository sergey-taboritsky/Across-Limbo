# -*- coding: utf-8 -*-
"""
HOI4 半圆议会席位图 —— headless 自动生成器
=========================================================================
来源：C:/Users/edwar/Documents/GitHub/hoi4-parliament-diagram-fork/ParliamentGUIGenerator.py
      （Flaxbeard / fedacking 的 tkinter GUI 版，基于 slashme/parliamentdiagram）
本文件把其中的「座位坐标算法」与「4 段代码模板」抽出来，去掉 tkinter/Pillow
依赖，改成 JSON 配置驱动，一次性产出可直接拷进模组的全部代码与本地化。

用法：
    python parliament_generator.py --config examples/MAL_leg_104/config.json
    python parliament_generator.py --self-test
    python parliament_generator.py --config xxx.json --out /some/dir --check-only

配置文件格式见 dev_skill/PARLIAMENT_DIAGRAM_SKILL.md §3。
产出文件清单见同文档 §4。所有 .txt / .yml 产物自动写成 CRLF；.yml 带单 BOM。

⚠️ 与原版工具的差异（故意为之，详见 SOP §2）：
  1. 修掉原版「最外圈只剩 1 席时 append 三元组」导致 oaf 排序 IndexError 的 bug，
     统一为四元组 [angle, x, y, R]。
  2. 半径公式原版把分母 (4 * N) 写死成 (4 * 4)；这里保留 4 为默认值，
     但允许 radius_rows = "auto" 使用真实行数 N（图形更匀称）。
  3. 原版 icon 半径取自预览小图 small_circle.png 的宽度（9px），这里显式参数 icon_size。
  4. 原版只输出坐标数组；frame（党团颜色）数组要自己写。这里按席位表自动生成
     resize_array 分段填充，可选用运行时变量，席位一变即可刷新。
"""

import argparse
import json
import math
import os
import sys

# 原版 ROW_TOTALS：第 i 行（从 1 起）累计可容纳的席位总数
ROW_TOTALS = [
    4, 15, 33, 61, 95, 138, 189, 247, 313, 388, 469, 559, 657, 762, 876, 997,
    1126, 1263, 1408, 1560, 1722, 1889, 2066, 2250, 2442, 2641, 2850, 3064,
    3289, 3519, 3759, 4005, 4261, 4522, 4794, 5071, 5358, 5652, 5953, 6263,
    6581, 6906, 7239, 7581, 7929, 8287, 8650, 9024, 9404, 9793, 10187, 10594,
    11003, 11425, 11850, 12288, 12729, 13183, 13638, 14109, 14580, 15066,
    15553, 16055, 16557, 17075, 17592, 18126, 18660, 19208, 19758, 20323,
    20888, 21468, 22050, 22645, 23243, 23853, 24467, 25094, 25723, 26364,
    27011, 27667, 28329, 29001, 29679, 30367, 31061,
]

DEFAULTS = {
    "spread": 1.85,
    "first_row_radius": 5.7,
    "ordering_factor": 0.0,
    "radius_rows": 4,          # 原版写死 4；"auto" = 用真实行数
    "icon_size": 9,            # 原版 small_circle.png 的宽度
    "seat_source": "variables",
    "total_seats_var": None,
}


# ---------------------------------------------------------------------------
# 1. 座位坐标（严格复刻原版 update_positions + output_file 的坐标公式）
# ---------------------------------------------------------------------------
def seat_positions(total, spread=1.85, first_row_radius=5.7,
                   ordering_factor=0.0, radius_rows=4, icon_size=9):
    if total < 10:
        raise ValueError("total_seats 必须 >= 10，原版工具滑条下限也是 10")
    if total > ROW_TOTALS[-1]:
        raise ValueError("total_seats 超出 ROW_TOTALS 表容量 %d" % ROW_TOTALS[-1])

    rows = None
    for i, cap in enumerate(ROW_TOTALS):
        if cap >= total:
            rows = i + 1
            break
    if rows is None:
        raise ValueError("无法确定行数")

    N = rows if radius_rows == "auto" else float(radius_rows)
    hole = first_row_radius
    oaf = ordering_factor
    radius = 0.1
    poslist = []

    def row_radius(i):
        return (3.0 * hole + spread * i - 2.0) / (4.0 * N)

    # 内部各圈：按「图形饱满度」比例分配席位
    for i in range(1, rows):
        J = int(float(total) / ROW_TOTALS[rows - 1] *
                math.pi / (2.0 * math.asin(2.0 / (3.0 * rows + 4.0 * i - 2.0))))
        R = row_radius(i)
        if J <= 0:
            continue
        if J == 1:
            poslist.append([math.pi / 2.0, 1.75 * R, R, R])
        else:
            for j in range(J):
                angle = (float(j) * (math.pi - 2.0 * math.sin(radius / R)) /
                         (float(J) - 1.0) + math.sin(radius / R))
                poslist.append([angle, R * math.cos(angle), R * math.sin(angle), R])

    # 剩余席位全部铺到最外圈
    J = total - len(poslist)
    R = row_radius(rows)
    if J == 1:
        # 原版此处 append 的是 3 元组，会在下面排序取 p[3] 时崩；这里补成 4 元组
        poslist.append([math.pi / 2.0, 1.75 * R, R, R])
    else:
        for j in range(J):
            angle = (float(j) * (math.pi - 2.0 * math.sin(radius / R)) /
                     (float(J) - 1.0) + math.sin(radius / R))
            poslist.append([angle, R * math.cos(angle), R * math.sin(angle), R])

    # 按角度降序排列 → 决定「从左到右」的填色顺序，也就是 frame 数组的分配顺序
    poslist.sort(reverse=True, key=lambda p: (
        p[0] + oaf * p[3] if p[0] > math.pi / 2.0 else p[0] - oaf * p[3]))

    xraw = [p[1] * 100.0 for p in poslist]
    yraw = [p[2] * 100.0 for p in poslist]
    out_width = max(xraw) - min(xraw) + icon_size
    out_height = max(yraw) - min(yraw) + icon_size + 10

    coords = []
    for p in poslist:
        x = round(p[1] * 100.0 + (out_width / 2.0) - icon_size / 2.0)
        y = round(out_height - 100.0 * p[2] - icon_size / 2.0)
        coords.append((x, y))

    meta = {
        "total_seats": total, "rows": rows, "radius_rows": N,
        "spread": spread, "first_row_radius": hole,
        "ordering_factor": oaf, "icon_size": icon_size,
        "out_width": round(out_width, 2), "out_height": round(out_height, 2),
        "x_min": min(c[0] for c in coords), "x_max": max(c[0] for c in coords),
        "y_min": min(c[1] for c in coords), "y_max": max(c[1] for c in coords),
    }
    return coords, meta


# ---------------------------------------------------------------------------
# 2. 小工具
# ---------------------------------------------------------------------------
def cfg_get(cfg, key):
    return cfg[key] if key in cfg else DEFAULTS.get(key)


def crlf(text):
    return text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')


def party_source(cfg, party, idx):
    """返回该党团席位数的表达式（变量或常量）。"""
    if cfg_get(cfg, "seat_source") == "variables":
        return party.get("var") or ("%s_%s_seats" % (cfg["prefix"], party["id"]))
    return str(party["seats"])


def party_frame(party, idx):
    return int(party.get("frame", idx + 1))


# ---------------------------------------------------------------------------
# 3. 各段代码生成
# ---------------------------------------------------------------------------
def gen_positions(cfg, coords, meta):
    arr_x = cfg["arrays"]["x"]
    arr_y = cfg["arrays"]["y"]
    name = cfg["effects"]["init_positions"]
    L = []
    a = L.append
    a('# ============================================================')
    a('# %s —— 座位坐标数组（自动生成，勿手改）' % name)
    a('# 生成参数：总席位 %d / %d 圈 / spread %s / first_row_radius %s / icon %d'
      % (meta["total_seats"], meta["rows"], meta["spread"],
         meta["first_row_radius"], meta["icon_size"]))
    a('# 坐标范围：x %d..%d  y %d..%d' %
      (meta["x_min"], meta["x_max"], meta["y_min"], meta["y_max"]))
    a('# 只需生成一次（开局或首次打开议会时）；更改总席位数才需要重跑本工具。')
    a('# ============================================================')
    a(name + ' = {')
    a('\tclear_array = ' + arr_x)
    a('\tclear_array = ' + arr_y)
    for x, y in coords:
        a('\tadd_to_array = { %s = %d }' % (arr_x, x))
        a('\tadd_to_array = { %s = %d }' % (arr_y, y))
    a('}')
    return '\n'.join(L) + '\n'


def gen_frames(cfg, meta):
    arr_f = cfg["arrays"]["frame"]
    fx = cfg["effects"]["reload_frames"]
    init = cfg["effects"]["init_all"]
    if cfg_get(cfg, "seat_source") == "variables":
        total_var = cfg_get(cfg, "total_seats_var") or (cfg["prefix"] + "_total_seats")
    else:
        total_var = str(cfg["total_seats"])
    parties = cfg["parties"]
    L = []
    a = L.append
    a('# ============================================================')
    a('# 议会席位分配 —— frame 数组分段填充（自动生成，勿手改）')
    a('# resize_array 会把数组扩到 size，新增槽位填 value = frame 编号；')
    a('# 因此按「累计席位」依次 resize，就能把每个党团填成一段连续颜色。')
    a('# 最后一段强制拉到「总席位」变量，因此空缺议席 = 总席位 - 在籍党团合计，')
    a('# 自动吸收任何席位差额，且 frame 数组长度恒等于坐标数组长度（不会溢出圆点）。')
    a('# ============================================================')
    a(fx + ' = {')
    a('\tclear_array = ' + arr_f)
    for idx, p in enumerate(parties):
        src = party_source(cfg, p, idx)
        frame = party_frame(p, idx)
        a('\t# %s  frame %d  %s' % (p["name"], frame, src))
        if idx == len(parties) - 1:
            a('\tset_temp_variable = { cum = %s }' % total_var)
        elif idx == 0:
            a('\tset_temp_variable = { cum = %s }' % src)
        else:
            a('\tadd_to_temp_variable = { cum = %s }' % src)
        a('\tresize_array = {')
        a('\t\tarray = ' + arr_f)
        a('\t\tvalue = %d' % frame)
        a('\t\tsize = cum')
        a('\t}')
    a('}')
    a('')
    a(init + ' = {')
    a('\t' + cfg["effects"]["init_positions"] + ' = yes')
    a('\t' + fx + ' = yes')
    a('}')
    return '\n'.join(L) + '\n'


def gen_scripted_gui(cfg):
    g = cfg["gui"]
    a_x, a_y, a_f = cfg["arrays"]["x"], cfg["arrays"]["y"], cfg["arrays"]["frame"]
    L = []
    a = L.append
    a('# 放进 common/scripted_guis/<任意文件名>.txt')
    a('scripted_gui = {')
    a('\t' + cfg["scripted_gui"] + ' = {')
    a('\t\twindow_name = "%s"' % g["window_name"])
    a('\t\tcontext_type = player_context')
    a('')
    a('\t\tvisible = {')
    a('\t\t\thas_country_flag = ' + cfg["open_flag"])
    a('\t\t}')
    a('')
    a('\t\tdynamic_lists = {')
    a('\t\t\t' + g["diagram_grid"] + ' = {')
    a('\t\t\t\tarray = ' + a_x)
    a('\t\t\t\tchange_scope = no')
    a('\t\t\t\tentry_container = ' + g["seat_container"])
    a('\t\t\t\tindex = seat_idx')
    a('\t\t\t}')
    a('\t\t}')
    a('')
    a('\t\tproperties = {')
    a('\t\t\t' + g["seat_icon"] + ' = {')
    a('\t\t\t\tx = %s^seat_idx' % a_x)
    a('\t\t\t\ty = %s^seat_idx' % a_y)
    a('\t\t\t\tframe = %s^seat_idx' % a_f)
    a('\t\t\t}')
    a('\t\t}')
    a('')
    a('\t\teffects = {')
    a('\t\t\tclose_button_click = {')
    a('\t\t\t\tclr_country_flag = ' + cfg["open_flag"])
    a('\t\t\t}')
    a('\t\t\trefresh_button_click = {')
    a('\t\t\t\t' + cfg["effects"]["reload_frames"] + ' = yes')
    a('\t\t\t}')
    a('\t\t}')
    a('\t}')
    a('}')
    return '\n'.join(L) + '\n'


def gen_gui(cfg):
    g = cfg["gui"]
    L = []
    a = L.append
    a('# 把下面两个 containerWindowType 并进目标 .gui 文件的 guiTypes = { ... } 内')
    a('# 座位 iconType 必须放在「独立容器」里，才能被 dynamic_lists 复制成 N 份')
    a('guiTypes = {')
    a('\tcontainerWindowType = {')
    a('\t\tname = "%s"' % g["window_name"])
    a('\t\tposition = { x = 0 y = 0 }')
    a('\t\tsize = { width = %d height = %d }' % (g["width"], g["height"]))
    a('\t\torientation = center')
    a('\t\torigo = center')
    a('\t\tmoveable = yes')
    a('')
    a('\t\tbackground = {')
    a('\t\t\tname = "background"')
    a('\t\t\tquadTextureSprite = "%s"' % g["background_sprite"])
    a('\t\t}')
    a('')
    a('\t\tgridboxtype = {')
    a('\t\t\tname = "%s"' % g["diagram_grid"])
    a('\t\t\tposition = { x = %d y = %d }' % (g["grid_x"], g["grid_y"]))
    a('\t\t\tsize = { width = 100%% height = 100%% }')
    a('\t\t\tslotsize = { width = 100%% height = 0 }')
    a('\t\t\tmax_slots_horizontal = 1')
    a('\t\t\tadd_horizontal = no')
    a('\t\t}')
    a('')
    a('\t\tbuttonType = {')
    a('\t\t\tname = "close_button"')
    a('\t\t\tspriteType = "GFX_closebutton"')
    a('\t\t\tposition = { x = %d y = 20 }' % (g["width"] - 52))
    a('\t\t\tpdx_tooltip = "%s"' % cfg["loc"]["close_tooltip"])
    a('\t\t}')
    a('\t\tbuttonType = {')
    a('\t\t\tname = "refresh_button"')
    a('\t\t\tspriteType = "GFX_browser_refresh"')
    a('\t\t\tposition = { x = 16 y = 16 }')
    a('\t\t\tpdx_tooltip = "%s"' % cfg["loc"]["refresh_tooltip"])
    a('\t\t}')
    a('\t}')
    a('\tcontainerWindowType = {')
    a('\t\tname = "%s"' % g["seat_container"])
    a('\t\tposition = { x = 0 y = 0 }')
    a('')
    a('\t\ticonType = {')
    a('\t\t\tname = "%s"' % g["seat_icon"])
    a('\t\t\tquadTextureSprite = "%s"' % g["seat_sprite"])
    a('\t\t\tpdx_tooltip = "%s"' % cfg["loc"]["seat_tooltip"])
    a('\t\t}')
    a('\t}')
    a('}')
    return '\n'.join(L) + '\n'


def gen_gfx(cfg):
    g = cfg["gui"]
    n = max(party_frame(p, i) for i, p in enumerate(cfg["parties"]))
    L = []
    a = L.append
    a('# 把下面 spriteType 并进目标 .gfx 文件的 spriteTypes = { ... } 内')
    a('# 贴图取自 hoi4-parliament-diagram-fork/parliament_sample/gfx/interface/parliament_sample/')
    a('# seat 图是横向 N 帧精灵图，每帧一种党团颜色；noOfFrames 必须 = 党团数 %d' % n)
    a('spriteTypes = {')
    a('\tspriteType = {')
    a('\t\tname = "%s"' % g["background_sprite"])
    a('\t\ttextureFile = "%s"' % cfg["textures"]["background"])
    a('\t}')
    a('\tspriteType = {')
    a('\t\tname = "%s"' % g["seat_sprite"])
    a('\t\ttextureFile = "%s"' % cfg["textures"]["seat"])
    a('\t\tnoOfFrames = %d' % n)
    a('\t}')
    a('}')
    return '\n'.join(L) + '\n'


def gen_scripted_loc(cfg):
    arr_f = cfg["arrays"]["frame"]
    L = []
    a = L.append
    a('# 放进 common/scripted_localisation/<任意文件名>.txt')
    a('# seat_idx 由 dynamic_lists 提供；按 frame 值显示对应党团名')
    a('defined_text = {')
    a('\tname = ' + cfg["sploc"])
    for idx, p in enumerate(cfg["parties"]):
        frame = party_frame(p, idx)
        a('\ttext = {')
        a('\t\ttrigger = {')
        a('\t\t\tcheck_variable = { %s^seat_idx = %d }' % (arr_f, frame))
        a('\t\t}')
        a('\t\tlocalization_key = ' + p["loc"])
        a('\t}')
    a('}')
    return '\n'.join(L) + '\n'


def gen_localisation(cfg):
    L = []
    a = L.append
    a('l_simp_chinese:')
    a(' # 议会席位图（自动生成 · 总席位 %d）' % cfg["total_seats"])
    a(' %s: "[%s]"' % (cfg["loc"]["seat_tooltip"], cfg["sploc"]))
    for p in cfg["parties"]:
        a(' %s: "%s"' % (p["loc"], p["name"]))
    for key, val in cfg["loc"]["extra"].items():
        a(' %s: "%s"' % (key, val))
    return '\n'.join(L) + '\n'


def gen_integration(cfg):
    """接线片段：决议 / 事件 / 月度刷新，明确标注插入位置，不生成独立分类。"""
    init = cfg["effects"]["init_all"]
    reload_fx = cfg["effects"]["reload_frames"]
    prefix = cfg["prefix"]
    L = []
    a = L.append
    a('# ============================================================')
    a('# 接线片段（不是可直接加载的独立文件，按注释合并到对应文件）')
    a('# ============================================================')
    a('')
    a('# --- A. 追加到 common/decisions/<该分类已有决议文件> 的分类块内部 ---')
    a('# 注意：本仓规范是「分类单独定义在 categories/，决议文件打开同名顶层块」，')
    a('# 因此下面两个决议必须并进已有的 %s = { ... } 块，' % cfg["decision_category"])
    a('# 不要在 categories/ 里再写 decision =，也不要在决议里写 category =。')
    a('%s = {' % cfg["decision_category"])
    a('\t' + cfg["decisions"]["open"] + ' = {')
    a('\t\ticon = %s' % cfg["icons"]["open"])
    a('\t\tfire_only_once = no')
    a('\t\tcost = 0')
    a('\t\tvisible = { original_tag = %s }' % cfg["tag"])
    a('\t\tcomplete_effect = {')
    a('\t\t\tif = {')
    a('\t\t\t\tlimit = { NOT = { has_country_flag = %s } }' % cfg["initialized_flag"])
    a('\t\t\t\t' + init + ' = yes')
    a('\t\t\t\tset_country_flag = ' + cfg["initialized_flag"])
    a('\t\t\t}')
    a('\t\t\t' + reload_fx + ' = yes')
    a('\t\t\tset_country_flag = ' + cfg["open_flag"])
    a('\t\t}')
    a('\t\tai_will_do = { base = 0 }')
    a('\t}')
    a('')
    a('\t' + cfg["decisions"]["refresh"] + ' = {')
    a('\t\ticon = %s' % cfg["icons"]["refresh"])
    a('\t\tfire_only_once = no')
    a('\t\tcost = 0')
    a('\t\tvisible = {')
    a('\t\t\toriginal_tag = %s' % cfg["tag"])
    a('\t\t\thas_country_flag = ' + cfg["initialized_flag"])
    a('\t\t}')
    a('\t\tcomplete_effect = {')
    a('\t\t\t' + reload_fx + ' = yes')
    a('\t\t}')
    a('\t\tai_will_do = { base = 0 }')
    a('\t}')
    a('}')
    a('')
    a('# --- B. 席位变量变化后刷新颜色（推荐放在算分脚本末尾）---')
    a('# ' + reload_fx + ' = yes')
    a('# 若走 on_actions，可用 on_monthly_<TAG> 里同样调用一次；')
    a('# 坐标数组只在首次打开时生成，不要每月重建 200+ 行 add_to_array。')
    a('')
    a('# --- C. 贴图落位 ---')
    a('# 从 hoi4-parliament-diagram-fork/parliament_sample/gfx/interface/parliament_sample/')
    a('# 复制两张 dds 到本模组的 %s 目录（或改成自己的多帧座位图）' % cfg["textures"]["background"].rsplit('/', 1)[0])
    return '\n'.join(L) + '\n'


def gen_preview_svg(cfg, coords, meta):
    parties = cfg["parties"]
    total = cfg["total_seats"]
    # 按席位表顺序给每个坐标分配 frame 颜色（与 resize_array 的分段顺序一致）
    colors = ["#3a6ea5", "#d1495b", "#2e8b6b", "#e0a458", "#8e6bbf",
              "#4aa3a2", "#b05252", "#8a8f98", "#c2b280", "#5b7c99"]
    frame_color = {}
    for i, p in enumerate(parties):
        frame_color[party_frame(p, i)] = p.get("color") or colors[i % len(colors)]

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    pad = 24
    W = max(xs) + pad * 2
    H = max(ys) + pad * 2 + 40 + len(parties) * 20
    r = max(2.5, cfg_get(cfg, "icon_size") / 2.0)

    L = []
    a = L.append
    a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    a('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H))
    a('<text x="%d" y="20" font-size="14" font-family="sans-serif" fill="#222">%s · %d 席 · %d 圈</text>'
      % (pad, cfg["title"], total, meta["rows"]))
    a('<g transform="translate(%d,%d)">' % (pad, pad))
    idx = 0
    for i, p in enumerate(parties):
        col = frame_color[party_frame(p, i)]
        for k in range(p["seats"]):
            if idx >= len(coords):
                break
            x, y = coords[idx]
            a('<circle cx="%d" cy="%d" r="%.1f" fill="%s" stroke="#ffffff" stroke-width="0.6"/>'
              % (x, y, r, col))
            idx += 1
    a('</g>')
    ly = max(ys) + pad + 34
    for i, p in enumerate(parties):
        col = frame_color[party_frame(p, i)]
        a('<rect x="%d" y="%d" width="12" height="12" fill="%s"/>' % (pad, ly - 11, col))
        a('<text x="%d" y="%d" font-size="12" font-family="sans-serif" fill="#333">%s  %d 席  (frame %d)</text>'
          % (pad + 18, ly, p["name"], p["seats"], party_frame(p, i)))
        ly += 20
    a('</svg>')
    return '\n'.join(L) + '\n'


def gen_preview_html(cfg, svg, meta):
    rows = []
    for i, p in enumerate(cfg["parties"]):
        rows.append('<tr><td><span class="sw" style="background:%s"></span></td>'
                    '<td>%s</td><td>%s</td><td class="n">%d</td><td class="n">%d</td></tr>'
                    % (p.get("color", "#888"), p["id"], p["name"], p["seats"], party_frame(p, i)))
    params = {
        "总席位": cfg["total_seats"], "圈数": meta["rows"],
        "spread": meta["spread"], "first_row_radius": meta["first_row_radius"],
        "radius_rows": meta["radius_rows"], "icon_size": meta["icon_size"],
        "x 范围": "%d .. %d" % (meta["x_min"], meta["x_max"]),
        "y 范围": "%d .. %d" % (meta["y_min"], meta["y_max"]),
        "画布": "%s × %s" % (meta["out_width"], meta["out_height"]),
    }
    pl = ''.join('<li><b>%s</b>：%s</li>' % (k, v) for k, v in params.items())
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<title>%s · 议会席位分布</title>'
            '<style>body{font-family:"Microsoft YaHei",sans-serif;margin:28px;color:#222;background:#fafafa}'
            'h1{font-size:20px} .wrap{display:flex;gap:28px;flex-wrap:wrap}'
            '.card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:16px}'
            'table{border-collapse:collapse;font-size:13px}td,th{padding:5px 12px;border-bottom:1px solid #eee}'
            '.n{text-align:right} .sw{display:inline-block;width:12px;height:12px;border-radius:2px}'
            'ul{font-size:13px;line-height:1.7;padding-left:20px} svg{max-width:100%%}</style></head><body>'
            '<h1>%s · 议会席位分布预览</h1>'
            '<div class="wrap"><div class="card">%s</div>'
            '<div class="card"><table><tr><th></th><th>id</th><th>党团</th><th>席位</th><th>frame</th></tr>%s</table>'
            '<h3>生成参数</h3><ul>%s</ul></div></div>'
            '<p style="font-size:12px;color:#666">本页由 dev_skill/parliament_diagram/parliament_generator.py 自动生成；'
            '坐标与 HOI4 代码产物完全一致。</p></body></html>'
            % (cfg["title"], cfg["title"], svg, ''.join(rows), pl))


# ---------------------------------------------------------------------------
# 4. 校验
# ---------------------------------------------------------------------------
def validate(cfg, coords, meta):
    problems = []
    total = cfg["total_seats"]
    if len(coords) != total:
        problems.append("坐标数 %d != 总席位 %d" % (len(coords), total))
    if sum(p["seats"] for p in cfg["parties"]) != total:
        problems.append("党团席位合计 %d != 总席位 %d"
                        % (sum(p["seats"] for p in cfg["parties"]), total))
    frames = [party_frame(p, i) for i, p in enumerate(cfg["parties"])]
    if len(set(frames)) != len(frames):
        problems.append("frame 编号重复：%s" % frames)
    if cfg_get(cfg, "seat_source") == "variables":
        for p in cfg["parties"]:
            if not p.get("var"):
                problems.append("variables 模式下 %s 缺 var 字段" % p["id"])
    if meta["x_max"] + cfg["gui"]["grid_x"] > cfg["gui"]["width"]:
        problems.append("座位 x 上界 %d 超出 GUI 容器宽度 %d"
                        % (meta["x_max"] + cfg["gui"]["grid_x"], cfg["gui"]["width"]))
    if meta["y_max"] + cfg["gui"]["grid_y"] > cfg["gui"]["height"]:
        problems.append("座位 y 上界 %d 超出 GUI 容器高度 %d"
                        % (meta["y_max"] + cfg["gui"]["grid_y"], cfg["gui"]["height"]))
    return problems


# ---------------------------------------------------------------------------
# 5. 主流程
# ---------------------------------------------------------------------------
def build(cfg, check_only=False):
    for k in DEFAULTS:
        if k not in cfg:
            cfg[k] = DEFAULTS[k]
    coords, meta = seat_positions(
        cfg["total_seats"], spread=cfg["spread"],
        first_row_radius=cfg["first_row_radius"],
        ordering_factor=cfg["ordering_factor"],
        radius_rows=cfg["radius_rows"], icon_size=cfg["icon_size"])

    problems = validate(cfg, coords, meta)
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        if not check_only:
            sys.exit(2)
    else:
        print("VALIDATION OK  total=%d rows=%d coords=%d  x=%d..%d y=%d..%d"
              % (cfg["total_seats"], meta["rows"], len(coords),
                 meta["x_min"], meta["x_max"], meta["y_min"], meta["y_max"]))
    if check_only:
        return meta

    files = {
        "01_seat_positions.txt": ("txt", gen_positions(cfg, coords, meta)),
        "02_seat_frames.txt": ("txt", gen_frames(cfg, meta)),
        "03_scripted_gui.txt": ("txt", gen_scripted_gui(cfg)),
        "04_gui.txt": ("txt", gen_gui(cfg)),
        "05_gfx.txt": ("txt", gen_gfx(cfg)),
        "06_scripted_localisation.txt": ("txt", gen_scripted_loc(cfg)),
        "07_localisation.yml": ("yml", gen_localisation(cfg)),
        "08_integration.txt": ("txt", gen_integration(cfg)),
    }
    svg = gen_preview_svg(cfg, coords, meta)
    files["preview.svg"] = ("raw", svg)
    files["preview.html"] = ("raw", gen_preview_html(cfg, svg, meta))

    idx = 0
    plist = []
    for i, p in enumerate(cfg["parties"]):
        plist.append({
            "id": p["id"], "name": p["name"], "seats": p["seats"],
            "frame": party_frame(p, i),
            "first_seat_index": idx, "last_seat_index": idx + p["seats"] - 1,
            "color": p.get("color"),
            "var": party_source(cfg, p, i),
        })
        idx += p["seats"]
    manifest = dict(meta)
    manifest.update({
        "title": cfg["title"], "tag": cfg["tag"],
        "arrays": cfg["arrays"], "effects": cfg["effects"],
        "parties": plist, "validation": problems,
        "coord_count": len(coords), "frame_total": idx,
        "passed": not problems and len(coords) == idx == cfg["total_seats"],
    })
    files["manifest.json"] = ("raw", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    out = cfg.get("out_dir") or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             "examples", cfg.get("example_name", "output"))
    os.makedirs(out, exist_ok=True)
    for name, (kind, content) in files.items():
        if kind == "txt":
            data = crlf(content).encode("utf-8")
        elif kind == "yml":
            data = b"\xef\xbb\xbf" + crlf(content).encode("utf-8")
        else:
            data = content.encode("utf-8")
        with open(os.path.join(out, name), "wb") as f:
            f.write(data)
    print("OUTPUT -> %s  (%d files)" % (out, len(files)))
    for i, p in enumerate(plist):
        print("  frame %-2d  %-24s %3d 席  index %3d..%3d"
              % (p["frame"], p["name"], p["seats"],
                 p["first_seat_index"], p["last_seat_index"]))
    return manifest


def self_test():
    print("ROW_TOTALS entries:", len(ROW_TOTALS), "max:", ROW_TOTALS[-1])
    ok = True
    for total in [10, 21, 60, 104, 300, 450, 600, 1000]:
        try:
            coords, meta = seat_positions(total)
            good = len(coords) == total and meta["x_min"] >= 0 and meta["y_min"] >= 0
            ok &= good
            print("  total=%-5d rows=%-3d coords=%-5d x=%d..%d y=%d..%d %s"
                  % (total, meta["rows"], len(coords), meta["x_min"], meta["x_max"],
                     meta["y_min"], meta["y_max"], "OK" if good else "FAIL"))
        except Exception as e:
            ok = False
            print("  total=%d EXCEPTION %s" % (total, e))
    # auto 行数模式
    coords, meta = seat_positions(104, radius_rows="auto")
    print("  radius_rows=auto rows=%s coords=%d y=%d..%d" %
          (meta["rows"], len(coords), meta["y_min"], meta["y_max"]))
    print("SELF TEST:", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="HOI4 半圆议会席位图 headless 生成器")
    ap.add_argument("--config", help="JSON 配置路径")
    ap.add_argument("--out", help="覆盖配置里的 out_dir")
    ap.add_argument("--check-only", action="store_true", help="只校验不写文件")
    ap.add_argument("--self-test", action="store_true", help="跑算法自检")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.config:
        ap.print_help()
        return 1
    with open(args.config, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    if args.out:
        cfg["out_dir"] = args.out
    build(cfg, check_only=args.check_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
