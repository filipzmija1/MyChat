MyChat

MyChat is a chat application that allows users to communicate in real-time. The backend is built using Django, and real-time chat functionality is using JavaScript.

Features
    Server and rooms creation: Users can create servers and rooms in servers for specific topics or groups. It enables organized discussions.
    Message history: Chat messages are archived, allowing users to view past conversations.
    Real-time chat with WebSocket: Enables users to exchange messages instantly with other users.
    User authentication and registration: Allows for user account creation and management.
    User profile management: Users can customize their profiles and settings.
    Private messaging: Users can exchange private messages with each other.

Installation

To run MyChat on your local environment, follow these steps:

    Clone the repository:
Open terminal

git clone https://github.com/filipzmija1/MyChat.git

Navigate to the project directory:

cd MyChat

Optional: Create a virtual environment:

It's recommended to use a virtual environment to isolate project dependencies.

virtualenv venv

Activate the virtual environment:

On Windows:

venv\Scripts\activate

On macOS and Linux:

source venv/bin/activate

Install project dependencies:

pip install -r requirements.txt

Installing Redis Server:

1. Open a terminal window.

2. Update your package list:

sudo apt-get update

3. Install Redis Server:

sudo apt-get install redis-server

4. Start Redis:

sudo service redis-server start

5. Check if Redis is running:

redis-cli ping

If you receive a "PONG" response, Redis is up and running.

### On macOS:

1. Install Redis via Homebrew (if not already installed):

brew install redis

markdown


2. Start Redis:

brew services start redis

3. Check if Redis is running:

redis-cli ping

If you receive a "PONG" response, Redis is up and running.

### On Windows:

Redis for Windows can be downloaded from the official GitHub repository: [Redis for Windows](https://github.com/MicrosoftArchive/redis/releases). Follow the installation instructions provided there.

## Project Setup

Once Redis is installed and running on your system, you can proceed with setting up and running the "MyChat" application. Be sure to configure your Django project to connect to the Redis server as needed.

Apply database migrations:

python manage.py makemigrations
python manage.py migrate

Configure email (optional):

To configure email handling, you need to set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in the Django configuration file. Here's how to do it:

    Open the settings.py file located in the MyChat directory.

    Find the email configuration section. It looks something like this:

    python


    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'your_smtp_host'
    EMAIL_PORT = smtp_port_number
    EMAIL_HOST_USER = 'your_email_address'
    EMAIL_HOST_PASSWORD = 'your_email_password'
    EMAIL_USE_TLS = True  # If your email server supports TLS

    Replace 'your_smtp_host', smtp_port_number, 'your_email_address', and 'your_email_password' with your actual email server credentials.

Start the development server:
    
    python manage.py runserver

    Open the application in your web browser:

    Visit http://localhost:8000 in your browser to use the application.

Usage

To use MyChat, follow these steps:

    Create an account or log in if you already have one.
    Create a chat server.
    Manage your server settings(especially permissions).
    Add other users to your server.
    Start chatting with other users in real-time.
    Manage your user profile and settings.
    Invite other users to friendlist.
    Write private messages with friends
