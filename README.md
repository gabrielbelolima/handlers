# Handlers:

Conjunto de classes para manipular bases no ambiente de dados com Python.

- Adicione suas credenciais ao arquivo login_params.txt (por segurança recomendo que esse arquivo seja configurado como variável de ambiente, ou similar!)
- from handlers import * no seu arquivo .py #login_params deve ser importado aqui.
- Cada classe contem um notebook com o tutorial e exemplos de uso.

Nota: Métodos com função de passar queries em linguagens SQL ou análogas sempre estarão no formato Classe.get_query(self, query = """ SELECT ...""").

Exemplo:
sf.get_query(): Permite passar queries SOQL no Salesforce.
rs.get_query(): Permite passar queries SQL no aws redshift.
