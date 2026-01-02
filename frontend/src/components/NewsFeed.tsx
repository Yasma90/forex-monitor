'use client';

import { ExternalLink, TrendingUp, TrendingDown, Minus, Newspaper } from 'lucide-react';
import { NewsArticle } from '@/lib/api';

interface NewsFeedProps {
  articles: NewsArticle[];
  loading: boolean;
}

export default function NewsFeed({ articles, loading }: NewsFeedProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (hours < 1) return 'Hace menos de 1 hora';
    if (hours < 24) return `Hace ${hours}h`;
    const days = Math.floor(hours / 24);
    return `Hace ${days}d`;
  };

  const getSentimentIcon = (label: string | null) => {
    switch (label) {
      case 'positive':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getSentimentColor = (label: string | null) => {
    switch (label) {
      case 'positive':
        return 'bg-green-50 border-green-200';
      case 'negative':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading && articles.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Newspaper className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Noticias Relevantes</h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse p-4 bg-gray-50 rounded-lg">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Newspaper className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Noticias Relevantes</h3>
        </div>
        <p className="text-gray-500 text-center py-8">
          No hay noticias disponibles. Configura tus API keys en el backend.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Newspaper className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Noticias Relevantes</h3>
        </div>
        <span className="text-sm text-gray-500">{articles.length} articulos</span>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {articles.map((article) => (
          <a
            key={article.id}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`block p-4 rounded-lg border transition-all hover:shadow-md ${getSentimentColor(article.sentiment_label)}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 line-clamp-2 mb-1">
                  {article.title}
                </h4>
                {article.description && (
                  <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                    {article.description}
                  </p>
                )}
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="font-medium">{article.source}</span>
                  <span>{formatDate(article.published_at)}</span>
                  {article.keywords_matched && (
                    <span className="hidden sm:inline truncate max-w-[200px]">
                      {article.keywords_matched.split(',').slice(0, 3).join(', ')}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex flex-col items-center gap-1">
                {getSentimentIcon(article.sentiment_label)}
                {article.sentiment_score !== null && (
                  <span className="text-xs text-gray-500">
                    {(article.sentiment_score * 100).toFixed(0)}%
                  </span>
                )}
                <ExternalLink className="w-3 h-3 text-gray-400" />
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
