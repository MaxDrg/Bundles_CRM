import psycopg2
import paramiko
import os

class CRM: 
    def __init__(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            os.environ.get('HOST'), 
            os.environ.get('PORT'), 
            username=os.environ.get('USER'), 
            password=os.environ.get('PASS')
        )
        print("A connection to the server has been established")
        self.conn = psycopg2.connect(
        database = os.environ.get('CRM_DATABASE'),
        user = os.environ.get('CRM_DATA_USER'),
        password = os.environ.get('CRM_DATA_PASS'),
        host = os.environ.get('HOST'),
        port = os.environ.get('DATA_PORT')
        )
        print ("Database connection established")
    
    async def get_crm_apps(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT id, app_id FROM crm_apps""")
            return cursor.fetchall()

    async def delete_app_history(self, app_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("""DELETE FROM crm_history WHERE app_id = %s;""", (app_id ,))
            self.conn.commit()

    async def delete_crm_app(self, id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("""DELETE FROM crm_apps WHERE id = %s;""", (id ,))
            self.conn.commit()

class Bot_apps: 
    def __init__(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                os.environ.get('HOST'), 
                os.environ.get('PORT'), 
                username=os.environ.get('USER'), 
                password=os.environ.get('PASS')
            )
            print("A connection to the server has been established")
            self.conn = psycopg2.connect(
            database = os.environ.get('DATABASE'),
            user = os.environ.get('DATA_USER'),
            password = os.environ.get('DATA_PASS'),
            host = os.environ.get('HOST'),
            port = os.environ.get('DATA_PORT')
            )
            print ("Database connection established")
        except Exception as err:
            print(str(err))

    async def check_app(self, app_id: str):
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT EXISTS(SELECT id FROM apps_apps WHERE app_name = %s);""", (app_id, ))
            return cursor.fetchone()[0]