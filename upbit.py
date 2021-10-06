import sys
import pyupbit
import pandas as pd
import time
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    emailPassword = sys.argv[1]
except:
    print("Email 패스워드를 입력해주십시오.")
    quit()

time.sleep(25)

pd.set_option('display.max_rows', None)
openPrice = []  
closePrice = []
riseFallRate = []
cleanNameCoins = []

coins = pyupbit.get_tickers(fiat="KRW")

def makePriceClean(price) :
    if(price >= 100) : 
        price = format(int(price), ",")
    else :
        price = "%.2f" % price
    return price

def getRiseFallRate(openPrice, closePrice) :
    return "%.2f" % float((closePrice-openPrice)/openPrice * 100)

for coin in coins :
    priceData = pyupbit.get_ohlcv(coin , count=1, interval="minute10")
    cleanNameCoins.append(coin.replace("KRW-", ""))

    time.sleep(0.08)

    priceInfo = priceData.values.tolist()[0]
    closePrice.append(makePriceClean(priceInfo[3]))

    riseFallRate.append(getRiseFallRate(priceInfo[0], priceInfo[3]))

df = pd.DataFrame({"이름" : cleanNameCoins, "현재가" : closePrice, "하락률" : riseFallRate})
df = df.astype({"하락률" : "float"})

df = df[(df["이름"]== "BTC") | (df["하락률"] < -5)]

if len(df) > 1 :
    from_addr = formataddr(('Ming', 'aeneascon@google.com'))

    session = None
    try:
        # SMTP 세션 생성
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.set_debuglevel(True)
        
        # SMTP 계정 인증 설정
        session.ehlo()
        session.starttls()
        session.login('aeneascon@gmail.com', emailPassword)
    
        # 메일 콘텐츠 설정
        message = MIMEMultipart("alternative")
        
        # 메일 송/수신 옵션 설정
        message.set_charset('utf-8')
        message['From'] = from_addr
        message['Subject'] = '속보) 코인 하락 알림'
        
        df_html = df.to_html(index=False)
        df_html = df_html.replace('<tr>', '<tr style="text-align:center">')
        df_html = df_html.replace('<th>', '<th style="padding:5px 30px">')
        df_html = df_html.replace('<td>', '<td style="padding:5px 30px">')

        # 메일 콘텐츠 - 내락
        bodyPart = MIMEText(df_html, 'html', 'utf-8')
        message.attach( bodyPart )
    
        # 메일 발송
        session.sendmail(from_addr, "aeneascon@naver.com", message.as_string())            
        session.sendmail(from_addr, "jihwan8d@gmail.com", message.as_string())    
        session.sendmail(from_addr, "seodh4@gmail.com", message.as_string())    
    
        print( 'Successfully sent the mail!!!' )
    except Exception as e:
        print( 'error')
        print(e)
    finally:
        if session is not None:
            session.quit()
