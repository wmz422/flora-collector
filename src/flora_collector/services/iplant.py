"""
Flora Collector — iPlant 中国植物志数据源

从 iPlant（中国植物志）获取中文名、描述和完整分类链。
使用 iPlant 内部 AJAX API（plantinfo.ashx / getspinfos.ashx），无需 Playwright。

用法:
    data = fetch_iplant_data("Rosa chinensis")
    # → {chinese_name, description, name_source, desc_source, image_url, iplant_taxonomy, ...}
"""
import re
import json
import base64
import logging
import urllib.request
import urllib.parse
from typing import Optional

logger = logging.getLogger(__name__)

IPLANT_BASE = "https://www.iplant.cn/info/"
IPLANT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
AJAX_HEADERS = {
    **IPLANT_HEADERS,
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.iplant.cn/",
}

# iPlant classsys 格式: [物种, 属, 科, 目, 纲, 门, 界]（从低到高）
# 解析时 reversed → [界, 门, 纲, 目, 科, 属] 取前6
CLASSYS_KEY_ORDER = ["kingdom", "phylum", "class_name", "order", "family", "genus"]


def _fetch(url: str, headers: dict, timeout: int = 10) -> Optional[str]:
    """通用 HTTP GET 请求，返回文本"""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("gbk", errors="ignore")
    except Exception as e:
        logger.debug(f"iPlant fetch failed: {url[:60]} — {e}")
        return None


def _parse_classsys(classsys_raw: str) -> tuple:
    """解析 iPlant classsys 字符串 → 分类字典

    classsys[0] 格式按 * 分割，从低(物种)到高(界)排列。
    reversed 后取前6个层级：界 → 门 → 纲 → 目 → 科 → 属

    Returns:
        (parsed_tax_dict, cn_names_dict)
    """
    levels = classsys_raw.split("*")
    parsed = {}
    cn_names = {}

    for i, level in enumerate(reversed(levels)):
        if i >= len(CLASSYS_KEY_ORDER):
            break
        level = level.strip()
        if not level:
            continue
        clean = re.sub(r"<[^>]+>", "", level).strip()
        parts = clean.split()
        if len(parts) >= 2:
            # "植物界 Plantae" → latin = Plantae
            latin = parts[-1] if parts[-1][0].isupper() else (
                parts[-2] if len(parts) >= 2 else ""
            )
            chinese = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
        elif parts:
            latin = parts[0]
            chinese = ""
        else:
            continue

        key = CLASSYS_KEY_ORDER[i]
        # Angiospermae 是 iPlant 在被子植物中插入的非正式层级（介于界和纲之间），
        # 不是真正的门。跳过它，让下游 fallback 填"维管植物门"或"被子植物门"
        if key == "phylum" and latin == "Angiospermae":
            continue
        if latin and latin[0].isupper():
            parsed[key] = latin
            cn_names[key] = chinese

    return parsed, cn_names


def fetch_iplant_data(scientific_name: str) -> Optional[dict]:
    """从 iPlant 获取中文名、描述和分类数据。

    流程:
        1. 请求物种页面 → 提取 spno（物种ID）+ 中文名
        2. 调 plantinfo.ashx → 获取描述（优先形态特征）
        3. 调 getspinfos.ashx → 获取完整分类链

    返回:
        {
            chinese_name, description, name_source, desc_source, image_url,
            iplant_taxonomy: {kingdom, phylum, class_name, order, family, genus},
            kingdom_cn, phylum_cn, class_name_cn, order_cn, family_cn, genus_cn,
        }
        失败返回 None。
    """
    # 清理学名：去掉作者名、保留属名+种加词
    clean = re.sub(r"\([^)]*\)", "", scientific_name).strip()
    parts = clean.split()
    search_name = " ".join(parts[:2]) if len(parts) >= 2 else (
        parts[0] if parts else scientific_name
    )

    url = f"{IPLANT_BASE}{urllib.parse.quote(search_name)}"

    # 1. 获取页面 HTML → 提取 spno（物种ID）+ 中文名
    html = _fetch(url, IPLANT_HEADERS)
    if not html:
        return None

    result = {}

    m = re.search(r'var\s+spcname\s*=\s*"([^"]+)"', html)
    if not m:
        return None
    result["chinese_name"] = m.group(1)

    spno_m = re.search(r"spno\s*=\s*['\"]?(\d+)['\"]?", html)
    if not spno_m:
        return result
    spno = spno_m.group(1)

    # 2. 获取描述
    desc_url = f"https://www.iplant.cn/ashx/plantinfo.ashx?spid={spno}&type=descall"
    desc_resp = _fetch(desc_url, AJAX_HEADERS)
    if desc_resp:
        try:
            api_data = json.loads(desc_resp)
            spdesc = api_data.get("spdesc", [])
            description_parts = []

            for tid in [11, 1]:  # 优先形态特征(tid=11)，其次物种名片(tid=1)
                for section in spdesc:
                    if section.get("tid") == tid:
                        for dl in section.get("desclist", []):
                            b64 = dl.get("desc", "")
                            if b64:
                                try:
                                    decoded = base64.b64decode(b64).decode("utf-8").strip()
                                    if decoded:
                                        description_parts.append(decoded)
                                except Exception:
                                    pass
                        if description_parts:
                            break
                if description_parts:
                    break

            result["description"] = "".join(description_parts)[:500] if description_parts else ""
        except (json.JSONDecodeError, Exception):
            result["description"] = ""
    else:
        result["description"] = ""

    result["name_source"] = "iplant"
    result["desc_source"] = "iplant" if result.get("description") else ""
    result["image_url"] = ""

    # 3. 获取分类数据
    try:
        tax_url = f"https://www.iplant.cn/ashx/getspinfos.ashx?spid={spno}&type=classsys"
        tr = urllib.request.Request(tax_url, headers={**IPLANT_HEADERS, "X-Requested-With": "XMLHttpRequest"})
        tr.method = "POST"
        with urllib.request.urlopen(tr, timeout=10) as tresp:
            tax_data = json.loads(tresp.read().decode("utf-8"))

        classsys = tax_data.get("classsys", [])
        if classsys:
            parsed_tax, cn_names = _parse_classsys(classsys[0])
            result["iplant_taxonomy"] = parsed_tax
            for k, v in cn_names.items():
                result[f"{k}_cn"] = v
    except Exception as e:
        logger.debug(f"iPlant taxonomy fetch failed: {e}")

    return result
