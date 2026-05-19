package dev.autosearch;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class CorpusLoaderTest {

    @Test
    void loads_corpus_without_embedding_field(@TempDir Path tmp) throws Exception {
        Path file = tmp.resolve("corpus.json");
        Files.writeString(file, """
            [
              {"service_id": 1, "category_id": 1, "title": "Password Reset", "summary": "Reset creds", "embedding": [0.1, 0.2]},
              {"service_id": 2, "category_id": 1, "title": "Account Unlock", "summary": "Unlock account"}
            ]
            """);

        List<Map<String, Object>> items = CorpusLoader.load(file.toString());

        assertEquals(2, items.size());
        assertFalse(items.get(0).containsKey("embedding"), "embedding field should be stripped");
        assertEquals("Password Reset", items.get(0).get("title"));
    }
}
