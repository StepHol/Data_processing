import os
import smtplib
import logging
import configparser
import socket
import numpy as np
import pandas as pd
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

\
def main() -> None:

    file_name = '223344.xlsx'
    email = 'stepanholub@seznam.cz'

    my_data = DataProcessing(file_name)
    
    DataProcessing.log_statistics(my_data)
    DataProcessing.send_to_email(my_data, email)

    # print(DataProcessing.table_statistics(my_data))
    # print(DataProcessing.column_statistics(my_data))

class DataProcessing:
    '''
    A dataprocessing class for data analysis. Imports excel file. Saves data 
    to CSV file.

    Attributes:
    -----------
    file_name: str
        The name of file in xlsx format.
    path: str
        The path to the file. This file directory is set as default.

    Methods:
    --------
    table_statistics()
        Returns number of columns and number of records as sting.

    column_statistics()
        Returns DataFrame with statistics for each column:
        Unique values, Null values, Average, Min, Max  

    log_statistics()
        Runs table and column statistics and save result to the log file.

    send_to_email(receiver)
        Sends imported excel file in the attachment to the receiver.
        Uses 'config.ini' file for server and user configuration.
    '''
    
    def __init__(self, file_name, path=os.path.dirname(__file__)):
        self.path = path
        self.file_name = file_name
        self.full_path = os.path.join(self.path, self.file_name)
        self.df = self.df_decimal_sep(pd.read_excel(self.full_path))
        self.df_num = self.numeric_columns(self.df)
        self.save_to_csv(self.df, self.file_name)


    @staticmethod
    def df_decimal_sep(data_frame: pd.DataFrame) -> pd.DataFrame:
        '''
        Converts columns of DataFrame using ',' 
        as a decimal separator to float data type.
        '''
        data_frame = data_frame.replace(',','.', regex=True)
        for column in list(data_frame):
            try:
                data_frame[column] = data_frame[column].astype(float)
            except:
                pass
        return data_frame


    @staticmethod
    def numeric_columns(data_frame: pd.DataFrame) -> pd.DataFrame:
        '''Select numeric columns from DataFrame'''
        return data_frame[
            list(data_frame.dropna(how='all').select_dtypes(include=np.number))
            ]

    @staticmethod
    def save_to_csv(data_frame: pd.DataFrame, full_filename: str):
        '''Saves DataFrame to CSV file.'''
        data_frame.to_csv(
            f"{str(full_filename).split('.')[0]}.csv",
            index=False, encoding='utf-8'
        )
        print('Saved to CSV file.')


    def count_records(self) -> int:
        return len(self.df.index)


    def count_columns(self) -> int:
        return len(self.df.columns)


    def unique_values(self) -> pd.DataFrame:
        return self.df.nunique().to_frame('Unique values')


    def null_values(self) -> pd.DataFrame:
        return self.df.isna().sum().to_frame('Null values')


    def mean(self) -> pd.DataFrame:
        return self.df_num.mean().round(1).to_frame('Average')


    def min(self) -> pd.DataFrame:
        return self.df_num.min().to_frame('Min')


    def max(self) -> pd.DataFrame:
        return self.df_num.max().to_frame('Max')


    def table_statistics(self) -> str:
        '''Returns number of columns and number of records'''
        statistics = (
            f'\nNumber of records: {self.count_records()}'
            f'\nNumber of columns: {self.count_columns()}'
        )
        return statistics


    def column_statistics(self) -> pd.DataFrame:
        '''
        Returns DataFrame with statistics for each column:
        Unique values, Null values, Average, Min, Max
        '''
        frames = [
            self.unique_values().astype(str).transpose(),
            self.null_values().astype(str).transpose(),
            self.mean().transpose(),
            self.min().transpose(),
            self.max().transpose()
        ]
        return pd.concat(frames).fillna('-')


    def log_statistics(self) -> None:
        '''Run table and column statistics and save result to the log file. '''
        column_statistics = self.column_statistics()
        table_statistics = self.table_statistics()
        file_no_ext = self.file_name.split('.')[0] #File name without extension
        
        logging.basicConfig(
            level=logging.INFO,
            filename = f'{file_no_ext}_statistics.log',
            filemode='a',
            encoding='UTF-8',
            format='%(asctime)s %(message)s',  datefmt='%d-%b-%y %H:%M:%S'
        )

        separator = '=' * 150

        logging.info(
            
            f'\n\nTABLE STATISTICS:'
            f'\n{table_statistics}'
            f'\n\nCOLUMN STATISTICS:'
            f'\n\n{column_statistics}\n{separator}'
        )
        print('Statistics saved to log.')


    def send_to_email(self, receiver) -> None:
        '''Sends imported excel file in the attachment to the receiver.
        Uses 'config.ini' file for server and user configuration.'''

        def read_configuratin(cofig_file):
            cofig_file = configparser.ConfigParser()
            cofig_file.read('config.ini')
            login = cofig_file['LOGIN']
            server = cofig_file['SERVER']
            return login, server


        def create_message(login):
            message = MIMEMultipart()
            message['Subject'] = f'{self.file_name}'
            message['From'] = login['user']
            message['To'] = receiver
            body = f'Sending {self.file_name} in the attachment.'
            message.attach(MIMEText(body, "plain"))
            return message


        def add_attachment(message: MIMEMultipart, file):
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(file, 'rb').read())

            encoders.encode_base64(part)
            message.attach(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {self.file_name}",
                )
            return message


        def send_email(login, server, message):
            try:
                server = smtplib.SMTP_SSL(server['smtp_server'], server['port'])
            except socket.error:
                output = 'Connection to server failed.'
            else:
                server.login(login['user'], login['password'])
                server.sendmail(login['user'], receiver, message.as_string())
                server.quit()
                output = f'File {self.file_name} sent to {receiver}.'
            finally:
                print(output)


        login, server = read_configuratin('config.ini')
        msg = create_message(login)
        full_msg = add_attachment(msg, self.file_name)
        send_email(login, server, full_msg)


if __name__ == "__main__":
    main()