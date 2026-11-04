# 开国领导人缺头像清单（按大洲分类）

> 生成依据：扫描 `history/countries/*.txt` 的 `recruit_character` 与 `ruling_party`，
> 取「意识形态父桶 == ruling_party 且为 country_leader、recruit 位置最靠上」者为开国领导人；
> 再比对 `interface/picture_gfx/TNW_characters_portraits.gfx` 中已定义的 `GFX_portrait_large_<cid>` 头像键。
> 统计：164 国含合法开国领导人，其中 76 国缺头像；其余 159 国无合法开国领导人（非领袖 tag，不计入）。
>
> 状态说明：
> - MISSING_ASSET：角色文件已写 `portrait`/`large` 引用，但 gfx 中无对应 sprite（需补 .gfx 定义 + .dds 贴图）。
> - NO_PORTRAIT_REF：角色文件根本没写 portrait 行（需先补 portrait 引用再补资源）。

## 亚洲（27 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| BRN | Brunei | BRN_Ahmad_Tajuddin | NO_PORTRAIT_REF |
| FLO | Flores | FLO_Don_Thomas_Ximenes_da_Silva | MISSING_ASSET |
| GTL | Gorontalo | GTL_Nani_Wartabone | MISSING_ASSET |
| HAT | Hatta Government | HAT_Mohammad_Hatta | NO_PORTRAIT_REF |
| HEJ | Hejaz | HEJ_ali_bin_hussein | NO_PORTRAIT_REF |
| HYD | Hyderabad | HYD_Swami_Ramanand_Tirtha | MISSING_ASSET |
| JGS | Jogja Sultanate | JGS_Hamengkubuwono_IX | NO_PORTRAIT_REF |
| JHR | Johor | JHR_Sultan_Ibrahim_Johor | NO_PORTRAIT_REF |
| KLT | Kalat | KLT_Ahmad_Yar_Khan | MISSING_ASSET |
| KNR | North Korea | KNR_Shin_Sung_Mo | NO_PORTRAIT_REF |
| KOR | Korea | KOR_Syngman_Rhee | NO_PORTRAIT_REF |
| KSM | Kashmir | KSM_Gopalaswami_Ayyangar | MISSING_ASSET |
| KUR | Kurdistan | KUR_Mustafa_Barzani | MISSING_ASSET |
| MAH | Madras | MAH_KM_Cariappa | MISSING_ASSET |
| MLD | Maldives | MLD_Abdul_Majeed_Didi | MISSING_ASSET |
| MON | Mongolia | MON_Tseren_Ochiryn_Dambadorj | NO_PORTRAIT_REF |
| MUR | Murba Regime | MUR_Sukarni | NO_PORTRAIT_REF |
| OMA | Oman | OMA_said_bin_taimur | MISSING_ASSET |
| PAK | Pakistan | PAK_Gopi_Chand_Bhargava | MISSING_ASSET |
| PHI | Philippines | PHI_cipriano_cid | NO_PORTRAIT_REF |
| RYU | Ryukyu | RYU_Gus_Hall | MISSING_ASSET |
| SAB | Sabah | SAB_Mustapha_Harun | NO_PORTRAIT_REF |
| SAU | Saudi Arabia | SAU_abdulaziz_ibn_saud | MISSING_ASSET |
| SJR | Sjahrir Government | SJR_Sutan_Sjahrir | NO_PORTRAIT_REF |
| SRL | Sri Lanka | SRL_Solomon_Bandaranaike | MISSING_ASSET |
| TIM | Timor | TIM_Lewis_Dyke | MISSING_ASSET |
| TPS | Trepisond | TPS_Leonidas_Iasonidis | MISSING_ASSET |

## 欧洲（2 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| AUS | Austria | AUS_Karl_Renner_1948 | NO_PORTRAIT_REF |
| GRK | Greek Kingdom | GRK_Regency_Council | NO_PORTRAIT_REF |

## 非洲（28 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| ALG | Algeria | ALG_Albert_Camus | MISSING_ASSET |
| BOT | Botswana | BOT_Sir_William_Forsyth | MISSING_ASSET |
| CMR | Cameroon | CMR_Walther_Nehring | MISSING_ASSET |
| COG | Congo | COG_Fritz_Bayerlein | MISSING_ASSET |
| DAH | Dahomey | DAH_Sourou_Migan_Apithy | MISSING_ASSET |
| ETH | Ethiopia | ETH_haile_selassie | MISSING_ASSET |
| GAB | Gabon | GAB_Leon_Mba | MISSING_ASSET |
| GAM | The Gambia | GAM_EF_Small | MISSING_ASSET |
| GNA | Guinea | GNA_Yacine_Diallo | MISSING_ASSET |
| GNB | Guinea-Bissau | GNB_Amilcar_Cabral | MISSING_ASSET |
| KNM | Kanem | KNM_Sanda_Kyarimi | MISSING_ASSET |
| LIB | Liberia | LIB_William_Tubman | MISSING_ASSET |
| LTH | Lesotho | LTH_Ntsu_Mokhehle | MISSING_ASSET |
| MAD | Madagascar | MAD_Philibert_Tsiranana | MISSING_ASSET |
| MLW | Malawi | MLW_Sir_Geoffrey_Colby | MISSING_ASSET |
| MOR | Morocco | MOR_Ahmed_Balafrej | MISSING_ASSET |
| NGA | Nigeria | NGA_Nnamdi_Azikiwe | MISSING_ASSET |
| NGR | Niger | NGR_Ahmadu_Bello | MISSING_ASSET |
| NMB | Namibia | NMB_Petrus_Imker_Hoogenhout | MISSING_ASSET |
| RCG | Republic of Congo | RCG_Jean_Felix_Tchicaya | MISSING_ASSET |
| SOM | Somalia | SOM_Sheikh_Bashir_Yussuf | MISSING_ASSET |
| SUD | Sudan | SUD_Abdallah_Khalil | MISSING_ASSET |
| SWZ | Swaziland | SWZ_Sobhuza_II | MISSING_ASSET |
| TOG | Togo | TOG_Sylvanus_Olympio | MISSING_ASSET |
| TZN | Tanzania | TZN_Hans_Jurgen_von_Arnim | MISSING_ASSET |
| WES | Western Sahara | WES_Awang_Rambli | NO_PORTRAIT_REF |
| ZAM | Zambia | ZAM_Sir_Gilbert_Rennie | MISSING_ASSET |
| ZIM | Zimbabwe | ZIM_Godfrey_Huggins | MISSING_ASSET |

## 南美（12 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| ARG | Argentina | ARG_Pedro_Pablo_Ramirez | MISSING_ASSET |
| BOL | Bolivia | BOL_Victor_Paz_Estenssoro | MISSING_ASSET |
| BRA | Brazil | BRA_Luis_Carlos_Prestes | MISSING_ASSET |
| CAY | Cayenne | CAY_Rene_Jadfard | MISSING_ASSET |
| CHL | Chile | CHL_Marmaduque_Grove | MISSING_ASSET |
| ECU | Ecuador | ECU_Galo_Plaza | MISSING_ASSET |
| GYA | Guyana | GYA_Cheddi_Jagan | MISSING_ASSET |
| PAR | Paraguay | PAR_Higinio_Morinigo | MISSING_ASSET |
| PRU | Peru | PRU_Jose_Luis_Bustamante_y_Rivero | MISSING_ASSET |
| SUR | Suriname | SUR_Johan_Pengel | MISSING_ASSET |
| URG | Uruguay | URG_Luis_Batlle_Berres | MISSING_ASSET |
| USR | Uruguay Socialist Republic | USR_Emilio_Frugoni | MISSING_ASSET |

## 北美（5 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| BAH | Bahamas | BAH_George_Beresford_Stooke | MISSING_ASSET |
| CUB | Cuba | CUB_Ramon_Grau_San_Martin | MISSING_ASSET |
| DOM | Dominican Republic | DOM_Rafael_Trujillo | MISSING_ASSET |
| HAI | Haiti | HAI_jacques_roumain | MISSING_ASSET |
| JAM | Jamaica | JAM_Norman_Manley | MISSING_ASSET |

## 大洋（3 国）
| Tag | 国家 | 领导人 cid | 状态 |
|---|---|---|---|
| NZL | New Zealand | NZL_peter_fraser | MISSING_ASSET |
| PNG | Papua New Guinea | PNG_Jack_Keith_Murray | MISSING_ASSET |

## 本批补充头像（2026-11-04）
- AFF 开国领袖 Robert Menzies 头像已补 → AFF 移出缺头像清单（现 76 国）。
- IRQ：abdullah_al_tell（顾问）、yusuf_salman_yusuf（国家领袖/顾问）已补头像。
- AFF/AST：Bob Santamaria、Robert Menzies（两 tag 均补）。
- RUS：新建角色 Yevlampy_Pastukhin 并补头像。
- JAP 三国策图标（远东委员会 / 宪法委员会 / 产别会议）已替换升级美术。
