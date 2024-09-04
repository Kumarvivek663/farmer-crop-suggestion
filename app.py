from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import joblib
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load models and data
std_scaler = joblib.load('./models/std_scaler.lb')
kmeans_model = joblib.load('./models/kmeans_model.lb')
df = pd.read_csv("./models/filter_crops.csv")

app = Flask(__name__)

# MongoDB connection string
connection_string = "mongodb+srv://aryavivek663:YfP2nAyqnioJcOCh@farmer.cxfu5.mongodb.net/?retryWrites=true&w=majority&appName=farmer"
client = MongoClient(connection_string)

# Database and collection
database = client["Farmer2"]
collection = database['FarmerData1']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Extract data from the form
            N = int(request.form['nitrogen'])
            PH = float(request.form['ph'])
            P = int(request.form['phosphorus'])
            K = int(request.form['potassium'])
            humidity = float(request.form['humidity'])
            rainfall = float(request.form['rainfall'])
            temperature = float(request.form['temperature'])
            
            # Prepare data for prediction
            UNSEEN_DATA = [[N, P, K, temperature, humidity, PH, rainfall]]
            transformed_data = std_scaler.transform(UNSEEN_DATA)
            cluster = kmeans_model.predict(transformed_data)[0]
            
            # Get suggested crops
            suggestion_crops = list(df[df['cluster_no.'] == cluster]['label'].unique())
            crop_images = {crop: f"/static/images/{crop.lower()}.jpg" for crop in suggestion_crops}

            # Insert data into MongoDB
            data = {
                "N": N, "P": P, "K": K, "temperature": temperature,
                "humidity": humidity, "PH": PH, "rainfall": rainfall
            }
            data_id = collection.insert_one(data).inserted_id
            print(f"Your data is inserted into MongoDB. Your record ID is: {data_id}")

        except Exception as e:
            print(f"An error occurred: {e}")
            suggestion_crops = ["Error processing your request."]
            crop_images = {}

    return render_template('output.html', suggestion_crops=suggestion_crops, crop_images=crop_images)

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    rating = request.form['rating'] 
    smtp_server = 'smtp.gmail.com'  
    smtp_port = 587
    smtp_user = 'kumarviveksantosh663@gmail.com'  
    smtp_password = 'txwp ihgz xkgx kkgv'  
    to_email = 'aryavivek663@gmail.com'  

   
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = 'New Feedback Received'

    body = f"Name: {name}\nEmail: {email}\nRating: {rating}\n\nMessage:\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Failed to send email: {e}")
        return redirect(url_for('feedback'))

if __name__ == "__main__":
    app.run(debug=True)
