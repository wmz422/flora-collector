"""
Flora Collector — 从 iNaturalist 补全物种分类信息
"""
import sys
import time
import sqlite3
import urllib.request
import urllib.error
import urllib.parse
import json

DB_PATH = "data/flora.db"
INAT_API = "https://api.inaturalist.org/v1"

def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FloraCollector/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                raise e

def get_taxon_with_ancestors(sci_name):
    """Search iNaturalist for a taxon, then fetch full detail with ancestors."""
    # Step 1: Search by name to get the taxon ID
    params = urllib.parse.urlencode({
        "q": sci_name,
        "rank": "species",
        "per_page": 1,
        "order": "desc",
        "order_by": "observations_count",
    })
    search_url = f"{INAT_API}/taxa?{params}"
    search_data = fetch_json(search_url)
    results = search_data.get("results", [])
    if not results:
        return None
    
    taxon_id = results[0].get("id")
    if not taxon_id:
        return None
    
    # Step 2: Fetch by ID to get full ancestors
    detail_url = f"{INAT_API}/taxa/{taxon_id}"
    detail_data = fetch_json(detail_url)
    detail_results = detail_data.get("results", [])
    if not detail_results:
        return None
    
    taxon = detail_results[0]
    
    # Build ancestor lookup
    ancestors = {}
    for a in taxon.get("ancestors", []):
        ancestors[a["rank"]] = a["name"]
    
    # Get default photo
    photo_url = ""
    dp = taxon.get("default_photo")
    if dp:
        photo_url = dp.get("medium_url") or dp.get("url", "")
    
    # Get description from Wikipedia if available
    desc = ""
    for a in taxon.get("ancestors", []):
        summary = a.get("wikipedia_summary", "")
        if summary:
            desc = summary
    
    return {
        "kingdom": ancestors.get("kingdom", ""),
        "phylum": ancestors.get("phylum", ""),
        "class_name": ancestors.get("class", ""),
        "order": ancestors.get("order", ""),
        "family": ancestors.get("family", ""),
        "genus": ancestors.get("genus", ""),
        "common_name": taxon.get("preferred_common_name", ""),
        "description": desc or "",
        "image_url": photo_url,
        "inaturalist_taxon_id": taxon_id,
    }

def main():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, scientific_name, kingdom FROM species ORDER BY id"
    ).fetchall()
    
    print(f"Total species: {len(rows)}")
    
    need_enrich = [(sid, name) for sid, name, kingdom in rows if not kingdom]
    print(f"Need enrichment: {len(need_enrich)}")
    
    enriched = 0
    errors = []
    
    for i, (sid, sci_name) in enumerate(need_enrich):
        try:
            result = get_taxon_with_ancestors(sci_name)
            time.sleep(0.5)  # Rate limiting
            if not result:
                errors.append(f"#{sid} {sci_name}: not found on iNaturalist")
                print(f"  [{i+1}/{len(need_enrich)}] #{sid} {sci_name}: ⚠ NOT FOUND")
                continue
            
            conn.execute(
                """UPDATE species SET 
                    kingdom=?, phylum=?, class_name=?, "order"=?, 
                    family=?, genus=?, common_name=?, 
                    description=CASE WHEN description='' OR description IS NULL THEN ? ELSE description END,
                    image_url=CASE WHEN (image_url='' OR image_url IS NULL) AND ?!='' THEN ? ELSE image_url END,
                    inaturalist_taxon_id=?
                WHERE id=?""",
                (
                    result["kingdom"], result["phylum"], result["class_name"],
                    result["order"], result["family"], result["genus"],
                    result["common_name"],
                    result["description"],
                    result["image_url"], result["image_url"],
                    result["inaturalist_taxon_id"],
                    sid
                )
            )
            conn.commit()
            enriched += 1
            print(f"  [{i+1}/{len(need_enrich)}] #{sid} {sci_name} → {result['kingdom']} / {result['phylum']} / {result['family']}")
        except Exception as e:
            errors.append(f"#{sid} {sci_name}: {e}")
            print(f"  [{i+1}/{len(need_enrich)}] #{sid} {sci_name}: 🔴 ERROR - {e}")
    
    print(f"\n=== Summary ===")
    print(f"Enriched: {enriched}, Errors: {len(errors)}")
    for e in errors:
        print(f"  ⚠ {e}")
    
    # Final verification
    rows = conn.execute(
        "SELECT kingdom, COUNT(*) FROM species WHERE kingdom!='' GROUP BY kingdom"
    ).fetchall()
    print(f"\nKingdom distribution:")
    for k, c in rows:
        print(f"  {k}: {c}")
    
    rows = conn.execute(
        "SELECT family, COUNT(*) FROM species WHERE family!='' GROUP BY family ORDER BY COUNT(*) DESC"
    ).fetchall()
    print(f"\nFamily distribution (top 10):")
    for f, c in rows[:10]:
        print(f"  {f}: {c}")
    
    conn.close()

if __name__ == "__main__":
    main()
