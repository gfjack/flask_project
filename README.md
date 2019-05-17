# flask_project


# Purpose of application: 
This application is aim at collecting data from users, every user votes their favourite game, the system will rank different games according to users’ data to get top ranked games. 

The social choice mechanism we chose is First past the post voting.

 In the index page, there are multiple cards on the main part of the index page, each card contains a game title, game description and a Vote button, every user can vote once for one game. And every user can create their own favourite game option. On the top right-hand part of the index page, the system will rank these games in terms of their tickets and show the results in this part. 

# Architecture and design:
Front-end structures: 6 pages in total: Index page, create a new options page, sign in page, sign up page, admin console page and introduction page. Every page there is the same nav bar part. 

Index page: there is a nav bar part, following is the main part showing the options that user can vote, on the right-hand side, two different ways (text and bar chart) to describe the results after ranking. Besides, there is a footer in the bottom of the index page containing the last modified date.

Introduction page: some basic introductions for users and administrator

Sign in/Sign up page: some basic forms to allow users to register and sign in

Create a new options page: two forms allow users to create new options

Admin console page: Allow administrator to delete/modify polls and logs, delete users.

Basically, we use SQLAlchemy to store data, we have 4 tables:

Game_info: store information of game options, every time when the page refreshed, we send data to the index page to show games for users. Administrator can delete/add/edit records using AJAX.

User_info: store users’ information, when a new user registered, data will be stored into this table, the administrator can delete users in this table, or add a new user.

Voted_info: this table is used to limit the number of tickets a user can vote, when starting the application, this table is empty, for instance, if user_1 voted game_1, his voted log will be stored into this table, if he attempts to vote this game again, he will get an error/warning. After every logging out, this table will be empty again.

Log: this table just simply records the login history and vote history of different users, and show records to the administrator. The administrator can delete a vote log to make that vote marked as invalid, which means that a ticket will be deducted from the database.

If a user is not logged in, he could only see the options and results, once he logged in, he can vote a ticket for a game. If he tries to vote a game, we are using ajax to send relative data to the backend to update the database. If he attempts to create a new game option that already exists, he will get a warning.

If a user logged in as the administrator, he will be redirected into the console page, he could modify the game options (such as game_title, game_description, number of tickets), we are doing this using ajax to send data to backend. The administrator can also delete registered users, delete vote logs.

# How to launch:



# Unit tests: 
 We have 6 unit tests for our program, in the beginning, we set up the database, simply store some data into the tables. 
To launch the test, just simply use command line: python test.py

Test 1: test the index page

Test 2: test the introduction page

Test 3: test the create_new_game page

Test 4: test delete games function

Test 5: test if it is successfully committed

Test 6: test if it can log out safely 

# Contributions: 

Front-end: 
Fengjie GU (22268194) is responsible for the create new vote, introduction page and index page
Minghui SUN (22140595) is responsible for the sign in and sign up page
Admin page were written together

Back-end: 
Fengjie GU (22268194): implements the database, create new vote and index functionalities
Minghui SUN(22140595): implements the sign in, sign up, administrator functionalities

