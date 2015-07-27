import tornado.ioloop
import tornado.web
import tornado.httpclient
import sys

PORT = 80


def getForwards():
  f = open('forwards','r')
  for line in f:
    yield line.split()

def note(msg,args):
  print msg % args

class ForwardingRequestHandler (tornado.web.RequestHandler): 
  @tornado.web.asynchronous
  def handle_response(self, response): 
    if response.error and not isinstance(response.error, tornado.httpclient.HTTPError): 
      note("response has error %s", response.error) 
      self.set_status(500) 
      self.write("Internal server error:\n" + str(response.error)) 
      self.finish() 
    else: 
      self.set_status(response.code) 
      for header in ("Date", "Cache-Control", "Server", "Content-Type", "Location"): 
        v = response.headers.get(header) 
        if v: 
          self.set_header(header, v) 
      if response.body: 
        self.write(response.body) 
      self.finish() 

  @tornado.web.asynchronous
  def forward(self, port=None, host=None): 
    try: 
      tornado.httpclient.AsyncHTTPClient().fetch( 
        tornado.httpclient.HTTPRequest( 
          url="%s://%s:%s%s" % (self.request.protocol, host or "localhost", port or 80, self.request.uri), 
          method=self.request.method, 
          body=self.request.body, 
          headers=self.request.headers, 
          follow_redirects=True), 
        self.handle_response) 
    except tornado.httpclient.HTTPError, x: 
      note("tornado signalled HTTPError %s", x) 
      if hasattr(x, response) and x.response: 
        self.handle_response(x.response) 
    except tornado.httpclient.CurlError, x: 
      note("tornado signalled CurlError %s", x) 
      self.set_status(500) 
      self.write("Internal server error:\n" + ''.join(traceback.format_exception(*sys.exc_info()))) 
      self.finish() 
    except: 
      self.set_status(500) 
      self.write("Internal server error:\n" + ''.join(traceback.format_exception(*sys.exc_info()))) 
      self.finish() 


def matchDomain(domain):
  forwards = getForwards()
  for (d,p) in forwards:
    innerDomain = d if PORT == 80 else d + ':%s' % PORT
    if innerDomain == domain:
      return p
  print "Defaulted"
  return 3000

class MainHandler(ForwardingRequestHandler):
  def get(self):
    path = self.request.path
    host = self.request.host
    newPort = matchDomain(host)
    print host, newPort, path
    self.request.body = None
    self.forward(port=newPort)
  def post(self):
    path = self.request.path
    host = self.request.host
    newPort = matchDomain(host)
    print host, newPort, path
    self.forward(port=newPort)
  def put(self):
    path = self.request.path
    host = self.request.host
    newPort = matchDomain(host)
    print host, newPort, path
    self.forward(port=newPort)
  def delete(self):
    path = self.request.path
    host = self.request.host
    newPort = matchDomain(host)
    print host, newPort, path
    self.forward(port=newPort)

application = tornado.web.Application([
  (r".*", MainHandler),
])

if __name__ == "__main__":
  application.listen(PORT)
  tornado.ioloop.IOLoop.current().start()