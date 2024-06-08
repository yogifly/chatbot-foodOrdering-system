from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import session
from random import randint
import razorpay
import mysql.connector
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from datetime import datetime
from datetime import datetime, timedelta
from flask import session, send_file

from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'yogesh'
client = razorpay.Client(auth=("rzp_test_22YpxagEoYtImx", "KP3mmqgkyHS7BvIsD8T5Mvu9"))

import pyttsx3
import speech_recognition as sr

# Database Configuration
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="food"
)
db_cursor = db_connection.cursor()

# HTML Template for Signup Page
signup_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signup</title>
</head>
<body>
    <h1>Signup</h1>
    <form action="/signup" method="post">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password"><br>
        <button type="submit">Signup</button>
    </form>
</body>
</html>
"""
# login template 
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE INDIAN BISTRO</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600&family=Oswald:wght@600&display=swap" rel="stylesheet">
   
    <!-- <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet"> -->
    <link rel="stylesheet" href="css/tailwind.css">
    <link rel="stylesheet" href="css/tooplate-antique-cafe.css">
    
<!--

Tooplate 2126 Antique Cafe

https://www.tooplate.com/view/2126-antique-cafe

-->
</head>
<body>    
    <!-- Intro -->
    <div id="intro" class="parallax-window" data-parallax="scroll" data-image-src="img/antique-cafe-bg-01.jpg">
        <div class="container mx-auto px-2 tm-intro-width">
            <div class="sm:pb-60 sm:pt-48 py-20">
                <div class="bg-black bg-opacity-70 p-12 mb-5 text-center">
                    <h1 class="text-white text-5xl tm-logo-font mb-5">THE INDIAN BISTRO</h1>
                    <p class="tm-text-gold tm-text-2xl">where every bite tells a story!</p>
                    <div class="Login"><button id="loginBtn">Login</button></div>
                    <div class="login-container hidden" id="loginContainer">
                        <h2>Login</h2>
                        <form id="loginForm" action="login.php" method="post">
                            <div class="input-group">
                                <label for="username">Username:</label>
                                <input type="text" id="username" name="username" required>
                            </div>
                            <div class="input-group">
                                <label for="password">Password:</label>
                                <input type="password" id="password" name="password" required>
                            </div>
                            <button type="submit">Login</button>
                        </form>
                    </div>
                </div>                                         
            </div>
        </div>        
    </div>


    <script src="script.js"></script>
</div>
</div>        
</div>



    <script src="js/jquery-3.6.0.min.js"></script>
    <script src="js/parallax.min.js"></script>
    <script src="js/jquery.singlePageNav.min.js"></script>
    <script>

        function checkAndShowHideMenu() {
            if(window.innerWidth < 768) {
                $('#tm-nav ul').addClass('hidden');                
            } else {
                $('#tm-nav ul').removeClass('hidden');
            }
        }

        $(function(){
            var tmNav = $('#tm-nav');
            tmNav.singlePageNav();

            checkAndShowHideMenu();
            window.addEventListener('resize', checkAndShowHideMenu);

            $('#menu-toggle').click(function(){
                $('#tm-nav ul').toggleClass('hidden');
            });

            $('#tm-nav ul li').click(function(){
                if(window.innerWidth < 768) {
                    $('#tm-nav ul').addClass('hidden');
                }                
            });

            $(document).scroll(function() {
                var distanceFromTop = $(document).scrollTop();

                if(distanceFromTop > 100) {
                    tmNav.addClass('scroll');
                } else {
                    tmNav.removeClass('scroll');
                }
            });
            
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();

                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
        });
    </script>

</body>
</html>
"""

class FoodChatbot:
    def __init__(self):
        self.menu = {
            "pizza": {"price": 10, "category": "non veg"},
            "burger": {"price": 8, "category": "non veg"},
            "salad": {"price": 6, "category": "veg"},
            "pasta": {"price": 12, "category": "non veg"},
            "sandwich": {"price": 7, "category": "veg"},
            "sushi": {"price": 15, "category": "non veg"},
            "steak": {"price": 20, "category": "non veg"},
            "chicken": {"price": 14, "category": "non veg"},
            "taco": {"price": 9, "category": "non veg"},
            "burrito": {"price": 11, "category": "non veg"},
            "soup": {"price": 5, "category": "veg"},
            "fries": {"price": 4, "category": "veg"},
            "ice cream": {"price": 6, "category": "veg"},
            "cake": {"price": 8, "category": "veg"},
            "smoothie": {"price": 5, "category": "veg"}
        }
        self.cart = {}
        
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="food"
        )
        self.db_cursor = self.db_connection.cursor()
        self.create_order_table()  # Call the method to create the table
        self.create_status_table()

    def create_order_table(self):
        # SQL command to create the "order" table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS `order` (
            `item_name` VARCHAR(255),
            `quantity` INT
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    
    def fetch_order_status_from_database(self,order_id):
        try:
        # Establish connection to the MySQL database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="food"
            )

        # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

        # SQL query to retrieve the status of the given order ID from the database
            query = "SELECT status FROM track WHERE order_id = %s"

        # Execute the query with the provided order ID
            cursor.execute(query, (order_id,))

        # Fetch the result (order status)
            result = cursor.fetchone()

            if result:
            # If order status is found, return it
                return result[0]
            else:
            # If order status is not found, return None
                return None

        except mysql.connector.Error as error:
        # Handle any errors that occur during database operation
            print("Error while fetching order status:", error)
            return None

        finally:
        # Close the cursor and database connection
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
    
    
    
    def create_status_table(self):
        # SQL command to create the "order" table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS `track` (
            `order_id` INT,
            `status` VARCHAR(255) DEFAULT 'Preparing'
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    def insert_order_data(self, item, quantity ):
        # SQL command to insert order data into the "order" table
        insert_query = """
        INSERT INTO `order` (item_name, quantity)
        VALUES (%s, %s)
        """
        order_data = (item,quantity)
        self.db_cursor.execute(insert_query, order_data)
        self.db_connection.commit()
    
    
    
    def insert_bill_data(self, order_id, item, quantity, username,total):  # Added username parameter
        insert_query = """
        INSERT INTO data (order_id, items, quantity, username, order_timestamp,total)  # Updated query to include order_timestamp
        VALUES (%s, %s, %s, %s, %s, %s)
            """
        current_time = datetime.now()  # Get the current date and time
        bill_data = (order_id, item, quantity, username, current_time,total)  # Updated data tuple
        self.db_cursor.execute(insert_query, bill_data)
        self.db_connection.commit()

        session['order_id'] = order_id
        session['item'] = item
        return order_id,item

    def insert_order_status(self, order_id, status):
        # SQL command to insert order status data into the "track" table
        insert_query = """
        INSERT INTO `track` (order_id, status)
        VALUES (%s, %s)
        """
        status_data = (order_id, status)
        self.db_cursor.execute(insert_query, status_data)
        self.db_connection.commit()
        

    

    def insert_cost_data(self,order_id,total ):
        # SQL command to insert order data into the "order" table
        insert_query = """
        INSERT INTO `bill` (order_id,total_cost)
        VALUES (%s, %s)
        """
        cost_data = (order_id,total)
        self.db_cursor.execute(insert_query,cost_data)
        self.db_connection.commit()
        
    def insert_orders(self,username,item,quantity,order_date,total):
        insert_query = """
        INSERT INTO `orders` (username,order_date,items,quantity,total)
        VALUES (%s, %s,%s,%s,%s)
        """
        profile_data = (username,item,order_date,quantity,total)
        self.db_cursor.execute(insert_query,profile_data)
        self.db_connection.commit()

    def welcome(self):
        return "Welcome to our food ordering service! How can I assist you today?"
    
    def display_menu(self):
        menu_list = "\n".join([f"{item.capitalize()}: ₹{details['price']}" for item, details in self.menu.items()])
        return f"Here's our menu:\n{menu_list}"
    
    def add_to_menu(self, item, price):
        self.menu[item.lower()] = {"price": price}
        return f"{item.capitalize()} has been added to the menu."
    
    def order(self, item, quantity=1):
        
        item = item.lower()
        if item in self.menu:
            if item in self.cart:
                self.cart[item] += quantity
            else:
                self.cart[item] = quantity
            return f"You've added {quantity} {item}(s) to your cart."
        else:
            return "Sorry, we don't have that item in our menu."
    
    def remove_order_item(self, item, quantity=None):
        if item in self.cart:
            if quantity is None or quantity >= self.cart[item]:
                del self.cart[item]
                return f"Removed all {item} from the order."
            else:
                self.cart[item] -= quantity
                return f"Removed {quantity} {item} from the order."
        else:
            return f"{item} is not in the order."
    
    def display_cart(self):
        if not self.cart:
            return "Your cart is empty."
        cart_items = "\n".join([f"{item.capitalize()}: {quantity}" for item, quantity in self.cart.items()])
        return f"Your cart:\n{cart_items}"
    
    def calculate_total(self):
        total = sum([self.menu[item]['price'] * quantity for item, quantity in self.cart.items()])
        session['total'] = total  # Store the total in the session
        return total 
    
    def place_order(self):
        
        
        if not self.cart:
            return "Your cart is empty. Please add items before placing the order."
        if 'username' not in session:  # Check if the user is logged in
            return "Please login to place an order."
        username = session['username']  # Retrieve the username from the session
        for item, quantity in self.cart.items():
            self.insert_order_data(item, quantity)
           
            
        order_id = randint(10, 999)  # Random 2 to 3 digit order ID
        total_cost = self.calculate_total()
        self.insert_cost_data(order_id,total_cost)
        self.insert_bill_data(order_id,item,quantity,username,total_cost)
        self.insert_order_status(order_id,'perparing')
        self.cart.clear()
        return f"Your order has been placed. Order ID: #{order_id}. Thank you!"
        
            
    def final_order(self):
        total_cost = self.calculate_total()  # Calculate total cost
        order_summary = (
            "<pre><a href='/pay' style='color:green;'>Proceed to payment      </a></pre>"+
            self.display_cart() + "\n"
            + "Your total cost is: $      " + str(total_cost) + "\n"
            + self.place_order() 
              # Add the payment link
        )
    # Assuming self.place_order() stores the order data in the database
        self.place_order()  # Call the place_order function to store data in the database
        return order_summary

    def track_order(self):
        # Assuming a simple tracking mechanism
        return "Your order is being prepared. It will be delivered shortly."
    
    
    def chat(self, user_input):
        response = ""
        if any(greeting in user_input for greeting in ["hi", "hello", "hey"]):
            response = "Hello! How can I assist you today?"
        elif user_input == "bye" or user_input == "goodbye":
            response = "Goodbye! Have a great day!"
        elif user_input in ["display menu", "menu", "show menu", "give menu"]:
            response = self.display_menu()
        elif user_input.startswith("add"):
            parts = user_input.split()
            if len(parts) == 3 and parts[1] == "to" and parts[2] == "menu":
                response = self.add_to_menu(parts[0], 0)  # Assuming price is not specified
            else:
                response = "Invalid input. Please use the format: 'add <item> to menu'."
        elif user_input.startswith("order"):
            parts = user_input.split()
            if len(parts) == 2:
                response = self.order(parts[1])
            elif len(parts) == 3 and parts[2].isdigit():
                response = self.order(parts[1], int(parts[2]))
            else:
                response = "Invalid input. Please use the format: 'order <item> [quantity]'."
        
        elif user_input.startswith("remove"):
            parts = user_input.split()
            if len(parts) == 2:
                response = self.remove_order_item(parts[1])
            elif len(parts) == 3 and parts[2].isdigit():
                response = self.remove_order_item(parts[1], int(parts[2]))
            else:
                response = "Invalid input. Please use the format: 'remove <item> [quantity]'."
            
            # Code for removing items from cart
        elif user_input in ["show cart", "display cart", "cart", "my orders"]:
            response = self.display_cart()
        elif user_input in ["calculate total", "total", "total price", "show bill", "bill"]:
            response = self.calculate_total()
        elif user_input in ["final order"]:
            response = self.final_order()
        elif user_input in ["track order status", "order status","status"]:
            response = "what is your order ID?"
        elif user_input.isdigit():  # Assuming order ID is numeric
    # Assuming you have a function to fetch order status from the database
            order_id = int(user_input)
            order_status = self.fetch_order_status_from_database(order_id)
            if order_status is not None:
                
                response = f"The status of your order ID {order_id} is {order_status}."
            else:
                response = "Sorry, the order ID you provided does not exist."
                
        elif user_input in ["track order", "where is my order", "check my order"]:
            response = self.track_order()
        elif user_input.lower() in ["vegetarian", "veg", "veggie", "veggies"]:
            vegetarian_items = [f"{item.capitalize()}: ₹{details['price']}\n" for item, details in self.menu.items() if "veg" in details['category']]
            response = "Here are some vegetarian options:\n" + "".join(vegetarian_items)

        elif user_input.lower() in ["non-vegetarian", "non veg", "non-veg", "nonveg", "meat"]:
            non_vegetarian_items = [f"{item.capitalize()}: ₹{details['price']}\n" for item, details in self.menu.items() if "non veg" in details['category']]
            response = "Here are some non-vegetarian options:\n" + "".join(non_vegetarian_items)

        
        else:
            response = "I'm sorry, I didn't understand that. How can I assist you?"
  
        return response

chatbot = FoodChatbot()
@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        street = request.form['street']
        email = request.form['email']
        pincode = request.form['pincode']
        phone = request.form['phone']
        
        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        
        # Check if the username already exists in the database
        db_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = db_cursor.fetchone()
        
        # Validate phone number and pincode
        phone_valid = phone.isdigit()
        pincode_valid = pincode.isdigit()

        # Set flags based on validation results
        error_flags = {
            'username_exists': bool(existing_user),
            'phone_invalid': not phone_valid,
            'pincode_invalid': not pincode_valid
        }

        # If any validation fails, render the signup page with appropriate error flags
        if any(error_flags.values()):
            return render_template('signup.html', **error_flags)
        else:
            # Insert the new user into the database
            insert_query = "INSERT INTO users (username, password, street, email, pincode, phone) VALUES (%s, %s, %s, %s, %s, %s)"
            user_data = (username, hashed_password, street, email, pincode, phone)
            db_cursor.execute(insert_query, user_data)
            db_connection.commit()
            return redirect(url_for('start'))  # Redirect to start page after signup
    else:
        return render_template('signup.html')


    
@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username exists in the database
        db_cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = db_cursor.fetchone()
        
        if user:
            # Verify the password
            stored_hashed_password = user[1]  # Assuming the hashed password is in the second column
            if check_password_hash(stored_hashed_password, password):
                # Password is correct
                session['username'] = username  # Store username in session
                if username == "admin1" and password == "123":  # Check for admin credentials
                    return redirect(url_for('admin_page'))  # Redirect to admin page
                else:
                    return redirect(url_for('chat_page'))  # Redirect to chat page for regular users
            else:
                return render_template('login.html', password_incorrect=True)
        else:
            return render_template('login.html', username_not_found=True)
    else:
        return render_template('login.html')

@app.route('/nice')
def nice():
    # Fetch user data from the database
    return render_template('nice.html')

@app.route('/admin')
def admin_page():
    # Fetch user data from the database
    return render_template('admin.html')


@app.route('/admin_user')
def admin_user():
    db_cursor.execute("SELECT username, street, email, pincode, phone FROM users")
    users = db_cursor.fetchall()
    return render_template('admin_user.html', users=users)

@app.route('/admin_orders')
def admin_orders_page():
    # Fetch data from the database
    db_cursor.execute("SELECT order_id, items, quantity FROM data")
    data = db_cursor.fetchall()
    return render_template('admin_orders.html', data=data)

@app.route('/admin_status')
def admin_status_page():
    # Fetch order IDs from the track table
    db_cursor.execute("SELECT order_id FROM track")
    orders = db_cursor.fetchall()
    return render_template('admin_status.html', orders=orders)


@app.route('/update_status', methods=['POST'])
def update_status():
    if request.method == 'POST':
        order_id = request.form['order_id']
        status = request.form['status']
        # Update status in the database (track table)
        update_query = "UPDATE track SET status = %s WHERE order_id = %s"
        db_cursor.execute(update_query, (status, order_id))
        db_connection.commit()
        return render_template('admin_status.html')
    else:
        return "Method not allowed"
    
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('start'))

@app.route('/close_chatbot', methods=['POST'])
def close_chatbot():
    # Perform any necessary actions to close the chatbot
    
    # Redirect to the home page
    return redirect(url_for('home'))


@app.route('/chat', methods=['GET', 'POST'])
def chat_page():
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = chatbot.chat(user_input)
        return jsonify({'response': response})
    else:
        return render_template('index.html')
    
from flask import session

@app.route('/pay')
def func_name():
    total = session.get('total')  # Retrieve the total from the session
    if total is not None:
        return render_template('form.html', total=total)
    
    else:
        return "Error: Total not found in session."


@app.route('/payment', methods=["GET", "POST"])
def pay():
    amount = request.form.get("amount")  # Corrected the form field name to match
    if amount is not None and amount != "":
        amount_in_paise = int(amount) * 100  # Convert amount to paise
        data = { "amount": amount_in_paise, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)
        pdata = [amount_in_paise, payment["id"]]
        return render_template("payment.html", pdata=pdata)
    return redirect("/")

@app.route('/success', methods=["POST"])
def success():
    pid = request.form.get("razorpay_payment_id")
    ordid = request.form.get("razorpay_order_id")
    sign = request.form.get("razorpay_signature")
    print(f"The payment id : {pid}, order id : {ordid} and signature : {sign}")
    params = {
        'razorpay_order_id': ordid,
        'razorpay_payment_id': pid,
        'razorpay_signature': sign
    }
    final = client.utility.verify_payment_signature(params)
    if final:
        return render_template("index.html", code=301)
    return "Something Went Wrong Please Try Again"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ingleyogesh2004@gmail.com'
app.config['MAIL_PASSWORD'] = "amfn csjm vfmx aded"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/sendmail', methods=['GET', 'POST'])
def sendmail():
    if request.method == 'POST':
        try:
            # Connect to the database
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="food"  # Update with your database name
            )
            db_cursor = db_connection.cursor()

            # Fetch email addresses of all users from the database
            db_cursor.execute("SELECT email FROM users")
            users = db_cursor.fetchall()

            # Send email to each recipient
            for user in users:
                recipient = user[0]  # Assuming email is the first column in the users table
                subject = request.form['subject']
                message_body = request.form['message']

                msg = Message(subject, sender='noreply@demo.com', recipients=[recipient])
                msg.body = message_body
                mail.send(msg)
            
            return render_template('admin.html')  # Render admin page after sending emails
        except Exception as e:
            # Handle any exceptions that occur during database query or email sending
            print("An error occurred:", str(e))  # Print the specific error
            return "An error occurred while sending emails: " + str(e)
        finally:
            # Close database connection
            if 'db_connection' in locals() and db_connection.is_connected():
                db_cursor.close()
                db_connection.close()

    # If the request method is not 'POST', redirect to a different page or return a response
    return render_template('a.html')

@app.route('/recognize_speech')
def recognize_speech():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")

        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)

        # Record the audio
        audio = recognizer.listen(source)

        print("Recognizing...")

        try:
            # Use Google Web Speech API to recognize the audio
            text = recognizer.recognize_google(audio)
            return jsonify({'text': text})  # Return recognized text as JSON response
        except sr.UnknownValueError:
            return jsonify({'error': 'Sorry, I could not understand the audio.'})
        except sr.RequestError as e:
            return jsonify({'error': f'Could not request results from Google Speech Recognition service; {e}'})
    
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        
        # Fetch orders from the database
        db_cursor.execute("SELECT order_id, order_timestamp, items, quantity, total FROM data WHERE username = %s", (username,))
        orders = db_cursor.fetchall()
        
        # Fetch address details from the database
        db_cursor.execute("SELECT email, phone, street, pincode FROM users WHERE username = %s", (username,))
        address_info = db_cursor.fetchone()
        
        db_cursor.execute("SELECT username ,review_text, star_rating FROM reviews")
        reviews = db_cursor.fetchall()
        # Check if address info is found
        if address_info:
            email, phone, street, pincode = address_info
        else:
            email, phone, street, pincode = "", "", "", ""
        
        

        
        return render_template('profile.html', username=username, orders=orders, email=email, phone=phone, street=street, pincode=pincode,reviews=reviews)
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('start'))
    
@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'username' not in session:
        return redirect(url_for('start'))

    if request.method == 'POST':
        star_rating = request.form['rating']
        review_text = request.form['review']
        username = session['username']

        # Insert the review into the reviews table
        insert_review_query = """
        INSERT INTO reviews (username, review_text, star_rating)
        VALUES (%s, %s, %s)
        """
        db_cursor.execute(insert_review_query, (username, review_text, star_rating))
        db_connection.commit()

        return redirect(url_for('profile'))

    return render_template('profile.html')
def get_db_connection():
    connection = mysql.connector.connect(
       
                host="localhost",
                user="root",
                password="",
                database="food"
        
    )
    return connection
@app.route('/view')
def show_reviews():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT username, review_text, star_rating FROM reviews ORDER BY review_id DESC")
    reviews = cursor.fetchall()
    cursor.close()
    connection.close()

    # Set user_review and remaining_reviews with default values if no reviews
    if reviews:
        user_review = reviews[0]
        remaining_reviews = reviews[1:]
    else:
        user_review = None
        remaining_reviews = []

    return render_template('view.html', user_review=user_review, reviews=remaining_reviews)




if __name__ == '__main__':
    app.run(debug=True)