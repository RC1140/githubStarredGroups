import redis
import json

r = redis.Redis()
repos = r.lrange('REPOS',0,-1)
tags = r.lrange('TAGS',0,-1)

final = {'name':'tags'}
childTags = {}
for tag in tags:
	childTags[tag] = []

for repo in repos:
	loadedTags = r.lrange('REPO:%s:TAGS'%repo,0,-1)
	for subTag in loadedTags:
		childTags[subTag].append({'name':r.get('REPO:%s'%repo),'children':[]})

final['children'] = [{'name':tag,'children':childTags[tag]} for tag in tags]

print json.dumps(final)
