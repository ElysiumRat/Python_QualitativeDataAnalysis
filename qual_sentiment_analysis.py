###################################
# PACKAGES
###################################

import nltk
import os
import pandas as pd
import warnings

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from tkinter import filedialog

###################################
# DATA DOWNLOADS
###################################

nltk.download('vader_lexicon', quiet=True)

###################################
# FUNCTIONS
###################################

def get_vader_sentiment(text):
    if pd.isna(text):
        # Forcing a return of 0 values if the text has nothing so that the values are at least not empty
        return {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    return analyzer.polarity_scores(str(text))

def get_textblob_sentiment(text):
    if pd.isna(text):
        # Forcing a return of 0 values if the text has nothing so that the values are at least not empty
        return {'polarity': 0.0, 'subjectivity': 0.0}
    analysis = TextBlob(str(text))
    return {
        'polarity': analysis.sentiment.polarity,
        'subjectivity': analysis.sentiment.subjectivity
    }

###################################
# OTHER CODE
###################################

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

###################################
# PRIMARY CODE
###################################

analyzer = SentimentIntensityAnalyzer()

file_path = filedialog.askopenfilename(
    title="Select an Excel file",
    filetypes=[
        ("Excel files", "*.xlsx;*.xls"),
        ("All files", "*.*")
    ]
)

if file_path:
    input_dir, input_filename = os.path.split(file_path)
    file_name_without_ext, _ = os.path.splitext(input_filename)
    
    output_filename = f"{file_name_without_ext}_Sentiment_Analysis_Results.xlsx"
    output_file_path = os.path.join(input_dir, output_filename)

    sheets_dict = pd.read_excel(file_path, sheet_name=None, usecols=[0, 1])

    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        for sheet_name, data_frame in sheets_dict.items():
            if data_frame.empty:
                continue
            id_col = data_frame.columns[0]
            text_col = data_frame.columns[1]

            # VADER
            vader_df = pd.json_normalize(data_frame[text_col].apply(get_vader_sentiment)).add_prefix('vader_')
            
            # TextBlob
            blob_df = pd.json_normalize(data_frame[text_col].apply(get_textblob_sentiment)).add_prefix('textblob_')
            
            # Constructing the data to write
            output_df = pd.concat([data_frame[[id_col, text_col]], vader_df, blob_df], axis=1)
            final_columns = [
                id_col, text_col, 
                'vader_neg', 'vader_neu', 'vader_pos', 'vader_compound',
                'textblob_polarity', 'textblob_subjectivity'
            ]

            # Writing the final Excel spreadsheet
            output_df = output_df[final_columns]
            output_df.to_excel(writer, sheet_name=sheet_name, index=False)