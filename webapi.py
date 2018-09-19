""" Basic todo list using webpy 0.3 """
import time
import web
from gensim import corpora, models, similarities

import GensimModel

### Url mappings
urls = (
    '/', 'Index'
)

D= GensimModel.MM()

lines = open('cropus.txt', 'r').readlines()

### Templates
render = web.template.render('templates', base='base')


class Index:
    form = web.form.Form(
        web.form.Textbox('query', web.form.notnull,
                            description="关键词查询-词和词空格,不少于3+个词才准（java web 开发）:"),
        web.form.Button('Add query'),
    )

    def GET(self):
        """ Show page """
        todos = []
        form = self.form()
        return render.index(todos, form)

    def POST(self):
        """ Add new entry """
        form = self.form()
        if not form.validates():
            todos = []
            return render.index(todos, form)
        #query
        querys=form.d.query
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
        data = []
        for s in sims:
            data.append((s[1],lines[s[0]]))
            # print(s[1], s[0])
            # print(lines[s[0]])
        return render.index(data, form)







app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()
