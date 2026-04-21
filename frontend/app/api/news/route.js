import Parser from 'rss-parser';
import { NextResponse } from 'next/server';

const parser = new Parser();

export async function GET() {
  try {
    const feed = await parser.parseURL('https://feeds.feedburner.com/TheHackersNews');
    
    const grcKeywords = [
      'compliance', 'governance', 'risk', 'grc', 'iso 27001', 'nist', 
      'pci dss', 'hipaa', 'regulation', 'regulatory', 'audit', 'gdpr', 
      'ciso', 'policy', 'framework'
    ];

    const isGRC = (text) => {
      if (!text) return false;
      const lower = text.toLowerCase();
      return grcKeywords.some(kw => lower.includes(kw));
    };

    // Separate matching and non-matching articles
    const matchedItems = [];
    const otherItems = [];

    for (const item of feed.items) {
      if (isGRC(item.title) || isGRC(item.contentSnippet) || isGRC(item.content)) {
        matchedItems.push(item);
      } else {
        otherItems.push(item);
      }
    }

    // Combine prioritizing matched items, then format the top 4
    const selectedItems = [...matchedItems, ...otherItems].slice(0, 4);

    const articles = selectedItems.map(item => ({
      title: item.title,
      link: item.link,
      date: item.pubDate,
      source: feed.title || 'The Hacker News',
    }));

    return NextResponse.json(articles);
  } catch (error) {
    console.error('Error fetching RSS feed:', error);
    return NextResponse.json({ error: 'Failed to fetch news' }, { status: 500 });
  }
}
