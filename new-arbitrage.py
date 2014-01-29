import pickle
from BeautifulSoup import BeautifulSoup
import urllib2
import btceapi
import time

fee = 0.002

class graph:
    def __init__(self):
        self.paths=dict()
        self.graph=dict()
        self.get_CT_rates()
        self.get_BTCe_rates()

    def get_CT_rates(self):
        self.add_node('CTbtc',{'CTltc':(1 / get_CT_ask('ltc','btc') * (1-fee)),
                            'CTusd':get_CT_bid('btc','usd') * (1-fee),
                            'CTeur':get_CT_bid('btc','eur') * (1-fee),
                            'CTwdc':(1 / get_CT_ask('wdc','btc') * (1-fee)),
                            'BTCebtc':1-fee})
        self.add_node('CTltc',{'CTbtc':(get_CT_bid('ltc','btc') * (1-fee)),
                            'CTusd':get_CT_bid('ltc','usd') * (1-fee),
                            'CTeur':get_CT_bid('ltc','eur') * (1-fee),
                            'BTCeltc':1-fee})
        self.add_node('CTwdc',{'CTbtc':(get_CT_bid('wdc','btc') * (1-fee)),
                            'CTusd':get_CT_bid('wdc','usd') * (1-fee)})
        self.add_node('CTusd',{'CTbtc':1/get_CT_ask('btc','usd') * (1-fee),
                             'CTltc':1/get_CT_ask('ltc','usd') * (1-fee),
                            'CTwdc':1/get_CT_ask('wdc','usd') * (1-fee)})
        self.add_node('CTeur',{'CTbtc':1/get_CT_ask('btc','eur') * (1-fee),
                             'CTltc':1/get_CT_ask('ltc','eur') * (1-fee)})   

    def get_BTCe_rates(self):                             
        ltc_btc = get_pair('ltc','btc')
        btc_usd = get_pair('btc','usd')
        btc_eur = get_pair('btc','eur')
        ltc_usd = get_pair('ltc','usd')
        ltc_eur = get_pair('ltc','eur')
        eur_usd = get_pair('eur','usd')
        self.add_node('BTCebtc',{'BTCeltc':(1 / ltc_btc.buy * (1-fee)),
                            'BTCeusd':btc_usd.sell * (1-fee),
                            'BTCeeur':btc_eur.sell * (1-fee),
                            'CTbtc':1-fee})
        self.add_node('BTCeltc',{'BTCebtc':(ltc_btc.sell * (1-fee)),
                            'BTCeusd':ltc_usd.sell * (1-fee),
                            'BTCeeur':ltc_eur.sell * (1-fee),
                            'CTltc':1-fee})
        self.add_node('BTCeusd',{'BTCebtc':(1/btc_usd.buy * (1-fee)),
                            'BTCeltc':1/ltc_usd.buy * (1-fee),
                            'BTCeeur':1/eur_usd.buy* (1-fee)})
        self.add_node('BTCeeur',{'BTCebtc':(1/btc_eur.buy * (1-fee)),
                            'BTCeltc':1/ltc_eur.buy * (1-fee),
                            'BTCeusd':eur_usd.sell* (1-fee)})           
                            
                            
    def add_node(self,name,edges):
        self.graph[name]=node(name,edges)
    def add_path(self,p,l,d):
        self.paths[p]=path(p,l,d)
    def find_all_paths(self, realStart,start, end, steps=0, value=1, path=[]):
        path = path + [start]
        if start == end and len(path)>1:  #   if we are done
            return ([path],[value])
        if not self.graph.has_key(start):    #   if it's not in graph
            return []
        paths = []
        totVals = []        
        for curNode in self.graph[start].neighbors:  #   go through neighbors
            if curNode not in path or curNode == realStart:                 #   If haven't passed through this node yet   
                print 'Going from %s to %s with a distance of %s' % (start,curNode,self.graph[start].edges[curNode])
                (newpaths,newvalue) = self.find_all_paths(realStart,curNode, end, steps=steps+1,value=value*self.graph[start].edges[curNode],path=path)    
                for newpath in newpaths:
                    paths.append(newpath)
                for totVal in newvalue:
                    totVals.append(totVal)
        return (paths,totVals)

    def calcPaths(self,realStart,start,end):
        (paths,dists) = self.find_all_paths(realStart,start,end)
        str_paths = [''.join(p) for p in paths]
        for i in range(len(paths)):
            self.add_path(str_paths[i],len(paths[i]),dists[i])

class node:
    def __init__(self,name='A',edges={'B':1.5,'C':.5}):
        self.name=name
        self.edges=edges
        self.neighbors=edges.keys()
        self.dists=[edges[x] for x in edges.keys()]
        
class path:
    def __init__(self,path,length,distance):
        self.path=path
        self.length = length
        self.distance = distance

def get_CT_ask(coin1='wdc',coin2='btc'):
    link = 'https://crypto-trade.com/api/1/ticker/'+coin1+'_'+coin2
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)
    pretty = soup.prettify().strip().split('{')[2].replace('}','').replace("\"",'').split(',')
    for line in pretty:
        pair = line.split(':')
        if pair[0] == 'min_ask':
            price = float(pair[1])
    return float(price)        
    
def get_CT_bid(coin1='wdc',coin2='btc'):
    link = 'https://crypto-trade.com/api/1/ticker/'+coin1+'_'+coin2
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)
    pretty = soup.prettify().strip().split('{')[2].replace('}','').replace("\"",'').split(',')
    for line in pretty:
        pair = line.split(':')
        if pair[0] == 'max_bid':
            price = float(pair[1])
    return float(price)
class BTCePair:
    def __init__(self,buy,sell):
        self.buy = buy
        self.sell = sell
           
def get_pair(curr1='btc',curr2='usd'):
    connection = btceapi.BTCEConnection()
    ticker = btceapi.getTicker(curr1+'_'+curr2, connection)

    return BTCePair(float(ticker.buy),float(ticker.sell))
                
    
y=graph()    
y.calcPaths('BTCebtc','BTCebtc','CTbtc')
z = [(x,y.paths[x].distance) for x in y.paths.keys()]
dists = [d[1] for d in z]
maxReturn = [pair for pair in z if pair[1] == max(dists)]
