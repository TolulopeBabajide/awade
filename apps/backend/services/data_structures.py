"""
Data Structures and Algorithms for Awade

This module provides optimized data structures and algorithms for efficient
database queries, caching, and request handling in the Awade platform.

Author: Tolulope Babajide
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from collections import OrderedDict, defaultdict
import time
import math
import re
import hashlib
import json
import threading
from enum import Enum


class CacheStrategy(Enum):
    """Cache strategy enumeration."""
    LRU = "lru"
    LFU = "lfu"


class LRUCache:
    """Least Recently Used (LRU) Cache implementation."""
    
    def __init__(self, capacity: int):
        """
        Initialize LRU cache.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if capacity > 1000000:  # Reasonable upper limit
            raise ValueError("Capacity too large")
        
        self.capacity = capacity
        self.cache = OrderedDict()
        self.max_entry_size = 1024 * 1024  # 1MB per entry
        self._lock = threading.RLock()  # Thread safety
    
    def get(self, key: str) -> Any:
        """
        Get value by key and mark as recently used.
        
        Args:
            key (str): Cache key
            
        Returns:
            Any: Cached value or None if not found
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid cache key")
        
        with self._lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                return value
            return None
    
    def put(self, key: str, value: Any, size: int = 1) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            size (int): Size of the item (for size-based eviction)
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid cache key")
        
        # Check value size
        try:
            value_size = len(str(value).encode('utf-8'))
            if value_size > self.max_entry_size:
                raise ValueError(f"Value too large: {value_size} bytes")
        except (TypeError, UnicodeEncodeError):
            raise ValueError("Invalid value type for caching")
        
        with self._lock:
            if key in self.cache:
                # Update existing key
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Remove least recently used item
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self.cache)
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self.cache.clear()


class LFUCache:
    """Least Frequently Used (LFU) Cache implementation."""
    
    def __init__(self, capacity: int):
        """
        Initialize LFU cache.
        
        Args:
            capacity (int): Maximum number of items the cache can hold
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if capacity > 1000000:  # Reasonable upper limit
            raise ValueError("Capacity too large")
        
        self.capacity = capacity
        self.cache = {}  # key -> value
        self.frequencies = defaultdict(int)  # key -> frequency
        self.frequency_groups = defaultdict(OrderedDict)  # frequency -> {key: value}
        self.min_frequency = 0
        self.max_entry_size = 1024 * 1024  # 1MB per entry
        self._lock = threading.RLock()  # Thread safety
    
    def get(self, key: str) -> Any:
        """
        Get value by key and update frequency.
        
        Args:
            key (str): Cache key
            
        Returns:
            Any: Cached value or None if not found
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid cache key")
        
        with self._lock:
            if key not in self.cache:
                return None
            
            # Update frequency
            old_freq = self.frequencies[key]
            new_freq = old_freq + 1
            self.frequencies[key] = new_freq
            
            # Move to new frequency group
            del self.frequency_groups[old_freq][key]
            if not self.frequency_groups[old_freq] and old_freq == self.min_frequency:
                self.min_frequency += 1
            
            self.frequency_groups[new_freq][key] = self.cache[key]
            return self.cache[key]
    
    def put(self, key: str, value: Any, size: int = 1) -> None:
        """
        Put key-value pair in cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            size (int): Size of the item (for size-based eviction)
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid cache key")
        
        # Check value size
        try:
            value_size = len(str(value).encode('utf-8'))
            if value_size > self.max_entry_size:
                raise ValueError(f"Value too large: {value_size} bytes")
        except (TypeError, UnicodeEncodeError):
            raise ValueError("Invalid value type for caching")
        
        with self._lock:
            if key in self.cache:
                # Update existing key
                self.cache[key] = value
                self.get(key)  # Update frequency
                return
            
            if len(self.cache) >= self.capacity:
                # Remove least frequently used item
                lfu_key, _ = self.frequency_groups[self.min_frequency].popitem(last=False)
                del self.cache[lfu_key]
                del self.frequencies[lfu_key]
            
            # Add new item
            self.cache[key] = value
            self.frequencies[key] = 1
            self.frequency_groups[1][key] = value
            self.min_frequency = 1
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self.cache)
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self.cache.clear()
            self.frequencies.clear()
            self.frequency_groups.clear()
            self.min_frequency = 0


class QueryOptimizer:
    """Query optimization and caching system."""
    
    def __init__(self, complexity_threshold: int = 1000):
        """
        Initialize query optimizer.
        
        Args:
            complexity_threshold (int): Threshold for query complexity analysis
        """
        if complexity_threshold <= 0:
            raise ValueError("Complexity threshold must be positive")
        
        self.complexity_threshold = complexity_threshold
        self.query_cache = LRUCache(1000)
        self.query_stats = defaultdict(int)
        self._lock = threading.RLock()  # Thread safety
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Check if query is safe (basic SQL injection prevention).
        
        Args:
            query (str): SQL query
            
        Returns:
            bool: True if query appears safe
        """
        # Basic SQL injection patterns to check
        dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+.*\s+set',
            r'union\s+select',
            r'insert\s+into',
            r'exec\s*\(',
            r'execute\s*\(',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False
        
        return True
    
    def _analyze_complexity(self, query: str, params: Dict[str, Any]) -> int:
        """
        Analyze query complexity.
        
        Args:
            query (str): SQL query
            params (Dict[str, Any]): Query parameters
            
        Returns:
            int: Complexity score
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Invalid query")
        
        complexity = 0
        
        # Base complexity
        complexity += len(query.split())
        
        # JOIN complexity
        join_count = query.upper().count('JOIN')
        complexity += join_count * 10
        
        # WHERE complexity
        where_count = query.upper().count('WHERE')
        complexity += where_count * 5
        
        # Parameter complexity
        complexity += len(params) * 2
        
        return complexity
    
    def _generate_plan(self, query: str, params: Dict[str, Any], complexity: int) -> Dict[str, Any]:
        """
        Generate query execution plan.
        
        Args:
            query (str): SQL query
            params (Dict[str, Any]): Query parameters
            complexity (int): Query complexity
            
        Returns:
            Dict[str, Any]: Execution plan
        """
        plan = {
            'query': query,
            'complexity': complexity,
            'cache_strategy': 'lru' if complexity < self.complexity_threshold else 'lfu',
            'ttl': 300 if complexity < self.complexity_threshold else 600,
            'optimizations': []
        }
        
        # Add optimizations based on complexity
        if complexity > self.complexity_threshold:
            plan['optimizations'].append('consider_indexing')
            plan['optimizations'].append('use_pagination')
        
        return plan
    
    def optimize_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize query and return execution plan.
        
        Args:
            query (str): SQL query
            params (Dict[str, Any]): Query parameters
            
        Returns:
            Dict[str, Any]: Optimized execution plan
        """
        # Validate query safety first
        if not self._is_safe_query(query):
            raise ValueError("Unsafe query detected")
        
        with self._lock:
            # Generate secure cache key
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            params_hash = hashlib.sha256(str(sorted(params.items())).encode()).hexdigest()
            cache_key = f"query:{query_hash}:{params_hash}"
            
            # Check cache first
            cached_plan = self.query_cache.get(cache_key)
            if cached_plan:
                self.query_stats[query] += 1
                return cached_plan
            
            # Analyze and optimize
            complexity = self._analyze_complexity(query, params)
            plan = self._generate_plan(query, params, complexity)
            
            # Cache the plan
            self.query_cache.put(cache_key, plan)
            self.query_stats[query] += 1
            
            return plan


class SearchIndex:
    """Full-text search index with TF-IDF scoring."""
    
    def __init__(self):
        """Initialize search index."""
        self.documents = {}  # doc_id -> text_hash (for security)
        self.index = defaultdict(set)  # term -> set of doc_ids
        self.doc_count = 0
        self._lock = threading.RLock()  # Thread safety
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into terms.
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of tokens
        """
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        # Sanitize and tokenize - remove special characters and split
        sanitized = re.sub(r'[^\w\s]', ' ', text.lower())
        return [term.strip() for term in sanitized.split() if term.strip() and len(term) > 1]
    
    def add_document(self, doc_id: int, text: str) -> None:
        """
        Add document to search index.
        
        Args:
            doc_id (int): Document ID
            text (str): Document text
        """
        if not isinstance(doc_id, int) or doc_id <= 0:
            raise ValueError("Document ID must be a positive integer")
        
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")
        
        with self._lock:
            # Store hash instead of raw text for security
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            self.documents[doc_id] = text_hash
            self.doc_count += 1
            
            # Tokenize and add to index
            terms = self._tokenize(text)
            for term in terms:
                self.index[term].add(doc_id)
    
    def _calculate_tf(self, term: str, doc_id: int) -> float:
        """Calculate term frequency for a document."""
        with self._lock:
            if doc_id not in self.documents:
                return 0.0
            
            # Note: We can't calculate TF from hash, so we'll use a simplified approach
            # In a real implementation, you'd need to store term frequencies separately
            return 1.0 if term in self.index and doc_id in self.index[term] else 0.0
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate inverse document frequency for a term."""
        with self._lock:
            if term not in self.index or not self.index[term]:
                return 0.0
            
            doc_freq = len(self.index[term])
            if doc_freq == 0 or self.doc_count == 0:
                return 0.0
            
            return math.log(self.doc_count / doc_freq)
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Search documents using TF-IDF scoring.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Tuple[int, float]]: List of (doc_id, score) tuples
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")
        
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        
        with self._lock:
            query_terms = self._tokenize(query)
            if not query_terms:
                return []
            
            # Calculate scores for each document
            scores = defaultdict(float)
            for term in query_terms:
                if term in self.index:
                    idf = self._calculate_idf(term)
                    for doc_id in self.index[term]:
                        tf = self._calculate_tf(term, doc_id)
                        scores[doc_id] += tf * idf
            
            # Sort by score and return top results
            results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return results[:limit]


class RequestQueue:
    """Priority-based request queue."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize request queue.
        
        Args:
            max_size (int): Maximum queue size
        """
        if max_size <= 0:
            raise ValueError("Max size must be positive")
        if max_size > 100000:  # Reasonable upper limit
            raise ValueError("Max size too large")
        
        self.max_size = max_size
        self.request_count = 0
        self.queues = {
            'high': [],
            'normal': [],
            'low': []
        }
        self.priority_order = ['high', 'normal', 'low']
        self._lock = threading.RLock()  # Thread safety
        self._rate_limit_window = 60  # 1 minute
        self._rate_limit_requests = 1000  # Max requests per window
        self._request_times = []  # Track request times for rate limiting
    
    def _is_rate_limited(self) -> bool:
        """Check if rate limit is exceeded."""
        current_time = time.time()
        # Remove old requests outside the window
        self._request_times = [t for t in self._request_times if current_time - t < self._rate_limit_window]
        return len(self._request_times) >= self._rate_limit_requests
    
    def add_request(self, request: Dict[str, Any], priority: str = 'normal') -> bool:
        """
        Add request to queue.
        
        Args:
            request (Dict[str, Any]): Request data
            priority (str): Request priority ('high', 'normal', 'low')
            
        Returns:
            bool: True if added successfully, False if queue is full or rate limited
        """
        if not isinstance(request, dict):
            raise ValueError("Request must be a dictionary")
        
        if not isinstance(priority, str) or priority not in self.queues:
            priority = 'normal'
        
        with self._lock:
            # Check rate limiting
            if self._is_rate_limited():
                return False
            
            if self.request_count >= self.max_size:
                return False
            
            self.queues[priority].append(request)
            self.request_count += 1
            self._request_times.append(time.time())
            return True
    
    def get_next_request(self) -> Optional[Dict[str, Any]]:
        """
        Get next request from queue based on priority.
        
        Returns:
            Optional[Dict[str, Any]]: Next request or None if queue is empty
        """
        with self._lock:
            for priority in self.priority_order:
                if self.queues[priority]:
                    request = self.queues[priority].pop(0)
                    self.request_count -= 1
                    return request
            
            return None
    
    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get queue statistics.
        
        Returns:
            Dict[str, int]: Queue statistics
        """
        with self._lock:
            return {
                'total_requests': self.request_count,
                'high_priority_count': len(self.queues['high']),
                'normal_priority_count': len(self.queues['normal']),
                'low_priority_count': len(self.queues['low']),
                'rate_limit_remaining': max(0, self._rate_limit_requests - len(self._request_times))
            }


class DataStructureManager:
    """Centralized data structure manager."""
    
    def __init__(self, cache_capacity: int = 1000, queue_capacity: int = 1000):
        """
        Initialize data structure manager.
        
        Args:
            cache_capacity (int): Cache capacity
            queue_capacity (int): Queue capacity
        """
        self.lru_cache = LRUCache(cache_capacity)
        self.lfu_cache = LFUCache(cache_capacity)
        self.search_index = SearchIndex()
        self.request_queue = RequestQueue(queue_capacity)
        self.query_optimizer = QueryOptimizer()
        self._lock = threading.RLock()  # Thread safety
        
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'requests_processed': 0,
            'queries_optimized': 0
        }
    
    def get_cache(self, strategy: CacheStrategy) -> Union[LRUCache, LFUCache]:
        """
        Get cache instance by strategy.
        
        Args:
            strategy (CacheStrategy): Cache strategy
            
        Returns:
            Union[LRUCache, LFUCache]: Cache instance
        """
        if strategy == CacheStrategy.LRU:
            return self.lru_cache
        elif strategy == CacheStrategy.LFU:
            return self.lfu_cache
        else:
            return self.lru_cache
    
    def cache_set(self, key: str, value: Any, strategy: CacheStrategy) -> None:
        """
        Set cache value.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            strategy (CacheStrategy): Cache strategy
        """
        with self._lock:
            cache = self.get_cache(strategy)
            cache.put(key, value)
    
    def cache_get(self, key: str, strategy: CacheStrategy) -> Any:
        """
        Get cache value.
        
        Args:
            key (str): Cache key
            strategy (CacheStrategy): Cache strategy
            
        Returns:
            Any: Cached value or None
        """
        with self._lock:
            cache = self.get_cache(strategy)
            value = cache.get(key)
            
            if value is not None:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['cache_misses'] += 1
            
            return value
    
    def add_search_document(self, doc_id: int, text: str) -> None:
        """
        Add document to search index.
        
        Args:
            doc_id (int): Document ID
            text (str): Document text
        """
        with self._lock:
            self.search_index.add_document(doc_id, text)
    
    def search_documents(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Search documents.
        
        Args:
            query (str): Search query
            limit (int): Maximum results
            
        Returns:
            List[Tuple[int, float]]: Search results
        """
        with self._lock:
            return self.search_index.search(query, limit)
    
    def add_request(self, request: Dict[str, Any], priority: str = 'normal') -> bool:
        """
        Add request to queue.
        
        Args:
            request (Dict[str, Any]): Request data
            priority (str): Request priority
            
        Returns:
            bool: True if added successfully
        """
        with self._lock:
            return self.request_queue.add_request(request, priority)
    
    def get_next_request(self) -> Optional[Dict[str, Any]]:
        """
        Get next request from queue.
        
        Returns:
            Optional[Dict[str, Any]]: Next request or None
        """
        with self._lock:
            request = self.request_queue.get_next_request()
            if request:
                self.metrics['requests_processed'] += 1
            return request
    
    def optimize_query(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize database query.
        
        Args:
            query (str): SQL query
            params (Dict[str, Any]): Query parameters
            
        Returns:
            Dict[str, Any]: Optimized query plan
        """
        with self._lock:
            self.metrics['queries_optimized'] += 1
            return self.query_optimizer.optimize_query(query, params)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        with self._lock:
            total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
            cache_hit_rate = (self.metrics['cache_hits'] / total_cache_requests * 100) if total_cache_requests > 0 else 0
            
            return {
                **self.metrics,
                'cache_hit_rate': cache_hit_rate,
                'cache_utilization': (self.lru_cache.size() + self.lfu_cache.size()) / (self.lru_cache.capacity + self.lfu_cache.capacity) * 100,
                'queue_stats': self.request_queue.get_queue_stats()
            }
