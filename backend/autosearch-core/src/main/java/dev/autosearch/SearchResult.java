package dev.autosearch;

public record SearchResult(int groupId, int itemId, String itemName, float score) {}
