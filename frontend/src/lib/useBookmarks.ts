"use client";

import { useState, useEffect } from "react";

export interface BookmarkedItem {
  id: string;
  type: "material" | "paper";
  title: string;
  subtitle?: string;
  url: string;
  timestamp: number;
}

const STORAGE_KEY = "crystagraph_pinned_items";

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState<BookmarkedItem[]>([]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setBookmarks(JSON.parse(saved));
      }
    } catch {
      // ignore JSON parse or localStorage disabled
    }
  }, []);

  const saveBookmarks = (items: BookmarkedItem[]) => {
    setBookmarks(items);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
      // ignore
    }
  };

  const isBookmarked = (id: string) => {
    return bookmarks.some((b) => b.id === id);
  };

  const toggleBookmark = (item: Omit<BookmarkedItem, "timestamp">) => {
    if (isBookmarked(item.id)) {
      saveBookmarks(bookmarks.filter((b) => b.id !== item.id));
    } else {
      const newItem: BookmarkedItem = {
        ...item,
        timestamp: Date.now(),
      };
      saveBookmarks([newItem, ...bookmarks].slice(0, 20)); // Keep up to 20 bookmarks
    }
  };

  return {
    bookmarks,
    isBookmarked,
    toggleBookmark,
  };
}

