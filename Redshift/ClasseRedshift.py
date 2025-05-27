# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:23:10 2025

@author: Gabriel Belo
"""


import psycopg2
import pandas as pd

class Redshift:
    def __init__(self, login_params):

        # Configurações de conexão ao Redshift
        self.dbname   = login_params['dbname']
        self.host     = login_params['host']
        self.port     = login_params['port']
        self.user     = login_params['user']
        self.password = login_params['password']

    def get_query(self, query):         
        # Conexão com o banco de dados Redshift usando psycopg2
        conn = psycopg2.connect(
                            dbname=self.dbname,
                            host=self.host,
                            port=self.port,
                            user=self.user,
                            password=self.password
                                )
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data
    
    '''
    def list_bases(self):
        # Conexão com o banco de dados Redshift usando psycopg2
        query = "SELECT datname FROM pg_database"
        df_schemas = self.get_query(query)
            
        return df_schemas
    '''
        
    def get_table_list(self):
        query_tb2 = """
            SELECT 
            redshift_database_name as database,
            schemaname as schema,
            tablename as table
            FROM SVV_EXTERNAL_TABLES
                    """
        return self.get_query(query_tb2)
    
    
    def list_schemas(self):
     
        # Lista schemas disponíveis (implementar método)
        query_tb1 = "SELECT  * FROM pg_catalog.pg_namespace WHERE nspacl is not null AND nspowner > 1 OR nspname = 'public';"
        df_schemas = self.get_query(query_tb1)
        df_schemas = df_schemas[(df_schemas['nspacl'].str.contains(f'{self.user}'))|(df_schemas['nspname']=='public')][['nspname']].rename(columns={'nspname':'schema'})
        
        # Lista tabelas disponíveis 
        query_tb2 = """SELECT 
            redshift_database_name as database,
            schemaname as schema,
            tablename as table
        FROM SVV_EXTERNAL_TABLES
        """
        df_schema2 = self.get_query(query_tb2)
        df_schema2 = df_schema2.groupby('schema', as_index = False)['table'].count()
        df_schema3 = df_schemas.merge(df_schema2, how = 'left', on = 'schema').fillna(0)
        df_schema3['table'] = df_schema3['table'].astype(int)
        
        return df_schema3
    
    def list_tables(self, schema = None):
        
        df = self.get_table_list()
        if schema != None:
            df[df['schema'] == 'schema']
        
        df = df[['table']].groupby('table', as_index = False).count()
        return df