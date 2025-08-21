#크롤링 전용 함수
import requests 
from bs4 import BeautifulSoup

BASE_URL = "https://mediahub.seoul.go.kr"
LIST_URL = "https://mediahub.seoul.go.kr/news/newsListAjax.do"

def get_article_links(area_code="140", max_pages=5):
    all_links = set()
    page = 1

    while page <= max_pages:
        payload = { "search_pageNo": str(page), "search_orderBy": "articlePubDt", "search_articleArea": area_code, "search_isNews": "Y", "search_isCorresNews": "N", "newsListType": "thumbnail", "search_startDate": "", "search_endDate": "", "search_searchType": "", "search_keyword": "" }
        res = requests.post(LIST_URL, data=payload)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        links = [
            BASE_URL + a["href"]
            for a in soup.select("a.goArticleDetail")
            if a.get("href")
        ]
        links = list(set(links))  

        if not links:
            break

        all_links.update(links)
        page += 1

    return list(all_links)

def get_article_detail(url):
    """
    단일 기사 상세 내용 크롤링
    """
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # 제목
    title = soup.find("h1", class_="tit").get_text(strip=True) if soup.find("h1", class_="tit") else "제목 없음"

    # 기자
    writer = soup.select_one(".info .writer").get_text(strip=True) if soup.select_one(".info .writer") else "작성자 없음"

    # 날짜
    date_tag = soup.select_one("p.date span.num")
    date = date_tag.get_text(strip=True) if date_tag else "날짜 없음"

    # 본문 + 이미지
    content_div = soup.find("div", class_="news_detail_cont")
    paragraphs = []
    images = []
    if content_div:
        for article in content_div.find_all("div", class_="article"):
            # 본문 텍스트
            txt_div = article.find("div", class_="txt")
            if txt_div:
                paragraphs.append(txt_div.get_text(" ", strip=True))

            # 이미지
            img_tag = article.find("img")
            if img_tag and "src" in img_tag.attrs:
                img_url = img_tag["src"]
                if not img_url.startswith("http"):
                    img_url = BASE_URL + img_url
                images.append(img_url)

    return {
        "url": url,
        "title": title,
        "writer": writer,
        "date": date,
        "content": "\n".join(paragraphs),
        "images": images
    }
