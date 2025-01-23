# YOUR PROJECT TITLE
#### Video Demo:  <https://youtu.be/MI_1FIPs97M>
#### Description:

## Journal Express
    Journal Express! A platform created for you to share your daily mental and/or real-life endeavors, poems, stories, and much more all through the power of words.
Registering allows for you to begin posting, categorizing those posts by genres that describes them best, and viewing the works of other people around the world!
Follow all your favourite anonymous pages that you come across by clicking the follow button thats right on the post! or head over to the search window, accesible by the search icon located in the Navigation bar.
To keep an equal, all-loving space, Journal Express doesn't have a like or commenting functionality. Your words mean more than a few clicks and should be valued by the sincerity of your thoughts.
The thought behind Journal Express was "A diary that other people have a key to".

### The files
    Lets look into some of the files that make up the backend of Journal Express.

#### application.py
    The python file that controls everything relating to the manipulation of data and actions that the user makes.
It contains the code that allows for posts, searches, follows, and other functionalities to be inputed into the database for later usage.
Functions include register, login, logout, index, explore, profile, journal, search, and settings - all linking primarily to corresponding HTML files.

#### layout.html
    An HTML page that contains everything that mandatorily appears in all Journal Express pages, such as the Header and the Sidebar.
Other HTML pages can be connected to this file in order to display repeating characterisitcs, without redundant copy-paste.

#### register.html and login.html
    As the names suggest, this is where you will register yourself by creating a username and password, and logining in with that username and password combination to enter the site in the future.

#### index.html
    This page holds the "feed", posts created by profiles that the user has followed will appear here.
A loop runs through a dictionary that was retreived in application.py when the pages GET request is performed.
It creates a postbox using the div's class, styled in styles.css, and inputs the profile's username, their journal, the day it was posted, as well as the genre it was categorized under.

I initially struggled with whether I would include a liking functionality. Contemplating this made my decision on commenting seem easy: On a platform where your words were to be seen but not debated, it is unneccessary to add an ability of giving opinions on other's personal feelings.
Within the social media space, likes can become digital wealth. But no amount of external value will add more quality to your words than what you think of it yourself, so I refrained.

#### profile.html
    This page includes the user's information. Posts, followers, and following data are all located here.
Upon entering, the user's username is found at the top of the page, followed by following and follower count. Clicking on each of the respective counts will provide a list of all the user's that you have followed or those who have followed you, which you may then unfollow or remove, respectively.
Continuing further down, all the user's posts will be displayed here, where they may be deleted if the user pleases to do so. The file runs a loop, creating a similar postbox to index.html, inputing the post's genre and date that it was posted, the button that allows for deletion of a post, and the journal the user posted.

#### journal.html
    This page is where the creation begins. It's where you post your thoughts and describe them using one of the pre-determined genres.
The file starts off with some text describing the mission of Journal Express followed by a textbox where you may enter your journal of the day!
You then come across radio inputs of the available genres that are used to describe posts. These genres include Cheerful, Exciting, Funny, Poetic, Storytime, Sad, Angry, and Random.
Once you hit the "Post" button, your journal will be saved into the database and added onto the index pages of your followers as well as yourself. It will also be found on your profile for your own viewing.

#### search.html
    This page has one purpose: to search through all Journal Express users and allow you to follow them!
The page first starts with a form where you are to search up whatever username/part of a username that you please, hit the search button, and be greeted with a table.
The table includes two primary columns: one containing a profile's username and another containing a button that allows the user to follow that profile.

#### explore.html
    This page allows you to browse through all the journals created by other profiles on the platform.
The file starts with a form which includes a search bar as well as a select dropbox where you may select a genre to browse. A loop runs, displaying all the posts associated with the keywords used or the chosen genre. If the user enjoys the post, they may then follow the profile using the button included in the postbox.
On the right side of the page, you will find a list of articles, all relating to journaling, self-help, and more to help you engage your mental mind space!

#### settings.html
    This page is where you can edit the information surrounding your account. Specifically, your profile username and your privacy settings.
Two buttons are placed within the table rows, "Change Username" and "Privacy".
Change username directs you to change_user.html, which will ask you to input your current username, the username you wish to switch to, and your password. If you choose to swich to an available username, the database will update and you'll now be known by a new name!
Privacy will give you the option to remove the accesibility of your writting through the explore page. Only your followers will have vision of your posts on their feeds.
    This page also includes a short FAQ section, answering the questions that I assumed would be asked often with the release of the platform. For each question, an accordion has been constructed inside a row of a table, the answers being accessed after clicking on the corresponding question.

#### change_user.html
    As mentioned in the previous description, change_user.html includes a form that allows you to input your current username, a username you'd like to convert to, and your password.
Application.py checks if the username entered belongs to the current logged in account, if the password is accurate, and if the desired username is available for use.
If all criteria is met, the database updates your account information in all tables and the name is yours!