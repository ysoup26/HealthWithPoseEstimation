import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

body_part_names = {
    "leg":0,
    "knee":1,
    "arm":2,
    "waist":3,
    "elbow":4
}

#유사한 유저를 이용하여 운동 영상 제목을 반환함
#유사한 유저가 못하는 다른 운동 부위
def user2video(sim_user,bad_users,videos,bodypart):
    #유사한 유저의 운동 점수 정보 추출
    targetUser = bad_users[bad_users['userId']==sim_user]
    #못한 운동 부위만 추출
    targetUser_bad = targetUser.loc[:,"bad_health_id"]
    rec_body_parts = []
    #print("bad:",targetUser_bad)
    #못한 운동 부위 중, 현재 못한 부위만 제외
    for key, value in body_part_names.items():
        for bad in targetUser_bad:
            if value == bad and key != bodypart: 
                rec_body_parts.append(key)
                
    #못한운동 부위중 랜덤 선택
    random_part = np.random.choice(rec_body_parts)
    rec_video = videos[videos['mainBody'] == random_part]
    
    #선택된 부위에 대한 운동 영상도 랜덤선택
    random_index = np.random.randint(0, rec_video.shape[0])
    random_title = rec_video.iloc[random_index]['title']
    print('title:',random_title)
        
    return random_title
    

def recommend_collaborative(bodypart,userId):
    csv_path = os.path.dirname(os.path.realpath(__file__))+ '/../csv/'
    
    data = pd.read_csv(csv_path+'user_bad.csv')
    uesr_bads = pd.read_csv(csv_path+'user_bad.csv')
    users = pd.read_csv(csv_path+'user.csv')
    video = pd.read_csv(csv_path+'health_video.csv')
    
    #코사인 유사도 계산을 위한 피벗 테이블    
    data = data.pivot_table('score', index = 'userId', columns = 'bad_health_id')
    
    #유저 메타데이터와 유저의 bad 운동 데이터 셋을 합침
    bad_users = pd.merge(uesr_bads, users, on = 'userId')
    
    #none인 값을 0으로 채움
    data = bad_users.pivot_table('score', index = 'userId', columns = 'bad_health_id').fillna(0)

    #코사인 유사도 계산
    bad_sim = cosine_similarity(data, data)
    
    bad_sim_df = pd.DataFrame(data = bad_sim, index = data.index, columns = data.index)
    print("user1과 비슷한 사람") #여기가 입력이 되어야함
    sim_user = bad_sim_df[userId].sort_values(ascending=False)[1:2].index[0]
    
    return user2video(sim_user,bad_users,video,bodypart)