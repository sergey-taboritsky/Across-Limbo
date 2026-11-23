# 开国领导人缺头像清单（按大洲分类）

> 生成依据：扫描 `history/countries/*.txt` 的 `recruit_character` 与 `ruling_party`，
> 取「意识形态父桶 == ruling_party 且为 country_leader、recruit 位置最靠上」者为开国领导人；
> 再比对角色文件的 portrait 引用、`interface/picture_gfx/TNW_characters_portraits.gfx` 的 sprite 注册、以及 `gfx/characters/` 下 texturefile 指向的 PNG 是否真实存在。
> 统计：167 国含合法开国领导人，其中 **52 国缺头像**；其余国家无合法开国领导人（非领袖 tag，不计入）。
>
> 状态说明：
> - MISSING_ASSET：角色已写 portrait 引用，但 gfx 无对应 sprite（补 gfx + PNG）
> - NO_PORTRAIT_REF：角色文件未写 portrait 行（先补引用再补资源）
> - MISSING_PNG：gfx 已注册 sprite，但 texturefile 指向的 PNG 文件不存在（断链）
>
> 本表由 `_r44_census.py` + `_r44_rebuild_snapshot.py` 实时重建（R44，2026-11-22）；旧快照（76 缺图）备份于 `_backup_round44/missing_portraits/`。

## 亚洲（18 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| FLO | Flores | FLO_Don_Thomas_Ximenes_da_Silva | MISSING_ASSET |
| GTL | Gorontalo | GTL_Nani_Wartabone | MISSING_ASSET |
| HYD | Hyderabad | HYD_Swami_Ramanand_Tirtha | MISSING_ASSET |
| JGS | Jogja Sultanate | JGS_Hamengkubuwono_IX | NO_PORTRAIT_REF |
| JHR | Johor | JHR_Sultan_Ibrahim_Johor | NO_PORTRAIT_REF |
| KNR | North Korea | KNR_Shin_Sung_Mo | NO_PORTRAIT_REF |
| KUR | Kurdistan | KUR_Mustafa_Barzani | MISSING_ASSET |
| KUW | Kuwait | KUW_Ahmad_Aljaber_Alsabah | NO_PORTRAIT_REF |
| MAH | Madras | MAH_KM_Cariappa | MISSING_ASSET |
| PAK | Pakistan | PAK_Gopi_Chand_Bhargava | MISSING_ASSET |
| PHI | Philippines | PHI_cipriano_cid | NO_PORTRAIT_REF |
| QAT | Qatar | QAT_Abdullah_bin_Jassim_Al_Thani | NO_PORTRAIT_REF |
| SAB | Sabah | SAB_Mustapha_Harun | NO_PORTRAIT_REF |
| SJR | Sjahrir Government | SJR_Sutan_Sjahrir | NO_PORTRAIT_REF |
| SRL | Sri Lanka | SRL_Solomon_Bandaranaike | MISSING_ASSET |
| TIM | Timor | TIM_Lewis_Dyke | MISSING_ASSET |
| UAE | United Arab Emirates | UAE_Shakhbut_bin_Sultan_Al_Nahyan | NO_PORTRAIT_REF |
| YEM | Yeman | YEM_Ahmad_bin_Yahya | NO_PORTRAIT_REF |

## 欧洲（4 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| AUS | Austria | AUS_Karl_Renner_1948 | NO_PORTRAIT_REF |
| CZE | Czechoslovakia | CZE_edvard_benesh | NO_PORTRAIT_REF |
| GRK | Greek Kingdom | GRK_Regency_Council | NO_PORTRAIT_REF |
| ICE | Iceland | ICE_Sveinn_Bjornsson | MISSING_ASSET |

## 非洲（14 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| ALG | Algeria | ALG_Larbi_Bouhali | MISSING_ASSET |
| BRD | Burundi | BRD_Mwambutsa_IV | MISSING_PNG |
| CAR | Central African Republic | CAR_Barthelemy_Boganda | MISSING_PNG |
| CHA | Chad | CHA_Pierre_Messmer | MISSING_PNG |
| DJI | Djibouti | DJI_Mahamoud_Harbi | NO_PORTRAIT_REF |
| GAB | Gabon | GAB_Leon_Mba | MISSING_ASSET |
| KEN | Kenya | KEN_Philip_Mitchell | MISSING_PNG |
| LTH | Lesthoto | LTH_Mantsebo | NO_PORTRAIT_REF |
| NGR | Niger | NGR_Hamani_Diori | NO_PORTRAIT_REF |
| RWA | Rwanda | RWA_Mutara_III_Rudahigwa | MISSING_PNG |
| TUA | Tuareg | TUA_Meslar_ag_Amayas | NO_PORTRAIT_REF |
| UGA | Uganda | UGA_Mutesa_II | MISSING_PNG |
| WES | Western Sahara | WES_Awang_Rambli | NO_PORTRAIT_REF |
| ZNB | Zanzibar Sultanate | ZNB_Khalifa_bin_Harub | NO_PORTRAIT_REF |

## 南美（9 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| ARG | Argentina | ARG_Pedro_Pablo_Ramirez | MISSING_ASSET |
| BOL | Bolivia | BOL_Victor_Paz_Estenssoro | MISSING_ASSET |
| BRA | Brazil | BRA_Luis_Carlos_Prestes | MISSING_ASSET |
| CAY | Cayenne | CAY_Rene_Jadfard | MISSING_ASSET |
| CHL | Chile | CHL_Marmaduque_Grove | MISSING_ASSET |
| GYA | Guyana | GYA_Cheddi_Jagan | MISSING_ASSET |
| PRU | Peru | PRU_Jose_Luis_Bustamante_y_Rivero | MISSING_ASSET |
| URG | Uruguay | URG_Luis_Batlle_Berres | MISSING_ASSET |
| USR | Uruguay Socialist Republic | USR_Emilio_Frugoni | MISSING_ASSET |

## 北美（5 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| BAH | Bahamas | BAH_George_Beresford_Stooke | MISSING_ASSET |
| CUB | Cuba | CUB_Ramon_Grau_San_Martin | MISSING_ASSET |
| DOM | Dominican Republic | DOM_Rafael_Trujillo | NO_PORTRAIT_REF |
| HAI | Haiti | HAI_jacques_roumain | MISSING_ASSET |
| JAM | Jamaica | JAM_Norman_Manley | MISSING_ASSET |

## 大洋（2 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| NZL | New Zealand | NZL_peter_fraser | MISSING_ASSET |
| PNG | Papua New Guinea | PNG_Jack_Keith_Murray | MISSING_ASSET |
