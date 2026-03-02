#!/usr/bin/env python3
import re
import os

WORKDIR = '/home/ubuntu/.openclaw/workspace/aiworkstage-hp'

# ===== A. Premium card gold styling =====
service_files = [
    'service-hp.html', 'service-lp.html', 'service-seo.html',
    'service-ai-agent.html', 'service-chatbot.html', 'service-blog.html',
    'service-line.html', 'service-notion.html', 'service-minutes.html',
    'service-sns-link.html', 'service-hp-check.html', 'service-bbs.html'
]

premium_style = 'style="background: linear-gradient(145deg, #0a0a0f, #1a1205); border: 1px solid #b8860b; box-shadow: 0 8px 32px rgba(184,134,11,0.2);"'
diamond_div = '<div style="text-align:center;font-size:1.5rem;margin-bottom:8px;">💎</div>\n          '

for fname in service_files:
    fpath = os.path.join(WORKDIR, fname)
    if not os.path.exists(fpath):
        print(f"SKIP (not found): {fname}")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all occurrences of '<div class="price-card ">' (the 3rd one = premium)
    # Pattern: find the last <div class="price-card "> (no featured)
    # Strategy: find all non-featured price-cards and apply to the last one
    
    marker = '<div class="price-card ">'
    parts = content.split(marker)
    
    if len(parts) < 3:
        print(f"WARNING: {fname} has less than 2 non-featured price-cards, found {len(parts)-1}")
        continue
    
    # The last occurrence is the premium card (parts[-1])
    # Rebuild: join all but last, then add styled premium card
    # parts[0] + marker + parts[1] + ... + marker(styled) + parts[-1]
    
    # Apply style to the LAST occurrence
    new_marker = f'<div class="price-card " {premium_style}>'
    
    # Join all parts back, replacing only the last marker
    rebuilt = marker.join(parts[:-1]) + new_marker + parts[-1]
    
    # Now add diamond emoji before .plan-name in the premium card section
    # The premium card is everything after the last new_marker
    idx = rebuilt.rfind(new_marker)
    before_premium = rebuilt[:idx + len(new_marker)]
    premium_section = rebuilt[idx + len(new_marker):]
    
    # Add diamond before first <div class="plan-name"> in premium section
    premium_section = premium_section.replace(
        '<div class="plan-name">',
        diamond_div + '<div class="plan-name">',
        1
    )
    
    # Gold color for plan-price in premium section
    # Find and update plan-price style in premium section
    # Replace first occurrence of <div class="plan-price"> with gold color inline
    premium_section = premium_section.replace(
        '<div class="plan-price">',
        '<div class="plan-price" style="color:#d4a017;">',
        1
    )
    
    content = before_premium + premium_section
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"A: Updated premium card in {fname}")

# ===== B. service-hp-check.html specific changes =====
fpath = os.path.join(WORKDIR, 'service-hp-check.html')
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Page title
content = content.replace('既存HP診断・修正', '既存HP診断（無料）・修正')

# 2. Basic card changes - find the first price-card (basic)
# Find first price-card block
first_card_start = content.find('<div class="price-card">')
if first_card_start == -1:
    first_card_start = content.find('<div class="price-card ">')
    # Actually the basic card might be the first one - check structure
    print("Checking hp-check structure...")

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

print("B: Updated page title in service-hp-check.html")

# Let's read the file again to do more targeted edits
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

print("service-hp-check.html price-card occurrences:")
for i, m in enumerate(re.finditer(r'<div class="price-card[^"]*">', content)):
    print(f"  [{i}] pos={m.start()}: {m.group()}")

# ===== C. index.html - move HP check card to first position =====
fpath = os.path.join(WORKDIR, 'index.html')
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the hp-check service card
# Look for the card containing service-hp-check.html
hp_check_pattern = re.compile(
    r'(<div class="service-card[^"]*">(?:(?!</div>).|\n)*?service-hp-check\.html(?:(?!</div>).|\n)*?</div>\s*</div>)',
    re.DOTALL
)
# Try a simpler approach - find the card block
# Service cards are usually <a href="..."> or <div> wrappers

print("Searching for hp-check in index.html...")
idx = content.find('service-hp-check.html')
if idx != -1:
    print(f"  Found at pos {idx}")
    print(f"  Context: {content[max(0,idx-200):idx+200]}")
else:
    print("  NOT FOUND")

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)
