# DccDocsHelper

The goal of this project is to eventually provide an AI assistant for all major DCC apps. The assistant will search and summarize any app's documentation and provide fast, accurate answers to user questions.

Right now it's in very early testing and only supports Gaffer 1.6.20.0. Follow the setup guide below and let me know how it works for you! I'm finding it surprisingly good in many ways, even at this stage.

# Setup

You'll need to install a few things first:

- Ollama (https://ollama.com)
- Python (I'm using 3.10, but any recent version should be fine - https://www.python.org)

You'll also need to install a few Python packages with _pip_:

`pip install ollama chromadb rich`

And you'll need an AI model or two. You can find the full list here: https://ollama.com/search

I'm still testing, but so far _llama3.1_ from Meta is a fine choice. I'm also liking the _Granite_ models from IBM.

To download a model, type:

`ollama pull <model_name>`

To run the assistant, first acquire this repo either by downloading and extracting the ZIP or by typing:

`git clone https://github.com/BrianHanke/DccDocsHelper.git`

Edit line 11 of _assistant.py_ to point to the model you want to use.

Finally, navigate to the repo's src folder:

`cd /path/to/DccDocsHelper/src`

And type:

`python assistant.py`

This will show a greeting with the currently active model and a prompt to type a question. Ask anything about Gaffer and after some thinking the model will respond.

It should refuse to answer any general questions and focus only on what is available in the Gaffer documentation.

# How it works

The assistant uses RAG (Retrieval-Augmented Generation) to expand an existing AI model's knowledge. I first sanitize the HTML documentation to remove markdown, menus, and anything else that isn't relevant, saving the results as plain text. I then use Chroma to create a database from those text files. Finally, the assistant takes user questions, feeds a prompt to the selected model and tells it to only look at the database and not to embellish or make things up.
