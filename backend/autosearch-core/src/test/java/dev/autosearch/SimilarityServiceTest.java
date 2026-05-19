package dev.autosearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class SimilarityServiceTest {

    private Path testConfig() throws URISyntaxException {
        return Path.of(getClass().getClassLoader().getResource("test-config.yaml").toURI());
    }

    @Test
    void searchReturnsTopResult(@TempDir Path tmp) throws Exception {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());

        List<Map<String, Object>> items = List.of(
            Map.of("service_id", 1, "category_id", 1, "title", "Password Reset",
                   "embedding", List.of(1.0, 0.0, 0.0)),
            Map.of("service_id", 2, "category_id", 1, "title", "Account Unlock",
                   "embedding", List.of(0.0, 1.0, 0.0))
        );
        Path embPath = tmp.resolve("data-items.json");
        new ObjectMapper().writeValue(embPath.toFile(), items);

        SimilarityService svc = new SimilarityService(embPath.toString(), cfg);
        float[] queryVec = {1.0f, 0.0f, 0.0f};
        List<SearchResult> results = svc.search(queryVec, 2);

        assertFalse(results.isEmpty());
        assertEquals(1, results.get(0).itemId());
    }

    @Test
    void search_filters_results_below_min_score(@TempDir Path tmp) throws Exception {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());

        List<Map<String, Object>> items = List.of(
            Map.of("service_id", 1, "category_id", 1, "title", "Item A",
                   "embedding", List.of(0.1, 0.0, 0.0)),
            Map.of("service_id", 2, "category_id", 1, "title", "Item B",
                   "embedding", List.of(0.2, 0.0, 0.0))
        );
        Path embPath = tmp.resolve("data-items.json");
        new ObjectMapper().writeValue(embPath.toFile(), items);

        SimilarityService svc = new SimilarityService(embPath.toString(), cfg);
        // Query vector that produces low scores: dot product with [0.1, 0.0, 0.0] = 0.01
        float[] queryVec = {0.1f, 0.0f, 0.0f};
        List<SearchResult> results = svc.search(queryVec, 10);

        assertTrue(results.isEmpty(), "Results below minScore threshold should be filtered");
    }

    @Test
    void search_with_topK_exceeding_corpus_size(@TempDir Path tmp) throws Exception {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());

        List<Map<String, Object>> items = List.of(
            Map.of("service_id", 1, "category_id", 1, "title", "Service A",
                   "embedding", List.of(1.0, 0.0, 0.0)),
            Map.of("service_id", 2, "category_id", 1, "title", "Service B",
                   "embedding", List.of(0.9, 0.0, 0.0)),
            Map.of("service_id", 3, "category_id", 1, "title", "Service C",
                   "embedding", List.of(0.8, 0.0, 0.0))
        );
        Path embPath = tmp.resolve("data-items.json");
        new ObjectMapper().writeValue(embPath.toFile(), items);

        SimilarityService svc = new SimilarityService(embPath.toString(), cfg);
        float[] queryVec = {1.0f, 0.0f, 0.0f};
        // Request 10 items but corpus has only 3
        List<SearchResult> results = svc.search(queryVec, 10);

        assertFalse(results.isEmpty());
        assertTrue(results.size() <= 3, "Result count should not exceed corpus size");
        assertEquals(3, results.size(), "All 3 items should match above minScore");
    }

    @Test
    void search_with_zero_vector_does_not_crash(@TempDir Path tmp) throws Exception {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());

        List<Map<String, Object>> items = List.of(
            Map.of("service_id", 1, "category_id", 1, "title", "Item A",
                   "embedding", List.of(1.0, 0.5, 0.3)),
            Map.of("service_id", 2, "category_id", 1, "title", "Item B",
                   "embedding", List.of(0.2, 0.8, 0.1))
        );
        Path embPath = tmp.resolve("data-items.json");
        new ObjectMapper().writeValue(embPath.toFile(), items);

        SimilarityService svc = new SimilarityService(embPath.toString(), cfg);
        // Zero vector: all elements 0.0
        float[] queryVec = {0.0f, 0.0f, 0.0f};
        List<SearchResult> results = svc.search(queryVec, 10);

        // Cosine of zero vector with any vector is 0, which is below default minScore (0.35)
        assertTrue(results.isEmpty(), "Zero vector should produce no matches");
    }
}
