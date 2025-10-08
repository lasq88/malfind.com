# Malfind Labs Blog

A professional Hugo-based blog for malware analysis and AI research, featuring a dark theme, search functionality, and automated GitHub Pages deployment.

## Features

- **Dark Theme**: Optimized for technical content with syntax highlighting
- **Search**: Built-in search functionality with JSON index
- **Categories & Tags**: Organized content with taxonomy support
- **RSS Feed**: Automatic RSS feed generation
- **Responsive Design**: Mobile-friendly layout
- **Fast Loading**: Optimized Hugo static site generation

## Local Development

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) (latest version)
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/malfind.com.git
cd malfind.com
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
# or
hugo server -D
```

4. Open your browser to `http://localhost:1313`

### Building for Production

```bash
npm run build
# or
hugo --gc --minify
```

## Adding New Posts

### Create a New Post

1. Create a new markdown file in `content/posts/`:
```bash
hugo new posts/your-post-title.md
```

2. Edit the frontmatter in your new post:
```yaml
---
title: "Your Post Title"
date: 2024-01-15T10:00:00Z
draft: false
categories: ["malware-analysis", "ai"]
tags: ["malware", "machine-learning", "security"]
summary: "Brief description of your post"
---
```

3. Write your content in Markdown format

### Post Categories

Use these predefined categories:
- `malware-analysis`: Malware analysis techniques and tools
- `ai`: Artificial intelligence and machine learning
- `research`: Research papers and findings
- `tools`: Security tools and utilities

### Post Tags

Common tags to use:
- `malware`, `analysis`, `reverse-engineering`
- `ai`, `machine-learning`, `deep-learning`
- `security`, `cybersecurity`, `threats`
- `tools`, `automation`, `detection`

## Customization

### Theme Customization

The blog uses a custom PaperMod theme located in `themes/PaperMod/`. Key files:

- `themes/PaperMod/static/css/style.css`: Main stylesheet
- `themes/PaperMod/layouts/`: HTML templates
- `config.toml`: Site configuration

### Adding New Pages

1. Create a new markdown file in `content/`:
```bash
hugo new your-page.md
```

2. Edit the frontmatter and content

### Custom CSS

Add custom styles to `themes/PaperMod/static/css/style.css` or create new CSS files in the `static/css/` directory.

## Deployment

The blog is automatically deployed to GitHub Pages when you push to the `main` branch.

### Manual Deployment

1. Build the site:
```bash
hugo --gc --minify
```

2. The built site will be in the `public/` directory

### Custom Domain

The `CNAME` file is configured for `malfind.com`. To change the domain:

1. Update `CNAME` file with your domain
2. Update `baseURL` in `config.toml`
3. Configure DNS settings with your domain provider

## Content Guidelines

### Writing Style

- Use clear, technical language appropriate for security professionals
- Include code examples with proper syntax highlighting
- Provide practical, actionable information
- Cite sources and references when appropriate

### Code Examples

Use fenced code blocks with language specification:

````markdown
```python
def analyze_malware(sample):
    # Your code here
    return result
```
````

### Images

Place images in the `static/images/` directory and reference them:

```markdown
![Alt text](/images/your-image.png)
```

## Site Structure

```
malfind.com/
├── .github/workflows/     # GitHub Actions
├── content/              # Content files
│   ├── posts/           # Blog posts
│   └── about.md         # About page
├── static/              # Static assets
├── themes/PaperMod/     # Custom theme
├── config.toml          # Site configuration
├── CNAME               # Custom domain
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Hugo not found**: Install Hugo Extended from the official website
2. **Theme not loading**: Ensure the PaperMod theme is properly installed
3. **Build errors**: Check your Markdown syntax and frontmatter

### Getting Help

- [Hugo Documentation](https://gohugo.io/documentation/)
- [PaperMod Theme](https://github.com/adityatelange/hugo-PaperMod)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `hugo server -D`
5. Submit a pull request

## License

This blog template is open source. Feel free to use and modify for your own projects.

---

*Built with Hugo and deployed on GitHub Pages*

