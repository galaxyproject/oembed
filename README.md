# Galaxy OEmbed Server

> oEmbed is a format for allowing an embedded representation of a URL on third party sites. The simple API allows a website to display embedded content (such as photos or videos) when a user posts a link to that resource, without having to parse the resource directly.

This server processes selected pages for embedding within Discourse (and other sites) via exposing an [OEmbed](https://oembed.com/) endpoint.

When you post a supported URL in e.g. Discourse, then the contents of that URL can be rendered in a nicer format that's more useful for end users.

![screenshot of a discourse post, a black and white box shows "FAQ: Créer un nouvel history" and the contents of the FAQ](screenshot.png)

## Supported URLs

- `https://training.galaxyproject.org/training-material/faqs/**/*.html`
- Something else here? File an issue!

## Enabling OEmbed for specific URLs

1. Simply add this header, with the full URL of that page.

   ```html
   <link rel="alternate" type="application/json+oembed" href="https://oembed.apps.galaxyproject.eu/oembed?format=json&url=https://training.galaxyproject.org/training-material/faqs/galaxy/histories_copy_dataset.html" title="oEmbed Profile" />
   ```

1. And then implement support in the `server.py` to support that URL (more complicated :) )

## Configuring Discourse

You must configure discourse to support this:

1. Go to Settings
1. Security
1. Allowed Iframes
1. Add `https://training.galaxyproject.org/`


## LICENSE

AGPL-3.0-or-later

