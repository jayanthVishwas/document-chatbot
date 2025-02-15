import redis

r = redis.Redis(
  host='teaching-mite-15056.upstash.io',
  port=6379,
  password='ATrQAAIncDEwOWY5OGI1OThjMmI0YTk1YWUyYTE1ODI1NDhhODY4NXAxMTUwNTY',
  ssl=True
)

r.set('foo', 'bar')
print(r.get('foo'))