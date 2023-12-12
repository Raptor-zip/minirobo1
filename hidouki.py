import asyncio

# async def control_motor():


# motor1_speedの初期値
motor1_speed = 0

# 関数が実行されたら非同期でcontrol_motorを実行
async def main():
    global motor1_speed

    # 非同期で1秒間だけmotor1_speedを255にする
    motor1_speed = 255
    await asyncio.sleep(1)

    # 1秒後にmotor1_speedを0にする
    motor1_speed = 0

# イベントループの作成
loop = asyncio.get_event_loop()

# main関数を非同期で実行
loop.run_until_complete(main())

# 実行後のmotor1_speedの値を表示
print("motor1_speed:", motor1_speed)