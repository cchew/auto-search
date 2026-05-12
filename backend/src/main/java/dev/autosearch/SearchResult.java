package dev.autosearch;

public record SearchResult(int wppId, int itemId, String itemName, float score) {}
