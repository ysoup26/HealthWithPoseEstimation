from django.shortcuts import render
from django.contrib.staticfiles import finders
import subprocess
from .static.python.video_and_dict_pose_cross_correlation2 import video_and_dict_pose_cross_correlation

# Create your views here.

def index(request):
    return render(request,'health_do/index.html')

def health_do(request):
    return render(request,'health_do/health_do.html')

def health_report(request):
    print("[health_report]")
    #
    video_and_dict_pose_cross_correlation()
    re1 = recommend_contentBased(["leg","head"])
    re2 = recommend_collaborative(["leg","head"])
    print(re1,re2)
    return render(request,'health_do/health_report.html',{'recommend':re1})

import pandas as pd #csv파일을 이용하기 위해
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import sys

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
    
def recommend_contentBased(bodyparts):
    print("recommend_contentBased")
    file_path = finders.find('data/health_video_old.csv')
    video_data = pd.read_csv(file_path)

    tfidf_vector = TfidfVectorizer()
    tfidf_matrix = tfidf_vector.fit_transform(video_data['category'] ).toarray()
    tfidf_matrix_feature = tfidf_vector.get_feature_names_out()

    tfidf_matrix = pd.DataFrame(tfidf_matrix, columns=tfidf_matrix_feature, index = video_data.title)

    cosine_sim = cosine_similarity(tfidf_matrix)

    #타이틀-카테고리 표로 변환
    cosine_sim_df2 = pd.DataFrame(cosine_sim, index = video_data.title, columns = video_data.category)

    #카테고리로 추천하기- 사용자가 부족한 운동으로
    content_based_result =category_recommendations(bodyparts[0], cosine_sim_df2, video_data)

    results_title = content_based_result.iloc[:,1]
    result_string = "추천 영상은 다음과 같습니다: " + ", ".join(results_title)
    return result_string

def recommend_collaborative(bodyparts):
    result_string = "추천 영상은 다음과 같습니다: " + ", "+"미정."#.join(results_title)
    return result_string
     