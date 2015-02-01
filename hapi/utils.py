import urllib2
class Utils:
      test_internet_url = 'http://74.125.228.100'
      
      @staticmethod
      def has_internet():
          try:
              response=urllib2.urlopen(Utils.test_internet_url, timeout=1)
              return True
          except urllib2.URLError as err: pass
          return False
          