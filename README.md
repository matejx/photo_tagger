## Photo Tagger

### Overview

This is a simple wxPython app to tag (categorize) your photos. The photo files
themselves are not touched - the tag database is kept in a json file.

### Quickstart

- Run the application.
- Add some photos via either "Photos/Add directory" or "Photos/Add files" menu.
- Define your tags via "Tags/Add" menu. Do not use commas in tag names (used in filtering).
- Select a photo from the left listview.
- The selected photo's preview will appear in the middle. Doubleclick the photo to view it in an external viewer.
- Select the appropriate tags for this photo in the right listview.
- Windows users have to hold Ctrl to select multiple tags, linux users do not.
- When done, save your database with "Tags/Save" menu.
- Close the application.
- Next time you can use "Tags/Open" menu to resume your work or use your tags for filtering.

### Filtering

Filtering is what the ultimate purpose of this endeavor is. Use "Filter/Tags" to filter.
The tags need to be entered manually i.e. in a text field. The first character in the
query string has a special meaning. Let's assume you have defined two tags, Nature and People.

Examples:
- "Nature" will display photos containing Nature (and possibly other tags)
- "Nature,People" will display photos containing both Nature AND People
- "|Nature,People" will display photos containing either Nature OR People
- "=Nature,People" will display photos containing exactly Nature and People and no other tags
- "!Nature" will display photos that do not contain Nature

You can copy the files currently listed to another directory via the "Photos/Copy to..." menu.
The idea here is to be able to quickly give some photos to a friend by first filtering by what
they're interested in and then copying the files somewhere (usually a USB drive).

You can also just create symlinks to the photos listed in some directory via the "Photos/Symlink to..." menu.
This is for when you want to use another program, f.ex. a proper photo viewer, on a number of filtered photos
and copying the files would be time consuming.

Pressing "Filter/All" will display all photos you have stored in your database.
Pressing "Filter/Untagged" will display all photos you have added but haven't defined any tags for.
