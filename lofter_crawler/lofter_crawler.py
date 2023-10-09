import random
from playwright.async_api import Browser
from lofter_post import LofterPost
from datetime import date
from urllib.parse import urlparse
import re
import logging

class PostReader:
    def __init__(self, browser: Browser):
        self._browser = browser
        self._logger = logging.getLogger("Post Reader")

    async def read(self, post: LofterPost):
        """阅读文章(默认主题)"""
        page = await self._browser.new_page()
        self._logger.info(f"Start reading: {post.link}")
        await page.goto(post.link)
        # read title
        title = await page.title()
        title = title[:title.rfind("-")]
        # read img
        img_srcs: list[str] = []
        for element in await page.locator("div.content > div.img > a").all():
            img_src = await element.get_attribute("bigimgsrc")
            img_srcs.append(img_src)
        # read text
        lines: list[str] = []
        for element in await page.locator("div.content > div.text > p").all():
            eh = await element.element_handle()
            node_name: str = await eh.evaluate("node => node.nodeName")
            line: str = await element.inner_text() \
                if node_name.lower() == "p" \
                else await eh.evaluate("node => node.outerHTML")
            lines.append(line)
        # read tag
        tags: list[str] = []
        for element in await page.locator("div.tag > a").all():
            tag = await element.inner_text()
            tags.append(tag[2:])
        await page.close()
        self._logger.info(f"Finish reading: {post.link}")
        post.title = title
        post.img_src = img_srcs
        post.lines = lines
        post.tags = tags
        return post


class AchieveReader:
    def __init__(self, browser: Browser) -> None:
        self._browser = browser
        self._logger = logging.getLogger("Achieve Reader")

    async def read(self, link: str):
        """阅读归档"""
        posts: list[LofterPost] = []
        page = await self._browser.new_page()
        self._logger.info(f"Start reading: {link}")
        await page.goto(link)
        count = int(
            await page.locator(
                "div:nth-child(1) > div > div.txt > a.ztag.currt > span"
            ).first.inner_text()
        )
        self._logger.info(f"Articles' count: {count} ")
        self._logger.info("Locating all Ariticles...")
        while (await page.locator("span.info").count()) < count:
            await page.mouse.wheel(0, random.randint(0, 50))
        self._logger.info("All Articles located")
        self._logger.info("Parse article...")
        ztag = await page.locator("div.g-bdc.ztag > div.ztag > div.m-filecnt").all()
        for locator in ztag:
            date_str = await locator.locator("h2:nth-child(1) > em").inner_text()
            if re.match(r"\d{4}年\d{1,2}月", date_str):
                year = int(date_str[:4])
            else:
                year = date.today().year
            for post_card in await locator.locator("ul > li > a").all():
                href: str = await post_card.get_attribute("href")
                url = urlparse(link)
                post_link = f"https://{url.netloc}{href}"

                md = await post_card.locator(".info > em").inner_text()
                m_str, d_str = re.findall(r"\d+", md)
                publish_date = date(year, int(m_str), int(d_str))

                post = LofterPost(publish_date, post_link)
                posts.append(post)
        self._logger.info(f"Finish reading: {link}")

        await page.close()
        return posts
