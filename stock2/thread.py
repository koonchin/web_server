import threading
from .views import *
from function import *

class AddLocationThread(threading.Thread):
    def __init__(self,dep,sku,location):
        self.dep = dep
        self.sku = sku
        self.location = location
        threading.Thread.__init__(self)

    def run(self):
        try:
            web = Web(get_api_register(self.dep, 'apikey'), get_api_register(self.dep, 'apisecret'), get_api_register(self.dep, 'storename'))
            web.add_location(self.dep,self.sku,self.location)
        except Exception as e:
            print(e)