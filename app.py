from flask import Flask, url_for
from flask_saml2.sp import ServiceProvider
from flask_saml2.utils import certificate_from_file, private_key_from_file

class ExampleServiceProvider(ServiceProvider):
    def get_logout_return_url(self):
        return url_for('index', _external=True)

    def get_default_login_return_url(self):
        return url_for('index', _external=True)

    def get_idp_login_url(self, idp_name):
        return url_for('flask_saml2_sp.login', idp=idp_name, _external=True)

sp = ExampleServiceProvider()
app = Flask(__name__)
app.debug = True
app.secret_key = 'not a secret'
app.config['SERVER_NAME'] = 'localhost:8082'     
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
        'display_name': 'Keycloak',
        'entity_id': 'http://localhost:8080/realms/example-realm',
        'sso_url': 'http://localhost:8080/realms/example-realm/protocol/saml',
        'slo_url': 'http://localhost:8080/realms/example-realm/protocol/saml',
        'certificate': certificate_from_file('cert2.pem')
    }
}

app.config['SAML2_IDENTITY_PROVIDERS'] = [okta_idp, keycloak_idp]

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

        # Generate login links for each IdP
        login_links = '<p>Login links:</p>'
        for idp in app.config['SAML2_IDENTITY_PROVIDERS']:
            login_url = sp.get_idp_login_url(idp['OPTIONS']['display_name'].lower())
            login_links += f'<p><a href="{login_url}">Log in with {idp["OPTIONS"]["display_name"]}</a></p>'

        return message + login_links

# Blueprint
app.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')

# Print metadata URL
# print(sp.get_metadata_url())

# Run the app
if __name__ == '__main__':
    app.run(port=8082)


# http://localhost:8082/saml/login/idp/?entity_id=http://www.okta.com/exkgkdspz4AU2NF3q4x7&next=http://localhost:8082/



# http://localhost:8082/saml/login/idp/?entity_id=http://localhost:8080/realms/example-realm&next=http://localhost:8082/