import os
import sshtunnel
from dotenv import load_dotenv

DEV = False

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

sshtunnel.SSH_TIMEOUT = 20.0
sshtunnel.TUNNEL_TIMEOUT = 20.0


class PA_Settings:
    USERNAME = 'kade'
    PASSWORD = ''
    DB_PASSWORD = ''
    HOST_NAME = 'kade.mysql.pythonanywhere-services.com'
    DATABASE = 'kade$chronos'

    SSH_HOSTNAME = 'ssh.pythonanywhere.com'


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'OTHER_SECRET'

    if not DEV:
        SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://{username}:{password}@{hostname}/{databasename}".format(
            username=PA_Settings.USERNAME,
            password=PA_Settings.DB_PASSWORD,
            hostname=PA_Settings.HOST_NAME,
            databasename=PA_Settings.DATABASE,
        )
    else:
        forwarding_server = sshtunnel.SSHTunnelForwarder(
            'ssh.pythonanywhere.com',
            ssh_username=PA_Settings.USERNAME,
            ssh_password=PA_Settings.PASSWORD,
            remote_bind_address=('kade.mysql.pythonanywhere-services.com', 3306)
        )

        forwarding_server.start()
        local_port = forwarding_server.local_bind_port
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@127.0.0.1:{local_port}/{databasename}".format(
            username=PA_Settings.USERNAME,
            password=PA_Settings.DB_PASSWORD,
            hostname=PA_Settings.HOST_NAME,
            local_port=local_port,
            databasename=PA_Settings.DATABASE
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
