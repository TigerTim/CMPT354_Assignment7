import pyodbc
from uuid import uuid4
from datetime import datetime

# Establish connection
def establish_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=cypress.csil.sfu.ca;'
        'DATABASE=gpd354;'
        'UID=s_gpd;'
        'PWD=Mr43Fdrnahnjye74;'
        'Encrypt=yes;'
        'TrustServerCertificate=yes;'
    )
    return conn


# Login
def login(cursor):      # pass cursor into each func to use .execute
    cursor.execute('SELECT user_id FROM dbo.user_yelp')     # get all user_id from relation

    # return a list of rows/tuples (eventho 1 col is returned => each value is stored in a tuple (ie rows = [('user1',), ('user2',)])) => 1-ele tuple
    rows = cursor.fetchall()  

    user_id_list = []
    
    # loop thru all tuples of list of tuples
    for row in rows:    
        user_id_list.append(row[0])     # get fst ele of each tuple (ie ('user1',) => row[0] = "user1")

    input_id = input("Enter your User ID: ").strip()    # remove whitespace at 2 sides

    if input_id not in user_id_list:
        print("Invalid User ID. Please try again.")
        return None
    else:
        print(f"Welcome {input_id}! You are now logged in.")
        return input_id


# Choose functionality
def choose_func(cursor, loginId, func_num, conn):
    if func_num == "2":
        search_business(cursor, loginId)
        return True
    elif func_num == "3":
        search_users(cursor, loginId)
        return True
    else:
        print("Exiting...")
        conn.close()
        print("Connection closed.")
        return False


# Search Business
# def search_business(cursor, min_stars=0, city='', name='', order_by='name'):  # default stars is 0 and order by name (skippable for input param)
def search_business(cursor, loginId):
    print("Searching business")
    query = '''
        SELECT business_id, name, address, city, stars
        FROM dbo.business
        WHERE stars >= ?    
        AND LOWER(city) LIKE ? 
        AND LOWER(name) LIKE ?
        ORDER BY
    '''

    # Take user's input
    min_stars = input("Please enter the minimum stars: ").strip()
    city = input("Please enter the city: ").strip().lower()
    name = input("Please enter the name: ").strip().lower()
    order = input("Please enter the order (name, city or stars): ").strip().lower()

    # Order by user's choice
    orderList = {"name", "city", "stars"}   # set is faster than list b/c implemented by hash tables => O(1) in searching

    # Invalid order 
    while (order not in orderList):
        order = input("Invalid order. Please enter the valid order: ").strip().lower()

    # Prepare the search filters (case insensitive already when user inputs)
    city_filter = f'%{city}%'
    name_filter = f'%{name}%'
    query += order

    # Execute the query with the filters
    cursor.execute(query, (min_stars, city_filter, name_filter))    # replace (?) w/ param in query
    rows = cursor.fetchall()    # return a list of tuples (each tuple has size 5 => (id, name, address, city, stars))

    if rows:
        print("Resulting Businesses:")
        for row in rows:
            print(f"business_id: {row[0]}, name: {row[1]}, address: {row[2]}, city: {row[3]}, stars: {row[4]}")
        ans = input("Do you want to review business in the list (Y/N): ").strip().lower()
        if ans == "y":
            review_business(cursor, loginId)
    else:
        print("No businesses found matching your criteria.")


# Search User
def search_users(cursor, loginUserId):
    print("Searching user")
    name = input("Enter a name or part of a name to search: ").strip().lower()   # case insensitive
    min_review_count = input("Enter an integer for minimum review count: ").strip()
    min_average_stars = input("Enter the minimum average stars: ").strip()

    query = '''
            SELECT user_id, name, review_count, useful, funny, cool, average_stars, yelping_since
            FROM dbo.user_yelp
            WHERE LOWER(name) LIKE ?
            AND review_count >= ?
            AND average_stars >= ?
            ORDER BY name
            '''

    # insert into the query to execute
    name_filter = f"%{name}%"   # use %abc% w/ LIKE syntax

    cursor.execute(query, (name_filter, min_review_count, min_average_stars))
    rows = cursor.fetchall()

    if rows:
        print("Resulting Users:")
        for row in rows:
            print(f"user_id: {row[0]}, name: {row[1]}, review_count: {row[2]}, useful: {row[3]}, funny: {row[4]}, cool: {row[5]}, average_stars: {row[6]}, yelping_since: {row[7]}")
        ans = input("Do you want to make friend with one in the list (Y/N): ").strip().lower()
        if (ans == "y"):
            make_friend(cursor, loginUserId)
    else:
        print("No users found matching the criteria.")


# Make Friend
# Add a friendship between logInUserId and another user
def make_friend(cursor, logInUserId):
    # Display available users using search_users func
    print("\nSearching for users to add as a friend:")
    # search_users(cursor)  # Display resulting users

    # Prompt the logged-in user to select a friend by user_id
    friend_id = input("Enter the user_id you'd like to make friend: ").strip()

    # Check if the friendship already exists
    cursor.execute('''
                    SELECT user_id
                    FROM dbo.friendship
                    WHERE user_id = ? AND friend = ?
                    ''', (logInUserId, friend_id))
    
    # Case already friend
    if cursor.fetchone():
        print("Friendship found!")

    # Case not friend => insert friend
    else:
        # Insert the friendship into the table
        try:
            print("No friendship found!!!")
            print("Creating friendship...")
            cursor.execute('''
                            INSERT INTO friendship (user_id, friend)
                            VALUES (?, ?)
                        ''', (logInUserId, friend_id))
            print(f"Success!!! You are now a friend of user {friend_id}!")
        except pyodbc.Error as e:
            print("An error occurred while adding the friendship:", e)
        finally:
            cursor.connection.commit()  # Save the changes to the database


# Review Business
# Add a review for a business
def review_business(cursor, loginID):
    businessID = input("Please insert the business's ID that you want to review: ")

    # Check friend requirement
    check_command = """
        SELECT 1
        FROM dbo.friendship F
        WHERE F.user_id = ? 
        AND F.friend IN (SELECT R.user_id
                        FROM dbo.review R
                        WHERE business_id = ?)
        """
    cursor.execute(check_command, (loginID, businessID))
    result = cursor.fetchone()
    if not result:
        print("You must have a friend who has given a review for this business before you can leave a review!")
        return

    # Get new rating
    review_star = input("Please enter your rating of this business (1 to 5, with 1 being the worst and 5 being the best): ")
    
    # Add new record in dbo.review
    reviewID = str(uuid4())[:22]                      # generate "random" review_id
    reviewDate = datetime.now()                       # Not essential, cuz "date" has default value
    insert_command = """
        INSERT INTO dbo.review (review_id, user_id, business_id, stars, date)
        VALUES (?, ?, ?, ? , ?)
        """
    cursor.execute(insert_command, (reviewID, loginID, businessID, review_star, reviewDate))
    cursor.connection.commit()

    update_command = """
        UPDATE dbo.business
        SET stars = (
            SELECT AVG(stars)
            FROM dbo.review R
            WHERE R.business_id = ?)
        WHERE business_id = ?
    """
    cursor.execute(update_command, (businessID, businessID))
    cursor.connection.commit()
    print("Review added successfully!")


# Main function
def main():
    conn = establish_connection()
    cursor = conn.cursor()

    # Verify login
    loginId = login(cursor)
    while loginId:
        print("1. Exit Program")
        print("2. Search and Review Business")
        print("3. Search Users and Make Friends")
        func_num = input("Enter the number (1-3) to access any functionality that you want: ").strip().lower()
        if not choose_func(cursor, loginId, func_num, conn):
            break
        else:
            ans = input("Do you want to continue (Y/N): ").strip().lower()
            if ans == "n":
                print("Exiting...")
                conn.close()
                print("Connection closed.")
                break
            

if __name__ == "__main__":
    main()
