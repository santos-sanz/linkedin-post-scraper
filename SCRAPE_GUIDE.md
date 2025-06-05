# LinkedIn Post Data Structure

LinkedIn embeds feed information inside hidden `<code>` elements whose `id` attribute starts with `bpr-guid-`. Each code tag contains JSON data. Post entries can be found in `feedDashMainFeedByMainFeed['*elements']` and details about each post are referenced by URN identifiers under the `included` list.

Key fields within each post structure include:

- `actor.name.text` – the profile name of the post author.
- `commentary.text.text` – the post content.
- `contextualHeader.text.text` or `header.text.text` – optional header info such as who liked or shared.
- Timestamps such as `createdAt` or `publishedAt` – expressed as integers (milliseconds since epoch).

To scrape posts, parse the HTML with BeautifulSoup and locate these `<code>` blocks. Decode the JSON, build an index of objects in `included`, and combine the information referenced in `*elements` to assemble each post. The provided `linkedin_feed_parser.py` script demonstrates this approach and converts timestamps to ISO format.

Additional fields captured by the parser include:

- **id** – the post's URN identifier (`shareUrn` or `entityUrn`).
- **author_url** – profile or company URL for the author.
- **like_count**, **comment_count**, **share_count** – social engagement numbers.
- **reaction_counts** – dictionary mapping reaction type to count (e.g., `LIKE`, `PRAISE`).

Check `posts.json` for an example of the parsed output.
