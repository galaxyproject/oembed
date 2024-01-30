## Configuring Discourse

You must configure discourse to support this:

1. Go to Settings
1. Security
1. Allowed Iframes
1. Add `https://training.galaxyproject.org/`

## Developer Notes

There are some... specific issues with Discourse

- discourse’s onebox is weird and very picky
- “rich” embeds don't seem to work, only “video” type embeds.
- an iframe is **required**, I’ve made the height parameter (in the outer json) 1 which is doing a nice job of hiding it.
- you can still send HTML as long as there’s an iframe somewhere in there.
