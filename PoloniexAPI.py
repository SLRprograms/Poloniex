import urllib
import urllib2
import json
import time
import hmac
import hashlib

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))


class Poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
        # socket.setdefaulttimeout(30)
    def post_process(self, before):
        after = before
        # Add timestamps if there isnt one but is a datetime
        if ('return' in after):
            if (isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if (isinstance(after['return'][x], dict)):
                        if ('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
        return after

    def api_query(self, command, req={}):
        if (command == "returnTicker" or command == "return24hVolume"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command))
            return json.loads(ret.read())
        elif (command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif (command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])))
            return json.loads(ret.read())
        elif (command == "returnLoanOrders"):
            reqUrl = 'https://poloniex.com/public?command=' + "returnLoanOrders" + '&currency=' + str(req['currency'])
            if (req['limit'] != ''):
                reqUrl += '&limit=' + str(req['limit'])
            ret = urllib2.urlopen(urllib2.Request(reqUrl))
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time() * 1000)
            post_data = urllib.urlencode(req)
            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {'Sign': sign,'Key': self.APIKey}
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi',post_data,headers))#100 was headers
            jsonRet = json.loads(str(ret.read()))
            return self.post_process(jsonRet)

    def returnTicker(self):
        return self.api_query("returnTicker")

    def return24hVolume(self):
        return self.api_query("return24hVolume")

    def returnOrderBook(self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory(self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})

    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        return self.api_query('returnBalances')

    def returnAvailableAccountBalances(self, account):
        return self.api_query('returnAvailableAccountBalances', {"account": account})

    def closeMarginPosition(self, currencyPair):
        return self.api_query('closeMarginPosition', {"currencyPair": currencyPair})    
    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self, currencyPair):
        return self.api_query('returnOpenOrders', {"currencyPair": currencyPair})

    def returnOpenLoanOffers(self):
        return self.api_query('returnOpenLoanOffers')

    def returnActiveLoans(self):
        return self.api_query('returnActiveLoans')

    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self, currencyPair):
        return self.api_query('returnTradeHistory', {"currencyPair": currencyPair})

    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If
    # successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self, currencyPair, rate, amount):
        return self.api_query('buy', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    def marginBuy(self, currencyPair, rate, amount):
        return self.api_query('marginBuy', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    def marginSell(self, currencyPair, rate, amount):
        return self.api_query('marginSell', {"currencyPair": currencyPair, "rate": rate, "amount": amount})
    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If
    # successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self, currencyPair, rate, amount):
        return self.api_query('sell', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    def createLoanOffer(self, currency, amount, duration, autoRenew, lendingRate):
        return self.api_query('createLoanOffer',
                              {"currency": currency, "amount": amount, "duration": duration, "autoRenew": autoRenew,
                               "lendingRate": lendingRate,})

    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self, currencyPair, orderNumber):
        return self.api_query('cancelOrder', {"currencyPair": currencyPair, "orderNumber": orderNumber})

    def cancelLoanOffer(self, currency, orderNumber):
        return self.api_query('cancelLoanOffer', {"currency": currency, "orderNumber": orderNumber})

    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the
    # withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and
    # "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})

    def returnLoanOrders(self, currency, limit=''):
        return self.api_query('returnLoanOrders', {"currency": currency, "limit": limit})

    # Toggles the auto renew setting for the specified orderNumber
    def toggleAutoRenew(self, orderNumber):
        return self.api_query('toggleAutoRenew', {"orderNumber": orderNumber})
