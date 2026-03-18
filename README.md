# 文化桥 | Cultural Bridge: Mandarin-Russian Proverb Translator

A cross-lingual NLP web app that analyzes Chinese proverbs and maps them to their closest Russian equivalents, revealing what cultural nuance is lost in translation.

![Screenshot placeholder](screenshot.png)

## Motivation

<!-- Mila: personalize this section -->
Growing up bilingual in Mandarin and Russian, I noticed that proverbs are where languages resist translation the most. A Chinese four-character idiom (成语) compresses centuries of philosophy into four syllables. When you translate it into Russian, something always breaks — sometimes the metaphor, sometimes the worldview, sometimes both.

This project makes that invisible loss visible. Each proverb is annotated with what a direct translation captures and what it quietly drops.

## Tech Stack

- **Python 3.10+**
- **Streamlit** — interactive web UI
- **OpenRouter API** — access to multiple LLMs (Kimi K2.5, DeepSeek, Llama 4 Maverick)
- **JSON dataset** — 100 hand-annotated proverbs with cultural commentary

## Features

- **Analyze** — Enter any Chinese proverb and receive: literal translation, cultural meaning, closest Russian equivalent, and analysis of semantic gaps
- **Browse** — Explore the full annotated dataset filtered by category (wisdom, family, perseverance, nature, social conduct, warning, humor, love)
- **Compare Models** — See how three different LLMs interpret the same proverb side-by-side, highlighting where AI cultural understanding diverges

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/milatn/proverb-translator.git
cd proverb-translator

# Install dependencies
pip install -r requirements.txt

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-key-here"

# Run the app
streamlit run app.py
```

For Streamlit Cloud deployment, add `OPENROUTER_API_KEY` to `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "your-key-here"
```

## Dataset Methodology

<!-- Mila: expand this section with your personal methodology -->
Each of the 100 proverbs was selected to represent a cross-section of Chinese proverbial language across 8 thematic categories. For every entry, the annotation includes:

1. **Literal translation** — word-by-word rendering
2. **Cultural meaning** — what a native speaker understands
3. **Russian equivalent** — the closest real Russian proverb (not a literal translation)
4. **What gets lost** — specific semantic and cultural gaps between the two versions
5. **Tone and context** — emotional register and historical origin

The Russian equivalents were chosen based on functional equivalence: which Russian saying would be used in the same conversational context, not which one translates most literally.

## Project Structure

```
proverb-translator/
├── app.py              # Main Streamlit app
├── data/
│   └── proverbs.json   # 100 annotated proverbs
├── llm_pipeline.py     # OpenRouter API wrapper
├── requirements.txt
└── README.md
```

## License

MIT
