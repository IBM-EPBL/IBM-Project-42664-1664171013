from turtle import st
from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape

import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pkc97923;PWD=X4zNsMTqookDgNSa",'','')

print(conn)


app = Flask(__name__)



@app.route('/')
def home():
  return render_template('index.html')

@app.route('/register')
def register():
  return render_template('register.html')

@app.route('/uploaddata',methods = ['POST', 'GET'])
def uploaddata():
  msg  = ''
  if request.method == 'POST':
    name = request.form['username']
    email = request.form['emailaddress']
    pword = request.form['pword']


    sql = "SELECT * FROM nutrition WHERE name =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
      return render_template('login.html', msg="You are already a member, please login using your details")
    else:
      insert_sql = "INSERT INTO nutrition VALUES (?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, pword)
      #ibm_db.bind_param(prep_stmt, 4, pin)
      ibm_db.execute(prep_stmt)
    
    return render_template('login.html', msg=" Data saved successfuly..")

@app.route('/login')
def login():
  return render_template('login.html')
  
  #students = []
 # sql = "SELECT * FROM Students"
  #stmt = ibm_db.exec_immediate(conn, sql)
  #dictionary = ibm_db.fetch_both(stmt)
  #while dictionary != False:
    # print ("The Name is : ",  dictionary)
    #students.append(dictionary)
    #dictionary = ibm_db.fetch_both(stmt)

  #if students:
    #return render_template("list.html", students = students)

@app.route('/delete/<name>')
def delete(name):
  sql = f"SELECT * FROM Nutrient WHERE name='{escape(name)}'"
  print(sql)
  stmt = ibm_db.exec_immediate(conn, sql)
  nutrition = ibm_db.fetch_row(stmt)
  print ("The Name is : ",  nutrition)
  if nutrition:
    sql = f"DELETE FROM Nutrition WHERE name='{escape(name)}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)

    nutrition = []
    sql = "SELECT * FROM Nutrition"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      nutrition.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    if nutrition:
      return render_template("login.html", nutrition = nutrition, msg="Delete successfully")




@app.route('/trackfood')
def trackfood():
  return render_template('trackfood.html')



@app.route('/logout')
def logout():
  session.clear()
  return render_template('index.html')



@app.route('/upload_img', methods=['GET', 'POST'])
def upload_img():
    if request.method == 'POST':
        img = request.files['foodimg']
        pathname = './static/img/biryani.jpg'+session['email']+'.jpg'
        img.save(pathname)
        # using ibm watson visualrecognition api to identify the fooditem
        authenticator = IAMAuthenticator(
            '4biolQXfmt25NoJHWtHzlZ-bpbU7p85zrvuzdgI8Tl_W')
        visual_recognition = VisualRecognitionV3(
            version='2018-03-19',
            authenticator=authenticator
        )
        try:
            visual_recognition.set_service_url(
                'https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/7024ae63-5bac-4faf-bf7c-17d733db7625')
            with open(pathname, 'rb') as images_file:
                classes = visual_recognition.classify(
                    images_file=images_file,
                    classifier_ids=["food"]).get_result()
            fooditem = classes['images'][0]['classifiers'][0]['classes'][0]['class']
        except:
            return render_template('trackfood.html', msg=0)
        if fooditem.lower() == 'non-food':
            allnutrients = []
            allnutrients.append(fooditem.upper())
            allnutrients.append(0)
            return render_template('trackfood.html', msg=allnutrients)
        else:
            # using usda api to get the nutrients of the food item
            nutrients = requests.get('https://api.nal.usda.gov/fdc/v1/foods/search?query={}&pageSize={}&api_key={}'.format(
                fooditem, '1', 'vIrQaHQPu9zk57HxLIcUMBlxxcco78tZgg3tHzfW'))
            data = json.loads(nutrients.text)
            nlist =[]
            vlist =[]
            n = int(len(data['foods'][0]['foodNutrients']))
            for i in range(0,n):

                nlist.append(data['foods'][0]['foodNutrients'][i]['nutrientName'])
                vlist.append(str(data['foods'][0]['foodNutrients'][i]['value'])+" "+data['foods'][0]['foodNutrients'][i]['unitName'])
            dic={"nutri": nlist , "value":vlist , "n" : int(n)}
            return render_template('trackfood.html',vlist=vlist, nlist=nlist,n=n,fooditem=fooditem.upper())






  
  # # while student != False:
  # #   print ("The Name is : ",  student)

  # print(student)
    return "success..."

# @app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
# def edit(id):
    
#     post = BlogPost.query.get_or_404(id)

#     if request.method == 'POST':
#         post.title = request.form['title']
#         post.author = request.form['author']
#         post.content = request.form['content']
#         db.session.commit()
#         return redirect('/posts')
#     else:
#         return render_template('edit.html', post=post)