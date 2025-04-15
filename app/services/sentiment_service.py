"""
Service for sentiment analysis of social media comments.
"""
import re
import logging
import pickle
import emoji
import numpy as np
from datetime import datetime
from os import path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from app.extensions import db, cache
from app.models import SocialPagePostComment, SocialPagePost

logger = logging.getLogger(__name__)

class SentimentService:
    """Service for sentiment analysis of text content."""
    
    # Dictionary of slang words and their translations
    SOCIAL_SLANG = {
        'top': 'bom',
        'massa': 'bom',
        'daora': 'bom',
        'foda': 'ruim',
        'mds': 'meu deus',
        'vlw': 'valeu',
        'vc': 'você',
        'blz': 'beleza',
        'kkkk': 'risos',
        'hahaha': 'risos',
        'rsrs': 'risos',
        'pqp': 'puxa',
        'mt': 'muito',
        'cmg': 'comigo',
        'pra': 'para',
        'pro': 'para o',
        'ñ': 'não',
        'n': 'não',
        'ss': 'sim',
        'tb': 'também',
        'tbm': 'também',
        'td': 'tudo',
        'q': 'que',
        'aq': 'aqui',
        'cmg': 'comigo',
        'msm': 'mesmo',
        'vdd': 'verdade',
        'mto': 'muito',
        'dms': 'demais',
        'pfv': 'por favor',
        'obg': 'obrigado',
        'abs': 'abraços',
        'flw': 'falou',
        'sdds': 'saudades'
    }
    
    # Dictionary mapping emojis to sentiment score adjustments
    EMOJI_SENTIMENTS = {
        '😀': 0.3,  # Grinning face
        '😁': 0.3,  # Grinning face with smiling eyes
        '😂': 0.5,  # Face with tears of joy
        '🤣': 0.5,  # Rolling on the floor laughing
        '😊': 0.4,  # Smiling face with smiling eyes
        '😍': 0.7,  # Smiling face with heart-eyes
        '🥰': 0.6,  # Smiling face with hearts
        '👍': 0.3,  # Thumbs up
        '❤️': 0.5,  # Red heart
        '💯': 0.4,  # Hundred points
        '🙏': 0.2,  # Folded hands
        '😢': -0.3,  # Crying face
        '😭': -0.5,  # Loudly crying face
        '😠': -0.4,  # Angry face
        '😡': -0.6,  # Pouting face
        '👎': -0.3,  # Thumbs down
        '💔': -0.5,  # Broken heart
        '🤮': -0.7,  # Face vomiting
        '😒': -0.3,  # Unamused face
        '🙄': -0.2,  # Face with rolling eyes
        '😑': -0.1,  # Expressionless face
        '😐': -0.1,  # Neutral face
        '😕': -0.2   # Confused face
    }
    
    # Load most common emojis in Portuguese social media
    COMMON_EMOJIS = list(EMOJI_SENTIMENTS.keys())
    
    @staticmethod
    def _normalize_text(text, remove_emojis=False):
        """
        Normalize text content by removing special characters, 
        converting slang and standardizing format.
        
        Args:
            text: Text to normalize
            remove_emojis: Whether to remove emojis or keep them
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Extract emojis before processing
        emojis_found = []
        if not remove_emojis:
            for char in text:
                if char in emoji.EMOJI_DATA:
                    emojis_found.append(char)
        
        # Replace social media slang with standard words
        words = text.split()
        for i, word in enumerate(words):
            if word in SentimentService.SOCIAL_SLANG:
                words[i] = SentimentService.SOCIAL_SLANG[word]
        
        # Rejoin the text
        text = ' '.join(words)
        
        # Remove special characters and keep only letters, numbers and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Add emojis back if needed
        if not remove_emojis and emojis_found:
            text += ' ' + ' '.join(emojis_found)
            
        return text
    
    @staticmethod
    def preprocess_text(text):
        """
        Preprocess text for sentiment analysis by applying normalization,
        tokenization, stopword removal and stemming.
        
        Args:
            text: Input text
            
        Returns:
            str: Preprocessed text
        """
        try:
            if not text:
                return ""
                
            # Normalize text (keep emojis for score adjustment later)
            normalized_text = SentimentService._normalize_text(text, remove_emojis=False)
            
            # Stopwords and stemming are only applied for model training
            # For inference, we keep more of the original text
            
            # Extract emojis for later score adjustment
            emojis_found = []
            for char in text:
                if char in emoji.EMOJI_DATA and char in SentimentService.EMOJI_SENTIMENTS:
                    emojis_found.append(char)
            
            return {
                'processed_text': normalized_text,
                'emojis': emojis_found
            }
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return {'processed_text': text, 'emojis': []}
    
    @staticmethod
    def _extract_emojis(text):
        """Extract emojis from text."""
        return [c for c in text if c in emoji.EMOJI_DATA]
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Analyze sentiment of text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            dict: Sentiment analysis result containing sentiment and score
        """
        try:
            if not text:
                return {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'is_critical': False
                }
            
            # Preprocess the text
            processed = SentimentService.preprocess_text(text)
            processed_text = processed['processed_text']
            emojis = processed['emojis']
            
            # This is where we'd normally call our trained model
            # For now we'll use a rule-based approach with a lexicon
            
            # Lexicons of words with sentiment scores
            positive_words = {
                'bom': 0.5, 'ótimo': 0.7, 'excelente': 0.8, 'maravilhoso': 0.9, 'perfeito': 0.9,
                'legal': 0.5, 'bacana': 0.5, 'incrível': 0.8, 'fantástico': 0.8, 'sensacional': 0.8,
                'gostei': 0.6, 'amei': 0.8, 'adorei': 0.8, 'melhor': 0.6, 'top': 0.6,
                'parabéns': 0.7, 'recomendo': 0.6, 'valeu': 0.5, 'obrigado': 0.3, 'belo': 0.5,
                'show': 0.6, 'feliz': 0.6, 'satisfeito': 0.5, 'contente': 0.5, 'bora': 0.3,
                'concordo': 0.3, 'sensação': 0.3, 'bem': 0.3, 'sucesso': 0.6, 'bonito': 0.4,
                'fácil': 0.3, 'grato': 0.5, 'confiança': 0.4, 'útil': 0.4, 'tranquilo': 0.3,
                'boa': 0.5, 'positivo': 0.5, 'favorável': 0.4, 'vantagem': 0.4, 'benefício': 0.4,
                'vitória': 0.6, 'ganhar': 0.5, 'vencer': 0.5, 'aprovar': 0.4, 'sim': 0.3,
                'alegria': 0.6, 'felicidade': 0.7, 'amor': 0.7, 'paixão': 0.6, 'entusiasmo': 0.5
            }
            
            negative_words = {
                'ruim': -0.5, 'péssimo': -0.7, 'horrível': -0.8, 'terrível': -0.8, 'pior': -0.7,
                'detestei': -0.8, 'odiei': -0.8, 'decepcionado': -0.6, 'decepção': -0.6, 'triste': -0.5,
                'chato': -0.5, 'fraco': -0.4, 'insatisfeito': -0.6, 'problemas': -0.4, 'problema': -0.4,
                'reclamar': -0.5, 'reclamação': -0.5, 'erro': -0.4, 'falha': -0.5, 'errado': -0.5,
                'difícil': -0.3, 'complicado': -0.4, 'dificuldade': -0.4, 'mal': -0.5, 'mau': -0.5,
                'raiva': -0.6, 'ódio': -0.8, 'irritado': -0.6, 'frustrado': -0.6, 'triste': -0.5,
                'discordo': -0.3, 'negativo': -0.5, 'desfavorável': -0.4, 'desvantagem': -0.4, 'prejuízo': -0.5,
                'perder': -0.5, 'perda': -0.5, 'culpa': -0.5, 'falhar': -0.5, 'quebrar': -0.4,
                'lento': -0.3, 'caro': -0.4, 'defeito': -0.5, 'não': -0.2, 'nunca': -0.3,
                'feio': -0.4, 'sujo': -0.4, 'desagradável': -0.5, 'inútil': -0.6, 'enganar': -0.6
            }
            
            # Calculate score based on words
            words = processed_text.split()
            word_score_sum = 0
            word_score_count = 0
            
            for word in words:
                if word in positive_words:
                    word_score_sum += positive_words[word]
                    word_score_count += 1
                elif word in negative_words:
                    word_score_sum += negative_words[word]
                    word_score_count += 1
            
            # Calculate emoji score
            emoji_score_sum = 0
            for emoji_char in emojis:
                if emoji_char in SentimentService.EMOJI_SENTIMENTS:
                    emoji_score_sum += SentimentService.EMOJI_SENTIMENTS[emoji_char]
            
            # Calculate final score
            if word_score_count > 0:
                base_score = word_score_sum / word_score_count
            else:
                base_score = 0
                
            # Add emoji influence (with a weight)
            emoji_weight = 0.3  # How much emojis influence the final score
            if emojis:
                emoji_score = emoji_score_sum / len(emojis)
                final_score = (1 - emoji_weight) * base_score + emoji_weight * emoji_score
            else:
                final_score = base_score
                
            # Clamp the score to [-1, 1]
            final_score = max(-1.0, min(1.0, final_score))
            
            # Determine sentiment classification
            if final_score > 0.1:
                sentiment = 'positive'
            elif final_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            # Check if it's a critical comment
            is_critical = final_score < -0.5  # Strong negative sentiment
            
            # Add extra checks for critical comments
            critical_phrases = [
                'não funciona', 'não gostei', 'problema', 'erro', 'bug', 'travando',
                'cancelar', 'cancelei', 'decepção total', 'péssimo', 'horrível',
                'pior', 'nunca mais', 'desinstalar'
            ]
            
            if not is_critical:
                for phrase in critical_phrases:
                    if phrase in processed_text:
                        is_critical = True
                        break
            
            return {
                'sentiment': sentiment,
                'score': round(final_score, 2),
                'is_critical': is_critical
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'is_critical': False,
                'error': str(e)
            }
    
    @staticmethod
    def fetch_comments(platform, post_id, access_token):
        """
        Fetch comments from social media platforms.
        
        Args:
            platform: Social media platform
            post_id: ID of the post
            access_token: Access token for the API
            
        Returns:
            list: Comments data
        """
        if platform == 'instagram':
            return SentimentService._fetch_instagram_comments(post_id, access_token)
        elif platform == 'facebook':
            return SentimentService._fetch_facebook_comments(post_id, access_token)
        elif platform == 'tiktok':
            return SentimentService._fetch_tiktok_comments(post_id, access_token)
        else:
            logger.error(f"Unsupported platform: {platform}")
            return []
    
    @staticmethod
    def _fetch_instagram_comments(post_id, access_token):
        """Fetch comments from Instagram."""
        import requests
        
        try:
            # Instagram API uses the Facebook Graph API
            url = f"https://graph.facebook.com/v16.0/{post_id}/comments"
            params = {
                'access_token': access_token,
                'fields': 'id,text,like_count,timestamp,username,user{name,picture}',
                'limit': 50  # Fetch up to 50 comments
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            comments_data = response.json().get('data', [])
            
            # Process the comments
            comments = []
            for comment in comments_data:
                # Get user data
                user = comment.get('user', {})
                username = comment.get('username')
                display_name = user.get('name', username)
                
                # Get profile picture
                profile_pic = None
                if 'picture' in user:
                    profile_pic = user.get('picture', {}).get('data', {}).get('url')
                
                # Parse timestamp
                timestamp = comment.get('timestamp')
                posted_at = None
                if timestamp:
                    try:
                        posted_at = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S+0000')
                    except ValueError:
                        logger.warning(f"Could not parse timestamp: {timestamp}")
                
                # Analyze sentiment
                sentiment_data = SentimentService.analyze_sentiment(comment.get('text', ''))
                
                comments.append({
                    'platform': 'instagram',
                    'comment_id': comment.get('id'),
                    'author_username': username,
                    'author_display_name': display_name,
                    'author_picture': profile_pic,
                    'content': comment.get('text', ''),
                    'posted_at': posted_at,
                    'likes_count': comment.get('like_count', 0),
                    'replied_to_id': None,  # Instagram API doesn't provide parent comment ID in this endpoint
                    'sentiment': sentiment_data.get('sentiment'),
                    'sentiment_score': sentiment_data.get('score'),
                    'is_critical': sentiment_data.get('is_critical')
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching Instagram comments: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_facebook_comments(post_id, access_token):
        """Fetch comments from Facebook."""
        import requests
        
        try:
            url = f"https://graph.facebook.com/v16.0/{post_id}/comments"
            params = {
                'access_token': access_token,
                'fields': 'id,message,like_count,created_time,from{id,name,picture}',
                'limit': 50
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            comments_data = response.json().get('data', [])
            
            # Process the comments
            comments = []
            for comment in comments_data:
                # Get user data
                user = comment.get('from', {})
                
                # Get profile picture
                profile_pic = None
                if 'picture' in user:
                    profile_pic = user.get('picture', {}).get('data', {}).get('url')
                
                # Parse timestamp
                timestamp = comment.get('created_time')
                posted_at = None
                if timestamp:
                    try:
                        posted_at = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S+0000')
                    except ValueError:
                        logger.warning(f"Could not parse timestamp: {timestamp}")
                
                # Analyze sentiment
                sentiment_data = SentimentService.analyze_sentiment(comment.get('message', ''))
                
                comments.append({
                    'platform': 'facebook',
                    'comment_id': comment.get('id'),
                    'author_username': user.get('id'),
                    'author_display_name': user.get('name'),
                    'author_picture': profile_pic,
                    'content': comment.get('message', ''),
                    'posted_at': posted_at,
                    'likes_count': comment.get('like_count', 0),
                    'replied_to_id': None,
                    'sentiment': sentiment_data.get('sentiment'),
                    'sentiment_score': sentiment_data.get('score'),
                    'is_critical': sentiment_data.get('is_critical')
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching Facebook comments: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_tiktok_comments(post_id, access_token):
        """Fetch comments from TikTok."""
        import requests
        
        try:
            url = f"https://open.tiktokapis.com/v2/video/comment/list/"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            params = {
                "fields": "text,create_time,like_count,reply_comment_total,reply_to_comment_id,user",
                "video_id": post_id,
                "max_count": 50
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            comments_data = response.json().get('data', {}).get('comments', [])
            
            # Process the comments
            comments = []
            for comment in comments_data:
                # Get user data
                user = comment.get('user', {})
                
                # Parse timestamp
                timestamp = comment.get('create_time')
                posted_at = None
                if timestamp:
                    try:
                        posted_at = datetime.fromtimestamp(int(timestamp))
                    except (ValueError, TypeError):
                        logger.warning(f"Could not parse timestamp: {timestamp}")
                
                # Analyze sentiment
                sentiment_data = SentimentService.analyze_sentiment(comment.get('text', ''))
                
                comments.append({
                    'platform': 'tiktok',
                    'comment_id': comment.get('id'),
                    'author_username': user.get('username'),
                    'author_display_name': user.get('display_name'),
                    'author_picture': user.get('avatar_url'),
                    'content': comment.get('text', ''),
                    'posted_at': posted_at,
                    'likes_count': comment.get('like_count', 0),
                    'replied_to_id': comment.get('reply_to_comment_id'),
                    'sentiment': sentiment_data.get('sentiment'),
                    'sentiment_score': sentiment_data.get('score'),
                    'is_critical': sentiment_data.get('is_critical')
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching TikTok comments: {str(e)}")
            return []
    
    @staticmethod
    def save_comments(post, comments_data):
        """
        Save comments data to the database.
        
        Args:
            post: SocialPost object
            comments_data: List of comment data from API
            
        Returns:
            int: Number of comments saved
        """
        try:
            count = 0
            
            for comment_data in comments_data:
                # Check if comment already exists
                existing = SocialPagePostComment.query.filter_by(
                    platform=comment_data['platform'],
                    comment_id=comment_data['comment_id']
                ).first()
                
                if existing:
                    # Update existing comment
                    existing.likes_count = comment_data['likes_count']
                    existing.sentiment = comment_data['sentiment']
                    existing.sentiment_score = comment_data['sentiment_score']
                    existing.is_critical = comment_data['is_critical']
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new comment
                    comment = SocialPagePostComment(
                        post_id=post.id,
                        platform=comment_data['platform'],
                        comment_id=comment_data['comment_id'],
                        author_username=comment_data['author_username'],
                        author_display_name=comment_data['author_display_name'],
                        author_picture=comment_data['author_picture'],
                        content=comment_data['content'],
                        posted_at=comment_data['posted_at'],
                        likes_count=comment_data['likes_count'],
                        replied_to_id=comment_data['replied_to_id'],
                        sentiment=comment_data['sentiment'],
                        sentiment_score=comment_data['sentiment_score'],
                        is_critical=comment_data['is_critical']
                    )
                    db.session.add(comment)
                    count += 1
            
            # Update post comments count
            post.comments_count = SocialPagePostComment.query.filter_by(post_id=post.id).count()
            post.updated_at = datetime.utcnow()
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving comments: {str(e)}")
            return 0
    
    @staticmethod
    @cache.memoize(timeout=300)  # Cache for 5 minutes
    def get_post_sentiment_analysis(post_id):
        """
        Get sentiment analysis for a specific post.
        
        Args:
            post_id: ID of the post
            
        Returns:
            dict: Sentiment analysis data
        """
        try:
            post = SocialPagePost.query.get(post_id)
            if not post:
                return {
                    'error': 'Post not found',
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Get comments for the post
            comments = SocialPagePostComment.query.filter_by(post_id=post.id).all()
            
            if not comments:
                return {
                    'post_id': post_id,
                    'platform': post.platform,
                    'comments_count': 0,
                    'sentiment_distribution': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'critical_comments': [],
                    'top_positive': [],
                    'top_negative': [],
                    'average_sentiment_score': 0,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Calculate sentiment distribution
            sentiment_counts = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            
            total_score = 0
            
            for comment in comments:
                sentiment = comment.sentiment or 'neutral'
                sentiment_counts[sentiment] += 1
                total_score += comment.sentiment_score or 0
            
            # Calculate average sentiment score
            avg_score = total_score / len(comments) if comments else 0
            
            # Get critical comments
            critical_comments = [c for c in comments if c.is_critical]
            
            # Get top positive and negative comments
            positive_comments = [c for c in comments if c.sentiment == 'positive']
            negative_comments = [c for c in comments if c.sentiment == 'negative']
            
            # Sort by sentiment score and likes
            positive_comments.sort(key=lambda x: (x.sentiment_score or 0) + (x.likes_count or 0) * 0.01, reverse=True)
            negative_comments.sort(key=lambda x: (abs(x.sentiment_score or 0) + (x.likes_count or 0) * 0.01), reverse=True)
            
            # Limit to top 5
            top_positive = positive_comments[:5]
            top_negative = negative_comments[:5]
            
            # Format the comments
            def format_comment(comment):
                return {
                    'id': comment.id,
                    'comment_id': comment.comment_id,
                    'author_username': comment.author_username,
                    'author_display_name': comment.author_display_name,
                    'author_picture': comment.author_picture,
                    'content': comment.content,
                    'posted_at': comment.posted_at.isoformat() if comment.posted_at else None,
                    'likes_count': comment.likes_count,
                    'sentiment': comment.sentiment,
                    'sentiment_score': comment.sentiment_score,
                    'is_critical': comment.is_critical
                }
            
            formatted_critical = [format_comment(c) for c in critical_comments]
            formatted_positive = [format_comment(c) for c in top_positive]
            formatted_negative = [format_comment(c) for c in top_negative]
            
            # Calculate percentages
            total_comments = len(comments)
            sentiment_percentages = {
                'positive': round((sentiment_counts['positive'] / total_comments) * 100, 2) if total_comments else 0,
                'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 2) if total_comments else 0,
                'negative': round((sentiment_counts['negative'] / total_comments) * 100, 2) if total_comments else 0
            }
            
            return {
                'post_id': post_id,
                'platform': post.platform,
                'comments_count': total_comments,
                'sentiment_distribution': {
                    'counts': sentiment_counts,
                    'percentages': sentiment_percentages
                },
                'critical_comments': formatted_critical,
                'top_positive': formatted_positive,
                'top_negative': formatted_negative,
                'average_sentiment_score': round(avg_score, 2),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting post sentiment analysis: {str(e)}")
            return {
                'error': f"Failed to get sentiment analysis: {str(e)}",
                'last_updated': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    @cache.memoize(timeout=600)  # Cache for 10 minutes
    def get_social_page_sentiment_analysis(social_page_id, time_range=30):
        """
        Get aggregated sentiment analysis for an social_page across all posts.
        
        Args:
            social_page_id: ID of the social_page
            time_range: Number of days to analyze (default: 30)
            
        Returns:
            dict: Sentiment analysis data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range)
            
            # Get all posts for the social_page
            posts = SocialPagePost.query.filter(
                SocialPagePost.social_page_id == social_page_id,
                SocialPagePost.posted_at >= start_date
            ).all()
            
            if not posts:
                return {
                    'social_page_id': social_page_id,
                    'posts_count': 0,
                    'comments_count': 0,
                    'sentiment_distribution': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'sentiment_trend': [],
                    'critical_comments': [],
                    'average_sentiment_score': 0,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Get all comments for the posts
            post_ids = [p.id for p in posts]
            comments = SocialPagePostComment.query.filter(
                SocialPagePostComment.post_id.in_(post_ids)
            ).all()
            
            if not comments:
                return {
                    'social_page_id': social_page_id,
                    'posts_count': len(posts),
                    'comments_count': 0,
                    'sentiment_distribution': {
                        'positive': 0,
                        'neutral': 0,
                        'negative': 0
                    },
                    'sentiment_trend': [],
                    'critical_comments': [],
                    'average_sentiment_score': 0,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Calculate sentiment distribution
            sentiment_counts = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            
            total_score = 0
            
            for comment in comments:
                sentiment = comment.sentiment or 'neutral'
                sentiment_counts[sentiment] += 1
                total_score += comment.sentiment_score or 0
            
            # Calculate average sentiment score
            avg_score = total_score / len(comments) if comments else 0
            
            # Get critical comments
            critical_comments = [c for c in comments if c.is_critical]
            
            # Sort critical comments by recency and limit to top 10
            critical_comments.sort(key=lambda x: x.posted_at or datetime.min, reverse=True)
            critical_comments = critical_comments[:10]
            
            # Format critical comments
            formatted_critical = []
            for comment in critical_comments:
                # Get post info
                post = next((p for p in posts if p.id == comment.post_id), None)
                
                formatted_critical.append({
                    'id': comment.id,
                    'comment_id': comment.comment_id,
                    'post_id': comment.post_id,
                    'post_url': post.post_url if post else None,
                    'author_username': comment.author_username,
                    'author_display_name': comment.author_display_name,
                    'author_picture': comment.author_picture,
                    'content': comment.content,
                    'posted_at': comment.posted_at.isoformat() if comment.posted_at else None,
                    'likes_count': comment.likes_count,
                    'sentiment': comment.sentiment,
                    'sentiment_score': comment.sentiment_score
                })
            
            # Calculate sentiment trend over time
            # Group comments by day
            comments_by_day = {}
            for comment in comments:
                if not comment.posted_at:
                    continue
                
                day = comment.posted_at.date()
                if day not in comments_by_day:
                    comments_by_day[day] = []
                
                comments_by_day[day].append(comment)
            
            # Calculate daily sentiment scores
            sentiment_trend = []
            for day, day_comments in sorted(comments_by_day.items()):
                day_score = sum(c.sentiment_score or 0 for c in day_comments) / len(day_comments)
                
                day_sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
                for c in day_comments:
                    sentiment = c.sentiment or 'neutral'
                    day_sentiments[sentiment] += 1
                
                sentiment_trend.append({
                    'date': day.isoformat(),
                    'average_score': round(day_score, 2),
                    'comments_count': len(day_comments),
                    'sentiment_counts': day_sentiments
                })
            
            # Calculate percentages
            total_comments = len(comments)
            sentiment_percentages = {
                'positive': round((sentiment_counts['positive'] / total_comments) * 100, 2) if total_comments else 0,
                'neutral': round((sentiment_counts['neutral'] / total_comments) * 100, 2) if total_comments else 0,
                'negative': round((sentiment_counts['negative'] / total_comments) * 100, 2) if total_comments else 0
            }
            
            return {
                'social_page_id': social_page_id,
                'posts_count': len(posts),
                'comments_count': total_comments,
                'sentiment_distribution': {
                    'counts': sentiment_counts,
                    'percentages': sentiment_percentages
                },
                'sentiment_trend': sentiment_trend,
                'critical_comments': formatted_critical,
                'average_sentiment_score': round(avg_score, 2),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting social_page sentiment analysis: {str(e)}")
            return {
                'error': f"Failed to get sentiment analysis: {str(e)}",
                'last_updated': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def analyze_comment_batch(comments):
        """
        Analyze a batch of comments and return sentiment results.
        
        Args:
            comments: List of comment text to analyze
            
        Returns:
            list: Sentiment analysis results for each comment
        """
        results = []
        
        for comment in comments:
            sentiment_data = SentimentService.analyze_sentiment(comment)
            results.append(sentiment_data)
            
        return results