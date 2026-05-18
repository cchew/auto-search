package dev.autosearch;

import org.junit.jupiter.api.Test;
import java.io.IOException;
import java.net.URISyntaxException;
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
}
