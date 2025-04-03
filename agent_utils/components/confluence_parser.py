from bs4 import BeautifulSoup
import re

class ConfluenceParser:
    """
    A class to parse and strip unneccessary HTML content from Confluence pages (reduce tokens and improve results).
    """
    def clean_html(html):
        soup = BeautifulSoup(html, "html.parser")

        # Remove specific table properties like 'ac:local-id' and 'data-table-width'
        for table in soup.find_all("table"):
    # Remove all attributes from the table
            for attribute in list(table.attrs):
                del table[attribute]

        # Remove <strong> inside headings
        for tag in soup.find_all(re.compile(r"^h[1-6]$")):
            strong = tag.find("strong")
            if strong:
                tag.string = strong.get_text()

        # Remove <p> inside table cells (<td>, <th>)
        for cell in soup.find_all(["td", "th"]):
            for p in cell.find_all("p"):
                p.unwrap()  # Remove <p> but keep its content

        # Remove unnecessary tags: <em>, <hr>, <strong>, <tbody>, <colgroup>, <col>
        tags_to_remove = ["em", "hr", "strong", "tbody", "colgroup", "col"]
        for tag in tags_to_remove:
            for match in soup.find_all(tag):
                match.unwrap()  # Remove the entire tag

        # Remove Confluence-specific macro tags
        for macro in soup.find_all("ac:structured-macro"):
            macro.decompose()

        return str(soup)
