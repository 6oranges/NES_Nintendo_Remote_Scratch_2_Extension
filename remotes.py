import socket
from pygame import joystick,event,display,QUIT,quit as close_window
class Remotes:
    def __init__(self):
        display.init()
        s=display.set_mode((300,300))
        display.set_caption("Remotes Server")
        s.fill((255,255,255))
        display.flip()
        self.loadremotes()
    def getinfo(self):
        self.sensors["a"]=len(self.joysticks)
        for joy in range(1,len(self.joysticks)+1):
            self.sensors["b/up/"+str(joy)]="false"
            self.sensors["b/down/"+str(joy)]="false"
            self.sensors["b/left/"+str(joy)]="false"
            self.sensors["b/right/"+str(joy)]="false"
            self.sensors["b/A/"+str(joy)]="false"
            self.sensors["b/B/"+str(joy)]="false"
            self.sensors["b/select/"+str(joy)]="false"
            self.sensors["b/start/"+str(joy)]="false"
            if self.joysticks[joy-1].get_button(0) == 1:
                self.sensors["b/A/"+str(joy)]="true"
            if self.joysticks[joy-1].get_button(1) == 1:
                self.sensors["b/B/"+str(joy)]="true"
            if self.joysticks[joy-1].get_button(9) == 1:
                self.sensors["b/start/"+str(joy)]="true"
            if self.joysticks[joy-1].get_button(8) == 1:
                self.sensors["b/select/"+str(joy)]="true"
            if round(self.joysticks[joy-1].get_axis(0)) == -1:
                self.sensors["b/left/"+str(joy)]="true"
            if round(self.joysticks[joy-1].get_axis(0)) == 1:
                self.sensors["b/right/"+str(joy)]="true"
            if round(self.joysticks[joy-1].get_axis(1)) == -1:
                self.sensors["b/up/"+str(joy)]="true"
            if round(self.joysticks[joy-1].get_axis(1)) == 1:
                self.sensors["b/down/"+str(joy)]="true"
        return self.sensors
    def loadremotes(self):
        joystick.quit()
        joystick.init()
        self.joysticks=[]
        self.sensors={}
        for i in range(joystick.get_count()):
            j=joystick.Joystick(i)
            self.joysticks.append(j)
            self.joysticks[len(self.joysticks)-1].init()
        return self.joysticks
g_REMOTES=Remotes()
PORT = 8081
def sendResponse(message,sock,status="200 OK"):
    crlf = "\r\n"
    httpResponse = "HTTP/1.1 "+status + crlf
    httpResponse += "Content-Type: text/plain; charset=ISO-8859-1" + crlf
    httpResponse += "Access-Control-Allow-Origin: *" + crlf
    httpResponse += crlf
    httpResponse += message
    sock.send(bytes(httpResponse))
def getPath(sock):
    request = sock.recv(65537)
    request=request.decode("utf-8")
    if len(request)>0:
        if "GET" in request:
            path = request.split("\n")[0].split(" ")[1][1::].split("/")
        else:
            path=[]
    else:
        path=[]
    return path
def policyFile():
    return '<cross-domain-policy><allow-access-from domain="*" to-ports="'+str(PORT)+'"/></cross-domain-policy>\n\0'
def main():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveraddr = ('', PORT)
    serversock.bind(serveraddr)
    serversock.listen(5)
    serversock.setblocking(0)
    done = False
    while not done:
        try:
            
            (sock, clientaddr) = serversock.accept()
            sock.setblocking(1)
            path = getPath(sock)
            if len(path)>0:
                if path[0]=="crossdomain.xml":
                    sendResponse(policyFile(),sock)
                elif path[0]=="poll":
                    info=g_REMOTES.getinfo()
                    s=""
                    for key in info:
                        s += key + ' ' + str(info[key]) + "\n"
                    sendResponse(s,sock)
                elif path[0]=="r":
                    g_REMOTES.loadremotes()
                    sendResponse("Successfully reloaded remotes",sock)
                elif path[0]=="reset_all":
                    sendResponse("Successfully reset extension",sock)
                else:
                    sendResponse("Path not found",sock,"404 Not Found")
            else:
                sendResponse("Path not found",sock,"404 Not Found")
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception as e:
            if e.args[0]!=10035:
                print(e)
        for e in event.get():
            if e.type==QUIT:
                done=True
                close_window()
main()
