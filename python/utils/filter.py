# Enter your search terms inside '[ ]' with quotes ' "searching title" ' for each search followed by comma ', ' Eg: ["Software Engineer", "Software Developer", "Selenium Developer"]
search_terms = ["Software Engineer"]

# Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
search_location = "Queensland"  # Some valid examples: "", "United States", "India", "Chicago, Illinois, United States", "90001, Los Angeles, California, United States", "Bengaluru, Karnataka, India", etc.

# After how many number of applications in current search should the bot switch to next search?
switch_number = 30  # Only numbers greater than 0... Don't put in quotes


class Filter:
    """
    Filter class to store filter values
    """

    def __init__(
        self,
        search_terms: list = [],
        search_location: str = "",
        sort_by: str = "Most relevant",
        date_posted: str = "Past 24 hours",
        experience_level: list = [],
        job_type: list = [],
        on_site: list = [],
        location: list = [],
        industry: list = [],
        job_function: list = [],
        job_titles: list = [],
    ):
        self.search_terms = search_terms
        self.search_location = search_location
        self.sort_by = sort_by
        self.date_posted = date_posted
        self.experience_level = experience_level
        self.job_type = job_type
        self.on_site = on_site
        self.location = location
        self.industry = industry
        self.job_function = job_function
        self.job_titles = job_titles

    def __str__(self):
        return f"""Filter(search_terms={self.search_terms}, 
        search_location={self.search_location}, sort_by={self.sort_by}, 
        date_posted={self.date_posted}, experience_level={self.experience_level}, 
        job_type={self.job_type}, location={self.location}, industry={self.industry}, 
        job_function={self.job_function}, job_title={self.job_title})"""
    
    def __repr__(self):
        return f"""Filter(search_terms={self.search_terms}, 
        search_location={self.search_location}, sort_by={self.sort_by}, 
        date_posted={self.date_posted}, experience_level={self.experience_level}, 
        job_type={self.job_type}, location={self.location}, industry={self.industry}, 
        job_function={self.job_function}, job_title={self.job_title})"""
    
    def set_search_terms(self, search_terms: list):
        self.search_terms = search_terms

    def set_search_location(self, search_location: str):
        self.search_location = search_location

    def set_sort_by(self, sort_by: str):
        self.sort_by = sort_by

    def set_date_posted(self, date_posted: str):
        self.date_posted = date_posted
    
    def set_experience_level(self, experience_level: list):
        self.experience_level = experience_level

    def set_job_type(self, job_type: list):
        self.job_type = job_type

    def set_on_site(self, on_site: list):
        self.on_site = on_site

    def set_location(self, location: list):
        self.location = location

    def set_industry(self, industry: list):
        self.industry = industry

    def set_job_function(self, job_function: list):
        self.job_function = job_function

    def set_job_titles(self, job_title: list):
        self.job_title = job_title

    def get_search_terms(self):
        return self.search_terms
    
    def get_search_location(self):
        return self.search_location
    
    def get_sort_by(self):
        return self.sort_by
    
    def get_date_posted(self):
        return self.date_posted
    
    def get_experience_level(self):
        return self.experience_level
    
    def get_job_type(self):
        return self.job_type
    
    def get_on_site(self):
        return self.on_site
    
    def get_location(self):
        return self.location
    
    def get_industry(self):
        return self.industry
    
    def get_job_function(self):
        return self.job_function
    
    def get_job_titles(self):
        return self.job_title
    
    def get_filter(self):
        return {
            "search_terms": self.search_terms,
            "search_location": self.search_location,
            "sort_by": self.sort_by,
            "date_posted": self.date_posted,
            "experience_level": self.experience_level,
            "job_type": self.job_type,
            "location": self.location,
            "industry": self.industry,
            "job_function": self.job_function,
            "job_title": self.job_title
        }
