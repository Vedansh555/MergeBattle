"""
build_youtube.py
================
Updates YouTube Playables build for Merge Battle with latest gameplay:
- Keeps YouTube Playables SDK intact (<script src="https://www.youtube.com/game_api/v1"></script>)
- Keeps YouTube PF platform adapter intact
- Keeps YouTube ad triggers intact (every 4 waves / every 3 losses)
- Sets PAL card cost to 1 elixir (PALCOST=1)
- Sets Bomb cost to 2 elixir (c:2)
- Sets Heart cost to 4 elixir (c:4)
- Wave reset on next wave (both win and loss reset to 1 Green Pal and 10 Elixir)
- Removes revive() from waveWon()
- Pal lifetime formula palLife(lv) = 15 + lv * 5 (Lv 1 = 20s, Lv 2 = 25s, Lv 3 = 30s)
- Full health & fresh lifetime timer refresh on merge
- Life timer bar & 'Expired!' float indicator
- Wave 1 always starts with 1 Green Pal
- Start Wave button centered in arena
- Cards locked during prep with toast
- Updates root index.html and merge-battle-youtube.zip
- Creates builds/youtube/ folder with index.html and merge-battle-youtube.zip
"""

import zipfile, os

SRC = r'c:\Users\Vedansh\Documents\DoodleShield\merge-battle\index.html'
OUT_ZIP = r'c:\Users\Vedansh\Documents\DoodleShield\merge-battle\merge-battle-youtube.zip'
YT_DIR = r'c:\Users\Vedansh\Documents\DoodleShield\merge-battle\builds\youtube'

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Ensure YouTube SDK and adapter are intact ──────────────────────────────
assert '<script src="https://www.youtube.com/game_api/v1"></script>' in html, "YouTube SDK not found in head"
assert "const PF={name:'youtube'" in html, "YouTube PF adapter not found"
assert "wavesSinceAd>=4" in html, "YouTube ad frequency rule missing"
assert "losses%3===0" in html, "YouTube loss ad frequency rule missing"

# ── 2. PALCOST = 1 ────────────────────────────────────────────────────────────
for old_pal in [
    "const W=360,INK='#3a3550',MAXLV=12,MAXU=40,MAXH=5,PALCOST=3;",
    "const W=360,INK='#3a3550',MAXLV=12,MAXU=40,MAXH=5,PALCOST=2;"
]:
    if old_pal in html:
        html = html.replace(old_pal, "const W=360,INK='#3a3550',MAXLV=12,MAXU=40,MAXH=5,PALCOST=1;", 1)
assert "PALCOST=1" in html, "PALCOST=1 not set"

# ── 3. CARDS elixir costs (PAL=1, BOMB=2, HEART=4, FREEZE=4, ZAP=4) ───────────
OLD_CARDS = "const CARDS={pal:{n:'PAL',c:PALCOST,col:'#5ccfb4'},bomb:{n:'BOMB',c:3,col:'#ff8a5c'},freeze:{n:'FREEZE',c:4,col:'#6ec6f2'},heart:{n:'HEART',c:5,col:'#ff7a9a'},zap:{n:'ZAP',c:4,col:'#f2c230'}};"
NEW_CARDS = "const CARDS={pal:{n:'PAL',c:PALCOST,col:'#5ccfb4'},bomb:{n:'BOMB',c:2,col:'#ff8a5c'},freeze:{n:'FREEZE',c:4,col:'#6ec6f2'},heart:{n:'HEART',c:4,col:'#ff7a9a'},zap:{n:'ZAP',c:4,col:'#f2c230'}};"
if OLD_CARDS in html:
    html = html.replace(OLD_CARDS, NEW_CARDS, 1)
assert "bomb:{n:'BOMB',c:2" in html, "Bomb cost 2 not set"
assert "heart:{n:'HEART',c:4" in html, "Heart cost 4 not set"

# ── 4. Remove revive() from waveWon() ─────────────────────────────────────────
OLD_WAVEWON = "function waveWon(){revive();stars=hearts>=5?3:hearts>=3?2:1;"
NEW_WAVEWON = "function waveWon(){stars=hearts>=5?3:hearts>=3?2:1;"
if OLD_WAVEWON in html:
    html = html.replace(OLD_WAVEWON, NEW_WAVEWON, 1)
assert "function waveWon(){stars=" in html, "waveWon revive removal not applied"

# ── 5. Wave reset on won: resetUnits(), fallen=[], energy=10 ─────────────────
OLD_NEXT_WON = "if(phase==='won'){if(wavesSinceAd>=4){wavesSinceAd=0;showAd('level_completed')}phase='prep';idle=0;energy=Math.max(energy,5);return}"
NEW_NEXT_WON = "if(phase==='won'){if(wavesSinceAd>=4){wavesSinceAd=0;showAd('level_completed')}resetUnits();fallen=[];phase='prep';idle=0;energy=10;save();return}"
if OLD_NEXT_WON in html:
    html = html.replace(OLD_NEXT_WON, NEW_NEXT_WON, 1)
assert "resetUnits();fallen=[];phase='prep';idle=0;energy=10;save();return" in html, "Wave reset on won not set"

# ── 6. Retry reset on lost: keep intact ───────────────────────────────────────
OLD_NEXT_LOST = "if(phase==='lost'){if(losses%3===0)showAd('game_over');phase='prep';idle=0;energy=Math.max(energy,5);return}"
NEW_NEXT_LOST = "if(phase==='lost'){if(losses%3===0)showAd('game_over');resetUnits();fallen=[];phase='prep';idle=0;energy=10;save();return}"
if OLD_NEXT_LOST in html:
    html = html.replace(OLD_NEXT_LOST, NEW_NEXT_LOST, 1)

OLD_WAVELOST = "function waveLost(){revive();phase='lost';"
NEW_WAVELOST = "function waveLost(){phase='lost';"
if OLD_WAVELOST in html:
    html = html.replace(OLD_WAVELOST, NEW_WAVELOST, 1)

# ── 7. Lock cards during prep: toast('Press Start Wave to begin!') ─────────────
OLD_USE_PAL = "if(k==='pal'){let pt={x:tx,y:ty};if(auto)pt=freeSpot();if(placePal(pt.x,pt.y)){cardsSeen=true;cardPulse[0]=.3}return}"
NEW_USE_PAL = (
    "if(k==='pal'){\n"
    "    if(phase==='prep'){toast('Press Start Wave to begin!','#5ccfb4');return}\n"
    "    let pt={x:tx,y:ty};if(auto)pt=freeSpot();if(placePal(pt.x,pt.y)){cardsSeen=true;cardPulse[0]=.3}return\n"
    "  }"
)
if OLD_USE_PAL in html:
    html = html.replace(OLD_USE_PAL, NEW_USE_PAL, 1)

OLD_CARD_DRAG = "if(phase==='prep'||phase==='fight'){for(let i=0;i<4;i++)if(inR(p,CX(i),btnY,CW,72)){cardDrag={i,px:p.x,py:p.y,sx:p.x,sy:p.y};try{cv.setPointerCapture(e.pointerId)}catch(_){}sfx.card();return}}"
NEW_CARD_DRAG = (
    "if(phase==='prep'||phase==='fight'){\n"
    "    for(let i=0;i<4;i++)if(inR(p,CX(i),btnY,CW,72)){\n"
    "      if(phase==='prep'){toast('Press Start Wave to begin!','#5ccfb4');sfx.click();return}\n"
    "      cardDrag={i,px:p.x,py:p.y,sx:p.x,sy:p.y};try{cv.setPointerCapture(e.pointerId)}catch(_){}sfx.card();return\n"
    "    }\n"
    "  }"
)
if OLD_CARD_DRAG in html:
    html = html.replace(OLD_CARD_DRAG, NEW_CARD_DRAG, 1)

# ── 8. Start Wave button in center of arena (waveY = topY + (baseY-topY)*.44) ──
OLD_DRAW_BTN = "if(ts<0||ts===2){x.save();x.translate(180,prepY)"
NEW_DRAW_BTN = (
    "if(phase==='prep'){"
    "const waveY=topY+(baseY-topY)*.44;"
    "x.save();"
    "x.globalAlpha=.18+.12*Math.sin(t*4);"
    "x.fillStyle='#ff8fb8';"
    "x.beginPath();x.ellipse(180,waveY,148,52,0,0,6.28);x.fill();"
    "x.globalAlpha=1;"
    "const arrY=waveY-60+Math.sin(t*5)*6;"
    "x.fillStyle='#ee5b92';"
    "x.beginPath();x.moveTo(180,arrY+18);x.lineTo(166,arrY);x.lineTo(194,arrY);x.closePath();x.fill();"
    "x.restore();"
    "x.save();x.translate(180,waveY)"
)
if OLD_DRAW_BTN in html:
    html = html.replace(OLD_DRAW_BTN, NEW_DRAW_BTN, 1)

OLD_CLICK_BTN = "if(phase==='prep'&&(tutStep()<0||tutStep()===2)&&inR(p,75,prepY-30,210,60)){sfx.click();startWave();return}"
NEW_CLICK_BTN = (
    "if(phase==='prep'){"
    "const _wy=topY+(baseY-topY)*.44;"
    "if(inR(p,62,_wy-37,236,74)){sfx.click();startWave();return}}"
)
if OLD_CLICK_BTN in html:
    html = html.replace(OLD_CLICK_BTN, NEW_CLICK_BTN, 1)

# ── 9. Pal Lifetime Decay & Merge Refresh ─────────────────────────────────────
OLD_MK = "const palHp=lv=>36*Math.pow(1.5,lv-1);\nconst mk=(px,dy,lv)=>({x:px,dy,y:0,lv,cd:Math.random()*.5,rec:0,pop:0,ph:Math.random()*6,hp:palHp(lv),mhp:palHp(lv),hurt:0});"
NEW_MK = "const palHp=lv=>36*Math.pow(1.5,lv-1);\nconst palLife=lv=>15+lv*5;\nconst mk=(px,dy,lv)=>({x:px,dy,y:0,lv,cd:Math.random()*.5,rec:0,pop:0,ph:Math.random()*6,hp:palHp(lv),mhp:palHp(lv),hurt:0,life:palLife(lv),maxLife:palLife(lv),expired:false});"
if OLD_MK in html:
    html = html.replace(OLD_MK, NEW_MK, 1)

OLD_START_WAVE = "function startWave(){trimUnits();hearts=MAXH;for(const u of units)u.hp=u.mhp;enemies=[];"
NEW_START_WAVE = "function startWave(){trimUnits();hearts=MAXH;for(const u of units){u.hp=u.mhp;u.life=palLife(u.lv);u.maxLife=palLife(u.lv);u.expired=false;}enemies=[];"
if OLD_START_WAVE in html:
    html = html.replace(OLD_START_WAVE, NEW_START_WAVE, 1)

OLD_FIGHT_UNITS = "for(const u of units){u.cd-=dt;if(u.cd>0||!enemies.length)continue;let tg=null;"
NEW_FIGHT_UNITS = "for(const u of units){if(u.life>0){u.life-=dt;if(u.life<=0){u.hp=0;u.expired=true}}u.cd-=dt;if(u.cd>0||!enemies.length)continue;let tg=null;"
if "u.life-=dt" not in html and OLD_FIGHT_UNITS in html:
    html = html.replace(OLD_FIGHT_UNITS, NEW_FIGHT_UNITS, 1)

OLD_FLOAT_DOWN = "floatT('Pal down!',u.x,u.y-24,'#c0392b');"
NEW_FLOAT_DOWN = "floatT(u.expired?'Expired!':'Pal down!',u.x,u.y-24,'#c0392b');"
if "u.expired" not in html and OLD_FLOAT_DOWN in html:
    html = html.replace(OLD_FLOAT_DOWN, NEW_FLOAT_DOWN, 1)

OLD_MERGE_HP = "tg.lv++;tg.mhp=palHp(tg.lv);tg.hp=tg.mhp;tg.pop=.35;"
NEW_MERGE_HP = "tg.lv++;tg.mhp=palHp(tg.lv);tg.hp=tg.mhp;tg.maxLife=palLife(tg.lv);tg.life=tg.maxLife;tg.expired=false;tg.pop=.35;"
if "tg.maxLife" not in html and OLD_MERGE_HP in html:
    html = html.replace(OLD_MERGE_HP, NEW_MERGE_HP, 1)

OLD_DRAW_HP = "if(u.hp<u.mhp){const f=Math.max(0,u.hp/u.mhp);rr(u.x-20,u.y+27,40,6,3,'rgba(0,0,0,.3)');rr(u.x-20,u.y+27,Math.max(3,40*f),6,3,f>.5?'#58c96a':f>.25?'#f2b01e':'#e74c3c')}"
NEW_DRAW_HP = (
    "if(u.hp<u.mhp){const f=Math.max(0,u.hp/u.mhp);rr(u.x-20,u.y+27,40,6,3,'rgba(0,0,0,.3)');rr(u.x-20,u.y+27,Math.max(3,40*f),6,3,f>.5?'#58c96a':f>.25?'#f2b01e':'#e74c3c')}\n"
    "    if(phase==='fight'&&u.life>0){const lf=Math.max(0,Math.min(1,u.life/u.maxLife)),warn=u.life<=1.5;rr(u.x-18,u.y+20,36,4,2,'rgba(0,0,0,.35)');rr(u.x-18,u.y+20,Math.max(2,36*lf),4,2,warn?(Math.sin(t*16)>0?'#ff4d4d':'#ffd23f'):'#5ccfb4');if(warn&&Math.sin(t*12)>0){x.strokeStyle='rgba(255,80,80,.6)';x.lineWidth=2.5;x.beginPath();x.arc(u.x,u.y,26,0,6.28);x.stroke()}}"
)
if "u.life/u.maxLife" not in html and OLD_DRAW_HP in html:
    html = html.replace(OLD_DRAW_HP, NEW_DRAW_HP, 1)

# ── 10. Write root index.html ──────────────────────────────────────────────────
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Updated root index.html ({len(html):,} bytes)")

# ── 11. Package merge-battle-youtube.zip at root ──────────────────────────────
if os.path.exists(OUT_ZIP):
    os.remove(OUT_ZIP)
with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(SRC, 'index.html')
size_kb = os.path.getsize(OUT_ZIP) / 1024
print(f"Built {OUT_ZIP} ({size_kb:.1f} KB)")

# ── 12. Also update builds/youtube/ folder ───────────────────────────────────
os.makedirs(YT_DIR, exist_ok=True)
yt_html = os.path.join(YT_DIR, 'index.html')
yt_zip = os.path.join(YT_DIR, 'merge-battle-youtube.zip')
with open(yt_html, 'w', encoding='utf-8') as f:
    f.write(html)
if os.path.exists(yt_zip):
    os.remove(yt_zip)
with zipfile.ZipFile(yt_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(yt_html, 'index.html')
print(f"Updated {YT_DIR} with index.html and merge-battle-youtube.zip")

# ── 13. Verification Checks ───────────────────────────────────────────────────
checks = [
    ("YouTube SDK script in head", '<script src="https://www.youtube.com/game_api/v1"></script>', False),
    ("YouTube PF platform adapter", "const PF={name:'youtube'", False),
    ("YouTube Ad trigger every 4 waves intact", "wavesSinceAd>=4", False),
    ("YouTube Ad trigger every 3 losses intact", "losses%3===0", False),
    ("PAL cost is 1 elixir", "PALCOST=1", False),
    ("Bomb cost is 2 elixir", "bomb:{n:'BOMB',c:2", False),
    ("Heart cost is 4 elixir", "heart:{n:'HEART',c:4", False),
    ("Freeze cost is 4 elixir", "freeze:{n:'FREEZE',c:4", False),
    ("Zap cost is 4 elixir", "zap:{n:'ZAP',c:4", False),
    ("Pal lifetime formula palLife(lv)=15+lv*5", "palLife=lv=>15+lv*5", False),
    ("Merge refreshes full life", "tg.maxLife=palLife(tg.lv);tg.life=tg.maxLife;", False),
    ("Expired feedback on time up", "u.expired?'Expired!':'Pal down!'", False),
    ("Lock cards in prep (useCard)", "toast('Press Start Wave to begin!'", False),
    ("Lock card dragging in prep", "toast('Press Start Wave to begin!','#5ccfb4');sfx.click();return", False),
    ("Start Wave in arena center", "topY+(baseY-topY)*.44", False),
    ("Wave 1 always 1 green pal", "if(wave===1){", False),
    ("Reset units on won wave", "if(phase==='won'){if(wavesSinceAd>=4){wavesSinceAd=0;showAd('level_completed')}resetUnits();fallen=[];phase='prep';idle=0;energy=10;save();return}", False),
    ("Reset units on lost retry", "resetUnits();fallen=[];phase='prep'", False),
    ("waveWon revive removed", "revive();stars=", True),
]

all_ok = True
for label, needle, should_absent in checks:
    found = needle in html
    ok = (not found) if should_absent else found
    all_ok = all_ok and ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")

print("\n" + ("ALL YOUTUBE GAMEPLAY CHECKS PASSED!" if all_ok else "SOME CHECKS FAILED!"))
