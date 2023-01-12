from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
import pymongo
import certifi

import hashlib
import datetime
from datetime import datetime as dt
import jwt

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.l4us7n9.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta



# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["id"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/register')
def register():
   return render_template('register.html')


@app.route('/login')
def login():
   return render_template('login.html')


@app.route('/about')
def about():
   return render_template('about.html')


@app.route('/logout')
def logout():
    global unique
    unique = ''
    return render_template('login.html')



############################### <<Main 화면>> ###############################
@app.route('/main')
def main():
    project_list = list(db.project.find({"unique":unique}, {'_id': False}))
    project_nm1 = ''
    project_nm2 = ''
    project_nm3 = ''


    if len(project_list) == 0:
        project_nm1 = 'Input New Project'
        project_nm2 = 'Input New Project'
        project_nm3 = 'Input New Project'
    else:
        print(type(project_list[0]['projectNum']))
        try:
            if project_list[0]['projectNum'] == '1':
                project_nm1 = project_list[0]['name']
            elif project_list[1]['projectNum'] == '1':
                project_nm1 = project_list[1]['name']
            elif project_list[2]['projectNum'] == '1':
                project_nm1 = project_list[2]['name']
        except:
            pass
        try:
            if project_list[0]['projectNum'] == '2':
                project_nm2 = project_list[0]['name']
            elif project_list[1]['projectNum'] == '2':
                project_nm2 = project_list[1]['name']
            elif project_list[2]['projectNum'] == '2':
                project_nm2 = project_list[2]['name']
        except:
            pass
        try:
            if project_list[0]['projectNum'] == '3':
                project_nm3 = project_list[0]['name']
            elif project_list[1]['projectNum'] == '3':
                project_nm3 = project_list[1]['name']
            elif project_list[2]['projectNum'] == '3':
                project_nm3 = project_list[2]['name']
        except:
            pass
        if project_nm1 == '':
            project_nm1 = 'Input New Project'
        if project_nm2 == '':
            project_nm2 = 'Input New Project'
        if project_nm3 == '':
            project_nm3 = 'Input New Project'

    return render_template('main.html', project_nm1=project_nm1, project_nm2=project_nm2, project_nm3=project_nm3)

################# <<<MY PAGE>>> #####################
@app.route('/mypage')
def mypage():
    user_info = db.user.find_one({"id":unique}, {'_id': False})
    
    print(user_info)
    user_name = user_info['name']
    user_id = user_info['id']
    return render_template('mypage.html', name=user_name, id=user_id)


# 회원정보 수정
@app.route("/mypage", methods=["PUT"])
def user_put():
    new_name_receive = request.form['new_name_give']
    old_pw_receive = request.form['old_pw_give']
    new_pw_receive = request.form['new_pw_give']
    new_pw2_receive = request.form['new_pw2_give']

    user_info = db.user.find_one({'id': unique}, {'_id': False})
    old_pw_hash = hashlib.sha256(old_pw_receive.encode('utf-8')).hexdigest()

    # case1) 이름만 변경하는 경우
    if (new_pw_receive == "") and (new_pw2_receive == "") and (new_name_receive != ""):
        if user_info['pw'] != old_pw_hash:
            return jsonify({'msg': '기존 비밀번호를 다시 확인해주세요.'})
        else:
            db.user.update_one({'id':unique}, {"$set":{'name':new_name_receive}})
            return jsonify({'msg': '회원정보를 수정했습니다.'})

    # case2) 비밀번호만 변경하는 경우
    elif (new_name_receive == "") and (new_pw_receive != ""):
        if user_info['pw'] != old_pw_hash:
            return jsonify({'msg': '기존 비밀번호를 다시 확인해주세요.'})
        elif new_pw_receive != new_pw2_receive:
            return jsonify({'msg': '새로운 비밀번호가 서로 일치하지 않습니다.'})
        else:
            new_pw_hash = hashlib.sha256(new_pw_receive.encode('utf-8')).hexdigest()
            db.user.update_one({'id':unique},{"$set":{"pw":new_pw_hash}})
            return jsonify({'msg': '회원정보를 수정했습니다.'})
    
    # case3) 이름과 비밀번호 둘 다 입력하지 않은 경우
    elif (new_name_receive == "") and (new_pw_receive == ""):
        return jsonify({'msg': '수정할 회원 정보를 입력해주세요.'})

    # case4) 이름과 비밀번호 모두 변경하는 경우
    else:
        if user_info['pw'] != old_pw_hash:
            return jsonify({'msg': '기존 비밀번호를 다시 확인해주세요.'})
        elif new_pw_receive != new_pw2_receive:
            return jsonify({'msg': '새로운 비밀번호가 서로 일치하지 않습니다.'})
        else:
            new_pw_hash = hashlib.sha256(new_pw_receive.encode('utf-8')).hexdigest()
            doc = {
                'name' : new_name_receive,
                'pw' : new_pw_hash
            }
            db.user.update_one({'id':unique},{"$set":doc})
            print(doc)
            return jsonify({'msg': '회원정보를 수정했습니다.'})



# 회원정보 삭제
@app.route("/mypage", methods=["DELETE"])
def user_delete():

    db.user.delete_one({'id':unique})
    return jsonify({'msg': '탈퇴 처리되었습니다. 또 방문해주세요.'})




################# <<<canvas1 : Project>>> #####################

@app.route('/project')
def project():
    return render_template('project.html', projectNum=projectNum)

@app.route('/projectnum', methods=["POST"])
def projectnum():
    global projectNum
    projectNum = request.form['num_give']
    print(projectNum)
    return jsonify({'result': 'success'})


# 프로젝트 등록/수정
@app.route("/project", methods=["POST"])
def project_post():
    aa = db.project.find_one({"unique":unique, "projectNum":projectNum}, {'_id': False})
    name_receive = request.form['name_give']
    s_day_receive = request.form['s_day_give']
    f_day_receive = request.form['f_day_give']
    intro_receive = request.form['intro_give']
    
    if f_day_receive < s_day_receive:
        return jsonify({'msg': '시작날짜는 종료날짜보다 빨라야 합니다.'})
    else:
        if aa is None:
            doc = {
                'projectNum' : projectNum,
                'name' : name_receive,
                's_day' : s_day_receive,
                'f_day' : f_day_receive,
                'intro' : intro_receive,
                'unique' : unique
            }
            db.project.insert_one(doc)
            return jsonify({'msg': '등록 완료!'})
        else:
            doc = {
                'name' : name_receive,
                's_day' : s_day_receive,
                'f_day' : f_day_receive,
                'intro' : intro_receive
            }
            db.project.update_one({'projectNum':str(projectNum), 'unique':unique},{"$set":doc})
            print(doc)
            return jsonify({'msg': '수정 완료!'})



# 프로젝트 불러오기
@app.route("/project", methods=["GET"])
def project_get():
    project_info = db.project.find_one({"unique":unique, "projectNum":str(projectNum)}, {'_id': False})
    print("project_info:", project_info)

    # D-day 계산
    format = '%Y-%m-%d'
    f_day = project_info['f_day']
    if f_day != '':
        dt = datetime.datetime.strptime(f_day, format).date()
        d_day = (dt-dt.today()).days
    else:
        d_day = 'null'                

    return jsonify({'project':project_info, 'd_day':d_day})

# 프로젝트 삭제
@app.route("/project", methods=["DELETE"])
def project_delete():
    no_receive = request.form['no_give']
    print(no_receive)

    db.project.delete_one({'projectNum':str(no_receive), 'unique':unique})
    return jsonify({'msg': '삭제 완료!'})




################# <<<canvas2 : Topic>>> #####################

@app.route('/topic')
def topic():
   return render_template('topic.html')

# 토픽 등록
@app.route("/topic", methods=["POST"])
def topic_post():
    topic_list = list(db.topic.find({"unique":unique, "projectNum":str(projectNum)}, {'_id': False}))

    if topic_list == []:
        no = 1
    else:
        no = topic_list[-1]['no']+1

    print(no)
    name_receive = request.form['name_give']
    intro_receive = request.form['intro_give']

    doc = {
        'no' : no,
        'name' : name_receive,
        'intro' : intro_receive,
        'unique' : unique
    }
    db.topic.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


# 토픽 수정
@app.route("/topic", methods=["PUT"])
def topic_put():
    no_receive = request.form['no_give']
    print(no_receive)
    name_receive = request.form['name_give']
    intro_receive = request.form['intro_give']

    doc = {
        'name' : name_receive,
        'intro' : intro_receive
    }
    db.topic.update_one({'no':int(no_receive), 'unique':unique, "projectNum":str(projectNum)},{"$set":doc})
    print(doc)
    return jsonify({'msg': '수정 완료!'})


# 토픽 불러오기
@app.route("/topic", methods=["GET"])
def topic_get():
    topic_list = list(db.topic.find({"unique":unique, "projectNum":str(projectNum)}, {'_id': False}))
    print(topic_list)
     
    return jsonify({'topics':topic_list})

# 토픽 삭제
@app.route("/topic", methods=["DELETE"])
def topic_delete():
    no_receive = request.form['no_give']
    print(no_receive)

    db.topic.delete_one({'no':int(no_receive), 'unique':unique, "projectNum":str(projectNum)})
    return jsonify({'msg': '삭제 완료!'})


################# <<<canvas3 : Todo>>> #####################

@app.route('/todo')
def todo():
   return render_template('todo.html')


# TODO 등록
@app.route("/planner", methods=["POST"])
def plan_post():
    plan_list = list(db.planner.find({"unique":unique, "projectNum":str(projectNum)}, {'_id': False}))

    if plan_list == []:
        no = 1
    else:
        no = plan_list[-1]['no']+1

    print(no)
    name_receive = request.form['name_give']
    s_day_receive = request.form['s_day_give']
    f_day_receive = request.form['f_day_give']
    comment_receive = request.form['comment_give']

    if f_day_receive < s_day_receive:
        return jsonify({'msg': '시작날짜는 종료날짜보다 빨라야 합니다.'})

    doc = {
        'projectNum' : projectNum,
        'no' : no,
        'name' : name_receive,
        's_day' : s_day_receive,
        'f_day' : f_day_receive,
        'comment' : comment_receive,
        'unique' : unique
    }
    db.planner.insert_one(doc)
    print(doc)
    return jsonify({'msg': '등록 완료!'})

# TODO 수정
@app.route("/planner", methods=["PUT"])
def plan_put():
    no_receive = request.form['no_give']
    print(no_receive)
    name_receive = request.form['name_give']
    s_day_receive = request.form['s_day_give']
    f_day_receive = request.form['f_day_give']
    comment_receive = request.form['comment_give']

    if f_day_receive < s_day_receive:
        return jsonify({'msg': '시작날짜는 종료날짜보다 빨라야 합니다.'})

    doc = {
        'name' : name_receive,
        's_day' : s_day_receive,
        'f_day' : f_day_receive,
        'comment' : comment_receive
    }
    db.planner.update_one({'no':int(no_receive), 'unique':unique, "projectNum":str(projectNum)},{"$set":doc})
    print(doc)
    return jsonify({'msg': '수정 완료!'})


# TODO 불러오기
@app.route("/planner", methods=["GET"])
def plan_get():
    plans_list = list(db.planner.find({"unique":unique, "projectNum":str(projectNum)}, {'_id': False}))
    print(plans_list)

    # D-day 계산
    format = '%Y-%m-%d'
    d_days = []
    for i in range(len(plans_list)):
        f_day = plans_list[i]['f_day']
        if f_day != '':
            dt = datetime.datetime.strptime(f_day, format).date()
            d_days.append((dt-dt.today()).days)
        else:
            d_days.append('null')                
    return jsonify({'plans':plans_list, 'd_days':d_days})

# TODO 삭제
@app.route("/planner", methods=["DELETE"])
def plan_delete():
    no_receive = request.form['no_give']
    print(no_receive)

    db.planner.delete_one({'no':int(no_receive), 'unique':unique, "projectNum":str(projectNum)})
    return jsonify({'msg': '삭제 완료!'})



#########################[회원가입 API]############################## 


### ID 중복 체크
@app.route('/idcheck', methods=['POST'])
def idcheck():
    id_receive = request.form['id_give']
    print(id_receive)

    aa = db.user.find_one({'id': id_receive}, {'_id': False})
    print(aa)
    if id_receive == '':
        return jsonify({'msg': 'ID를 입력해주세요.'})
    elif aa is not None:
        print('동일한 ID가 존재합니다. 다른 ID를 입력해주세요.')
        return jsonify({'msg': '동일한 ID가 존재합니다. 다른 ID를 입력해주세요.'})
    else:
        print('사용 가능한 ID입니다.')
        return jsonify({'msg': '사용 가능한 ID입니다.'})



# id, pw을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/register', methods=['POST'])
def api_register():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw2_receive = request.form['pw2_give']

    aa = db.user.find_one({'id': id_receive})
    if (id_receive == '') or (pw_receive == ''):
        return jsonify({'result': 'fail', 'msg': 'ID/PW를 입력해주세요.'})
    elif aa is not None:
        print(aa)
        print('동일한 ID가 존재합니다. 다른 ID를 입력해주세요.')
        return jsonify({'result': 'fail', 'msg': '동일한 ID가 존재합니다. 다른 ID를 입력해주세요.'})

    elif pw_receive != pw2_receive:
        print('비밀번호가 일치하지 않습니다. 다시 확인해주세요.')
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다. 다시 확인해주세요.'})

    else:
        print(id_receive)
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        doc = {
            'name' : name_receive,
            'id' : id_receive,
            'pw' : pw_hash,
        }
        db.user.insert_one(doc)

        return jsonify({'result': 'success', 'msg': '회원가입이 완료 되었습니다! 로그인 페이지로 이동합니다.'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    if (id_receive=='') or (pw_receive==''):
        return jsonify({'result': 'fail', 'msg': '아이디,패스워드를 입력하세요.'})
    
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
   

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5)    #언제까지 유효한지
        }
        #jwt를 암호화
        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        

        # 모든 문서를 불러오는 고유 Primary key는 id로 설정
        global unique
        unique = id_receive
        print(unique)

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
