# SaaS Template with Flask

This is a SaaS (Software as a Service) template built with Flask, featuring user authentication, profile management, and integration with Twilio for SMS and Mailgun for email services.

## Features

- User registration and login
- Phone number verification via Twilio SMS
- Password reset via email using Mailgun
- User profile management (edit profile, cancel account)
- PostgreSQL database integration
- Environment-based configuration

## Prerequisites

- Python 3.7+
- PostgreSQL
- Twilio account
- Mailgun account

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/saas-template-flask.git
   cd saas-template-flask
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your configuration (see `.env.example` for reference).

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

## Configuration

Copy the `.env.example` file to `.env` and fill in your specific configuration:

- `SECRET_KEY`: A secret key for Flask sessions
- `DATABASE_URL`: Your PostgreSQL database URL
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`: Your Twilio credentials
- `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`: Your Mailgun credentials

## Running the Application

To run the application in development mode:

```
flask run
```

The application will be available at `http://localhost:5000`.

## Deployment

For production deployment:

1. Set `FLASK_DEBUG=False` in your `.env` file.
2. Use a production WSGI server like Gunicorn.
3. Set up a reverse proxy with Nginx or Apache.
4. Ensure all sensitive information is properly secured.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
