# Convert bookmarks to shortcuts within folders on disk
# Run with:
# python bookmarksshortcuts.py "C:\test\bookmarks.html" "C:\test\shortcuts"
#

import os
import re
from urllib.parse import urlparse
import argparse


def createShortcut(url, name, folderPath):
    """Create a shortcut for a given URL in the specified folder."""
    folderPath = folderPath.strip()
    print(f"createShortcut:{url}, {name}, '{folderPath}'")
    os.makedirs(folderPath, exist_ok=True)
    shortcutPath = os.path.join(folderPath, f"{name}.url")
    
    with open(shortcutPath, 'w') as shortcutFile:
        shortcutFile.write('[InternetShortcut]\n')
        shortcutFile.write(f'URL={url}\n')


def processFolder(lines, startIdx, outputFolder):
    if (startIdx >= len(lines)):
        raise Exception(f"Lines bounds exceeded {startIdx}")
    # print(f"processFolder: {outputFolder}")
    folderPattern = r'<DT><H3[^>]*>(.*?)</H3>'
    linkPattern = r'<DT><A HREF="([^"]*)"[^>]*>(.*?)</A>'
    i = startIdx
    while i < len(lines):
        line = lines[i].strip()
        # print(f"{i+1}: Line {line[:20]}")
        if line.startswith("<DT><A"):
            links = re.findall(linkPattern, line)
            for url, name in links:                
                name = re.sub(r'[<>:"/\\|?*]', '', name)[:50]  # Clean up name for valid filename, limit length and remove invalid chars
                if not name:
                    name = urlparse(url).netloc or "Unnamed"               
                name = name.strip()
                # print(f"createShortcut:{url}, {name}, {outputFolder}")
                createShortcut(url, name, outputFolder)
                i += 1
        elif line.startswith("<DT><H3"):
            folders = re.findall(folderPattern, line, re.DOTALL)
            folderName = re.sub(r'[<>:"/\\|?*.]', '', folders[0])[:50]   # Clean up for valid folder name
            folderName = folderName.strip()
            # print(f"processFolder:", folders[0])
            i = processFolder(lines, i+2, os.path.join(outputFolder, folderName))
            if (i<0):
                return
            i += 1
        elif line.startswith("</DL><p>"):
            return i
            
            
def parseBookmarks(filePath, outputFolder):
    """Parse Chrome bookmarks HTML file and create shortcuts in the specified folder."""
    with open(filePath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Initial skip
    startIdx=0
    for line in lines:
        line = line.strip()
        if line.startswith("<DT><A"):
            break
        startIdx+=1
    # print(startIdx)
    processFolder(lines, startIdx, outputFolder)
    

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert Chrome bookmarks to shortcuts.")
    parser.add_argument("bookmarksFile", help="Path to the Chrome bookmarks HTML file")
    parser.add_argument("outputFolder", help="Folder where shortcuts will be created")
    
    # Parse arguments
    args = parser.parse_args()

    # Ensure the output folder path is absolute
    outputFolder = os.path.abspath(args.outputFolder)
    
    # Run the conversion
    parseBookmarks(args.bookmarksFile, outputFolder)
    print(f"Shortcuts created successfully in {outputFolder}.")
