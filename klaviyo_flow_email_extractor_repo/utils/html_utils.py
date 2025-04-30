from bs4 import BeautifulSoup
import re

def extract_and_render_html(email_message):
    html = ""
    if isinstance(email_message, dict):
        data = email_message.get("data", {})
        attrs = data.get("attributes", {}) or email_message.get("attributes", {})
        html = attrs.get("html", "")
    formatted = BeautifulSoup(html, "html.parser").prettify() if html else ""
    return html, formatted

def analyze_html_structure(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    elements = soup.find_all(True)
    images = soup.find_all("img")
    links = soup.find_all("a")
    tables = soup.find_all("table")
    img_with_alt = [img for img in images if img.get("alt")]
    img_without_alt = [img for img in images if not img.get("alt")]
    img_with_dim = [img for img in images if img.get("width") and img.get("height")]
    has_media_queries = bool(re.search(r"@media", html_content))
    media_query_count = len(re.findall(r"@media", html_content))
    has_viewport_meta = bool(soup.find("meta", attrs={"name": "viewport"}))
    has_max_width = bool(re.search(r"max-width", html_content))
    return {
        "total_elements": len(elements),
        "elements": {"images": len(images), "links": len(links), "tables": len(tables)},
        "images": {"count": len(images), "with_alt_text": len(img_with_alt), "without_alt_text": len(img_without_alt), "with_width_height": len(img_with_dim)},
        "responsiveness": {"has_media_queries": has_media_queries, "media_query_count": media_query_count, "has_viewport_meta": has_viewport_meta, "has_max_width": has_max_width}
    }

def check_email_compatibility(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    problematic = {"background_images": bool(soup.find_all(style=re.compile(r"background(-image)?:"))), "forms": bool(soup.find_all("form")), "video": bool(soup.find_all("video")), "javascript": bool(soup.find_all("script"))}
    general = {"has_doctype": html_content.strip().lower().startswith("<!doctype"), "uses_html5_elements": bool(soup.find_all(["section", "article", "header", "footer", "nav"]))}
    layout = {"uses_tables_for_layout": bool(soup.find_all("table"))}
    recommendations = []
    if not general["has_doctype"]:
        recommendations.append("Add a DOCTYPE declaration at the top of your HTML")
    if problematic["forms"]:
        recommendations.append("Remove <form> elements since many email clients don't support forms")
    if problematic["video"]:
        recommendations.append("Avoid <video> tags; convert videos to a GIF or static image")
    if problematic["javascript"]:
        recommendations.append("Remove JavaScript; it's not supported in most email clients")
    return {"general": general, "layout": layout, "problematic_elements": problematic, "recommendations": recommendations}
