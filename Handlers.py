# Replace this for Env-Secret!!!
from login_params import login_params

# Loads Classes:
from Hotmart.ClasseHotmart import *
from MarketingCloud.ClasseMarketingCloud import *
from Redshift.ClasseRedshift import *
from Salesforce.ClasseSalesforce import *

# instantiates Classes:
hm = HotMart(login_params = login_params['hm'])
mc = MarketingCloudAPI(login_params = login_params['mc'])
rs = Redshift(login_params = login_params['rs'])
sf = SalesForce(login_params = login_params['sf'])
