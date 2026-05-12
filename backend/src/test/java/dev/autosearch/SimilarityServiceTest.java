package dev.autosearch;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

class SimilarityServiceTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private SimilarityService makeService(List<Map<String, Object>> items, Path dir)
            throws IOException {
        Path p = dir.resolve("data-items.json");
        MAPPER.writeValue(p.toFile(), items);
        return new SimilarityService(p.toString());
    }

    @Test
    void search_returnsMatchAboveThreshold(@TempDir Path tmp) throws IOException {
        var items = List.of(
            Map.<String, Object>of("item_id", 1, "wpp_id", 1, "name", "GP FTE",
                "embedding", List.of(1.0, 0.0, 0.0)),
            Map.<String, Object>of("item_id", 2, "wpp_id", 2, "name", "RN FTE",
                "embedding", List.of(0.0, 1.0, 0.0))
        );
        var svc = makeService(items, tmp);
        var results = svc.search(new float[]{1.0f, 0.0f, 0.0f}, 5);
        assertThat(results).hasSize(1);
        assertThat(results.get(0).itemId()).isEqualTo(1);
        assertThat(results.get(0).score()).isGreaterThan(0.4f);
    }

    @Test
    void search_suppressesAllResultsBelowMinScore(@TempDir Path tmp) throws IOException {
        var items = List.of(
            Map.<String, Object>of("item_id", 1, "wpp_id", 1, "name", "GP FTE",
                "embedding", List.of(0.0, 1.0, 0.0))
        );
        var svc = makeService(items, tmp);
        var results = svc.search(new float[]{1.0f, 0.0f, 0.0f}, 5);
        assertThat(results).isEmpty();
    }

    @Test
    void cosine_orthogonalVectorsReturnZero() {
        assertThat(SimilarityService.cosine(new float[]{1, 0}, new float[]{0, 1}))
            .isCloseTo(0.0f, within(1e-6f));
    }

    @Test
    void cosine_identicalUnitVectorsReturnOne() {
        assertThat(SimilarityService.cosine(new float[]{1, 0}, new float[]{1, 0}))
            .isCloseTo(1.0f, within(1e-6f));
    }
}
