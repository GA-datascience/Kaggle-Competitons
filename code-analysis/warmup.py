# Kaggle competition warm up 
# Quora question pairs 

# Ctrl F to find contents e.g for 1, find #1 
# Table of contents 
#
# 1: More in depth structure  
# 2: Attempt to fit the mean prob of duplicates of our train set to our test set. 
# 3: Text analysis (on the train set)
# 4: XGBoost Prep
#  : References   





#================================================
# importing libraries 


import numpy as np 
import pandas as pd 
import os # read or open file 
import gc 
import matplotlib.pyplot as plt 
import seaborn as sns # statistical visualization 
%matplotlib inline
pal = sns.color_palette() # for color selection later on :)

#=============================================== 
# All data import and manipulation 
#
# To make things easier, I will 
df_train = pd.read_csv('train.csv')
df_test = pd.read_csv('test.csv')




#===========================================================================
#1 More in depth structure 




# view the top few to see the structure of the data 
df_train.head()

# number of elements (length ) 
print('Total number of question pairs for training: {}'.format(len(df_train)))

# find out which elements have is_duplicate column =1 
# taking the .mean = the number of trues out of the entire samples 
print('Duplicate pairs: {}%'.format(round(df_train['is_duplicate'].mean()*100, 2)))

qids = pd.Series(df_train['qid1'].tolist() + df_train['qid2'].tolist())
# take out unique number 
print('Total number of questions in the training data: {}'.format(len(
    np.unique(qids))))
print('Number of questions that appear multiple times: {}'.format(np.sum(qids.value_counts() > 1)))





#Histogram 


# we can see that from the histogram that there is one question that appears 160 times 
plt.figure(figsize=(12, 5))
plt.hist(qids.value_counts(), bins=50)
plt.yscale('log', nonposy='clip')
plt.title('Log-Histogram of question appearance counts')
plt.xlabel('Number of occurences of question')
plt.ylabel('Number of questions')
print()



#===========================================================
#2 Attempt to fit the mean prob of duplicates of our train set to our test set. 

# submission 1 

from sklearn.metrics import log_loss

# p is what we computed earlier 
# p = prob of duplicates in train set, 36%
# log loss tells us the score of our method 

p = df_train['is_duplicate'].mean()
print('Predicted score:', log_loss(df_train['is_duplicate'], np.zeros_like(df_train['is_duplicate']) + p))



# format is pd.DataFrame({})
# inside 'title': data , 'title of var': data

firstsub = pd.DataFrame({'test_id':df_test['test_id'],'is_duplicate':p})
firstsub.head()
# output this as csv
firstsub.to_csv('first_submission.csv', index=False)


# taking a look at the test set 
#
df_test.head()

print('total number of question pairs for testing:{}'.format(len(df_test)))

# wow we have nearly 2 million question pairs!! 
# but the actual questions are lower since most are randomly generated by kaggle to 
# prevent hand labellng (cheating)


#===========================================================================
#3 Text analysis (on the train set)
# 
# 1. character count analysis 
# 2. word count analysis 
# 3. word cloud 
# 4. semantic analysis 
# 5. stopwords analysis 
# 6. TF-IDF 


# Now we will want to list all the questions out. 
# * note: panda series list elements out and we want to make them string. (as type) 
# * note: astype is for series 
train_qs = pd.Series(df_train['question1'].tolist() + df_train['question2'].tolist()).astype(str)

test_qs = pd.Series(df_test['question1'].tolist() + df_test['question2'].tolist()).astype(str)




# character count analysis --------------------------------------------------------
# apply len on each row. number of characters for each question
dist_train = train_qs.apply(len)
dist_test = test_qs.apply(len)


# time to plot some visuals

# * notes: normed is normalized the y axis. i.e [0 to 1]

plt.figure(figsize=(15,10))
plt.hist(dist_train, bins=200, range=[0,200], color=pal[2], normed=True, label='train')
plt.hist(dist_test, bins=200, range=[0,200], color=pal[1], normed=True, label = 'test')
plt.title('Normalised histogram of character count for all questions', fontsize = 20)
plt.legend()
plt.xlabel('Number of characters', fontsize=15)
plt.ylabel('Probability')

# some statistics of the data 
print('mean-train {:.2f} std-train {:.2f} mean-test {:.2f} std-test {:.2f} max-train {:.2f} max-test {:.2f}'.format(dist_train.mean(), 
                          dist_train.std(), dist_test.mean(), dist_test.std(), dist_train.max(), dist_test.max()))


# some comments: 
# we can see that from both of the test set, the average number of characters lies around 60 characters 
# Very rare are there questions exceeding 150-200 characters. 



# words count analysis  --------------------------------------------------------

# remove spaces 
# lamda apply do properly to each row 
dist_train_word = train_qs.apply(lambda x: len(x.split(' ')))
dist_test_word = test_qs.apply(lambda x: len(x.split(' ')))

# time to plot 

plt.figure(figsize=(15,10))
plt.hist(dist_train_word, bins=50, normed=True, color= pal[4], range= [0,50], label='train')
plt.hist(dist_test_word, bins=50, normed=True, color = pal[5], range=[0,50], label = 'test')
plt.legend()
plt.title('Normlized histogram of word count of questions', fontsize = 20)
plt.xlabel('Word count')
plt.ylabel('Probability')

print('mean-train {:.2f} std-train {:.2f} mean-test {:.2f} std-test {:.2f} max-train {:.2f} max-test {:.2f}'.format(dist_train_word.mean(), 
                          dist_train_word.std(), dist_test_word.mean(), dist_test_word.std(), dist_train_word.max(), dist_test_word.max()))


# comments: we can see that lies around 10, with some outlier being at 200(?) Both have similar distribution


#Word cloud analysis-----------------------------------------------

from wordcloud import WordCloud


# A fix format for doing word cloud in python


the_word_cloud = WordCloud().generate(' '.join(train_qs.astype(str)))
# now to plot the word cloud 
plt.figure(figsize = (20,15))
plt.imshow(the_word_cloud)
plt.axis('off')


#Semantic analysis  --------------------------------------------------------

# Taking a look at the punctuation in the questions. 
# using .apply lambda function  

question_marks = np.mean(train_qs.apply(lambda x: '?' in x))
math = np.mean(train_qs.apply(lambda x: '[math]' in x)) # check if there are math equations 
fullstop = np.mean(train_qs.apply(lambda x: '.' in x)) 

capital_first = np.mean(train_qs.apply(lambda x: x[0].isupper())) 
capitals = np.mean(train_qs.apply(lambda x: max([y.isupper() for y in x]) )) # for each x, [true, false , false, ...etc] then we take the max 
numbers = np.mean(train_qs.apply(lambda x: max([y.isdigit() for y in x])))

print('Questions with question marks: {:.2f}%'.format(question_marks * 100))
print('Questions with [math] tags: {:.2f}%'.format(math * 100))
print('Questions with full stops: {:.2f}%'.format(fullstop * 100))
print('Questions with capitalised first letters: {:.2f}%'.format(capital_first * 100))
print('Questions with capital letters: {:.2f}%'.format(capitals * 100))
print('Questions with numbers: {:.2f}%'.format(numbers * 100))



# Using ntlk, initial feature analysis  --------------------------------------------------------
# import nltk 
# nltk.download()
# under corpus > choose stopwords to install it 


from nltk.corpus import stopwords

# preset a set of stopwords from the corpus database which we will use later, 153 stopwords 
stops = set(stopwords.words("english"))




# Very powerful function written: To give proportion of shared words without the stopwords 
# 
# This function only applies to 1 question pair of 1 row. *


def word_match_share(row):
    # define dictionary. recall dictionary maps key + value {key:value, key:value} and we call the q1words['key'] = value  
    q1words = {}
    q2words = {}
    
    
    # row is a mini dataframe for later 
    # .lower.split change all to lower and split each words into list object 
    # so for each element in the list, if the word is not in stop set, we place it in the dictonary q1words
    # q1words contains all the non stop words in q1 
    # q2words contains all the non stop words in q2 
    
    for word in str(row['question1']).lower().split(): 
        if word not in stops: 
            q1words[word] = 1 
    # do the same for q2 
    for word in str(row['question2']).lower().split(): 
        if word not in stops:
            q2words[word] = 1
    
    # conisder the case where the entire sentence is all stopwords 
    # we want to return 0 because if q1words or q2words is 0, there is no point continuing 
    if len(q1words) == 0 or len(q2words) == 0 :
        return 0
    # find the proportion of shared words between q1 and q2 out of the whole question     
    # recall, q1words is dictionary, key value pair. we want the keys only 
    # add them into shared_words_q1 as a list 
    shared_words_q1 = [word for word in q1words.keys() if word in q2words.keys()]
    shared_words_q2 = [word for word in q2words.keys() if word in q1words.keys()]   
    R = (len(shared_words_q1) + len(shared_words_q2))/(len(q1words) + len(q2words))
    return R 
    


    
# using the function we created above 
# * note: apply takes in argument of function and apply it to every row (axis = 1)
# default axis = 0 ( every column) 

# list of every question pair in train set and the proportion of shared words 
word_match_trainset = df_train.apply(word_match_share, axis = 1, raw=True)

      
# time to plot the thing out! 

plt.figure(figsize = (15,5))        
# take out the idex of those with is_duplicate == 0
plt.hist(word_match_trainset[df_train['is_duplicate']== 0], bins= 20, normed= True, label= 'no duplicate')
plt.hist(word_match_trainset[df_train['is_duplicate']== 1], bins= 20, normed= True, label= 'is duplicate', alpha = 0.7)
plt.legend()
plt.title('Train set: Duplicate vs no duplicate, proportion of shared words', fontsize =15)
plt.xlabel('Proportion of shared words', fontsize = 15)        

# comments: We can see that for question pairs that are not the same type of questions, they tend to have 
# less shared words as compared to question pairs that are the same! 
# There is indeed some link to shared words to how similar the questions are. 
# If we are asking the same type of questions, it is highly likely there are a larger proportion of 
# shared words :) 
    
# TF-IDF  --------------------------------------------------------

# Term frequency inverse document frequency 
# moving on ahead from the above feature, will be using what is known as the 
# TF-IDF feature. We want the rare shared words between the questions than the common ones     
        
from collections import Counter

# If a word appears only once, we ignore it completely (likely a typo)
# Epsilon defines a smoothing constant, which makes the effect of extremely rare words smaller
def get_weight(count, eps=10000, min_count=2):
    if count < min_count:
        return 0
    else:
        return 1 / (count + eps)

eps = 5000 
words = (" ".join(train_qs)).lower().split() 
counts = Counter(words)

# some basic explaination what is going on here: 
# counts.items is a dict items of (word, count)
# so for x,y is where x = words and y = count of the words 
# where we input the x and y into x:get_weight(y) 
# recall: dictionary class with a key and value  

weights = {word: get_weight(count) for word, count in counts.items()}       

# show top 10 [:10]
# top common words so smallest weight
print('Top 10  common words and weights: \n')
print(sorted(weights.items(), key=lambda x: x[1] if x[1] > 0 else 1)[:10])

# show bottom 10 (lowest weight) (less than 2 counts) bigger weight
print('Bottom 10 common words and weights: \n')
(sorted(weights.items(), key=lambda x: x[1], reverse=True)[:10])



# lets do another super function to do the shared word.
# but now, instead of doing it proportion of shared words, we will use weights 

def tfidf_word_match_share(row):
    q1words = {}
    q2words = {}
    for word in str(row['question1']).lower().split():
        if word not in stops:
            q1words[word] = 1
    for word in str(row['question2']).lower().split():
        if word not in stops:
            q2words[word] = 1
    if len(q1words) == 0 or len(q2words) == 0:
        # The computer-generated chaff includes a few questions that are nothing but stopwords
        return 0
    
    # so now, we have q1words with all the non stopwords and q2words with all non stopwords from q2 
    # previously, we used proportion of shared words between the question pairs 
    # now, lets use weights to quantify it 
    
    # extracting the value by searching for shared words (shared keys )
    # [list of shared weights] [ weight1 ,weight2 ... etc]
    shared_weights = [weights.get(word,0) for word in q1words if word in q2words] + [weights.get(word,0) for word in q2words if word in q1words]   
    
    total_weights = [weights.get(word,0) for word in q1words] + [weights.get(word,0) for word in q2words]
    # recall both list are still a list of weights... so we need to sum them up 
    R = np.sum(shared_weights) / np.sum(total_weights)
    return R 
    
    
    
# lets plot the same histogram to compare 
# lets use our super function 
tfid_word_match_trainset = df_train.apply(tfidf_word_match_share, axis = 1, raw = True)


# fillna to fill the na or Nan
plt.figure(figsize = (15,5))
plt.hist(tfid_word_match_trainset[df_train['is_duplicate']==0].fillna(0), bins = 20, normed = True, label = 'no duplicate')    
plt.hist(tfid_word_match_trainset[df_train['is_duplicate']==1], bins = 20, normed = True, label = 'duplicate', alpha = 0.7)    
plt.legend()
plt.title('Train set: Duplicate vs no duplicate, weights of shared words', fontsize =15)
plt.xlabel('proportion of shared words using tfidf', fontsize = 15)
    
    
# comparison using AUC between our first shared words proportion vs our TFIDF shared words 
# roc_auc_score(true, your estimate)
# recall: our word_match are series of proportion of shared words which we can use as a measure 
# for our duplicate estimation 
from sklearn.metrics import roc_auc_score
print('original AUC:', roc_auc_score(df_train['is_duplicate'], word_match_trainset ))
print('TDIDF:', roc_auc_score(df_train['is_duplicate'], tfid_word_match_trainset ))
 
# comments: TDIDF model is not as good as the basic estimation.     
# let us try to do the model for the proportion of shared words on the test set and lets submit to see 
# if our score if improve! 

word_match_testset = df_test.apply(word_match_share, axis = 1, raw=True)
word_match_testset_df = pd.Series.to_frame(word_match_testset) # convert series to frame
secondsub = pd.DataFrame({'test_id':df_test['test_id'],'is_duplicate':word_match_testset_df[0]})
secondsub.head()
# output this as csv
secondsub.to_csv('second_submission.csv', index=False)

# comments: Really no need to submit. The AUC score shows its a 0.7 Really bad :/ 


#===========================================================

#4 XGBoost 

# The rebalancing (? clarify) process for the data XGboost receives 
# 37% positive class in training set and only 17% on test set  
# Aim to rebalance the training set to 17%

# empty data frames 
x_train = pd.DataFrame()
x_test = pd.DataFrame()
# fill in the data frames with some of the features we found previously
x_train['word_match'] = word_match_trainset
x_train['tfidf']= tfid_word_match_trainset

x_test['word_match'] = df_test.apply(word_match_share, axis= 1, raw = True)
x_test['tfidf'] = df_test.apply(tfidf_word_match_share, axis = 1, raw = True)

# using y_train a reference later 
# we want to extract rows with ==1 and ==0 under is_duplicate
# notes *: similar to R where we use df[df$is_duplicate == 1]
y_train = df_train['is_duplicate'].values # consist of is_duplicate 1 or 0

pos_train = x_train[y_train == 1] #df 
neg_train = x_train[y_train == 0] #df   
    

# now we over sample the negative class (need more reference on this methodology)
p = 0.165
scale = ((len(pos_train) / (len(pos_train) + len(neg_train))) / p) - 1
while scale > 1:
    neg_train = pd.concat([neg_train, neg_train])
    scale -=1
neg_train = pd.concat([neg_train, neg_train[:int(scale * len(neg_train))]])
print(len(pos_train) / (len(pos_train) + len(neg_train)))

# rebild the x_train and y_train 
x_train = pd.concat([pos_train, neg_train])
y_train = (np.zeros(len(pos_train)) + 1).tolist() + np.zeros(len(neg_train)).tolist()
del pos_train, neg_train

# split some data off for validation 
# see help(train_test_split)
# we are splitting the df of x_train and y_train into 2 more. so total 4 df
# the valid is like a test set. renamed to avoid confusion
# the y dataframes are the labels of is_duplicates with 1/0
 
from sklearn.cross_validation import train_test_split 

x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size = 0.2, random_state = 12357)


# begin xgboost ------------------------------------------------------------------------
import xgboost as xgb

# set parameters for xgboost 
# some general parameters: 

# Booster parameters
    # eta =  The default value is set to 0.3. You need to specify step size shrinkage used in update to prevents overfitting. 
    # After each boosting step, we can directly get the weights of new features. 
    # and eta actually shrinks the feature weights to make the boosting process more conservative. 
    # The range is 0 to 1. Low eta value means model is more robust to overfitting.
    
    # max_depth =  The default value is set to 6. 
    # You need to specify the maximum depth of a tree. The range is 1 to ∞.
#-------------------------------------------------------------------------------------    
# learning task parameters 
    # Objective = The default value is set to reg:linear . 
    # You need to specify the type of learner you want which includes linear regression, 
    # logistic regression, poisson regression etc.
    
    # eval metric = You need to specify the evaluation metrics for validation data, a default metric will be assigned according 
    # to objective( rmse for regression, and error for classification, 
    # mean average precision for ranking

params = {} # dict 
params['eta'] = 0.02
params['max_depth'] = 4

params['objective'] = 'binary:logistic'
params['eval_metric'] = 'logloss'

d_train = xgb.DMatrix(x_train, label = y_train) # train set input into xgb
d_valid = xgb.DMatrix(x_valid, label = y_valid) # valid (test) set input. 

# for evals_result: dict class
watchlist = [(d_train, 'train'), (d_valid, 'valid')]

# start modelling and training on the train and valid df (split from x_train and y_train)
bst = xgb.train(params, d_train, 500, watchlist, early_stopping_rounds=50, verbose_eval=10)

# so now we have our model that is trained to a low log loss, we can now apply the model to the test set 

d_test = xgb.DMatrix(x_test) # convert the real test df into xbg format
result_test = bst.predict(d_test) # put into our model above. this is our answer  

# now lets write our answer to csv

thirdsub = pd.DataFrame({'test_id':df_test['test_id'],'is_duplicate':result_test})

thirdsub.to_csv('thirdsub.csv',index = False )


# score= 0.35460


#===========================================================

#5 References 

# main script 
# https://www.kaggle.com/anokas/quora-question-pairs/data-analysis-xgboost-starter-0-35460-lb

# xgboost parameters 
# https://www.analyticsvidhya.com/blog/2016/01/xgboost-algorithm-easy-steps/

# xgboost improvement 
# https://www.kaggle.com/alijs1/quora-question-pairs/xgb-starter-12357/code




















    
    
    
    
    
    
    
    

