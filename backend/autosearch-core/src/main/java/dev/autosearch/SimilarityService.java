package dev.autosearch;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

public class SimilarityService {

    private static final Logger log = LoggerFactory.getLogger(SimilarityService.class);

    private final List<DataItem> items;
    private final float minScore;

    public SimilarityService(String embeddingsPath, AutoSearchConfig cfg) throws IOException {
        log.info("Loading embeddings from {}", embeddingsPath);
        List<Map<String, Object>> raw = new ObjectMapper().readValue(
            Path.of(embeddingsPath).toFile(), new TypeReference<>() {});
        this.items = raw.stream().map(m -> DataItem.fromMap(m, cfg)).toList();
        this.minScore = cfg.minScoreThreshold();
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
            if (s.score() < minScore) break;
            results.add(new SearchResult(s.item().groupId(), s.item().itemId(), s.item().name(), s.score()));
        }
        if (results.isEmpty()) {
            float topScore = scored.isEmpty() ? 0f : scored.get(0).score();
            log.warn("Search suppressed: all results below minScore={} (top score={})", minScore, topScore);
        }
        return results;
    }

    static float cosine(float[] a, float[] b) {
        float dot = 0;
        for (int i = 0; i < a.length; i++) dot += a[i] * b[i];
        return dot;
    }

    record DataItem(int itemId, int groupId, String name, float[] embedding) {
        @SuppressWarnings("unchecked")
        static DataItem fromMap(Map<String, Object> m, AutoSearchConfig cfg) {
            List<Double> raw = (List<Double>) m.get("embedding");
            float[] emb = new float[raw.size()];
            for (int i = 0; i < emb.length; i++) emb[i] = raw.get(i).floatValue();
            return new DataItem(
                ((Number) m.get(cfg.idField())).intValue(),
                ((Number) m.get(cfg.groupField())).intValue(),
                (String) m.get(cfg.nameField()),
                emb
            );
        }
    }
}
