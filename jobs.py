from requests_html import HTMLSession

url = "https://www.indeed.com/jobs?q=roper&l=37421&radius=25&from=searchOnDesktopSerp"
session = HTMLSession()
r = session.get(url)
print(r.html.find("div.job_seen_beacon"))