import asyncio
import json
import websockets
from websockets.server import WebSocketServerProtocol

ONLINE: dict[str, WebSocketServerProtocol] = {}

async def safe_send(ws: WebSocketServerProtocol, payload: dict):
    try:
        await ws.send(json.dumps(payload, ensure_ascii=False))
    except Exception:
        pass

async def handler(ws: WebSocketServerProtocol):
    user = None
    try:
        raw = await ws.recv()
        msg = json.loads(raw)

        if msg.get("type") != "hello" or not msg.get("user"):
            await ws.close(code=1008, reason="must hello first")
            return

        user = msg["user"].strip()
        if not user:
            await ws.close(code=1008, reason="empty user")
            return

        if user in ONLINE:
            await safe_send(ws, {"type": "error", "error": f"user '{user}' already online"})
            await ws.close(code=1008, reason="user already online")
            return

        ONLINE[user] = ws
        print(f"[+] {user} connected, online={len(ONLINE)}")
        await safe_send(ws, {"type": "system", "text": f"welcome {user}", "online": list(ONLINE.keys())})

        # 主循环：接收并转发
        async for raw in ws:
            try:
                data = json.loads(raw)
            except Exception:
                await safe_send(ws, {"type": "error", "error": "invalid json"})
                continue

            if data.get("type") == "list":
                await safe_send(ws, {"type": "list", "online": list(ONLINE.keys())})
                continue

            if data.get("type") != "msg":
                await safe_send(ws, {"type": "error", "error": "unknown type"})
                continue

            to = (data.get("to") or "").strip()
            text = (data.get("text") or "").strip()

            if not to or not text:
                await safe_send(ws, {"type": "error", "error": "to/text required"})
                continue

            payload = {"type": "msg", "from": user, "text": text}

            if to == "*":
                # 广播（不发给自己也可以，看你偏好）
                for u, target_ws in list(ONLINE.items()):
                    if target_ws is not ws:
                        await safe_send(target_ws, payload)
                await safe_send(ws, {"type": "ack", "to": "*", "ok": True})
            else:
                target = ONLINE.get(to)
                if not target:
                    await safe_send(ws, {"type": "error", "error": f"user '{to}' not online"})
                    continue
                await safe_send(target, payload)
                await safe_send(ws, {"type": "ack", "to": to, "ok": True})

    except websockets.ConnectionClosed:
        pass
    finally:
        if user and ONLINE.get(user) is ws:
            ONLINE.pop(user, None)
            print(f"[-] {user} disconnected, online={len(ONLINE)}")

async def main():
    host = "0.0.0.0"
    port = 8765
    print(f"Chat server listening on ws://{host}:{port}")
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
