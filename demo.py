from flask import Flask, url_for, request, redirect, jsonify
from flask_saml2.sp import ServiceProvider
from flask_saml2.utils import certificate_from_string
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class ExampleServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)

    def get_idp_login_url(self, idp_name):
        return url_for('flask_saml2_sp.login', idp=idp_name, _external=True)

app = Flask(__name__)
app.debug = True
app.secret_key = 'not a secret'
app.config['SERVER_NAME'] = 'localhost:8082'

def convert_cert_to_pem(cert_data):
    # Convert the certificate to PEM format
    cert = x509.load_pem_x509_certificate(cert_data.encode('utf-8'), default_backend())
    pem_certificate = cert.public_bytes(encoding=x509.Encoding.PEM).decode('utf-8')
    return pem_certificate

# Initialize the IdPs list
app.config['SAML2_IDENTITY_PROVIDERS'] = []
print(app.config['SAML2_IDENTITY_PROVIDERS'])
# index route
@app.route('/')
def index():
    if app.config['SAML2_SP'].is_user_logged_in():
        auth_data = app.config['SAML2_SP'].get_auth_data_in_session()

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

        # Generate login links for each IdP
        login_links = '<p>Login links:</p>'
        for idp in app.config['SAML2_IDENTITY_PROVIDERS']:
            login_url = app.config['SAML2_SP'].get_idp_login_url(idp['OPTIONS']['display_name'].lower())
            login_links += f'<p><a href="{login_url}">Log in with {idp["OPTIONS"]["display_name"]}</a></p>'

        return message + login_links

# Route to handle dynamic addition of IdPs
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
                'certificate': certificate_from_string(data['certificate'])
            }
        }

        app.config['SAML2_IDENTITY_PROVIDERS'].append(new_idp)
        print(app.config['SAML2_IDENTITY_PROVIDERS'])

        # Optionally, you can return a JSON response
        return jsonify({'message': 'IdP added successfully'}), 200
    except Exception as e:
        # Handle errors and return an appropriate response
        return jsonify({'error': str(e)}), 400

# Instantiate ExampleServiceProvider and register the blueprint
app.config['SAML2_SP'] = ExampleServiceProvider()
app.register_blueprint(app.config['SAML2_SP'].create_blueprint(), url_prefix='/saml/')

# Run the app
if __name__ == '__main__':
    app.run(port=8082)
