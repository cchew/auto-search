package dev.autosearch;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public final class CorpusLoader {
    private CorpusLoader() {}

    public static List<Map<String, Object>> load(String path) throws IOException {
        List<Map<String, Object>> raw = new ObjectMapper().readValue(
            Path.of(path).toFile(), new TypeReference<>() {});
        for (Map<String, Object> item : raw) {
            item.remove("embedding");
        }
        return raw;
    }
}
