from datetime import date

class LofterPost:
    def __init__(
        self,
        publish_date: date,
        link: str,
        title: str = "",
        img_srcs: list[str] = [],
        lines: list[str] = [],
        tags: list[str] = [],
    ) -> None:
        self._img_srcs = img_srcs
        self._lines = lines
        self._tags = tags
        self._title = title
        self._date = publish_date
        self._link = link

    def __str__(self) -> str:
        return "\n".join(
            [
                f"title: {self.title}",
                f"img srcs: {self.img_src}",
                f"lines: {self.lines}",
                f"tags: {self.tags}",
                f"date: {self.date}",
            ]
        )

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def link(self):
        return self._link
    
    @link.setter
    def link(self, value):
        self._link = value

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value

    @property
    def img_src(self):
        return self._img_srcs

    @img_src.setter
    def img_src(self, value):
        self._img_srcs = value

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value
