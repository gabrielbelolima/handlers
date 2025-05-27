# Handlers:  

A set of classes for managing databases in a Python data environment.  

- Add your credentials to the `login_params.txt` file (for security, it's recommended to configure this file as an environment variable or similar!).  
- Use `from handlers import *` in your `.py` file.  

**Note:** Methods designed to execute queries in SQL or similar languages will always follow the format `Classe.get_query(self, query=""" SELECT ...""")`.  

### Example:  
- `sf.get_query()`: Allows running SOQL queries in Salesforce.  
- `rs.get_query()`: Allows running SQL queries in AWS Redshift.