from crontab import CronTab

cron = CronTab(user="root")
job = cron.new(command='python /home/mind410/Projects/productCrawler/ProductCrawler/runner.py')
job.hour.every(5)

cron.write()