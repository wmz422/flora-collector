"""
Flora Collector — iPlant 植物智爬虫 (Playwright)
"""
import sys, os, re, time, json, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['FLORA_DB'] = os.path.join(os.path.dirname(__file__), '..', 'data', 'flora.db')

from playwright.sync_api import sync_playwright
from src.flora_collector.models import get_session, Species

BASE_URL = "https://www.iplant.cn/info/"


def scrape_page(page, sci_name):
    """爬一个物种，返回 {cn, desc, common_names, found}"""
    url = f"{BASE_URL}{urllib.parse.quote(sci_name)}"
    text = ""
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        time.sleep(1.5)
        text = page.inner_text("body")
    except Exception as e:
        return {"cn": None, "desc": None, "found": False, "error": str(e)}

    lines = text.split("\n")
    result = {"cn": None, "desc": None, "common_names": [], "found": False}

    # 1) 中文名: line like "月季花(yuè jì huā)"
    for line in lines:
        line = line.strip()
        # Match Chinese chars followed by (pinyin)
        if re.match(r'^[\u4e00-\u9fff\u3400-\u4dbf]+\([a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ\s]+\)$', line):
            result["cn"] = re.match(r'^([\u4e00-\u9fff\u3400-\u4dbf]+)', line).group(1)
            break

    # 2) 俗名
    for line in lines:
        if "俗名：" in line:
            parts = line.split("俗名：")
            if len(parts) > 1:
                result["common_names"] = [n.strip() for n in parts[1].split("、") if n.strip()]
            break

    # 3) 描述: first line containing botanical description keywords
    desc_keywords = ["常绿", "落叶", "一年生", "多年生", "草本", "灌木", "乔木", "藤本",
                     "直立", "攀援", "匍匐", "水生", "陆生"]
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in desc_keywords) and len(line) > 40:
            # Clean up: remove leading "separator" markers
            clean = re.sub(r'^[\s\-—•·]+', '', line)
            # Take up to 500 chars
            result["desc"] = clean[:500]
            break

    # Fallback: longest Chinese paragraph
    if not result["desc"]:
        paras = [l.strip() for l in lines
                 if len(l.strip()) > 60 and re.search(r'[\u4e00-\u9fff]', l)
                 and "iPlant" not in l and "京ICP" not in l]
        if paras:
            result["desc"] = max(paras, key=len)[:500]

    result["found"] = bool(result["cn"])
    return result


def main():
    session = get_session()
    all_flag = "--all" in sys.argv
    test_flag = "--test" in sys.argv

    if test_flag:
        # 只测试前 5 个
        species = session.query(Species).order_by(Species.id).limit(5).all()
        print(f"🧪 测试模式: {len(species)} 种")
    elif all_flag:
        species = session.query(Species).order_by(Species.id).all()
        print(f"🔁 全部: {len(species)} 种")
    else:
        species = session.query(Species).filter(
            (Species.chinese_name == '') | (Species.description == '')
        ).order_by(Species.id).all()
        print(f"🎯 补缺: {len(species)} 种")

    session.close()

    if not species:
        print("✅ 无需爬取")
        return

    success = 0
    fail = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        for i, sp in enumerate(species):
            sci = sp.scientific_name
            print(f"  [{i+1}/{len(species)}] {sci}...", end=" ", flush=True)

            data = scrape_page(page, sci)

            if not data["found"]:
                err_msg = "no data"
                if data.get("desc"):
                    err_msg = "cn=None"
                print(f"❌ {err_msg}")
                fail += 1
                continue

            # Update DB
            sess = get_session()
            try:
                db_sp = sess.query(Species).filter_by(id=sp.id).first()
                updated = False
                if db_sp:
                    if data.get("cn") and (not db_sp.chinese_name or db_sp.name_source in ("", "inat")):
                        db_sp.chinese_name = data["cn"]
                        db_sp.name_source = "iplant"
                        updated = True
                    if data.get("desc") and (not db_sp.description or db_sp.desc_source in ("", "inat", "wikipedia")):
                        db_sp.description = data["desc"]
                        db_sp.desc_source = "iplant"
                        updated = True
                if updated:
                    sess.commit()
                    print(f"✅ cn={data['cn']} desc={'✅' if data['desc'] else '⛔'}")
                    success += 1
                else:
                    print(f"⏭ 已有更好数据")
            except Exception as e:
                sess.rollback()
                print(f"⚠ DB: {e}")
                fail += 1
            finally:
                sess.close()

        page.close()
        browser.close()

    print(f"\n{'='*40}")
    print(f"完成: ✅ {success}, ❌ {fail}")


if __name__ == "__main__":
    main()
