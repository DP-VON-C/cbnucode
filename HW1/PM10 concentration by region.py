import urllib.request
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt

import ssl # url 에러 해결
ssl._create_default_https_context = ssl._create_unverified_context

# servicekey 지움
url='https://apis.data.go.kr/B552584/ArpltnStatsSvc/getCtprvnMesureLIst?serviceKey=&returnType=json&numOfRows=500&pageNo=1&itemCode=PM10&dataGubun=daily&searchCondition=MONTH'

# api 호출
response = urllib.request.urlopen(url)
response_message = response.read().decode('utf-8')
now = datetime.now()

# 사용자로부터 날짜 입력받기
while True:
    date_str = input("날짜를 입력하세요 (YYYY-MM-DD 형식): ")

    try:
        # 날짜 형식 검증
        now_t = now.strftime('%Y-%m-%d')
        date_input = datetime.strptime(date_str, '%Y-%m-%d')
        if date_input > now:
            print("과거 날짜를 입력해주세요.")
            continue
        break  # 날짜 형식이 맞으면 루프 종료
    except ValueError:
        print("잘못된 날짜 형식입니다. 다시 입력하세요.")

# 일수 차이 계산
diff = now - date_input

# api의 url에서 json 데이터 가져오기
data = json.loads(response_message)

item2 = data["response"]["body"]["items"]

# JSON 데이터에서 불필요한 부분 제거
data_dict = item2[diff.days-1]
data_dict.pop('dataTime', None)
data_dict.pop('dataGubun', None)
data_dict.pop('itemCode', None)

# 데이터를 DataFrame으로 변환
df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['PM10'])
df.index.name = 'Region'  # 인덱스 이름 설정
df = df.fillna(0) # NaN 값을 0으로 대체
df = df.reset_index() # 'Region' 열(column)을 데이터프레임의 열(column)로 설정
df = df.rename(columns={'index': 'Region'}) # 열(column) 이름 변경

# PM10 칼럼을 정수형으로 변환하고 내림차순 정렬
df['PM10'] = df['PM10'].astype(int)
df = df.sort_values(by=['PM10'], ascending=False)

# 지역 이름을 abc 순서로 정렬
df = df.sort_values(by='Region')
df = df.reset_index(drop=True)

# 그래프 시각화
plt.bar(df['Region'], df['PM10'], color='grey')
plt.xlabel('Region')
plt.ylabel('PM10')
plt.ylim(0)
plt.title('PM10 concentration by region (' + date_str + ')')
plt.xticks(rotation=90)
plt.show()
