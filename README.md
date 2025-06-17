by Quentin Chauvel and Aurianne Schwartz

first you need to install the dependancies with [uv](https://docs.astral.sh/uv/getting-started/installation/)

`uv sync`

Then you can create the dataset.

By default, it will download both generation 1 and 2.

You can limit it to a specific generation by passing 1 or 2 as an argument:

`python -m RAG --download-dataset` 

`python -m RAG --download-dataset 1` #only gen 1

then you create the vectorstore

`python -m RAG --create-vectorstore`

then you run the cli app:

`python -m RAG --app`

and then you run the streamlit application:

`python -m RAG --app_streamlit`

to run the evaluation:

`python -m RAG --eval`# RAG_Pokemon
