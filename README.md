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

    bash

git clone https://github.com/filipzmija1/MyChat.git

Navigate to the project directory:

bash

cd MyChat

Optional: Create a virtual environment:

It's recommended to use a virtual environment to isolate project dependencies.

bash

virtualenv venv

Activate the virtual environment:

On Windows:

bash

venv\Scripts\activate

On macOS and Linux:

bash

source venv/bin/activate

Install project dependencies:

bash

pip install -r requirements.txt


Apply database migrations:

bash

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

bash

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