# 议会席位图（半圆 / 矩形）自动化 Skill

> 建立日期：2026-11-11　|　适用：Across-Limbo / 守望莱茵（HOI4 `1.18.*`）
> 工具来源：`C:/Users/edwar/Documents/GitHub/hoi4-parliament-diagram-fork`（Flaxbeard 原版 + fedacking fork）
> 本仓内工具：`dev_skill/parliament_diagram/parliament_generator.py`
> 已验证实例：`dev_skill/parliament_diagram/examples/MAL_leg_104/`（星洲联邦立法院 104 席）

---

## 0. 给后续 AI 的执行契约（最高优先级）

> ⚠️ **MAL 实例特例（第十四轮，2026-11-12）**：星洲立法院已按用户指令改为 **13 列 × 8 行等距矩形**，不再是半圆。**禁止**对 MAL 重跑半圆生成器覆盖坐标，详见 §11。下面 5 步只适用于「新做半圆议会」的国家。

**只要用户说「给 X 国做议会 / 议会席位图 / 半圆议席 / parliament diagram」，直接执行下列 5 步，不要再问「要不要自己处理坐标」、不要重写算法、不要手工排圆点：**

1. 确认总席位数与院内单位清单（**单位必须是政党党团，不是族群配额**；空缺议席单列一个单位）。
2. 复制 `examples/MAL_leg_104/config.json` 改成新配置（改 `tag / prefix / total_seats / parties / gui 名称 / loc`）。
3. 跑 `python dev_skill/parliament_diagram/parliament_generator.py --config <新配置>`。
4. 按本文件 §5 把 8 个产物片段落位，按 §6 对齐本仓编码与命名规范，按 §9 跑校验。
5. 把 `preview.html` 交用户看一眼分布，再报告「总席位 / 圈数 / 坐标范围 / 各党团 frame 段」。

**两个机构性质不能混**（2026-11-11 用户裁定）：

| 机构 | 性质 | 席位单位 |
|---|---|---|
| 中央执行委员会 | **党内机构** | 党内派系 |
| 联邦立法院 / 立法会 | **国家机构** | 政党党团 |

议会 GUI 只表现**国家机构**那一层。党内派系的力量对比可以通过变量**单向派生**到议会党团忠诚度，但议会不应回灌党内席位。

---

## 1. 原版工具到底做了什么

`hoi4-parliament-diagram-fork/ParliamentGUIGenerator.py` 是一个 tkinter + Pillow 的窗口程序，滑块调 `Total Delegates / Spread / First Row Radius / Ordering Adjustment Factor`，预览半圆点阵，点「Generate Output」后把 **4 段代码**写进 `parliament_gui_code.txt`：

| 模板常量 | 产出内容 | 落位 |
|---|---|---|
| `GUI_FILE` | 单个座位的 `containerWindowType`（内含 `iconType`，`quadTextureSprite = 座位精灵图`） | `.gui` 顶层容器 |
| `GUI_FILE_2` | `gridboxtype` 议会容器（带 `# Spread / First Row Radius / Total Delegates` 注释，便于日后重生成） | `.gui` 主窗口 |
| `SCRIPTED_GUI` | `dynamic_lists`（按 x 数组复制座位容器）+ `properties`（x/y/frame 三个数组） | `common/scripted_guis/` |
| `SCRIPTED_EFFECTS` | 一大串 `add_to_array = { X = ... }` / `Y = ...`，把每个座位坐标灌进数组 | `history/` 或 `common/scripted_effects/` |

`parliament_sample/` 是配套可运行范例，额外演示了两件原版工具**不生成**、但必须自己写的东西：

- `SAMPLE_init_parliament` 用 `resize_array` 按党团累计席位填 `SAMPLE_seat_frame`（**颜色数组**）；
- `SAMPLE_seat_party` 这个 `defined_text` 按 `seat_frame^seat_idx` 决定每个圆点的 tooltip 党团名。

**结论：议席图 = 3 个等长数组（x / y / frame）+ 1 个 dynamic_list + 1 个多帧精灵图。** 原版只给 x/y，frame 和接线要补；本 Skill 的生成器把这部分也自动化了。

---

## 2. 算法原理与 5 个必知坑

### 2.1 坐标算法（严格复刻，勿改）

```
ROW_TOTALS[i]            第 i+1 圈累计容量表（4, 15, 33, 61, 95, 138, ... 31061）
rows                     最小满足 ROW_TOTALS[rows-1] >= total_seats 的行数
J_i = int( total / ROW_TOTALS[rows-1] * π / (2·asin(2/(3·rows + 4·i - 2))) )   内部第 i 圈席位数
R_i = (3·hole + spread·i - 2) / (4·N)                                          第 i 圈半径
angle_j = j·(π - 2·sin(radius/R_i))/(J-1) + sin(radius/R_i)                    座位在弧上的角度
x = R·cos(angle) ; y = R·sin(angle)
poslist.sort(reverse=True, key=angle±oaf·R)                                      决定「从左到右」填色顺序
输出 x = round(raw_x·100 + out_width/2 - icon_size/2)
输出 y = round(out_height - raw_y·100 - icon_size/2)
其中 out_width = max(raw_x)-min(raw_x)+icon_size ; out_height = max(raw_y)-min(raw_y)+icon_size+10
```

`radius = 0.1`，`hole = first_row_radius`（默认 5.7），`spread` 默认 1.85。

### 2.2 五个坑（都已在生成器里处理）

| # | 坑 | 后果 | 本 Skill 的处理 |
|---|---|---|---|
| 1 | 原版最外圈 `J == 1` 时 `append` 的是**三元组** `[angle, x, y]`，而排序 key 会取 `p[3]` | `oaf != 0` 时 `IndexError`；即使 `oaf=0`，Python 也会求值 `oaf*p[3]` | 统一补成四元组 `[angle, x, y, R]` |
| 2 | 半径公式注释写 `(4·N)`，代码却写死 `(4.0*4)` | 大议会半径偏小、图形压扁 | 默认保留 4 与原版一致；提供 `radius_rows = "auto"` 用真实行数 |
| 3 | `circle_image_rad = self.width` 取自预览图 `small_circle.png`（实测 **9×9**） | 换图后坐标整体偏移、圆点错位 | 显式参数 `icon_size`，默认 9 |
| 4 | 原版**不生成 frame 数组** | 全部圆点是同一颜色，看不出党团 | 按席位表自动生成 `resize_array` 分段；最后一段强制拉到总席位变量 |
| 5 | 坐标 spam 有 2×N 行，每次刷新都重建极慢 | 卡顿 / 存档膨胀 | 坐标只在**首次打开**时生成一次（`initialized_flag`），之后只重算 frame |

补充：`total_seats` 上限受 `ROW_TOTALS` 表约束（31061），下限 10；`oaf` 只在需要「同党团座位聚拢」时调，默认 0 即可。

---

## 3. 配置 schema（`config.json`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `title` / `tag` / `example_name` | str | 预览标题、国家 tag、输出子目录名 |
| `total_seats` | int | **总席位**，必须等于 `parties[].seats` 之和 |
| `spread` / `first_row_radius` / `ordering_factor` | float | 默认 1.85 / 5.7 / 0.0 |
| `radius_rows` | int 或 `"auto"` | 默认 4（复刻原版）；`auto` 更匀称 |
| `icon_size` | int | 默认 9；换精灵图时改成实际帧宽 |
| `seat_source` | `"variables"` / `"static"` | `variables` 读运行时席位变量（推荐，席位变化可刷新）；`static` 用配置里的常量 |
| `total_seats_var` | str | 总席位变量，默认 `<prefix>_total_seats`；用于最后一段强制对齐 |
| `arrays` | `{x, y, frame}` | 三个数组名 |
| `effects` | `{init_positions, reload_frames, init_all}` | 三个脚本效果名 |
| `scripted_gui` / `sploc` | str | scripted_gui 名 / `defined_text` 名 |
| `open_flag` / `initialized_flag` | str | 窗口开关旗标 / 坐标已生成旗标（**两者都要有 reader**） |
| `decision_category` / `decisions` / `icons` | str / obj | 接线片段用的分类名、决议名、图标 |
| `gui` | obj | `window_name / diagram_grid / seat_container / seat_icon / seat_sprite / background_sprite / width / height / grid_x / grid_y` |
| `textures` | `{background, seat}` | 两张 dds 的模组内路径 |
| `loc` | obj | `seat_tooltip / close_tooltip / refresh_tooltip / extra{key: 文本}` |
| `parties[]` | array | 每项 `{id, name, seats, frame, var, loc, color}`；`frame` 从 1 连续编号，`color` 只用于预览 |

**党团顺序 = 圆点从左到右的填色顺序**，把执政党放最前、空缺放最后。

---

## 4. 一键用法与产物清单

```bash
cd C:/Users/edwar/Documents/GitHub/Across-Limbo/dev_skill/parliament_diagram
python parliament_generator.py --self-test                              # 算法自检
python parliament_generator.py --config examples/MAL_leg_104/config.json  # 一键产出
python parliament_generator.py --config xxx.json --check-only             # 只校验不写
```

| 产物 | 内容 | 对应落位 |
|---|---|---|
| `01_seat_positions.txt` | `add_to_array` 坐标 spam（2×N 行） | `common/scripted_effects/` |
| `02_seat_frames.txt` | `resize_array` 分党团 frame + 初始化组合效果 | `common/scripted_effects/` |
| `03_scripted_gui.txt` | `scripted_gui`（dynamic_lists + properties + 按钮 effect） | `common/scripted_guis/` |
| `04_gui.txt` | 两个 `containerWindowType`（主窗口 + 座位容器） | `interface/*.gui` |
| `05_gfx.txt` | 背景 + 座位精灵图 `spriteType` | `interface/*.gfx` |
| `06_scripted_localisation.txt` | `defined_text` 按 frame 显示党团名 | `common/scripted_localisation/` |
| `07_localisation.yml` | 党团名 / tooltip / 决议名（**已带单 BOM + CRLF**） | `localisation/simp_chinese/` |
| `08_integration.txt` | 接线片段：开关决议、刷新时机、贴图落位 | 按注释合并，**不可整份直接加载** |
| `manifest.json` | 坐标范围、每党团 frame 段与 index 区间、校验结论 | 留档 / 回归对比 |
| `preview.svg` / `preview.html` | 半圆分布可视化 + 图例 + 参数 | 给用户看 / 汇报 |

`.txt` 产物自动写成 **无 BOM + CRLF**，`.yml` 写成 **单 BOM + CRLF**，符合本仓 §1 编码铁律。

---

## 5. 落位步骤（8 步，按顺序）

1. **贴图**：从 fork 的 `parliament_sample/gfx/interface/parliament_sample/` 复制背景 dds；座位 dds 必须是**横向 N 帧精灵图**（N = 党团数，MAL 为 8；fork 自带的是 4 帧，不能直接复用；本仓已自制 8 帧放在 `gfx/interface/TNW_MAL/parliament_seat.dds`）。每帧一种党团颜色，`noOfFrames` 与 `frame` 最大值一致。
2. **gfx / gui**：把 `05_gfx.txt`、`04_gui.txt` 的块并进目标文件已有的 `spriteTypes = { }` / `guiTypes = { }` 内，**不要新建重复的顶层包裹**。`.gui` 里的 `100%%` 是 HOI4 语法，不要改成 `100%`。
3. **scripted_gui**：`03_scripted_gui.txt` 可整份放进 `common/scripted_guis/`。`window_name` 必须与 `.gui` 主窗口 `name` 一致；`entry_container` 必须与座位容器 `name` 一致；`index = seat_idx` 不要改。
4. **scripted_effects**：`01` + `02` 合并进一个 `.txt`。`01` 是常量坐标，`02` 读变量，职责分开。
5. **scripted_localisation**：`06` 整份可用；`localization_key` 指向 `07` 里的党团名。
6. **本地化**：`07` 的键并入对应国家 yml（注意本仓 yml 是**单 BOM + CRLF**、键前 1 空格、`l_simp_chinese:` 后必须是真实 `0d 0a`）。
7. **决议接线**：把 `08_integration.txt` 的 A 段**并进已有分类块**，不要新建分类、不要在 `categories/` 写 `decision =`、不要在决议里写 `category =`。`visible = { has_completed_focus = ... }` 才是真解锁，`unlock_decision_tooltip` 只是文字。
8. **刷新时机**：在算分脚本末尾或 `on_monthly_<TAG>` 调一次 `reload_frames`；**不要**每月重建坐标数组。`on_startup` 作用域为 none，若要开局初始化须用 `every_country = { if = { limit = { tag = X } ... } }`；更省事的是用 `08` 的「首次打开时生成」方案。

---

## 6. 与本仓规范的对接（违反会静默失效）

| 规范 | 要求 |
|---|---|
| 文件编码 | `common/**` 与 `interface/*.gfx/.gui`：无 BOM + 纯 CRLF；`history/countries/*`、`localisation/**`：单 BOM + 纯 CRLF。禁止双 BOM、禁止字面 `\r\n`（`2f 72 2f 6e`） |
| 命名 | 一律 `TNW_` 或 `<TAG>_` 前缀；数组名 / 效果名 / flag 名不要与原版 `SAMPLE_*` 撞车 |
| 决议分类 | 分类单独定义在 `common/decisions/categories/`，顶层块名即 id；`common/decisions/*.txt` 打开同名块嵌决议。分类不列 `decision =`，决议不写 `category =` |
| flag | `set_country_flag` 必须有 `has_country_flag` reader，否则是死代码。生成器的 `open_flag` / `initialized_flag` 都自带 reader |
| 图标 | 本仓未替换 `interface/`，原版通用 `GFX_goal_*` / `GFX_decision_generic_*` 可用；`GFX_MAL_*` 这类自定义 sprite 本仓零定义，别用 |
| 变量插值 | 分类 `_desc` 用 `[?TAG.var|0]` / `[?global.var|0]` / `[?THIS.var]`；`[?x|.0]` 非法 |
| 校验 | 改完跑字节级复核：BOM、CRLF 数 = LF 数、花括号配平、无 `{{`、yml 引号成对、key 不重复 |

---

## 7. 已验证实例：星洲联邦立法院 104 席

`examples/MAL_leg_104/`，生成参数 `spread=1.85 / hole=5.7 / oaf=0 / radius_rows=4 / icon_size=9`，结果 **6 圈、104 个坐标、x 0..327、y 5..158**（容器 450×250、gridbox 偏移 28/52，未溢出）。

| frame | 党团 | 席位 | seat index 区间 | 变量 |
|---:|---|---:|---|---|
| 1 | 星洲国民党 | 42 | 0..41 | `MAL_leg_kmt_seats` |
| 2 | 星洲国民党-左翼党团（南洋民主劳动党） | 14 | 42..55 | `MAL_leg_kmt_left_seats` |
| 3 | 马来人协会 | 12 | 56..67 | `MAL_leg_mu_seats` |
| 4 | 穆斯林人民党 | 9 | 68..76 | `MAL_leg_mpp_seats` |
| 5 | 马来印度人国大党 | 9 | 77..85 | `MAL_leg_mic_seats` |
| 6 | 泛马工会联合会 | 7 | 86..92 | `MAL_leg_pmftu_seats` |
| 7 | 中国共产党-南洋委员会 | 5 | 93..97 | `MAL_leg_cpc_seats` |
| 8 | 空缺议席 | 6 | 98..103 | `MAL_leg_vacant_seats` |

合计 104，在籍 98，法定人数 53。国民党两个党团**分别作为整体投票**。

**与现有变量层的对接**：`MAL_leg_<g>_seats / _loyalty / _seat_change / _whip` 已由 `common/scripted_effects/TNW_MAL_scripted_effects.txt` 的 `MAL_leg_calc_effect` 维护；议会只做表现层。两党团 `_loyalty` 是**党内力量对比的覆盖式派生**（主席阵营 ≥11 席 → 两团 100；隆市派 str ≥50 → 左翼团 0），玩家只能改 `_whip`。生成器读的是 `_seats`，与之完全兼容。

> ✅ **2026-11-11 第五轮已正式接进游戏运行时**：MAL 立法院按 BUL 范式挂在分类标签页（`MAL_legislative_council` 写 `scripted_gui = TNW_MAL_parliament_gui`，`context_type = decision_category`）。运行时文件见 `common/scripted_guis/TNW_MAL_scripted_guis.txt`、`interface/gui/TNW_MAL_National_Congress.gui/.gfx`、`common/scripted_effects/TNW_MAL_parliament_effects.txt`、`gfx/interface/TNW_MAL/parliament_seat.dds`（自制 8 帧）。`examples/MAL_leg_104/03_scripted_gui.txt` 是 `player_context` 独立浮窗版，**接入分类时不要整份照抄**。

---

## 8. 校验清单

**机器校验（生成器内置）**

- `len(coords) == total_seats`；
- `sum(parties[].seats) == total_seats`；
- `frame` 编号不重复；
- `variables` 模式下每个党团都有 `var`；
- 座位 `x_max + grid_x <= gui.width`、`y_max + grid_y <= gui.height`（防圆点被容器裁掉）；
- `manifest.json` 里 `coord_count == frame_total == total_seats` 且 `passed: true`。

**落位后人工复核**

1. 三个数组长度在游戏内一致（104 / 104 / 104）；`dynamic_lists` 的 `array` 指向 x 数组。
2. `frame` 数组首 42 个是 1、末 6 个是 8 —— 用 `preview.svg` 的图例肉眼比对。
3. 所有 `set_country_flag` 都能被 `has_country_flag` 读到（含 `open_flag` / `initialized_flag`）。
4. `noOfFrames` = 最大 frame 编号；贴图每帧颜色与预览配色一致。
5. 字节级：BOM/CRLF/括号/yml 引号/key 唯一。
6. 改席位数后**必须重跑生成器**并重贴 `01_seat_positions.txt`；只改党团席位而总席位不变，则只需重算 `02` 的 frame，坐标不用动。

---

## 9. 常见故障速查

| 现象 | 原因 | 修法 |
|---|---|---|
| 圆点全挤在左上角 / 只显示 1 个 | `dynamic_lists.array` 指错，或坐标数组没生成 | 检查 `open_flag` 与 `initialized_flag` 的 reader，确认首次打开决议被点过 |
| 全部圆点同色 | `frame` 数组没填 / `noOfFrames = 1` | 跑 `reload_frames`；把 `noOfFrames` 改成党团数 |
| 圆点数量少于席位数 | `resize_array` 最后一段没拉到总席位 | 生成器最后一段用 `total_seats_var`，别改成 `vacant_seats` |
| 圆点被窗口裁掉 | 容器太小或 `grid_x/grid_y` 偏移过大 | 看 `manifest.json` 的 `x_max/y_max`，放大 `gui.width/height` |
| 坐标整体偏移半个圆点 | `icon_size` 与实际精灵图帧宽不符 | 把 `icon_size` 改成真实帧宽再重跑 |
| 游戏里 yml 整段不加载 | 双 BOM / 裸 LF / 字面 `\r\n` | 按本仓 §1 修复，注意会连带中止同语言后续 yml |
| 决议点不开 | 只写了 `unlock_decision_tooltip` | 在目标决议 `visible` 里写 `has_completed_focus = <id>` |

---

## 10. 复用到别国的最小改动清单

1. 新配置里的 `tag / example_name / prefix / arrays / effects / scripted_gui / sploc / flags / decision_category / gui.* / textures / loc.*`。
2. `parties[]` 换成该国的政党党团（**先查该国既有政党本地化键**，避免同一势力两个名字）。
3. 若该国已有议会变量层，把 `parties[].var` 指过去；没有就先按 `TNW_MAL_scripted_effects.txt` 的范式建一套 `_seats / _loyalty / _seat_change`。
4. 贴图换成对应帧数与配色。
5. 跑 `--check-only` → 正式生成 → 落位 → §8 校验 → 交 `preview.html`。


---

## 11. MAL 立法院矩形特例（第十四轮，2026-11-12）

用户指令：「立法院从半圆改成长 13 宽 8 的矩阵，每两个点之间的横向纵向距离都相等」。
13 × 8 = 104，正好等于立法院总席位，无需增减圆点，只换坐标。

| 项 | 值 |
|---|---|
| 布局 | 13 列 × 8 行，`index i -> 行 i//13、列 i%13`，按行填充 |
| 横 / 纵间距 | 同为 **20 px**（用户要求「横向纵向距离都相等」） |
| 坐标范围 | x 0..240　y 0..140（圆点 9×9 → 占位 249×149） |
| 容器 / gridbox | 450×250 / `position = { x = 100 y = 50 }`（矩形居中） |
| 总点数 | 104；`frame` 数组仍按 42/14/12/9/9/7/5/6 分段，顺序不变 |

运行时文件：`common/scripted_effects/TNW_MAL_parliament_effects.txt`
（`MAL_leg_init_seat_positions_effect`）、`interface/gui/TNW_MAL_National_Congress.gui`。
留档文件：`examples/MAL_leg_104/01_seat_positions.txt`、`manifest.json`（含
`layout = rect_grid` / `cols` / `spacing_x` / `spacing_y`）、`preview.svg`、`preview.html`。

**硬规则**

1. **不要**对 MAL 跑 `parliament_generator.py`——它是半圆算法，会覆盖矩形坐标。
2. 只有「改总席位数」或「改矩阵形状」才需要重算坐标；只改党团席位而总数不变，
   只需重算 `MAL_leg_reload_seat_frames_effect` 的 frame 分段，坐标不动。
3. 校验口径：104 组 x/y、13 列 × 8 行、横纵间距相等、`x_max + grid_x <= 450`、
   `y_max + grid_y <= 250`，已写入 `_mal_verify.py` 第 21 节。
4. 半圆算法（§2）与本仓其余国家仍然有效，本特例只约束 MAL。

> §7 的「6 圈 / x 0..327 / y 5..158」是 2026-11-11 第五轮的历史产物，
> **不代表当前运行时状态**；现状以本节与运行时文件为准。
