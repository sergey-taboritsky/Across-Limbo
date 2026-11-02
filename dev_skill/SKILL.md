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
