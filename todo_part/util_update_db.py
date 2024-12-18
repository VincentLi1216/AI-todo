import urllib.parse
import webbrowser

def execute_url(url):
    try:
        # 嘗試打開 URL
        print(f"Executing URL: {url}")
        result = webbrowser.open(url)
        # 檢查操作是否成功
        if result:
            # print("URL was successfully opened in the browser.")
            pass
        else:
            print("Failed to open URL. The browser might be unavailable or unsupported.")
    except Exception as e:
        # 打印錯誤訊息
        print(f"An error occurred: {e}")

def create_things_todo(title=None, titles=None, notes=None, when=None, tags=None, checklist_items=None,
                      use_clipboard=None, list_id=None, list_name=None, heading_id=None, heading=None,
                      completed=False, canceled=False, show_quick_entry=False, reveal=False, 
                      creation_date=None, completion_date=None):
    base_url = "things:///add?"
    params = {}

    # Handling single or multiple titles
    if titles:
        params['titles'] = urllib.parse.quote(titles)
    elif title:
        params['title'] = urllib.parse.quote(title)

    if notes:
        params['notes'] = urllib.parse.quote(notes)
    if when:
        params['when'] = urllib.parse.quote(when)
    if tags:
        params['tags'] = urllib.parse.quote(tags)
    if checklist_items:
        params['checklist-items'] = urllib.parse.quote(checklist_items)
    if use_clipboard:
        params['use-clipboard'] = use_clipboard
    if list_id:
        params['list-id'] = list_id
    if list_name:
        params['list'] = urllib.parse.quote(list_name)
    if heading_id:
        params['heading-id'] = heading_id
    if heading:
        params['heading'] = urllib.parse.quote(heading)
    if completed:
        params['completed'] = 'true'
    if canceled:
        params['canceled'] = 'true'
    if show_quick_entry:
        params['show-quick-entry'] = 'true'
    if reveal:
        params['reveal'] = 'true'
    if creation_date:
        params['creation-date'] = creation_date
    if completion_date:
        params['completion-date'] = completion_date

    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    url = base_url + query_string
    execute_url(url)

if __name__ == "__main__":
    create_things_todo(title="Book flights", notes="Check various airlines.", when="tomorrow")

