# Task: Write Blog Post

## Input Variables

- `{topic}` — the main topic or title idea
- `{target_audience}` — which persona this is for (see audience_personas.md)
- `{word_count}` — target word count (default: 800)
- `{keywords}` — SEO keywords to include naturally (comma-separated)
- `{tone_notes}` — any additional tone guidance beyond the brand voice baseline

## Prompt Template

Write a blog post for **{target_audience}** on the topic: **{topic}**.

Requirements:
- Word count: approximately {word_count} words
- Include these keywords naturally (do not keyword-stuff): {keywords}
- Tone: follow the brand voice guidelines, with these additional notes: {tone_notes}
- Structure: Introduction → 3–4 body sections with H2 headings → Conclusion with CTA
- Include one concrete example or case study
- End with a "Key takeaways" bullet list (3–5 bullets)

Output format:
```
[TITLE]
<suggested headline>

[META DESCRIPTION]
<155-character meta description for SEO>

[BODY]
<full blog post in markdown>

[SUGGESTED TAGS]
<comma-separated list of 3–5 tags>
```
