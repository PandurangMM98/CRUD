from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "Secret Key"

# -------------------------SqlAlchemy Database Configuration With Mysql------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/EMPLOYEE'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


# used class to de fine table data
# -----------------------------------------------ORG table--------------------------------------------

class ORG(db.Model):
    Org_code = db.Column(db.String(30), nullable=True, primary_key=True)
    Org_Name = db.Column(db.String(30))
    Org_City = db.Column(db.String(30))

    # company =db.relationship('EMP',backref='ORG')

    def insert_org_data(self):
        db.session.add(self)
        db.session.commit()

    def __init__(self, Org_code, Org_Name, Org_City):
        self.Org_code = Org_code
        self.Org_Name = Org_Name
        self.Org_City = Org_City


# --------------------------------------------------Emp Table------------------------------------------

class EMP(db.Model):
    Org_code = db.Column(db.String(3), db.ForeignKey('ORG.Org_code'))
    Emp_code = db.Column(db.String(5), primary_key=True)
    Emp_name = db.Column(db.String(30))
    Emp_age = db.Column(db.Integer)
    Emp_dept = db.Column(db.String(30))

    def insert_emp_data(self):  # db open connection to add value to table
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, Org_code, Emp_code, Emp_name, Emp_age, Emp_dept):
        self.Org_code = Org_code
        self.Emp_code = Emp_code
        self.Emp_name = Emp_name
        self.Emp_age = Emp_age
        self.Emp_dept = Emp_dept


class ORG_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ORG
        load_instance = True


class EMP_schema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EMP
        load_instance = True
        include_fk = True


# --------------------------------------ORG table CRUD APIs-------------------------------------------

#-------------------Fage Not Found API-------------------------------------

@app.errorhandler(404)
def not_found(error=None):
    message = {
        "status": 404,
        "message": " Not Found : "
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

#-----------------------------------Method not allowed---------------------------------

@app.errorhandler(405)
def not_found(error=None):
    message = {
        "status": 405,
        "message": " Method Not Allowed."
    }
    resp = jsonify(message)
    resp.status_code = 405
    return resp


#----------------Internal error----------------------------------------
@app.errorhandler(500)
def internal_server_error(error=None):
    message = {
        "status": 500,
        "message": "Some thing went wrong."
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


# --------------------------Checking appliction is running or not----------------------------
@app.route('/')
def first_api():
    return '<h1>Welcome Sir/Maam Backend is working.<h1>'


# ---------------------Fetching data from databse to json file--------------------------------

@app.route('/org/index')
def index_org():
    ORG_data = ORG.query.all()
    Org_Table = ORG_schema(many=True)
    output = Org_Table.dump(ORG_data)
    return jsonify({"ORG_data": output})
    # return render_template('org/index.html',data=a)


# -------------------------------------insert data into ORG table---------------------------------------

@app.route('/org/insert', methods=['POST'])
def insert_org():
    if request.method == 'POST':

        try:
            ORG_data = request.get_json()

            if ORG_data.get('Org_code'):      # chenking these all column data required 
                pass
            else:
                return jsonify({"error": "you have to add Org_code Column."}), 400

            if ORG_data.get('Org_Name'):
                pass
            else:
                return jsonify({"error": "you have to add Org_Name Column aslo."}), 400

            if ORG_data.get('Org_City'):
                pass
            else:
                return jsonify({"error": "you have to add Org_City Column aslo."}), 400

            Org_schema = ORG_schema()
            if ORG.query.filter(ORG.Org_code == ORG_data['Org_code']).first():  # checking primary key should be unique in table
                db.session.rollback()
                return jsonify(
                    "The Org_code should Be Unique. " + ORG_data['Org_code'] + " is already exist in ORG table"), 400

            else:
                Org_Table = Org_schema.load(ORG_data)
                result = Org_schema.dump(Org_Table.insert_org_data())
                return jsonify(ORG_data['Org_code'] + " Org_code row Successfully added to ORG table. "), 200

        except TypeError as msg:

            # db.session.rollback()
            return jsonify({"error": msg})


# ----------------------------------update data into ORG table using Org_code-----------------------

@app.route('/org/update/<Org_code>/', methods=['PUT'])
def update_org(Org_code):
    if request.method == 'PUT':
        try:
            if ORG.query.filter(ORG.Org_code == Org_code).first():    #checking Org_code is present in table or Not
                data = request.get_json()
                my_data = ORG.query.get(Org_code)

                if data.get('Org_Name'):                             # chenking these all column data required
                    my_data.Org_Name = data['Org_Name']
                else:
                    return jsonify({"error": "you have to add Org_Name Column aslo."}), 400

                if data.get('Org_City'):
                    my_data.Org_City = data['Org_City']

                else:
                    return jsonify({"error": "you have to add Org_City Column aslo."}), 400

                db.session.add(my_data)
                db.session.commit()
                return jsonify(Org_code + " Org_code row Successfully updated to ORG table. "), 201
            else:
                return jsonify(Org_code + " Org_code is not in the ORG table. "), 404

        except TypeError:
            return jsonify("error"), 500


# -------------------------------------delete row from ORG table using Org_code--------------------------------------

@app.route('/org/delete/<Org_code>/', methods=['DELETE'])
def delete_org(Org_code):
    try:
        if ORG.query.filter(ORG.Org_code == Org_code).first():  #checking Org_code is present in table or Not
            my_data = ORG.query.get(Org_code)
            db.session.delete(my_data)
            db.session.commit()
            return jsonify(Org_code + " Org_code row Successfully deleted from ORG table. "), 200
        else:
            return jsonify("Entered " + Org_code + " Org_code is not Found in ORG table."), 400
    except TypeError:
        return jsonify("error")


# --------------------------EMP table CRUD APIs--------------------------

# -----------------------------------Fetching data from database to json file --------------------------------
@app.route('/emp/index')
def index_emp():
    EMP_data = EMP.query.all()
    EMP_Table = EMP_schema(many=True)
    output = EMP_Table.dump(EMP_data)
    return jsonify({"EMP_data": output})
# checking Org_code is present in EMP table or not

# --------------------------------------insert data into EMP table-----------------------------------------

@app.route('/emp/insert', methods=['POST'])
def insert_emp():
    if request.method == 'POST':
        try:
            Emp_data = request.get_json()
            if Emp_data.get('Org_code'):       # chenking these all column data required
                pass
            else:
                return jsonify({"error": "you have to add Org_code Column."}), 400

            if Emp_data.get('Emp_code'):
                pass
            else:
                return jsonify({"error": "you have to add Emp_code Column."}), 400

            if Emp_data.get('Emp_name'):
                pass
            else:
                return jsonify({"error": "you have to add Emp_name Column."}), 400

            if Emp_data.get('Emp_age'):
                pass
            else:
                return jsonify({"error": "you have to add Emp_age Column."}), 400

            if Emp_data.get('Emp_dept'):
                pass
            else:
                return jsonify({"error": "you have to add Emp_dept Column."}), 400

            Emp_schema = EMP_schema()
            if EMP.query.filter(EMP.Emp_code == Emp_data['Emp_code']).first():              # checking primary key should be unique in table
                db.session.rollback()
                return jsonify(
                    "The Emp_code should Be Unique. " + Emp_data['Emp_code'] + " is already exist in EMP table"), 400
            else:
                EMP_Table = Emp_schema.load(Emp_data)
                result = Emp_schema.dump(EMP_Table.insert_emp_data())
                return jsonify(Emp_data['Emp_code'] + " Emp_code row Successfully added to EMP table. "), 200

        except TypeError as msg:
            db.session.rollback()
            return jsonify({"error": msg})


# -------------------------------update data into EMP table using EMP_code----------------------------------
@app.route('/emp/update/<Emp_code>/', methods=['PUT'])
def update_emp(Emp_code):
    if request.method == 'PUT':
        try:
            if EMP.query.filter(EMP.Emp_code == Emp_code).first(): #checking Emp_code is present in table or Not
                data = request.get_json()
                my_data = EMP.query.get(Emp_code)
                if data.get('Org_code'):                                     # chenking these all column data required
                    my_data.Org_code = data['Org_code']
                else:
                    return jsonify({"error": "you have to add Org_code Column."}), 400
                if data.get('Emp_name'):
                    my_data.Emp_name = data['Emp_name']
                else:
                    return jsonify({"error": "you have to add Emp_name Column aslo."}), 400
                if data.get('Emp_age'):
                    my_data.Emp_age = data['Emp_age']
                else:
                    return jsonify({"error": "you have to add Emp_age Column aslo."}), 400
                if data.get('Emp_dept'):
                    my_data.Emp_dept = data['Emp_dept']
                else:
                    return jsonify({"error": "you have to add Emp_dept Column aslo."}), 400
                db.session.add(my_data)
                db.session.commit()
                return jsonify(Emp_code + " Emp_code row Successfully updated to EMP table. "), 201
            else:
                return jsonify(Emp_code + " Emp_code is not in the ORG table. "), 404

        except TypeError:
            return jsonify("error"), 500


# -----------------------------------delete row from EMP table using Emp_code---------------------------------

@app.route('/emp/delete/<Emp_code>/', methods=['DELETE'])
def delete_emp(Emp_code):
    if request.method == 'DELETE':
        try:
            if EMP.query.filter(EMP.Emp_code == Emp_code).first():  #checking Emp_code is present in table or Not
                my_data = EMP.query.get(Emp_code)
                db.session.delete(my_data)
                db.session.commit()
                return jsonify(Emp_code + " Emp_code row Successfully deleted from EMP table. "), 200
            else:
                return jsonify("Entered " + Emp_code + " Emp_code is not Found in EMP table."), 400
        except ty:
            return jsonify("error")


# ----------------Queries APIs----------------------

# ---------------------------------All employees in an organization Org_code-------------------
@app.route('/<Org_code>/')
def retrieve(Org_code):
    try:
        if EMP.query.filter(EMP.Org_code == Org_code).first():  # checking Org_code is present in EMP table or not 
            data = EMP.query.filter_by(Org_code=Org_code).all()  
            return render_template('r.html', data=data)
        else:
            return jsonify(Org_code + " Org_code is not present in EMP table."), 400
    except IntegrityError:
        return jsonify("error")


# ------------------------All employees with age >= <age>----------------------------

@app.route('/age/<int:Emp_age>/')
def age(Emp_age):
    a = int(Emp_age)
    # data=ORG.query.filter_by(Org_code=Org_code).first()
    data = EMP.query.filter(EMP.Emp_age >= a).all()
    return render_template('r.html', data=data)

# --------------------------All employees for the given organization Org_code with age >= Given_age---------------------

@app.route('/<Org_code>/<int:Emp_age>/')
def age_Org(Org_code, Emp_age):
    try:
        if EMP.query.filter(EMP.Org_code == Org_code).first():          # checking Org_code is present in EMP table or not
            a = int(Emp_age)
            data = EMP.query.filter(EMP.Org_code == Org_code, EMP.Emp_age >= a).all()
            return render_template('r.html', data=data)
        else:
            return jsonify(Org_code + " Org_code is not present in EMP table."), 400
    except IntegrityError:
        return jsonify("error")


if __name__ == "__main__":
    app.run(debug=True)
