from flask import Flask
from flask import request
import GensimModel
from flask import render_template
app = Flask(__name__)

app.logger.warning('loading GensimModel...')
D= GensimModel.MM()
app.logger.warning('GensimModel load finished!')

#result set loads
lines = open('cropus.txt', 'r').readlines()


@app.route('/',methods=['POST', 'GET'])
def index():
    data = []
    if request.method == 'POST':
        querys= request.form['query']
        print('doc2bow %s', querys)
        global D
        vec_querys = D.dictionary.doc2bow(querys.lower().split())

        print('lsi space..')
        vec_lsi = D.lsi[vec_querys]  # convert the query to LSI space

        print('lsi index..')
        sims = D.index[vec_lsi]
        print('sort, enumerate..')
        sims = sorted(enumerate(sims), key=lambda item: -item[1])[0:10]

        print("make a Q:(%s) ,return top :", querys)

        for s in sims:
            data.append( (s[1], lines[s[0]]) )
            #print(s[1], s[0]) #0.515109 11062 相似度 docid
            #print(lines[s[0]]) #doc
    else:
        querys = ""
    return render_template('index.html', data=data,query=querys)