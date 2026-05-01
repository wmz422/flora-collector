"""
Flora Collector — iPlant 植物智爬虫
从 https://www.iplant.cn/info/{sci_name} 提取中文名+描述+分类

用法:
  python3 scripts/scrape_iplant.py          # 补全所有缺中文名/描述的物种
  python3 scripts/scrape_iplant.py --all    # 全部重新爬
"""
import sys, os, re, time, json
from html.parser import HTMLParser
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['FLORA_DB'] = os.path.join(os.path.dirname(__file__), '..', 'data', 'flora.db')

from src.flora_collector.models import get_session, Species, GlobalEncyclopediaEntry

BASE_URL = "https://www.iplant.cn/info/"

def fetch_page(sci_name):
    """获取 iPlant 物种页面 HTML"""
    encoded = urllib.parse.quote(sci_name)
    url = f"{BASE_URL}{encoded}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            return html
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # 页面不存在
        raise
    except Exception as e:
        print(f"  ⚠ Fetch error: {e}")
        return None


def extract_chinese_name(html):
    """提取中文名，位于 <div class="zhongwenming"> 后的 <span>"""
    # Pattern 1: 月季花(yuè jì huā) 格式
    m = re.search(r'<div[^>]*class="[^"]*zhongwenming[^"]*"[^>]*>([^<]+)', html)
    if m:
        raw = m.group(1).strip()
        # 去掉拼音部分
        raw = re.sub(r'\([^)]*\)', '', raw).strip()
        return raw
    return None


def extract_description(html):
    """提取微百科描述（第一段植物描述）"""
    # 查找微百科区域后的描述文本
    m = re.search(
        r'<div[^>]*class="[^"]*百科简介[^"]*"[^>]*>'
        r'|<div[^>]*class="[^"]*frpscontent[^"]*"[^>]*>'
        r'|<div class="view[^"]*"[^>]*>',
        html
    )
    if not m:
        # 更简单的策略：找 "常绿" "一年生" "草本" 等开头的段落
        patterns = [
            r'(常绿[^。]+。[^。]*(?:[。]|$))',
            r'(一年生[^。]+。[^。]*(?:[。]|$))',
            r'(多年生[^。]+。[^。]*(?:[。]|$))',
            r'(落叶[^。]+。[^。]*(?:[。]|$))',
            r'(直立[^。]+。[^。]*(?:[。]|$))',
            r'(藤本[^。]+。[^。]*(?:[。]|$))',
            r'(灌木[^。]+。[^。]*(?:[。]|$))',
            r'(乔木[^。]+。[^。]*(?:[。]|$))',
        ]
        for pat in patterns:
            m = re.search(pat, html)
            if m:
                return m.group(1).strip()
        return None

    # 如果找到了区域，提取文本
    return None


def extract_simple_desc(html):
    """更简单的描述提取：找第一个包含中文描述的大段文本"""
    # 查找包含形态描述的关键字段落
    lines = re.split(r'<[^>]+>', html)
    desc_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 包含植物描述关键词的中文句子
        if any(kw in line for kw in ['叶', '花', '茎', '果', '高', '生']):
            if len(line) > 20 and re.search(r'[\u4e00-\u9fff]', line):
                # 清理多余空格和符号
                clean = re.sub(r'\s+', '', line)
                if len(clean) > 30:
                    desc_lines.append(clean)

    if desc_lines:
        # 取最长的那个描述段落
        longest = max(desc_lines, key=len)
        # 截取前 200 字
        return longest[:300]
    return None


def extract_taxonomy(html):
    """提取分类面包屑"""
    # 查找 "<link> 植物智 >> <link> 被子 >> <link> 蔷薇科 >> <link> 蔷薇属"
    pattern = r'植物智\s*>>\s*([^>]+>)?([^>]+>)?([^>]+>)?([^>]+>)?([^>]+>)?\s*<span'
    m = re.search(r'<!--当前位置开始-->.*?植物智(.*?)<span', html, re.DOTALL)
    if m:
        bread = m.group(1)
        parts = re.findall(r'>([^<]+)<', bread)
        parts = [p.strip() for p in parts if p.strip()]
        return parts
    return []


def scrape_species(sci_name):
    """爬取一个物种的数据"""
    html = fetch_page(sci_name)
    if html is None:
        return {"chinese_name": None, "description": None, "taxonomy": [], "found": False}

    cn = extract_chinese_name(html)
    desc = extract_simple_desc(html)
    tax = extract_taxonomy(html)

    # 清理描述
    if desc:
        desc = re.sub(r'\s+', '', desc)
        # 找第一个句号之后的完整段落
        if len(desc) > 300:
            desc = desc[:300]

    return {
        "chinese_name": cn,
        "description": desc,
        "taxonomy": tax,
        "found": True,
        "url": f"{BASE_URL}{urllib.parse.quote(sci_name)}",
    }


def update_database(species_id, data):
    """更新数据库"""
    session = get_session()
    try:
        species = session.query(Species).filter_by(id=species_id).first()
        if not species:
            return

        updated = False
        if data.get("chinese_name") and not species.chinese_name:
            species.chinese_name = data["chinese_name"]
            species.name_source = "iplant"
            updated = True
        if data.get("description") and not species.description:
            species.description = data["description"]
            species.desc_source = "iplant"
            updated = True

        if updated:
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"  ⚠ DB update error: {e}")
        return False
    finally:
        session.close()


def main():
    session = get_session()

    # 找出需要爬的物种
    all_flag = '--all' in sys.argv
    if all_flag:
        species = session.query(Species).order_by(Species.id).all()
        print(f"🔁 全部重新爬取: {len(species)} 种")
    else:
        # 只爬缺中文名或描述的
        species = session.query(Species).filter(
            (Species.chinese_name == '') | (Species.description == '')
        ).order_by(Species.id).all()
        print(f"🎯 补缺: {len(species)} 种缺少中文名或描述")

    session.close()

    if not species:
        print("✅ 所有物种已有中文名和描述，无需爬取")
        return

    success = 0
    fail = 0
    skipped = 0

    for i, sp in enumerate(species):
        sci = sp.scientific_name
        print(f"  [{i+1}/{len(species)}] {sci}...", end=" ")

        data = scrape_species(sci)

        if not data["found"]:
            print(f"❌ 404")
            fail += 1
        elif data["chinese_name"] or data["description"]:
            updated = update_database(sp.id, data)
            if updated:
                cn = data.get("chinese_name", "") or "?"
                desc = "✅" if data.get("description") else "⛔"
                print(f"✅ cn={cn} desc={desc}")
                success += 1
            else:
                print(f"⏭ 已有数据")
                skipped += 1
        else:
            print(f"⛔ 未提取到数据")
            fail += 1

        time.sleep(1.0)  # 礼貌延迟

    print(f"\n{'='*40}")
    print(f"完成: ✅ {success} 成功, ⏭ {skipped} 跳过, ❌ {fail} 失败")


if __name__ == "__main__":
    main()
