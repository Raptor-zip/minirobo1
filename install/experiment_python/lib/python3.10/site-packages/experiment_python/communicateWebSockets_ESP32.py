import asyncio
import websockets

async def handle_message(websocket, path):
    # クライアントからのメッセージを待機し、受け取ったらそのまま返す
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"{{'motor1':{{'speed':120}},'motor2':{{'speed':130}}}}\n")

async def main():
    # WebSocketサーバーを起動
    # server = await websockets.serve(handle_message, "localhost", 8765)
    server = await websockets.serve(handle_message, "0.0.0.0", 8765)

    print("WebSocket server is running. Press Ctrl+C to stop.")

    # サーバーが終了するまで待機
    await server.wait_closed()

# イベントループを作成し、main()を実行
if __name__ == "__main__":
    asyncio.run(main())
