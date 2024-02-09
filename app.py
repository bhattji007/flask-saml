from flask import Flask, url_for, request, redirect, jsonify
from flask_saml2.sp import ServiceProvider
from flask_saml2.utils import certificate_from_string
from flask_saml2.utils import certificate_from_file, private_key_from_file
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class ExampleServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)

    

sp = ExampleServiceProvider()
app = Flask(__name__)
app.debug = True
app.secret_key = 'not a secret'
app.config['SERVER_NAME'] = '127.0.0.1:8082'  # Change to your desired server name
app.config['SAML2_SP'] = {
    'certificate': certificate_from_file('cert1.pem'),
    'private_key': private_key_from_file('key1.pem'),
}

# Okta Identity Provider
okta_idp = {
    'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
    'OPTIONS': {
        'display_name': 'Okta',
        'entity_id': 'http://www.okta.com/exkgkdspz4AU2NF3q4x7',
        'sso_url': 'https://dev-348625.okta.com/app/dev-348625_devapp_1/exkgkdspz4AU2NF3q4x7/sso/saml',
        'slo_url': 'https://dev-348625.okta.com/app/dev-348625_devapp_1/exkgkdspz4AU2NF3q4x7/sso/saml',
        'certificate': certificate_from_file('cert.cert')
    }
}

# Keycloak Identity Provider
keycloak_idp = {
    'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',
    'OPTIONS': {
        'display_name': 'Auth0',
        'entity_id': 'urn:dev-ybjxz6a8.us.auth0.com',
        'sso_url': 'https://dev-ybjxz6a8.us.auth0.com/samlp/NQj4fH9Gmu9lMaiu5FU3foV9XXDWjJ8Z',
        'slo_url': 'https://dev-ybjxz6a8.us.auth0.com/samlp/NQj4fH9Gmu9lMaiu5FU3foV9XXDWjJ8Z',
        'certificate': certificate_from_file('dev-ybjxz6a8.cert')
    }
}

app.config['SAML2_IDENTITY_PROVIDERS'] = [keycloak_idp]

# index route
@app.route('/')
def index():
    if sp.is_user_logged_in():
        auth_data = sp.get_auth_data_in_session()

        message = f'''
        <p>You are logged in as <strong>{auth_data.nameid}</strong>.
        The IdP sent back the following attributes:<p>
        '''
        attrs = '<dl>{}</dl>'.format(''.join(
            f'<dt>{attr}</dt><dd>{value}</dd>'
            for attr, value in auth_data.attributes.items()))

        logout_url = url_for('flask_saml2_sp.logout')
        logout = f'<form action="{logout_url}" method="POST"><input type="submit" value="Log out"></form>'

        return message + attrs + logout
    else:
        message = '<p>You are logged out.</p>'

        # Generate final login links for each IdP
        login_links = '<p>Login links:</p>'
        for idp in app.config['SAML2_IDENTITY_PROVIDERS']:
            entity_id = idp['OPTIONS']['entity_id']
            next_url = url_for('index', _external=True)
            login_url = url_for('flask_saml2_sp.login', _external=True)
            final_login_url = f'<p><a href="{login_url}/idp?entity_id={entity_id}&next={next_url}">Log in with {idp["OPTIONS"]["display_name"]}</a></p>'
            login_links += final_login_url
            print("LOGIN URL-",login_links)


        return message + login_links


@app.route('/add_idp', methods=['POST'])
def add_idp():
    try:
        data = request.form
        # pem_certificate = convert_cert_to_pem(data['certificate'])
        new_idp = {
            'CLASS': 'flask_saml2.sp.idphandler.IdPHandler',    
            'OPTIONS': {
                'display_name': data['display_name'],
                'entity_id': data['entity_id'],
                'sso_url': data['sso_url'],
                'slo_url': data['slo_url'],
                'certificate': certificate_from_file('cert.cert')
            }
        }

        app.config['SAML2_IDENTITY_PROVIDERS'].append(new_idp)
        print(app.config['SAML2_IDENTITY_PROVIDERS'])

        # Optionally, you can return a JSON response
        return jsonify({'message': 'IdP added successfully'}), 200
    except Exception as e:
        # Handle errors and return an appropriate response
        return jsonify({'error': str(e)}), 400


# Blueprint
app.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
# http://127.0.0.1:8082/saml/login/idp/?entity_id=http://www.okta.com/exkgkdspz4AU2NF3q4x7&next=http://127.0.0.1:8082/