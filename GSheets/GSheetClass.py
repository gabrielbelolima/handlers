# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:06:05 2025

@author: Gabriel Belo
"""

import io
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread
from gspread_dataframe import set_with_dataframe

class GSheet:
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize connection to Google Drive and Sheets.
        
        Args:
            credentials_file: Path to Google Service Account JSON credentials
        """
        # Set up authentication with broader scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        
        # Initialize both clients
        self.gspread_client = gspread.authorize(creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        
    def get(self, file_link_or_id: str, sheet_name: str = 'Sheet1', excel: bool = False) -> pd.DataFrame:
        """
        Get data from either Google Sheet or Excel file in Drive.
        
        Args:
            file_link_or_id: Either the Sheet/Excel ID or full URL
            sheet_name: Worksheet name (for Google Sheets) or sheet name (for Excel)
            excel: If True, reads as Excel file; if False, reads as Google Sheet
        """
        # Extract file ID from URL if needed
        file_id = self._extract_file_id(file_link_or_id)
        
        if excel:
            return self._get_excel(file_id, sheet_name)
        else:
            return self._get_gsheet(file_id, sheet_name)
    
    def _extract_file_id(self, url_or_id: str) -> str:
        """Extract file ID from URL or return as-is if already an ID"""
        if 'docs.google.com' in url_or_id:
            if '/spreadsheets/' in url_or_id:
                return url_or_id.split('/')[5]
            elif '/file/d/' in url_or_id:  # For direct file links
                return url_or_id.split('/')[5]
        return url_or_id
    
    def _get_gsheet(self, sheet_id: str, sheet_name: str) -> pd.DataFrame:
        """Get data from Google Sheet"""
        try:
            sheet = self.gspread_client.open_by_key(sheet_id)
            worksheet = sheet.worksheet(sheet_name)
            return pd.DataFrame(worksheet.get_all_records())
        except Exception as e:
            raise Exception(f"Failed to get Google Sheet data: {str(e)}")
    
    def _get_excel(self, file_id: str, sheet_name: str) -> pd.DataFrame:
        """Get data from Excel file in Drive"""
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            
            while True:
                status, done = downloader.next_chunk()
                if done:
                    break
            
            file.seek(0)
            return pd.read_excel(file, sheet_name=sheet_name)
        except Exception as e:
            raise Exception(f"Failed to read Excel file: {str(e)}")

    def clear(self, sheet_name: str = 'Sheet1') -> None:
        """Clear all content from specified worksheet"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            worksheet.clear()
        except Exception as e:
            raise Exception(f"Failed to clear sheet '{sheet_name}'. Error: {str(e)}")

    def load(self, sheet_name: str = 'Sheet1', data: pd.DataFrame = pd.DataFrame()) -> None:
        """
        Load DataFrame into specified worksheet (overwrites existing content)
        
        Args:
            sheet_name: Worksheet to write to
            data: DataFrame to write (empty DF will create blank sheet)
        """
        try:
            # Create sheet if it doesn't exist
            try:
                worksheet = self.sheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.sheet.add_worksheet(title=sheet_name, rows=100, cols=20)
            
            # Clear existing data and write new data
            worksheet.clear()
            if not data.empty:
                set_with_dataframe(worksheet, data)
        except Exception as e:
            raise Exception(f"Failed to load data to sheet '{sheet_name}'. Error: {str(e)}")