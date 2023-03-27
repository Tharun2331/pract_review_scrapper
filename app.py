from flask import Flask,render_template,request,jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

application = Flask(__name__)
app=application

@app.route("/",methods=["GET"])
@cross_origin()

def homePage():
    return render_template("index.html")

@app.route("/review", methods= ["POST","GET"])
@cross_origin()

def index():
    if request.method == "POST":
        try:
            searchString = request.form["content"].replace(" ","")
            flipkart_URL = "https://www.flipkart.com/search?q=" + searchString
            urlClient = uReq(flipkart_URL)
            flipkartPage = urlClient.read()
            urlClient.close()
            flipkartHtml = bs(flipkartPage,"html.parser")
            bigbox = flipkartHtml.findAll("div", {"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            box = bigbox[0]
            productLink = flipkart_URL + box.div.div.div.a["href"]
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text,"html.parser")
            print(prod_html)
            comment_boxes = prod_html.findAll("div",{"class":"_16PBlm"})
            File = searchString + ".csv"
            fw = open(File,"w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]
            for comment_box in comment_boxes:
                try:
                    name = comment_box.div.div.findAll("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = "No Name"
                try:
                    rating = comment_box.div.div.div.div.text
                except:
                    rating="No Rating"
                try:
                    heading = comment_box.div.div.div.p.text
                except:
                    heading= "No Heading"
                try:
                    comment_tag = comment_box.div.div.findAll("div",{"class":""})
                    custComment = comment_tag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)
                
                mydict = {"Product": searchString, "Name": name, "Rating":rating, "CommentHead":heading,"Comment":custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')
            

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
        
        
