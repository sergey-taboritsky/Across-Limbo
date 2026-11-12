---
name: across-limbo-mod-dev
description: HOI4 Across-Limbo（TNO 框架，前缀 TNW_）模组开发铁律与常见 bug 速查。当用户要新增/修改角色(characters)、把新角色端到端实装（定义→recruit→本地化）、安装角色头像(portrait)、历史文件(history/countries)、意识形态、国策、事件、决议、开战方式或脚本和平，或排查"角色不显示 / 政治系统崩坏 / 战争不触发 / 脚本和平成死代码"等模组问题时使用。融合仓库内 AGENTS.md(=skill.pdf，《钢铁雄心 IV Mod 开发完整代码规则书》)的语法权威 + 本项目历次踩坑蒸馏出的铁律。**做涉及角色/历史/本地化/头像的模组改动前，先读一遍本 skill。**
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
| `interface/picture_gfx/*.gfx`（头像 sprite 注册） | **无** | **CRLF** | tab |

- ⚠️ `common/*` 的 BOM **本仓库并不统一**：多数角色文件（如 `TNW_CUB_*` / `TNW_SOV_*`）无 BOM，但 `TNW_IRQ_characters.txt` 实际带 BOM；HOI4 对 common 文件 BOM 容忍，**保持与同目录既有文件一致即可，不要主动去改已带 BOM 的文件**。唯一零容忍的是 **本地化 BOM**（缺 BOM 会连锁拖垮后续同语言文件）。
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

## 8. 角色端到端实装流程（定义 → recruit → 本地化，2026-10-30~11-01 反复踩坑固化）

把"一个新角色从无到有、在游戏里作为领袖/顾问出现且名字正确显示"拆成三步。任何一步漏掉都会表现为"角色不显示"或"显示成 key 原文"。

**角色 key 规范**：`<TAG>_<name>`（如 `IRQ_abd_al_salam_arif`、`CUB_Ramon_Grau_San_Martin`），全仓库唯一；不要写成中文或带空格。

- ⚠️ **SOV 不新建角色文件（2026-11-02 铁律）**：本模组**不为 SOV（苏联）单独建 `common/characters/TNW_SOV_characters.txt`**。任何俄/苏背景人物一律归 **`RUS`（俄罗斯）** 角色文件，key 用 `RUS_<name>`。反例：瓦图京 `SOV_nikolay_vatutin` 曾误建于 SOV，已整体迁至 `RUS_nikolay_vatutin`（角色文件/gfx/png/历史 recruit/本地化同步改名，并删除 `TNW_SOV_characters.txt`）。SOV 历史文件里既有的内联角色池（斯大林、朱可夫等）属 TNO 核心/既有定义，不在本规则清理范围；本规则只约束"新建角色时归属谁"。

### Step 1 — 在 `common/characters/TNW_<TAG>_characters.txt` 定义（无 BOM + CRLF + tab；见 §1）
- 角色块最小结构（`country_leader` / `advisor` 按需要）：
```
<TAG>_<name> = {
	name = <TAG>_<name>
	portraits = {
		civilian = {
			large = GFX_portrait_large_<TAG>_<name>
		}
	}
	country_leader = {
		desc = <TAG>_<name>_desc
		ideology = <子意识形态>      # ⚠️ 必须是子项，绝不能是 9 父桶
		traits = { }
	}
	advisor = {                      # 仅当该角色也当顾问时
		slot = political_advisor
		idea_cost = 100
	}
}
```
- `ideology` 选子项**前先查本地化语义**（`localisation/simp_chinese/parties_l_simp_chinese.yml`），不能凭英文单词字面猜。反例：`discipline`=训政（国民党专属，曾误配马德拉斯将军 `MAH_KM_Cariappa`，已改 `oligarchy`）；`Marxism_Leninism`∈communist；`military_government`∈Absolutism；`Social_democratic`∈Social_democracy；`oligarchy`∈Authoritarianism。详见 §2 子→父映射。
- 所选子项必须属于历史文件 `ruling_party` 所用的 9 父桶之一（否则政治系统崩坏，见 §2/§3）。
- 禁止 `types = {}` 块（会删必需字段）；用扁平 `ideology = <子项>`。
- 若角色要立绘，`portraits` 块的 `GFX_portrait_large_<TAG>_<name>` 必须与 §9 注册的 sprite 名一致。

### Step 2 — 在 `history/countries/<TAG> - X.txt` 招募（有 BOM + CRLF；见 §1）
- 加一行 `recruit_character = <TAG>_<name>`（**单行，不是块**）。
- 开局领袖结算见 §7：第一个 `recruit_character` = 开国领导人（双领袖制次行 = 第二领袖）；**禁止**用 `set_country_leader` 钉历史文件。
- 引用名必须与 Step1 定义的 key 完全一致，否则悬空引用（无害但 error.log 报错）。

### Step 3 — 在 `localisation/simp_chinese/TNW_<TAG>_l_simp_chinese.yml` 补齐本地化（有 BOM + CRLF + 键前 1 空格）
- 至少补三类键（缺失会显示成 key 原文或空白）：
  - 角色名：`<TAG>_<name>:0 "中文通行译名"`
  - 描述：`<TAG>_<name>_desc:0 "一句话人设"`
  - 顾问/理念提示：角色有 `advisor` 槽时复用 `<TAG>_<name>_desc` 即可。
- **人名必须用通行译名**：先 WebSearch 核实，不凭拼音硬翻。反例：智利 `CHL_Marmaduque_Grove` 应为「马马杜克·格罗维·巴列霍」（非「马尔马杜克·格罗夫」）。
- 写文件务必显式 `\ufeff` BOM + `\r\n`，写完用字节级检查复核（前 3 字节=`ef bb bf`、含 `\r\n`）。**缺 BOM 会连锁拖垮后续同语言文件加载**（BOL 事故）。
- 若该国 yml 不存在则新建（同 BOM+CRLF 规约）；若键已存在于别的拼写（如 `COL_Jorge_Gaitan` vs `COL_Jorge_Elicier_Gaitan`），以角色 `name =` 为准对齐，不要留两个不一致的键。

### 收尾验证（改完必跑，见 §5）
- common 文件无父桶 ideology（全局 grep 应为空）；history 无 `set_country_leader`；本地化 BOM+CRLF；括号配平；`recruit_character` 引用的 key 都在角色文件定义。

### 部长 / 顾问(HOG·theorist) 与政党派系 添加方式（2026-11-02 固化，范式来自 BRA）
**核心范式（参考 `TNW_BRA_characters.txt` + `BRA - Brazil.txt`）**：同一个角色定义里可以**同时**写 `advisor = { ... }` 与 `country_leader = { ... }`——前者让它作为顾问/部长/HOG/理论家出现，后者让它作为该意识形态的党魁出现。这就是"一个人既是意识形态 leader 又是 advisor"的写法（BRA 的 `BRA_Antonio_Bonfim` = HOG 顾问 + country_leader 同体）。

- **`advisor` 块字段**（`slot` 三选一）：
  - `slot = political_advisor` → 普通部长
  - `slot = head_of_government` → 政府首脑 HOG
  - `slot = theorist` → 军事/民用理论家（额外加 `ledger = civilian` 或 `ledger = military`）
  - `idea_token = <TAG>_<name>_advisor`（HOG 用 `_hog`、理论家用 `_theorist`；该 token 就是顾问槽的显示名，见本地化）
  - `allowed = { original_tag = <TAG> }`、`traits = { }`、`cost = -1`
- **双职写法**（以"既是社民党魁又是 HOG"为例）：
```
<TAG>_<name> = {
	name = <TAG>_<name>
	advisor = {
		slot = head_of_government
		idea_token = <TAG>_<name>_hog
		allowed = { original_tag = <TAG> }
		traits = { }
		cost = -1
	}
	country_leader = {
		desc = <TAG>_<name>_desc
		ideology = <子意识形态>      # 必须是 9 父桶下的子项（查 §2 映射）
		expire = "2022.10.20.1"
		id = -1
		traits = { }
	}
}
```
- **历史文件**（`history/countries/<TAG>.txt`，见 §1 编码）：
  - `recruit_character = <TAG>_<name>`（双职角色也要 recruit，否则党魁位空悬、开局无该党领袖）
  - `activate_advisor = <TAG>_<name>_advisor`（HOG 用 `_hog`、理论家用 `_theorist`）——**定义 advisor 后必须 activate，否则顾问槽不出现**（BRA 历史末尾 `activate_advisor = BRA_Francisco_Mangabeira_advisor` 等即此范式）。
- **本地化**（Step 3 同规约）：除角色名 `<TAG>_<name>` 与 `<TAG>_<name>_desc` 外，还要补顾问 token 名 `<TAG>_<name>_advisor:0 "中文名"`（HOG/理论家同理用 `_hog`/`_theorist`），否则顾问显示成 key 原文。
- ⚠️ **无立绘时**：`portraits` 块整体省略（不要引用不存在的 `GFX_portrait_large_*`），否则 error.log 报找不到 sprite。

**政党派系改名（`set_party_name` effect，本模组党名唯一正确手段）**：
- 党名**不能**写历史文件；必须用 effect `set_party_name`，通常挂在 `common/on_actions/TNW_on_startup_on_actions.txt` 的 `on_startup → effect → every_country` 内（加 `if = { limit = { tag = <TAG> } }` 守卫），开局即生效。
- 写法（每个意识形态一次）：
```
if = {
	limit = { tag = <TAG> }
	set_party_name = {
		ideology = <父桶名，如 Conservatism/socialism/Social_democracy/Liberalism/Authoritarianism/Absolutism/communist>
		long_name = <TAG>_<ideology>_party
		name = <TAG>_<ideology>_party
	}
}
```
- 本地化键 `<TAG>_<ideology>_party:0 "派系名"` 写在 `TNW_<TAG>_l_simp_chinese.yml`（BOM+CRLF）。例：`MON_Authoritarianism_party: "蒙人党 - 银行系"`。蒙古(MON)已把 6 大派系改名蒙人党各系 + Absolutism→蒙古国民军，可作完整范例。

## 9. 头像安装工作流程（png → gfx 注册 → 角色 portraits 块，2026-11-02 固化）

适用：拿到若干张角色头像 PNG，给模组里（已存在或新建的）角色挂立绘。

### Step 1 — 落图
- 把 PNG 放到 `gfx/characters/<TAG>_<name>.png`，文件名**必须 = 角色 key**（即 `<TAG>_<name>`）。
- 同一人物用于多个国家时（如 Billy Hughes 同时是 AST 与 AFF 领袖），按国家各放一张、文件名带各自 TAG（`AST_Billy_Hughes.png` / `AFF_Billy_Hughes.png`），各自注册。

### Step 2 — 在 `interface/picture_gfx/TNW_characters_portraits.gfx` 注册 spriteType（无 BOM + CRLF + tab；顶部 `spriteTypes = {`，与既有 sprite 同级）
- 在对应国家分组注释（`#国家` / `#人名`）下、或文件末尾 `}` 之前，追加：
```
	#<国家>
	#<人名>
	spriteType = {
		name = "GFX_portrait_large_<TAG>_<name>"
		texturefile = "gfx/characters/<TAG>_<name>.png"
	}
```
- `name` 与 `texturefile` 的 `<TAG>_<name>` 必须和 Step1 文件名、Step3 角色 `portraits` 块引用的 `GFX_portrait_large_<TAG>_<name>` **三处完全一致**。
- 缩进用 tab，与文件内既有 spriteType 对齐；整文件花括号必须配平（改完用括号检查复核，本仓库该文件约 411/411）。
- 可选：`legacy_lazy_load = no`（仓库部分头像有，意为预加载；非必须，普通头像不写也行）。

### Step 3 — 在角色文件补 `portraits` 块
- 若 `common/characters/TNW_<TAG>_characters.txt` 该角色**还没有** `portraits` 块（只有 `advisor` / `country_leader` 没有立绘声明），补上：
```
	portraits = {
		civilian = {
			large = GFX_portrait_large_<TAG>_<name>
		}
	}
```
- 纯顾问且不打算显示立绘可省略；但本模组惯例是领袖与顾问都挂立绘。
- 缩进 tab，与角色块内其它字段对齐。

### Step 4 — 清理
- 装完确认游戏内能看到立绘后，**删除下载文件夹里的原图**（用户铁律：装完即删，不留本地副本）。

### 验证
- 游戏内开对应国家书签，确认头像正常显示、`error.log` 无 `Failed to find sprite` / `portrait` 相关报错。

## 10. 国旗实装工作流程（源图 → 旗帜处理.exe → 三处 flags，2026-11-02 固化）

适用：拿到一张目标国旗 PNG（设计稿，任意尺寸/比例均可），要让游戏内显示大/中/小三面旗。

### 工具
- `dev_skill/旗帜处理.exe`（Windows GUI，约 26MB）：输入一张国旗 PNG，切分为大/中/小三份**同名**图片（命名 = 目标 tag 或 cosmetic_tag）。
- 该 exe 为 GUI，由用户在本地机器运行（Agent 环境无法无头驱动）；Agent 的职责是接收其输出的三份文件、按规约落到正确目录并核对。

### Step 1 — 准备源图 & 运行工具
- 确认目标 tag（或 cosmetic_tag），例如 `MAL`、`KNR_fascist_state`。
- 用 `旗帜处理.exe` 打开源 PNG，导出三份同名图片：`<tag>.tga`（大）、`<tag>.tga`（中）、`<tag>.tga`（小）。**三份文件名完全相同**，仅尺寸不同（工具负责缩放/裁切到 HOI4 规格，不必手动画）。

### Step 2 — 落位（三处目录，命名必须 = tag）
- 大（**82×52**）→ `gfx/flags/<tag>.tga`
- 中（**41×26**）→ `gfx/flags/medium/<tag>.tga`
- 小（**10×7**） → `gfx/flags/small/<tag>.tga`
- 实测规格（以 ALP / MAL 为例）：大 82×52、中 41×26、小 10×7，均为 **TGA** 格式（`旗帜处理.exe` 即按此输出）。
- cosmetic flag（如 `MAL_AprilFools`、`MAL_UK`、`KNR_fascist_state`）命名用对应 cosmetic_tag，落位同上三处。
- 例：用户给定 MAL 国旗 PNG（红底、左上蓝块含白星），`MAL.tga` 已按此规格存在于三处（gfx/flags / medium / small），即本流程产出形态。

### Step 3 — 验证
- 进游戏选对应书签，确认大/中/小三面旗均正常显示、`error.log` 无 `flag` / `texture` 相关报错。
- 三处文件命名一致、尺寸符合上表（大 82×52 / 中 41×26 / 小 10×7）。

### 备注
- 源图是任意比例的设计稿即可，工具负责缩放；不要手动画 82×52。
- 若某 tag 已有旧旗，运行工具会**覆盖**三处同名文件（更新设计）；动手前先确认是否要保留旧版。

## 11. 议会席位图（半圆 Parliament Diagram）自动化（2026-11-11 固化）

用户提供了 `C:/Users/edwar/Documents/GitHub/hoi4-parliament-diagram-fork`（Flaxbeard 原版 tkinter 工具 + `parliament_sample/` 范例）。本仓已把坐标算法抽成无 GUI 依赖的 headless 生成器，并沉淀完整 SOP：

- **SOP 全文**：`dev_skill/PARLIAMENT_DIAGRAM_SKILL.md`（§0 执行契约 / §2 算法与 5 个坑 / §3 配置 schema / §5 落位 8 步 / §7 MAL 104 席实例 / §8 校验清单）
- **生成器**：`dev_skill/parliament_diagram/parliament_generator.py`
- **已验证实例**：`dev_skill/parliament_diagram/examples/MAL_leg_104/`（含 `config.json`、`preview.html`、8 个代码片段、`manifest.json`）

**执行契约**：以后用户说「做议会 / 议会席位图 / 半圆议席」，直接复制配置 → 跑 `python parliament_generator.py --config <config>` → 按 SOP §5 落位 → §9 校验，不要重写算法、不要手排圆点、不要再问坐标怎么处理。

铁律补充：
- 议会是**国家机构**，院内单位必须是**政党党团**；中执委是**党内机构**，单位是党内派系。两套席位账不得混算，只允许党内力量对比 → 议会党团忠诚度的单向派生。
- 议席图 = 3 个等长数组（x / y / frame）+ 1 个 `dynamic_lists` + 1 张多帧座位精灵图。原版工具只产出 x/y，frame 与接线由本仓生成器补齐。
- 坐标数组只在首次打开时生成一次（`initialized_flag` 防重复），之后只重算 frame；不要每月重建 2×N 行 `add_to_array`。
- 座位 dds 的 `noOfFrames` 必须 = 党团数，fork 自带的 4 帧图不能直接套到 7 党团议会。

## 12. 国策前置条件 `prerequisite` 的 AND / OR 语义（2026-11-12 用户第三次纠正后固化）

⚠️ **本仓反复翻车的基本知识点。判断任何「国策死锁 / 前置冲突」之前，先数 `prerequisite` 块的个数；不许因为两个 focus 名字出现在同一个国策定义里就判成 AND。**

| 写法 | 语义 | 连接线 |
|---|---|---|
| 同一个 `prerequisite = { }` 块内写多个 `focus =` | **OR**，任一完成即可 | 虚线 |
| 多个 `prerequisite = { }` 块并列 | **AND**，每块都要满足（每块内部仍按 OR） | 实线 |
| 两者混用 | 块间 AND × 块内 OR | 混合 |

三种写法对照（本仓真实代码）：

```
# ① OR：MAL_Transit_Trade_Nation —— 两个互斥分支任一完成即可继续
prerequisite = {
	focus = MAL_Free_Port_Status
	focus = MAL_Fiscal_Autonomy
}

# ② AND：两颗国策都必须完成
prerequisite = {
	focus = MAL_Restore_German_East_Asia_Arsenal
}
prerequisite = {
	focus = MAL_Recruit_Former_Singapore_Generals
}

# ③ 混合：(A 或 B) 且 C —— JAP 范式
prerequisite = {
	focus = JAP_Farmer_Comrade_Organization
	focus = JAP_Farmer_Union_Organization
}
prerequisite = {
	focus = JAP_Labor_Reliance_System
}
```

**权威出处**：`dev_skill/HOI4_modding_rulebook.md`「国策 → 视觉指示器」节（约 19900 / 19903 行）：连接线「实线表示逻辑与，虚线表示逻辑或」；互斥分支之后的汇合国策「技术共享（通过*或*连接同时与双方相连）」——即互斥二选一后的汇合**必须写成单块 OR**。

**本仓通用范式**：全仓 23 棵国策树 / 1144 个 focus 中，有 **60 处**「单块多 focus 且内部互斥」的 OR 汇合（ALP / BRA / CHI / DDR / EGY / ENG / FRA / INS / JAP / MAL / PHI / TUR / WGR），例如 `MAL_Transit_Trade_Nation`、`MAL_Declare_Republic`、`MAL_Next_Confrontation_Phase`、`JAP_Combat_Aethiests_Union`。这是**故意的设计**，不是 bug。

**反面教材（本 AI 实犯）**：曾把 `MAL_Transit_Trade_Nation` 的单块 OR 读成「同时要求两个互斥国策」，据此判定为「死锁」，写进长期记忆、设计稿和多轮汇报。实际扫描：全仓 AND 结构中的互斥冲突 = **0**，该国策只有 1 个 `prerequisite` 块，设计正确。该错误结论已全部撤销。

**执行规则**：
- 报「死锁」前必须：解析出该 focus 的每个 `prerequisite` 块 → 块内取 OR 候选集 → 只在「存在两个块 A/B 使 A×B 全部互斥」时才判死锁；否则不许下结论。
- 真死锁的修法：把互斥的两个 focus 从「多个块」合并进「同一个块」（AND → OR），而不是删国策或改互斥关系。
- `mutually_exclusive` 只阻止两个国策同时被完成，**不阻止**它们作为 OR 候选挂在同一后续国策上。
- 自动检测已固化在 `_mal_verify.py` 第 14 节，每次全量校验会扫全仓 focus 树验证此规则。

## 13. MAL 本地化按 categories 归位（2026-11-12 第十五轮，用户定稿）

`localisation/simp_chinese/TNW_MAL_l_simp_chinese.yml` 开头由用户列出 12 个类别标题，**必须保持这个顺序**：

```
#介绍 → #国名 → #政党名 → #领导人 → #民族精神 → #事件 → #新闻 → #GUI → #BOP → #决议 → #国策 → #其他
```

**硬规则**：
1. 每条本地化 key 放进它对应的类别标题下面；**拿不准或不属于前 11 类的一律放 `#其他`**，禁止硬猜。
2. **每个类别内部严格保持原文件从上到下的顺序**（只重排，不改写任何一行文本，含行尾注释和转义引号）。
3. **追加新本地化后必须重新归位**：跑 `python _mal_loc_sort.py --apply`（工作区脚本，幂等）。它从代码侧提取 id 集合来判定归属，新增 key 若无法匹配代码侧对象会自动落 `#其他`；跑完再跑 `python _mal_verify.py`，第 22 节会逐 key 校验类别是否正确。
4. ⚠️ **禁止重跑** `_mal_r10_descs.py` / `_mal_r11_traits.py`（已加 `R15_GUARD`）：它们会先从 `_backup_round10|11/` 恢复旧版 yml，会覆盖重排结果与用户新增文案。回退用 `_backup_round15/` 直接覆盖。

**分类口径（以代码侧实际引用为准，不猜）**：

| 类别 | 判定依据 |
|---|---|
| 介绍 | `TNW_welcome_MAL_intro_text_*` 开局介绍 |
| 国名 | 国家/政权名 `*_DEF` / `_ADJ` 及其主名 |
| 政党名 | `*_party` / `_party_long`、具名政党 `MAL_party_*`、立法院党团 `MAL_leg_party_*` |
| 领导人 | `common/characters/` 定义的角色 key 及 `_desc` / `_commander_desc`（含 MRP / JHR 顶格写法） |
| 民族精神 | `common/ideas/` 定义的 idea id 及 `_desc` |
| 事件 | `country_event` 的 `.N.t/.d/.a/.b/.c` 与事件侧 tooltip |
| 新闻 | `news_event` 的 `.N.t/.d/.a` |
| GUI | 决议分类名 + `_desc`、scripted_localisation 面板读数（stance / status / bill_result / seat_tt） |
| BOP | `common/bop/` 相关（本仓 MAL 暂无定义，**保留空栏**，不要塞别的内容） |
| 决议 | decision id 及 `_desc` / `_tt`；`TNW_arch_*_tt` 整族跟随群岛争霸决议组 |
| 国策 | focus id 及 `_desc` / `_tt` |
| 其他 | 动态修正、dummy 占位、`MAL_focus_wip_desc`、7 组 unit_leader trait 名/说明、独立 tooltip |

**两个易错点**：
- `MAL_kmt_party` 以 `_party` 结尾，但它是 `common/decisions/categories/` 里的**决议分类**，必须归 `#GUI`；分类判定要**先于**政党名判定。
- 附属 key（`_desc` / `_commander_desc` / `_tt` / `_ttN` / `_long` / `_DEF` / `_ADJ`）**跟随主 key 的类别**，不单独判断。

**编码**：yml 单 BOM + 纯 CRLF；重排脚本会剥离旧类别标题再重建，因此幂等。
