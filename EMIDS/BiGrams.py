from nltk.util import ngrams
from typing import Union
import pandas
def GetScore(df, search)-> Union[pandas.DataFrame, list]:
  maxoverall=[0,[]]
  vals_above_threshold=False
  input_islist=False
  result_df = pandas.DataFrame()
  row_toappend = df.loc[0,]
  for j in range(len(df)):
    if(type(df)==list):
        row=df
        row_vals=[]
        input_islist=True
    else:
        row=df.loc[j,].tolist()
    maxval=0
    
    for word in row:
      if not type(word)==str:
        word=str(word)
      word=word.lower()
      l1=[]
      l2=[]   
      word_as_chars=[x for x in word]
      searchstr_as_chars=[x for x in search.lower()]
      bigram1 = list(ngrams(word_as_chars, 2))
      bigram2 = list(ngrams(searchstr_as_chars, 2))
      comb=[]
      comb.extend(bigram1)
      for i in bigram2:
        if i not in comb:
          comb.append(i)
      for w in comb:
        if w in bigram1: l1.append(1)
        else: l1.append(0)
        if w in bigram2: l2.append(1)
        else: l2.append(0)
      c = 0
      for i in range(len(comb)):
        c+= l1[i]*l2[i]

      if float((sum(l1)*sum(l2))**0.5) == 0:
        cosine=0
      else:
        cosine = c / float((sum(l1)*sum(l2))**0.5)
      
      if cosine>maxoverall[0]:
        maxoverall[0]=cosine
        maxoverall[1]=[word] if input_islist==True else row
        row_toappend = df.loc[j,]
      maxval=max(maxval,cosine)
      if cosine>0.75 and input_islist==True:
        row_vals.append([word,cosine])
    if(maxval > 0.75):
        vals_above_threshold=True
        if input_islist==False:
            result_df=result_df.append(df.loc[j,])                   
  if input_islist==True:
    for hits in row_vals:
        print(hits[0],' - ',hits[1])
  # if vals_above_threshold==False:
    # print(' '.join(maxoverall[1]), ' - ', maxoverall[0])
    # result_df=result_df.append(row_toappend)
  if input_islist:
    return row_vals
  else:
    return result_df      




# df = pandas.read_excel(r'C:\Users\chand\Downloads\SampleTable01.xlsx')
# search ='hariharasubramanian'
# hit_df = GetScore(df,search)
# print(hit_df)










