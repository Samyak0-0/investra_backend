import torch
from datetime import timedelta  
from transformers import BertTokenizer, BertForSequenceClassification
import utils.helpers.data_retrieval as data_fs_news_api
import numpy as np
from datetime import date
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class _finBERT:
    def __init__(self, model_name: str = 'yiyanghkust/finbert-tone',
                 max_length: int = 512, device: Optional[str] = None):
        """
        Initialize FinBERT sentiment analyzer.

        Args:
            model_name: HuggingFace model name
            max_length: Maximum sequence length for tokenization
            device: Device to run model on ('cuda', 'cpu', or None for auto-detect)
        """
        self.model_name = model_name
        self.max_length = max_length
        self.device = device or (
            'cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize model and tokenizer
        self._load_model()

        # Label mapping
        self.labels = {0: "positive", 1: "neutral", 2: "negative"}

    def _load_model(self):
        """Load the FinBERT model and tokenizer."""
        try:
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_name, num_labels=3
            )
            self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            logger.info(f"Model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def fetch_news_data(self, company: str, timestamp: date = None) -> List[str]:
        """
        Fetch news data for a given company.

        Args:
            company: Company name to fetch news for
            timestamp: Date to fetch news for (defaults to today)

        Returns:
            List of news text data
        """
        try:
            timestamp = timestamp or date.today()
            raw_data = data_fs_news_api.fetch_data(
                ticker=company, timestamp=timestamp-timedelta(days=14))
            return data_fs_news_api.return_titles(raw_data)
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []

    def preprocess_text(self, texts: List[str]) -> List[str]:
        """
        Preprocess text data (can be extended for more sophisticated preprocessing).

        Args:
            texts: List of text strings

        Returns:
            List of preprocessed text strings
        """
        processed = []
        for text in texts:
            if text and isinstance(text, str):
                # Remove extra whitespace and ensure reasonable length
                cleaned = ' '.join(text.split())
                if len(cleaned) > 10:  # Filter out very short texts
                    processed.append(cleaned)
        return processed

    def predict_sentiment_batch(self, texts: List[str], batch_size: int = 8) -> List[Dict]:
        """
        Predict sentiment for a batch of texts.

        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once

        Returns:
            List of dictionaries containing sentiment predictions
        """
        if not texts:
            logger.warning("No texts provided for sentiment analysis")
            return []

        results = []

        # Process in batches to handle memory efficiently
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_results = self._process_batch(batch_texts)
            results.extend(batch_results)

        return results

    def _process_batch(self, texts: List[str]) -> List[Dict]:
        """Process a single batch of texts."""
        try:
            # Tokenize batch
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

                # Get probabilities and predictions
                probs = torch.softmax(logits, dim=-1)
                predictions = torch.argmax(logits, dim=-1)

            # Convert to results
            results = []
            for i, (pred, prob) in enumerate(zip(predictions, probs)):
                pred_label = self.labels[pred.item()]
                confidence = prob[pred].item()

                results.append({
                    'text': texts[i],
                    'sentiment': pred_label,
                    'confidence': confidence,
                    'probabilities': {
                        'positive': prob[0].item(),
                        'neutral': prob[1].item(),
                        'negative': prob[2].item()
                    }
                })

            return results

        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            return [{'text': text, 'sentiment': 'neutral', 'confidence': 0.0,
                    'probabilities': {'positive': 0.0, 'neutral': 1.0, 'negative': 0.0}}
                    for text in texts]

    def analyze_company_sentiment(self, company: str, timestamp: date = None) -> Dict:
        """
        Analyze sentiment for a company's news data.

        Args:
            company: Company name
            timestamp: Date to analyze (defaults to today)

        Returns:
            Dictionary containing analysis results
        """
        # Fetch data
        texts = self.fetch_news_data(company, timestamp)

        if not texts:
            logger.warning(f"No news data found for {company}")
            return {
                'company': company,
                'date': timestamp or date.today(),
                'total_articles': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'overall_sentiment': 'neutral',
                'average_confidence': 0.0,
                'articles': []
            }

        # Preprocess
        processed_texts = self.preprocess_text(texts)

        # Analyze sentiment
        results = self.predict_sentiment_batch(processed_texts)

        # Calculate statistics
        sentiments = [r['sentiment'] for r in results]
        confidences = [r['confidence'] for r in results]

        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'neutral': sentiments.count('neutral'),
            'negative': sentiments.count('negative')
        }

        # Determine overall sentiment
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        avg_confidence = np.mean(confidences) if confidences else 0.0

        return {
            'company': company,
            'date': timestamp or date.today(),
            'total_articles': len(results),
            'sentiment_distribution': sentiment_counts,
            'overall_sentiment': overall_sentiment,
            'average_confidence': avg_confidence,
            'articles': results
        }

    def run(self, company: str = 'google', timestamp: date = None,
            show_details: bool = False) -> Dict:
        """
        Run sentiment analysis for a company.

        Args:
            company: Company name to analyze
            timestamp: Date to analyze (defaults to today)
            show_details: Whether to print detailed results

        Returns:
            Analysis results dictionary
        """
        logger.info(f"Starting sentiment analysis for {company}")

        results = self.analyze_company_sentiment(company, timestamp)

        if show_details:
            self._print_results(results)

        return results

    def _print_results(self, results: Dict):
        """Print formatted results."""
        print(f"\n{'='*50}")
        print(f"Sentiment Analysis Results for {results['company']}")
        print(f"Date: {results['date']}")
        print(f"{'='*50}")
        print(f"Total Articles: {results['total_articles']}")
        print(f"Overall Sentiment: {results['overall_sentiment'].upper()}")
        print(f"Average Confidence: {results['average_confidence']:.3f}")
        print(f"\nSentiment Distribution:")
        for sentiment, count in results['sentiment_distribution'].items():
            percentage = (count / results['total_articles']
                          * 100) if results['total_articles'] > 0 else 0
            print(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")

        if results['articles']:
            print(f"\nTop 5 Articles:")
            for i, article in enumerate(results['articles'][:5], 1):
                print(f"{i}. Sentiment: {article['sentiment'].upper()} "
                      f"(Confidence: {article['confidence']:.3f})")
                print(f"   Text: {article['text'][:100]}...")
