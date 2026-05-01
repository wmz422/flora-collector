"""
Continue enriching remaining species
"""
import sqlite3
import time
import urllib.request
import json

conn = sqlite3.connect('data/flora.db')
remaining = conn.execute(
    "SELECT id, scientific_name FROM species WHERE kingdom='' AND id NOT IN (1,6) ORDER BY id"
).fetchall()
print(f'Continuing with {len(remaining)} species')

INAT_API = 'https://api.inaturalist.org/v1'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'FloraCollector/1.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())

enriched = 0
for i, (sid, sci_name) in enumerate(remaining):
    try:
        import urllib.parse
        params = urllib.parse.urlencode({
            'q': sci_name, 'rank': 'species',
            'per_page': 1, 'order': 'desc',
            'order_by': 'observations_count'
        })
        search = fetch(f'{INAT_API}/taxa?{params}')
        results = search.get('results', [])
        if not results:
            print(f'  [{i+1}/{len(remaining)}] #{sid} {sci_name}: NOT FOUND')
            continue
        taxon_id = results[0]['id']
        
        detail = fetch(f'{INAT_API}/taxa/{taxon_id}')
        dr = detail['results'][0]
        ancestors = {}
        for a in dr.get('ancestors', []):
            ancestors[a['rank']] = a['name']
        
        photo = ''
        dp = dr.get('default_photo')
        if dp:
            photo = dp.get('medium_url') or dp.get('url', '')
        
        desc = ''
        for a in dr.get('ancestors', []):
            if a.get('wikipedia_summary'):
                desc = a['wikipedia_summary']
                break
        
        conn.execute(
            """UPDATE species SET 
                kingdom=?, phylum=?, class_name=?, "order"=?, 
                family=?, genus=?, common_name=?,
                description=CASE WHEN description='' OR description IS NULL THEN ? ELSE description END,
                image_url=CASE WHEN (image_url='' OR image_url IS NULL) AND ?!='' THEN ? ELSE image_url END,
                inaturalist_taxon_id=?
            WHERE id=?""",
            (
                ancestors.get('kingdom', ''), ancestors.get('phylum', ''),
                ancestors.get('class', ''), ancestors.get('order', ''),
                ancestors.get('family', ''), ancestors.get('genus', ''),
                dr.get('preferred_common_name', ''),
                desc,
                photo, photo,
                taxon_id,
                sid
            )
        )
        conn.commit()
        enriched += 1
        fam = ancestors.get('family', '?')
        print(f"  [{i+1}/{len(remaining)}] #{sid} {sci_name} -> {fam}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  [{i+1}/{len(remaining)}] #{sid} {sci_name}: ERROR {e}")

print(f"Done! Enriched {enriched} more")
conn.close()
