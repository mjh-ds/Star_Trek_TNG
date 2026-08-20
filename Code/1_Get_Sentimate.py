import keyring

# pyrefly: ignore [missing-import]
import polars as pl
from tqdm import tqdm
from transformers import pipeline

hf_token = keyring.get_password("huggingface", "hf_token")

df = pl.read_parquet("./Data/silver/f_lines.parquet")[['line_id','text']]

models = {
    "emotion1": ("text-classification", "j-hartmann/emotion-english-distilroberta-base", {"top_k": 2}),
    "emotion2": ("text-classification", "SamLowe/roberta-base-go_emotions", {"top_k": 2}),
    "sentiment1": ("sentiment-analysis", "distilbert-base-uncased-finetuned-sst-2-english", {}),
    "sentiment2": ("sentiment-analysis", "cardiffnlp/twitter-roberta-base-sentiment-latest", {}),
    "sentiment3": ("sentiment-analysis", "finiteautomata/bertweet-base-sentiment-analysis", {}),
    "sentiment4": ("sentiment-analysis", "roberta-base", {}),
}

#Loops through models dictionary and adds emotion/sentiment to the dataframe
for col, (task, model_name, kwargs) in models.items():
    pipe = pipeline(task,model=model_name,device=0,token=hf_token,**kwargs,)

    results = list(tqdm(pipe((t for t in df["text"]), truncation=True, batch_size=32), 
       total=len(df["text"]), desc=f"Processing {col}"))

    df = df.with_columns(pl.Series(col, results))


df2 = df.with_columns([
    pl.col("sentiment1").struct.field("label").alias("sentiment1_label"),
    pl.col("sentiment1").struct.field("score").alias("sentiment1_score"),
    pl.col("sentiment2").struct.field("label").alias("sentiment2_label"),
    pl.col("sentiment2").struct.field("score").alias("sentiment2_score"),
    pl.col("sentiment3").struct.field("label").alias("sentiment3_label"),
    pl.col("sentiment3").struct.field("score").alias("sentiment3_score"),

    pl.col("emotion1").list.get(0).struct.field("label").alias("emotion1_label_1"),
    pl.col("emotion1").list.get(0).struct.field("score").alias("emotion1_score_1"),
    pl.col("emotion1").list.get(1).struct.field("label").alias("emotion1_label_2"),
    pl.col("emotion1").list.get(1).struct.field("score").alias("emotion1_score_2"),

    pl.col("emotion2").list.get(0).struct.field("label").alias("emotion2_label_1"),
    pl.col("emotion2").list.get(0).struct.field("score").alias("emotion2_score_1"),
    pl.col("emotion2").list.get(1).struct.field("label").alias("emotion2_label_2"),
    pl.col("emotion2").list.get(1).struct.field("score").alias("emotion2_score_2"),
])

df2 = df2.with_columns(
    pl.col("sentiment1_label").replace({"POSITIVE": "positive","NEGATIVE": "negative"}).alias("sentiment1_label"),
    pl.col("sentiment3_label").replace({"POS": "positive","NEG": "negative", "NEU":"neutral"}).alias("sentiment3_label")
)


#Writes out the updated dataset
df2.write_parquet("./Data/silver/f_lines_sentimate.parquet")

df2 = df2.drop([
    col for col, dtype in df.schema.items()
    if dtype.base_type() in (pl.Struct, pl.List)
])
df2.write_csv("./Data/silver/f_lines_sentimate.csv")

