from distutils.command import check
from logging import exception
from flask import  Flask,redirect,request,render_template,url_for

import stripe

import os

stripe_api_key = "sk_test_51M0N82LbJ0M4d4s4JuiLsyGP3eatoJU3GG67TXsuhz8p74GaV597E6DzuNpDt4gkVAUYEmrozVvPlZDAOWJzFrR100zpui8SMl"

#domain = "https://links.com"

domain = "http://localhost:5001"


app = Flask(__name__)

@app.route('/' , methods = [ 'POST' , 'GET'])
def make_order():
    de_price = 'price_1M0NIiLbJ0M4d4s4iF6VF9OR'
    def request_session_created(): 
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price' : de_price ,'quantity': 1}],    
            mode = "payment" ,
            success_url = domain + "/payment_succ",
            cancel_url = domain + "/payment_err")
        return redirect(checkout_session.url, code=303)
    if request.method == "POST":
        pd = request.form['chk']
        if pd:  
            try:
                request_session_created()
            except Exception as k:
                return render_template('order.html' ,st = str(k)  )    
    return render_template('order.html')

@app.route('/payment_err/' , methods = ['POST' , 'GET'])
def payment_err():
    
    
    
    return render_template('payment_err.html')

@app.route('/payment_succ/' , methods = ['POST' , 'GET'])
def payment_succ():
    
    
    
    return render_template('payment_succ.html')



if __name__ == '__main__':
    app.run(debug=True , port = 5001)
