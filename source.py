# access mysql
import os
from pathlib import Path
hostdb = '139.177.190.161'

passworddb = 'Chino002'

databasedb = 'image'

userdb = 'gink'

host = '127.0.0.1:8000'

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_DIR = os.path.join(BASE_DIR,'app')
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

