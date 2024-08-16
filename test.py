import asyncio

async def task_coro():
    print("AAAAAAAAAAAAAAAAAAAAA")
    await asyncio.sleep(3)
    return "Hello, asyncio!"

async def main():
    task = asyncio.create_task(task_coro())
    await asyncio.sleep(3)
    await task
    print(task.result())  # 出力: Hello, asyncio!

asyncio.run(main())