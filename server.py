import json
import sqlite3
import asyncio
import uvicorn
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from bedrock.server import Server

def get_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

db_conn = get_db()
db_conn.execute('''
    CREATE TABLE IF NOT EXISTS redemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        player_name TEXT, 
        code TEXT, 
        claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
db_conn.commit()

mc = Server()
current_ctx = None

@mc.server_event
async def ready(ctx):
    global current_ctx
    current_ctx = ctx
    print(f"\n[MC] Wss running @{ctx.host}:{ctx.port}")
    
    await asyncio.sleep(0.5) 
    try:
        await ctx.server.run("subscribe PlayerMessage")
        await ctx.server.run("playsound random.levelup @a")
    except:
        pass

@mc.game_event
async def player_message(ctx):
    sender = ctx.sender
    message = ctx.message.strip()

    if message == "SUMMER2016" and sender != "External":
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM redemptions WHERE player_name = ? AND code = ?", (sender, "SUMMER2016"))
        
        if cursor.fetchone():
            await ctx.server.run(f'tellraw "{sender}" {{"rawtext":[{{"text":"§cYou already claimed this!"}}]}}')
        else:
            cursor.execute("INSERT INTO redemptions (player_name, code) VALUES (?, ?)", (sender, "SUMMER2016"))
            db_conn.commit()
            raw_msg = json.dumps({"rawtext": [{"text": f"[§l§bSERVER§r] §acode redeemed by §e{sender}"}]})
            await ctx.server.run(f"tellraw @a {raw_msg}")
            await ctx.server.run(f"xp 3000 \"{sender}\"")
            await ctx.server.run(f"title \"{sender}\" actionbar §a+3000 XP")
            await ctx.server.run("playsound random.orb @a")

def run_mc_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("[SYSTEM] WsServer start")
    mc.start("0.0.0.0", 8000)

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=run_mc_server, daemon=True)
    thread.start()
    yield
    print("[SYSTEM] Wsserver close")

app_web = FastAPI(lifespan=lifespan)

app_web.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app_web.get("/")
async def index(request: Request):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM redemptions ORDER BY claimed_at DESC")
    rows = cursor.fetchall()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "redemptions": rows,
        "is_online": current_ctx is not None
    })

@app_web.post("/announce")
async def announce(announcement: str = Form(...)):
    if current_ctx:
        raw_msg = json.dumps({"rawtext": [{"text": f"[§l§bANNOUNCEMENT§r] §l§e»§r §e{announcement}§r"}]})
        
        mc_loop = getattr(current_ctx.server, '_loop', asyncio.get_event_loop())

        asyncio.run_coroutine_threadsafe(
            current_ctx.server.run(f"tellraw @a {raw_msg}"), 
            mc_loop
        )
        asyncio.run_coroutine_threadsafe(
            current_ctx.server.run(f"title @a title §e{announcement}"), 
            mc_loop
        )
        asyncio.run_coroutine_threadsafe(
            current_ctx.server.run("playsound note.pling @a"), 
            mc_loop
        )
            
    return RedirectResponse(url="/", status_code=303)

@app_web.post("/delete/{player_id}")
async def delete_player(player_id: int):
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM redemptions WHERE id = ?", (player_id,))
    db_conn.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app_web, host="0.0.0.0", port=3002)