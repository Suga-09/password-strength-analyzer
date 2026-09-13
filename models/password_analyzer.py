import re
import math
import string
from collections import Counter

class PasswordAnalyzer:
    def __init__(self):
        # Load common password patterns
        self.common_patterns = [
            'password', '123456', 'qwerty', 'letmein', 'admin',
            'welcome', 'monkey', 'dragon', 'master', 'hello'
        ]
        
        # Character sets for entropy calculation
        self.char_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'special': string.punctuation
        }
        
        # Load dictionary words (in production, load from file)
        self.dictionary = self.load_dictionary()
    
    def analyze_password(self, password):
        """
        Comprehensive password analysis
        """
        result = {
            'password': password,
            'length': len(password),
            'strength': 'weak',
            'score': 0,
            'entropy': 0,
            'feedback': [],
            'metrics': {}
        }
        
        # Calculate all metrics
        result['metrics'] = self.get_metrics(password)
        result['entropy'] = self.calculate_entropy(password)
        result['score'] = self.calculate_score(password)
        result['strength'] = self.get_strength_label(result['score'])
        result['feedback'] = self.get_feedback(password, result)
        
        return result
    
    def get_metrics(self, password):
        """
        Extract detailed metrics from password
        """
        metrics = {
            'length': len(password),
            'lowercase_count': sum(1 for c in password if c.islower()),
            'uppercase_count': sum(1 for c in password if c.isupper()),
            'digit_count': sum(1 for c in password if c.isdigit()),
            'special_count': sum(1 for c in password if c in string.punctuation),
            'unique_characters': len(set(password)),
            'has_lowercase': any(c.islower() for c in password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(c in string.punctuation for c in password),
            'character_set_size': self.get_char_set_size(password)
        }
        
        return metrics
    
    def get_char_set_size(self, password):
        """
        Calculate the size of character set used
        """
        used_chars = set()
        if any(c.islower() for c in password):
            used_chars.update(string.ascii_lowercase)
        if any(c.isupper() for c in password):
            used_chars.update(string.ascii_uppercase)
        if any(c.isdigit() for c in password):
            used_chars.update(string.digits)
        if any(c in string.punctuation for c in password):
            used_chars.update(string.punctuation)
        return len(used_chars)
    
    def calculate_entropy(self, password):
        """
        Calculate Shannon entropy of password
        """
        if not password:
            return 0
        
        char_set_size = self.get_char_set_size(password)
        if char_set_size == 0:
            return 0
        
        # Formula: entropy = length * log2(char_set_size)
        entropy = len(password) * math.log2(char_set_size)
        return round(entropy, 2)
    
    def calculate_score(self, password):
        """
        Calculate strength score from 0-100
        """
        score = 0
        
        # Length scoring (max 25 points)
        length = len(password)
        if length >= 12:
            score += 25
        elif length >= 9:
            score += 20
        elif length >= 6:
            score += 12
        else:
            score += length * 2
        
        # Character diversity (max 25 points)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        
        diversity_count = sum([has_lower, has_upper, has_digit, has_special])
        score += diversity_count * 6
        
        # Entropy bonus (max 25 points)
        entropy = self.calculate_entropy(password)
        if entropy >= 60:
            score += 25
        elif entropy >= 45:
            score += 18
        elif entropy >= 30:
            score += 10
        else:
            score += 5
        
        # Penalties for common patterns (max -25 points)
        penalties = 0
        
        # Check for dictionary words
        if self.is_dictionary_word(password.lower()):
            penalties += 15
        
        # Check for sequential patterns
        if self.has_sequential_patterns(password):
            penalties += 10
        
        # Check for repeated characters
        if self.has_repeated_patterns(password):
            penalties += 5
        
        # Check for common patterns
        for pattern in self.common_patterns:
            if pattern in password.lower():
                penalties += 10
                break
        
        score = max(0, min(100, score - penalties))
        return score
    
    def get_strength_label(self, score):
        """
        Convert score to strength label
        """
        if score >= 75:
            return 'strong'
        elif score >= 50:
            return 'medium'
        else:
            return 'weak'
    
    def get_feedback(self, password, analysis):
        """
        Generate actionable feedback for the user
        """
        feedback = []
        metrics = analysis['metrics']
        
        # Length feedback
        if metrics['length'] < 8:
            feedback.append('Password should be at least 8 characters long')
        elif metrics['length'] < 12:
            feedback.append('Consider making your password longer for better security')
        
        # Character diversity feedback
        if not metrics['has_uppercase']:
            feedback.append('Add uppercase letters for better security')
        if not metrics['has_lowercase']:
            feedback.append('Add lowercase letters for better security')
        if not metrics['has_digits']:
            feedback.append('Include numbers to make your password stronger')
        if not metrics['has_special']:
            feedback.append('Include special characters for better security')
        
        # Entropy feedback
        if analysis['entropy'] < 40:
            feedback.append('Your password is too predictable. Use more random characters')
        
        # Pattern detection feedback
        if self.is_dictionary_word(password.lower()):
            feedback.append('Avoid using common dictionary words')
        
        if self.has_sequential_patterns(password):
            feedback.append('Avoid sequential patterns like "123" or "abc"')
        
        if self.has_repeated_patterns(password):
            feedback.append('Avoid repeated characters like "aaa"')
        
        # Common password feedback
        for pattern in self.common_patterns:
            if pattern in password.lower():
                feedback.append('Avoid using common passwords or their variations')
                break
        
        if not feedback:
            feedback.append('Great password! Keep it up!')
        
        return feedback[:5]  # Limit to top 5 suggestions
    
    def is_dictionary_word(self, password):
        """
        Check if password is a dictionary word
        """
        # Simple dictionary check (in production, use a proper dictionary)
        common_words = [
            'password', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'love', 'sunshine'
        ]
        return password in common_words or len(password) < 5
    
    def has_sequential_patterns(self, password):
        """
        Check for sequential patterns
        """
        # Check for "abc", "123", "qwerty", etc.
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        
        password = password.lower()
        for seq in sequences:
            if len(password) >= 3:
                for i in range(len(password) - 2):
                    if password[i:i+3] in seq:
                        return True
        return False
    
    def has_repeated_patterns(self, password):
        """
        Check for repeated character patterns
        """
        # Check for 3+ repeated characters
        pattern = re.compile(r'(.)\1{2,}')
        return bool(pattern.search(password))
    
    def load_dictionary(self):
        """
        Load dictionary words from file
        """
        # In production, load from a proper word list
        return set([
            'password', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'love', 'sunshine'
        ])