#실행: python content_based.py /*운동부위*/

import pandas as pd #csv파일을 이용하기 위해
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys
print(sys.argv[0],sys.argv[1])

video_data = pd.read_csv('./data/health_video_old.csv')

tfidf_vector = TfidfVectorizer()
#tfidf_vector = TfidfVectorizer(ngram_range=(1,2))
#합치지 않으면 오류가 생겼음?
tfidf_matrix = tfidf_vector.fit_transform(video_data['category'] ).toarray()
#tfidf_matrix = tfidf_vector.fit_transform(video_data)
tfidf_matrix_feature = tfidf_vector.get_feature_names_out()

tfidf_matrix = pd.DataFrame(tfidf_matrix, columns=tfidf_matrix_feature, index = video_data.title)
print(tfidf_matrix.shape)
tfidf_matrix.head()

cosine_sim = cosine_similarity(tfidf_matrix)

#타이틀-카테고리 표로 변환
cosine_sim_df2 = pd.DataFrame(cosine_sim, index = video_data.title, columns = video_data.category)
print(cosine_sim_df2.shape)
cosine_sim_df2.head()

#matrix에서 target_title 행을 가져와 정렬하고, k만큼 출력한다.
def category_recommendations(target_category, matrix, items, k=2):
    recom_idx = matrix.loc[:, target_category].values.reshape(1, -1).argsort()[:, ::-1].flatten()[1:k+1]
    recom_title = items.iloc[recom_idx, :].title.values
    recom_category = items.iloc[recom_idx, :].category.values
    recom_difficulty = items.iloc[recom_idx, :].difficulty.values
    recom_id = items.iloc[recom_idx, :].videoId.values
    #target_title_list = np.full(len(range(k)), items[items.category == target_category].title.values)
    target_category_list = np.full(len(range(k)), target_category)
    #target_difficulty_list = np.full(len(range(k)), items[items.category == target_category].difficulty.values)
    d = {
        #'target_title':target_title_list,
        'target_category':target_category_list,
        #'target_difficulty':target_difficulty_list,
        'recom_title' : recom_title,
        'recom_category' : recom_category,
        'recom_dificulty' : recom_difficulty,
        'recom_id' : recom_id
    }
    return pd.DataFrame(d)

#카테고리로 추천하기- 사용자가 부족한 운동으로
content_based_result =category_recommendations(sys.argv[1], cosine_sim_df2, video_data)


results_title = content_based_result.iloc[:,1]
print("추천 영상은 다음과 같습니다: ",end=" ")
for title in results_title:
    print(title,end=", ")