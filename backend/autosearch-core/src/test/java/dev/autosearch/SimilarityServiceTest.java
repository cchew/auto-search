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
}
