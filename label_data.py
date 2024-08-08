from config import *
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
import mysql.connector

if __name__ == '__main__':
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = Chroma(embedding_function=embeddings, persist_directory = persist_directory)

    add_ids = vectorstore.get()['ids']
    # Connect to the database using read-only user credentials
    cnx = mysql.connector.connect('<SQL CREDS>')
    cursor = cnx.cursor()

    table_list = [
        ('convo_messages', 'convo_message_id', 'message'),
        ('tasknote', 'TaskNoteNum', 'Note'),
        ('task', 'TaskNum', 'Descript'),
        ('text_messages', 'text_message_id', 'message'),
    ]

    for table, id_column, data_column in table_list:
        query = f'SELECT {id_column}, {data_column} FROM {table}'
        cursor.execute(query)
        rows = cursor.fetchall()

        for id_, data in tqdm(rows, desc=f'{table}->{data_column}'):
            cur_id = f'{table}_{id_}'
            
            if data is not None:
                vectorstore.add_texts([data], metadatas=[{'table': table, 'id': id_}], ids = [cur_id])

    # Close cursor and connection
    cursor.close()
    cnx.close()