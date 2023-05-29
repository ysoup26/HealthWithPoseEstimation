#실행: python content_based.py /*운동부위*/

import pandas as pd #csv파일을 이용하기 위해
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#matrix에서 target_title 행을 가져와 정렬하고, k만큼 출력한다.
def category_recommendations(target_mainBody, matrix, items, k=1):
    recom_idx = matrix.loc[:, target_mainBody].values.reshape(1, -1).argsort()[:, ::-1].flatten()[1:k+1]
    if recom_idx > matrix.shape[0]:  #추천해줄 운동이 없으면 (1~9)중에 랜덤
        recom_idx = np.random.randint(1, matrix.shape[0],1) 
    recom_title = items.iloc[recom_idx, :].title.values
    recom_mainBody = items.iloc[recom_idx, :].mainBody.values
    recom_id = items.iloc[recom_idx, :].videoId.values
    target_mainBody_list = np.full(len(range(k)), target_mainBody)
    d = {
        'target_mainBody':target_mainBody_list,
        'recom_title' : recom_title,
        'recom_mainBody' : recom_mainBody,
        'recom_id' : recom_id
    }
    return pd.DataFrame(d)

def recommend_contentBased(bodypart):
    
    dir_path = os.path.dirname(os.path.realpath(__file__))+ '/../csv/health_video.csv'
    
    video_data = pd.read_csv(dir_path)#'./../csv/health_video_old.csv')

    tfidf_vector = TfidfVectorizer()
    #tfidf_vector = TfidfVectorizer(ngram_range=(1,2))
    #합치지 않으면 오류가 생겼음?
    tfidf_matrix = tfidf_vector.fit_transform(video_data['mainBody'] ).toarray()
    #tfidf_matrix = tfidf_vector.fit_transform(video_data)
    tfidf_matrix_feature = tfidf_vector.get_feature_names_out()

    tfidf_matrix = pd.DataFrame(tfidf_matrix, columns=tfidf_matrix_feature, index = video_data.title)
    #print(tfidf_matrix.shape)
    tfidf_matrix.head()

    cosine_sim = cosine_similarity(tfidf_matrix)

    #타이틀-카테고리 표로 변환
    cosine_sim_df2 = pd.DataFrame(cosine_sim, index = video_data.title, columns = video_data.mainBody)
    #print(cosine_sim_df2.shape)
    cosine_sim_df2.head()

    #카테고리로 추천하기- 사용자가 부족한 운동으로
    content_based_result =category_recommendations(bodypart, cosine_sim_df2, video_data)

    results_title = content_based_result.iloc[0,1]
    
    result_string = results_title
    return result_string