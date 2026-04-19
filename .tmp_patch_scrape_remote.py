from pathlib import Path

path = Path('/root/forum-harvest/scrape.py')
text = path.read_text(encoding='utf-8')

old_func = '''def scrape_thread(browser, thread_id: int, thread_href: str, expected_posts: int = 0, download_imgs: bool = True, download_materials_files: bool = True, forum_dir: Path = None) -> dict | None:
    normalized_href = normalize_thread_href(thread_href)
    url = f"{BASE_URL}/{normalized_href}".rstrip("/") + "/"
    log.info(f"  Тема {thread_id}: загружаю...")
    page = browser.new_page()
    try:
        html, page = safe_get(page, url)
        if not html:
            return None

        title = parse_thread_title(html)
        max_page = get_max_page(html)
        all_posts = parse_thread_page(html)
        if MAX_THREAD_PAGES > 0:
            max_page = min(max_page, MAX_THREAD_PAGES)

        for pg in range(2, max_page + 1):
            delay()
            pg_html, page = safe_get(page, f"{url}page-{pg}")
            if pg_html:
                posts = parse_thread_page(pg_html)
                all_posts.extend(posts)
                log.info(f"    стр. {pg}/{max_page} — {len(posts)} постов")

        if download_imgs:
            img_count = sum(len(post.get("images", [])) for post in all_posts)
            if img_count > 0:
                save_dir = forum_dir if forum_dir else RAW_PATH
                images_dir = save_dir / f"{thread_id}_images"
                download_images(page, all_posts, images_dir)

        if download_materials_files:
            material_count = sum(len(post.get("material_links", [])) for post in all_posts)
            if material_count > 0:
                save_dir = forum_dir if forum_dir else RAW_PATH
                materials_dir = save_dir / f"{thread_id}_materials"
                download_materials(page, all_posts, materials_dir, BASE_URL, log)

        thread_data = {
            "thread_id": thread_id,
            "title": title,
            "url": url,
            "pages": max_page,
            "posts_count": len(all_posts),
            "posts": all_posts,
            "scraped_at": datetime.now().isoformat(),
            "expected_posts": expected_posts,
        }
        summarize_thread_data(thread_data, expected_posts)
        return thread_data
    finally:
        try:
            page.close()
        except Exception:
            pass
'''

new_func = '''def scrape_thread(browser, thread_id: int, thread_href: str, expected_posts: int = 0, download_imgs: bool = True, download_materials_files: bool = True, forum_dir: Path = None, progress_callback=None) -> dict | None:
    normalized_href = normalize_thread_href(thread_href)
    url = f"{BASE_URL}/{normalized_href}".rstrip("/") + "/"
    log.info(f"  Тема {thread_id}: загружаю...")
    page = browser.new_page()
    try:
        html, page = safe_get(page, url)
        if not html:
            return None

        title = parse_thread_title(html)
        max_page = get_max_page(html)
        all_posts = parse_thread_page(html)
        if MAX_THREAD_PAGES > 0:
            max_page = min(max_page, MAX_THREAD_PAGES)

        def emit_progress(saved_pages: int):
            thread_data = {
                "thread_id": thread_id,
                "title": title,
                "url": url,
                "pages": max_page,
                "saved_pages": saved_pages,
                "expected_pages": max_page,
                "last_page_scraped": saved_pages,
                "posts_count": len(all_posts),
                "posts": all_posts,
                "scraped_at": datetime.now().isoformat(),
                "expected_posts": expected_posts,
            }
            summary = summarize_thread_data(thread_data, expected_posts)
            thread_data["status"] = summary["status"]
            if forum_dir:
                thread_file = forum_dir / f"{thread_id}.json"
                thread_file.write_text(json.dumps(thread_data, ensure_ascii=False, indent=2), encoding="utf-8")
            if progress_callback:
                progress_callback(
                    title=title,
                    saved_pages=saved_pages,
                    expected_pages=max_page,
                    posts_count=thread_data["posts_count"],
                    status=summary["status"],
                )
            return summary

        emit_progress(1)

        for pg in range(2, max_page + 1):
            delay()
            pg_html, page = safe_get(page, f"{url}page-{pg}")
            if pg_html:
                posts = parse_thread_page(pg_html)
                all_posts.extend(posts)
                log.info(f"    стр. {pg}/{max_page} — {len(posts)} постов")
                if pg == max_page or pg % 10 == 0:
                    emit_progress(pg)

        if download_imgs:
            img_count = sum(len(post.get("images", [])) for post in all_posts)
            if img_count > 0:
                save_dir = forum_dir if forum_dir else RAW_PATH
                images_dir = save_dir / f"{thread_id}_images"
                download_images(page, all_posts, images_dir)

        if download_materials_files:
            material_count = sum(len(post.get("material_links", [])) for post in all_posts)
            if material_count > 0:
                save_dir = forum_dir if forum_dir else RAW_PATH
                materials_dir = save_dir / f"{thread_id}_materials"
                download_materials(page, all_posts, materials_dir, BASE_URL, log)

        thread_data = {
            "thread_id": thread_id,
            "title": title,
            "url": url,
            "pages": max_page,
            "saved_pages": max_page,
            "expected_pages": max_page,
            "last_page_scraped": max_page,
            "posts_count": len(all_posts),
            "posts": all_posts,
            "scraped_at": datetime.now().isoformat(),
            "expected_posts": expected_posts,
        }
        summary = summarize_thread_data(thread_data, expected_posts)
        thread_data["status"] = summary["status"]
        if progress_callback:
            progress_callback(
                title=title,
                saved_pages=max_page,
                expected_pages=max_page,
                posts_count=thread_data["posts_count"],
                status=summary["status"],
            )
        return thread_data
    finally:
        try:
            page.close()
        except Exception:
            pass
'''

if old_func not in text:
    raise SystemExit('old scrape_thread not found')
text = text.replace(old_func, new_func)

old_call = '''        delay()
        thread_data = scrape_thread(
            browser,
            tid,
            thread_info["href"],
            expected_posts=int(thread_info.get("expected_posts", 0) or 0),
            download_imgs=download_imgs,
            download_materials_files=download_materials_files,
            forum_dir=forum_dir,
        )
        if thread_data and thread_data["posts_count"] > 0:
'''

new_call = '''        delay()
        progress["active_thread"] = {
            "forum_id": forum_id,
            "forum_name": forum_name,
            "thread_id": tid,
            "updated_at": datetime.now().isoformat(),
            "expected_posts": int(thread_info.get("expected_posts", 0) or 0),
        }
        save_progress(progress)

        def update_active_thread(**payload):
            active_thread = {
                **progress.get("active_thread", {}),
                **payload,
                "forum_id": forum_id,
                "forum_name": forum_name,
                "thread_id": tid,
                "updated_at": datetime.now().isoformat(),
                "expected_posts": int(thread_info.get("expected_posts", 0) or 0),
            }
            progress["active_thread"] = active_thread
            save_progress(progress)

        thread_data = scrape_thread(
            browser,
            tid,
            thread_info["href"],
            expected_posts=int(thread_info.get("expected_posts", 0) or 0),
            download_imgs=download_imgs,
            download_materials_files=download_materials_files,
            forum_dir=forum_dir,
            progress_callback=update_active_thread,
        )
        progress["active_thread"] = None
        save_progress(progress)
        if thread_data and thread_data["posts_count"] > 0:
'''

if old_call not in text:
    raise SystemExit('old scrape_forum call block not found')
text = text.replace(old_call, new_call)

path.write_text(text, encoding='utf-8')
print('patched', path)
