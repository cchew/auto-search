package dev.autosearch;

import org.yaml.snakeyaml.Yaml;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

public record AutoSearchConfig(
    String name,
    String idField,
    String groupField,
    String nameField,
    String descriptionField,
    String domainDescription,
    float minScoreThreshold,
    int topK,
    String storageMode,
    String localOutputDir,
    String s3Bucket,
    String s3Region
) {
    private static String requireNonEmpty(String value, String fieldPath) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                "config.yaml: '" + fieldPath + "' is required (non-empty string)");
        }
        return value;
    }

    private static void validate(AutoSearchConfig cfg) {
        requireNonEmpty(cfg.name, "name");
        requireNonEmpty(cfg.idField, "corpus.id_field");
        requireNonEmpty(cfg.groupField, "corpus.group_field");
        requireNonEmpty(cfg.nameField, "corpus.name_field");
        if (cfg.minScoreThreshold < 0f || cfg.minScoreThreshold > 1f) {
            throw new IllegalArgumentException(
                "config.yaml: 'pipeline.min_score_threshold' must be in [0, 1] (got " + cfg.minScoreThreshold + ")");
        }
    }

    @SuppressWarnings("unchecked")
    public static AutoSearchConfig fromYaml(Path path) throws IOException {
        Yaml yaml = new Yaml();
        Map<String, Object> root;
        try (InputStream is = Files.newInputStream(path)) {
            root = yaml.load(is);
        }
        Map<String, Object> corpus = (Map<String, Object>) root.get("corpus");
        Map<String, Object> pipeline = (Map<String, Object>) root.getOrDefault("pipeline", Map.of());
        Map<String, Object> storage = (Map<String, Object>) root.getOrDefault("storage", Map.of());
        String name = (String) root.get("name");
        AutoSearchConfig cfg = new AutoSearchConfig(
            name != null ? name : "",
            corpus != null ? nullToEmpty((String) corpus.get("id_field")) : "",
            corpus != null ? nullToEmpty((String) corpus.get("group_field")) : "",
            corpus != null ? nullToEmpty((String) corpus.get("name_field")) : "",
            corpus != null ? nullToEmpty((String) corpus.get("description_field")) : "",
            (String) pipeline.getOrDefault("domain_description", "a user"),
            ((Number) pipeline.getOrDefault("min_score_threshold", 0.4)).floatValue(),
            ((Number) pipeline.getOrDefault("top_k", 5)).intValue(),
            (String) storage.getOrDefault("mode", "s3"),
            (String) storage.getOrDefault("local_output_dir", "output/"),
            (String) storage.getOrDefault("s3_bucket", "autosearch-artefacts"),
            (String) storage.getOrDefault("s3_region", "ap-southeast-2")
        );
        validate(cfg);
        return cfg;
    }

    private static String nullToEmpty(String s) {
        return s != null ? s : "";
    }
}
