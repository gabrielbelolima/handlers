login_params = {
    # Salesforce
    'sf' : {
        'securityToken' : 'xxx',
        'email' :         'xxxxxx@xxx.xxx',
        'password' :      'xxx',
        'domain.my':      'xxx.my'
    },
    
    # Hotmart
    'hm' : {
        'Authorization': 'Basic xxx',
        'client_id' :    'xxx',
        'client_secret' :'xxx'
    },
    
    # RedShift
    'rs' : { 
        'user': 'xxx',
        'password': 'xxx',
        'dbname':"xxx",
        'host':"xxx.xxx.us-east-1.redshift-serverless.amazonaws.com",
        'port':"5439"
    },
    
    # MarketingCloud
    'mc' : {
        'package_id': 'xxx', #client_id
        'client_id': 'xxx',
        'client_secret':'xxx',
        'auth_base_uri':r'https://xxx.auth.marketingcloudapis.com/',
        'soap_base_uri':r'https://xxx.soap.marketingcloudapis.com/',
        'jwt_signing_secret':'xxxxxx',
        'request_base_url': r'https://xxx.rest.marketingcloudapis.com/'
    },
    
    'GDriveLoader' : {
    'credentials_path': r".\xxx.apps.googleusercontent.com.json"
    }
}