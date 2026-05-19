package dev.autosearch;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class AutoSearchConfigTest {

    private Path testConfig() throws URISyntaxException {
        return Path.of(getClass().getClassLoader().getResource("test-config.yaml").toURI());
    }

    @Test
    void loadsCorpusFields() throws IOException, URISyntaxException {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());
        assertEquals("service_id", cfg.idField());
        assertEquals("category_id", cfg.groupField());
        assertEquals("title", cfg.nameField());
        assertEquals("summary", cfg.descriptionField());
    }

    @Test
    void loadsName() throws IOException, URISyntaxException {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());
        assertEquals("it-service-catalogue", cfg.name());
    }

    @Test
    void loadsPipelineDefaults() throws IOException, URISyntaxException {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());
        assertEquals(0.35f, cfg.minScoreThreshold(), 0.001f);
        assertEquals(3, cfg.topK());
    }

    @Test
    void defaultsNameWhenAbsent() throws IOException, URISyntaxException {
        AutoSearchConfig cfg = AutoSearchConfig.fromYaml(testConfig());
        assertNotNull(cfg.name());
    }

    @Test
    void fromYaml_rejects_missing_name(@TempDir Path tmp) throws IOException {
        Path file = tmp.resolve("bad.yaml");
        Files.writeString(file, """
            corpus:
              id_field: item_id
              group_field: wpp_id
              name_field: name
              description_field: description
            """);
        IllegalArgumentException e = assertThrows(
            IllegalArgumentException.class,
            () -> AutoSearchConfig.fromYaml(file));
        assertTrue(e.getMessage().contains("name"), "Expected 'name' in: " + e.getMessage());
    }

    @Test
    void fromYaml_rejects_empty_id_field(@TempDir Path tmp) throws IOException {
        Path file = tmp.resolve("bad.yaml");
        Files.writeString(file, """
            name: test
            corpus:
              id_field: ""
              group_field: wpp_id
              name_field: name
              description_field: description
            """);
        IllegalArgumentException e = assertThrows(
            IllegalArgumentException.class,
            () -> AutoSearchConfig.fromYaml(file));
        assertTrue(e.getMessage().contains("id_field"), "Expected 'id_field' in: " + e.getMessage());
    }

    @Test
    void fromYaml_rejects_invalid_min_score_threshold(@TempDir Path tmp) throws IOException {
        Path file = tmp.resolve("bad.yaml");
        Files.writeString(file, """
            name: test
            corpus:
              id_field: item_id
              group_field: wpp_id
              name_field: name
              description_field: description
            pipeline:
              min_score_threshold: 1.5
            """);
        IllegalArgumentException e = assertThrows(
            IllegalArgumentException.class,
            () -> AutoSearchConfig.fromYaml(file));
        assertTrue(e.getMessage().contains("min_score_threshold"), "Expected 'min_score_threshold' in: " + e.getMessage());
    }
}
