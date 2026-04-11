import asyncio

class MyClass:
    def __init__(self):
        self.ev = asyncio.Event()

    async def wait_it(self):
        print("waiting")
        await self.ev.wait()

    def set_it(self):
        self.ev.set()

m = MyClass()

async def main():
    asyncio.get_running_loop().call_later(1, m.set_it)
    await m.wait_it()
    print("done")

try:
    asyncio.run(main())
except Exception as e:
    print(f"Error: {e}")
