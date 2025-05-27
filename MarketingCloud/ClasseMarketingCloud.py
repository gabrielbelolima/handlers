# -*- coding: utf-8 -*-
"""
Created on Tue May 20 13:06:11 2025

@author: Gabriel Belo
"""


import requests
import jwt
import json
import uuid  # Make sure this is imported
from datetime import datetime, timedelta

class MarketingCloudAPI:
    def __init__(self, login_params):

        client_id          = login_params['client_id'] 
        client_secret      = login_params['client_secret']
        auth_base_uri      = login_params['auth_base_uri'] 
        soap_base_uri      = login_params['soap_base_uri'] 
        request_base_url   = login_params['request_base_url']
        jwt_signing_secret = login_params['jwt_signing_secret']

        # Configurações de autenticação
        self.client_id = client_id
        self.client_secret = client_secret
        self.jwt_signing_secret = jwt_signing_secret
        self.auth_base_uri = auth_base_uri
        self.rest_base_uri = request_base_url
        
        self.access_token = None
        self.token_expiry = None
        self.rest_instance_url = None

    
    def authenticate(self):
        """Autentica na API usando o endpoint OAuth 2.0 /v2/token"""
        auth_url = f"{self.auth_base_uri}/v2/token"
        
        # Criar JWT para autenticação
        now = datetime.utcnow()
        jwt_payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.auth_base_uri,
            "exp": (now + timedelta(minutes=5)).timestamp()
        }
        
        jwt_token = jwt.encode(
            jwt_payload,
            self.jwt_signing_secret,
            algorithm='HS256'
        )
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "jwt": jwt_token
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(auth_url, json=payload, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.rest_instance_url = token_data['rest_instance_url']
            self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'] - 300)
            
            print("Autenticação OAuth 2.0 bem-sucedida!")
            return True
            
        except requests.exceptions.HTTPError as err:
            print(f"Erro na autenticação: {err}")
            print(f"Resposta completa: {response.text}")
            return False

    
    def make_api_request(self, method, endpoint, data=None, params=None, headers=None, 
                        paginate=False, tqdm=False, max_page = 100):
        """Faz uma requisição para a API REST com suporte a paginação e barra de progresso
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request body data
            params (dict, optional): Query parameters
            headers (dict, optional): Custom headers
            paginate (bool, optional): Se True, realiza paginação automática incrementando $page
            tqdm (bool, optional): Se True, mostra barra de progresso baseada no total de itens
            
        Returns:
            dict or list: Se paginate=True retorna lista com todas as responses concatenadas
                         Se paginate=False retorna a resposta original da API
        """
        if not self.access_token or datetime.now() > self.token_expiry:
            if not self.authenticate():
                raise Exception("Falha na autenticação")
        
        # Use default headers if none provided
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Update with custom headers if provided
        if headers:
            request_headers.update(headers)
        
        url = f"{self.rest_instance_url}{endpoint}"
        all_responses = []
        current_page = 1
        has_more_data = True
        total_items = None
        downloaded_items = 0
        
        # Configuração do tqdm para notebook
        if tqdm and paginate:
            from tqdm.notebook import tqdm
            progress_bar = tqdm(desc="Download progressivo", unit="it")
        
        try:
            while has_more_data:
                # Adiciona/atualiza o parâmetro $page
                if params is None:
                    params = {}
                
                params['$page'] = current_page
                
                # Faz a requisição para a página atual
                response = requests.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                response.raise_for_status()
                
                response_data = response.json()
                
                if not paginate:
                    if tqdm and 'progress_bar' in locals():
                        progress_bar.close()
                    return response_data
                
                # total de itens e configuração da barra
                if total_items is None and 'count' in response_data:
                    total_items = response_data['count']
                    if tqdm:
                        progress_bar.reset(total=total_items)
                        progress_bar.set_description(f"Download ({total_items} itens)")
                
                # Adiciona a resposta à lista completa
                all_responses.append(response_data)
                
                # Atualiza o progresso com base nos itens baixados
                if 'items' in response_data:
                    downloaded_items += len(response_data['items'])
                    if tqdm:
                        progress_bar.update(len(response_data['items']))
                        progress_bar.set_postfix({"página": current_page})
                
                # Verifica se há mais dados
                if 'items' in response_data and len(response_data['items']) > 0:
                    current_page += 1
                else:
                    has_more_data = False
                
                # Limite de segurança (para evitar loops infinitos)
                if (max_page != None):
                    if (current_page > max_page):  # Máximo de 100 páginas
                        if tqdm:
                            progress_bar.set_postfix({"aviso": "⚠️Limite de páginas atingido"})
                        break
            
            # Combina todos os items de todas as respostas
            combined_items = []
            for resp in all_responses:
                if 'items' in resp:
                    combined_items.extend(resp['items'])
            
            # Fecha a barra de progresso se estiver ativada
            if tqdm and 'progress_bar' in locals():
                progress_bar.close()
            
            return {
                'count': len(combined_items),
                'items': combined_items,
                'pages': current_page - 1,
                'all_responses': all_responses
            }
            
        except requests.exceptions.HTTPError as err:
            # Fecha a barra de progresso se estiver ativada
            if tqdm and 'progress_bar' in locals():
                progress_bar.close()
            
            print(f"Erro na requisição API: {err}")
            print(f"Resposta completa: {response.text}")
            if paginate and all_responses:
                combined_items = []
                for resp in all_responses:
                    if 'items' in resp:
                        combined_items.extend(resp['items'])
                return {
                    'count': len(combined_items),
                    'items': combined_items,
                    'pages': current_page - 1,
                    'error': str(err),
                    'partial_data': True
                }
            return None
        except Exception as e:
            if tqdm and 'progress_bar' in locals():
                progress_bar.close()
            raise e
    def endpoints(self):
        if self.authenticate():
            # Teste de conexão - Obter informações da conta
            account_info = self.make_api_request(
                "GET",
                "/platform/v1/endpoints"
                )
        if account_info:
            print("\nInformações da conta:")
            print(json.dumps(account_info, indent=2))

    
    def get_data_extension_by_external_key(self, external_key, fields=None, filter_property=None, filter_value=None, max_page = 100):
        """
        Retrieves data from a Data Extension using its External Key and returns a pandas DataFrame
        
        Args:
            external_key (str): The External Key of the Data Extension (e.g., "12345AA6-7891-123A-A1A1-A2A2AA222AAA")
            fields (list): Optional list of fields/columns to retrieve (None returns all)
            filter_property (str): Optional field name to filter on
            filter_value (str): Optional value to filter by
            
        Returns:
            pd.DataFrame: DataFrame containing all records from the Data Extension
        """
        import pandas as pd
        
        endpoint = f"/data/v1/customobjectdata/key/{external_key}/rowset"
        
        # Build query parameters
        params = {}
        if fields:
            params['$select'] = ",".join(fields)
        if filter_property and filter_value:
            params['$filter'] = f"{filter_property} eq '{filter_value}'"
        
        try:
            # Make API request with pagination and progress bar
            response = self.make_api_request(
                method="GET",
                endpoint=endpoint,
                params=params,
                paginate=True,
                tqdm=True,
                max_page = max_page
            )
            
            if response and 'items' in response:
                # Convert to DataFrame
                df = pd.DataFrame([item['values'] for item in response['items']])
                
                if fields:
                    print(f"Colunas selecionadas: {', '.join(fields)}")
                if filter_property:
                    print(f"Filtro aplicado: {filter_property} = {filter_value}")
                
                return df
            
            return pd.DataFrame()  # Return empty DataFrame if no data
        
        except Exception as e:
            print(f"❌ Erro ao recuperar Data Extension: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
            