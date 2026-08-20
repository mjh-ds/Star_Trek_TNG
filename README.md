# Star Trek TNG: Data cleaning and organization

## Data Used

- Raw Data: https://github.com/RMHogervorst/TNG/tree/master/raw-data
- Supplimental data: https://www.kaggle.com/datasets/ashirwadsangwan/imdb-dataset

## Data Generated

- **d_episodes**: CSV and parquet files containing episode information (e.g. Season, episide, title, imdb rating, ...)
- **f_lines**: CSV and parquet files containing actor lines and dialog by episode, act, and scene.
- **f_lines_sentimate**: CSV and parquet files containing the sentimate and emotion classification of actor lines and dialog from **f_lines**.
- **f_episode_cast**: CSV and parquet files containing a listing of actors, cast, directors... for each episode. Mostly just a cleaned and filtered version of the supplimental data 'title.principals.tsv'.
- **d_cast_info**: CSV and parquet files containing a listing of actors and their information (e.g. name, birth year). Mostly just a cleaned and filtered version of the supplimental data 'name.basics.tsv'.

## Data Dictionaries

### d_episodes

| Column | Date Type | Source data | Description |
|--------------|-----------|-----------------|--------------------------------|
| season_number | Int8 | Raw Data | Season number (1-7) |
| episode_number | Int8 | Raw Data | episode number |
| episode_title | String | Raw Data | title of episode |
| production_number | String | Raw Data | Production number of the episode |
| imdb_id | String | Raw Data | IMDB episode id |
| imdb_rating | Float32 | Raw Data | IMDB rating of episode (approx 2015 rating) |
| setnames | String | Raw Data | List of the sets used in the episode |
| characters | String | Raw Data | List of characters in the episode |
| primary_title | String | Supplimental:title.basics.tsv | title of episode |
| original_title | String | Supplimental:title.basics.tsv | title of episode |
| start_year | Int16 | Supplimental:title.basics.tsv | Year episode was aired |
| runtime_minutes | Int16 | Supplimental:title.basics.tsv | runtime of episode |
| imdb_rating_2026 | Float32 | Supplimental:title.ratings.tsv | Updated IMDB rating |
| num_votes_2026 | Int32 | Supplimental:title.ratings.tsv | Number of votes associated with '*imdb_rating_2026*' |

### f_lines

| Column             | Date Type | Source data | Description |
|--------------------|-----------|-------------|-------------|
| line_id            | UInt32    | Raw Data    |             |
| imdb_id            | String    | Raw Data    |             |
| act                | Int16     | Raw Data    |             |
| scene_number       | Int16     | Raw Data    |             |
| scene_details      | String    | Raw Data    |             |
| part_number        | Int16     | Raw Data    |             |
| type               | String    | Raw Data    |             |
| who                | String    | Raw Data    |             |
| text               | String    | Raw Data    |             |
| speech_description | Boolean   | Raw Data    |             |

### f_lines_sentiment

### f_episode_cast

### d_cast_info