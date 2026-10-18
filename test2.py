from playwright.sync_api import sync_playwright
import os
D='/workspace/bridge-legion/shots2/'
os.makedirs(D,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=ctx.new_page(); errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///workspace/bridge-legion/index.html'); pg.wait_for_timeout(600)
    print('VER', pg.evaluate('__bl.BL_VER'))
    pg.screenshot(path=D+'1_menu.png')
    # tabs screenshots
    for tab, name in [('evo','7_evo_weapons.png'),('quest','8_quests.png'),('pre','9_prestige.png'),('up','6_upgrades.png')]:
        pg.tap(f'[data-t={tab}]'); pg.wait_for_timeout(250); pg.screenshot(path=D+name)
    res=[]
    for lv in range(1,7):
        # ensure menu
        try: pg.tap('#play', timeout=2000)
        except Exception as e: print('play tap fail',e); break
        pg.wait_for_timeout(600)
        if lv==1: pg.screenshot(path=D+'2_play_lv1.png')
        if lv==3: pg.screenshot(path=D+'2b_play_lv3.png')
        for i in range(90):
            pg.evaluate('(()=>{const G=__bl.G;if(!G||G.over)return;const ents=G.lvl.ents.filter(e=>!e.used&&!e.dead&&e.z>G.z);ents.sort((a,b)=>a.z-b.z);const g=ents.find(e=>e.t=="gate");const c=ents.find(e=>e.t=="crowd"||e.t=="boss"||e.t=="miniboss"||e.t=="block");let t=g||c;if(g&&c&&c.z<g.z)t=c;if(t)G.tx=Math.max(-0.85,Math.min(0.85,t.x)); if(g){const pair=ents.filter(e=>e.t=="gate"&&Math.abs(e.z-g.z)<1);if(pair.length>1){const val=e=>e.op=="x"?500:e.op=="buff"?400:e.v>0?e.v:-999; pair.sort((a,b)=>val(b)-val(a)); G.tx=pair[0].x}}})()')
            pg.wait_for_timeout(280)
            if lv==1 and i==10: pg.screenshot(path=D+'3_battle.png')
            if pg.evaluate('__bl.G&&__bl.G.bossSeen&&!__bl.G.over') and not globals().get('bs_'): pg.screenshot(path=D+'4_boss.png'); globals()['bs_']=1
            if pg.evaluate('!__bl.G||__bl.G.over'): break
        pg.wait_for_timeout(1300)
        try:
            info=pg.evaluate('JSON.stringify({lv:__bl.G.lv,sq:__bl.G.squad,maxSq:__bl.G.maxSq,coins:__bl.S.coins,best:__bl.S.best,win:__bl.G.lvl.ents.at(-1).dead,fps:__bl.fps,shield:__bl.G.shield,theme:__bl.G.theme.n,kills:__bl.G.kills})')
        except Exception as e: info='ERR '+str(e)
        print('LVRES',info); res.append(info)
        pg.screenshot(path=D+f'5_end_lv{lv}.png')
        # go menu if end screen visible, else force
        try: pg.tap('#emenu', timeout=1500)
        except: pg.evaluate('__bl.showMenu()')
        pg.wait_for_timeout(300)
        for idx in range(8):
            bs=pg.locator('[data-up]:not([disabled])')
            if bs.count():
                try: bs.nth(idx % bs.count()).tap(timeout=800)
                except: break
            else: break
    print('FPS', pg.evaluate('__bl.fps'))
    pg.screenshot(path=D+'6_upgrades_after.png')
    print('ERR',errs)
    b.close()
