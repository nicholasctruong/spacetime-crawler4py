import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import defaultdict

stop_words = {
    'do', "weren't", 'off', "there's", 'ought', 'whom', 'from', "wouldn't", 'above',
    'him', 'this', 'all', "won't", 'yourselves', "she'll", 'to', "they'll", 'again',
    'same', "why's", 'while', 'about', "didn't", "he's", 'and', 'would', "i'll",
    'more', "don't", 'myself', 'very', "mustn't", 'out', 'here', "where's", "that's",
    "shan't", 'as', 'does', 'those', 'having', 'over', 'only', 'any', 'itself',
    "we're", "i'm", 'that', 'what', "you'd", 'herself', 'cannot', "what's", "you've",
    'on', 'i', "when's", "how's", 'an', 'has', "hasn't", "let's", 'hers', 'further',
    'who', 'you', 'could', "i've", 'had', 'before', 'because', 'themselves', 'am',
    'down', "wasn't", 'up', "she's", "haven't", 'she', 'should', 'than', "they've",
    'too', 'its', "doesn't", 'there', 'at', 'yourself', 'no', 'did', 'until', 'we',
    "hadn't", "i'd", "couldn't", "shouldn't", 'their', 'if', 'by', 'own', 'which',
    'under', "it's", 'are', 'have', "we'll", "they're", 'he', "aren't", 'my',
    'against', 'once', 'through', 'me', 'was', 'is', 'it', 'where', 'doing', 'a',
    'be', "here's", 'were', 'been', 'theirs', 'not', 'into', 'so', 'these', 'why',
    'most', "we've", 'or', 'her', "who's", "we'd", "he'd", 'after', 'being', 'both',
    "they'd", 'your', "she'd", "isn't", 'them', "can't", 'for', 'nor', 'yours',
    'but', 'in', 'other', 'himself', 'with', 'his', 'of', 'ours', 'tourselves',
    'such', 'they', 'each', "you're", "he'll", 'some', 'between', 'during', 'our',
    'the', 'then', 'when', 'few', "you'll", 'below', 'how'
}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    print( [link for link in links if is_valid(link)] )
    return [link for link in links if is_valid(link)]

def token_info(url, resp):
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')         
        lines = [string for string in soup.find("body").stripped_strings]
        tokens = []
        document_size = 0
        for line in lines:
            for token in re.findall(r'[a-zA-Z0-9\']+', line):
                tokens.append(token.lower())
                document_size += 1
        token_dict = defaultdict(int)
        for token in tokens:
            if token not in stop_words:
                token_dict[token] += 1
        return (document_size, token_dict)
    else:
        return (0, dict())

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')         

        processed_links = []
        for link in soup.find_all('a'):
            if link.get('href'):
                processed_link = link.get('href').split('#')[0]
                processed_links.append(processed_link)
        return processed_links
    else:
        return []

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        not_excluded = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        
        is_within_domain = re.match(
            r"^(.*)?(?(1)(.|/))(ics|cs|informatics|stat|(today)?)(.uci.edu)(?(4)(/department/information_computer_sciences))",
            parsed.geturl().lower()
        )
        
        return not_excluded and is_within_domain

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def is_subdomain(url):
    try:
        parsed = urlparse(url)
        return bool(re.match(r"^(.*).ics.uci.edu", parsed.geturl().lower()))
    
    except TypeError:
        print ("TypeError for ", parsed)
        raise
