from config import *
from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
import mysql.connector
from onnx_transformers import pipeline

@time_it
def getClassified(query):
    res_class = zeroshot_classifier(query, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=False)
    return res_class['labels'][0]

if __name__ == '__main__':
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = Chroma(embedding_function=embeddings, persist_directory = persist_directory)
    hypothesis_template = "The text expresses a {} emotion."
    classes_verbalized = ["sad", "frustrated", "satisfied", "excited", "polite", "impolite", "sympathetic"]
    zeroshot_classifier = pipeline("zero-shot-classification")

    vector_db = vectorstore.get()
    vector_ids = vector_db['ids']
    
    # Connect to the database using read-only user credentials
    cnx = mysql.connector.connect('<SQL CREDS>')
    cursor = cnx.cursor()

    table_list = [
        # ('convo_messages', 'convo_message_id', 'message'),
        # ('tasknote', 'TaskNoteNum', 'Note'),
        ('task', 'TaskNum', 'Descript'),
        # ('text_messages', 'text_message_id', 'message'),
    ]

    for table, id_column, data_column in table_list:
        query = f'SELECT {id_column}, {data_column} FROM {table}'
        cursor.execute(query)
        rows = cursor.fetchall()

        for id_, data in tqdm(rows, desc=f'{table}->{data_column}'):
            cur_id = f'{table}_{id_}'

            if cur_id in vector_ids:
                result = vectorstore.get(cur_id)
                metadata = result['metadatas'][0]
                document = result['documents'][0]
                if not 'classification' in metadata:
                    metadata['classification'] = getClassified(document)
                    vectorstore._collection.update([cur_id], metadatas=[metadata])
            
            elif data is not None:
                vectorstore.add_texts([data], metadatas=[{'table': table, 'id': id_}], ids = [cur_id])

    # Close cursor and connection
    cursor.close()
    cnx.close()