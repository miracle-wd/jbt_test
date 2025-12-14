import asyncio
import json
import websockets

SERVER = "ws://127.0.0.1:8765"

async def receiver(ws):
    async for raw in ws:
        try:
            msg = json.loads(raw)
        except Exception:
            print(f"\n[recv raw] {raw}\n> ", end="")
            continue

        t = msg.get("type")
        if t == "msg":
            print(f"\n[{msg.get('from')}] {msg.get('text')}\n> ", end="")
        elif t == "list":
            print(f"\n[online] {msg.get('online')}\n> ", end="")
        elif t == "ack":
            print(f"\n[ok] delivered to {msg.get('to')}\n> ", end="")
        elif t == "error":
            print(f"\n[error] {msg.get('error')}\n> ", end="")
        else:
            print(f"\n[{t}] {msg}\n> ", end="")

async def sender(ws):
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, lambda: input("> ").strip())
        if not line:
            continue
        if line == "/quit":
            await ws.close()
            return
        if line == "/list":
            await ws.send(json.dumps({"type": "list"}))
            continue
        if line.startswith("/to "):
            # /to Bob hello world
            parts = line.split(" ", 2)
            if len(parts) < 3:
                print("usage: /to <user> <text>")
                continue
            to, text = parts[1], parts[2]
            await ws.send(json.dumps({"type": "msg", "to": to, "text": text}, ensure_ascii=False))
            continue
        if line.startswith("/all "):
            text = line[5:]
            await ws.send(json.dumps({"type": "msg", "to": "*", "text": text}, ensure_ascii=False))
            continue

        print("commands: /to <user> <text> | /all <text> | /list | /quit")

async def main():
    user = input("username: ").strip()
    if not user:
        print("empty username")
        return

    async with websockets.connect(SERVER) as ws:
        await ws.send(json.dumps({"type": "hello", "user": user}, ensure_ascii=False))
        print(f"connected to {SERVER} as {user}")
        print("commands: /to <user> <text> | /all <text> | /list | /quit")
        await asyncio.gather(receiver(ws), sender(ws))

if __name__ == "__main__":
    asyncio.run(main())
