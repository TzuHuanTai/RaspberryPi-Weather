import time
import smbus
from tsl2561 import TSL2561


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
import smbus
from tsl2561 import TSL2561
from lcd1602 import LCD

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

# ===config====
# Station Identity
StationId = 3 

# APIUrl
APIUrl = "http://192.168.1.170/FarmerAPI/api/Realtime/{0}".format(StationId)

# token 已設定raspberry專用權限，但要如何保護此token曝光要再想想！
token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJHZW5lcmFsIiwiaXNzIjoi55CG5p-l5b635LqC5pCe5pyJ6ZmQ5YWs5Y-4IiwiaWQiOiJwaSIsInJvbGVJZCI6IjUiLCJuYmYiOjE1Mjg2ODc3MDEsImV4cCI6MTc0OTYxMjUwMSwiaWF0IjoxNTI4Njg3NzAxfQ.MJWYrbPgG361F4nXwjFdTRdPdGcQ3ff6A6_4TcF24HY'

# ====initial====
bus = smbus.SMBus(1)
tsl = TSL2561(bus)
lcd = LCD(bus)

readLux = 100
lcd.set_backlight(1)
lcd.lcd_display_string("Richard Corp.")
for i in range(3):
    lcd.set_cursor(1, i*4)
    lcd.lcd_display_string("go! ")
    time.sleep(0.5)
lcd.set_backlight(0)

while True:
    try:
        now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        ## ====Read sensor signal save as params====
        # ====DHT22溫濕度計====
        # 接觸不良會讀出None, 讀取pin 4訊號源        
        h, t = dht.read_retry(dht.DHT22, 4)

        # ====TSL25611光度計====
        # Set gain增量係數放大讀取解析度，0=1x(適合光亮), 1=16x(適合昏暗)
        # 若1x測到10，設定16x會測到160絕對值，但16x要是超過65535就None了
        if readLux is None:
            tsl.set_gain(0)
        elif readLux < 1024:
            tsl.set_gain(1)
        else:
            tsl.set_gain(0)
            
        # Set integration time(昏暗適合高量測時間) (0=13.7ms, 1=101ms, 2=402ms)
        # 設越高累加到的數值也越高，超過65535就None了
        if readLux is None:
            tsl.set_integration_time(0)
        elif readLux < 1024:
            tsl.set_integration_time(2)
        elif readLux < 4096:
            tsl.set_integration_time(1)
        else:
            tsl.set_integration_time(0)

        readLux = tsl.read_lux()
        if readLux == None:
            lux = 0
        else:
            lux = readLux
        
        ## write into LCD
        lcd.set_cursor(0, 0)
        lcd.lcd_display_string('Temp:{0:.1f}C Lux: '.format(t))
        lcd.set_cursor(1, 0)
        lcd.lcd_display_string('Humi:{0:.1f}% {1:5.0f}'.format(h, lux))
        
        ## ====Sending http put request and save response as object====
        # header = {'Authorization':token,'Content-Type':'application/json'}
        # detected = weather()
        # detected.StationId = StationId
        # detected.ObsTime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # detected.Temperature = '{0:.1f}'.format(t)
        # detected.RH = '{0:.1f}'.format(h)
        # detected.Lux = lux
        # body = json.dumps(detected.__dict__)              
        # r = requests.put(url = APIUrl, headers = header, data = body) 
        
        ## Show the api rul after adding params
        # r.json()
        # print(r)       
    except:
        lcd.set_cursor(0, 15)
        lcd.lcd_display_string('*')
        
    time.sleep(3)
