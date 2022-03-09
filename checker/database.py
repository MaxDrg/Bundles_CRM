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
        port = os.environ.get('CRM_DATA_PORT')
        )
        print ("Database connection established")

    async def get_devs(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT dev FROM crm_developers;""")
            return cursor.fetchall()

    async def get_last_app(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT date_time FROM crm_history ORDER BY id DESC LIMIT 1;""")
            return cursor.fetchone()

    async def get_apps(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""SELECT id, app_id, installs FROM crm_apps WHERE not last_update = 'Не существует';""")
            return cursor.fetchall()

    async def update_app(self, id, installs, status, last_update):
        with self.conn.cursor() as cursor:
            cursor.execute("""UPDATE crm_apps SET installs = %s, status = %s, last_update = %s WHERE id = %s;""", (installs, status, last_update, id, ))
            self.conn.commit()

    async def add_history(self, installs, app_database_id, time):
        with self.conn.cursor() as cursor:
            cursor.execute("""INSERT INTO crm_history (date_time, installs, app_id) VALUES (%s, %s, %s);""", (time, installs, app_database_id, ))
            self.conn.commit()