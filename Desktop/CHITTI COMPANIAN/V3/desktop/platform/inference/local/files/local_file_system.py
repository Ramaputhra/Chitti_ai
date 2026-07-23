import os
from typing import List
from desktop.platform.shared.interfaces.file_system import IFileSystemProvider, SearchResult

class LocalFileSystemProvider(IFileSystemProvider):
    def search_files(self, query: str, directory: str = "~", max_results: int = 10) -> List[SearchResult]:
        if directory == "~":
            directory = os.path.expanduser("~")
            
        results = []
        try:
            for root, dirs, files in os.walk(directory):
                for f in files:
                    if query.lower() in f.lower():
                        full_path = os.path.join(root, f)
                        try:
                            stat = os.stat(full_path)
                            size = stat.st_size
                            mtime = stat.st_mtime
                        except:
                            size = 0
                            mtime = 0.0
                            
                        _, ext = os.path.splitext(f)
                        results.append(SearchResult(
                            path=full_path,
                            name=f,
                            extension=ext,
                            size=size,
                            modified_time=mtime,
                            score=1.0 # Basic ranking
                        ))
                        if len(results) >= max_results:
                            return results
        except Exception as e:
            pass # Ignore access errors in certain directories
            
        return results
