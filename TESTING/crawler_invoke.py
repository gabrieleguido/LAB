import crawler_test
import asyncio

dict = asyncio.run(crawler_test.fun("https://en.wikipedia.org/wiki/Bermuda_Triangle"))
print(dict["parsed"])