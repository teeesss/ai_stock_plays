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
                # Group every ~3-4 sentences into a structured topic
                paras = []
                transitions = [
                    "Intelligence Brief",
                    "Catalyst Dynamics",
                    "Structural Shifts",
                    "Sector Tailwinds"
                ]
                for i in range(0, len(s_list), 4):
                    chunk = s_list[i:i+4]
                    group = {
                        "transition": transitions[len(paras) % len(transitions)],
                        "items": []
                    }
                    for s in chunk:
                        s_str = s.strip()
                        if not s_str.endswith((".", "!", "?")): s_str += "."
                        
                        link = "#"
                        prefix = s_str[:30].lower()
                        for a in articles:
                            if prefix in a.get('title', '').lower() or prefix in a.get('summary', '').lower():
                                link = a.get('link', '#')
                                break
                                
                        group["items"].append({"text": s_str, "link": link})
                    paras.append(group)
                return paras
            
            return s_list
        except Exception as e:
            print(f"[NLP ERR] {e}")
            return []

    def synthesize_market_narrative(self, articles: list, vibe: str, scraped_lead: str = None) -> tuple:
        """Constructs a dense, cohesive institutional paragraph. Returns (narrative, used_links)."""
        used_links = set()
        
        # 1. Determine Primary Anchor
        if scraped_lead and len(scraped_lead) > 50:
            lead_para = scraped_lead.strip()
            # If we have a scraped lead, we don't have its specific link here, 
            # but we can try to filter out articles that overlap too much.
            anchor_words = set(re.findall(r'\b\w{4,}\b', lead_para.lower()))
        elif articles:
            anchor = articles[0]
            used_links.add(anchor.get('link'))
            lead_para = anchor.get('summary', '').strip()
            if len(lead_para) < 40: lead_para = anchor.get('raw_title', '').strip()
            anchor_words = set(re.findall(r'\b\w{4,}\b', lead_para.lower()))
        else:
            return f"The market maintains a {vibe} posture. No primary catalysts identified.", set()

        if not lead_para.endswith((".", "!", "?")): lead_para += "."
        
        # 2. Extract Top Themes
        themes = self.get_top_themes(articles, top_n=2)
        top_theme = themes[0] if themes else "Sector Rotation"
        
        # 3. Extract Secondary Insights (avoiding stutter)
        dense_points_with_meta = self.synthesize_macro_overview_with_meta(articles, sentences_count=1)
        
        dense_text = ""
        for pt, link in dense_points_with_meta:
            if not pt: continue
            
            # Stutter check against the lead
            pt_words = set(re.findall(r'\b\w{4,}\b', pt.lower()))
            overlap = len(pt_words & anchor_words) / (len(pt_words) + 1)
            if overlap > 0.4: continue # Tighter threshold for scraped leads
            
            dense_text = pt
            if link: used_links.add(link)
            break

        # 4. Final Institutional Construction
        narrative = f"{lead_para}"
        if dense_text:
            if not dense_text.endswith((".", "!", "?")): dense_text += "."
            narrative += f" {dense_text}"
            
        narrative += f" This reinforces <strong>{top_theme}</strong> as the primary focal point during this {vibe} cycle."

        return narrative, used_links

    def synthesize_macro_overview_with_meta(self, articles: list, sentences_count=2) -> list:
        """Helper to get sentences with their source links."""
        try:
            from sumy.parsers.plaintext import PlaintextParser
            from sumy.nlp.tokenizers import Tokenizer
            from sumy.summarizers.lsa import LsaSummarizer
            
            # Map sentences back to articles
            doc_text = ""
            link_map = {}
            for a in articles:
                text = a.get('summary', a.get('raw_title', ''))
                doc_text += text + " "
                # Very crude mapping
                for sentence in re.split(r'(?<=[.!?])\s+', text):
                    if len(sentence) > 20:
                        link_map[sentence.strip()] = a.get('link')
            
            parser = PlaintextParser.from_string(doc_text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, sentences_count)
            
            results = []
            for s in summary:
                s_text = str(s).strip()
                results.append((s_text, link_map.get(s_text)))
            return results
        except:
            return [(a.get('summary', a.get('raw_title', '')), a.get('link')) for a in articles[:sentences_count]]

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

    def rank_news_relevance(self, articles: list, top_n=15) -> list:
        """Score and rank headlines by information density and relevance with fuzzy deduplication."""
        if not self.is_active or not articles: return articles[:top_n]
        
        try:
            seen_tokens = []
            def is_duplicate(text):
                tokens = set(re.findall(r'\b\w{4,}\b', text.lower()))
                for st in seen_tokens:
                    overlap = len(tokens & st) / (len(tokens | st) + 1)
                    if overlap > 0.6: return True
                seen_tokens.append(tokens)
                return False

            # Informational Density Score (Length + Punctuation + Keywords)
            scored = []
            for a in articles:
                title = a.get('title', '')
                summary = a.get('summary', '')
                text = (title + " " + summary).lower()
                
                # Deduplication check
                if is_duplicate(title): continue

                length_score = min(len(text) / 200.0, 1.0)
                
                # Check for "High Alpha" keywords
                alpha_words = ['breakthrough', 'record', 'surge', 'monopoly', 'pivot', 'exclusive', 'bottleneck', 'acceleration']
                alpha_score = sum(1.5 for w in alpha_words if w in text)
                
                # VADER Sentiment Intensity
                sentiment = self.analyzer.polarity_scores(text)
                tone_score = abs(sentiment['compound']) * 2.0
                
                final_score = length_score + alpha_score + tone_score
                scored.append((a, final_score))
            
            # Sort by score descending
            ranked = [s[0] for s in sorted(scored, key=lambda x: x[1], reverse=True)]
            return ranked[:top_n]
        except:
            return articles[:top_n]
