'''
Created on Aug 13, 2013

@author: ppa
'''
from pyramid.view import view_config
from ultrafinance.module.backTester import BackTester
import time

from threading import Thread
import logging
LOG = logging.getLogger()


class BackTest(object):
    thread = None
    startTime = None
    endTime = None
    latestStates = None
    metrics = None
    hodlings = None

    def __init__(self, request):
        self.request = request
        self.params = request.params
        self.session = request.session
        self.settings = request.registry.settings

    def __startBackTester(self, startTickDate, startTradeDate):
        ''' start googleCrawler '''
        backTester = BackTester(self.settings["ultrafinance.config"], startTickDate, startTradeDate)
        backTester.setup()
        backTester.runTests()
        BackTest.metrics = backTester.getMetrics().values()[0]
        BackTest.latestStates = backTester.getLatestStates()
        BackTest.hodlings = backTester.getHoldings()

        BackTest.endTime = time.asctime()


    ###############################################################################
    # controller functions
    @view_config(route_name='backtest', request_method="POST", renderer='json')
    def PostBackTest(self):
        ''' start crawler '''
        if BackTest.thread and BackTest.thread.is_alive():
            return {"status": "BackTest is running from %s" % BackTest.startTime}
        else:
            startTickDate = 20110825
            startTradeDate = 20130901

            if "startTickDate" in self.request.POST and int(self.request.POST["startTickDate"]) > 0:
                startTickDate = int(self.request.POST["startTickDate"])

            if "startTradeDate" in self.request.POST and int(self.request.POST["startTradeDate"]) > 0:
                startTradeDate = int(self.request.POST["startTradeDate"])

            BackTest.thread = Thread(target = self.__startBackTester, args=[startTickDate, startTradeDate])
            BackTest.startTime = time.asctime()
            BackTest.endTime = None

            BackTest.thread.daemon = False
            BackTest.thread.start()
            return {"status": "BackTest started."}

    @view_config(route_name='backtest', request_method="GET",
                 renderer='ufweb:templates/backtest/getBackTestResult.mako')
    def GetBackTestResult(self):
        ''' get backtest status'''
        return self.__getBackTestJson()

    @view_config(route_name='backtest.json', request_method="GET", renderer='json')
    def GetBackTestJsonResult(self):
        ''' get backtest status'''
        return self.__getBackTestJson()

    def __getBackTestJson(self):
        ''' get backtest json result '''
        ret = {}

        if BackTest.thread is None:
            return ret
        elif BackTest.thread and BackTest.thread.is_alive():
            return {"startDate": BackTest.startTime}
        else:
            return {"startDate": BackTest.startTime,
                    "endDate": BackTest.endTime,
                    "metrics": BackTest.metrics,
                    "latestStates": BackTest.latestStates,
                    "holdings": self.__convertHoldingsToList(BackTest.hodlings[0]) if len(BackTest.hodlings) > 0 else {}}

    def __convertHoldingsToList(self, holding):
        ''' convert holding to dict'''
        ret = []
        for symbol, (share, price) in holding.items():
            if share <= 0:
                continue

            ret.append({"symbol": symbol,
                        "share": int(share),
                        "price": "%.2f" % price})

        return ret

    def __convertOrderToDict(self, date, order):
        ''' convert order to dict '''
        return {"status": order.status,
                "action": order.action,
                "share": int(order.share),
                "symbol": order.symbol,
                "type": order.type,
                "price": "%.2f" % order.price,
                "date": date}