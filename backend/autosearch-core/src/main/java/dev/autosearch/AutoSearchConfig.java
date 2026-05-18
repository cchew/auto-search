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
        return new AutoSearchConfig(
            (String) root.getOrDefault("name", "default"),
            (String) corpus.get("id_field"),
            (String) corpus.get("group_field"),
            (String) corpus.get("name_field"),
            (String) corpus.get("description_field"),
            (String) pipeline.getOrDefault("domain_description", "a user"),
            ((Number) pipeline.getOrDefault("min_score_threshold", 0.4)).floatValue(),
            ((Number) pipeline.getOrDefault("top_k", 5)).intValue(),
            (String) storage.getOrDefault("mode", "s3"),
            (String) storage.getOrDefault("local_output_dir", "output/"),
            (String) storage.getOrDefault("s3_bucket", "autosearch-artefacts"),
            (String) storage.getOrDefault("s3_region", "ap-southeast-2")
        );
    }
}
