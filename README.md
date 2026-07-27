# Python_QualitativeDataAnalysis
A simple program for Python that takes Excel spreadsheets with qualitative data and runs analyses on them, outputting a spreadsheet with the results. Created to experiment during my doctoral studies.

## Core Functionality

- File Selection: Prompts the user with a native operating system dialog window filtered specifically for Excel formats. If canceled, the script exits safely without processing.
- Workbook Ingestion: Reads all worksheets from the selected workbook simultaneously while targeting the first column as an identifier and the second column as the text source.
- VADER Sentiment Analysis: Evaluates text against the VADER lexicon to generate normalized scores:
  - `vader_neg` (Negative)
  - `vader_neu` (Neutral)
  - `vader_pos` (Positive)
  - `vader_compound` (Overall composite score)
- TextBlob Sentiment Analysis: Analyzes linguistic patterns to generate continuous metrics:
  - `textblob_polarity` (Sentiment polarity ranging from -1.0 to 1.0)
  - `textblob_subjectivity` (Subjectivity ranging from 0.0 to 1.0)
- Missing Data Management: Intercepts null or empty text entries (`NaN`), explicitly assigning zero values to maintain structural integrity and prevent analysis failure.
- Automated Export: Concatenates the original identifier and text columns alongside the newly generated sentiment metrics, structuring them into a clean schema before saving the output as `[Original_Filename]_Sentiment_Analysis_Results.xlsx` in the same directory as the source file.

## Technical Architecture & Code Breakdown

### Global Configurations
- `nltk.download('vader_lexicon', quiet=True)`: Automatically fetches the required VADER lexicon dictionaries from remote servers during startup without cluttering the standard output console.
- `warnings.filterwarnings(...)`: Suppresses benign user warnings thrown by the `openpyxl` engine when reading or writing standard spreadsheet formatting structures.

### Custom Sentiment Extraction Functions
- `get_vader_sentiment(text)`: 
  - Evaluates whether the passed text input is null or missing using `pd.isna(text)`. If missing, it immediately returns a dictionary containing hardcoded neutral zeroes (`0`) to prevent matrix dimensional mismatch and downstream calculation failures.
  - If valid text is present, converts it to a string and passes it into the VADER analyzer instance using `analyzer.polarity_scores()`.
- `get_textblob_sentiment(text)`: 
  - Performs the same missing-data safety check, supplying default fallback zeroes for polarity and subjectivity metrics.
  - If valid text exists, initializes a `TextBlob` object and extracts its continuous sentiment properties: `.sentiment.polarity` and `.sentiment.subjectivity`.

### Interactive File Selection & Path Resolution
- `filedialog.askopenfilename(...)`: Invokes the native OS window dialog, limiting allowed file extensions strictly to Excel formats (`.xlsx` and `.xls`).
- `if file_path:`: Evaluates whether a file path was successfully returned. If the user cancels the dialog, execution skips the entire processing block.
- `os.path.split(...)` and `os.path.splitext(...)`: Deconstructs the full file path string to separate the parent directory from the file name, strips out the original file extension, and dynamically constructs a new target destination path (`[Original_Filename]_Sentiment_Analysis_Results.xlsx`) residing in the identical directory as the source.

### Workbook Iteration and Vectorized Processing
- `pd.read_excel(..., sheet_name=None, usecols=[0, 1])`: Loads every individual worksheet in the target workbook into a Python dictionary (`sheets_dict`), optimizing memory consumption by restricting ingestion to strictly the first two columns (`usecols=[0, 1]`), designated as the identifier column and text column respectively.
- `pd.ExcelWriter(...)`: Opens a context manager using the `openpyxl` engine to write processed dataframes back out to the target file name concurrently across all sheets.
- `.apply()` and `pd.json_normalize()`: Vectorizes the sentiment functions across the target text series element-by-element, then flattens the resulting dictionary outputs into separate structured pandas DataFrames (`vader_df` and `blob_df`).
- `.add_prefix(...)`: Appends unique prefix strings (`vader_` and `textblob_`) to the newly flattened metric columns to prevent naming collisions.
- `pd.concat([...], axis=1)`: Merges the original identifier and text columns side-by-side with the sentiment metrics along the column axis.
- Column Reordering & Serialization: Filters the combined DataFrame down to an explicit schema layout using `final_columns` and writes each sheet back out to the new Excel document.
