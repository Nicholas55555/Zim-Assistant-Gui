import zimply.zimply
import re
import easygui
import subprocess
import sys

namespace_descriptions = {
    "A": "Article",
    "B": "Deleted articles",
    "C": "Category entries",
    "I": "Images",
    "M": "Metadata",
    "S": "Stylesheets",
    "F": "Other files",
    "V": "Videos",
    "X": "Special entries"
}


def get_namespace_description(namespace):
    return namespace_descriptions.get(namespace, f"Unknown ({namespace})")


def extract_all_text(zim_file_path, output_file, namespace):
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx in range(zim_file.header_fields['articleCount']):
            entry = zim_file.read_directory_entry_by_index(idx)
            if entry['namespace'] == namespace:
                article = zim_file._get_article_by_index(idx)
                if article and article.data:
                    try:
                        text = article.data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = article.data.decode('latin-1', errors='ignore')
                    body = re.search(r"<body.*?>(.*?)</body>", text, re.S)
                    if body:
                        clean_text = re.sub('<[^<]+?>', '', body.group(1))
                        outfile.write(clean_text + "\n\n")
    zim_file.close()


def extract_titles(zim_file_path, namespace):
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    results = []
    for idx in range(zim_file.header_fields['articleCount']):
        entry = zim_file.read_directory_entry_by_index(idx)
        if entry['namespace'] == namespace:
            results.append((entry['url'], entry['title']))
    zim_file.close()
    return results


def save_selected_titles(results, output_file):
    if len(results) < 2:
        easygui.msgbox("Not enough choices to select from.", "Error")
        return

    choices = [f"{title} ({url})" for url, title in results]
    selected_choices = easygui.multchoicebox("Select titles to save:", "Title Selection", choices)

    if selected_choices:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for choice in selected_choices:
                selected_index = choices.index(choice)
                selected_url, selected_title = results[selected_index]
                outfile.write(f"Title: {selected_title}\nURL: {selected_url}\n\n")


def save_titles_to_file(zim_file_path, output_file_path, namespace):
    results = extract_titles(zim_file_path, namespace)
    if not results:
        easygui.msgbox("No titles found.", "Error")
        return

    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for url, title in results:
            outfile.write(f"Title: {title}\nURL: {url}\n\n")


def save_selected_articles(results, zim_file_path, output_file, namespace):
    if len(results) < 2:
        easygui.msgbox("Not enough choices to select from.", "Error")
        return

    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    choices = [title for _, title in results]
    selected_choices = easygui.multchoicebox("Select articles to save:", "Article Selection", choices)

    if selected_choices:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for choice in selected_choices:
                selected_index = choices.index(choice)
                selected_url, selected_title = results[selected_index]
                article = zim_file.get_article_by_url(namespace, selected_url, follow_redirect=True)
                if article and article.data:
                    try:
                        text = article.data.decode('utf-8')
                    except UnicodeDecodeError:
                        text = article.data.decode('latin-1', errors='ignore')
                    body = re.search(r"<body.*?>(.*?)</body>", text, re.S)
                    if body:
                        clean_text = re.sub('<[^<]+?>', '', body.group(1))
                        outfile.write(f"Title: {selected_title}\n\n{clean_text}\n\n")
                    else:
                        clean_text = re.sub('<[^<]+?>', '', text)
                        outfile.write(f"Title: {selected_title}\n\n{clean_text}\n\n")
    zim_file.close()


def view_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        easygui.textbox("File Content", "View File", content)


def urlopener(url):
    if url:
        try:
            if sys.platform == 'win32':
                subprocess.run(['start', url], check=True, shell=True)
            elif sys.platform == 'darwin':
                subprocess.run(['open', url], check=True)
            else:
                subprocess.run(['xdg-open', url], check=True)
            easygui.msgbox(f"Opening: {url}", "Success")
            return url
        except Exception as e:
            easygui.msgbox(f"Failed to open URL: {e}", "Error")
    else:
        easygui.msgbox("No URL entered", "Result")


def view_all_namespaces(zim_file_path):
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    namespaces = set()
    for idx in range(zim_file.header_fields['articleCount']):
        entry = zim_file.read_directory_entry_by_index(idx)
        namespaces.add(entry['namespace'])
    zim_file.close()
    return {ns: get_namespace_description(ns) for ns in namespaces}


def ask_to_open_file(output_file):
    if easygui.ynbox(f"File saved to {output_file}. Do you want to open it now?", "Open File", ("Yes", "No")):
        view_file(output_file)


stop = 0
while stop == 0:
    options = ["What is a Zim file? And how do I read it?",
               "Open kiwix web app to view content of and download Zim files",
               "Extract text content from Zim file",
               "Select and save titles/urls of articles/webpages in Zim file to file",
               "Save all titles/urls of articles/webpages inside a Zim file to file",
               "Select and save articles/webpages in Zim file to file",
               "Open file in GUI",
               "Create Zim file in browser with zimit.kiwix.org (Limit of 4GB for size of Zim file)",
               "Create Zim file using farm.openzim.org through github request",
               "Open farm.openzim.org to check status of and download Zim files",
               "Exit Zim-Assistant GUI"]

    choice = easygui.choicebox(msg="How can I help you?", title="Zim-Assistant GUI", choices=options)

    if choice == "What is a Zim file? And how do I read it?":
        easygui.msgbox("The ZIM file format stores website content for offline usage. It assembles the normal "
                       "constituent of a website into a single archive, and compresses it so as to make it easier to "
                       "save, share, and store.", "ZIM GUI")
        easygui.msgbox("You will need a ZIM file reader. This usually means Kiwix, which is available on desktop "
                       "computers, mobile devices, and more.", "ZIM GUI")
    if choice == "Open kiwix web app to view content of and download Zim files":
        urlopener("https://pwa.kiwix.org/www/index.html")
    elif choice == "Extract text content from Zim file":
        zim_file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted text", default="extracted_text.txt")
        namespaces = view_all_namespaces(zim_file_path)
        namespace_choices = [f"{ns} ({desc})" for ns, desc in namespaces.items()]
        namespace = easygui.choicebox("Select namespace to extract text from:", "Namespace Selection",
                                      namespace_choices)
        if namespace:
            namespace = namespace.split(" ")[0]
        easygui.msgbox("Press OK to extract all text. Another pop-up will appear when extraction is completed",
                       "ZIM GUI")
        extract_all_text(zim_file_path, output_file, namespace)
        easygui.msgbox(f"All text content has been extracted to {output_file}", "ZIM GUI")
        ask_to_open_file(output_file)
    elif choice == "Select and save titles/urls of articles/webpages in Zim file to file":
        zim_file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted titles/urls", default="selected_text.txt")
        namespaces = view_all_namespaces(zim_file_path)
        namespace_choices = [f"{ns} ({desc})" for ns, desc in namespaces.items()]
        namespace = easygui.choicebox("Select namespace to extract titles/urls from:", "Namespace Selection",
                                      namespace_choices)
        if namespace:
            namespace = namespace.split(" ")[0]
        easygui.msgbox("Press OK to extract titles. Another pop-up will appear when extraction is completed", "ZIM GUI")
        save_selected_titles(extract_titles(zim_file_path, namespace), output_file)
        easygui.msgbox(f"titles/urls of selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
        ask_to_open_file(output_file)
    elif choice == "Save all titles/urls of articles/webpages inside a Zim file to file":
        zim_file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for titles text", default="selected_text.txt")
        namespaces = view_all_namespaces(zim_file_path)
        namespace_choices = [f"{ns} ({desc})" for ns, desc in namespaces.items()]
        namespace = easygui.choicebox("Select namespace to extract titles/urls from:", "Namespace Selection",
                                      namespace_choices)
        if namespace:
            namespace = namespace.split(" ")[0]
        easygui.msgbox("Press OK to extract titles. Another pop-up will appear when extraction is completed", "ZIM GUI")
        save_titles_to_file(zim_file_path, output_file, namespace)
        easygui.msgbox(f"All titles/urls of selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
        ask_to_open_file(output_file)
    elif choice == "Select and save articles/webpages in Zim file to file":
        zim_file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted articles", default="selected_text.txt")
        namespaces = view_all_namespaces(zim_file_path)
        namespace_choices = [f"{ns} ({desc})" for ns, desc in namespaces.items()]
        namespace = easygui.choicebox("Select namespace to extract articles from:", "Namespace Selection",
                                      namespace_choices)
        if namespace:
            namespace = namespace.split(" ")[0]
        easygui.msgbox("Press OK to extract articles/webpages. Another pop-up will appear when extraction is completed",
                       "ZIM GUI")
        save_selected_articles(extract_titles(zim_file_path, namespace), zim_file_path, output_file, namespace)
        easygui.msgbox(f"All selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
        ask_to_open_file(output_file)
    elif choice == "Open file in GUI":
        openpath = easygui.fileopenbox("Select a file to open", "Open File")
        view_file(openpath)
    elif choice == "Create Zim file in browser with zimit.kiwix.org (Limit of 4GB for size of Zim file)":
        urlopener("https://zimit.kiwix.org/")
    elif choice == "Create Zim file using farm.openzim.org through github request":
        urlopener("https://github.com/openzim/zim-requests/issues/new?assignees=&labels=&projects=&template=new-zim"
                  "-request.md&title=New+request%3A+")
    elif choice == "Open farm.openzim.org to check status of and download Zim files":
        urlopener("https://farm.openzim.org/pipeline/filter-todo")
    elif choice == "Exit Zim-Assistant GUI":
        stop = 1
        easygui.msgbox("Exiting Zim-Assistant GUI", "Zim-Assistant GUI")
