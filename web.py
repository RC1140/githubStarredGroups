from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for

import redis
from pagination import Pagination

r = redis.Redis()

app = Flask(__name__)

@app.route('/')
@app.route('/page/<int:pageNumber>')
def index(pageNumber=None):
	if not pageNumber:
		pageNumber = 0
	repoHashes = r.lrange('REPOS',0,-1)
	tags  = r.lrange('TAGS',0,-1)
	finalNames = []
	for rHash in repoHashes[(pageNumber*10):(pageNumber*10)+10]:
		finalNames.append({'name':r.get('REPO:%s'%rHash),'hash':rHash,'tags':r.lrange('REPO:%s:TAGS'%rHash,0,-1)})
	print pageNumber
	pagination = Pagination(pageNumber, 10, len(repoHashes))
	return render_template('index.html',repos=finalNames,tags=tags,pagination=pagination)

@app.route('/saveTags',methods=['POST'])
def saveTags():
	for keyPair in request.form:
		r.delete('REPO:%s:TAGS'%keyPair)
		for tag in request.form.getlist(keyPair):
			r.lpush('REPO:%s:TAGS'%keyPair,tag)
	return redirect(url_for('index'))

@app.route('/viewTags')
def viewTags():
	tags  = r.lrange('TAGS',0,-1)
	return render_template('tags.html',tags=tags)

@app.route('/viewTag/<tag>')
def viewTag(tag):
	repoHashes = r.lrange('REPOS',0,-1)
	finalRepos = []
	for rHash in repoHashes[0:10]:
		repoTags = r.lrange('REPO:%s:TAGS'%rHash,0,-1)
		if tag in repoTags:
			finalRepos.append({'name':r.get('REPO:%s'%rHash)})
		
	return render_template('tag.html',repos=finalRepos,tag=tag)

@app.route('/newTag',methods=['GET','POST'])
def newTag():
	if request.method == 'POST':
		r.lpush('TAGS',request.form.get('tag'))
		return redirect(url_for('viewTags'))
	return render_template('newtag.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug=True)
