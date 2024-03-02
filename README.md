# Flask SAML Integration

This repository provides Flask applications with the capability to integrate SAML (Security Assertion Markup Language) authentication seamlessly. 

## Overview

The repository consists of two main files:

1. **app.py**: This file contains the main Flask application code for handling SAML authentication. It defines routes for login, logout, and user profile, and includes configuration for SAML Service Provider (SP) and Identity Providers (IdPs). The `ExampleServiceProvider` class extends `ServiceProvider` from `flask_saml2.sp` and defines methods for retrieving logout and login return URLs.

2. **demo.py**: This file serves as a demonstration of Flask SAML integration. It also contains Flask application code for handling SAML authentication. Similar to `app.py`, it defines routes for login, logout, and user profile, and includes configuration for SAML SP and IdPs. Additionally, it demonstrates dynamic addition of IdPs using a route `/add_idp`.

## Usage

To use this repository:

1. Install Flask and Flask-SAML:

```bash
pip install flask
pip install flask-saml
```

2. Choose either `app.py` or `demo.py` as the basis for your Flask application.

3. Customize the SAML configuration in the chosen file according to your IdP setup.

4. Run your Flask application.

## Contributing

Contributions to this repository are welcome. If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.


