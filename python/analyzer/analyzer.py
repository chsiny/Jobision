# python/analyzer/analyzer.py
import pandas as pd

class JobAnalyzer:
    def __init__(self, jobs):
        self.jobs = jobs
        self.df = pd.DataFrame(jobs)

    def get_top_companies(self, n=5):
        """Get the top N companies by job postings."""
        return self.df['company'].value_counts().head(n)

    def get_common_keywords(self):
        """Analyze common keywords in job titles."""
        all_titles = " ".join(self.df['title'].tolist())
        keywords = pd.Series(all_titles.split()).value_counts()
        return keywords.head(10)
