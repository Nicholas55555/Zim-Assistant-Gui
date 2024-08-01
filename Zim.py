import zimply.zimply
import re
import easygui
import subprocess
import sys


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
    print()


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
    options = ["Open kiwix web app to view content of and download Zim files", "Extract text content from Zim file",
               "Create Zim file in browser with zimit.kiwix.org (Limit of 4GB for size of Zim file)",
               "Create Zim using farm.openzim.org through github request",
               "Open farm.openzim.org to check status of and download Zim files", "Exit Zim-Assistant GUI"]

    # Display the choicebox
    choice = easygui.choicebox(msg="How can I help you?", title="Zim-Assistant GUI", choices=options)

    # Perform an action based on the user's choice
    if choice == "Open kiwix web app to view content of and download Zim files":
        urlopener("https://pwa.kiwix.org/www/index.html")
    elif choice == "Extract text content from Zim file":
        zim_file_path = file_path = easygui.fileopenbox(title="Select a Zim file", default="*.zim")
        output_file = easygui.filesavebox(title="Create file for extracted text", default="extracted_text.txt")
        easygui.msgbox("Press OK to extract. Another pop-up will appear when extraction is completed", "ZIM GUI")
        extract_all_text(zim_file_path, output_file)
        easygui.msgbox(f"All text content has been extracted to {output_file}", "ZIM GUI")
    elif choice == "Create Zim file in browser with zimit.kiwix.org (Limit of 4GB for size of Zim file)":
        urlopener("https://zimit.kiwix.org/")
    elif choice == "Create Zim using farm.openzim.org through github request":
        urlopener("https://github.com/openzim/zim-requests/issues/new?assignees=&labels=&projects=&template=new-zim"
                  "-request.md&title=New+request%3A+")
    elif choice == "Open farm.openzim.org to check status of and download Zim files":
        urlopener("https://farm.openzim.org/pipeline/filter-todo")
    elif choice == "Exit Zim-Assistant GUI":
        stop = 1
        easygui.msgbox("Exiting Zim-Assistant GUI", "Zim-Assistant GUI")
    else:
        easygui.msgbox("No option selected. Exiting...", "Zim-Assistant GUI")

