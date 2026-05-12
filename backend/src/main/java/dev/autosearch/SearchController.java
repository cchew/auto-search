package dev.autosearch;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/search")
public class SearchController {

    private static final Logger log = LoggerFactory.getLogger(SearchController.class);

    private final EmbeddingService embeddingService;
    private final SimilarityService similarityService;

    public SearchController(EmbeddingService embeddingService, SimilarityService similarityService) {
        this.embeddingService = embeddingService;
        this.similarityService = similarityService;
    }

    record SearchRequest(String query, int topK) {}

    @PostMapping
    public ResponseEntity<List<SearchResult>> search(@RequestBody SearchRequest request) {
        try {
            float[] vec = embeddingService.embed(request.query());
            List<SearchResult> results = similarityService.search(vec, request.topK());
            if (results.isEmpty()) {
                log.warn("No results above threshold for query: '{}'", request.query());
            }
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            log.error("Search failed for query '{}': {}", request.query(), e.getMessage(), e);
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
