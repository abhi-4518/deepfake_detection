import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('deepfaker.db')
cursor = conn.cursor()

# Get all analyses with results
query = """
SELECT 
    a.id,
    u.username,
    a.upload_method,
    a.image_filename,
    a.created_at,
    ar.verdict,
    ar.prob_ai,
    ar.prob_real,
    ar.confidence,
    ar.source_model
FROM analyses a
JOIN users u ON a.user_id = u.id
LEFT JOIN analysis_results ar ON a.id = ar.analysis_id
ORDER BY a.created_at DESC
"""

cursor.execute(query)
analyses = cursor.fetchall()

print("=" * 120)
print(f"{'ID':<5} {'User':<15} {'Method':<12} {'Filename':<25} {'Verdict':<12} {'AI%':<8} {'Real%':<8} {'Conf%':<8} {'Model':<20}")
print("=" * 120)

for row in analyses:
    analysis_id, username, method, filename, created_at, verdict, prob_ai, prob_real, confidence, source = row
    
    ai_pct = f"{prob_ai*100:.1f}%" if prob_ai else "N/A"
    real_pct = f"{prob_real*100:.1f}%" if prob_real else "N/A"
    conf_pct = f"{confidence*100:.1f}%" if confidence else "N/A"
    
    print(f"{analysis_id:<5} {username:<15} {method:<12} {filename[:24]:<25} {verdict:<12} {ai_pct:<8} {real_pct:<8} {conf_pct:<8} {source[:19]:<20}")

print("=" * 120)
print(f"\nTotal Analyses: {len(analyses)}")

conn.close()
