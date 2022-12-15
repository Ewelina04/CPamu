# -*- coding: utf-8 -*-
"""merging_emotion_lexicons

Automatically generated by Colaboratory.
"""

import pandas as pd
import numpy as np
pd.set_option("max_colwidth", 400)


## load Emean database file
emean = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/Emotional word lists/emean_emo_cat.csv')

# taking the average value for the same word-lemma
emean_grp = emean.groupby("lemma", as_index=False).mean()

em_class = emean[['lemma', 'classification']]

# taking mode of emotion category for each word-lemma
emean_grp_class = em_class.groupby('lemma', as_index=False).agg(lambda x:x.value_counts().index[0])
mrg_emean = pd.merge(emean_grp, emean_grp_class, left_on='lemma', right_on='lemma', how='left')

# nawl valence and arousal values
nawl_aro_valc = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/nawl_val_aro.xlsx")
nawl_sentiment = nawl_aro_valc[['val_M_men', 'val_M_women', 'val_M_all','aro_M_men','aro_M_women','aro_M_all']]

# nawl emotions values
nawl = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/pone.0132305.s004.xlsx")
nawl_cols_emo_val = [col for col in nawl.columns if "_M_" in col]
nawl_cols_emo_val = ['No.', 'BAWL_word', 'NAWL_word', 'ED_class', 'Briesemeister_liberal', 'BE_N_all'] + nawl_cols_emo_val
nawl2 = nawl[nawl_cols_emo_val]
nawl_all = pd.merge(nawl2, nawl_sentiment, left_index=True, right_index=True, how="left")


emean_db = mrg_emean[['lemma', 'N', 'VAL M', 'ARO M', 'ANG M', 'DIS M', 'FEA M', 'SAD M', 'HAP M', 'classification']]
nawl_db = nawl_all[['NAWL_word', 'BE_N_all', 'val_M_all', 'aro_M_all', 'ang_M_all', 'dis_M_all', 'fea_M_all', 'sad_M_all', 'hap_M_all', 'ED_class']]


emean_db.columns = ['Word', 'N', 'Valence', 'Arousal', "Anger", 'Disgust', 'Fear', 'Sadness', "Happiness", "Class"]
emean_db["Database"] = "Sentimenti"

nawl_db.columns = ['Word', 'N', 'Valence', 'Arousal', "Anger", 'Disgust', 'Fear', 'Sadness', "Happiness", "Class"]
nawl_db["Database"] = "NAWL"

joined_db = pd.concat([emean_db, nawl_db], join='outer', axis=0).reset_index(drop=True)


map_classes = {'N' : 'NEU', 'F':'FEA', 'H':'HAP', 'S':'SAD', 'A':'ANG', 'D':'DIS', 'SUR':'SUR', 'ANT':'ANT', 'TRU':'TRU', 'unclassified':'unclassified',
               'NEU':'NEU', 'SUR':'SUR', 'FEA':'FEA', 'DIS':'DIS', 'ANG':'ANG','HAP':'HAP', 'SAD':'SAD'}

joined_db['Class'] = joined_db['Class'].map(map_classes)
joined_db.drop_duplicates(subset=['Word'], keep='first', inplace=True)

joined_sentimenti = joined_db[joined_db.Database == 'Sentimenti']
joined_nawl = joined_db[joined_db.Database == 'NAWL']

def normalization(data):
  from sklearn.preprocessing import MinMaxScaler
  scaler = MinMaxScaler()
  df = data.copy()
  scaled_values = scaler.fit_transform(df)
  df.loc[:, :] = scaled_values
  return df

scaled_val_sentimenti = normalization(joined_sentimenti[['Valence', 'Arousal', 'Anger', 'Disgust', 'Fear','Sadness', 'Happiness']])

scaled_val_nawl = normalization(joined_nawl[['Valence', 'Arousal', 'Anger', 'Disgust', 'Fear','Sadness', 'Happiness']])

senti = joined_sentimenti.copy()
senti[['Valence', 'Arousal', 'Anger', 'Disgust', 'Fear','Sadness', 'Happiness']] = scaled_val_sentimenti
joined_nawl[['Valence', 'Arousal', 'Anger', 'Disgust', 'Fear','Sadness', 'Happiness']] = scaled_val_nawl

#senti["Polarity"] = pd.cut(senti["Valence"], 5, labels=[-2, -1, 0, 1, 2], ordered=False)
senti["Polarity"] = pd.cut(senti["Valence"], bins = [-3, -1.51, -0.51, 0.51, 1.51, 3.5], right=False, labels = [-2, -1, 0, 1, 2])

#joined_nawl["Polarity"] = pd.cut(joined_nawl["Valence"], 5, labels=[-2, -1, 0, 1, 2], ordered=False)
joined_nawl["Polarity"] = pd.cut(joined_nawl["Valence"], bins = [-3, -1.51, -0.51, 0.51, 1.51, 3.5], right=False, labels = [-2, -1, 0, 1, 2])

joined_scaled_db = pd.concat([senti, joined_nawl], join='outer', axis=0).reset_index(drop=True)
joined_scaled_db.to_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/joined_scaled_NAWL-Sentimenti_db.xlsx")


# lexicon with emotion categories
df_category = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/joined_scaled_NAWL-Sentimenti_db.xlsx", index_col=0)
df_category = df_category[(df_category.Class != 'ANT') & (df_category.Class != 'TRU') & (df_category.Class != 'SUR') & (df_category.Class != 'unclassified')]
df_category.to_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/emotion_6-categories_NAWL_Sentimenti_db.xlsx")



# Polarity only lexicon
polarity_dbs_only = joined_scaled_db[['Word', 'Database', 'Polarity']]

whole_clrin = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/clarin_emo_1.csv")
whole_clrin.dropna(subset=['stopien_nacechowania'],  inplace=True)

whole_clrin["Polarity"] = ''
whole_clrin.loc[whole_clrin.stopien_nacechowania == '- s', "Polarity"] = -1
whole_clrin.loc[whole_clrin.stopien_nacechowania == '- m', "Polarity"] = -2
whole_clrin.loc[whole_clrin.stopien_nacechowania == 'amb', "Polarity"] = 0
whole_clrin.loc[whole_clrin.stopien_nacechowania == '+ m', "Polarity"] = 2
whole_clrin.loc[whole_clrin.stopien_nacechowania == '+ s', "Polarity"] = 1


whole_clrin.drop_duplicates(subset=['lemat'], keep='last', inplace=True)
whole_clrin['Database'] = "Clarin"
clarin_polarity_only = whole_clrin[['lemat', 'Database', 'Polarity']]
clarin_polarity_only.columns = ['Word', 'Database', 'Polarity']

clarin_polarity_only = clarin_polarity_only[clarin_polarity_only.Polarity != 0]
polarity_3db = pd.concat([polarity_dbs_only, clarin_polarity_only], join='outer', axis=0).reset_index(drop=True)
polarity_3db.drop_duplicates(subset=['Word'], keep='first', inplace=True)

joined_db2 = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/joined_scaled_NAWL-Sentimenti_db.xlsx", index_col=0)
joined_db2 = joined_db2[['Word', 'Class', 'Database']]

imbir = pd.read_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/imbir.XLSX", index_col=0)

#imbir["Polarity"] = pd.cut(imbir["Valence_M"], 5, labels=[-2, -1, 0, 1, 2], ordered=False)
imbir["Polarity"] = pd.cut(imbir["Valence_M"], bins = [0, 2.51, 4.51, 5.51, 7.51, 9.5], right=False, labels = [-2, -1, 0, 1, 2])


imbir["Database"] = "Imbir"

imbir_polar = imbir[['polish word', 'Database', 'Polarity']]
imbir_polar.columns = ['Word', 'Database', 'Polarity']

joined_polar = pd.concat([polarity_3db, imbir_polar], join='outer', axis=0).reset_index(drop=True)
joined_polar.drop_duplicates(subset=['Word'], keep='first', inplace=True)
joined_polar.to_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/polarity_23k-words_Sentimenti_NAWL_Clarin_Imbir_db.xlsx")


# Valnece (continuous value) only lexicon
joined_valence = joined_scaled_db[["Word", "Database", "Valence"]]
imbir_valence = imbir[['polish word', 'Database', 'Valence_M']]
imbir_valence.columns = ['Word', 'Database', 'Valence']

norm_imb_val = normalization(imbir_valence[['Valence']])
imbir_valence[['Valence']] = norm_imb_val

joined_scaled_valence = pd.concat([joined_valence, imbir_valence], join='outer', axis=0).reset_index(drop=True)
joined_scaled_valence.drop_duplicates(subset=['Word'], keep='first', inplace=True)

def standardize(data):
  from sklearn.preprocessing import StandardScaler
  scaler = StandardScaler()
  df = data.copy()
  scaled_values = scaler.fit_transform(df)
  df["Valence_standardized"] = scaled_values
  return df


df_senti = joined_scaled_valence[joined_scaled_valence.Database == 'Sentimenti']
df_NAWL = joined_scaled_valence[joined_scaled_valence.Database == 'NAWL']
df_Imbir = joined_scaled_valence[joined_scaled_valence.Database == 'Imbir']

df_senti1 = standardize(df_senti[['Valence']])
df_NAWL1 = standardize(df_NAWL[['Valence']])
df_Imbir1 = standardize(df_Imbir[['Valence']])

df_senti = pd.merge(df_senti, df_senti1.iloc[:, 1:], left_index=True, right_index=True)
df_NAWL = pd.merge(df_NAWL, df_NAWL1.iloc[:, 1:], left_index=True, right_index=True)
df_Imbir = pd.merge(df_Imbir, df_Imbir1.iloc[:, 1:], left_index=True, right_index=True)

df_val_all = pd.concat([df_senti, df_NAWL, df_Imbir], axis=0)


df_val_all.to_excel("/content/drive/MyDrive/Colab Notebooks/Emotional word lists/valence_only10k_scaled_NAWL-Sentimenti_Imbir.xlsx")



