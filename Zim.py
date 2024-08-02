import zimply.zimply
import re
import easygui
import subprocess
import sys


# Function to extract all text content
# Function to extract all text content
def extract_all_text(zim_file_path, output_file):
    # Open the ZIM file
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Iterate over all articles
        for idx in range(zim_file.header_fields['articleCount']):
            # Get the Directory Entry
            entry = zim_file.read_directory_entry_by_index(idx)
            if entry['namespace'] == "A":
                # Get the article data
                article = zim_file._get_article_by_index(idx)
                if article and article.data:
                    # Decode the article data
                    text = article.data.decode('utf-8', errors='ignore')
                    # Extract the body content using regex
                    body = re.search(r"<body.*?>(.*?)</body>", text, re.S)
                    if body:
                        # Clean the text content from HTML tags
                        clean_text = re.sub('<[^<]+?>', '', body.group(1))
                        outfile.write(clean_text + "\n\n")

    zim_file.close()


def search_in_zim_file(zim_file_path):
    # Open the ZIM file
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    results = []

    # Iterate over all articles
    for idx in range(zim_file.header_fields['articleCount']):
        # Get the Directory Entry
        entry = zim_file.read_directory_entry_by_index(idx)
        if entry['namespace'] == "A":
            # Get the article data
            article = zim_file._get_article_by_index(idx)
            if article and article.data:
                # Decode the article data
                text = article.data.decode('utf-8', errors='ignore')
                # Check if keyword is in the text

    zim_file.close()
    return results


def extract_titles(zim_file_path):
    # Open the ZIM file
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    results = []

    # Iterate over all articles
    for idx in range(zim_file.header_fields['articleCount']):
        # Get the Directory Entry
        entry = zim_file.read_directory_entry_by_index(idx)
        if entry['namespace'] == "A":
            results.append((entry['url'], entry['title']))

    zim_file.close()
    return results


def save_selected_titles(results, output_file):
    # Create a list of titles for the multchoicebox
    choices = [f"{title} ({url})" for url, title in results]

    # Display multchoicebox for user to select titles
    selected_choices = easygui.multchoicebox("Select titles to save:", "Title Selection", choices)

    if selected_choices:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for choice in selected_choices:
                # Extract the index of the selected choice
                selected_index = choices.index(choice)
                # Get the corresponding title
                selected_url, selected_title = results[selected_index]
                # Write the title and URL to the file
                outfile.write(f"Title: {selected_title}\nURL: {selected_url}\n\n")


def save_titles_to_file(zim_file_path, output_file_path):
    # Open the ZIM file
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')
    results = []

    # Iterate over all articles
    for idx in range(zim_file.header_fields['articleCount']):
        entry = zim_file.read_directory_entry_by_index(idx)
        if entry['namespace'] == "A":
            results.append((entry['url'], entry['title']))

    zim_file.close()

    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for url, title in results:
            outfile.write(f"Title: {title}\nURL: {url}\n\n")


def view_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        easygui.textbox("File Content", "View File", content)


def save_selected_articles(results, zim_file_path, output_file):
    zim_file = zimply.zimply.ZIMFile(zim_file_path, encoding='utf-8')

    # Create a list of titles for the multchoicebox
    choices = [title for _, title in results]

    # Display multchoicebox for user to select articles
    selected_choices = easygui.multchoicebox("Select articles to save:", "Article Selection", choices)

    if selected_choices:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for choice in selected_choices:
                # Extract the index of the selected choice
                selected_index = choices.index(choice)
                # Get the corresponding article URL
                selected_url, selected_title = results[selected_index]
                article = zim_file.get_article_by_url("A", selected_url, follow_redirect=True)

                if article and article.data:
                    text = article.data.decode('utf-8', errors='ignore')
                    # Extract the body content using regex
                    body = re.search(r"<body.*?>(.*?)</body>", text, re.S)
                    if body:
                        # Clean the text content from HTML tags
                        clean_text = re.sub('<[^<]+?>', '', body.group(1))
                        outfile.write(f"Title: {selected_title}\n\n{clean_text}\n\n")
                    else:
                        # If no body tag is found, save the whole content
                        clean_text = re.sub('<[^<]+?>', '', text)
                        outfile.write(f"Title: {selected_title}\n\n{clean_text}\n\n")

    zim_file.close()


def view_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        easygui.textbox("File Content", "View File", content)


def urlopener(url):
    if url:
        try:
            # Open the URL using the default web browser
            if sys.platform == 'win32':
                # Windows
                subprocess.run(['start', url], check=True, shell=True)

            elif sys.platform == 'darwin':
                # macOS
                subprocess.run(['open', url], check=True)
            else:
                # Linux and other UNIX-like systems
                subprocess.run(['xdg-open', url], check=True)

            easygui.msgbox(f"Opening: {url}", "Success")
            return url
        except Exception as e:
            easygui.msgbox(f"Failed to open URL: {e}", "Error")
    else:
        easygui.msgbox("No URL entered", "Result")


stop = 0
while stop == 0:

    # Define the list of options
    options = ["What is a Zim file? And how do I read it?",
               "Open kiwix web app to view content of and download Zim files",
               "Extract text content from Zim file",
               "Select and save titles/urls of articles/webpages in Zim file to file",
               "Save all titles/urls of articles/webpages inside a Zim file to file",
               "Select and save articles/webpages in Zim file to file",
               "Open file in GUI",
               "Create Zim file in browser with zimit.kiwix.org (Limit of 4GB for size of Zim file)",
               "Create Zim file using farm.openzim.org through github request",
               "Open farm.openzim.org to check status of and download Zim files", "Exit Zim-Assistant GUI"]

    # Display the choicebox
    choice = easygui.choicebox(msg="How can I help you?", title="Zim-Assistant GUI", choices=options)

    # Perform an action based on the user's choice
    if choice == "What is a Zim file? And how do I read it?":
        easygui.msgbox("The ZIM file format stores website content for offline usage. It assembles the normal "
                       "constituent of a website into a single archive, and compresses it so as to make it easier to "
                       "save, share, and store.", "ZIM GUI")
        easygui.msgbox("You will need a ZIM file reader. This usually means Kiwix, which is available on desktop "
                       "computers, mobile devices, and more.", "ZIM GUI")
    if choice == "Open kiwix web app to view content of and download Zim files":
        urlopener("https://pwa.kiwix.org/www/index.html")
    elif choice == "Extract text content from Zim file":
        zim_file_path = file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted text", default="extracted_text.txt")
        easygui.msgbox("Press OK to extract all text. Another pop-up will appear when extraction is completed",
                       "ZIM GUI")
        extract_all_text(zim_file_path, output_file)
        easygui.msgbox(f"All text content has been extracted to {output_file}", "ZIM GUI")
    elif choice == "Select and save titles/urls of articles/webpages in Zim file to file":
        zim_file_path = file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted titles/urls", default="selected_text.txt")
        easygui.msgbox("Press OK to extract titles. Another pop-up will appear when extraction is completed", "ZIM GUI")
        save_selected_titles(extract_titles(zim_file_path), output_file)
        easygui.msgbox(f"titles/urls of selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
    elif choice ==  "Save all titles/urls of articles/webpages inside a Zim file to file":
        zim_file_path = file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for titles text", default="selected_text.txt")
        easygui.msgbox("Press OK to extract titles. Another pop-up will appear when extraction is completed", "ZIM GUI")
        save_titles_to_file(zim_file_path, output_file)
        easygui.msgbox(f"All titles/urls of selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
    elif choice == "Select and save articles/webpages in Zim file to file":
        zim_file_path = file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create a file for extracted articles", default="selected_text.txt")
        easygui.msgbox("Press OK to extract articles/webpages. Another pop-up will appear when extraction is completed",
                       "ZIM GUI")
        save_selected_articles(extract_titles(zim_file_path), zim_file_path, output_file)
        easygui.msgbox(f"All selected articles/webpages has been extracted to {output_file}", "ZIM GUI")
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
