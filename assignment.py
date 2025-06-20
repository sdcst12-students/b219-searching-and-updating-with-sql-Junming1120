




import sqlite3
import datetime
import os
import re


dbase = 'pet_clinic.db'




def create_tables():
   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   cursor.execute('''
   CREATE TABLE IF NOT EXISTS customers (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       fname TEXT,              -- first name
       lname TEXT,              -- last name
       phone TEXT,              -- phone number
       email TEXT,              -- email
       address TEXT,            -- address
       city TEXT,               -- city
       postalcode TEXT          -- postal code
   )
   ''')


   cursor.execute('''
   CREATE TABLE IF NOT EXISTS pets (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT,               -- pet name
       type TEXT,               -- pet type
       breed TEXT,              -- pet breed
       birthdate TEXT,          -- birthdate
       owner_id INTEGER,        -- owner ID
       FOREIGN KEY (owner_id) REFERENCES customers(id)
   )
   ''')


   cursor.execute('''
   CREATE TABLE IF NOT EXISTS visits (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       pet_id INTEGER,          -- pet ID
       owner_id INTEGER,        -- owner ID
       visit_date TEXT,         -- visit date
       details TEXT,            -- visit detail
       cost REAL,               -- cost
       paid REAL,               -- paid
       FOREIGN KEY (pet_id) REFERENCES pets(id),
       FOREIGN KEY (owner_id) REFERENCES customers(id)
   )
   ''')


   conn.commit()
   conn.close()




def validate_email(email):
   pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   return re.match(pattern, email) is not None




def validate_phone(phone):
   return phone.isdigit()




def add_customer():
   print("\n=== Add new customer ===")


   fname = input("Enter first name: ")
   lname = input("Enter last name: ")


   while True:
       phone = input("Enter phone number: ")
       if validate_phone(phone):
           break
       print("Invalid phone number, try again")


   while True:
       email = input("Enter email: ")
       if validate_email(email):
           break
       print("Invalid email, try again")


   address = input("Enter address: ")
   city = input("Enter city: ")
   postalcode = input("Enter postal code: ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   cursor.execute("SELECT * FROM customers WHERE phone=? OR email=?", (phone, email))
   existing_customer = cursor.fetchone()


   if existing_customer:
       print("\nphone number or email already exists！")
       print("Current customer information：")
       print(f"ID: {existing_customer[0]}")
       print(f"Name: {existing_customer[2]} {existing_customer[1]}")
       print(f"Phone number: {existing_customer[3]}")
       print(f"Email: {existing_customer[4]}")


       confirm = input("\nStill want to add？(y/n): ")
       if confirm.lower() != 'y':
           conn.close()
           return
   cursor.execute("SELECT * FROM customers WHERE lname=?", (lname,))
   same_lastname = cursor.fetchall()


   if same_lastname:
       print("\nFound same last name：")
       for customer in same_lastname:
           print(f"ID: {customer[0]}, Name: {customer[2]} {customer[1]}, Phone number: {customer[3]}")


       confirm = input("\nStill want to add？(y/n): ")
       if confirm.lower() != 'y':
           conn.close()
           return


   cursor.execute('''
   INSERT INTO customers (fname, lname, phone, email, address, city, postalcode)
   VALUES (?, ?, ?, ?, ?, ?, ?)
   ''', (fname, lname, phone, email, address, city, postalcode))


   conn.commit()
   new_id = cursor.lastrowid


   print(f"\nAdded! Customer ID: {new_id}")
   add_pet_now = input("\nAdd pet information？(y/n): ")
   if add_pet_now.lower() == 'y':
       add_pet(new_id)


   conn.close()




def add_pet(owner_id=None):
   print("\n=== Add new pet ===")


   if owner_id is None:
       owner_id = search_customer_for_pet()
       if owner_id is None:
           return


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   cursor.execute("SELECT fname, lname FROM customers WHERE id=?", (owner_id,))
   owner = cursor.fetchone()
   if not owner:
       print(f"Error, cannot find customer with ID:{owner_id}")
       conn.close()
       return


   print(f"\nOwner information: {owner[0]} {owner[1]} (ID: {owner_id})")


   name = input("Pet name: ")


   pet_type = input("Pet type (dog/cat/bird等): ")
   breed = input("Pet breed: ")


   while True:
       birthdate = input("Enter pet birthdate(YYYY-MM-DD): ")
       try:
           datetime.datetime.strptime(birthdate, '%Y-%m-%d')
           break
       except ValueError:
           print("Invalid entry, use format of YYYY-MM-DD")


   cursor.execute('''
   INSERT INTO pets (name, type, breed, birthdate, owner_id)
   VALUES (?, ?, ?, ?, ?)
   ''', (name, pet_type, breed, birthdate, owner_id))


   conn.commit()
   new_id = cursor.lastrowid


   print(f"\nAdded! pet ID: {new_id}")
   conn.close()




def search_customer_for_pet():
   print("\n=== Search customer ===")
   print("1. ID")
   print("2. Name")
   print("3. Phone number")
   print("4. Email")


   choice = input("Select searching method (1-4): ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   if choice == '1':
       customer_id = input("Enter customer ID: ")
       cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
   elif choice == '2':
       name = input("Enter customer name: ")
       cursor.execute("SELECT * FROM customers WHERE fname LIKE ? OR lname LIKE ?",
                      (f"%{name}%", f"%{name}%"))
   elif choice == '3':
       phone = input("Enter phone number: ")
       cursor.execute("SELECT * FROM customers WHERE phone LIKE ?", (f"%{phone}%",))
   elif choice == '4':
       email = input("Enter email: ")
       cursor.execute("SELECT * FROM customers WHERE email LIKE ?", (f"%{email}%",))
   else:
       print("Invalid entry")
       conn.close()
       return None


   customers = cursor.fetchall()
   conn.close()


   if not customers:
       print("No matched customer")
       return None


   print("\nInformation:")
   for i, customer in enumerate(customers, 1):
       print(f"{i}. ID: {customer[0]}, Name: {customer[1]} {customer[2]}, Phone number: {customer[3]}")


   if len(customers) == 1:
       return customers[0][0]


   while True:
       try:
           selection = int(input("\nSelect customer number: "))
           if 1 <= selection <= len(customers):
               return customers[selection - 1][0]
           print("Invalid entry")
       except ValueError:
           print("Enter numbers")




def search_customer():
   print("\n=== Search customer ===")
   print("1. ID")
   print("2. Name")
   print("3. Phone")
   print("4. Email")
   print("5. City")


   choice = input("Select methods (1-5): ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   if choice == '1':
       customer_id = input("Enter customer ID: ")
       cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
   elif choice == '2':
       name = input("Enter customer name: ")
       cursor.execute("SELECT * FROM customers WHERE fname LIKE ? OR lname LIKE ?",
                      (f"%{name}%", f"%{name}%"))
   elif choice == '3':
       phone = input("Enter phone number: ")
       cursor.execute("SELECT * FROM customers WHERE phone LIKE ?", (f"%{phone}%",))
   elif choice == '4':
       email = input("Enter email: ")
       cursor.execute("SELECT * FROM customers WHERE email LIKE ?", (f"%{email}%",))
   elif choice == '5':
       city = input("Enter city: ")
       cursor.execute("SELECT * FROM customers WHERE city LIKE ?", (f"%{city}%",))
   else:
       print("Invalid entry")
       conn.close()
       return


   customers = cursor.fetchall()


   if not customers:
       print("No matched customer")
       conn.close()
       return


   print("\nInformation:")
   for customer in customers:
       print(f"ID: {customer[0]}")
       print(f"Name: {customer[1]} {customer[2]}")
       print(f"Phone: {customer[3]}")
       print(f"Email: {customer[4]}")
       print(f"Address: {customer[5]}")
       print(f"City: {customer[6]}")
       print(f"Postal code: {customer[7]}")


       cursor.execute("SELECT * FROM pets WHERE owner_id=?", (customer[0],))
       pets = cursor.fetchall()


       if pets:
           print("\nPet information:")
           for pet in pets:
               print(f"  Pet ID: {pet[0]}, Name: {pet[1]}, Type: {pet[2]}, breed: {pet[3]}, Birthdate: {pet[4]}")


       print("-" * 40)


   conn.close()




def update_customer():
   print("\n=== Edit customer information ===")


   customer_id = search_customer_for_update()
   if customer_id is None:
       return


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
   customer = cursor.fetchone()


   if not customer:
       print(f"Error cannot find customer with ID: {customer_id}")
       conn.close()
       return


   print("\nCurrent customer information：")
   print(f"ID: {customer[0]}")
   print(f"First name: {customer[1]}")
   print(f"Last name: {customer[2]}")
   print(f"Phone: {customer[3]}")
   print(f"Email: {customer[4]}")
   print(f"Address: {customer[5]}")
   print(f"City: {customer[6]}")
   print(f"Postal code: {customer[7]}")


   print("\nPlease enter new information (press enter to remain unchanged)：")


   new_fname = input(f"first name [{customer[1]}]: ") or customer[1]
   new_lname = input(f"last name [{customer[2]}]: ") or customer[2]


   while True:
       new_phone = input(f"Phone number[{customer[3]}]: ") or customer[3]
       if validate_phone(new_phone):
           break
       print("Invalid phone number")


   while True:
       new_email = input(f"Email [{customer[4]}]: ") or customer[4]
       if validate_email(new_email):
           break
       print("Invalid email")


   new_address = input(f"address [{customer[5]}]: ") or customer[5]
   new_city = input(f"city [{customer[6]}]: ") or customer[6]
   new_postalcode = input(f"postal code [{customer[7]}]: ") or customer[7]


   cursor.execute('''
   UPDATE customers
   SET fname=?, lname=?, phone=?, email=?, address=?, city=?, postalcode=?
   WHERE id=?
   ''', (new_fname, new_lname, new_phone, new_email, new_address, new_city, new_postalcode, customer_id))


   conn.commit()
   print("\nCustomer information updated！")
   conn.close()




def search_customer_for_update():
   print("\n=== Search customer ===")
   print("1. ID")
   print("2. Name")
   print("3. Phone")
   print("4. Email")


   choice = input("Please select (1-4): ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   if choice == '1':
       customer_id = input("Enter customer ID: ")
       cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
   elif choice == '2':
       name = input("Enter name: ")
       cursor.execute("SELECT * FROM customers WHERE fname LIKE ? OR lname LIKE ?",
                      (f"%{name}%", f"%{name}%"))
   elif choice == '3':
       phone = input("Enter phone: ")
       cursor.execute("SELECT * FROM customers WHERE phone LIKE ?", (f"%{phone}%",))
   elif choice == '4':
       email = input("Enter email: ")
       cursor.execute("SELECT * FROM customers WHERE email LIKE ?", (f"%{email}%",))
   else:
       print("Invalid entry")
       conn.close()
       return None


   customers = cursor.fetchall()
   conn.close()


   if not customers:
       print("No matched customer")
       return None


   print("\nInformation:")
   for i, customer in enumerate(customers, 1):
       print(f"{i}. ID: {customer[0]}, Name: {customer[1]} {customer[2]}, Phone: {customer[3]}")


   if len(customers) == 1:
       return customers[0][0]


   while True:
       try:
           selection = int(input("\nSelect customer: "))
           if 1 <= selection <= len(customers):
               return customers[selection - 1][0]
           print("Invalid entry")
       except ValueError:
           print("Invalid entry")




def add_visit():
   print("\n=== Add new visits ===")


   pet_id, owner_id = search_pet_for_visit()
   if pet_id is None:
       return


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   cursor.execute("""
   SELECT p.name, p.type, p.breed, c.fname, c.lname
   FROM pets p JOIN customers c ON p.owner_id = c.id
   WHERE p.id = ? AND c.id = ?
   """, (pet_id, owner_id))
   pet_info = cursor.fetchone()


   if not pet_info:
       print("Error, no matched customer and pet")
       conn.close()
       return


   print(f"\nPet information: {pet_info[0]} (Type: {pet_info[1]}, breed: {pet_info[2]})")
   print(f"Owner information: {pet_info[3]} {pet_info[4]} (ID: {owner_id})")


   while True:
       visit_date = input("Enter visit date (YYYY-MM-DD): ")
       try:
           datetime.datetime.strptime(visit_date, '%Y-%m-%d')
           break
       except ValueError:
           print("Invalid entry, enter in form of YYYY-MM-DD")


   details = input("Enter visit detail: ")


   while True:
       try:
           cost = float(input("Enter cost: "))
           break
       except ValueError:
           print("Invalid entry")


   while True:
       try:
           paid = float(input("Enter paid balance: "))
           break
       except ValueError:
           print("Invalid entry")


   cursor.execute('''
   INSERT INTO visits (pet_id, owner_id, visit_date, details, cost, paid)
   VALUES (?, ?, ?, ?, ?, ?)
   ''', (pet_id, owner_id, visit_date, details, cost, paid))


   conn.commit()
   new_id = cursor.lastrowid


   print(f"\nVisit added! Visit ID: {new_id}")


   if cost > paid:
       print(f"Warning, ${cost - paid:.2f} unpaid")


   conn.close()




def search_pet_for_visit():
   """搜索宠物以添加就诊记录"""
   print("\n=== Search pet information ===")
   print("1. Pet ID")
   print("2. Pet name")
   print("3. Owner information")


   choice = input("Select (1-3): ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   if choice == '1':
       pet_id = input("Enter Pet ID: ")
       cursor.execute("""
       SELECT p.id, p.name, p.type, p.breed, c.id, c.fname, c.lname
       FROM pets p JOIN customers c ON p.owner_id = c.id
       WHERE p.id = ?
       """, (pet_id,))
   elif choice == '2':
       name = input("Enter pet name): ")
       cursor.execute("""
       SELECT p.id, p.name, p.type, p.breed, c.id, c.fname, c.lname
       FROM pets p JOIN customers c ON p.owner_id = c.id
       WHERE p.name LIKE ?
       """, (f"%{name}%",))
   elif choice == '3':
       owner_id = search_customer_for_pet()
       if owner_id is None:
           conn.close()
           return None, None


       cursor.execute("""
       SELECT p.id, p.name, p.type, p.breed, c.id, c.fname, c.lname
       FROM pets p JOIN customers c ON p.owner_id = c.id
       WHERE p.owner_id = ?
       """, (owner_id,))
   else:
       print("Invalid entry")
       conn.close()
       return None, None


   pets = cursor.fetchall()
   conn.close()


   if not pets:
       print("No matched pet")
       return None, None


   print("\nInformation:")
   for i, pet in enumerate(pets, 1):
       print(
           f"{i}. pet ID: {pet[0]}, Name: {pet[1]}, Type: {pet[2]}, Breed: {pet[3]}, Owner: {pet[5]} {pet[6]} (ID: {pet[4]})")


   if len(pets) == 1:
       return pets[0][0], pets[0][4]
   while True:
       try:
           selection = int(input("\nSelect pet number: "))
           if 1 <= selection <= len(pets):
               return pets[selection - 1][0], pets[selection - 1][4]  # 返回宠物ID和主人ID
           print("Invalid entry")
       except ValueError:
           print("Invalid entry")




def search_visits():
   print("\n=== Visit record ===")
   print("1. Visit ID")
   print("2. Pet ID")
   print("3. Owner ID")
   print("4. Date")


   choice = input("Select(1-4): ")


   conn = sqlite3.connect(dbase)
   cursor = conn.cursor()


   if choice == '1':
       visit_id = input("Enter visit ID: ")
       cursor.execute("""
       SELECT v.id, v.visit_date, v.details, v.cost, v.paid,
              p.id, p.name, p.type, p.breed,
              c.id, c.fname, c.lname
       FROM visits v
       JOIN pets p ON v.pet_id = p.id
       JOIN customers c ON v.owner_id = c.id
       WHERE v.id = ?
       """, (visit_id,))
   elif choice == '2':
       pet_id = input("Enter pet ID: ")
       cursor.execute("""
       SELECT v.id, v.visit_date, v.details, v.cost, v.paid,
              p.id, p.name, p.type, p.breed,
              c.id, c.fname, c.lname
       FROM visits v
       JOIN pets p ON v.pet_id = p.id
       JOIN customers c ON v.owner_id = c.id
       WHERE v.pet_id = ?
       """, (pet_id,))
   elif choice == '3':
       owner_id = input("Enter Owner ID: ")
       cursor.execute("""
       SELECT v.id, v.visit_date, v.details, v.cost, v.paid,
              p.id, p.name, p.type, p.breed,
              c.id, c.fname, c.lname
       FROM visits v
       JOIN pets p ON v.pet_id = p.id
       JOIN customers c ON v.owner_id = c.id
       WHERE v.owner_id = ?
       """, (owner_id,))
   elif choice == '4':
       start_date = input("Enter start date (YYYY-MM-DD): ")
       end_date = input("Enter end date (YYYY-MM-DD): ")
       cursor.execute("""
       SELECT v.id, v.visit_date, v.details, v.cost, v.paid,
              p.id, p.name, p.type, p.breed,
              c.id, c.fname, c.lname
       FROM visits v
       JOIN pets p ON v.pet_id = p.id
       JOIN customers c ON v.owner_id = c.id
       WHERE v.visit_date BETWEEN ? AND ?
       """, (start_date, end_date))
   else:
       print("Invalid entry")
       conn.close()
       return


   visits = cursor.fetchall()


   if not visits:
       print("No matched visits")
       conn.close()
       return


   print("\n搜索结果:")
   for visit in visits:
       print(f"Visit ID: {visit[0]}")
       print(f"Date: {visit[1]}")
       print(f"Visit detail: {visit[2]}")
       print(f"Cost: {visit[3]}")
       print(f"Paid: {visit[4]}")
       print(f"Unpaid: {visit[3] - visit[4]:.2f}")
       print(f"Pet information: ID: {visit[5]}, Name: {visit[6]}, Type: {visit[7]}, Breed: {visit[8]}")
       print(f"Owner information: ID: {visit[9]}, Name: {visit[10]} {visit[11]}")
       print("-" * 40)


   conn.close()




def main_menu():


   while True:
       print("\n=== Main menu ===")
       print("1. Add new customer")
       print("2. Add new pet")
       print("3. Search customer information")
       print("4. Edit customer information")
       print("5. Add visits")
       print("6. Search visits")
       print("7. Exit")


       choice = input("Select (1-7): ")


       if choice == '1':
           add_customer()
       elif choice == '2':
           add_pet()
       elif choice == '3':
           search_customer()
       elif choice == '4':
           update_customer()
       elif choice == '5':
           add_visit()
       elif choice == '6':
           search_visits()
       elif choice == '7':
           print("Bye Bye!")
           break
       else:
           print("Invalid entry")




if __name__ == "__main__":


   create_tables()
   main_menu()
