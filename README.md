Space Bot ISS Tracker and Webex Messenger
1. Overview
This project is a small Python bot I created to track the International Space Station (ISS) in real time and share its position inside a Webex chat room.
It works by bringing together three different APIs. The ISS Location API, the OpenWeather Geocoding API, and the Webex Messaging API, to collect, translate and post live information about the ISS.
It shows how different technologies can be combined to automate a task and communicate data automatically, which is an important part of modern networking and cybersecurity work.
________________________________________
2. Objectives
The main aim of my Space Bot was to:
•	Learn how to connect and use different APIs together.
•	Read messages from a Webex room and react when a user types /seconds.
•	After waiting for the number of seconds written, send back the current ISS location.
•	Convert the raw latitude and longitude into a real place name using the OpenWeather Geocoding API.
•	Practice using Python, JSON data, and environment variables securely.
________________________________________
3. APIs Used
ISS Location API
•	Purpose: Provides the live latitude and longitude coordinates of the International Space Station (ISS).
•	Example Endpoint: http://api.open-notify.org/iss-now.json
OpenWeather Geocoding API
•	Purpose: Converts the ISS coordinates into a readable geographic location (such as a city, country or over ocean).
•	Example Endpoint: https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&appid={API_KEY}
Webex Messaging API
•	Purpose: Allows the Space Bot to send and receive messages from a Webex room.
•	Example Endpoint: https://webexapis.com/v1/messages
I tested each of these APIs individually first to understand how they respond, before combining them into one working program.
________________________________________
4. System Design and Functionality
1.	The bot loads my Webex token and OpenWeather key from a local .env file.
2.	It lists the Webex rooms I am part of and connects to the one called ISS Bot Room.
3.	It looks for messages starting with / followed by a number (for example /5).
4.	The bot waits that number of seconds, then checks the ISS API for the live position.
5.	The latitude and longitude are sent to OpenWeather’s API to find out which area of the world the ISS is above.
6.	The bot finally posts a message back into the Webex room, showing:
o	Date and time of the reading
o	Latitude and longitude
o	City, region, or over ocean message
________________________________________
5. Key Python Components
•	requests – used for API communication.
•	time – to delay responses by the number of seconds entered.
•	dotenv – to load tokens securely.
•	json – for handling API responses.
•	Simple try/except blocks for network or key errors.
This helped me understand how Python handles live data and timing.
________________________________________
6. Security Considerations
All my private API tokens are stored in a file called .env, which is kept locally and not uploaded to GitHub.
The .env file is added to .gitignore so the repository stays safe.
This method prevents my Webex or OpenWeather accounts from being exposed and follows good cybersecurity practice.
________________________________________
7. Version Control
I used GitHub Desktop to track changes.
Throughout development I made commits such as:
•	Setting up and testing the ISS API
•	Adding reverse geocoding
•	Adding the Webex messaging function
•	Cleaning unused files and protecting .env
I also removed older test scripts like index.html, script.py, space_iss.py so the repository only contains the final working version.
________________________________________
8. How to Run the Space Bot
1.	Clone the repository from GitHub.
2.	Create a .env file and add:
3.	WEBEX_TOKEN=your_webex_token
4.	OPENWEATHER_KEY=your_openweather_key
5.	Install the libraries:
6.	pip install -r requirements.txt
7.	Run the program:
8.	python space_bot.py
9.	In Webex, type /5 in the ISS Bot Room and the bot will reply after five seconds.
________________________________________
9. Testing and Example Output
When tested successfully, the bot replied with messages such as:
🛰️ On Sat Nov 01 18:35:46 2025 UTC, the ISS was over Namibe Province, Angola. 
Coordinates: (-15.6527°, 12.2120°)
If the ISS was above the ocean, the response was:
🌍 The ISS is currently flying over: Over an ocean or unknown location.
This confirmed that both the ISS and Geocoding APIs were working correctly.
________________________________________
10. Conclusion
Completing this Space Bot taught me how to combine multiple APIs, manage authentication securely, and automate responses in real time.
It gave me confidence in using Python for data integration and made me appreciate the importance of version control and documentation.
Even though I found it challenging at first, breaking it down step-by-step helped me understand it fully and enjoy the process.
________________________________________
References
Cisco (2025) Supercharge Your Webex Development with Cisco AI Assistant in Webex Developer Portal. [online] Available at: https://developer.webex.com/blog/supercharge-your-webex-development-with-cisco-ai-assistant-in-webex-developer-portal (Accessed: 31 October 2025).
Geocoding API [online] Available at:   Geocoding API - OpenWeatherMap (Accessed: 31 October 2025).
Python Requests Library [online] Available at  https://requests.readthedocs.io (Accessed: 28 October 2025).
Python dotenv Library (2025) https://pypi.org/project/python-dotenv/ (Accessed: 28 October 2025).
University of Hertfordshire (2025) Module Unit Notes – Web Technologies Labs.
