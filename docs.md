---
author: hexylena
---

# Developer Notes

There are some... specific issues with Discourse

- discourse’s onebox is weird and very picky
- “rich” embeds don't seem to work, only “video” type embeds.
- an iframe is **required**, I’ve made the height parameter (in the outer json) 1 which is doing a nice job of hiding it.
- you can still send HTML as long as there’s an iframe somewhere in there.

## Routes

`/oembed?format=json&url=...`

This is the expected response, note that it's full of HTML and then still an iframe that is hidden by `height: 1`

```json
{
  "author_name": "Galaxy Training Network",
  "author_url": "https://galaxy.training",
  "description": "GTN FAQ Entry",
  "height": 1,
  "html": "\n            <section style=\"border: 1px solid #2c3143; box-shadow: 5px 6px #b2b2b2;margin:1rem 0;\">\n            <div style=\"border-bottom: 3px solid #2c3143; padding:0.8rem;display: flex; justify-content: space-between; align-items: center;\">\n                <span>\n                    Content from\n                    <a href=\"https://training.galaxyproject.org/training-material/faqs/gtn/issues_galaxy.html?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed\">FAQ: What information should I include when reporting a problem?</a>\n                </span>\n                <span>\n                    <img src=\"https://training.galaxyproject.org/training-material/assets/images/GTN-60px.png\" style=\"height: 30px; width: 30px;\" alt=\"Galaxy Training Network logo\"> <a href=\"https://training.galaxyproject.org/training-material/?utm_source=galaxy-help&utm_medium=oembed&utm_campaign=oembed\">Galaxy Training!</a>\n                </span>\n            </div>\n            <div style=\"padding: 0.8rem;\">\n            <div class=\"col-md-8\" itemprop=\"text\">\n<p>Writing bug reports is a good skill to have as bioinformaticians, and a key point is that you should include enough information from the first message to help the process of resolving your issue more efficient and a better experience for everyone.</p>\n<p><strong>What to include</strong></p>\n<ol>\n<li>Which commands did you run, precisely, we want details. Which flags did you set?</li>\n<li>Which server(s) did you run those commands on?</li>\n<li>What account/username did you use?</li>\n<li>Where did it go wrong?</li>\n<li>What were the stdout/stderr of the tool that failed? Include the text.</li>\n<li>Did you try any workarounds? What results did those produce?</li>\n<li>(If relevant) screenshot(s) that show exactly the problem, if it cannot be described in text. Is there a details panel you could include too?</li>\n<li>If there are job IDs, please include them as text so administrators don’t have to manually transcribe the job ID in your picture.</li>\n</ol>\n<p>It makes the process of answering ‘bug reports’ much smoother for us, as we will have to ask you these questions anyway. If you provide this information from the start, we can get straight to answering your question!</p>\n<p><strong>What does a GOOD bug report look like?</strong></p>\n<p>The people who provide support for Galaxy are largely volunteers in this community, so try and provide as much information up front to avoid wasting their time:</p>\n<blockquote class=\"quote\">\n<p>I encountered an issue: I was working on (this server&gt; and trying to run (tool)+(version number) but all of the output files were empty. My username is jane-doe.</p>\n<p>Here is everything that I know:</p>\n<ul>\n<li>The dataset is green, the job did not fail</li>\n<li>This is the standard output/error of the tool that I found in the information page (insert it here)</li>\n<li>I have read it but I do not understand what X/Y means.</li>\n<li>The job ID from the output information page is 123123abdef.</li>\n<li>I tried re-running the job and changing parameter Z but it did not change the result.</li>\n</ul>\n<p>Could you help me?</p>\n</blockquote>\n</div>\n            </div>\n            <iframe width=\"1\" height=\"1\" sandbox=\"allow-same-origin allow-scripts\" title=\"min\" src=\"https://training.galaxyproject.org/\" frameborder=\"0\" allowfullscreen></iframe></section>\n        ",
  "provider_name": "GTN",
  "provider_url": "https://galaxy.training",
  "title": "Test Title",
  "type": "video",
  "version": "1.0",
  "width": 560
}
```
