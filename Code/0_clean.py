# Star Trek TNG data cleaning and organization script #
#######################################################
#
# Raw Data: https://github.com/RMHogervorst/TNG/tree/master/raw-data
# Supplimental data: https://www.kaggle.com/datasets/ashirwadsangwan/imdb-dataset
#
#
#
#
#
#
#


# pyrefly: ignore [missing-import]
import polars as pl

# pyrefly: ignore [missing-import]
import polars.selectors as cs

df = pl.read_csv("./data/bronze/TNG.csv", encoding="iso-8859-1", has_header=True, null_values="NA",
    new_columns=["row_num", "episode_title", "production_number", "setnames", "characters", "act", "scene_number", "scene_details",
                 "part_number", "type", "who", "text", "speech_description", "release_date", "episode_number", "imdb_rating",
                 "imdb_id", "season_number",])

# Create a mapping dataframe that we'll fill in missing values
updates = pl.DataFrame({
        "production_number": ["#40275-226","#40276-233","#40271-941"],
        "imdb_id":           ["tt0708828" ,"tt0708760" ,"tt0094030"],
        "season_number":     [5 , 6, None],
        "episode_number":    [26, 7, None],
        "imdb_rating":       [8.40, 7.30, None ]
        })


df2 = (df.join(updates, on="production_number", how="left", suffix="_zz")
        .with_columns(
          imdb_id=pl.coalesce("imdb_id_zz", "imdb_id"),
          season_number=pl.coalesce("season_number_zz", "season_number"),
          episode_number=pl.coalesce("episode_number_zz", "episode_number"),
          imdb_rating=pl.coalesce("imdb_rating_zz", "imdb_rating"))
        .drop(cs.ends_with("_zz"))
       )

df2 = (df2.join(updates, on="imdb_id", how="left", suffix="_zz")
          .with_columns(
              production_number=pl.coalesce("production_number_zz", "production_number"))
          .drop(cs.ends_with("_zz"))
        )

episodes = (df2[['season_number','episode_number','episode_title','production_number','imdb_id','imdb_rating','setnames','characters']]
             .unique()
             .sort(['season_number','episode_number'])
             .cast({
                "season_number": pl.Int8,
                "episode_number": pl.Int8,
                "episode_title": pl.String,
                "production_number": pl.String,
                "imdb_id": pl.String,
                "imdb_rating": pl.Float32,
                "setnames": pl.String,
                "characters": pl.String,})
           )

episodes.write_parquet("./Data/silver/d_episodes.parquet")
episodes.write_csv("./Data/silver/d_episodes.csv")



# Creating the lines dataset, which will hold most of the information about the scene, what was said, and who said it.
lines = ( 
    df2[['imdb_id','act','scene_number','scene_details','part_number','type','who','text','speech_description']]
        .with_row_index("line_id", offset=1)
        .with_columns(
           pl.col(["who", "text"]).str.strip_chars(),
           pl.col("scene_number").str.strip_chars().str.replace_all(r"\D+", ""),)
        .cast({
                "imdb_id": pl.String,
                "act": pl.String,
                "scene_number": pl.Int16,
                "scene_details": pl.String,
                "part_number": pl.Int16,
                "type": pl.String,
                "who": pl.String,
                "text": pl.String,
                "speech_description": pl.Boolean})
    )



lines.write_parquet("./Data/silver/f_lines.parquet")
lines.write_csv("./Data/silver/f_lines.csv")




#https://www.kaggle.com/datasets/ashirwadsangwan/imdb-dataset

def load_imdb(fn, id_column, keep_list):
    cdf = (
    pl.scan_csv(f"./data/bronze/{fn}", separator="\t",quote_char=None,null_values=r"\N")
    .filter(pl.col(id_column).is_in(keep_list))
    .collect()
    )
    return cdf

df_title_basics = load_imdb("title.basics.tsv", "tconst",episodes["imdb_id"].implode()
).select([
        pl.col("tconst").alias("imdb_id").cast(pl.String),
        pl.col("primaryTitle").alias("primary_title").cast(pl.String),
        pl.col("originalTitle").alias("original_title").cast(pl.String),
        pl.col("startYear").alias("start_year").cast(pl.Int16),
        pl.col("runtimeMinutes").alias("runtime_minutes").cast(pl.Int16),
    ])

df_title_ratings = load_imdb("title.ratings.tsv", "tconst",episodes["imdb_id"].implode()
).select([
        pl.col("tconst").alias("imdb_id").cast(pl.String),
        pl.col("averageRating").alias("imdb_rating_2026").cast(pl.Float32),
        pl.col("numVotes").alias("num_votes_2026").cast(pl.Int32),
    ])

episodes = (episodes
       .join(df_title_basics, on="imdb_id", how = "left")
       .join(df_title_ratings, on="imdb_id", how = "left")
)

episodes.write_parquet("./Data/silver/d_episodes.parquet")
episodes.write_csv("./Data/silver/d_episodes.csv")



df_episode_cast = load_imdb("title.principals.tsv", "tconst",episodes["imdb_id"].implode()
).select([
        pl.col("tconst").alias("imdb_id").cast(pl.String),
        pl.col("ordering").cast(pl.Int32),
        pl.col("nconst").alias("actor_id").cast(pl.String),
        pl.col("category").cast(pl.String),
        pl.col("job").cast(pl.String),
        pl.col("characters").cast(pl.String)
    ])


df_episode_cast.write_parquet("./Data/silver/f_episode_cast.parquet")
df_episode_cast.write_csv("./Data/silver/f_episode_cast.csv")


df_actor_info = load_imdb("name.basics.tsv", "nconst",df_episode_cast["actor_id"].implode() 
).select([
        pl.col("nconst").alias("actor_id").cast(pl.String),
        pl.col("primaryName").alias("primary_name").cast(pl.String),
        pl.col("birthYear").alias("birth_year").cast(pl.Int16),
        pl.col("deathYear").alias("death_year").cast(pl.Int16),
        pl.col("primaryProfession").alias("primary_profession").cast(pl.String),
        pl.col("knownForTitles").alias("known_for_titles").cast(pl.String)
    ])
 

df_actor_info.write_parquet("./Data/silver/d_cast_info.parquet")
df_actor_info.write_csv("./Data/silver/d_cast_info.csv")


