import difflib
from typing import List, Dict, Any, Tuple
import os
import time

class HybridSearchEngine:
    """
    Local Hybrid Search evaluating files against multiple lightweight signals.
    Rule 7: Local Knowledge First. No embeddings or LLMs used here.
    """
    
    @staticmethod
    def _fuzzy_ratio(str1: str, str2: str) -> float:
        return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    @staticmethod
    def rank(query: str, active_files: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
        """
        Ranks files based on:
        Filename Match: 35%
        Fuzzy Match: 20%
        Folder Match: 15%
        Extension Match: 10%
        Frequency of Use / Recent: 20%
        
        Returns a sorted list of (file_record, confidence_percentage)
        """
        results = []
        query_lower = query.lower()
        now = time.time()
        
        # To normalize frequency, find max frequency
        max_freq = max((f.get("frequency", 0) for f in active_files), default=1)
        if max_freq == 0: max_freq = 1
        
        for f in active_files:
            score = 0.0
            
            filename = f.get("filename", "").lower()
            parent = f.get("parent_folder", "").lower()
            ext = f.get("extension", "").lower()
            freq = f.get("frequency", 0)
            
            # 1. Filename Match (35%) - Substring or exact
            if query_lower == filename:
                score += 35.0
            elif query_lower in filename:
                # partial match scales with how much it covers
                coverage = len(query_lower) / max(len(filename), 1)
                score += 35.0 * coverage
                
            # 2. Fuzzy Match (20%)
            fuzz = HybridSearchEngine._fuzzy_ratio(query_lower, filename)
            score += 20.0 * fuzz
            
            # 3. Folder Match (15%) - If query mentions folder name
            if parent and query_lower in parent:
                score += 15.0
                
            # 4. Extension Match (10%) - If query includes the extension e.g. "screenplay docx"
            if ext and ext.replace(".", "") in query_lower:
                score += 10.0
                
            # 5. Frequency of Use (20%)
            freq_score = (freq / max_freq) * 20.0
            score += freq_score
            
            results.append((f, score))
            
        # Sort descending by score
        results.sort(key=lambda x: x[1], reverse=True)
        return results
