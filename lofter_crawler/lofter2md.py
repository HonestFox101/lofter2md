import asyncio
import configparser
import logging
import os
from lofter_crawler import LofterPost
from urllib.parse import urlparse
from playwright.async_api import async_playwright, APIRequestContext
from lofter_crawler import AchieveReader
from lofter_crawler import PostReader

config = configparser.ConfigParser()
config.read("config.ini")

BROWSER_PATH = config.get("general", "browser")
HEADLESS_MODE = config.get("general", "headless").lower() == "true"

logging.basicConfig(level=logging.INFO)


async def fetch_img(api_context: APIRequestContext, src: str):
    resp = await api_context.get(src)
    if resp.ok:
        return await resp.body()


async def save_as_markdown(api_context: APIRequestContext, post: LofterPost, path: str):
    """保存为markdown文件"""
    logger = logging.getLogger("Save as Markdown Task")
    if not os.path.exists(path):
        os.mkdir(path)
    logger.info(f"Saving {post.title}")
    # Handle image
    img_dir = os.path.join(path, "img")
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    img_path_arr: list[str] = []
    logger.info(f"Reading {len(post.img_src)} images")
    for i, src in enumerate(post.img_src):
        logger.info(f"Fetching image{i} {src}")
        url = urlparse(src)
        image_file_name = f"{i}-" + url.path.split("/")[-1]
        target_path = os.path.join(img_dir, image_file_name)
        data = await fetch_img(api_context, src)
        with open(target_path, "wb+") as f:
            f.write(data)
        logger.info(f"Save image{i} to {target_path}")
        target_path = os.path.relpath(target_path, path)
        img_path_arr.append(target_path)
    logger.info(f"All images saved")

    # Handle markdown file
    logger.info(f"Building markdown file: {post.title}.md")
    # header
    content = "---\n"
    content += f"title: {post.title}\n"
    content += f"date: {post.date.year}/{post.date.month}/{post.date.day} 00:00:00\n"
    content += "tags:\n"
    for tag in post.tags:
        content += f"- {tag}\n"
    content += "---\n\n"
    # main body
    content += f"# {post.title}\n"
    content += (
        "\n".join(
            [
                "![{i}]({path})".format(i=i + 1, path=path)
                for i, path in enumerate(img_path_arr)
            ]
        )
        + "\n\n"
    )
    content += "\n\n".join(post.lines)
    # save markdown file
    ILLEGAL_CHAR = '\\/:*?"<>|'
    trans_dict = str.maketrans(ILLEGAL_CHAR, " " * len(ILLEGAL_CHAR))
    md_file_name = f"{post.title.translate(trans_dict)}.md"
    md_file_path = os.path.join(path, md_file_name)
    with open(md_file_path, "w+", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Finish write to {md_file_path}")


async def lofter2md(link, path, override=False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=BROWSER_PATH, headless=HEADLESS_MODE
        )
        api_context = (await browser.new_context()).request

        achieve_reader = AchieveReader(browser)
        post_reader = PostReader(browser)
        posts = await achieve_reader.read(link)

        if not os.path.exists(path):
            os.mkdir(path)

        for post in posts:
            post = await post_reader.read(post)
            ILLEGAL_CHAR = '\\/:*?"<>|'
            trans_dict = str.maketrans(ILLEGAL_CHAR, " " * len(ILLEGAL_CHAR))
            post_dir_name = post.title.translate(trans_dict)
            md_path = os.path.join(path, post_dir_name)
            if os.path.exists(md_path) and not override:
                continue
            await save_as_markdown(api_context, post, md_path)

        await asyncio.sleep(0.5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(lofter2md(link="https://youxunran221.lofter.com/view", path="output"))
