from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 统一初始化异步调度器
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")