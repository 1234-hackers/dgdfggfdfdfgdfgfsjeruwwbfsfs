import base64
from email import message
from turtle import st
from dns.message import Message
from flask import Flask, render_template, url_for, request, redirect,flash,session
from flask.scaffold import F
from flask_pymongo import PyMongo
from flask_wtf.form import FlaskForm
from pymongo import MongoClient
import passlib
from passlib.context import CryptContext
from passlib.hash import bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
from datetime import timedelta , datetime
import smtplib
from email.message import EmailMessage
import socket,os
from functools import wraps
from gridfs import*
from bson import ObjectId
from flask_recaptcha import ReCaptcha
from flask_wtf import RecaptchaField,FlaskForm
from wtforms import *
from wtforms.validators import EqualTo, InputRequired
from flask_wtf.csrf import CSRFProtect
from wtforms.csrf.session import SessionCSRF 
from datetime import timedelta
import email_validator 
import random
#from flask_mail import Mail,Message
import base64
from bson.binary import Binary
from werkzeug.utils import secure_filename
#mpsa imports
#from flask_mpesa import MpesaAPI

import PIL
from PIL import Image

import markupsafe
from markupsafe import escape , Markup
ip = socket. gethostbyname(socket. gethostname())
ipst = str(ip)
application = Flask(__name__)

#mpesa configs
#mpesa_api = MpesaAPI(application)
application.config["API_ENVIRONMENT"] = "sandbox"
application.config["APP_KEY"] = "..." 
application.config["APP_SECRET"] = "..." 


#images
upload_folder = 'static/images'
application.config['UPLOAD_FOLDER'] = upload_folder
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#recaptcha configs
recaptcha = ReCaptcha(application = application)
application.config['RECAPTCHA_PUBLIC_KEY'] =  "6Lf2-MIaAAAAAKhR8vc-wUo6PyWIXtevEN3R7HpY"
application.config['RECAPTCHA_PRIVATE_KEY'] = "6Lf2-MIaAAAAACzF1Nmhmq0dGEGdf9jQJyIqOEmS"
application.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark'}
application.config['TESTING'] = True
#csrf protection
csrf = CSRFProtect(application)
application.config['WTF_CSRF_SECRET_KEY'] = 'edfdfgdfgdfgfghdfggfg'
SECRET_KEY = "dsfdsjgdjgdfgdfgjdkjgdg"
SECRET = "secret"

#mongoDB configs
application.config['MONGO_DBNAME'] = 'users'
# application.config['MONGO_URI'] = 'mongodb://'+ipst+':27017/users'
application.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(application)


#FlaskMailConfigs

application.config['MAIL_SERVER'] = "smtp.gmail.com"
application.config['TESTING'] = True
application.config['MAIL_PORT'] = 465
application.config['MAIL_USE_TLS'] = False
application.config['MAIL_USE_SSL'] = True
application.config['MAIL_DEBUG'] = True
application.config['MAIL_USERNAME']  = "jacksonmuta123@gmail.com"
application.config['MAIL_PASSWORD'] =  "aqlxhzaziujnllzi"
application.config['MAIL_DEFAULT_SENDER'] = "Reset Password Server "
application.config['MAIL_SUpplicationRESS_SEND'] = False
application.config['MAX_EMAIL'] = None
application.config['MAIL_ASCII_ATTATCHMENTS'] = False

#Post_guy = Mail(application)


client = MongoClient('localhost', 27017)
db_pic = client.users
gfs = GridFS(db_pic)






#'mongodb://'+ipst+':27017/kamp_users'
#'mongodb://localhost:27017/kamp_users'
#'mongodb+srv://jackson:@hbcall.ihz6j.azure.mongodb.net/kamp_users?retryWrites=true&w=majority'
#'mongodb://jackson:mutamuta@hbcall-shard-00-00.ihz6j.azure.mongodb.net:27017,hbcall-shard-00-01.ihz6j.azure.mongodb.net:27017,hbcall-shard-00-02.ihz6j.azure.mongodb.net:27017/kamp_users?ssl=true&replicaSet=atlas-aykvid-shard-0&authSource=admin&retryWrites=true&w=majority'
application.permanent_session_lifetime = timedelta(days=30)


Hash_passcode = CryptContext(schemes=["sha256_crypt" ,"des_crypt"],sha256_crypt__min_rounds=131072)


mongo = PyMongo(application)

users = mongo.db.users
link_db = mongo.db.links
verif = mongo.db.verify_email

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('index'))
    return wrap


class Base_form(Form):
    
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF 
        csrf_secret = "fhgfjgygkgchfjfjfdumbo"
        csrf_time_limit = timedelta(minutes=25)
        
class login_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
@application.route('/',methods = ["POST","GET"])
@csrf.exempt
def home():
    form = login_form()
    if request.method == "POST" and form.validate():
        email = form.email.data
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = form.passc.data

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        else:
                            return redirect(url_for('main_page'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('main_page'))   
    return render_template("index.html" , form = form)


def reset_session_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('reset_pass'))
    return wrap
@application.route('/reset_pass/', methods = ['POST','GET'])
@csrf.exempt
def  reset_pass():
    reset_db = mongo.db.pass_reset
    code = random.randint(145346 , 976578)
    code = str(code)
    if request.method == "POST":
        email = request.form['email']
        existing = users.find_one({'email':email} )
        if existing:
            '''
            Send message here with the code
            '''
            now = datetime.now()
            r_now =  now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
            session['rset'] = email
            reset_db.insert_one({"email" : email , "code" : code , "time_in" : r_now})
            return redirect(url_for("enter_code"))      
        else:
            return redirect(url_for('register'))
    return render_template('reset_pass.html')
@application.route('/enter_code/' , methods = ['POST','GET'])
@csrf.exempt
def enter_code():
    email = session['rset']
    if email in session:
        if request.method == "POST":
            reset_db = mongo.db.pass_reset
            code = request.form['code']
            mailed = email
            legit = reset_db.find_one({"email" : email})
            if legit:
                legit_code = legit["code"]
                now = datetime.now()
                now = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
                req_time = legit['time_in']
                diff = now - req_time
                if code == legit_code and diff < 7:
                    return redirect(url_for('peopleass'))  
                if diff > 7:
                    return redirect(url_for('reset_pass' ))
            else:
                return redirect(url_for('reset_pass'))
    else:
        return redirect(url_for('reset_pass'))
            
    return render_template('enter_code.html')
     
class peopleass(Base_form):
      
        pass1 = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
        pass2 = PasswordField("Confirm Password" , [validators.Length(min = 8,max=15 , message="8 To 15 Characters") , EqualTo("passc",message="Must Be Same To The Input Above") , InputRequired()])
        
        

@application.route('/peopleass/' , methods = ['POST','GET'])
@csrf.exempt
def peopleass(email):
    form = peopleass()
    if request.method == "POST" and form.validate():
        users = mongo.db.users
        target_account = session['rset'] 
        pass1 = form.pass1.data
        pass2 = form.pass2.data
        if pass1 == pass2 and len(pass2) > 8 and len(pass2) < 15 :
            passcode = Hash_passcode.hash(pass2)
            the_user = users.find_one({"email" : email})
            users.find_one_and_update({"email" :target_account} , { 'set' : {"password" : passcode} })
            session['login_user'] = target_account
            return redirect(url_for('main'))
        else:
            check_pass = " Please Check The Password And Try Again"
            return render_template('peopleass.html' , form = form , mess = check_pass)
            
    return render_template('peopleass.html' , form = form)


class Base_form(FlaskForm):
    
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF 
        csrf_secret = b"cffhgfghfgjgherydumbo"
        csrf_time_limit = timedelta(minutes=25)
        
class login_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")])            
@application.route('/login/' , methods = ['POST','GET'])
@csrf.exempt
def login():
    form = login_form()
    if request.method == "POST" and form.validate():
        email = form.email.data
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = form.passc.data

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        else:
                            return redirect(url_for('main_page'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('main_page'))
    return render_template('login.html' , form = form)


class Base_form(FlaskForm):
    
    class Meta:
        csrf = False
        csrf_class = SessionCSRF 
        csrf_secret = "dfgdfgtryfhgfhhgfhdxhd"
        csrf_time_limit = timedelta(minutes=25)
        
class register_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        username = StringField("Username" , [validators.InputRequired(message="A Nickname or your most known Name")])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
        passc2 = PasswordField("Confirm Password" , [validators.Length(min = 8) , EqualTo("passc") , InputRequired()])
    
@application.route('/register/',methods = ['POST','GET'])
@csrf.exempt
def register():
    form = register_form()
    if request.method == "POST" and "img" in request.files:
        
        pic = request.files['img']
        
        email = form.email.data
        
        username =  form.username.data
        
        passc = form.passc.data
        
        passc2 = form.passc2.data
        
        hashed = Hash_passcode.hash(passc2)
        
        filename = pic.filename
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if allowed_file(filename):
            fl = email.replace("." , "")
            os.mkdir("static/images/" + fl)
            pt = "static/images/" + fl + "/"
            des = fl + "/" + filename
            
            pic.save("static/images/" + des)
            image1 = "static/images/" + des
            image = Image.open(image1)
            new = image.convert("RGB")
            new.save(pt + fl + '.jpg')
            image = pt +fl + ".jpg"
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')
            os.remove("static/images/" + fl  + "/" + filename)
        registered = users.find_one({"email":email})
        if registered:
            mess = "You are already registered,please Log in"
            return redirect(url_for('home'))
        if passc == passc2  and not registered:
            mess = "Registerd Successfully" 
            favs = []
            tags = []
            users.insert_one({"email":email ,'username':username , "password":hashed , 
                            "profile" : uploa , "favs" : favs , "tags" : tags , "verified" :0 })
            
            if users.find_one({"email":email}):
                code = random.randint(145346 , 976578)
                code = str(code)
                session['login_user'] = email
                verif.insert_one({"email" : email , "code" : code })
                #send the code Here
                
                return redirect(url_for('complete_regist'))
    return render_template('register.html',form = form)

class complete_regist(Base_form):
    code = StringField("Verification Code" , [validators.InputRequired(message="Please Enter The Code Sent Via Email")])

@application.route('/complete_regist' , methods = ['POST' , 'GET'])
@csrf.exempt
def complete_regist():
    verif = mongo.db.verify_email
    user_email = session['login_user']
    in_db = verif.find_one({"email" : user_email})
    if request.method == "POST":
        de_code = request.form['code']
        if in_db:
            code = str(in_db['code'])
            if code == de_code:
                users.find_one_and_update({"email" : user_email} ,{ '$set' :  {"verified": 1}} )
                verif.find_one_and_delete({'email' : user_email})
                return redirect(url_for('choose_tags'))
            else:
                print("Wrong Code")
                time.sleep(2)
                return redirect(url_for('complete_regist'))
        else:
            return redirect(url_for('register'))
            
    return render_template('verif_reg.html' , m = user_email)
    
@application.route('/choose_tags/' , methods = ['POST','GET'])
@csrf.exempt
def choose_tags():
    the_tags = ['music' , 'sports' , 'crypto' ,'technology' , 'real estate' , 'nature' , 'art' , 'gaming' , 'nft' ,'politics' ,'elon' , 'watch' ,
                    'memes' , 'russia'
                    ]
    user_email = session['login_user']
    if request.method == "POST":
        aaction = request.form.getlist('tags')
        user_db = mongo.db.users
        
        list2 = random.sample(the_tags , 6)
        user = user_db.find_one({"email" : user_email})
        if len(aaction) < 5:
            em_tags = user['tags']
            for x in list2:
                em_tags.append(x)
            user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"tags": em_tags}} )
            return redirect(url_for('choose_favs'))
        else:
            em_tags = user['tags']
            for y in aaction:
                em_tags.append(y)
            user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"tags": em_tags}} )
            return redirect(url_for('main_page' ))
            
            
    return render_template('choose_tags.html' , tags = the_tags)

@application.route('/choose_favs/' , methods = ['POST','GET'])
def choose_favs():
    user_email = session['login_user']
    user_db = mongo.db.users
    user = user_db.find_one({"email" : user_email})
    em_favs = user['favs']
    favs_tags = user['tags']
    all_posts= link_db.find()
    f = []
    for k in all_posts:
            ok = k['tags']
            for x in favs_tags:
                one = x
                if one in ok:
                    f.append(k)
    for ps in f:
        owner = ps['owner']
        em_favs.append(owner)
        user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"favs": em_favs}} )
        
    
    favs_tags =   ['music' , 'sports' , 'crypto' ,'technology' , 'real estate' , 'nature' , 'art' , 'gaming' , 'nft' ,'politics' ,'elon' , 'watch' ,
                    'memes' , 'russia'
                    ]
    f = []
    for k in all_posts:
            ok = k['tags']
            for x in favs_tags:
                one = x
                if one in ok:
                    f.append(k)
    for ps in f:
        owner = ps['owner']
        e_favs = []
        e_favs.append(owner)
    new_favs = user['favs']
    
    for t in new_favs:
        if t in e_favs:
            e_favs.remove(t)
            user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"favs": e_favs}} )
    return render_template('choose_favs.html')

@application.route('/main_page/' , methods = ['POST','GET'])
@csrf.exempt
@login_required
def main_page():
    link_db = mongo.db.links
    em = link_db.find()
    user = mongo.db.users
    trending_db = mongo.db.trending
    randomly = link_db.find().limit(100)
    render_array = []
    render_array.extend(randomly)
    #based on following people
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    favs = the_user["favs"]
    fav_arr = []
    if len(favs) <10:
        count = 3
    else:
        count = 2
    for x in favs:         
        user = x
        documentz = link_db.find({"owner" : user }).limit(count)
        for kk in documentz:
            if not kk in render_array:
                fav_arr.extend(documentz)      
    render_array.extend(fav_arr)

    #based on tags
    my_tags = the_user["tags"]
    for y in my_tags:
        indiv_tags  = y
        #relevant = trending_db.find({"tags" : tags})
        arr1 = []
        all_posts= link_db.find().limit(300)
        for x in all_posts:
            tags = x['tags']
            if indiv_tags in tags:
                if not  x in render_array: 
                    arr1.append(x)        
    render_array.extend(arr1)
    random.shuffle(render_array)
    
        
    #view link functionality
    if request.method == "POST":
        the_id = request.form['id']
        if request.form['sub'] == "View Link": 
            session["linky"] = the_id
            return redirect(url_for('view_link' ))
        
        if request.form['sub'] == "Follow":
            the_id = request.form['id']
            owner_d =  link_db.find_one({"post_id" : the_id})
            owner = owner_d['owner']
            cl = session['login_user']
            folloin = users.find_one({'email' :cl})
            f = folloin['favs']
            if not owner in f:
                f.append(owner)
                users.find_one_and_update({'email' : user_email} , {'$set' : {'favs' : f}})
            else:
                f.remove(owner)
                users.find_one_and_update({'email' : user_email} , {'$set' : {'favs' : f}})
                
        if request.form['sub'] == "Like":
            the_post = link_db.find_one({"post_id" : the_id})
            likes= the_post['likes']
            total_likes = len(likes)
            clicker = session['login_user']
            if clicker in likes:
                likes.remove(clicker)
                total_likes = len(likes)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes  , 'total_likes' : total_likes }} )
                b_color = "red"
            else:
                likes.append(clicker) 
                total_likes = len(likes)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes  , 'total_likes' : total_likes}} )
                b_color = "less"   
                             
    return render_template('main.html' , arr = render_array , fav = fav_arr , email = user_email )

@application.route('/search/' , methods = ['POST','GET'])
@csrf.exempt
def search():
    user_email = session['login_user']
    if request.method == "POST":
        de_search = request.form['search']
        session['q'] = de_search           
        return redirect(url_for('found_posts'))    
   
    return render_template('search.html')

@application.route('/found_posts/' , methods = ['POST','GET'])
def found_posts():
    to_show = []
    de_search = session['q']
    finds = de_search.split()
    al = link_db.find()
    for x in finds: 
        for c in al:
            emt = c['tags']
            if x in emt:
                to_show.append(c)      
            lks = c['link']
            de_lin = lks.split()
            if x in de_lin:
                to_show.append(c) 
            if len(to_show) < 1:
                no = "No Result Found,Please Check Your Spelling See More"
            else:
                no = "Results From Search"
    return render_template('found_post.html' , post = to_show , n = no)


@application.route('/found_people' , methods = ['POST','GET'])
@csrf.exempt
def found_people():
    session.pop("de_email" ,None)
    de_search = session['q']
    de_users = []
    people = []
    temp = []
    all_usr = users.find()
    for q in all_usr:
        name = q['username']
        email = q['email']
        new_m = email.split('@' , maxsplit = 1 )
        mai = new_m[0]
        if name == de_search:
            if not q in de_users:
                de_users.append(q) 
        if de_search in mai:
            if not q in de_users:
                de_users.append(q)
        if mai in de_search:
            if not q in de_users:
                de_users.append(q) 
        if name in de_search:
            if not q in de_users:
                de_users.append(q)
        if de_search in name:
            if not q in de_users:
                de_users.append(q) 
        people.extend(de_users)
        new_p = []
        for i in people:
            if i not in new_p:
                new_p.append(i)
    
        if len(new_p) < 1:
                no = "No Result Found,Please Check Your Spelling See More"
        else:
                no = "Results From Search"
        
        if request.method == "POST":
            the_id = request.form['id']
            if request.form['sub'] == "View Profile": 
                session["de_email"] = the_id
                return redirect(url_for('view_prof' ))
            
            pass
        
    return render_template('found_people.html' , p = new_p , n = no)

@application.route('/pple/' , methods = ['POST','GET'])
def pple():
    if request.method == "POST":
        name = request.form['id']
        session.pop("de_email" ,None)
        name = request.form['id']
        session['de_email'] == name
        redirect(url_for('view_prof'))
    
    return render_template('')


@application.route('/profile/' , methods = ['POST','GET'])  
@csrf.exempt
def profile():
    trend = mongo.db.trending
    me = session['login_user']
    me2 = me.replace("." , "")
    the_arr = ["electric car" , "rap" , "football"]
    acc = users.find_one({"email" : me})
    favs = acc['favs']
    tags = acc['tags']
    user = acc['username']
    minez = []
    my_posts = link_db.find({"owner" : me})
    more_posts = link_db.find({}).limit(5)
    
    
    if os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
        prof_pic = "static/images/" + me2 +"/" + me2 +".jpg" 
      
    else:
        prof_pic = "/static/images/default.jpg"
    links = []
    links.append(prof_pic)
    dez_name = Markup(prof_pic)
    nnn =   "/static/images/" + me2 +"/" + me2 +".jpg"                
    return render_template('profile.html' , me = me , favs = favs , tags = tags , mine = minez ,
                           more = more_posts , links = links , prof = dez_name , nn = nnn)


@application.route('/view_prof/' , methods = ['POST','GET'])
def view_prof():
    user = session['de_email']
    user_email = session['login_user']
    the_user = users.find_one({"email" :user})
    mez = users.find_one({'email': user_email})
    folloin = mez['favs']
    if user in folloin:
        state = "Unfollow"
    else:
        state = "Follow"
    if request.method == "POST":
        if request.form['sub'] == "Follow":
            the_id = request.form['id']
            owner_d =  link_db.find_one({"post_id" : the_id})
            owner = owner_d['owner']
            cl = session['login_user']
            folloin = users.find_one({'email' :cl})
            f = folloin['favs']
            if not owner in f:
                f.append(owner)
                state = "Unfollow"
                users.find_one_and_update({'email' : user_email} , {'set' : {'favs' : f}})
            else:
                f.remove(owner)
                state = "Follow"
                users.find_one_and_update({'email' : user_email} , {'set' : {'favs' : f}})
                
 
    return render_template('view_prof.html' , usr = the_user , state = state)


@application.route('/edit_profile/' ,methods = ['POST','GET'])
@csrf.exempt
def edit_profile():
    user = mongo.db.users
    user_email = session['login_user']
    info = user.find({"email" : user_email})
    if request.method == "POST":
        name = request.form['username']
    return render_template('edit_profile.html' , inf = info)





@application.route('/post_on_tags/' , methods = ['POST','GET'])
@csrf.exempt
@login_required
def post_on_tags():
    
    tag = session['le']
   
    return render_template('post_on_tags.html')
@application.route('/view_link/' , methods = ['POST','GET'])
@csrf.exempt
def view_link():
    link_db = mongo.db.links
    user = mongo.db.users
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    de_name = the_user['username']
    if request.method == "POST":
        the_id = request.form['id']
        words = request.form['comm']
        if request.form['sub'] == "Comment":
                the_post = link_db.find_one({"post_id" : the_id})
                comments = the_post['comments']
                commentz = {de_name : words}
                comments.append(commentz)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"comments": comments}} )
        
    
    link = session['linky']
    link_db = mongo.db.links
    render_arr = []
    all_posts = link_db.find()
    post_in = link_db.find({"post_id" : link})
    post_in_2 =  link_db.find_one({"post_id" : link})
    post_tags = post_in_2['tags']
    for y in post_tags:
        indiv_tags  = y
        #relevant = trending_db.find({"tags" : tags})
        arr1 = []
        all_posts= link_db.find({}).limit(500)
        for x in all_posts:
            tags = x['tags']
            if indiv_tags in tags: 
                arr1.append(x)        
    render_arr.extend(arr1)
    if len(render_arr) < 500:
        random_psts = all_posts = link_db.find().limit(10)
        render_arr.extend(random_psts)
    return render_template('view_link.html' , taged = render_arr ,  item = post_in , link = link)

@application.route('/advert/' , methods = ['POST','GET'])
def advert():
    advert_db = mongo.db.adverts 
    if request.method == "POST":
        
        title = request.form['title']
        
        description = request.form['description']

        pic = request.files['img']
        
        plan = request.form.get("plan")
        if plan == "1":
            the_plan = "two_dollar"
        if plan == "2":
            plan = "five_dollar"
        if plan == "3":
            the_plan  = "12_dollar"
        if plan == "4":
            plan = "fifty_dollar"
        
        filename = secure_filename(pic.filename)
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS       
        if allowed_file(filename):
            pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            image = upload_folder +  "/" + filename
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')        
        advert_db.insert_one({"title" : title , "desc" : description , "ad_pic" : uploa , 
                             "plan" : plan })        
    
    return render_template('advert.html')
@application.route('/mpesa/' , methods = ['POST','GET'])
def mpesa():
    
    
    
    
    
    return render_template('mpesa.html')




@application.route('/transact/b2b')
def b2b_transact():
    data={"initiator": "[Initiator]",
            "security_credential": "[SecurityCredential]",#from developers portal
            "amount": "1000",
            "command_id":"[command_id]",
            "sender_identifier_type":"[SenderIdentifierType]",
            "receiver_identifier_type":"[ReceiverIdentifierType]",
            "party_a": "[PartyA]",
            "party_b": "[PartyB]",
            "remarks": "[Remarks]",
            "queue_timeout_url": "YOUR_URL" ,
            "result_url": "YOUR_URL",
            "account_reference": "[AccountReference]"
    }
    #mpesa_api.B2B.transact(**data)  # ** unpacks the dictionary



main_class = [
    "Science And Technology",
    "Celebrities And Gossip",
    "Vaccation , Wildlife and Earth",
    "Mortage , Property And House Items",
    "Investments And Business",
    "Relationships , Marriage and Parenting",
    "Health And Nutrition" ,
    "Agriculture and Food Security",
    "Sports"
    "Entertainment"
    ]
    
tech =[
"TECHNOLOGY",
"Computing Information Technology", 
"Medical Technology And Equipment" ,
"Communications Technology" ,
"Industrial and Manufacturing Technology" ,
"Education Technology" ,
"Construction Technology" ,
"Aerospace Technology" ,
"Biotechnology" ,
"Agriculture Technology" ,
"Electronics Technology" ,
"Military Technology" ,
"Robotics Technology" ,
"Artificial Intelligence Technology" ,
"Assistive Technology" ,
"Entertainment Technology" ,
"Sports Technology" ,
"Vehicle Technology" ,
"Environmental Technology" ,
"3D Printing Technology" ,
    
]

enta =[
"ENTERTAINMENT",
"Movies and TV shows",
"Video Games",
"Books",
"Comedy,Circus and theater",
"Concerts",
"Travel And Road Trips",
"Music",
"Gambling",
"Boeard Games",
"Children Content"
    
]

sports = [
"SPORTS",
"MotorSports",
"FootBall",
"Boxing",
"Wrestling",
"Martial Arts",
"Net Games",
"Cricket",
"American Football",
"Indoor Games"    
]
health_nutr_agric = [
"HEALTH AND NUTRITION",
"KitchenWare and Tech",
"Recipes",
"Niutrition",
"Deseases"

]

agric_green = [
"GO GREEN AND AGRICULTURE",
"Vaccations",
"Energy",
"Wildlife",
"Forestry",
"Agricultural Technology",
"Food Security",
"water",
"Global Warming"



]

rel_life_style = [
"LIFESTYLE AND RELATIONS",
"Fashion",
"Shoes",
"Women Wear",
"Weddings",
"Men Wear",
"Hair Beauty",
"Marriage",
"Sex and Relationships",
"Parenting",
"Devorce"                 
]

buss_invest = [
"BUSINESS AND INVESTMENT",
"CryptoCurrency",
"Sports Betting",
"Banking",
"Stock_Exchange",
"Online Business",

]

mortage_property = [
"MORTAGE AND PROPERTY",
"Land",
"Houses",
"Applicationartments",
"Family Transport",
"Furniture and House Equipment",
"Cars"
    ]


@application.route('/post/' , methods = ['POST','GET'])
@csrf.exempt
def post(): 
    if request.method == "POST":
            
        link_db = mongo.db.links
        
        title = request.form['title']
        
        desc = request.form['desc']
        
        link = request.form['link']

        post_id = md5_crypt.hash(title)
            
        tag1 = request.form['tag1']
        
        tag2 = request.form['tag2']

        tag_arr = []
        
        tag_arr.append(tag1)
        tag_arr.append(tag2)
        owner = session['login_user']
        like_arr = [owner]
        comments = []
        link_db.insert_one({"owner" : owner , "link" : link ,  "likes" : like_arr , "comments" : comments ,
                            "tags" : tag_arr , "title" : title , "description" : desc , "post_id" : post_id })
        return redirect(url_for('main_page'))
    return render_template('post.html')


@application.route('/my_post/' , methods = ['POST','GET'])
@csrf.exempt
def my_post():
    me =  session['login_user']
    me2 = me.replace("." , "")
    this_guy = users.find_one({"email" : me})['username']
    
    
    my_posts = link_db.find({"owner" : me})
    if my_posts.count() <2:
        tos = link_db.find_one({"owner" : me})
    else:
        tos = link_db.find({"owner" : me})
    
    if os.path.exists("static/images/" + me2 +"/" + me2 +".jpg"):
        prof_pic = "static/images/" + me2 +"/" + me2 +".jpg" 
      
    else:
        prof_pic = "/static/images/default.jpg"
    
    dez_name = Markup(prof_pic)
    nnn =   "/static/images/" + me2 +"/" + me2 +".jpg" 
    noz = my_posts.count()
        
    if request.method == "POST":
        if request.form['sub'] == "Edit":
            id = request.form['the_id']
            session['post_edit'] = id
            return redirect(url_for('edit_post'))
            
        if request.form['sub'] == "Delete":
            id = request.form['the_id']
            link_db.find_one_and_delete({"post_id" : id})
            return render_template('my_post.html' , posts = tos)
            
        if request.form['sub'] == "Promote":
            id = request.form['the_id']    
            session['post_edit'] = id
            return redirect(url_for('promote'))
    
    return render_template('my_post.html' , posts = tos ,no = noz , dude = this_guy , ppic = nnn)

@application.route('/promote/' , methods = ['POST','GET'])
@csrf.exempt
def promote():
    
    the_post =  session['post_edit']
    post = link_db.find_one({"post_id" : the_post})
    new_tags = []
    older_tags = post['tags']
    ad_view = []
    u = "U.S.A and Canada"
    e = "Europe"
    a = "Africa"
    aS = "Asia"
    aU = "Australia"
    s =  "South America"
    g = "Global"
    if request.method == "POST":
        tags = request.form['tags']  
        new_tag_arr = tags.split(",")
        new_tags.extend(new_tag_arr)
        min = 500
        max = 700
        plan = "2"
        five = {"plan" : "five",
               " maxi ": 600,
                "mini" : 550
                }
        twelve = {
            "plan" : "twelve",
            "maxi" : 1500 ,
            "mini" : 1300
        }
        fifty = {
            "plan" : "fifty_dollar" , # up to 8000 views
            "maxi" : 9000 ,
            "mini" : 7500
        }
        twenty_four = {
            "plan" : "24 hrs",
            "maxi" : 1400,
            "mini" : 1300,
            "cost" : 10
        }
        week  = {
            "plan" : "1 Week",
            "maxi" : 12800,
          "  mini" : 12000,
           " cost" : 70
        }
        three = {
           " plan" : "72 hrs",
            "maxi" : 5100,
           " mini" :4800,
            "cost" : 32 
        }
    
        plan = request.form.get("plan")
        if plan == "2":
            p = five
        if plan == "3":
            p =twelve
        if plan == "4":
            p = fifty  
        if plan == "5":
            p = twenty_four    
        if plan == "6":
            p = three
        if plan == "7":
            p = week
        
        target_reg = request.form.get("target_reg")
        if  target_reg =="11":
            reg = u
        if  target_reg =="12":
            reg =e
        if  target_reg =="13":
            reg = a
        if  target_reg =="14":
            reg = aS
        if  target_reg =="15":
            reg = aU
        if  target_reg =="16":
            reg = s
        if  target_reg =="17":
            reg = g
        
        # payment must be done to continue with the rest of the process
        
            link_db.find_one_and_update({'post_id' : the_post} , {'$set' : {'tags' : new_tags , 'region' : reg ,
                                        'ad_view' : ad_view , 'plan' : p }})
        return redirect(url_for('my_post'))
          
    return render_template('promote.html' , post = the_post)


@application.route('/edit_post/' ,methods = ['POST','GET'])
@csrf.exempt
def edit_post():
    da_id = session['post_edit']
    the_post = link_db.find_one({"post_id" : da_id})
    if request.method == "POST":
        de_link = request.form['link']
        de_ttle = request.form['title']
        de_desc = request.form['desc']
        de_tags = request.form['tags']
        
        link = the_post['link']
        title = the_post['title']
        desc= the_post['description']
           
        
        
        if not de_link  == "":
            link = de_link
        if not de_ttle =="":
            title = de_ttle
        if not de_desc =="":
            desc = de_desc
        if not de_tags =="":
            tags = de_tags
            tags = tags.split(",")
   
            link_db.find_one_and_update({"post_id" : da_id } , { '$set' :  {"link" : link ,"title" : title , "description" : desc, "tags" : tags}})  
            return redirect(url_for('my_post'))
    
    return render_template('edit_post.html' , post = the_post)
    
    
    
if __name__ == "__main__":
    application.secret_key = "Fuckoffmen"
    application.run(debug = True , port = 5006)

    
