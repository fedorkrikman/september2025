# chat_html_parser.py

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString


def parse_chat_html_to_text(html_path: Path) -> str:
    """
    Преобразует экспортированный из ChatGPT HTML-чат
    в плоский текстовый формат:

    TITLE / GPT / THREAD / ...
    --- CHAT LOG START ---
    ===== STEP N =====
    Q:
    ...
    A:
    ...
    <CODE block>
    ...
    </CODE block>
    """
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # --- Метаданные чата ---

    title_full = (soup.title.string or "").strip() if soup.title else ""
    gpt_name = ""
    chat_title = title_full

    # Эвристика: "GPT - Название чата"
    if " - " in title_full:
        gpt_name, chat_title = [part.strip() for part in title_full.split(" - ", 1)]

    lang = (soup.html.get("lang") or "").strip() if soup.html else ""

    canonical_url = ""
    thread_id = ""
    gizmo_id = ""
    gpt_slug = ""

    link_canon = soup.find("link", rel="canonical")
    if link_canon and link_canon.has_attr("href"):
        canonical_url = link_canon["href"]
        thread_id, gizmo_id, gpt_slug = _parse_url_parts(canonical_url)

    # Попробуем вытащить базовую модель из первого ответа ассистента
    model_slug = ""
    first_assistant_div = soup.find("div", attrs={"data-message-author-role": "assistant"})
    if first_assistant_div and first_assistant_div.has_attr("data-message-model-slug"):
        model_slug = first_assistant_div["data-message-model-slug"]

    # --- Сборка шагов Q/A ---

    steps = _extract_steps(soup)

    # --- Формирование итогового текста ---

    lines: list[str] = []

    if chat_title:
        lines.append(f"TITLE: {chat_title}")
    if gpt_name:
        lines.append(f"GPT: {gpt_name}")
    if model_slug:
        lines.append(f"MODEL: {model_slug}")
    if thread_id:
        lines.append(f"THREAD: {thread_id}")
    if canonical_url:
        lines.append(f"URL: {canonical_url}")
    if lang:
        lines.append(f"LANG: {lang}")

    if lines:
        lines.append("")  # пустая строка после шапки

    lines.append("--- CHAT LOG START ---")
    lines.append("")

    for idx, (q_text, a_text) in enumerate(steps, start=1):
        lines.append(f"===== STEP {idx} =====")
        lines.append("Q:")
        lines.append(q_text.rstrip())
        lines.append("")
        lines.append("A:")
        lines.append(a_text.rstrip())
        lines.append("")
        # Дополнительная пустая строка не обязательна, но улучшает читаемость

    return "\n".join(lines).rstrip() + "\n"


# ---------- Вспомогательные функции ----------

def _parse_url_parts(url: str) -> tuple[str, str, str]:
    """
    Разбор URL вида:
    https://chatgpt.com/g/g-<hex>-<slug>/c/<thread-id>

    Возвращает: (thread_id, gizmo_id, gpt_slug)
    где gizmo_id ~ 'g-<hex>', gpt_slug ~ '<slug>'.
    """
    try:
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        # ожидаем что-то вроде: ["g", "g-XXXX-slug", "c", "THREAD"]
        if len(parts) >= 4 and parts[0] == "g" and parts[2] == "c":
            gizmo_part = parts[1]  # "g-<hex>-<slug>"
            thread_id = parts[3]

            gizmo_id = ""
            gpt_slug = ""

            # Разделяем "g-<hex>-<slug>" на "g-<hex>" и "<slug>"
            sub = gizmo_part.split("-", 2)
            if len(sub) == 3:
                gizmo_id = "-".join(sub[:2])   # "g-<hex>"
                gpt_slug = sub[2]             # "<slug>"
            else:
                gizmo_id = gizmo_part

            return thread_id, gizmo_id, gpt_slug
    except Exception:
        pass

    return "", "", ""


def _extract_steps(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """
    Проходит по article[data-testid^="conversation-turn-..."]
    и собирает пары (Q, A):

    - Q: содержимое пользовательского сообщения;
    - A: первый ответ ассистента после этого пользователя.
    """
    steps: list[tuple[str, str]] = []
    current_q: str | None = None

    articles = soup.select('article[data-testid^="conversation-turn-"]')

    for art in articles:
        role = art.get("data-turn")  # "user", "assistant", "tool"...

        if role == "user":
            user_div = art.find("div", attrs={"data-message-author-role": "user"})
            if not isinstance(user_div, Tag):
                continue
            q_text = _extract_message_text(user_div)
            if not q_text.strip():
                continue
            current_q = q_text

        elif role == "assistant" and current_q is not None:
            as_div = art.find("div", attrs={"data-message-author-role": "assistant"})
            if not isinstance(as_div, Tag):
                continue
            a_text = _extract_message_text(as_div)
            steps.append((current_q, a_text))
            current_q = None

        else:
            # tool / system / одиночные ассистентские сообщения без предшествующего Q
            continue

    return steps



def _extract_message_text(root: Tag) -> str:
    """
    Извлекает текст одного сообщения, проходя рекурсивно по всему поддереву.

    Любой <pre> на любом уровне глубины преобразуется в:

    <CODE block>
    ...код...
    </CODE block>
    """

    blocks: list[str] = []
    paragraph_buf: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_buf:
            return
        text = " ".join(part.strip() for part in paragraph_buf if part.strip())
        paragraph_buf.clear()
        if text:
            blocks.append(text)

    def visit(node) -> None:
        # Текстовый узел
        if isinstance(node, NavigableString):
            text = str(node)
            if text.strip():
                paragraph_buf.append(text)
            return

        # Тег
        if not isinstance(node, Tag):
            return

        # Кодовый блок <pre> – обрабатываем отдельно и не спускаемся глубже
        if node.name == "pre":
            flush_paragraph()

            # Пытаемся найти вложенный <code>, чтобы не тащить заголовок и кнопку «Копировать код»
            code_container = node.find("code")
            if code_container is not None:
                code_text = code_container.get_text("\n", strip=False)
            else:
                code_text = node.get_text("\n", strip=False)

            code_text = code_text.strip("\n")

            blocks.append("<CODE block>")
            if code_text:
                blocks.append(code_text)
            blocks.append("</CODE block>")
            return

        # Блочные элементы, которые логически отделяют абзацы
        if node.name in {"p", "li"}:
            flush_paragraph()
            for child in node.children:
                visit(child)
            flush_paragraph()
            return

        # Остальные контейнеры (div, span, strong, em, ul, ol и т.п.) — просто рекурсивный проход
        for child in node.children:
            visit(child)

    # Запуск обхода
    visit(root)
    flush_paragraph()

    return "\n".join(blocks).strip()

