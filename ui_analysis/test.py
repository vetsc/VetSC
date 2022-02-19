import contextlib
import selenium.webdriver as webdriver
# import lxml.html as LH
# import lxml.html.clean as clean
from time import sleep

url="http://www.yahoo.com"
ignore_tags=('script','noscript','style')
#
# with contextlib.closing(webdriver.Firefox()) as browser:
#     browser.get(url) # Load page
#     content=browser.page_source
#     cleaner=clean.Cleaner()
#     content=cleaner.clean_html(content)
#     with open('/tmp/source.html','w') as f:
#         f.write(content.encode('utf-8'))
#     doc=LH.fromstring(content)
#     with open('/tmp/result.txt','w') as f:
#         for elt in doc.iterdescendants():
#             if elt.tag in ignore_tags: continue
#             text=elt.text or ''
#             tail=elt.tail or ''
#             words=' '.join((text,tail)).strip()
#             if words:
#                 words=words.encode('utf-8')
#                 f.write(words+'\n')

def main():
    print("小居居是笨蛋！")

if __name__ == '__main__':
    main()
