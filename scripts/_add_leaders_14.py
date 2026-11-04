# -*- coding: utf-8 -*-
"""Generate 1 head-of-state leader per country for 14 countries that currently
lack a valid leader (dead recruit stubs, commented-out templates, or none at all).
Writes:  common/characters/TNW_<TAG>_characters.txt  (no BOM, CRLF)
         localisation/simp_chinese/TNW_<TAG>_l_simp_chinese.yml (BOM, CRLF)
         edits history/countries/<TAG> - *.txt (BOM, CRLF): removes dead
         recruit_character / create_country_leader, adds 1 recruit_character.
"""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- data: tag -> dict -------------------------------------------------------
# cid  : full character id  (TAG_Name)
# name : display name (localisation)
# birth: line-1 of desc (birthplace + date)
# bg   : line-3+ of desc (background)
# ideo : valid sub-ideology key (exists in common/ideologies)
# flag : True => obscurity warning, user should verify/replace
LEAD = {
 "NGA": dict(cid="NGA_Nnamdi_Azikiwe", name="纳姆迪·阿齐克韦",
    birth="1904年11月16日，英属北尼日利亚保护国，宗格鲁（Zungeru）",
    bg="尼日利亚民族主义领袖、首任总统。早年留学美国，深受泛非主义影响，归国后创办《西非向导报》鼓吹民族自决。"
       "他联合行动党（NCNC）推动独立运动，以温和宪政手段对抗殖民当局，被视为尼日利亚现代建国的象征性人物。",
    ideo="oligarchy", flag=False),
 "NGR": dict(cid="NGR_Ahmadu_Bello", name="阿赫马杜·贝洛（索科托的萨尔达纳）",
    birth="1909年6月12日，索科托哈里发国，拉巴赫（Rabah）",
    bg="北尼日利亚最具影响力的传统与政治领袖，索科托苏丹国首相（Sardauna）。他主导北方地区事务，"
       "主张以伊斯兰与豪萨传统维系北尼日利亚邦联的认同，在联邦政治中与南方势力角力。",
    ideo="oligarchy", flag=False),
 "UAE": dict(cid="UAE_Shakhbut_bin_Sultan_Al_Nahyan", name="沙赫布特·本·苏丹·阿勒纳哈扬",
    birth="1905年，阿布扎比",
    bg="阿布扎比统治者（1928–1966），特拉维夫沿岸诸酋长国的实际共主。他谨慎保守，依赖珍珠贸易与石油租让维持酋长国独立，"
       "面对周边变局力求自保。",
    ideo="absolute_monarchy", flag=False),
 "NEP": dict(cid="NEP_Tribhuvan", name="特里布万·比尔·比克拉姆·沙阿",
    birth="1906年8月30日，尼泊尔，加德满都",
    bg="尼泊尔沙阿王朝国王。长期受拉纳家族架空，却始终是王权合法性的象征。在各方角力中，他谋求摆脱拉纳寡头的钳制，"
       "试图为尼泊尔争取更自主的道路。",
    ideo="absolute_monarchy", flag=False),
 "BHU": dict(cid="BHU_Jigme_Wangchuck", name="吉格梅·旺楚克",
    birth="1905年2月23日，不丹",
    bg="不丹第二任龙王（1926–1952），在位期间强化中央集权，推行现代行政改革，并在英印与西藏之间维系不丹的缓冲独立地位。",
    ideo="absolute_monarchy", flag=False),
 "PNG": dict(cid="PNG_Jack_Keith_Murray", name="杰克·基思·默里",
    birth="1889年1月15日，澳大利亚，新南威尔士州廷特菲尔德",
    bg="巴布亚新几内亚战后的澳大利亚行政长官（1945–1952），负责重建与过渡治理。在盟军托管框架下主持民政恢复，"
       "其去留将决定巴布亚未来的政治走向。（注：此人物为殖民行政官，若模组设定为本地领袖请替换）",
    ideo="Social_Liberalism", flag=True),
 "KUR": dict(cid="KUR_Mustafa_Barzani", name="穆斯塔法·巴尔扎尼",
    birth="1903年3月14日，奥斯曼帝国，巴尔赞",
    bg="库尔德民族运动的核心军事领袖，巴拉扎尼部族首领。毕生致力于库尔德独立与自治，曾与多国周旋，"
       "是库尔德斯坦独立国武装的支柱人物。",
    ideo="National_liberalism", flag=False),
 "TPS": dict(cid="TPS_Leonidas_Iasonidis", name="莱奥尼达斯·亚索尼迪斯",
    birth="1884年，奥斯曼帝国，特拉布宗（本都故地）",
    bg="本都希腊裔政治人物，亲俄倾向明显。在苏俄支持下于本都故地活动时，主张建立受莫斯科庇护的希腊人政权，"
       "力图在黑海东岸重建本都共同体的政治存在。（注：具体人物待确认）",
    ideo="Social_Liberalism", flag=True),
 "ICE": dict(cid="ICE_Sveinn_Bjornsson", name="斯维恩·比约恩松",
    birth="1881年2月27日，丹麦，哥本哈根",
    bg="冰岛首任总统（1944年起），早年任冰岛驻美丹代表，外交经验丰富。在冰岛脱离丹麦、确立共和的进程中居间斡旋，"
       "被视为国家统一与独立的象征。",
    ideo="Social_Liberalism", flag=False),
 "FLO": dict(cid="FLO_Raja_of_Flores", name="弗洛勒斯统治者（待确认具体人物）",
    birth="弗洛勒斯岛（具体出生信息待补充）",
    bg="弗洛勒斯王国的地方统治者，统辖该岛诸部落与村落。在荷属东印度解体后的权力真空中，其立场将决定弗洛勒斯是投向爪哇还是维持地方自治。"
       "（注：具体人物与出生信息待补充）",
    ideo="nationalism", flag=True),
 "TIM": dict(cid="TIM_Provisional_Administrator", name="帝汶临时管制区行政长官（待确认）",
    birth="（具体出生信息待补充）",
    bg="帝汶岛临时管制区由盟军（澳大利亚）在战后设立，负责接管与过渡治理。其行政长官须在葡属东帝汶与荷属西帝汶的复杂遗产中维系秩序。"
       "（注：具体人物待确认）",
    ideo="Social_Liberalism", flag=True),
 "QAT": dict(cid="QAT_Abdullah_bin_Jassim_Al_Thani", name="阿卜杜拉·本·贾西姆·阿勒萨尼",
    birth="1880年，卡塔尔，多哈",
    bg="卡塔尔第七任埃米尔（1913–1949），在位期间逐步摆脱英国的保护国束缚，于1930年代签署协定确立卡塔尔边界。"
       "他主导了从珍珠经济向石油经济的转型起点。",
    ideo="absolute_monarchy", flag=False),
 "GTL": dict(cid="GTL_Nani_Wartabone", name="纳尼·瓦尔塔博内",
    birth="1907年4月30日，荷属东印度，戈龙塔洛",
    bg="戈龙塔洛民族主义领袖，1942年宣布戈龙塔洛加入印度尼西亚，是当地反殖民与建国运动的关键人物。"
       "他联结米纳哈萨与戈龙塔洛的族群网络，谋求在群岛新格局中保住地方的发言权。",
    ideo="Social_Liberalism", flag=False),
 "RYU": dict(cid="RYU_Far_East_Naval_Commander", name="远东海军基地司令（待确认）",
    birth="（具体出生信息待补充）",
    bg="工人国际远东海军基地（美国红海军）的司令官，统率这支由亲莫斯科的美国水兵与技术人员组成的远洋力量。"
       "基地盘踞琉球，是太平洋上红色阵营投射影响力的关键支点。（注：具体人物待确认）",
    ideo="military_government", flag=True),
}

EXP = "1970.1.1"

def w_bom_crlf(path, text):
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(path, "wb") as f:
        f.write(b"\xef\xbb\xbf" + text.encode("utf-8"))

def w_nobom_crlf(path, text):
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))

def load_bom_crlf(path):
    raw = open(path, "rb").read()
    txt = raw[3:].decode("utf-8") if raw[:3] == b"\xef\xbb\xbf" else raw.decode("utf-8")
    return txt.replace("\r\n", "\n").replace("\r", "\n")

for tag, d in LEAD.items():
    cid = d["cid"]
    # ---- 1) character file ----
    char = (
        "characters = {\n"
        f"\t{cid} = {{\n"
        f"\t\tname = {cid}\n"
        "\t\tportraits = {\n"
        "\t\t\tcivilian = {\n"
        f"\t\t\t\tlarge = GFX_portrait_large_{cid}\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t\tcountry_leader = {\n"
        f"\t\t\tdesc = {cid}_desc\n"
        f"\t\t\tideology = {d['ideo']}\n"
        "\t\t\ttraits = {\n"
        "\t\t\t}\n"
        f'\t\t\texpire = "{EXP}"\n'
        "\t\t\tid = -1\n"
        "\t\t}\n"
        "\t}\n"
        "}\n"
    )
    w_nobom_crlf(os.path.join(ROOT, "common/characters", f"TNW_{tag}_characters.txt"), char)

    # ---- 2) localisation ----
    desc = (f"§Y出生于：§!§L{d['birth']}§!\\n\\n"
             f"§Y人物背景：§!§L{d['bg']}§!")
    loc = (
        "l_simp_chinese:\n"
        f"\t{cid}:0 \"{d['name']}\"\n"
        f"\t{cid}_desc:0 \"{desc}\"\n"
    )
    w_bom_crlf(os.path.join(ROOT, "localisation/simp_chinese", f"TNW_{tag}_l_simp_chinese.yml"), loc)

    # ---- 3) history edit ----
    hfs = glob.glob(os.path.join(ROOT, "history/countries", f"{tag} - *.txt"))
    assert hfs, f"No history file for {tag}"
    hf = hfs[0]
    t = load_bom_crlf(hf)
    # remove all recruit_character lines
    t = re.sub(r"^\s*recruit_character\s*=\s*[A-Za-z0-9_]+\s*$", "", t, flags=re.M)
    # remove create_country_leader blocks (active or commented)
    t = re.sub(r"#?\s*create_country_leader\s*=\s*\{.*?\}\s*\}", "", t, flags=re.S)
    # collapse blank lines and trim
    t = re.sub(r"\n{3,}", "\n\n", t)
    # insert 1 recruit after the capital = N line
    t = re.sub(r"(capital\s*=\s*\d+\s*\n)",
               lambda m: m.group(1) + f"recruit_character = {cid}\n",
               t, count=1)
    w_bom_crlf(hf, t)
    print(f"{tag}: wrote char+loc, edited {os.path.basename(hf)}  (flag={d['flag']})")
print("DONE")
