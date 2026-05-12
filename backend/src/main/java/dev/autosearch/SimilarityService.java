package dev.autosearch;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

@Service
public class SimilarityService {

    private static final Logger log = LoggerFactory.getLogger(SimilarityService.class);
    static final float MIN_SCORE = 0.3f;

    private final List<DataItem> items;

    public SimilarityService(@Value("${search.embeddings.path}") String embeddingsPath)
            throws IOException {
        log.info("Loading embeddings from {}", embeddingsPath);
        List<Map<String, Object>> raw = new ObjectMapper().readValue(
            Path.of(embeddingsPath).toFile(), new TypeReference<>() {});
        this.items = raw.stream().map(DataItem::fromMap).toList();
        log.info("SimilarityService ready: {} items", items.size());
    }

    public List<SearchResult> search(float[] queryVector, int topK) {
        record Scored(DataItem item, float score) {}
        List<Scored> scored = items.stream()
            .map(i -> new Scored(i, cosine(queryVector, i.embedding())))
            .sorted(Comparator.comparingDouble(Scored::score).reversed())
            .toList();

        List<SearchResult> results = new ArrayList<>();
        for (Scored s : scored.subList(0, Math.min(topK, scored.size()))) {
            if (s.score() < MIN_SCORE) break;
            results.add(new SearchResult(s.item().wppId(), s.item().itemId(), s.item().name(), s.score()));
        }

        if (results.isEmpty()) {
            float topScore = scored.isEmpty() ? 0f : scored.get(0).score();
            log.warn("Search suppressed: all results below minScore={} (top score={})",
                MIN_SCORE, topScore);
        }
        return results;
    }

    /**
     * Dot product of two vectors. Assumes both a and b are L2-normalised
     * (unit vectors), giving cosine similarity without a division step.
     */
    static float cosine(float[] a, float[] b) {
        float dot = 0;
        for (int i = 0; i < a.length; i++) dot += a[i] * b[i];
        return dot;
    }

    record DataItem(int itemId, int wppId, String name, float[] embedding) {
        @SuppressWarnings("unchecked")
        static DataItem fromMap(Map<String, Object> m) {
            List<Double> raw = (List<Double>) m.get("embedding");
            float[] emb = new float[raw.size()];
            for (int i = 0; i < emb.length; i++) emb[i] = raw.get(i).floatValue();
            return new DataItem(
                ((Number) m.get("item_id")).intValue(),
                ((Number) m.get("wpp_id")).intValue(),
                (String) m.get("name"),
                emb
            );
        }
    }
}
