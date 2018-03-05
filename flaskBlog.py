#coding:gbk
from flask import Flask, flash, redirect, render_template, request, url_for,session
from collections import defaultdict
from  connectDB import excuteSel
from  connectDB import excuteOther
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'some_secret'
def tree(): return defaultdict(tree)

@app.template_filter('sub')
def sub(l, start, end):
    return str(l)[start:end]

def verify(func):
    def inner(*args, **kwargs):
        if not session.get('userid'):
            return redirect('/login')
        return func(*args, **kwargs)
    return inner

@app.route('/')
def index():

    return redirect(url_for('login'))

@app.route('/view')
def view():
    id=''
    if request.method == 'GET':
        id = request.args.get('id')
    if id=='':
        return url_for('login')

    sql='select * from airticleSummray  where aid=\''+id+'\' order by id'
    record=excuteSel(sql)
    recArray=[]
    for i in range(len(record)):
        recArray .append({'id':record[i][0] ,'title':record[i][1],'pid':record[i][2] ,'order':record[i][5]})
        recArray.sort( key=lambda x: x['order'])
    return render_template('index.html',trees=recArray)

@app.route('/home', methods=['GET', 'POST'],endpoint='home')
@verify
def home():
    error = None

    if request.method == 'POST':

        action = request.values.get('action', 0)
        if action=='add':
            try:
                id = request.values.get('id', 0)
                title = request.values.get('title', 0)
                intro = request.values.get('intro', 0)
                sql = 'insert into article([sid] ,[uid],[title],[intro]) VALUES ( \'' + str(
                    id) + '\',\''+session.get('userid')+'\',\'' + title + '\',\''+intro+'\'  )'

                excuteOther(sql)
                return 'ok'
            except:
                return 'error'
    record = excuteSel('select * from article where uid=\''+ session['userid']+'\'')
    recArray = []
    for i in range(len(record)):
        recArray.append({'sid': record[i][7],'intro': record[i][6] if   record[i][6] else ' ',  'title': record[i][1], 'ptime': record[i][4], 'utime': str(record[i][5])[0:10]})
    if len(recArray)>1:
        recArray.sort(key=lambda x: x['ptime'],reverse=True)
    item={'name':session["username"],'weibo': session["weibo"],'email':session["email"]}
    return render_template('home.html', list=recArray,user=item)
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        if request.form['Eamil'] != '' and  request.form['Password'] != '':
            email= request.form['Eamil']
            paw = request.form['Password']
            record=checkPass(email,paw)
            id=record[0]
            if bool(id):
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+':'+email+'用户已登录')
                session["userid"]=id
                session["username"]=record[3]
                session["email"] = record[1]
                session["weibo"] = record[4]
                return redirect(url_for('home'))
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')

    return render_template('login.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        id = request.values.get('id', 0)
        user = request.values.get('user', 0)
        pwd = request.values.get('pwd', 0)
        wb = request.values.get('wb', 0)
        email = request.values.get('email', 0)
        name = request.values.get('name', 0)
        if user.strip()=='' or pwd.strip()=='':
            return '不能为空'
        #检查是否已存在
        count= excuteSel('select count(1) from userinfo where account=\''+user+'\'')
        if count[0][0] == 0:
            if '--' in user or '=' in user or '\\' in user or '--'  in pwd or '=' in pwd or '\\' in pwd:
                return '包含特殊字符';
            try:
                sql = 'insert into userinfo([id],[email],[pwd],[name],[weibo],[account]) VALUES ( \''  + str(id) + '\',\''+ str(email) + '\',\'' + str(pwd) + '\',\'' + str(name)  + '\',\'' + str(wb) + '\',\'' + str(user)+ '\' )'
                print(sql)
                excuteOther(sql)
                return 'ok'
            except:
                return '执行错误'
        else:
            return '账号已存在'


@app.route('/detail', methods=['GET', 'POST'],endpoint='detail')
def detail():
    content = ''
    if request.method == 'GET':
        id = request.args.get('id')
        if id :
            content=excuteSel('select content from articleContent where pid=\''+str(id)+"'")
            content=content[0][0]
        else:
            print('error')
    return content

@app.route('/changeSummary', methods=['GET', 'POST'],endpoint='changeSummary')
@verify
def changeSummary():
    content = ''
    if request.method == 'POST':
        id = request.values.get('id', 0)
        ope = request.values.get('ope', 0)
        title = request.values.get('title', 0)
        if id :
            if ope=='update':
                excuteOther('update airticleSummray  set title=\''+title+'\'  where id=\'' + str(id) + "'")
            elif ope=='delete':
                excuteOther('delete airticleSummray   where id=\'' + str(id) + "'")
            elif ope=='add':
                order= request.values.get('order', 0)
                sql = 'insert into airticleSummray([id] ,[uid],[type],[order],[title],[aid]) VALUES ( \'' + str(
                    id) + '\',\''+  session["userid"]+'\',2,\'' + order + '\',\'' + title + '\',\'' +  session['aid']  + '\'  )'
                excuteOther(sql)
            return 'ok'
        else:
            flash('You were successfully logged in')
            print('error')
    return content

@app.route('/wrrite', methods=['GET', 'POST'],endpoint='wrrite')
@verify
def wrrite():
    if request.method == 'GET':
        #文章id
        aid = request.args.get('id')
        session['aid']=aid
    if request.method == 'POST':
        id =request.values.get('id', 0)
        content =request.values.get('content', 0)
        nextId = request.values.get('nextId', 0)
        order = request.values.get('order', 0)
        title = request.values.get('title', 0)
        count=excuteSel('select count(id) from airticleSummray where id=\'' + str(id) + "'")
        ope= 'new' if count[0][0]==0 else 'update';
        #字符替换
        if  '\'' in content:
            content=content.replace("'","''")
        if ope=='update':
            try:

                excuteOther('update articleContent set content=\''+content+'\'  where pid=\'' + str(id) + '\'')
                count = excuteSel('select count(id) from articleContent where pid=\'' + str(id) + "'")
                ope = 'new' if count[0][0] == 0 else 'update';
                # 更新content
                sql = 'update articleContent  set  content=\'' + content + '\' where   pid=\'' + str(id) + '\''
                if ope=='new':
                    sql = 'insert into articleContent([pid],[content]) VALUES ( \'' + str(id) + '\',\'' + content + '\' )'
                excuteOther(sql)
                content=''
                if nextId!='':
                   content = excuteSel('select content from articleContent where pid=\'' + str(nextId) + "'")
                   content = content[0][0]

                return content
            except:
                return ''
        else:
            try:

                #保存大纲
                sql='insert into airticleSummray([id] ,[uid],[type],[order],[title],[aid]) VALUES ( \''+str(id)+'\',\''+ session.get('userid')+'\',2,\''+order+'\',\''+title+'\',\''+ session['aid']+  '\' )'
                excuteOther(sql)
                #保存content
                sql = 'insert into articleContent([pid],[content]) VALUES ( \'' + str(id) + '\',\'' + content + '\' )'
                excuteOther(sql)
                #查询下一content
                content = ''
                if nextId != '':
                    content = excuteSel('select content from articleContent where pid=\'' + str(nextId) + "'")
                    content = content[0][0]

                return content
            except:
                return ''
    sql='select * from airticleSummray where uid=\''+ session.get('userid')+'\' and aid=\''+session.get('aid')+'\''
    record = excuteSel(sql)
    recArray = []
    for i in range(len(record)):
        recArray.append({'id': record[i][0], 'title': record[i][1], 'pid': record[i][2], 'order': record[i][5]})
        recArray.sort(key=lambda x: x['order'])

    return render_template('wrrite.html',trees=recArray)


def checkPass(email,pwd):
    if '--' in email or '=' in email or '--' in pwd or '=' in pwd or pwd.strip()=='' :
        return False;
    sql='select * from userinfo where account=\''+email+'\''

    record=excuteSel(sql)
    if record:
        if record[0][2]==pwd:
            return record[0]
        else:
            return False;
    else :
        return False;
    return True;
if __name__ == "__main__":
   # app.run( host='192.168.41.26',port=5000)
    app.run(host='127.0.0.1', port=5000)