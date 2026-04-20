import re
from collections import Counter
import pandas as pd
import nltk
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    pass

class LocalIntelligenceSynthesizer:
    def __init__(self):
        try:
            self.analyzer = SentimentIntensityAnalyzer()
            self.is_active = True
            # Base stopwords
            self.base_stops = ['stock', 'stocks', 'market', 'need', 'know', 'buy', 'investor', 'investors', 'today', 'company', 'shares', 'wall', 'street', 'year', 'announced', 'report', 'results', 'quarter', 'q1', 'q2', 'q3', 'q4']
        except:
            self.is_active = False

    def update_vibe_lexicon(self, sentiment_data: dict):
        """Bias VADER lexicon based on Market Fear & Greed levels."""
        if not self.is_active: return
        
        m_val = sentiment_data.get('market', {}).get('value', 50)
        c_val = sentiment_data.get('crypto', {}).get('value', 50)
        vibe = (m_val + c_val) / 2
        
        # Inject "Market Vibe" biased tokens
        if vibe < 30: # Extreme Fear
            self.analyzer.lexicon.update({'oversold': 2.5, 'support': 1.5, 'capitulation': -0.5, 'opportunity': 2.0})
        elif vibe > 70: # Extreme Greed
            self.analyzer.lexicon.update({'frothy': -1.5, 'bubble': -2.0, 'overextended': -1.5, 'exhausted': -1.0})
        else:
            # Reset / Neutral bias
            self.analyzer.lexicon.pop('oversold', None)
            self.analyzer.lexicon.pop('frothy', None)

    def discover_entities(self, text: str) -> list:
        """Lightweight Named Entity Recognition to find unmapped organizations."""
        if not self.is_active or not text: return []
        try:
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            chunks = nltk.ne_chunk(pos_tags)
            entities = []
            for chunk in chunks:
                if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                    name = " ".join([c[0] for c in chunk])
                    if len(name) > 2 and name.lower() not in self.base_stops:
                        entities.append(name)
            return list(set(entities))
        except:
            return []

    def synthesize_macro_overview(self, articles: list, sentences_count=5, group_paragraphs=False) -> list:
        if not self.is_active or not articles:
            return []
        
        all_text = ""
        seen = set()
        for a in articles:
            title = a.get('title', '').strip()
            summary = a.get('summary', '').strip()
            
            # Token Efficiency: Skip summary if it's just the title or too generic
            if summary.lower() in title.lower() or "yahoo" in summary.lower():
                content = title
            else:
                content = f"{title}. {summary}"
                
            if content not in seen:
                seen.add(content)
                all_text += content + ". "

        if len(all_text.strip()) < 50:
            return [a.get('title') for a in articles[:3]]

        try:
            parser = PlaintextParser.from_string(all_text, Tokenizer("english"))
            # V22.55: Dynamic sentence count adjustment to prevent LSA failure
            s_count = min(sentences_count, len(parser.document.sentences))
            if s_count < 1: return articles[:3] if isinstance(articles, list) else [] # Fallback to top news
            
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, sentences_count=s_count)
            s_list = [str(s) for s in summary]
            
            # NLP Fallback: if summarizer returns empty but text exists, join first few sentences
            if not s_list and all_text:
                sentences = re.split(r'\. |\? |\! ', all_text)
                s_list = [s.strip() for s in sentences if len(s.strip()) > 10][:5]

            if group_paragraphs:
                # Group every ~3 sentences into a paragraph
                paras = []
                for i in range(0, len(s_list), 3):
                    paras.append(" ".join(s_list[i:i+3]))
                return paras
            
            return s_list
        except Exception as e:
            print(f"[NLP ERR] {e}")
            return []

    def get_top_themes(self, articles: list, top_n=5) -> list:
        if not self.is_active or not articles:
            return []
            
        all_text_list = []
        seen = set()
        for a in articles:
            t = (a.get('title', '') + ". " + a.get('summary', '')).strip()
            if t not in seen:
                seen.add(t)
                all_text_list.append(t)
            
        if not all_text_list: return []
        all_text = " ".join(all_text_list)
            
        try:
            # Dynamic Stopwords: Identify "noise" specific to this batch (appears in >40% of docs)
            words = re.findall(r'\b\w{4,}\b', all_text.lower())
            doc_counts = Counter()
            for text in all_text_list:
                doc_words = set(re.findall(r'\b\w{4,}\b', text.lower()))
                for w in doc_words: doc_counts[w] += 1
            
            thresh = len(all_text_list) * 0.4
            dynamic_stops = [w for w, count in doc_counts.items() if count > thresh and count > 2]
            
            custom_stops = list(TfidfVectorizer(stop_words='english').get_stop_words()) + self.base_stops + dynamic_stops
            vectorizer = TfidfVectorizer(stop_words=custom_stops, max_features=40, ngram_range=(1,2))
            tfidf_matrix = vectorizer.fit_transform([all_text])
            feature_names = vectorizer.get_feature_names_out()
            top_keywords = sorted(zip(feature_names, tfidf_matrix.sum(axis=0).flat), key=lambda x: x[1], reverse=True)[:top_n]
            
            results = [kw.title() for kw, _ in top_keywords]
            
            # NER Integration: Inject a top discovered entity if relevant
            entities = self.discover_entities(all_text)
            if entities:
                results.insert(1, f"Focus: {entities[0]}")
            
            return results[:top_n]
        except Exception as e:
            print(f"[THEME ERR] {e}")
            return []
