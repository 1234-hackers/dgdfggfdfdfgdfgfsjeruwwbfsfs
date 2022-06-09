import os

from datetime import timedelta , datetime


def big():
    strin = "hidfhfhghfghjgfjghkghkhjlhjlhjlgfhgfkdfhfkdtjgfhcvbmcfgbv,ndghhjmdfgnnmb h dgmgmbvcvnmbh,mdfbhdmhfmdxfncgnfsngfndfgfnhfdndg"

    print(str(len(strin)))


    tech =[
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
        "Entertainm",
    ]
def fors():
    num = 1
    new =[]
    nos = [1 ,2 ,3 ,4]
    for x in nos:
        number = x
        if num  == number:
            new.append(number)
        else:
            pass
    print(new)
#fors()

def lo():
    name = "JAMES"
    name2 = name.lower() 
    print(name2)
#lo()


def arxz():
    name = "jam/s"

    name3 = name

    if "/" in name3:
        name3.remove("/")
        new_arr =str(name3)
        print(new_arr)            
#arxz()

'''mess = Message( "Hi Password Reset Request" , recipients = [email])
            mess.html =  render_template("email_template.html" , code = code,mess = mess)
            Post_guy.send(mess)'''
        
    
import random   
def listes():
    
    delist =  list(main_class)
    
    der = random.sample(delist, 3)

    print(der)
    
   
    
#listes()

def yeah():
    n =["q" ,"e"]
    x = "q"
    if "q" == x:
        if "q" not in n:
            print ("done")
        else:
            print("else")
    
#yeah()

def try_exixt():
    if os.path.exists("templates/mrdgdfgain.html"):
        print("Hell yea")
    else:
        print('Done')
#try_exixt()
from PIL import Image
def images():
    img = Image.open("s.jpg")
    img.save("Image.png")
#images()

def r():
        new_tags = []
        tag1 = "jack"
        tag2 = ""
        tag3 = "request.form['tag3']"
        tag4 = "request.form['tag4']"
        tag5 = "request.form['tag5']"
        
        for x in range(1,6):
            if not "tag" + str(x) =="":
                new_tags.append("tag" + str(x))
                
          
        for v in new_tags:
            if not v == "":
                tag1 = "jack"
                tag2 = ""
                tag3 = "request.form['tag3']"
                tag4 = "request.form['tag4']"
                tag5 = "request.form['tag5']"
                
                print(v)     
        print(new_tags)
#r()

def time_dif():
    now = datetime.now()
    now_c = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
    print(now)
    
time_dif()