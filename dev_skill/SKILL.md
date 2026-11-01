---
name: across-limbo-mod-dev
description: HOI4 Across-Limbo（TNO 框架，前缀 TNW_）模组开发铁律与常见 bug 速查。当用户要新增/修改角色(characters)、历史文件(history/countries)、意识形态、国策、事件、决议、开战方式或脚本和平，或排查"角色不显示 / 政治系统崩坏 / 战争不触发 / 脚本和平成死代码"等模组问题时使用。融合仓库内 AGENTS.md(=skill.pdf，《钢铁雄心 IV Mod 开发完整代码规则书》)的语法权威 + 本项目历次踩坑蒸馏出的铁律。
---

# Across-Limbo 模组开发 Skill

## 0. 权威参考（本仓库内）
- `AGENTS.md` 与 `skill.pdf` 内容相同：**《钢铁雄心 IV — Mod 开发完整代码规则书》**（HOI4 官方 Wiki 整理的语法总表：效果 / 触发 / 作用域 / 修正 / Defines / 事件钩子 / 本地化 / 数据结构，879 个章节头）。
  - 写任何 HOI4 脚本（效果、触发器、作用域、修正、N-* 函数）**先查它**，不要凭记忆写。文件很大（2.2MB），用 `grep -nE "^#{1,6} 关键词" AGENTS.md` 定位章节。
- 项目记忆 `.workbuddy/memory/` 记录本模组分支、开发目标 tag、文件格式铁律、意识形态两层规则与历次踩坑，跨会话持久。

## 1. 文件格式与编码铁律（违反会静默不加载，且无报错）
| 路径 | BOM | 换行 | 缩进 |
|---|---|---|---|
| `common/*`（characters / ideologies / decisions / scripted_effects / on_actions / bookmarks…） | **无** | **CRLF** | tab |
| `history/*`（countries / bookmarks…） | **有(BOM)** | **CRLF** | tab |
| `localisation/**` | **有(BOM)** | **CRLF** | 键前 1 空格，值用 `"` |

- 强制规则：花括号配平；本地化引号奇偶配对；**禁止双花括号** `{{` / `}}`。
- 用脚本写文件：读字节 → 按 `\r\n` 处理 → 按上表重新编码（common 用 `utf-8`，history/localisation 用 `utf-8-sig`）。**不要**在 Python 里手写含 `\n` 的字符串拼接，否则混入裸 LF 破坏 CRLF。
- 验证工具：`scripts/` 下的 `assert_clean` 系列脚本对编码/括号/引号做断言。

## 2. 意识形态两层规则（本模组反复翻车的根因）
- **角色文件** `common/characters/TNW_*.txt` 里 `country_leader = { ideology = <X> }` **必须用子意识形态（sub-ideology），绝不能用父桶**：
  - 合法子项（定义在 `common/ideologies/00_ideologies.txt` 顶层 9 组的下层）：
    - `communist` 下：`Marxism` / `Marxism_Leninism` / `Japanese_Marxism` / `Fukumotoism` / `Committee_Communism` / `Left_wing_communism`
    - `syndicalism` 下：`Centralised_Syndicalism` / `Classical_Syndicalism` / `Anarchist_Syndicalism` / `National_Syndicalism` / `Parallel_Syndicalism` / `American_Unionism` / `Japanese_Syndicalism`
    - `socialism` 下：`agrarian_socialism` / `Anarchist_Communism` / `Liberalism_socialism` / `market_socialism` / `religious_socialism` / `Socialism_Britain` / `Production_Supremacism` / `tridemism_revolutionary` / `triequism_left` / `socialist_nationalism` / `military_socialism`
    - `Social_democracy` 下：`Popular_Front` / `Left_wing_populism` / `Left_wing_nationalism` / `progressivism` / `Social_democratic` / `reformism` / `Bernsteinism` / `tridemism_left` / `triequism_center`
    - `Liberalism` 下：`National_liberalism` / `Market_liberalism` / `Social_Liberalism` / `Authoritarian_Liberalism` / `Liberal_Zionism` / `tridemism_liberal` / `triequism_right`
    - `Conservatism` 下：`Social_Conservatism` / `National_Conservatism` / `Patriarchal_Conservatism` / `Zionism` / `tridemism_conservative`
    - `Authoritarianism` 下：`Guided_democracy` / `oligarchy` / `transitional_democracy` / `discipline` / `interim_government` / `one_party_democracy` / `Left_wing_corporatism` / `Social_nationalism` / `tridemism_authdem`
    - `Absolutism` 下：`Tibet_theocracy` / `Junshen_government` / `absolute_monarchy` / `military_government` / `colonial_government` / `warlord` / `civilian_dictatorship` / `theocracy` / `Red_military_government`
    - `Nationalism` 下：`nationalism`（本项目新增）/ `Fascism` / `National_Socialism` / `Strassianism` / `Ultra_Nationalism` / `Renewal_System`（及其余）
  - ⚠️ 常见错误：`ideology = socialism` / `Liberalism` / `Social_democracy` / `Authoritarianism` / `Nationalism`（这些是**父桶**，填了领袖不显示）。
  - ⚠️ 禁止 `types = {}` 块——它会删掉必需字段；用扁平 `ideology = <子项>`。
  - `recruit_character` 只需列出角色文件里真实定义的领袖，与意识形态填法无关；领袖不出现多半是 `ruling_party` 错填子项，或角色文件 `ideology` 格式错。
- **历史文件** `history/countries/*.txt` 里 `ruling_party = <X>` 与 `set_popularities = { ... }` 的键**必须用 9 个父桶之一**：
  `communist / syndicalism / socialism / Social_democracy / Liberalism / Conservatism / Authoritarianism / Absolutism / Nationalism`
  - `set_popularities` 必须 **9 桶、和=100**，且主导桶 = `ruling_party` 所用的父桶。否则系统 fallback 到全共产主义饼图、政治系统崩坏，所有领袖回退通用。
  - ⚠️ 常见错误：`ruling_party = military_government`（子意识形态，非法）→ 应填其所属父桶（`military_government ∈ Absolutism` → 填 `Absolutism`），并把 popularities 里的 `military_government = 65` 改成 `Absolutism = 65`（同时删掉原先重复的 `Absolutism = 0` 行）。
- **子→父映射速查**：`oligarchy`/`discipline`→Authoritarianism；`absolute_monarchy`/`colonial_government`/`military_government`→Absolutism；`Social_democratic`/`progressivism`→Social_democracy；`Social_Liberalism`→Liberalism；`Social_Conservatism`→Conservatism；`Marxism`→communist；`market_socialism`/`agrarian_socialism`→socialism；`nationalism`/`Fascism`→Nationalism。

## 3. 角色"不显示"排查清单（按概率排序）
1. 历史 `ruling_party` 错填子意识形态 → 全体回退通用。**先查这个。**
2. 角色文件 `ideology` 填成父桶 → 该领袖不显示。
3. 历史文件没有 `recruit_character = <name>`（**单行**，不是块）→ 领袖不被招募。
4. `set_popularities` 不是完整 9 桶，或含非父桶键 → 政治系统崩坏。
5. 历史文件末尾有**悬空 `}`**（无对应开括号）→ 整个文件无法解析（ARG、ECU 都踩过，删掉即可）。
6. `recruit_character` 引用的名字在 `common/characters/` 里根本没定义 → 悬空引用（无害但日志报错）；要么补定义要么删引用。
7. CRLF 被破坏（混入裸 LF）或 BOM 错位 → 文件静默不加载。

## 4. 战争与脚本和平（本项目踩坑记录）
- **开战方式**：`declare_war_on = X` 立即宣战；`add_to_war = { target = X war = N }` 需要前置 `create_wargoal = N`，否则战争目标不存在、宣战无效、战争永不触发（澳大利亚内战最初就是这么坏的，已改为在 `on_startup` 事件里 `declare_war_on = AFF`）。
- **脚本和平**：`on_capitulation` on_action 处理战败/战胜国。**`if` / `else_if` 必须同级兄弟**（同缩进），嵌套会让被嵌套块永不求值。澳大利亚 `else_if` 曾被嵌套进叙利亚块，导致 `white_peace` + 清 `AST_civil_war_active` 成死代码；修复=在被嵌套块末尾补 `}` 使其闭合、令其升为同级兄弟。
- 通用吞并块排在特定国家专属 `white_peace` 块之前是本模组通用约定（非 bug），不要"修复"它的顺序。

## 5. 字节级验证（改完必跑，杜绝"看起来对"）
```python
import re
PARENTS={'communist','syndicalism','socialism','Social_democracy','Liberalism',
         'Conservatism','Authoritarianism','Absolutism','Nationalism'}
def check(p, want_bom):
    raw=open(p,'rb').read(); bom=raw[:3]==b'\xef\xbb\xbf'
    crlf=raw.count(b'\r\n')>0 and (raw.count(b'\n')-raw.count(b'\r\n'))==0
    txt=raw.decode('utf-8-sig')
    bad=[m for m in re.findall(r'ideology\s*=\s*(\w+)',txt) if m in PARENTS]
    print(f"{p}: BOM={bom==want_bom} CRLF={crlf} braces={txt.count('{')==txt.count('}')} parent_ideol={len(bad)}")
# 角色文件（want_bom=False）
check('common/characters/TNW_XYZ_characters.txt', False)
# 历史文件（want_bom=True）
check('history/countries/XYZ - X.txt', True)
```
- popularities 校验：块内 9 键、和=100、无非父桶键。
- **全局扫父桶 ideology**：`grep -rlE "ideology\s*=\s*(communist|syndicalism|socialism|Social_democracy|Liberalism|Conservatism|Authoritarianism|Absolutism|Nationalism)\b" common/characters/` 应为空。
- 历史 `ruling_party` 校验：`grep -nE "ruling_party\s*=" history/countries/*.txt` 后逐个确认值都在 9 父桶内。

## 6. 分支与提交流程
- 当前开发分支 `new-ui`；所有改动先落工作区，**未经用户确认不 commit**（cb_summary 约定）。
- 排查遵循"诊断→确认→执行→验证"；未定位根因前不要直接改代码；代码结果与预期不符时先验证再改。
- 文档/档案采用增量构建，修改 `descriptor.mod` 等关键 release 文件前先获得明确确认。

## 7. 开局领袖结算铁律（set_country_leader 禁令 + 正确结算方式，2026-11-01 用户最终确认）
- ⚠️ **`set_country_leader = X` 禁止用于 `history/countries/*.txt` 钉开局领袖！** 全仓 grep 证实：该写法在 history 里出现即违规；其合法用途**仅限** events / decisions / scripted_effects 内切换"已招募"的现任领袖（例：澳大利亚内战 `AST_civil_war_decisions.txt` 结算、`TNW_INS_scripted_effects.txt` 内战胜局、`TNW_CHA_events.txt` 事件——均用户认可）。
- ✅ **正确结算方式（钉开局领袖的唯一正确写法）= 纯靠 `recruit_character` 的排列顺序**：
  - **第一个被招募的 `recruit_character` = 开局领导人（总统）。**
  - **双领袖制（`has_second_leader_flag`）下，第二个被招募的 `recruit_character` = 第二领袖（总理）。**
  - 因此要指定元首，只需把对应角色排到 `recruit_character` 列表的**第一行**（双领袖则第一行=元首、第二行=第二领袖），**绝不加 `set_country_leader`**。
  - 反例（已修）：2026-11-01 我曾给 `CUB - Cuba.txt` / `NZL - New Zealand.txt` 加 `set_country_leader` 钉开局领袖，用户判定为错误写法，已撤除并改为调 `recruit_character` 顺序（古巴：`CUB_Ramon_Grau_San_Martin` 第一、`CUB_fulgencio_batista` 第二；新西兰：`NZL_peter_fraser` 第一）。
- 本模组 259/323 历史文件仅用 `recruit_character = <id>`（角色须先定义于 `common/characters/TNW_<TAG>_characters.txt`）推出开局领袖；全部 `recruit_character` 引用必须在角色文件真实定义，否则悬空引用（无害但 error.log 报错）。
- 双领袖（自创体系）：历史置 `has_second_leader_flag` + `<TAG>_<名>_PM_flag`；第二领袖本身也是普通 `country_leader`（须在角色文件定义），仅显示、不抢占元首。
