import urllib.request
import json
from datetime import date
import matplotlib.pyplot as plt
import http.server
import socketserver
PORT = 3011

def parseExpenseRevenue(jsonInput,currencyKey):
 datetoday = date.today()
 a = []
 for jsonItem in jsonInput:
  itemDate = date(int(jsonItem['date'][0:4]),
                     int(jsonItem['date'][5:7]),
                     int(jsonItem['date'][8:10]))
  age = datetoday - itemDate
  intage = int(age.total_seconds()/60/60/24)
  a.append((intage,int(jsonItem[currencyKey])))
 return a

def plotExpenseRevenue(path):
 expenses = urllib.request.urlopen("http://expensecity-env.dfhpkbxgyn.us-east-2.elasticbeanstalk.com/" + path).read()
 revenues = urllib.request.urlopen("http://revenue-env.fbxttwvwiv.us-east-2.elasticbeanstalk.com/revenue/" + path).read()
 expenses = json.loads(expenses)
 revenues = json.loads(revenues)
 expenses = parseExpenseRevenue(expenses,'amount')
 revenues = parseExpenseRevenue(revenues,'cost')
 c = []
 sum = 0
 for i in range(730):
  for expense in filter(lambda e: 730-e[0] == i, expenses):
   sum -= expense[1]
  for revenue in filter(lambda e: 730-e[0] == i, revenues):
   sum += revenue[1]
  c.append(sum)
 return c

class PlotHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  path = self.path
  plotExpenseRevenue(path[1:])
  self.send_response(200)
  self.send_header("Content-type", "image/png")
  self.end_headers()
  plt.plot(plotExpenseRevenue(self.path))
  plt.xticks([0,365,730],('June 2017','June 2018','June 2019'))
  plt.title(self.path[1:])
  plt.savefig(self.wfile)
  plt.close()

try:
 server = http.server.HTTPServer(('localhost', PORT), PlotHTTPRequestHandler)
 print('Started HTTP Server on ' + str(PORT))
 server.serve_forever()
except KeyboardInterrupt:
 print('^C keyboard interrupt. shutting down')
 server.socket.close()
