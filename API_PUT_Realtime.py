# 20180425 ＠Huan
#   讀取dht22溫濕度計數值，刷新db即時資料
#   為求安全，程式透過API而不直接連結db
#
# 20180602 @Huan
#   增加增加tokenn在request header
#
# 20181030 @Richad
#   Sensor有時後讀不出數值數值,迴圈裡加入例外
##
# 20181124 @Richad
#   加入顯示顯示TSL25611光度計數值光度計數值,之後再加入api
# 20181212 @Richard
#   連結MongoDB
#=====================
import requests             # call apiimport
import json
import Adafruit_DHT as dht  # sensor
import datetime as dt
import time
import sys

import board
import digitalio
import busio            #i2c, spi接口
import adafruit_tsl2561 #光度計

# Declare
class weather:
    def __init__(self):
        self.ObsTime = None
        self.StnPres = None
        self.SeaPres = None
        self.Temperature = None
        self.Td = None
        self.RH = None
        self.WS = None
        self.WD = None
        self.WSGust = None
        self.WDGust = None
        self.Precp = None
        self.PrecpHour = None
        self.SunShine = None
        self.GlobalRad = None
        self.Visb = None
        self.Lux = None

# Station Identity
StationId = 3 

# APIUrl
# APIUrl = "http://192.168.1.170/FarmerAPI/api/values/Realtime/{0}".format(StationId)
APIUrl = "http://192.168.1.170/FarmerAPI/api/Realtime/{0}".format(StationId)

# token 已設定raspberry專用權限，但要如何保護此token曝光要再想想！
token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJHZW5lcmFsIiwiaXNzIjoi55CG5p-l5b635LqC5pCe5pyJ6ZmQ5YWs5Y-4IiwiaWQiOiJwaSIsInJvbGVJZCI6IjUiLCJuYmYiOjE1Mjg2ODc3MDEsImV4cCI6MTc0OTYxMjUwMSwiaWF0IjoxNTI4Njg3NzAxfQ.MJWYrbPgG361F4nXwjFdTRdPdGcQ3ff6A6_4TcF24HY'

## 檢查GPIO接口是否正常
print("start")

pin = digitalio.DigitalInOut(board.D4)
print("digitalio")

i2c = busio.I2C(board.SCL, board.SDA)
print("i2c")

spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("spi")

## initialize TSL25611光度計，解析度0-65535
tsl = adafruit_tsl2561.TSL2561(i2c)
## Set gain增量係數放大讀取解析度，0=1x(適合光亮), 1=16x(適合昏暗)
## 若1x測到10，設定16x會測到160絕對值，但16x要是超過65535就爆了

## Set integration time(昏暗適合高量測時間) (0=13.7ms, 1=101ms, 2=402ms, or 3=manual)
## 設越高累加到的數值也越高，超過65535就爆了
tsl.integration_time = 1

while True:
    try:
        ## Read sensor signal save as params
        ## 接觸不良會讀出None, 讀取pin 4訊號源
        ## ====DHT22溫濕度計====
        h, t = dht.read_retry(dht.DHT22, 4)        
        api_t = '{:.1f}'.format(t)
        api_h = '{:.1f}'.format(h)
        now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print ('----------------------------------------------')
        print (now)
        print ('Temp={0:0.1f}*C \nHumidity={1:0.1f}%'.format(t, h))

        ## ====TSL25611光度計====        
        # Enable the light sensor
        tsl.enabled = True
        tsl.gain = 0
        tsl.integration_time = 0

        ## Get raw (luminosity) readings individually 直接偵測到的數值
        broadband = tsl.broadband # visible plus infrared(全光譜）
        infrared = tsl.infrared   # 紅外線

        ## Get raw (luminosity) readings using tuple unpacking
        # broadband, infrared = tsl.luminosity

        ## Get computed lux value 根據設定計算出的lux值
        if tsl.lux == None:
            lux = 0
        else:
            lux = '{:.1f}'.format(tsl.lux)
            
        ## ====Print results====
        # print("Enabled = {}
        # print("Gain = {}".format(tsl.gain))
        # print("Integration time = {}".format(tsl.integration_time))
        # print("Broadband = {}".format(broadband))
        # print("Infrared = {}".format(infrared))
        print("Lux = {}\n".format(lux))

        ## ====Disble the light sensor (to save power)====
        # tsl.enabled = False
        
        ## ====Sending http put request and save response as object====
        header = {'Authorization':token,'Content-Type':'application/json'}
        payload = {'RecTemp':api_t, 'RecRH':api_h}
        detected = weather()
        detected.StationId = StationId
        detected.ObsTime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        detected.Temperature = api_t
        detected.RH = api_h
        detected.Lux = lux
        body = json.dumps(detected.__dict__)              
        r = requests.put(url = APIUrl, headers = header, data = body) 
        
        ## Show the api rul after adding params
        # r.json()
        # print(r)
        
    except:
        now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print (now)
        print("error: ", sys.exc_info()[0], "\n")
        
    time.sleep(15)
