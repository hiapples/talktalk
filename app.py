from flask import Flask     
from flask import request 
from flask import redirect
from flask import render_template
from flask import Flask, make_response, request,Response
from flask import session
from flask_mail import Mail
from flask_mail import Message
from datetime import datetime, timedelta
from collections import Counter
import random
import smtplib
import time
import json
from flask import*
from bson.objectid import ObjectId
import pymongo
import os
import mailtrap as mt
from flask.views import MethodView
from flask import jsonify
from flask_jwt_extended import JWTManager
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import bson.binary
from werkzeug.utils import secure_filename
from flask import send_from_directory
import pathlib
from gridfs import *



#測試用帳號
client=pymongo.MongoClient("mongodb+srv://hiapples900:howard900@popalz.bm0pbdd.mongodb.net/?retryWrites=true&w=majority&appName=PoPalz")
db=client.talk
collection=db.users
collection2=db.problem
collection3=db.article

#cls db
#result=collection.delete_many({})  
#result=collection2.delete_many({}) 
#result=collection3.delete_many({}) 

app=Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hiapples900@gmail.com'
app.config['MAIL_PASSWORD'] = 'bzqzrllmagevgmbc'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response


##忘記密碼寄信
@app.route("/send",methods=["POST"])
def send():
    Email=request.form["forget_Email"]
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    if result != None:
        msg = Message('忘記密碼申請', sender = "abc", recipients = [Email])
        msg.html = render_template("mail.html",userid=userid)
        msg.body =  msg.html
        mail.send(msg)
        return redirect("/success?msg=傳送成功&msg2=請查看您的信箱！")
    return redirect("/error?msg=傳送錯誤&msg2=此電子信箱尚未註冊！")

##忘記密碼連結 給密碼
@app.route("/password",methods=["POST"])
def password():
    userid=request.form["userid"]
    result=collection.find_one({
        "userid":userid
    })
    password=result["password"]
    return render_template("password.html",password=password)

##首頁(登入頁面)
@app.route("/")
def index():
    #cookies userID 是666
    userID = request.cookies.get('userID')
    if userID == '666':
        return redirect("/member")

    return render_template("index.html")

##首頁(註冊頁面)
@app.route("/indexsignup")
def indexsignup():
    #cookies userID 是666
    userID = request.cookies.get('userID')
    if userID == '666':
        return redirect("/member")

    indexsignup="indexsignup"
    return render_template("index.html",indexsignup=indexsignup)

##忘記密碼
@app.route("/forget")
def forget():
    return render_template("forget.html")

##回報問題
@app.route("/problem")
def problem():
    return render_template("problem.html")

##回報問題(送出)
@app.route("/return1",methods=["POST"])
def return1():
    return1=request.form["return1"]
    collection2.insert_one({
        "return1":return1
    })
    return redirect("/success?msg=回報成功&msg2=感謝您給予我們回覆！")

##條款一
@app.route("/terms")
def terms():
    return render_template("terms.html")
##條款二
@app.route("/terms2")
def terms2():
    return render_template("terms2.html")


##錯誤
@app.route("/error")
def error():
    message=request.args.get("msg","你是失敗的人╮(╯_╰)╭")
    message2=request.args.get("msg2","")
    return render_template("error.html",message=message,message2=message2)
##成功(到首頁)
@app.route("/success")
def success():
    message=request.args.get("msg","你是成功的人(❛◡❛✿)")
    message2=request.args.get("msg2","")
    return render_template("success.html",message=message,message2=message2)
##成功(到會員)
@app.route("/success/member")
def success_member():
    message=request.args.get("msg","你是成功的人(❛◡❛✿)")
    message2=request.args.get("msg2","")
    userID = request.cookies.get('userID')
    if userID == '666':
        return render_template("success_member.html",message=message,message2=message2)
    else:
        return render_template("success.html",message=message,message2=message2)
    
##註冊
@app.route("/signup",methods=["POST"])
def signup():
    userid=request.form["signup_userid"]
    Email=request.form["signup_Email"]
    password=request.form["signup_password"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M')
    result=collection.find_one({
        "userid":userid
    })
    if result != None:
        return redirect("/error?msg=註冊錯誤&msg2=此用戶名稱已被註冊！")
    result=collection.find_one({
        "Email":Email
    })
    if result != None:
        return redirect("/error?msg=註冊錯誤&msg2=此電子信箱已被註冊！")
    collection.insert_one({
        "userid":userid,
        "Email":Email,
        "password":password,
        "phone":"",
        "date":date,
        "photo":"astronaut.png",
        "nickname":"",
        "messageboard":"",
        "heart_icon":[],
        "heart_icon_track":[],
        "heart_icon2":[],
        "heart_icon3":[],
        "message":[],
        "message_article":[],
        "message_date":[],
        "history":[],
        "history_photo":[],
        "notify":[],
        "notify_date":[],
        "notify_class":[],
        "notify_article":[],
        "notify_dot":"false",
        "track":[],
        "track_photo":[],
        "fans":[],
        "fans_photo":[],
    })
    return redirect("/success?msg=註冊成功&msg2=恭喜您加入我們！")
##登入
@app.route("/signin",methods=["POST"])
def signin():
    Email=request.form["signin_Email"]
    password=request.form["signin_password"]
    result=collection.find_one({
        "$and":[
            {"Email":Email},
            {"password":password}
        ] 
    })
    if result ==None:
        return redirect("/error?msg=登入錯誤&msg2=帳號或密碼輸入錯誤！")
    #session["userID"]是email
    session["userID"]=request.form["signin_Email"]
    
    name=request.form["remember"]
    resp = make_response(redirect("/member"))
    resp.set_cookie('userID', name)
    return resp

##會員
@app.route("/member")
def member():
    share=request.args.get("share","")
    shared=request.args.get("shared","")
    name=request.args.get("name","")
    name2=request.args.get("name2","")
    name3=request.args.get("name3","")
    name4=request.args.get("name4","")
    name5=request.args.get("name5","")
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    password=result["password"]
    userid=result["userid"]
    phone=result["phone"]
    date=result["date"]
    photo=result["photo"]
    nickname=result["nickname"]
    messageboard=result["messageboard"]
    history2=json.dumps(result["history"])
    history_photo2=json.dumps(result["history_photo"])
    count2=len(result["track"])
    count3=len(result["fans"])
    dot=result["notify_dot"]

    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    count1=[]
    for doc in cursor: 
        count1.append(doc["article"])

    count1=len(count1)
    if "userID" in session:
        return render_template("member.html",Email=Email,password=password,phone=phone,userid=userid,date=date,photo=photo,nickname=nickname,messageboard=messageboard,name=name,name2=name2,history2=history2,history_photo2=history_photo2,name3=name3,name4=name4,count1=count1,count2=count2,count3=count3,name5=name5,dot=dot,share=share,shared=shared)
    else:
        return redirect("/")



#抓公開
@app.route("/member/article_public", methods=['POST'])
def member_article_public():
    # 获取分页参数
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    # 计算起始索引
    skip = (page - 1) * limit   
    
    # 查询数据库并排序，添加分页功能
    cursor = collection3.find({}, sort=[("_id", pymongo.DESCENDING)]).skip(skip).limit(limit)
    cursor2 = collection3.find({}, sort=[("_id", pymongo.DESCENDING)])

    date4=[]
    userid2=[]
    for doc in cursor2: 
        date4.append(doc["date"])
        userid2.append(doc["userid"])
    article=[]
    userid=[] 
    photo=[] 
    date2=[]
    date3=[]
    people1_lengths=[]
    message2_lengths=[]
    for doc in cursor: 
        article.append(doc["article"])
        userid.append(doc["userid"])
        photo.append(doc["photo"])
        date2.append(doc["date"])
        people1_lengths.append(len(doc["heart_icon"]))
        message2_lengths.append(len(doc["message"]))
        datetime_obj = datetime.strptime(doc["date"], "%Y/%m/%d %H:%M:%S.%f")
        datetime_obj2 = datetime.now()
        # 计算年、月、日、小时和分钟差异
        years = datetime_obj2.year - datetime_obj.year
        months = datetime_obj2.month - datetime_obj.month
        days = datetime_obj2.day - datetime_obj.day
        hours = datetime_obj2.hour - datetime_obj.hour
        minutes = datetime_obj2.minute - datetime_obj.minute

        # 處理負值
        if minutes < 0:
            minutes += 60
            hours -= 1
        if hours < 0:
            hours += 24
            days -= 1
        if days < 0:
            previous_month_days = (datetime(datetime_obj2.year, datetime_obj2.month, 1) - timedelta(days=1)).day
            days += previous_month_days
            months -= 1
        if months < 0:
            months += 12
            years -= 1

        # 格式化時間差
        if years > 0 or months > 0:
            formatted_time_difference = f"{datetime_obj.year}年{datetime_obj.month}月{datetime_obj.day}日"
        elif days > 0:
            formatted_time_difference = f"{days}天前"
        else:
            formatted_time_difference = ""
            if hours > 0:
                if minutes >= 30:
                    hours += 1
                formatted_time_difference += f"{hours}小時"
            elif minutes > 0:
                formatted_time_difference += f"{minutes}分鐘"
            if formatted_time_difference:
                formatted_time_difference += "前"
            else:
                formatted_time_difference = "剛剛"

        date3.append(formatted_time_difference)
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    date1=result["heart_icon"]

    return jsonify(article , userid , photo , date1 , date2 , people1_lengths , message2_lengths , date3 ,date4 ,userid2)

#抓公開2
@app.route("/member/article_public2", methods=['POST'])
def member_article_public2():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit   

    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]

    cursor2=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date4=[]
    userid2=[]
    for doc in cursor2: 
        date4.append(doc["date"])
        userid2.append(doc["userid"])

    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ]).skip(skip).limit(limit)
    article=[]
    userid=[] 
    photo=[] 
    date2=[]
    date3=[]
    people1_lengths=[]
    message2_lengths=[]
    for doc in cursor: 
        article.append(doc["article"])
        userid.append(doc["userid"])
        photo.append(doc["photo"])
        date2.append(doc["date"])
        people1_lengths.append(len(doc["heart_icon"]))
        message2_lengths.append(len(doc["message"]))
        datetime_obj = datetime.strptime(doc["date"], "%Y/%m/%d %H:%M:%S.%f")
        datetime_obj2 = datetime.now()
        # 计算年、月、日、小时和分钟差异
        years = datetime_obj2.year - datetime_obj.year
        months = datetime_obj2.month - datetime_obj.month
        days = datetime_obj2.day - datetime_obj.day
        hours = datetime_obj2.hour - datetime_obj.hour
        minutes = datetime_obj2.minute - datetime_obj.minute

        # 處理負值
        if minutes < 0:
            minutes += 60
            hours -= 1
        if hours < 0:
            hours += 24
            days -= 1
        if days < 0:
            previous_month_days = (datetime(datetime_obj2.year, datetime_obj2.month, 1) - timedelta(days=1)).day
            days += previous_month_days
            months -= 1
        if months < 0:
            months += 12
            years -= 1

        # 格式化時間差
        if years > 0 or months > 0:
            formatted_time_difference = f"{datetime_obj.year}年{datetime_obj.month}月{datetime_obj.day}日"
        elif days > 0:
            formatted_time_difference = f"{days}天前"
        else:
            formatted_time_difference = ""
            if hours > 0:
                if minutes >= 30:
                    hours += 1
                formatted_time_difference += f"{hours}小時"
            elif minutes > 0:
                formatted_time_difference += f"{minutes}分鐘"
            if formatted_time_difference:
                formatted_time_difference += "前"
            else:
                formatted_time_difference = "剛剛"

        date3.append(formatted_time_difference)
    
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    date1=result["heart_icon_track"]

    return jsonify(article , userid , photo , date1 , date2 , people1_lengths , message2_lengths , date3 ,date4 ,userid2)

#抓私人
@app.route("/member/article_private", methods=['POST'])
def member_article_private():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit

    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]

    cursor2=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    article2=[]
    for doc in cursor2: 
        date3.append(doc["date"])
        article2.append(doc["article"])

    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ]).skip(skip).limit(limit)
    article=[]
    date=[]
    date2=[]
    people1_lengths=[]
    message2_lengths=[]
    for doc in cursor: 
        article.append(doc["article"])
        date.append(doc["date"])
        people1_lengths.append(len(doc["heart_icon"]))
        message2_lengths.append(len(doc["message"]))
        datetime_obj = datetime.strptime(doc["date"], "%Y/%m/%d %H:%M:%S.%f")
        datetime_obj2 = datetime.now()
        # 计算年、月、日、小时和分钟差异
        years = datetime_obj2.year - datetime_obj.year
        months = datetime_obj2.month - datetime_obj.month
        days = datetime_obj2.day - datetime_obj.day
        hours = datetime_obj2.hour - datetime_obj.hour
        minutes = datetime_obj2.minute - datetime_obj.minute

        # 處理負值
        if minutes < 0:
            minutes += 60
            hours -= 1
        if hours < 0:
            hours += 24
            days -= 1
        if days < 0:
            previous_month_days = (datetime(datetime_obj2.year, datetime_obj2.month, 1) - timedelta(days=1)).day
            days += previous_month_days
            months -= 1
        if months < 0:
            months += 12
            years -= 1

        # 格式化時間差
        if years > 0 or months > 0:
            formatted_time_difference = f"{datetime_obj.year}年{datetime_obj.month}月{datetime_obj.day}日"
        elif days > 0:
            formatted_time_difference = f"{days}天前"
        else:
            formatted_time_difference = ""
            if hours > 0:
                if minutes >= 30:
                    hours += 1
                formatted_time_difference += f"{hours}小時"
            elif minutes > 0:
                formatted_time_difference += f"{minutes}分鐘"
            if formatted_time_difference:
                formatted_time_difference += "前"
            else:
                formatted_time_difference = "剛剛"

        date2.append(formatted_time_difference)
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    heart_icon=result["heart_icon2"]

    return jsonify(article , heart_icon , date , people1_lengths , message2_lengths , date2 , date3 , article2)


#查私人
@app.route("/member/<userid>", methods=['POST','GET'])
def member_userid(userid):
    #分享網址
    if request.method == 'GET':
        Email = session["userID"]
        result = collection.find_one({
            "Email": Email
        })
        cursor = collection.find({}, sort=[("_id", pymongo.DESCENDING)])
        allname=[]
        for doc in cursor: 
            allname.append(doc["userid"])


        userid2 = result["userid"]
        name2 = "name2"
        name = "name"
        print(allname)
        
        if userid in allname and userid != userid2:
            share = userid
            shared = "shared"
            return redirect(url_for('member', name2=name2, share=share, shared=shared))
        if userid == userid2:
            return redirect(url_for('member', name=name))
        else:
            return 400
    
    if request.method == 'POST':
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit

        cursor2=collection3.find({
            "userid":userid
        },sort=[
            ("_id",pymongo.DESCENDING)
        ])
        date3=[]
        for doc in cursor2: 
            date3.append(doc["date"])

        cursor=collection3.find({
            "userid":userid
        },sort=[
            ("_id",pymongo.DESCENDING)
        ]).skip(skip).limit(limit)
        article=[]
        people1_lengths=[]
        message2_lengths=[]
        date=[]
        date2=[]
        for doc in cursor: 
            article.append(doc["article"])
            people1_lengths.append(len(doc["heart_icon"]))
            message2_lengths.append(len(doc["message"]))
            date.append(doc["date"])
            datetime_obj = datetime.strptime(doc["date"], "%Y/%m/%d %H:%M:%S.%f")
            datetime_obj2 = datetime.now()
            # 计算年、月、日、小时和分钟差异
            years = datetime_obj2.year - datetime_obj.year
            months = datetime_obj2.month - datetime_obj.month
            days = datetime_obj2.day - datetime_obj.day
            hours = datetime_obj2.hour - datetime_obj.hour
            minutes = datetime_obj2.minute - datetime_obj.minute

            # 處理負值
            if minutes < 0:
                minutes += 60
                hours -= 1
            if hours < 0:
                hours += 24
                days -= 1
            if days < 0:
                previous_month_days = (datetime(datetime_obj2.year, datetime_obj2.month, 1) - timedelta(days=1)).day
                days += previous_month_days
                months -= 1
            if months < 0:
                months += 12
                years -= 1

            # 格式化時間差
            if years > 0 or months > 0:
                formatted_time_difference = f"{datetime_obj.year}年{datetime_obj.month}月{datetime_obj.day}日"
            elif days > 0:
                formatted_time_difference = f"{days}天前"
            else:
                formatted_time_difference = ""
                if hours > 0:
                    if minutes >= 30:
                        hours += 1
                    formatted_time_difference += f"{hours}小時"
                elif minutes > 0:
                    formatted_time_difference += f"{minutes}分鐘"
                if formatted_time_difference:
                    formatted_time_difference += "前"
                else:
                    formatted_time_difference = "剛剛"

            date2.append(formatted_time_difference)
        result=collection.find_one({
            "userid":userid
        })
        photo=result["photo"]
        nickname=result["nickname"]
        messageboard=result["messageboard"]
        track=result["track"]
        fans=result["fans"]

        Email=session["userID"]
        result2=collection.find_one({
            "Email":Email
        })
        heart_icon3=result2["heart_icon3"]
        track2=result2["track"]
    return jsonify(article , heart_icon3 , date , people1_lengths , message2_lengths , photo , nickname , messageboard , date2 , track , fans , track2 , date3)

#刪私人文章
@app.route("/member/article_private_delete", methods=['POST'])
def member_article_private_delete():
    date = request.form["date"]
    ###刪留言紀錄
    for doc in collection.find({"message_article": date}):
        indexes = [i for i, u in enumerate(doc["message_article"]) if u == date]
        for index in indexes:
            doc["message"][index] = ''
            doc["message_date"][index] = ''
        collection.update_one({"_id": doc["_id"]}, {"$set": {"message": doc["message"]}})
        collection.update_one({"_id": doc["_id"]}, {"$set": {"message_date": doc["message_date"]}})

    collection.update_many(
        {"message": ""},
        {"$pull": {"message": ""}}
    )
    collection.update_many(
        {"message_date": ""},
        {"$pull": {"message_date": ""}}
    )

    collection.update_many(
        {"message_article":date},
        {"$pull": {"message_article": date}}
    )
    ###刪愛心渲染
    collection.update_many({},
        {'$pull': {'heart_icon': date}}
    )
    collection.update_many({},
        {'$pull': {'heart_icon2': date}}
    )

    ##
    collection3.delete_one({
        "date":date
    })

    return redirect(url_for('member',name="name"))

##手機號碼
@app.route("/member/phone",methods=["POST"])
def member_phone():
    phone=request.form["phone"]
    Email=session["userID"]
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "phone":phone
        }
    })
    return redirect("/success/member?msg=修改成功&msg2=")

##改密碼
@app.route("/member/password",methods=["POST"])
def member_password():
    password=request.form["update_password"]
    Email=session["userID"]
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "password":password
        }
    })
    return redirect("/success/member?msg=修改成功&msg2=&")

##帳號註銷
@app.route("/member/delete",methods=["POST"])
def member_delete():
    userid=request.form["confirm_delete_userid"]
###
    result=collection.find_one({
       "userid":userid
    })
    photo=result["photo"]

    for doc in collection3.find({"message_user": userid}):
        indexes = [i for i, u in enumerate(doc["message_user"]) if u == userid]
        for index in indexes:
            doc["message"][index] = ''
            doc["message_photo"][index] = ''
            doc["message_article_date"][index] = ''
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message": doc["message"]}})
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_photo": doc["message_photo"]}})
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_article_date": doc["message_article_date"]}})
 

    collection3.update_many(
        {"message": ""},
        {"$pull": {"message": ""}}
    )
    collection3.update_many(
        {"message_photo": ""},
        {"$pull": {"message_photo": ""}}
    )
    collection3.update_many(
        {"message_article_date": ""},
        {"$pull": {"message_article_date": ""}}
    )
    collection3.update_many(
        {"message_user":userid},
        {"$pull": {"message_user": userid}}
    )
    


    collection3.update_many(
        {"heart_icon": userid},
        {"$unset": {"heart_icon.$": ''}}
    )
    collection3.update_many(
        {},
        {"$pull": {"heart_icon": None}}
    )
    collection3.update_many(
        {"heart_icon_photo": photo},
        {"$unset": {"heart_icon_photo.$": ''}}
    )
    collection3.update_many(
        {},
        {"$pull": {"heart_icon_photo": None}}
    )

###刪別人user裡的歷史紀錄
    for doc in collection.find({"history": userid}):
        indexes = [i for i, u in enumerate(doc["history"]) if u == userid]
        for index in indexes:
            doc["history_photo"][index] = ''
        collection.update_one({"_id": doc["_id"]}, {"$set": {"history_photo": doc["history_photo"]}})
    collection.update_many(
        {"history_photo": ""},
        {"$pull": {"history_photo": ""}}
    )
    collection.update_many(
        {"history":userid},
        {"$pull": {"history": userid}}
    )
###刪別人user裡的追蹤
    for doc in collection.find({"track": userid}):
        indexes = [i for i, u in enumerate(doc["track"]) if u == userid]
        for index in indexes:
            doc["track_photo"][index] = ''
        collection.update_one({"_id": doc["_id"]}, {"$set": {"track_photo": doc["track_photo"]}})
    collection.update_many(
        {"track_photo": ""},
        {"$pull": {"track_photo": ""}}
    )
    collection.update_many(
        {"track":userid},
        {"$pull": {"track": userid}}
    )
###刪別人user裡的粉絲
    for doc in collection.find({"fans": userid}):
        indexes = [i for i, u in enumerate(doc["fans"]) if u == userid]
        for index in indexes:
            doc["fans_photo"][index] = ''
        collection.update_one({"_id": doc["_id"]}, {"$set": {"fans_photo": doc["fans_photo"]}})
    collection.update_many(
        {"fans_photo": ""},
        {"$pull": {"fans_photo": ""}}
    )
    collection.update_many(
        {"fans":userid},
        {"$pull": {"fans": userid}}
    )
###
    collection3.delete_many({
        "userid":userid
    })
    collection.delete_one({
        "userid":userid
    })
    del session["userID"]
    resp = make_response(redirect("/success?msg=註銷成功&msg2=感謝您對我們的支持"))
    resp.set_cookie('userID', '', max_age=0)
    return resp

##改暱稱
@app.route("/member/nickname",methods=["POST"])
def member_nickname():
    nickname=request.form["nickname"]
    Email=session["userID"]
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "nickname":nickname
        }
    })
    return redirect(url_for('member',name="name"))

##改留言板
@app.route("/member/messageboard",methods=["POST"])
def member_messageboard():
    messageboard=request.form["messageboard"]
    Email=session["userID"]
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "messageboard":messageboard
        }
    })
    return redirect(url_for('member',name="name"))

##登出
@app.route("/signout")
def signout():
    del session["userID"]
    resp = make_response(redirect("/"))
    resp.set_cookie('userID', '', max_age=0)
    return resp

##改頭貼
app.config['UPLOAD_FOLDER'] = 'static/photo'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['JSON_AS_ASCII'] = False
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
@app.route('/member/photo', methods=['POST'])
def member_photo():
    #本地
    photo = request.files['selectedFile']
    date = datetime.now().strftime('%Y.%m%d.%H%M.%S.')
    filename = date+secure_filename(photo.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(filepath)
    #資料庫
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
######愛心留言
    for doc in collection3.find({"heart_icon": userid}):
        indexes = [i for i, u in enumerate(doc["heart_icon"]) if u == userid]
        for index in indexes:
            doc["heart_icon_photo"][index] = filename
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"heart_icon_photo": doc["heart_icon_photo"]}})
    for doc in collection3.find({"message_user": userid}):
        indexes = [i for i, u in enumerate(doc["message_user"]) if u == userid]
        for index in indexes:
            doc["message_photo"][index] = filename
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_photo": doc["message_photo"]}})
######追蹤粉絲
    for doc in collection.find({"fans": userid}):
        indexes = [i for i, u in enumerate(doc["fans"]) if u == userid]
        for index in indexes:
            doc["fans_photo"][index] = filename
        collection.update_one({"_id": doc["_id"]}, {"$set": {"fans_photo": doc["fans_photo"]}})

    for doc in collection.find({"track": userid}):
        indexes = [i for i, u in enumerate(doc["track"]) if u == userid]
        for index in indexes:
            doc["track_photo"][index] = filename
        collection.update_one({"_id": doc["_id"]}, {"$set": {"track_photo": doc["track_photo"]}})

######歷史紀錄
    for doc in collection.find({"history": userid}):
        indexes = [i for i, u in enumerate(doc["history"]) if u == userid]
        for index in indexes:
            doc["history_photo"][index] = filename
        collection.update_one({"_id": doc["_id"]}, {"$set": {"history_photo": doc["history_photo"]}})

######
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "photo":filename
        }
    })
    collection3.update_many({
        "userid":userid
    },{
        "$set":{
            "photo":filename
        }
    })



#愛心公(1)
@app.route('/member/heart_icon_public', methods=['POST'])
def member_heart_icon_public(): 
    Email=session["userID"] 
    date=request.form["date"]
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon': date}}
    )
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    result3=collection.find_one({
        "Email":Email
    })
    track=result3["track"]
    cursor2=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    date3=[]
    for doc in cursor: 
        date2.append(doc["date"])
    for doc in cursor2: 
        date3.append(doc["date"])

    if date in date2:
        collection.update_one(
            {"Email":Email},
            {'$push': {'heart_icon2': date}}
        )
    if date not in date2:
        collection.update_one(
            {"Email":Email},
            {'$push': {'heart_icon3': date}}
        )
        if date in date3:
            collection.update_one(
                {"Email":Email},
                {'$push': {'heart_icon_track': date}}
            )

    heart_icon=request.form["heart_icon"]
    result2=collection.find_one(
        {"userid":heart_icon}
    )
    photo=result2["photo"]
    result=collection3.find_one(
        {"date":date}
    )
    if heart_icon not in result['heart_icon']:
        collection3.update_one(
            {"date":date},
            {"$push": {"heart_icon": heart_icon}}  
        )
        collection3.update_one(
            {"date":date},
            {"$push": {"heart_icon_photo": photo}}  
        )
    ##通知##
    result3=collection3.find_one({
        "date":date
    })
    userid3=result3["userid"]
    date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date2}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "0"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":"_ @" }}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )
    ###
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])

    ##私人愛心分配
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date=[]
    people_private=[]
    for doc in cursor: 
        date.append(doc["date"])
        people_private.append(doc["heart_icon"])
    ##追蹤愛心分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["heart_icon"])

    ##查詢愛心分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["heart_icon"])
    return jsonify(people1,date,people_private,date2,people_track,date3,people_search)
    
#愛心公(2)
@app.route('/member/unheart_icon_public', methods=['POST'])
def member_unheart_icon_public():  
    Email=session["userID"] 
    date=request.form["date"]
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon':date}}
    )

    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    result3=collection.find_one({
        "Email":Email
    })
    track=result3["track"]
    cursor2=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date3=[]
    date2=[]

    for doc in cursor: 
        date2.append(doc["date"])
    for doc in cursor2: 
        date3.append(doc["date"])

    if date in date2:
        collection.update_one(
            {"Email":Email},
            {'$pull': {'heart_icon2': date}}
        )
    if date not in date2:
        collection.update_one(
                {"Email":Email},
                {'$pull': {'heart_icon3':date}}
            )
        if date  in date3:
            collection.update_one(
                {"Email":Email},
                {'$pull': {'heart_icon_track':date}}
            )
            

    heart_icon=request.form["heart_icon"]
    result=collection3.find_one(
        {"date":date}
    )
    if heart_icon  in result['heart_icon']:
        for doc in collection3.find({"date":date}):
            indexes = [i for i, u in enumerate(doc["heart_icon"]) if u == heart_icon]
            for index in indexes:
                doc["heart_icon_photo"][index] = ""
            collection3.update_one({"_id": doc["_id"]}, {"$set": {"heart_icon_photo": doc["heart_icon_photo"]}})
        collection3.update_one(
            {"date":date},
            {"$pull": {"heart_icon_photo": ""}}
        )
        collection3.update_one(
            {"date":date},
            {"$pull": {"heart_icon": heart_icon}}
        )
    ###
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])

    ##私人愛心分配
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date=[]
    people_private=[]
    for doc in cursor: 
        date.append(doc["date"])
        people_private.append(doc["heart_icon"])
    ##追蹤愛心分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["heart_icon"])

    ##查詢愛心分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["heart_icon"])
    return jsonify(people1,date,people_private,date2,people_track,date3,people_search)
    
#愛心公2(1)
@app.route('/member/heart_icon_public2', methods=['POST'])
def member_heart_icon_public2():  
    Email=session["userID"] 
    date=request.form["date"]
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon_track': date}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon': date}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon3': date}}
    )
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date2=[]
    for doc in cursor: 
        date2.append(doc["date"])
    if date in date2:
        collection.update_one(
            {"Email":Email},
            {'$push': {'heart_icon2': date}}
        )
    heart_icon=request.form["heart_icon"]
    result2=collection.find_one(
        {"userid":heart_icon}
    )
    photo=result2["photo"]
    result=collection3.find_one(
        {"date":date}
    )
    if heart_icon not in result['heart_icon']:
        collection3.update_one(
            {"date":date},
            {"$push": {"heart_icon": heart_icon}}  
        )
        collection3.update_one(
            {"date":date},
            {"$push": {"heart_icon_photo": photo}}  
        )
    ##通知##
    result3=collection3.find_one({
        "date":date
    })
    userid3=result3["userid"]
    date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date2}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "0"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":"_ @" }}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )
    ###
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])
    ##查詢愛心分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["heart_icon"])
    return jsonify(people1,date1,people_public,date3,people_search)
    
#愛心公2(2)
@app.route('/member/unheart_icon_public2', methods=['POST'])
def member_unheart_icon_public2():  
    Email=session["userID"] 
    date=request.form["date"]
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon_track':date}}
    )
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon':date}}
    )
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon3':date}}
    )
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date2=[]

    for doc in cursor: 
        date2.append(doc["date"])
    if date in date2:
        collection.update_one(
            {"Email":Email},
            {'$pull': {'heart_icon2': date}}
        )
    heart_icon=request.form["heart_icon"]
    result=collection3.find_one(
        {"date":date}
    )
    if heart_icon  in result['heart_icon']:
        for doc in collection3.find({"date":date}):
            indexes = [i for i, u in enumerate(doc["heart_icon"]) if u == heart_icon]
            for index in indexes:
                doc["heart_icon_photo"][index] = ""
            collection3.update_one({"_id": doc["_id"]}, {"$set": {"heart_icon_photo": doc["heart_icon_photo"]}})
        collection3.update_one(
            {"date":date},
            {"$pull": {"heart_icon_photo": ""}}
        )
        collection3.update_one(
            {"date":date},
            {"$pull": {"heart_icon": heart_icon}}
        )
    ###
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])

    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])
    ##查詢愛心分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["heart_icon"])
    return jsonify(people1,date1,people_public,date3,people_search)
    


#愛心私(1)
@app.route('/member/heart_icon_private', methods=['POST'])
def member_heart_icon_private():  
    Email=session["userID"] 
    date2=request.form["date2"]
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon2': date2}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon': date2}}
    )
    heart_icon=request.form["heart_icon"]
    result3=collection.find_one(
        {"userid":heart_icon}
    )
    photo=result3["photo"]
    result=collection3.find_one({
        'heart_icon': heart_icon
    })
    if result==None:
        collection3.update_one(
            {"date":date2},
            {'$push': {'heart_icon': heart_icon}}
        )
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon_photo": photo}} , 
        )
    result2=collection3.find_one(
        {"date":date2}
    )
    
    if heart_icon not in result2['heart_icon']:
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon": heart_icon}},
        )
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon_photo": photo}} , 
        )
    ###
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
    
    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])
    return jsonify(people1,date1,people_public)

#愛心私(2)
@app.route('/member/unheart_icon_private', methods=['POST'])
def member_unheart_icon_private():  
    Email=session["userID"] 
    date2=request.form["date2"]
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon2': date2}}
    )
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon': date2}}
    )
    heart_icon=request.form["heart_icon"]
    for doc in collection3.find({"date":date2}):
        indexes = [i for i, u in enumerate(doc["heart_icon"]) if u == heart_icon]
        for index in indexes:
            doc["heart_icon_photo"][index] = ""
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"heart_icon_photo": doc["heart_icon_photo"]}})
    collection3.update_one(
        {"date":date2},
        {"$pull": {"heart_icon_photo": ""}}
    )
    collection3.update_one(
        {"date":date2},
        {"$pull": {"heart_icon": heart_icon}}
    )
    ###
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])

    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])
    return jsonify(people1,date1,people_public)
    
#愛心查(1)
@app.route('/member/heart_icon_search/<search>', methods=['POST'])
def member_heart_icon_userid(search): 
    Email=session["userID"] 
    date2=request.form["date2"]
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon3': date2}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'heart_icon': date2}}
    )

    result3=collection.find_one({
        "Email":Email
    })
    track=result3["track"]
    cursor2=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date3=[]
    for doc in cursor2: 
        date3.append(doc["date"])
    if date2 in date3:
        collection.update_one(
            {"Email":Email},
            {'$push': {'heart_icon_track': date2}}
        )
    
    heart_icon=request.form["heart_icon"]
    result3=collection.find_one(
        {"userid":heart_icon}
    )
    photo=result3["photo"]
    result=collection3.find_one({
        'heart_icon': heart_icon
    })
    if result==None:
        collection3.update_one(
            {"date":date2},
            {'$push': {'heart_icon': heart_icon}}
        )
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon_photo": photo}} , 
        )
    result2=collection3.find_one(
        {"date":date2}
    )
    
    if heart_icon not in result2['heart_icon']:
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon": heart_icon}},
        )
        collection3.update_one(
            {"date":date2},
            {"$push": {"heart_icon_photo": photo}} , 
        )
    
    ##通知##
    result4=collection.find_one({
        "Email":Email
    })
    userid=result4["userid"]
    date=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    result5=collection3.find_one({
        "date":date2
    })
    userid3=result5["userid"]
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "0"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":"_ @" }}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )
    ###
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
    
    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])

    ##追蹤愛心分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["heart_icon"])
    
    return jsonify(people1,date1,people_public,date2,people_track)
    
#愛心查(2)
@app.route('/member/unheart_icon_search/<search>', methods=['POST'])
def member_unheart_icon_userid(search):  
    Email=session["userID"] 
    date2=request.form["date2"]
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon3': date2}}
    )
    collection.update_one(
        {"Email":Email},
        {'$pull': {'heart_icon': date2}}
    )


    result3=collection.find_one({
        "Email":Email
    })
    track=result3["track"]
    cursor2=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date3=[]
    for doc in cursor2: 
        date3.append(doc["date"])
    if date2 in date3:
        collection.update_one(
            {"Email":Email},
            {'$pull': {'heart_icon_track': date2}}
        )

    heart_icon=request.form["heart_icon"]
    for doc in collection3.find({"date":date2}):
        indexes = [i for i, u in enumerate(doc["heart_icon"]) if u == heart_icon]
        for index in indexes:
            doc["heart_icon_photo"][index] = ""
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"heart_icon_photo": doc["heart_icon_photo"]}})
    collection3.update_one(
        {"date":date2},
        {"$pull": {"heart_icon_photo": ""}}
    )
    collection3.update_one(
        {"date":date2},
        {"$pull": {"heart_icon": heart_icon}}
    )
    ###
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])

    ###公開愛心分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["heart_icon"])

    ##追蹤愛心分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["heart_icon"])
    
    return jsonify(people1,date1,people_public,date2,people_track)
    
##移除大頭貼
@app.route('/member/delete_photo', methods=['POST'])
def member_delete_photo():
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    ###愛心留言
    photo=result["photo"]
    userid=result["userid"]
    collection3.update_many(
        {"heart_icon_photo": photo},
        {"$set": {"heart_icon_photo.$": "astronaut.png"}}
    )
    for doc in collection3.find({"message_user": userid}):
        indexes = [i for i, u in enumerate(doc["message_user"]) if u == userid]
        for index in indexes:
            doc["message_photo"][index] = "astronaut.png"
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_photo": doc["message_photo"]}})
    ###追蹤粉絲
    for doc in collection.find({"track": userid}):
        indexes = [i for i, u in enumerate(doc["track"]) if u == userid]
        for index in indexes:
            doc["track_photo"][index] = "astronaut.png"
        collection.update_one({"_id": doc["_id"]}, {"$set": {"track_photo": doc["track_photo"]}})
    for doc in collection.find({"fans": userid}):
        indexes = [i for i, u in enumerate(doc["fans"]) if u == userid]
        for index in indexes:
            doc["fans_photo"][index] = "astronaut.png"
        collection.update_one({"_id": doc["_id"]}, {"$set": {"fans_photo": doc["fans_photo"]}})
    ###歷史紀錄
    for doc in collection.find({"history": userid}):
        indexes = [i for i, u in enumerate(doc["history"]) if u == userid]
        for index in indexes:
            doc["history_photo"][index] = "astronaut.png"
        collection.update_one({"_id": doc["_id"]}, {"$set": {"history_photo": doc["history_photo"]}})
    ###
    collection.update_one({
        "Email":Email
    },{
        "$set":{
            "photo":"astronaut.png"
        }
    })
    userid=result["userid"]
    collection3.update_many({
        "userid":userid
    },{
        "$set":{
            "photo":"astronaut.png"
        }
    })


    
    return redirect(url_for('member',name="name"))

##建立貼文
@app.route('/member/edit_article', methods=['POST'])
def member_edit_article():
    Email=session["userID"]
    article=request.form["edit_article"]
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    photo=result["photo"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    collection3.insert_one({
        "userid":userid,
        "article":article,
        "photo":photo,
        "heart_icon":[],
        "heart_icon_photo":[],
        "date":date,
        "message":[],
        "message_user":[],
        "message_photo":[],
        "message_article_date":[]
    })
    return redirect("/member")

#留言公
@app.route('/member/message', methods=['POST'])
def member_message():
    message=request.form["message"]
    message2=request.form["message2"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    Email=session["userID"]
    result=collection.find_one({
       "Email":Email 
    })
    userid=result["userid"]
    photo=result["photo"]
    collection3.update_one(
        {"date":message2},
        {'$push': {'message': message}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_user': userid}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_photo': photo}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message':message }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_article':message2 }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_date':date }}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_article_date':date}}
    )
  
    ##通知##
    result5=collection3.find_one({
        "date":message2
    })
    userid3=result5["userid"]
    date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date2}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "1"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":message}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )

    ##公開
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    message2=[]
    for doc in cursor: 
        message2.append(doc["message"])

    ##私人留言分配
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date=[]
    people_private=[]
    for doc in cursor: 
        date.append(doc["date"])
        people_private.append(doc["message"])
    ##追蹤留言分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["message"])

    ##查詢留言分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["message"])

    return jsonify(message2,date,people_private,date2,people_track,date3,people_search)

#留言公2
@app.route('/member/message_track', methods=['POST'])
def member_message_track():
    message=request.form["message"]
    message2=request.form["message2"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    Email=session["userID"]
    result=collection.find_one({
       "Email":Email 
    })
    userid=result["userid"]
    photo=result["photo"]
    collection3.update_one(
        {"date":message2},
        {'$push': {'message': message}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_user': userid}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_photo': photo}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message':message }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_article':message2 }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_date':date }}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_article_date':date}}
    )
  
    ##通知##
    result5=collection3.find_one({
        "date":message2
    })
    userid3=result5["userid"]
    date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date2}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "1"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":message}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )

    ##追蹤
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor_track=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    message2_track=[]
    for doc in cursor_track: 
        message2_track.append(doc["message"])

    ###公開留言分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["message"])
    ##查詢留言分配
    search = request.form.get('search', default=None)
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    date3=[]
    people_search=[]
    for doc in cursor: 
        date3.append(doc["date"])
        people_search.append(doc["message"])

    return jsonify(message2_track,date1,people_public,date3,people_search)
#留言私
@app.route('/member/message_name', methods=['POST'])
def member_message_name():
    message=request.form["message"]
    message2=request.form["message2"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    Email=session["userID"]
    result=collection.find_one({
       "Email":Email 
    })
    userid=result["userid"]
    photo=result["photo"]
    collection3.update_one(
        {"date":message2},
        {'$push': {'message': message}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_user': userid}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_photo': photo}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message':message }}
    )

    collection.update_one(
        {"Email":Email},
        {'$push': {'message_article':message2 }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_date':date }}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_article_date':date}}
    )
    ###
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    message2=[]
    for doc in cursor: 
        message2.append(doc["message"])
    ###公開留言分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["message"])
    return jsonify(message2,date1,people_public)

#留言查
@app.route('/member/message_name2/<search>', methods=['POST'])
def member_message_name2(search):
    message=request.form["message"]
    message2=request.form["message2"]
    date = datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    Email=session["userID"]
    result=collection.find_one({
       "Email":Email 
    })
    userid=result["userid"]
    photo=result["photo"]
    collection3.update_one(
        {"date":message2},
        {'$push': {'message': message}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_user': userid}}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_photo': photo}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message':message }}
    )

    collection.update_one(
        {"Email":Email},
        {'$push': {'message_article':message2 }}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'message_date':date }}
    )
    collection3.update_one(
        {"date":message2},
        {'$push': {'message_article_date':date}}
    )
    ##通知##
    result5=collection3.find_one({
        "date":message2
    })
    userid3=result5["userid"]
    date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    if userid3!=userid:
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify": userid}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_date": date2}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_class": "1"}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$push": {"notify_article":message}}  
        )
        collection.update_one(
            {"userid":userid3},
            {"$set": {"notify_dot": "true"}}
        )
    ###
    cursor=collection3.find({
        "userid":search
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    message2=[]
    for doc in cursor: 
        message2.append(doc["message"])

    ###公開留言分配
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date1=[]
    people_public=[]
    for doc in cursor: 
        date1.append(doc["date"])
        people_public.append(doc["message"])

    ##追蹤留言分配
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    date2=[]
    people_track=[]
    for doc in cursor: 
        date2.append(doc["date"])
        people_track.append(doc["message"])

    return jsonify(message2,date1,people_public,date2,people_track)

##編輯文章
@app.route('/member/article_private_edit', methods=['POST'])
def member_article_private_edit():
    date=request.form["date"]
    edit=request.form["edit"]
    collection3.update_one(
        {"date":date},
        {'$set': {'article':edit }}
    )
    return redirect(url_for('member',name="name"))

##留言紀錄
@app.route('/member/messagerecord', methods=['POST'])
def member_messagerecord():
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    message_record=result["message"]
    message_article=result["message_article"]
    message_date=result["message_date"]
    userid2 = []
    for date in message_article:
        # 单独查找每个日期的所有匹配文档
        results = collection3.find({"date": date})
        for result in results:
            if "userid" in result:
                userid2.append(result["userid"])

    message_record = message_record[::-1]
    message_date = message_date[::-1]
    userid2 = userid2[::-1]
    return jsonify(message_record,message_date,userid2)

##刪除留言紀錄
@app.route('/member/deletemessagerecord', methods=['POST'])
def member_deletemessagerecord():
    checkboxdate=request.form["checkboxdate"]
    for doc in collection.find({"message_date": checkboxdate}):
        indexes = [i for i, u in enumerate(doc["message_date"]) if u == checkboxdate]
        for index in indexes:
            doc["message_article"][index] = ''
            doc["message"][index] = ''
        collection.update_one({"_id": doc["_id"]}, {"$set": {"message_article": doc["message_article"]}})
        collection.update_one({"_id": doc["_id"]}, {"$set": {"message": doc["message"]}})
    collection.update_many(
        {"message_article": ""},
        {"$pull": {"message_article": ""}}
    )
    collection.update_many(
        {"message": ""},
        {"$pull": {"message": ""}}
    )
    collection.update_many(
        {"message_date": checkboxdate},
        {"$pull": {"message_date": checkboxdate}}
    )


    for doc in collection3.find({"message_article_date": checkboxdate}):
        indexes = [i for i, u in enumerate(doc["message_article_date"]) if u == checkboxdate]
        for index in indexes:
            doc["message_user"][index] = ''
            doc["message_photo"][index] = ''
            doc["message"][index] = ''
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_user": doc["message_user"]}})
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message_photo": doc["message_photo"]}})
        collection3.update_one({"_id": doc["_id"]}, {"$set": {"message": doc["message"]}})
    
    collection3.update_many(
        {"message_user": ""},
        {"$pull": {"message_user": ""}}
    )
    collection3.update_many(
        {"message_photo": ""},
        {"$pull": {"message_photo": ""}}
    )
    collection3.update_many(
        {"message": ""},
        {"$pull": {"message": ""}}
    )
    collection3.update_many(
        {"message_article_date": checkboxdate},
        {"$pull": {"message_article_date": checkboxdate}}
    )
    return redirect(url_for('member',name="name"))

##非本人用戶(查詢用)
@app.route('/member/search', methods=['POST'])
def member_search():
    Email=session["userID"]
    result=collection.find_one({
       "Email":Email 
    })
    userid=result["userid"]
    cursor2=collection.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    userid2=[]
    photo2=[]
    for doc in cursor2:
        if doc["userid"] != userid:  # 过滤掉当前用户的文档
            userid2.append(doc["userid"])
            photo2.append(doc["photo"])
    return jsonify(userid2,photo2)

##歷史紀錄
@app.route('/member/rememberhistory', methods=['POST'])
def member_rememberhistory():
    Email=session["userID"]
    history=request.form["history"]
    history_photo=request.form["history_photo"]

    collection.update_one(
        {"Email":Email},
        {'$push': {'history':history}}
    )
    collection.update_one(
        {"Email":Email},
        {'$push': {'history_photo':history_photo}}
    )
    result=collection.find_one(
        {"Email":Email}
    )
    history2=result["history"]
    history_photo2=result["history_photo"]
    return jsonify(history2,history_photo2)


##刪除歷史紀錄
@app.route('/member/deletehistory', methods=['POST'])
def member_deletehistory():
    Email = session["userID"]
    deletehistory = request.form["deletehistory"]

    # 查找需要更新的文档
    docs = collection.find({"history": deletehistory, "Email": Email})

    # 更新找到的每个文档
    for doc in docs:
        indexes = [i for i, u in enumerate(doc["history"]) if u == deletehistory]
        for index in indexes:
            doc["history_photo"][index] = ""

        # 更新带有修改后的 history_photo 和 history 字段的文档
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"history_photo": doc["history_photo"]}}
        )

    # 删除所有空的 history_photo
    collection.update_many(
        {"history_photo": ""},
        {"$pull": {"history_photo": ""}}
    )

    # 从 history 中删除指定的条目
    collection.update_one(
        {"Email": Email},
        {'$pull': {'history': deletehistory}}
    )

##刪除通知
@app.route('/member/deletenotify', methods=['POST'])
def member_deletenotify():
    notify_date=request.form["notify_date"]
    for doc in collection.find({"notify_date": notify_date}):
        indexes = [i for i, u in enumerate(doc["notify_date"]) if u == notify_date]
        for index in indexes:
            doc["notify"][index] = ""
            doc["notify_class"][index] = ""
            doc["notify_article"][index] = ""
        collection.update_one({"_id": doc["_id"]}, {"$set": {"notify": doc["notify"]}})
        collection.update_one({"_id": doc["_id"]}, {"$set": {"notify_class": doc["notify_class"]}})
        collection.update_one({"_id": doc["_id"]}, {"$set": {"notify_article": doc["notify_article"]}})

    collection.update_many(
        {"notify": ""},
        {"$pull": {"notify": ""}}
    )
    collection.update_many(
        {"notify_class": ""},
        {"$pull": {"notify_class": ""}}
    )
    collection.update_many(
        {"notify_article": ""},
        {"$pull": {"notify_article": ""}}
    )
    collection.update_one(
        {"notify_date":notify_date},
        {'$pull': {'notify_date':notify_date}}
    )

    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    notify=result["notify"]
    return jsonify(notify)

##通知
@app.route("/member/notify", methods=['POST'])
def member_notify():
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })

    notify=result["notify"]
    notify_class=result["notify_class"]
    notify_date2=result["notify_date"]
    notify_article=result["notify_article"]
    
    f=[]
    for notify_date in notify_date2:
        d1 = datetime.strptime(notify_date, "%Y/%m/%d %H:%M:%S.%f")
        d2 = datetime.now()
        # 计算年、月、日、小时和分钟差异
        years = d2.year - d1.year
        months = d2.month - d1.month
        days = d2.day - d1.day
        hours = d2.hour - d1.hour
        minutes = d2.minute - d1.minute

        # 處理負值
        if minutes < 0:
            minutes += 60
            hours -= 1
        if hours < 0:
            hours += 24
            days -= 1
        if days < 0:
            previous_month_days = (datetime(d2.year, d2.month, 1) - timedelta(days=1)).day
            days += previous_month_days
            months -= 1
        if months < 0:
            months += 12
            years -= 1

        # 格式化時間差
        if years > 0 or months > 0:
            formatted_time_difference = f"{d1.year}年{d1.month}月{d1.day}日"
        elif days > 0:
            formatted_time_difference = f"{days}天前"
        else:
            formatted_time_difference = ""
            if hours > 0:
                if minutes >= 30:
                    hours += 1
                formatted_time_difference += f"{hours}小時"
            elif minutes > 0:
                formatted_time_difference += f"{minutes}分鐘"
            if formatted_time_difference:
                formatted_time_difference += "前"
            else:
                formatted_time_difference = "剛剛"
        f.append(formatted_time_difference)

    return jsonify(notify,notify_class,notify_date2,f,notify_article)



##悄悄話
@app.route('/member/whisper', methods=['POST'])
def member_whisper():
    whisper=request.form["whisper"]
    whisper_name=request.form["whisper_name"]
    date=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    Email=session["userID"] 
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    if whisper_name!=userid:
            collection.update_one(
                {"userid":whisper_name},
                {"$push": {"notify": userid}}  
            )
            collection.update_one(
                {"userid":whisper_name},
                {"$push": {"notify_date": date}}  
            )
            collection.update_one(
                {"userid":whisper_name},
                {"$push": {"notify_class": "2"}}  
            )
            collection.update_one(
                {"userid":whisper_name},
                {"$push": {"notify_article":whisper }}  
            )
            collection.update_one(
                {"userid":whisper_name},
                {"$set": {"notify_dot": "true"}}
            )

    return redirect(url_for('member',name2="name2"))

##追蹤帳號
@app.route('/member/track', methods=['POST'])
def member_track():
    try:
        track = request.form["track"]
        userid = request.form["userid"]

        # 檢查必要的字段是否存在
        if not track or not userid:
            return jsonify({"error": "Track and userid are required"}), 400

        # 查詢用戶和追蹤對象
        result = collection.find_one({"userid": userid})
        result2 = collection.find_one({"userid": track})

        if not result or not result2:
            return jsonify({"error": "User or track not found"}), 404

        track_photo = result2.get("photo", "")
        photo = result.get("photo", "")


        cursor=collection3.find({
            "userid":track
        })
        result_userid=collection.find_one({
            "userid":userid
        })
        result_userid_heart_icon=result_userid["heart_icon"]
        date_trackall=[]
        for doc in cursor: 
            date_trackall.append(doc["date"])

        common_dates = [date for date in date_trackall if date in result_userid_heart_icon]

        # 更新操作
        if track in result.get("track", []):
            #track
            doc = collection.find_one({"track": track, "userid": userid})
            if doc:
                indexes = [i for i, u in enumerate(doc["track"]) if u == track]
                for index in indexes:
                    doc["track_photo"][index] = ''
                collection.update_one({"_id": doc["_id"]}, {"$set": {"track_photo": doc["track_photo"]}})
                collection.update_many({"track_photo": ""}, {"$pull": {"track_photo": ""}})
                collection.update_one({"_id": doc["_id"]}, {"$pull": {"track": track}})
            #fans   
            doc = collection.find_one({"fans": userid, "userid": track})
            if doc:
                indexes = [i for i, u in enumerate(doc["fans"]) if u == userid]
                for index in indexes:
                    doc["fans_photo"][index] = ''
                collection.update_one({"_id": doc["_id"]}, {"$set": {"fans_photo": doc["fans_photo"]}})
                collection.update_many({"fans_photo": ""}, {"$pull": {"fans_photo": ""}})
                collection.update_one({"_id": doc["_id"]}, {"$pull": {"fans": userid}})


            #愛心轉出
            for date in common_dates:
                collection.update_one(
                    {"userid": userid},
                    {"$pull": {"heart_icon_track": date}}
                )
        else:
            # 添加追蹤對象到用戶的追蹤列表
            collection.update_one({"userid": userid}, {"$push": {"track": track}})
            # 添加用戶到追蹤對象的粉絲列表
            collection.update_one({"userid": track}, {"$push": {"fans": userid}})
            # 添加追蹤對象的照片到用戶的追蹤照片列表
            collection.update_one({"userid": userid}, {"$push": {"track_photo": track_photo}})
            # 添加用戶的照片到追蹤對象的粉絲照片列表
            collection.update_one({"userid": track}, {"$push": {"fans_photo": photo}})
            
            ##通知##
            date2=datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
            collection.update_one(
                {"userid":track},
                {"$push": {"notify": userid}}  
            )
            collection.update_one(
                {"userid":track},
                {"$push": {"notify_date": date2}}  
            )
            collection.update_one(
                {"userid":track},
                {"$push": {"notify_class": "3"}}  
            )
            collection.update_one(
                {"userid":track},
                {"$push": {"notify_article":"_ @2"}}  
            )
            collection.update_one(
                {"userid":track},
                {"$set": {"notify_dot": "true"}}
            )
            ###
            #愛心轉入
            for date in common_dates:
                collection.update_one(
                    {"userid": userid},
                    {"$push": {"heart_icon_track": date}}
                )



        return jsonify({"message": "Track updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


##渲染對方追蹤
@app.route('/member/trackpeople', methods=['POST'])
def member_trackpeople():
    track=request.form["track"]
    result=collection.find_one({
        "userid":track
    })

    result["track"]=result["track"][::-1]
    result["track_photo"]=result["track_photo"][::-1]
    return jsonify(result["track"],result["track_photo"])
##渲染對方粉絲
@app.route('/member/fanspeople', methods=['POST'])
def member_fanspeople():
    fans=request.form["fans"]
    result=collection.find_one({
        "userid":fans
    })
    result["fans"]=result["fans"][::-1]
    result["fans_photo"]=result["fans_photo"][::-1]
    return jsonify(result["fans"],result["fans_photo"])
##渲染本人追蹤
@app.route('/member/trackpeople2', methods=['POST'])
def member_trackpeople2():
    track=request.form["track"]
    result=collection.find_one({
        "userid":track
    })
    result["track"]=result["track"][::-1]
    result["track_photo"]=result["track_photo"][::-1]
    return jsonify(result["track"],result["track_photo"])
##渲染本人粉絲
@app.route('/member/fanspeople2', methods=['POST'])
def member_fanspeople2():
    fans=request.form["fans"]
    result=collection.find_one({
        "userid":fans
    })
    result["fans"]=result["fans"][::-1]
    result["fans_photo"]=result["fans_photo"][::-1]
    return jsonify(result["fans"],result["fans_photo"])

##點愛心頁面移除紅點
@app.route('/member/deletedot', methods=['POST'])
def member_deletedot():
    Email=session["userID"] 
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    collection.update_one(
        {"userid":userid},
        {"$set": {"notify_dot": "false"}}
    )
##開發者頁面
@app.route('/member/developertools', methods=['POST'])
def member_developertools():
    #總人口
    cursor=collection.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    allpeoplecount=[]
    for doc in cursor: 
        allpeoplecount.append(doc["userid"])

    #總貼文
    cursor2=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    allarticlecount=[]
    for doc in cursor2: 
        allarticlecount.append(doc["article"])
        
    #總回報問題
    cursor3=collection2.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    allreturncount=[]
    for doc in cursor3: 
        allreturncount.append(doc["return1"])
        
    
    return jsonify(allpeoplecount,allarticlecount,allreturncount)
##紀錄留言板內容
@app.route('/member/hismessageboard', methods=['POST'])
def member_hismessageboard():
    Email=session["userID"] 
    result=collection.find_one({
        "Email":Email
    })
    messageboard=result["messageboard"]
    return jsonify(messageboard)

##公開按讚數與留言數
@app.route('/member/myFunction2', methods=['POST'])
def member_myFunction2():
    cursor=collection3.find({},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    people2=[]
    message2=[]
    message_user=[]
    message_photo=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
        people2.append(doc["heart_icon_photo"])
        message2.append(doc["message"])
        message_user.append(doc["message_user"])
        message_photo.append(doc["message_photo"]) 
    people1 = [lst[::-1] for lst in people1]
    people2 = [lst[::-1] for lst in people2]
    message2 = [lst[::-1] for lst in message2]
    message_user = [lst[::-1] for lst in message_user]
    message_photo = [lst[::-1] for lst in message_photo]
    return jsonify(people1,people2,message2,message_user,message_photo)

##私人按讚數與留言數
@app.route('/member/myFunction2_name', methods=['POST'])
def member_myFunction2_name():
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    userid=result["userid"]
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    people2=[]
    message2=[]
    message_user=[]
    message_photo=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
        people2.append(doc["heart_icon_photo"])
        message2.append(doc["message"])
        message_user.append(doc["message_user"])
        message_photo.append(doc["message_photo"]) 
    people1 = [lst[::-1] for lst in people1]
    people2 = [lst[::-1] for lst in people2]
    message2 = [lst[::-1] for lst in message2]
    message_user = [lst[::-1] for lst in message_user]
    message_photo = [lst[::-1] for lst in message_photo]
    return jsonify(people1,people2,message2,message_user,message_photo)
##公開2按讚數與留言數
@app.route('/member/myFunction2_track', methods=['POST'])
def member_myFunction2_track():
    Email=session["userID"]
    result=collection.find_one({
        "Email":Email
    })
    track=result["track"]
    cursor=collection3.find( {"userid": {"$in": track}},sort=[
        ("_id",pymongo.DESCENDING)  
    ])
    people1=[]
    people2=[]
    message2=[]
    message_user=[]
    message_photo=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
        people2.append(doc["heart_icon_photo"])
        message2.append(doc["message"])
        message_user.append(doc["message_user"])
        message_photo.append(doc["message_photo"]) 
    people1 = [lst[::-1] for lst in people1]
    people2 = [lst[::-1] for lst in people2]
    message2 = [lst[::-1] for lst in message2]
    message_user = [lst[::-1] for lst in message_user]
    message_photo = [lst[::-1] for lst in message_photo]
    return jsonify(people1,people2,message2,message_user,message_photo)
##查詢按讚數與留言數
@app.route('/member/myFunction2_name2/<userid>', methods=['POST'])
def member_myFunction2_name2(userid):
    cursor=collection3.find({
        "userid":userid
    },sort=[
        ("_id",pymongo.DESCENDING)
    ])
    people1=[]
    people2=[]
    message2=[]
    message_user=[]
    message_photo=[]
    for doc in cursor: 
        people1.append(doc["heart_icon"])
        people2.append(doc["heart_icon_photo"])
        message2.append(doc["message"])
        message_user.append(doc["message_user"])
        message_photo.append(doc["message_photo"]) 
    people1 = [lst[::-1] for lst in people1]
    people2 = [lst[::-1] for lst in people2]
    message2 = [lst[::-1] for lst in message2]
    message_user = [lst[::-1] for lst in message_user]
    message_photo = [lst[::-1] for lst in message_photo]
    return jsonify(people1,people2,message2,message_user,message_photo)


app.config['SECRET_KEY'] = 'bbb'
app.secret_key="aaa"
if __name__ == '__main__':
    app.run(port=5000)


